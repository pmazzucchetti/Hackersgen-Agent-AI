"""Lezione 3, passo 5: RAG, cercare i pezzi giusti.

Il regolamento e la bacheca della scuola sono lunghi: metterli tutti nel prompt
costa tanti token e confonde il modello. Allora:
  1. dividiamo i documenti in pezzi (un paragrafo ciascuno)
  2. trasformiamo ogni pezzo in un "vettore" di numeri (embedding)
  3. per ogni domanda, prendiamo i pezzi più simili e mettiamo solo quelli nel prompt
È la Retrieval Augmented Generation (RAG): recupera, poi genera.

Lancia: uv run lezione3/05_rag.py
"""

import math
from pathlib import Path

import config

config.controlla_modello()
config.controlla_modello(config.MODELLO_EMBEDDING)
llm = config.client()
CARTELLA = Path(config.__file__).parent / "scuola"
DOMANDA = "Posso usare il telefono in classe?"


def vettore(testo):
    return llm.embeddings.create(model=config.MODELLO_EMBEDDING, input=[testo]).data[0].embedding


def somiglianza(a, b):  # 1 = stessa direzione, 0 = niente in comune
    prodotto = sum(x * y for x, y in zip(a, b))
    return prodotto / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def rispondi(contesto):
    system = f"Sei {config.NOME_ASSISTENTE}, l'assistente della 4B. Rispondi in breve.\n{contesto}"
    messaggi = [{"role": "system", "content": system}, {"role": "user", "content": DOMANDA}]
    return llm.chat.completions.create(model=config.MODELLO, messages=messaggi).choices[0].message.content


# 1. I pezzi: ogni paragrafo "## ..." del regolamento e della bacheca
pezzi = []
for nome in ["regolamento.md", "bacheca.md"]:
    pezzi += ["## " + p for p in (CARTELLA / nome).read_text(encoding="utf-8").split("\n## ")[1:]]

# 2. Un vettore per ogni pezzo (in un'app vera si calcolano una volta e si salvano)
vettori = [vettore(p) for p in pezzi]

# 3. I due pezzi più simili alla domanda
v_domanda = vettore(DOMANDA)
classifica = sorted(range(len(pezzi)), key=lambda i: somiglianza(v_domanda, vettori[i]), reverse=True)
scelti = [pezzi[i] for i in classifica[:2]]

print("SENZA documenti:\n" + rispondi(""))
print("\nPezzi trovati:", [p.split("\n")[0] for p in scelti])
print("\nCON i pezzi trovati:\n" + rispondi("Usa solo questi estratti:\n" + "\n\n".join(scelti)))
