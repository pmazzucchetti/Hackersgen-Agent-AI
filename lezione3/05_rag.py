"""Lezione 3, passo 5: RAG, cercare i pezzi giusti.

Il regolamento e la bacheca della scuola sono lunghi: metterli tutti nel prompt
costa tanti token e confonde il modello. Allora:
  1. dividiamo i documenti in pezzi (un paragrafo ciascuno)
  2. trasformiamo ogni pezzo in un "vettore" di numeri (embedding)
  3. a ogni domanda prendiamo i due pezzi più simili e passiamo solo quelli
È la Retrieval Augmented Generation (RAG): prima recupera, poi genera.

Lancia: uv run lezione3/05_rag.py
Prova:  "posso usare il telefono in classe?", "quando c'è il torneo di calcetto?"
"""

import math
from pathlib import Path

import config

config.controlla_modello()
config.controlla_modello(config.MODELLO_EMBEDDING)
llm = config.client()


def somiglianza(a, b):  # 1 = stessa direzione, 0 = niente in comune
    prodotto = sum(x * y for x, y in zip(a, b))
    return prodotto / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


# 1. I pezzi: ogni paragrafo che inizia con "## " nel regolamento e nella bacheca
pezzi = []
for nome_file in ["regolamento.md", "bacheca.md"]:
    testo = Path("scuola", nome_file).read_text(encoding="utf-8")
    for paragrafo in testo.split("\n## ")[1:]:
        pezzi.append("## " + paragrafo)

# 2. Un vettore per ogni pezzo, con una sola chiamata al modello di embedding
risultato = llm.embeddings.create(model=config.MODELLO_EMBEDDING, input=pezzi)
vettori = [elemento.embedding for elemento in risultato.data]

messaggi = [{"role": "system", "content": f"""Sei {config.NOME_ASSISTENTE}, l'assistente della 4B.
Rispondi in breve, dando del tu, usando gli estratti dei documenti della scuola che ti passo."""}]


def rispondi(domanda):
    # 3. I due pezzi più simili alla domanda
    v_domanda = llm.embeddings.create(model=config.MODELLO_EMBEDDING, input=[domanda]).data[0].embedding
    classifica = []
    for pezzo, vettore in zip(pezzi, vettori):
        classifica.append((somiglianza(v_domanda, vettore), pezzo))
    classifica.sort(reverse=True)
    scelti = [classifica[0][1], classifica[1][1]]
    print("  [pezzi trovati: " + " | ".join(p.split("\n")[0] for p in scelti) + "]")

    estratti = "\n\n".join(scelti)
    messaggi.append({"role": "user", "content": f"Estratti:\n{estratti}\n\nDomanda: {domanda}"})
    risposta = llm.chat.completions.create(model=config.MODELLO, messages=messaggi)
    testo = risposta.choices[0].message.content
    messaggi.append({"role": "assistant", "content": testo})
    return testo


config.chat(rispondi, nome=config.NOME_ASSISTENTE)
