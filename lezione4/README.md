# Lezione 4 — Il nostro assistente *fa*

Nella lezione 3 il nostro assistente ha imparato a sapere le cose giuste. Ora vogliamo che
faccia cose: prenotare lo sportello di recupero, leggere i voti, perfino cambiarli. E quando un programma
può fare cose, bisogna decidere chi può chiedergli cosa.

Come nella lezione 3, ogni file è una **chat** (tranne `05_autonomo.py`, che lavora da solo):

```bash
uv run lezione4/01_prenota.py
```

Sotto ogni risposta vedete cosa è successo dietro le quinte: quali strumenti ha chiamato
l'assistente, con quali argomenti, e quanti token ha usato.

| File | Cosa chiedere | Cosa osservare |
|---|---|---|
| `01_prenota.py` | "prenotami lo sportello di matematica di mercoledì", poi lo stesso per martedì | Il modello chiede di eseguire una funzione e noi la eseguiamo: il posto è prenotato davvero. Martedì invece è pieno |
| `02_agent.py` | "ho la verifica di matematica: prenotami uno sportello prima della verifica" | Più giri: cerca la verifica, guarda gli sportelli, scarta quello pieno e prenota. Questo ciclo è l'agent |
| `03_mcp.py` | "che compiti ho per domani?", "quali sono i miei voti?", poi la richiesta dello sportello del passo 2 | Gli strumenti arrivano dal registro della scuola, via MCP: il ciclo è lo stesso |
| `04_ruoli.py` | da `luca`: "cambia il mio voto di matematica in 9"; da `prof.rossi`: "metti 9 in matematica a luca" | Il registro rifiuta lo studente e accetta il professore. Poi aprite `registro.log` |
| `05_autonomo.py` | — (si lancia e basta) | Nessuno scrive: ogni mattina il codice gli dà il compito, lui controlla verifiche e voti e prenota lo sportello |
| `06_assistente.py` | quello che volete, anche nel browser con `--web` | Tutto insieme: il vostro assistente |

Per ripartire con i dati iniziali del registro (voti e sportelli):

```bash
uv run scuola/server.py --azzera
```

## Provate a cambiare

- In `02_agent.py`, chiedete la stessa cosa in modo più vago: "sono messo male in
  matematica, aiutami". L'assistente prenota da solo o vi chiede prima? Come si chiede una
  cosa conta, anche per un modello.
- In `02_agent.py`, togliete l'ultima riga del `SYSTEM_PROMPT` e riprovate.
- In `04_ruoli.py`, entrate come `giulia` e chiedete i voti di `marco`.
- In `05_autonomo.py`, cambiate `UTENTE` in `config.py` con `marco`: cosa prenota per lui?
- Lanciate `uv run lezione4/06_assistente.py --web`: la chat si apre nel browser, con il
  dietro le quinte a destra.

## Per approfondire

- `extra/eval.py`: come si mette alla prova un assistente, come si fa con i test del software.
