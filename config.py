"""Impostazioni comuni a tutti i file delle lezioni.

Per usare un modello online invece di quello sul tuo computer non serve toccare
le lezioni: basta cambiare INDIRIZZO, CHIAVE e MODELLO qui sotto (o le variabili
d'ambiente con lo stesso nome).
"""

import os
import sys

from openai import APIConnectionError, OpenAI

# Dove sta il modello: Ollama sul tuo computer, oppure un servizio online
INDIRIZZO = os.getenv("INDIRIZZO", "http://localhost:11434/v1")
CHIAVE = os.getenv("CHIAVE", "ollama")
MODELLO = os.getenv("MODELLO", "qwen3:4b-instruct")
MODELLO_EMBEDDING = os.getenv("MODELLO_EMBEDDING", "qwen3-embedding:0.6b")

# Il nostro assistente: dagli il nome che vuoi
NOME_ASSISTENTE = "Ada"

# Chi sta usando l'assistente (un "login" finto): "luca", "giulia", "marco" o "prof.rossi"
UTENTE = "luca"

# Oggi, per la scuola simulata: una data fissa, così le demo danno sempre lo stesso risultato
DATA_DI_OGGI = "2026-11-30"
CALENDARIO = (
    "Oggi è lunedì 2026-11-30. Questa settimana: martedì 2026-12-01, mercoledì 2026-12-02, "
    "giovedì 2026-12-03, venerdì 2026-12-04. Le date si scrivono nel formato AAAA-MM-GG."
)


def client() -> OpenAI:
    return OpenAI(base_url=INDIRIZZO, api_key=CHIAVE)


def controlla_modello(modello: str = MODELLO) -> None:
    """Esce con un messaggio chiaro se il modello non è raggiungibile."""
    try:
        disponibili = [m.id for m in client().models.list()]
    except APIConnectionError:
        print(f"Ollama (o il servizio in {INDIRIZZO}) non risponde: è acceso?")
        sys.exit(1)
    if modello not in disponibili and f"{modello}:latest" not in disponibili:
        print(f"Il modello {modello} non c'è. Con Ollama: ollama pull {modello}")
        sys.exit(1)
