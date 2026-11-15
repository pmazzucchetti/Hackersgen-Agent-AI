# Lezione 4 — Il nostro assistente *fa*

Nella lezione 3 il nostro assistente ha imparato a sapere le cose giuste. Ora vogliamo che
faccia cose: segnare un promemoria, leggere i voti, perfino cambiarli. E quando un programma
può fare cose, bisogna decidere chi può chiedergli cosa.

Ogni file si lancia da solo, dalla cartella del progetto:

```bash
uv run lezione4/01_promemoria.py
```

| File | Il problema | Cosa aggiungiamo |
|---|---|---|
| `01_promemoria.py` | Dice "fatto!" ma non ha fatto niente | Il tool calling: il modello chiede, noi eseguiamo |
| `02_agent.py` | Una richiesta vera richiede più passi | Il loop: questo ciclo *è* l'agent |
| `03_mcp.py` | Gli strumenti stanno in altri sistemi | MCP: il registro dice quali strumenti ha e li esegue |
| `04_ruoli.py` | Chi può cambiare un voto? | Ruoli e permessi, e un registro di ogni azione (`registro.log`) |
| `05_eval.py` | Qualcuno cambia il prompt e nessuno se ne accorge | Gli eval: i test di un assistente AI |
| `06_assistente.py` | — | Tutto insieme: il vostro assistente, in chat |

Per ripartire con i dati iniziali del registro (voti e promemoria):

```bash
uv run scuola/server.py --azzera
```

## Provate a cambiare

- In `02_agent.py`, scrivete la richiesta al contrario: *"Ho la verifica di storia: cosa devo
  ripassare? Mettimi un promemoria il giorno prima."* Il promemoria finisce davvero in
  agenda? Come si chiede una cosa conta, anche per un modello.
- In `02_agent.py`, togliete l'ultima riga del `SYSTEM_PROMPT` e guardate cosa succede.
- In `config.py`, cambiate `UTENTE` in `"prof.rossi"` e rilanciate `06_assistente.py`.
- In `05_eval.py`, aggiungete un caso vostro alla lista `CASI`.
- Sfida: aggiungete all'assistente di `06_assistente.py` la ricerca nel regolamento della
  lezione 3.
