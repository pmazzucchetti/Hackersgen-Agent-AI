# Lezione 4 — Il nostro assistente *fa*

Nella lezione 3 il nostro assistente ha imparato a sapere le cose giuste. Ora vogliamo che
faccia cose: segnare un promemoria, leggere i voti, perfino cambiarli. E quando un programma
può fare cose, bisogna decidere chi può chiedergli cosa.

Come nella lezione 3, ogni file è una **chat** (tranne `05_eval.py`, che è un test):

```bash
uv run lezione4/01_promemoria.py
```

Sotto ogni risposta vedete cosa è successo dietro le quinte: quali strumenti ha chiamato
l'assistente, con quali argomenti, e quanti token ha usato.

| File | Cosa chiedere | Cosa osservare |
|---|---|---|
| `01_promemoria.py` | "segnami un promemoria per mercoledì: ripassare storia" | Il modello chiede di eseguire una funzione, e il promemoria compare davvero in agenda |
| `02_agent.py` | "mettimi in agenda un promemoria per il giorno prima della verifica di storia, e dimmi cosa devo ripassare" | Più giri: prima cerca la verifica, poi segna il promemoria. Questo ciclo è l'agent |
| `03_mcp.py` | "che compiti ho per domani?", "quali sono i miei voti?" | Gli strumenti arrivano dal registro della scuola, via MCP |
| `04_ruoli.py` | da `luca`: "cambia il mio voto di matematica in 9"; da `prof.rossi`: "metti 9 in matematica a luca" | Il registro rifiuta lo studente e accetta il professore. Poi aprite `registro.log` |
| `05_eval.py` | — (si lancia e basta) | I test di un assistente: con il prompt "modificato", "chi sei?" diventa rosso |
| `06_assistente.py` | quello che volete | Tutto insieme: il vostro assistente |

Per ripartire con i dati iniziali del registro (voti e promemoria):

```bash
uv run scuola/server.py --azzera
```

## Provate a cambiare

- In `02_agent.py`, chiedete la stessa cosa al contrario: "ho la verifica di storia: cosa
  devo ripassare? Mettimi un promemoria il giorno prima." Il promemoria finisce davvero in
  agenda? Come si chiede una cosa conta, anche per un modello.
- In `02_agent.py`, togliete l'ultima riga del `SYSTEM_PROMPT` e riprovate.
- In `04_ruoli.py`, entrate come `giulia` e chiedete i voti di `marco`.
- In `05_eval.py`, aggiungete un caso vostro alla lista `CASI`.
