"""Lezione 3, passo 4: il contesto.

Il modello sa tante cose del mondo, ma niente della NOSTRA scuola: non conosce le
verifiche della 4B e non sa nemmeno che giorno è oggi. Nel passo 3, se glielo
chiedi, se lo inventa. La soluzione più semplice: mettere nel prompt le
informazioni che servono.

Lancia: uv run lezione3/04_contesto.py
Prova:  "quando ho la verifica di matematica?", "posso usare il telefono in classe?",
        "prenotami lo sportello di matematica di mercoledì" (lo sportello c'è: cosa risponde?)
"""

import json

import config
from scuola import dati

config.controlla_modello()
llm = config.client()

SYSTEM_PROMPT = f"""Sei {config.NOME_ASSISTENTE}, l'assistente AI degli studenti della classe 4B.
Rispondi in italiano, in modo breve, dando del tu.

{config.CALENDARIO}
Prossime verifiche: {json.dumps(dati.VERIFICHE, ensure_ascii=False)}
Usa solo queste informazioni. Se una cosa non c'è, dillo: non inventare."""

messaggi = [{"role": "system", "content": SYSTEM_PROMPT}]


def rispondi(domanda):
    messaggi.append({"role": "user", "content": domanda})
    risposta = llm.chat.completions.create(model=config.MODELLO, messages=messaggi)
    testo = risposta.choices[0].message.content
    messaggi.append({"role": "assistant", "content": testo})
    return testo


config.chat(rispondi, nome=config.NOME_ASSISTENTE)
