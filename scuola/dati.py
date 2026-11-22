"""Fake data of class 4B at Istituto Tecnico "Valle dei Bit".

Fixed data (timetable, tests, homework) live here. What can change (grades and
revision session bookings) is saved in stato.json, next to this file.
"""

import copy
import json
from pathlib import Path

STATO_FILE = Path(__file__).with_name("stato.json")

CLASSE = "4B"

UTENTI = {
    "luca": "studente",
    "giulia": "studente",
    "marco": "studente",
    "prof.rossi": "professore",
}

ORARIO = {
    "lunedì": ["italiano", "italiano", "matematica", "inglese", "informatica", "informatica"],
    "martedì": ["storia", "matematica", "matematica", "inglese", "sistemi", "educazione fisica"],
    "mercoledì": ["informatica", "informatica", "italiano", "storia", "matematica", "inglese"],
    "giovedì": ["matematica", "matematica", "sistemi", "sistemi", "italiano", "religione"],
    "venerdì": ["inglese", "storia", "informatica", "informatica", "italiano", "educazione fisica"],
}

VERIFICHE = [
    {"materia": "matematica", "data": "2026-12-03", "argomenti": "equazioni e disequazioni di secondo grado"},
    {"materia": "storia", "data": "2026-12-04", "argomenti": "la Rivoluzione francese, dal 1789 al Terrore"},
    {"materia": "inglese", "data": "2026-12-09", "argomenti": "present perfect e past simple"},
]

COMPITI = {
    "2026-12-01": [
        {"materia": "matematica", "testo": "esercizi 12-18 a pagina 210"},
        {"materia": "italiano", "testo": "leggere il capitolo 3 dei Promessi sposi"},
    ],
    "2026-12-02": [{"materia": "inglese", "testo": "workbook, pagina 45"}],
    "2026-12-03": [{"materia": "informatica", "testo": "finire l'esercizio sui cicli for"}],
}

STATO_INIZIALE = {
    "voti": {
        "luca": [
            {"materia": "matematica", "voto": 6},
            {"materia": "storia", "voto": 7},
            {"materia": "inglese", "voto": 8},
            {"materia": "informatica", "voto": 9},
        ],
        "giulia": [
            {"materia": "matematica", "voto": 8},
            {"materia": "storia", "voto": 9},
            {"materia": "inglese", "voto": 7},
        ],
        "marco": [
            {"materia": "matematica", "voto": 5},
            {"materia": "storia", "voto": 6},
            {"materia": "informatica", "voto": 8},
        ],
    },
    # Afternoon revision sessions with a teacher: few seats, students book them
    "sportelli": [
        {"materia": "matematica", "data": "2026-12-01", "ora": "14:30", "professore": "prof. Rossi",
         "aula": "aula 12", "posti": 2, "iscritti": ["giulia", "marco"]},
        {"materia": "matematica", "data": "2026-12-02", "ora": "15:00", "professore": "prof. Rossi",
         "aula": "aula 12", "posti": 4, "iscritti": ["marco"]},
        {"materia": "matematica", "data": "2026-12-04", "ora": "14:30", "professore": "prof. Rossi",
         "aula": "aula 12", "posti": 4, "iscritti": []},
        {"materia": "storia", "data": "2026-12-03", "ora": "14:30", "professore": "prof.ssa Verdi",
         "aula": "biblioteca", "posti": 5, "iscritti": ["giulia"]},
        {"materia": "inglese", "data": "2026-12-07", "ora": "14:30", "professore": "prof.ssa Bianchi",
         "aula": "laboratorio linguistico", "posti": 6, "iscritti": []},
    ],
}


def carica_stato() -> dict:
    stato = copy.deepcopy(STATO_INIZIALE)
    if STATO_FILE.exists():  # parts missing from an older saved state start from the initial data
        stato.update(json.loads(STATO_FILE.read_text(encoding="utf-8")))
    return stato


def salva_stato(stato: dict) -> None:
    STATO_FILE.write_text(json.dumps(stato, indent=2, ensure_ascii=False), encoding="utf-8")


def azzera() -> None:
    STATO_FILE.unlink(missing_ok=True)
