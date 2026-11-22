# Lezione 3 — Il nostro assistente *sa*

Ogni azienda oggi vuole il suo assistente AI. Costruiamo il nostro, per la classe 4B: un
passo alla volta, partendo ogni volta da un problema che vediamo sullo schermo.

Ogni file è una **chat**: lo lanci dalla cartella del progetto, fai le tue domande e
scrivi `esci` (o premi Ctrl+C) per finire.

```bash
uv run lezione3/01_prima_chiamata.py
```

Il trucco per seguire la lezione: **la domanda che un passo sbaglia, il passo dopo la
risolve.** Provate le stesse domande in due file vicini.

| File | Cosa chiedere | Cosa osservare |
|---|---|---|
| `01_prima_chiamata.py` | "mi chiamo Luca", poi "come mi chiamo?" | Non lo sa: ogni domanda è una chiamata a sé |
| `02_chat.py` | le stesse due domande, poi "chi sei?" | Ora ricorda (guarda i token crescere), ma dice di essere Qwen |
| `03_chi_sei.py` | "chi sei?", poi "quando ho la verifica di matematica?" | Ha un nome e uno scopo, ma la data della verifica se la inventa |
| `04_contesto.py` | "quando ho la verifica di matematica?", "posso usare il telefono in classe?" | La data è giusta; sul telefono tira a indovinare. E se gli chiedi di prenotarti lo sportello di recupero? |
| `05_rag.py` | "posso usare il telefono in classe?", "quando c'è il torneo di calcetto?" | Cerca nel regolamento e nella bacheca e risponde con le regole vere |

## Provate a cambiare

- In `config.py`, `NOME_ASSISTENTE`: battezzate il vostro assistente.
- In `03_chi_sei.py`, il `SYSTEM_PROMPT`: fatelo rispondere come un pirata, o solo in inglese.
- In `04_contesto.py`, togliete la riga "non inventare" e chiedete una verifica che non c'è.
- In `05_rag.py`, guardate quali pezzi trova per domande diverse: "posso svapare in cortile?",
  "chi ha caricato gli appunti di storia?".

## Se qualcosa non va

- **"Ollama non risponde"**: apri l'app Ollama e riprova.
- **Risposte diverse dalle nostre**: è normale, il modello non risponde mai due volte uguale.
- **Molto lento**: con 8 GB di RAM ogni risposta può richiedere 10-20 secondi.
- **I file vanno lanciati dalla cartella del progetto** (`Hackersgen-Agent-AI`), non da `lezione3`.
