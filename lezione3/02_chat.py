"""Lezione 3, passo 2: la chat.

Il modello non ricorda niente: ogni chiamata parte da zero. Una chat "ricorda"
solo perché siamo noi a rimandargli, ogni volta, tutta la conversazione.
Guarda i token: crescono a ogni domanda.

Lancia: uv run lezione3/02_chat.py   (scrivi "esci" per finire)
"""

import config

config.controlla_modello()
llm = config.client()

messaggi = []  # la memoria della chat: una semplice lista

while True:
    try:
        domanda = input("\nTu: ")
    except (KeyboardInterrupt, EOFError):
        break
    if domanda.strip().lower() == "esci":
        break

    messaggi.append({"role": "user", "content": domanda})
    risposta = llm.chat.completions.create(model=config.MODELLO, messages=messaggi)
    testo = risposta.choices[0].message.content
    messaggi.append({"role": "assistant", "content": testo})

    print(f"\nAssistente: {testo}")
    print(f"(token usati: {risposta.usage.total_tokens})")
