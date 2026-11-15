"""Lezione 3, passo 4: il contesto.

Il modello sa tante cose del mondo, ma niente della NOSTRA scuola: non conosce
le verifiche della 4B e non sa nemmeno che giorno è oggi. Se glielo chiediamo,
o ammette di non saperlo o, peggio, se lo inventa.
La soluzione più semplice: mettere le informazioni che servono nel prompt.

Lancia: uv run lezione3/04_contesto.py
"""

import json

import config
from scuola import dati

config.controlla_modello()
llm = config.client()

SYSTEM_PROMPT = f"""Sei {config.NOME_ASSISTENTE}, l'assistente AI degli studenti della classe 4B.
Rispondi in italiano, in modo breve, dando del tu."""

CONTESTO = f"""Oggi è lunedì {config.DATA_DI_OGGI}.
Orario settimanale della 4B: {json.dumps(dati.ORARIO, ensure_ascii=False)}
Prossime verifiche: {json.dumps(dati.VERIFICHE, ensure_ascii=False)}
Usa solo queste informazioni. Se una cosa non c'è, dillo: non inventare."""


def chiedi(system):
    domanda = "Quando ho la verifica di matematica e cosa devo studiare?"
    messaggi = [{"role": "system", "content": system}, {"role": "user", "content": domanda}]
    return llm.chat.completions.create(model=config.MODELLO, messages=messaggi).choices[0].message.content


print("SENZA contesto:")
print(chiedi(SYSTEM_PROMPT))

print("\nCON il contesto:")
print(chiedi(SYSTEM_PROMPT + "\n\n" + CONTESTO))
