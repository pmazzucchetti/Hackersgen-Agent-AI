"""Lezione 4, passo 4: ruoli e registro delle azioni.

Ora l'assistente può fare cose vere, anche cambiare un voto. Chi può farlo?
Un professore sì, uno studente no. Il registro conosce il ruolo di ogni utente
e controlla prima di eseguire: un permesso, alla fine, è un "if".
E se qualcosa va storto? Teniamo traccia di ogni azione in registro.log:
chi ha chiesto cosa, quale strumento è stato usato, con che risultato.

Lancia: uv run lezione4/04_ruoli.py   (all'inizio ti chiede chi sei)
Prova:  da luca "cambia il mio voto di matematica in 9", da prof.rossi
        "metti 9 in matematica a luca"; poi apri registro.log
"""

import json
from datetime import datetime

import config
import registro

config.controlla_modello()
llm = config.client()
MAX_PASSI = 6
STRUMENTI = registro.strumenti()

utente = input("Chi sei? (luca, giulia, marco, prof.rossi): ").strip().lower()

SYSTEM_PROMPT = f"""Sei {config.NOME_ASSISTENTE}, l'assistente della 4B. {config.CALENDARIO}
Stai parlando con {utente} (utente: {utente}).
Per fare un'azione usa SEMPRE lo strumento: non dire mai di aver fatto qualcosa che non hai fatto."""

messaggi = [{"role": "system", "content": SYSTEM_PROMPT}]


def annota(domanda, strumento, argomenti, risultato):
    riga = {
        "ora": datetime.now().isoformat(timespec="seconds"),
        "utente": utente,
        "domanda": domanda,
        "strumento": strumento,
        "argomenti": argomenti,
        "risultato": json.loads(risultato),
    }
    with open("registro.log", "a", encoding="utf-8") as log:
        log.write(json.dumps(riga, ensure_ascii=False) + "\n")


def rispondi(domanda):
    messaggi.append({"role": "user", "content": domanda})
    for giro in range(MAX_PASSI):
        messaggio = llm.chat.completions.create(model=config.MODELLO, messages=messaggi, tools=STRUMENTI).choices[0].message
        messaggi.append(messaggio)
        if not messaggio.tool_calls:
            return messaggio.content
        for chiamata in messaggio.tool_calls:
            argomenti = json.loads(chiamata.function.arguments or "{}")
            risultato = registro.chiama(chiamata.function.name, argomenti)
            print(f"  [registro: {chiamata.function.name} → {risultato}]")
            annota(domanda, chiamata.function.name, argomenti, risultato)
            messaggi.append({"role": "tool", "tool_call_id": chiamata.id, "content": risultato})
    return "Mi fermo qui: troppi passi."


config.chat(rispondi, nome=config.NOME_ASSISTENTE)
