"""Simulated school system exposed over MCP: rooms, equipment and bookings.

It is the "outside world" our agent talks to. Data are fake and bookings are
saved in prenotazioni.json next to this file. Start it with:

    uv run scuola/server.py
"""

import json
from pathlib import Path

from mcp.server.mcpserver import MCPServer

BOOKINGS_FILE = Path(__file__).with_name("prenotazioni.json")

ROOMS = [
    {"nome": "Aula 1A", "capienza": 28, "attrezzature": ["lavagna", "proiettore"]},
    {"nome": "Aula 2B", "capienza": 25, "attrezzature": ["lavagna"]},
    {"nome": "Laboratorio di informatica", "capienza": 24,
     "attrezzature": ["computer", "proiettore", "lavagna interattiva"]},
    {"nome": "Laboratorio di chimica", "capienza": 20, "attrezzature": ["banconi", "cappa aspirante"]},
    {"nome": "Aula magna", "capienza": 150, "attrezzature": ["proiettore", "microfoni", "palco"]},
    {"nome": "Palestra", "capienza": 60, "attrezzature": ["spogliatoi"]},
    {"nome": "Ufficio del preside", "capienza": 6, "attrezzature": ["tavolo riunioni", "telefono"]},
]

server = MCPServer("scuola", instructions="Aule, attrezzature e prenotazioni dell'istituto.")


def _load_bookings() -> list[dict]:
    if not BOOKINGS_FILE.exists():
        return []
    return json.loads(BOOKINGS_FILE.read_text(encoding="utf-8"))


def _overlaps(booking: dict, room: str, date: str, start: str, end: str) -> bool:
    same_slot = booking["aula"] == room and booking["data"] == date
    return same_slot and booking["ora_inizio"] < end and start < booking["ora_fine"]


def _find_room(name: str) -> dict | None:
    return next((r for r in ROOMS if r["nome"].lower() == name.strip().lower()), None)


@server.tool()
def cerca_aule(attrezzatura: str = "", capienza_minima: int = 0) -> list[dict]:
    """Elenca le aule della scuola. Filtra per attrezzatura (es. "proiettore") e capienza minima.
    Senza filtri restituisce tutte le aule."""
    return [
        r for r in ROOMS
        if r["capienza"] >= capienza_minima
        and (not attrezzatura or any(attrezzatura.lower() in a for a in r["attrezzature"]))
    ]


@server.tool()
def verifica_disponibilita(aula: str, data: str, ora_inizio: str, ora_fine: str) -> dict:
    """Dice se un'aula è libera. data nel formato AAAA-MM-GG, orari nel formato HH:MM."""
    if _find_room(aula) is None:
        return {"errore": f"Aula sconosciuta: {aula}"}
    clashes = [b for b in _load_bookings() if _overlaps(b, aula, data, ora_inizio, ora_fine)]
    return {"aula": aula, "libera": not clashes, "prenotazioni_in_conflitto": clashes}


@server.tool()
def prenota_aula(aula: str, data: str, ora_inizio: str, ora_fine: str, richiedente: str, motivo: str) -> dict:
    """Prenota un'aula. data nel formato AAAA-MM-GG, orari nel formato HH:MM."""
    room = _find_room(aula)
    if room is None:
        return {"errore": f"Aula sconosciuta: {aula}"}
    bookings = _load_bookings()
    if any(_overlaps(b, room["nome"], data, ora_inizio, ora_fine) for b in bookings):
        return {"errore": "L'aula è già occupata in quell'orario"}
    booking = {"aula": room["nome"], "data": data, "ora_inizio": ora_inizio, "ora_fine": ora_fine,
               "richiedente": richiedente, "motivo": motivo}
    bookings.append(booking)
    BOOKINGS_FILE.write_text(json.dumps(bookings, indent=2, ensure_ascii=False), encoding="utf-8")
    return {"confermata": True, "prenotazione": booking}


if __name__ == "__main__":
    server.run()
