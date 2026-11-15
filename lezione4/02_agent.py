"""Lezione 4, passo 2: il loop, ovvero l'agent.

Una richiesta vera richiede più passi: prima scoprire quando è la verifica, poi
segnare il promemoria. Mettiamo la chiamata dentro un ciclo: finché il modello
chiede strumenti, li eseguiamo e gli rimandiamo il risultato. Quando smette di
chiederne, ha finito. Questo ciclo È un agent. MAX_PASSI evita che giri all'infinito.

Lancia: uv run lezione4/02_agent.py
"""

import json

import config
from scuola import dati

config.controlla_modello()
llm = config.client()
MAX_PASSI = 6


def verifiche():
    return dati.VERIFICHE


def aggiungi_promemoria(testo, data):
    stato = dati.carica_stato()
    stato["promemoria"].setdefault(config.UTENTE, []).append({"testo": testo, "data": data})
    dati.salva_stato(stato)
    return {"fatto": True}


FUNZIONI = {"verifiche": verifiche, "aggiungi_promemoria": aggiungi_promemoria}
STRUMENTI = [
    {"type": "function", "function": {"name": "verifiche", "description": "Elenca le prossime verifiche della classe",
                                      "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {"name": "aggiungi_promemoria", "description": "Aggiunge un promemoria all'agenda",
                                      "parameters": {"type": "object", "required": ["testo", "data"], "properties": {
                                          "testo": {"type": "string"}, "data": {"type": "string"}}}}},
]

# L'ultima frase conta: senza, i modelli piccoli dicono "fatto!" senza usare lo strumento
SYSTEM_PROMPT = f"""Sei {config.NOME_ASSISTENTE}, l'assistente della 4B. {config.CALENDARIO}
Per fare un'azione usa SEMPRE lo strumento: non dire mai di aver fatto qualcosa che non hai fatto."""

messaggi = [{"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "Mettimi in agenda un promemoria per il giorno prima della verifica di storia, e dimmi cosa devo ripassare."}]

for passo in range(MAX_PASSI):
    risposta = llm.chat.completions.create(model=config.MODELLO, messages=messaggi, tools=STRUMENTI)
    messaggio = risposta.choices[0].message
    messaggi.append(messaggio)
    if not messaggio.tool_calls:  # nessuno strumento richiesto: ha finito
        break
    for chiamata in messaggio.tool_calls:
        argomenti = json.loads(chiamata.function.arguments or "{}")
        risultato = FUNZIONI[chiamata.function.name](**argomenti)
        print(f"Passo {passo + 1}: {chiamata.function.name}({argomenti})")
        messaggi.append({"role": "tool", "tool_call_id": chiamata.id, "content": json.dumps(risultato, ensure_ascii=False)})

print("\n" + (messaggio.content or "(nessuna risposta)"))
