"""Lezione 4, passo 6: il vostro assistente.

Mettiamo insieme tutto: la chat della lezione 3 (che ricorda la conversazione),
il system prompt con nome e calendario, il loop dell'agent, gli strumenti del
registro via MCP e il registro delle azioni. Non è più un chatbot: è un agent.

Lancia: uv run lezione4/06_assistente.py   (scrivi "esci" per finire)
Chi sei lo decide UTENTE in config.py.
"""

import json
from datetime import datetime

import config
import registro

config.controlla_modello()
llm = config.client()
STRUMENTI = registro.strumenti()
MAX_PASSI = 6

SYSTEM_PROMPT = f"""Sei {config.NOME_ASSISTENTE}, l'assistente AI degli studenti della classe 4B
dell'Istituto Tecnico "Valle dei Bit". Rispondi in italiano, in breve, dando del tu. {config.CALENDARIO}
Stai parlando con {config.UTENTE} (utente: {config.UTENTE}).
Per fare un'azione usa SEMPRE lo strumento: non dire mai di aver fatto qualcosa che non hai fatto."""

messaggi = [{"role": "system", "content": SYSTEM_PROMPT}]
print(f"{config.NOME_ASSISTENTE} è pronta. Stai usando l'account: {config.UTENTE}")

while True:
    try:
        richiesta = input("\nTu: ")
    except (KeyboardInterrupt, EOFError):
        break
    if richiesta.strip().lower() == "esci":
        break
    messaggi.append({"role": "user", "content": richiesta})

    for _ in range(MAX_PASSI):  # il loop dell'agent
        messaggio = llm.chat.completions.create(model=config.MODELLO, messages=messaggi, tools=STRUMENTI).choices[0].message
        messaggi.append(messaggio)
        if not messaggio.tool_calls:
            break
        for chiamata in messaggio.tool_calls:
            argomenti = json.loads(chiamata.function.arguments or "{}")
            risultato = registro.chiama(chiamata.function.name, argomenti)
            print(f"  [{chiamata.function.name}]")
            with open("registro.log", "a", encoding="utf-8") as log:
                log.write(json.dumps({"ora": datetime.now().isoformat(timespec="seconds"), "utente": config.UTENTE,
                                      "strumento": chiamata.function.name, "argomenti": argomenti,
                                      "risultato": json.loads(risultato)}, ensure_ascii=False) + "\n")
            messaggi.append({"role": "tool", "tool_call_id": chiamata.id, "content": risultato})

    print(f"\n{config.NOME_ASSISTENTE}: {messaggio.content or '(nessuna risposta)'}")
