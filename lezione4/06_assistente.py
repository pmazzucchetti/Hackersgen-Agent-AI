"""Lezione 4, passo 6: il vostro assistente.

Tutto insieme: la chat che ricorda, il system prompt con nome e calendario, il loop
dell'agent, gli strumenti del registro via MCP, il registro delle azioni, e la
ricerca nei documenti della scuola della lezione 3, che qui diventa uno strumento
in più: è l'agent a decidere quando cercare. Non è più un chatbot: è un agent.

Lancia: uv run lezione4/06_assistente.py   (all'inizio ti chiede chi sei)
"""

import json
import math
from datetime import datetime
from pathlib import Path

import config
import registro

config.controlla_modello()
config.controlla_modello(config.MODELLO_EMBEDDING)
llm = config.client()
MAX_PASSI = 6

# --- La ricerca nei documenti (lezione 3, passo 5), trasformata in uno strumento ---
pezzi = []
for nome_file in ["regolamento.md", "bacheca.md"]:
    for paragrafo in Path("scuola", nome_file).read_text(encoding="utf-8").split("\n## ")[1:]:
        pezzi.append("## " + paragrafo)
vettori = [e.embedding for e in llm.embeddings.create(model=config.MODELLO_EMBEDDING, input=pezzi).data]


def somiglianza(a, b):
    prodotto = sum(x * y for x, y in zip(a, b))
    return prodotto / (math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b)))


def cerca_documenti(domanda):
    v_domanda = llm.embeddings.create(model=config.MODELLO_EMBEDDING, input=[domanda]).data[0].embedding
    classifica = []
    for pezzo, vettore in zip(pezzi, vettori):
        classifica.append((somiglianza(v_domanda, vettore), pezzo))
    classifica.sort(reverse=True)
    return json.dumps([classifica[0][1], classifica[1][1]], ensure_ascii=False)


CERCA = {"type": "function", "function": {
    "name": "cerca_documenti",
    "description": "Cerca nel regolamento della scuola e negli avvisi della bacheca della classe. Usalo per ogni domanda su regole, divieti, eventi e avvisi",
    "parameters": {"type": "object", "required": ["domanda"], "properties": {"domanda": {"type": "string"}}}}}
STRUMENTI = registro.strumenti() + [CERCA]

# --- Chi sei, e il registro delle azioni ---
utente = input("Chi sei? (luca, giulia, marco, prof.rossi): ").strip().lower()


def annota(strumento, argomenti, risultato):
    riga = {"ora": datetime.now().isoformat(timespec="seconds"), "utente": utente,
            "strumento": strumento, "argomenti": argomenti, "risultato": json.loads(risultato)}
    with open("registro.log", "a", encoding="utf-8") as log:
        log.write(json.dumps(riga, ensure_ascii=False) + "\n")


# --- L'agent ---
SYSTEM_PROMPT = f"""Sei {config.NOME_ASSISTENTE}, l'assistente AI degli studenti della classe 4B
dell'Istituto Tecnico "Valle dei Bit". Rispondi in italiano, in breve, dando del tu. {config.CALENDARIO}
Stai parlando con {utente} (utente: {utente}).
Per ogni domanda su regole, divieti, eventi o avvisi chiama SUBITO cerca_documenti, senza chiedere il permesso.
Per fare un'azione usa SEMPRE lo strumento: non dire mai di aver fatto qualcosa che non hai fatto."""

messaggi = [{"role": "system", "content": SYSTEM_PROMPT}]


def rispondi(domanda):
    messaggi.append({"role": "user", "content": domanda})
    for giro in range(MAX_PASSI):
        messaggio = llm.chat.completions.create(model=config.MODELLO, messages=messaggi, tools=STRUMENTI).choices[0].message
        messaggi.append(messaggio)
        if not messaggio.tool_calls:
            return messaggio.content
        for chiamata in messaggio.tool_calls:
            argomenti = json.loads(chiamata.function.arguments or "{}")
            print(f"  [{chiamata.function.name} {argomenti}]")
            if chiamata.function.name == "cerca_documenti":
                risultato = cerca_documenti(argomenti.get("domanda", domanda))
            else:
                risultato = registro.chiama(chiamata.function.name, argomenti)
            annota(chiamata.function.name, argomenti, risultato)
            messaggi.append({"role": "tool", "tool_call_id": chiamata.id, "content": risultato})
    return "Mi fermo qui: troppi passi."


config.chat(rispondi, nome=config.NOME_ASSISTENTE)
