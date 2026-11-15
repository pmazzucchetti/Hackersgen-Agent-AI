"""Lezione 3, passo 1: la prima chiamata al modello.

Un'app di intelligenza artificiale, alla base, è un programma che manda del testo
a un modello e ne riceve altro. Facciamolo: una domanda, una risposta.

Lancia: uv run lezione3/01_prima_chiamata.py
"""

import config

config.controlla_modello()
llm = config.client()

risposta = llm.chat.completions.create(
    model=config.MODELLO,
    messages=[{"role": "user", "content": "Spiegami in tre righe la fotosintesi."}],
)

print(risposta.choices[0].message.content)

# Ogni parola (più o meno) è un "token": è l'unità con cui si misura il lavoro del modello
print(f"\n(token usati: {risposta.usage.total_tokens})")
