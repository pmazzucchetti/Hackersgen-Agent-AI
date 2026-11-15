"""Lezione 4, passo 1: dal dire al fare (tool calling).

Non vogliamo solo risposte: vogliamo che l'assistente FACCIA cose. Gli chiediamo
un promemoria e risponde "fatto!"... ma non ha fatto niente: sa solo scrivere testo.
Il trucco: gli descriviamo una funzione. Il modello non la esegue, scrive un JSON
con il nome e gli argomenti; siamo noi a eseguirla.

Lancia: uv run lezione4/01_promemoria.py
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
        "testo": {"type": "string"}, "data": {"type": "string", "description": "AAAA-MM-GG"}}},
}}

messaggi = [{"role": "system", "content": config.CALENDARIO},
            {"role": "user", "content": "Segnami un promemoria: ripassare storia mercoledì."}]

print("SENZA strumenti:")
print(llm.chat.completions.create(model=config.MODELLO, messages=messaggi).choices[0].message.content)
print("Promemoria nell'agenda:", dati.carica_stato()["promemoria"].get(config.UTENTE, []))

print("\nCON lo strumento:")
risposta = llm.chat.completions.create(model=config.MODELLO, messages=messaggi, tools=[STRUMENTO])
for chiamata in risposta.choices[0].message.tool_calls or []:
    argomenti = json.loads(chiamata.function.arguments)
    print("Il modello chiede di eseguire:", chiamata.function.name, argomenti)
    aggiungi_promemoria(**argomenti)  # siamo NOI a eseguire la funzione
print("Promemoria nell'agenda:", dati.carica_stato()["promemoria"].get(config.UTENTE, []))
