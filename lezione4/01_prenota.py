"""Lezione 4, passo 1: dal dire al fare (tool calling).

Nel passo 4 della lezione 3, a "prenotami lo sportello di matematica" l'assistente
risponde "fatto!"... ma non ha fatto niente: sa solo scrivere testo.
Il trucco: gli descriviamo una funzione. Il modello non la esegue: scrive un JSON
con il nome e gli argomenti. Siamo noi a eseguirla e a dirgli com'è andata.

Lancia: uv run lezione4/01_prenota.py
Prova:  "prenotami lo sportello di matematica di mercoledì", poi lo stesso per martedì
"""

import json

import config
from scuola import dati

config.controlla_modello()
llm = config.client()


def prenota_sportello(materia, data):
    stato = dati.carica_stato()
    for sportello in stato["sportelli"]:
        if sportello["materia"] == materia.lower() and sportello["data"] == data:
            if config.UTENTE in sportello["iscritti"]:
                return {"errore": "Sei già prenotato"}
            if len(sportello["iscritti"]) >= sportello["posti"]:
                return {"errore": "Lo sportello è pieno"}
            sportello["iscritti"].append(config.UTENTE)
            dati.salva_stato(stato)
            return {"fatto": True, "ora": sportello["ora"], "aula": sportello["aula"]}
    return {"errore": f"Nessuno sportello di {materia} il {data}"}


# La descrizione della funzione, nel formato che il modello capisce (JSON Schema)
STRUMENTO = {"type": "function", "function": {
    "name": "prenota_sportello",
    "description": "Prenota un posto allo sportello di recupero (ripasso pomeridiano con un professore)",
    "parameters": {"type": "object", "required": ["materia", "data"], "properties": {
        "materia": {"type": "string"},
        "data": {"type": "string", "description": "AAAA-MM-GG"},
    }},
}}

messaggi = [{"role": "system", "content": f"Sei {config.NOME_ASSISTENTE}, l'assistente della 4B. {config.CALENDARIO}"}]


def rispondi(domanda):
    messaggi.append({"role": "user", "content": domanda})
    messaggio = llm.chat.completions.create(model=config.MODELLO, messages=messaggi, tools=[STRUMENTO]).choices[0].message
    messaggi.append(messaggio)
    if not messaggio.tool_calls:
        return messaggio.content

    for chiamata in messaggio.tool_calls:
        argomenti = json.loads(chiamata.function.arguments)
        print(f"  [il modello chiede: {chiamata.function.name} {argomenti}]")
        risultato = prenota_sportello(argomenti["materia"], argomenti["data"])  # siamo NOI a eseguirla
        print(f"  [risultato: {risultato}]")
        messaggi.append({"role": "tool", "tool_call_id": chiamata.id, "content": json.dumps(risultato)})

    # Gli diciamo com'è andata e lui risponde
    messaggio = llm.chat.completions.create(model=config.MODELLO, messages=messaggi).choices[0].message
    messaggi.append(messaggio)
    return messaggio.content


config.chat(rispondi, nome=config.NOME_ASSISTENTE)
