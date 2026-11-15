# HackersGen Live 2026 — AI Agent

Il codice dei laboratori della live HackersGen sugli **AI Agent**: lezioni 3 e 4,
*Costruisco e miglioro*.

## Il progetto: un assistente scolastico

Costruiamo da zero, in Python, un **agent** che fa da assistente alla segreteria di una
scuola. Un passo alla volta impara a:

- rispondere a domande su aule e attrezzature;
- verificare se un'aula è libera;
- gestire una richiesta articolata: trovare un'aula con certe caratteristiche e prenotarla.

La scuola non è vera: è un **sistema simulato** (in `scuola/`) che l'agent usa attraverso
**MCP**, lo standard con cui gli agent si collegano a strumenti e servizi esterni.

Il modello di AI gira **sul tuo computer**, con Ollama: niente account, niente costi,
nessun dato che esce dal tuo PC.

> In diretta il docente potrebbe usare un modello online, più veloce, per non far aspettare
> tutti. Il codice è lo stesso: cambiano solo l'indirizzo e il nome del modello. Cambia
> invece quanto è "intelligente" il modello, e lo vedremo.

## Prima della live

Segui **[SETUP.md](SETUP.md)** e lancia la verifica: deve essere tutta verde.

## Com'è fatta la repository

```
Hackersgen-Agent-AI/
├── SETUP.md        la guida per preparare l'ambiente
├── verifica.py     controlla che sia tutto pronto
├── scuola/         il sistema simulato della scuola (server MCP)
├── lezione3/       in arrivo il giorno della lezione 3
└── lezione4/       in arrivo dopo la lezione 3
```

Ogni lezione ha la sua cartella con il punto di partenza: se ne hai persa una, riparti da
lì. Le cartelle arrivano man mano che si fanno le lezioni.

## Aggiornare il codice

Prima di ogni lezione, dalla cartella del progetto:

```bash
git pull
uv sync
```

## Come usare l'AI per farti aiutare

Usare un assistente AI (ChatGPT, Gemini, Claude...) per capire un errore o un concetto è
una buona idea. Due regole:

- **Dagli il contesto:** sistema operativo, comando, errore completo.
- **Capisci prima di copiare:** l'AI sbaglia, e lo vedremo proprio in queste lezioni.
