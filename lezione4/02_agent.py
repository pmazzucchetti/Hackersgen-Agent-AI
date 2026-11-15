"""Lezione 4, passo 2: il loop, ovvero l'agent.

Una richiesta vera richiede più passi: prima scoprire quando è la verifica, poi
segnare il promemoria. Mettiamo la chiamata dentro un ciclo: finché il modello
chiede strumenti, li eseguiamo e gli rimandiamo il risultato. Quando smette di
chiederne, ha finito. Questo ciclo È un agent. MAX_PASSI evita che giri all'infinito.

Lancia: uv run lezione4/02_agent.py
Prova:  "mettimi in agenda un promemoria per il giorno prima della verifica di storia,
        e dimmi cosa devo ripassare", poi "che promemoria ho?"
"""

import json

import config
from scuola import dati

config.controlla_modello()
llm = config.client()
MAX_PASSI = 6


def verifiche():
    return dati.VERIFICHE


def promemoria():
    return dati.carica_stato()["promemoria"].get(config.UTENTE, [])


def aggiungi_promemoria(testo, data):
    stato = dati.carica_stato()
    stato["promemoria"].setdefault(config.UTENTE, []).append({"testo": testo, "data": data})
    dati.salva_stato(stato)
    return {"fatto": True}


def esegui(nome, argomenti):
    if nome == "verifiche":
        return verifiche()
    if nome == "promemoria":
        return promemoria()
    if nome == "aggiungi_promemoria":
        return aggiungi_promemoria(argomenti.get("testo", ""), argomenti.get("data", ""))
    return {"errore": f"Strumento sconosciuto: {nome}"}


STRUMENTI = [
    {"type": "function", "function": {
        "name": "verifiche", "description": "Elenca le prossime verifiche della classe",
        "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {
        "name": "promemoria", "description": "Elenca i promemoria nell'agenda dello studente",
        "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {
        "name": "aggiungi_promemoria", "description": "Aggiunge un promemoria all'agenda dello studente",
        "parameters": {"type": "object", "required": ["testo", "data"], "properties": {
            "testo": {"type": "string"}, "data": {"type": "string", "description": "AAAA-MM-GG"}}}}},
]

# L'ultima frase conta: senza, i modelli piccoli dicono "fatto!" senza usare lo strumento
SYSTEM_PROMPT = f"""Sei {config.NOME_ASSISTENTE}, l'assistente della 4B. {config.CALENDARIO}
Per fare un'azione usa SEMPRE lo strumento: non dire mai di aver fatto qualcosa che non hai fatto."""

messaggi = [{"role": "system", "content": SYSTEM_PROMPT}]


def rispondi(domanda):
    messaggi.append({"role": "user", "content": domanda})
    for giro in range(MAX_PASSI):
        risposta = llm.chat.completions.create(model=config.MODELLO, messages=messaggi, tools=STRUMENTI)
        messaggio = risposta.choices[0].message
        messaggi.append(messaggio)
        print(f"  [giro {giro + 1}: {risposta.usage.total_tokens} token]")
        if not messaggio.tool_calls:  # nessuno strumento richiesto: ha finito
            return messaggio.content
        for chiamata in messaggio.tool_calls:
            argomenti = json.loads(chiamata.function.arguments or "{}")
            print(f"  [strumento: {chiamata.function.name} {argomenti}]")
            risultato = esegui(chiamata.function.name, argomenti)
            messaggi.append({"role": "tool", "tool_call_id": chiamata.id,
                             "content": json.dumps(risultato, ensure_ascii=False)})
    return "Mi fermo qui: troppi passi."


config.chat(rispondi, nome=config.NOME_ASSISTENTE)
