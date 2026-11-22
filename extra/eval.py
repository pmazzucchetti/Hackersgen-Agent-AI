"""Approfondimento: gli eval, ovvero i test di un assistente AI.

Un giorno qualcuno "migliora" il system prompt, nessuno controlla, e l'assistente
torna a dire "sono Qwen". Con il codice normale si scrivono i test; con un modello
si fanno gli eval: domande con la risposta attesa, da lanciare a ogni modifica.
Qui li lanciamo due volte: con il prompt giusto e con uno "rotto".

Lancia: uv run extra/eval.py
"""

import json

import config
from scuola import dati

config.controlla_modello()
llm = config.client()

SYSTEM_PROMPT = f"""Sei {config.NOME_ASSISTENTE}, l'assistente AI degli studenti della classe 4B
dell'Istituto Tecnico "Valle dei Bit". Rispondi in italiano, in breve. {config.CALENDARIO}
Prossime verifiche: {json.dumps(dati.VERIFICHE, ensure_ascii=False)}"""

# Il prompt dopo la "modifica" di qualcuno: sembra uguale, ma manca la prima riga
PROMPT_ROTTO = SYSTEM_PROMPT.split("\n", 1)[1]

# Ogni caso: la domanda e le parole che la risposta DEVE contenere (basta una)
CASI = [
    ("Chi sei?", [config.NOME_ASSISTENTE]),
    ("Di quale classe sei l'assistente?", ["4B"]),
    ("In che scuola siamo?", ["Valle dei Bit"]),
    ("Quando ho la verifica di matematica?", ["2026-12-03", "3 dicembre"]),
]


def esegui_eval(system):
    superati = 0
    for domanda, attese in CASI:
        messaggi = [{"role": "system", "content": system}, {"role": "user", "content": domanda}]
        risposta = llm.chat.completions.create(model=config.MODELLO, messages=messaggi)
        testo = risposta.choices[0].message.content
        anteprima = testo.replace("\n", " ")[:70]
        if any(parola.lower() in testo.lower() for parola in attese):
            superati = superati + 1
            print(f"  ✅ {domanda}  →  {anteprima}")
        else:
            print(f"  ❌ {domanda}  →  {anteprima}")
    print(f"  Superati: {superati}/{len(CASI)}")


print("Prompt giusto:")
esegui_eval(SYSTEM_PROMPT)
print("\nPrompt dopo la modifica:")
esegui_eval(PROMPT_ROTTO)
