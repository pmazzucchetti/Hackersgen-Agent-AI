"""Lezione 4, passo 1: dal dire al fare (tool calling).

Nel passo 4 della lezione 3, a "segnami un promemoria" l'assistente risponde
"ok!"... ma non ha fatto niente: sa solo scrivere testo.
Il trucco: gli descriviamo una funzione. Il modello non la esegue: scrive un JSON
con il nome e gli argomenti. Siamo noi a eseguirla e a dirgli com'è andata.

Lancia: uv run lezione4/01_promemoria.py
Prova:  "segnami un promemoria per mercoledì: ripassare storia"
"""

import json

import config
from scuola import dati

config.controlla_modello()
llm = config.client()


def aggiungi_promemoria(testo, data):
    stato = dati.carica_stato()
    stato["promemoria"].setdefault(config.UTENTE, []).append({"testo": testo, "data": data})
    dati.salva_stato(stato)
    return {"fatto": True}


# La descrizione della funzione, nel formato che il modello capisce (JSON Schema)
STRUMENTO = {"type": "function", "function": {
    "name": "aggiungi_promemoria",
    "description": "Aggiunge un promemoria all'agenda dello studente",
    "parameters": {"type": "object", "required": ["testo", "data"], "properties": {
        "testo": {"type": "string"},
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
        risultato = aggiungi_promemoria(argomenti["testo"], argomenti["data"])  # siamo NOI a eseguirla
        messaggi.append({"role": "tool", "tool_call_id": chiamata.id, "content": json.dumps(risultato)})
    print(f"  [agenda: {dati.carica_stato()['promemoria'].get(config.UTENTE)}]")

    # Gli diciamo com'è andata e lui risponde
    messaggio = llm.chat.completions.create(model=config.MODELLO, messages=messaggi).choices[0].message
    messaggi.append(messaggio)
    return messaggio.content


config.chat(rispondi, nome=config.NOME_ASSISTENTE)
