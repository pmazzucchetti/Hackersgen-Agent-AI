"""Simulated class register exposed over MCP: tests, homework, grades, reminders.

It is the "outside world" our agent talks to. Data are fake (see dati.py).
Start it with `uv run scuola/server.py`; start over with `uv run scuola/server.py --azzera`.
"""

import sys
from datetime import date

from mcp.server.mcpserver import MCPServer

import dati

server = MCPServer("registro", instructions="Registro elettronico della classe 4B.")


def _chi_e(utente: str) -> tuple[str, str | None]:
    nome = utente.strip().lower()
    return nome, dati.UTENTI.get(nome)


def _data_valida(testo: str) -> bool:
    try:
        date.fromisoformat(testo)
    except ValueError:
        return False
    return True


@server.tool()
def verifiche(utente: str) -> list[dict] | dict:
    """Elenca le prossime verifiche della classe, con data e argomenti."""
    if _chi_e(utente)[1] is None:
        return {"errore": f"Utente sconosciuto: {utente}"}
    return dati.VERIFICHE


@server.tool()
def compiti(utente: str, data: str) -> list[dict] | dict:
    """Elenca i compiti da fare per una certa data (formato AAAA-MM-GG)."""
    if _chi_e(utente)[1] is None:
        return {"errore": f"Utente sconosciuto: {utente}"}
    if not _data_valida(data):
        return {"errore": f"Data non valida: {data}. Usa il formato AAAA-MM-GG"}
    return dati.COMPITI.get(data, [])


@server.tool()
def voti(utente: str, studente: str) -> list[dict] | dict:
    """Mostra i voti di uno studente. Uno studente può vedere solo i propri."""
    nome, ruolo = _chi_e(utente)
    studente = studente.strip().lower()
    if ruolo is None:
        return {"errore": f"Utente sconosciuto: {utente}"}
    if ruolo == "studente" and studente != nome:
        return {"errore": "Uno studente può vedere solo i propri voti"}
    return dati.carica_stato()["voti"].get(studente, [])


@server.tool()
def cambia_voto(utente: str, studente: str, materia: str, voto: float) -> dict:
    """Inserisce o cambia il voto di uno studente in una materia."""
    if _chi_e(utente)[1] != "professore":
        return {"errore": "Solo i professori possono cambiare un voto"}
    stato = dati.carica_stato()
    voti_studente = stato["voti"].setdefault(studente.strip().lower(), [])
    voti_studente[:] = [v for v in voti_studente if v["materia"] != materia]
    voti_studente.append({"materia": materia, "voto": voto})
    dati.salva_stato(stato)
    return {"fatto": True, "studente": studente, "materia": materia, "voto": voto}


@server.tool()
def aggiungi_promemoria(utente: str, testo: str, data: str) -> dict:
    """Aggiunge un promemoria all'agenda dell'utente per una data (formato AAAA-MM-GG)."""
    nome, ruolo = _chi_e(utente)
    if ruolo is None:
        return {"errore": f"Utente sconosciuto: {utente}"}
    if not _data_valida(data):
        return {"errore": f"Data non valida: {data}. Usa il formato AAAA-MM-GG"}
    stato = dati.carica_stato()
    stato["promemoria"].setdefault(nome, []).append({"testo": testo, "data": data})
    dati.salva_stato(stato)
    return {"fatto": True, "promemoria": {"testo": testo, "data": data}}


@server.tool()
def promemoria(utente: str) -> list[dict] | dict:
    """Elenca i promemoria dell'utente."""
    nome, ruolo = _chi_e(utente)
    if ruolo is None:
        return {"errore": f"Utente sconosciuto: {utente}"}
    return dati.carica_stato()["promemoria"].get(nome, [])


if __name__ == "__main__":
    if "--azzera" in sys.argv:
        dati.azzera()
        print("Registro riportato ai dati iniziali.")
    else:
        server.run()
