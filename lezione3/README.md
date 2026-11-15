# Lezione 3 — Il nostro assistente *sa*

Ogni azienda oggi vuole il suo assistente AI. Costruiamo il nostro, per la classe 4B:
un passo alla volta, partendo ogni volta da un problema che vediamo sullo schermo.

Ogni file si lancia da solo, dalla cartella del progetto:

```bash
uv run lezione3/01_prima_chiamata.py
```

| File | Il problema | Cosa aggiungiamo |
|---|---|---|
| `01_prima_chiamata.py` | Come si parla con un modello? | Una chiamata: domanda e risposta |
| `02_chat.py` | Il modello non ricorda niente | La conversazione, rimandata ogni volta (guarda i token crescere) |
| `03_chi_sei.py` | "Chi sei?" → "Sono Qwen" | Il system prompt: nome, scopo, tono |
| `04_contesto.py` | Non sa quando hai la verifica e se lo inventa | Le informazioni della classe nel prompt |
| `05_rag.py` | Il regolamento è troppo lungo per il prompt | Cercare solo i pezzi giusti (RAG) |

## Provate a cambiare

- In `config.py`, `NOME_ASSISTENTE`: battezzate il vostro assistente.
- In `03_chi_sei.py`, il `SYSTEM_PROMPT`: fatelo rispondere come un pirata, o solo in inglese.
- In `04_contesto.py`, togliete la riga "non inventare" e chiedete una verifica che non c'è.
- In `05_rag.py`, cambiate `DOMANDA` ("Posso svapare in cortile?", "Quando c'è il torneo di
  calcetto?") e guardate quali pezzi trova.

## Se qualcosa non va

- **"Ollama non risponde"**: apri l'app Ollama e riprova.
- **Risposte diverse dalle nostre**: è normale, il modello non risponde mai due volte uguale.
- **Molto lento**: con 8 GB di RAM ogni risposta può richiedere 10-20 secondi.
