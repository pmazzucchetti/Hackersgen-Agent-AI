"""Lezione 3, passo 1: la prima chiamata al modello.

Un'app di intelligenza artificiale, alla base, è un programma che manda del testo
a un modello e ne riceve altro. Qui ogni domanda è una chiamata a sé.

Lancia: uv run lezione3/01_prima_chiamata.py
Prova:  "spiegami la fotosintesi", poi "mi chiamo Luca" e "come mi chiamo?"
"""

import config

config.controlla_modello()
llm = config.client()


def rispondi(domanda):
    risposta = llm.chat.completions.create(
        model=config.MODELLO,
        messages=[{"role": "user", "content": domanda}],
    )
    testo = risposta.choices[0].message.content
    # Un "token" è più o meno una parola: è l'unità con cui si misura il lavoro del modello
    return f"{testo}\n(token usati: {risposta.usage.total_tokens})"


config.chat(rispondi, nome="Modello")
