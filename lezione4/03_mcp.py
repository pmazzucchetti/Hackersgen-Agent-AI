"""Lezione 4, passo 3: MCP, gli strumenti arrivano dal registro.

Nel passo 2 gli strumenti li abbiamo scritti noi, dentro il programma. Nella realtà
stanno in altri sistemi: il registro elettronico, il calendario, la mail.
MCP (Model Context Protocol) è lo standard con cui un agent chiede a un sistema
"che strumenti hai?" e poi li usa. Il loop è identico: cambia solo da dove
arrivano gli strumenti e chi li esegue.

Lancia: uv run lezione4/03_mcp.py
Prova:  "che compiti ho per domani?", "quali sono i miei voti?",
        "ho la verifica di matematica: prenotami uno sportello prima della verifica"
"""

import json

import config
import registro

config.controlla_modello()
llm = config.client()
MAX_PASSI = 6

STRUMENTI = registro.strumenti()  # "che strumenti hai?"
print("Strumenti del registro:", [s["function"]["name"] for s in STRUMENTI])

SYSTEM_PROMPT = f"""Sei {config.NOME_ASSISTENTE}, l'assistente della 4B. {config.CALENDARIO}
Stai parlando con {config.UTENTE} (utente: {config.UTENTE}).
Per fare un'azione usa SEMPRE lo strumento: non dire mai di aver fatto qualcosa che non hai fatto."""

messaggi = [{"role": "system", "content": SYSTEM_PROMPT}]


def rispondi(domanda):
    messaggi.append({"role": "user", "content": domanda})
    for giro in range(MAX_PASSI):
        risposta = llm.chat.completions.create(model=config.MODELLO, messages=messaggi, tools=STRUMENTI)
        messaggio = risposta.choices[0].message
        messaggi.append(messaggio)
        print(f"  [giro {giro + 1}: {risposta.usage.total_tokens} token]")
        if not messaggio.tool_calls:
            return messaggio.content
        for chiamata in messaggio.tool_calls:
            argomenti = json.loads(chiamata.function.arguments or "{}")
            print(f"  [registro: {chiamata.function.name} {argomenti}]")
            risultato = registro.chiama(chiamata.function.name, argomenti)  # lo esegue il registro, non noi
            messaggi.append({"role": "tool", "tool_call_id": chiamata.id, "content": risultato})
    return "Mi fermo qui: troppi passi."


config.chat(rispondi, nome=config.NOME_ASSISTENTE)
