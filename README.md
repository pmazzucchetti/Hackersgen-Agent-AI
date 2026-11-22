# HackersGen Live 2026 — AI Agent

Il codice dei laboratori della live HackersGen sugli **AI Agent**: lezioni 3 e 4,
*Costruisco e miglioro*.

## Il progetto: un assistente scolastico

Ogni azienda oggi vuole il suo assistente AI. Costruiamo il nostro, da zero, in Python:
**Ada**, l'assistente degli studenti della classe 4B. Un passo alla volta impara a:

- presentarsi e rispondere come vogliamo noi;
- sapere quando sono le verifiche e cosa dice il regolamento della scuola;
- fare cose: prenotare lo sportello di recupero, leggere i voti, e (solo per i professori) cambiarli.

La scuola, l'Istituto Tecnico "Valle dei Bit", non esiste: è un **registro elettronico
simulato** (in `scuola/`) che l'agent usa attraverso **MCP**, lo standard con cui gli agent
si collegano a strumenti e servizi esterni.

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

## Vuoi contribuire?

La repository è aperta. Se trovi un errore, hai un'idea per un esercizio o vuoi
migliorare la guida: fai un fork, lavora sulla tua copia e apri una pull request. Per
segnalare un problema o fare una domanda va benissimo anche una issue.

Il codice è rilasciato con licenza [MIT](LICENSE): puoi riusarlo come vuoi, anche nei
tuoi progetti.
