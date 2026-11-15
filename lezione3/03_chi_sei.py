"""Lezione 3, passo 3: "chi sei?"

Vorremmo che il modello fosse il NOSTRO assistente, ma se nella chat del passo 2
gli chiedi chi è, risponde con il nome del modello. Il system prompt è il briefing
che gli diamo prima di ogni conversazione: chi è, cosa fa, come parla.

Lancia: uv run lezione3/03_chi_sei.py
Prova:  "chi sei?", poi "quando ho la verifica di matematica?"
"""

import config

config.controlla_modello()
llm = config.client()

SYSTEM_PROMPT = f"""Sei {config.NOME_ASSISTENTE}, l'assistente AI degli studenti della classe 4B
dell'Istituto Tecnico "Valle dei Bit". Aiuti con orario, verifiche, compiti e regole della scuola.
Rispondi in italiano, in modo breve e amichevole, dando del tu."""

messaggi = [{"role": "system", "content": SYSTEM_PROMPT}]


def rispondi(domanda):
    messaggi.append({"role": "user", "content": domanda})
    risposta = llm.chat.completions.create(model=config.MODELLO, messages=messaggi)
    testo = risposta.choices[0].message.content
    messaggi.append({"role": "assistant", "content": testo})
    return testo


config.chat(rispondi, nome=config.NOME_ASSISTENTE)
