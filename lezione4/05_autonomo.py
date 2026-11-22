"""Lezione 4, passo 5: l'agente autonomo.

Finora l'assistente aspetta le nostre domande: è una chat, come ChatGPT o Gemini.
Un agent può anche partire da solo, a un orario o quando succede qualcosa, e lavorare
mentre dormite. Qui ogni mattina alle 7 è il CODICE, non uno studente, a dargli il
compito: controllare le verifiche in arrivo e, dove il voto è basso, prenotare lo
sportello di recupero. Per non aspettare, facciamo scorrere i tre giorni prima della
verifica di matematica in un minuto.

Nella realtà questo programma gira su un server e lo fa partire un orario: cron su
Linux, oppure su AWS un agente in AgentCore Runtime avviato da uno scheduler.
Il ciclo dell'agent è identico al passo 3: cambia solo chi fa la domanda.

E se sbaglia mentre nessuno guarda? Le aziende lo mettono alla prova come un software,
con dei test fatti apposta (gli "eval": c'è un esempio in extra/eval.py).

Lancia: uv run lezione4/05_autonomo.py
"""

import json
import time

import config
import registro

config.controlla_modello()
llm = config.client()
MAX_PASSI = 8
UTENTE = config.UTENTE

SETTIMANA = [("lunedì", "2026-11-30"), ("martedì", "2026-12-01"), ("mercoledì", "2026-12-02"),
             ("giovedì", "2026-12-03"), ("venerdì", "2026-12-04")]
CALENDARIO = ", ".join(f"{giorno} {data}" for giorno, data in SETTIMANA)
TIME_LAPSE = SETTIMANA[:3]  # i giorni prima della verifica di matematica (giovedì)

# Un agente che lavora da solo riceve solo gli strumenti che gli servono: niente cambia_voto
STRUMENTI = [s for s in registro.strumenti()
             if s["function"]["name"] in ("verifiche", "voti", "sportelli", "prenota_sportello")]

SYSTEM_PROMPT = f"""Sei {config.NOME_ASSISTENTE}, l'assistente della 4B. Lavori da solo, senza nessuno
a cui chiedere conferma: decidi tu e usa SEMPRE gli strumenti per fare le azioni.
Lavori per {UTENTE} (utente: {UTENTE}). Calendario: {CALENDARIO}. Date nel formato AAAA-MM-GG."""

COMPITO = """Sono le 7:00 di {giorno} {data}. Fai il giro del mattino:
1. guarda le verifiche e i voti di {utente};
2. prendi la prossima verifica dopo oggi in una materia dove il voto è 6 o meno, e guarda gli
   sportelli di quella materia. Se nessuno è prenotato, PRENOTA il primo con posti liberi
   fra oggi e il giorno prima della verifica;
3. scrivi a {utente} il messaggio del mattino, al massimo 3 righe, senza dettagli tecnici."""


def giro_del_mattino(giorno, data):
    messaggi = [{"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": COMPITO.format(giorno=giorno, data=data, utente=UTENTE)}]
    for _ in range(MAX_PASSI):
        messaggio = llm.chat.completions.create(model=config.MODELLO, messages=messaggi, tools=STRUMENTI).choices[0].message
        messaggi.append(messaggio)
        if not messaggio.tool_calls:
            return messaggio.content
        for chiamata in messaggio.tool_calls:
            argomenti = json.loads(chiamata.function.arguments or "{}")
            risultato = registro.chiama(chiamata.function.name, argomenti)
            print(f"  [{chiamata.function.name} {argomenti} → {risultato[:90]}]")
            messaggi.append({"role": "tool", "tool_call_id": chiamata.id, "content": risultato})
    return "Mi fermo qui: troppi passi."


try:  # Ctrl+C ferma il time-lapse in qualunque momento
    for giorno, data in TIME_LAPSE:
        print(f"\n☀️  {giorno} {data}, ore 7:00: parte il giro del mattino")
        messaggio = giro_del_mattino(giorno, data)
        print(f"📬 Messaggio per {UTENTE}:\n{messaggio}")
        time.sleep(1)
except KeyboardInterrupt:
    print("\nGiro interrotto.")
