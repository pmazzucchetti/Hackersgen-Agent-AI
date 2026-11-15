"""Lezione 3, passo 3: "chi sei?"

Abbiamo collegato un modello e vorremmo che fosse il NOSTRO assistente. Ma se gli
chiediamo chi è, risponde con il nome del modello. Il system prompt è il briefing
che diamo al modello prima di ogni conversazione: chi è, cosa fa, come parla.

Lancia: uv run lezione3/03_chi_sei.py   (prova a cambiare SYSTEM_PROMPT)
"""

import config

config.controlla_modello()
llm = config.client()

SYSTEM_PROMPT = f"""Sei {config.NOME_ASSISTENTE}, l'assistente AI degli studenti della classe 4B
dell'Istituto Tecnico "Valle dei Bit". Aiuti con orario, verifiche, compiti e regole della scuola.
Rispondi in italiano, in modo breve e amichevole, dando del tu."""


def chiedi(messaggi):
    risposta = llm.chat.completions.create(model=config.MODELLO, messages=messaggi)
    return risposta.choices[0].message.content


domanda = {"role": "user", "content": "Chi sei?"}

print("SENZA system prompt:")
print(chiedi([domanda]))

print("\nCON il system prompt:")
print(chiedi([{"role": "system", "content": SYSTEM_PROMPT}, domanda]))
