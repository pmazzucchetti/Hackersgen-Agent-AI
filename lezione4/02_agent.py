"""Lezione 4, passo 2: il loop, ovvero l'agent.

Una richiesta vera richiede più passi: prima scoprire quando è la verifica, poi
vedere quali sportelli ci sono prima di quel giorno, poi prenotarne uno libero.
Mettiamo la chiamata dentro un ciclo: finché il modello chiede strumenti, li
eseguiamo e gli rimandiamo il risultato. Quando smette di chiederne, ha finito.
Questo ciclo È un agent. MAX_PASSI evita che giri all'infinito.

Lancia: uv run lezione4/02_agent.py
Prova:  "ho la verifica di matematica: prenotami uno sportello prima della verifica",
        poi "a quali sportelli sono iscritto?"
"""

import json

import config
from scuola import dati

config.controlla_modello()
llm = config.client()
MAX_PASSI = 6


def verifiche():
    return dati.VERIFICHE


def sportelli(materia):
    elenco = []
    for s in dati.carica_stato()["sportelli"]:
        if s["materia"] == materia.lower():
            elenco.append({"data": s["data"], "ora": s["ora"], "posti_liberi": s["posti"] - len(s["iscritti"]),
                           "prenotato": config.UTENTE in s["iscritti"]})
    return elenco


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


def esegui(nome, argomenti):
    if nome == "verifiche":
        return verifiche()
    if nome == "sportelli":
        return sportelli(argomenti.get("materia", ""))
    if nome == "prenota_sportello":
        return prenota_sportello(argomenti.get("materia", ""), argomenti.get("data", ""))
    return {"errore": f"Strumento sconosciuto: {nome}"}


STRUMENTI = [
    {"type": "function", "function": {
        "name": "verifiche", "description": "Elenca le prossime verifiche della classe",
        "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {
        "name": "sportelli", "description": "Elenca gli sportelli di recupero di una materia, con i posti liberi",
        "parameters": {"type": "object", "required": ["materia"], "properties": {
            "materia": {"type": "string"}}}}},
    {"type": "function", "function": {
        "name": "prenota_sportello",
        "description": "Prenota un posto allo sportello di recupero (ripasso pomeridiano con un professore)",
        "parameters": {"type": "object", "required": ["materia", "data"], "properties": {
            "materia": {"type": "string"}, "data": {"type": "string", "description": "AAAA-MM-GG"}}}}},
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
