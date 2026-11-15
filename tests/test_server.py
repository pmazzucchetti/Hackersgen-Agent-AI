"""Rules of the simulated class register: who can read and change what."""

import asyncio
import json

import pytest
from mcp import Client

import dati
import server


@pytest.fixture(autouse=True)
def stato_pulito(tmp_path, monkeypatch):
    monkeypatch.setattr(dati, "STATO_FILE", tmp_path / "stato.json")


def chiama(strumento: str, **argomenti):
    async def run():
        async with Client(server.server) as client:
            return await client.call_tool(strumento, argomenti)

    risultato = asyncio.run(run())
    contenuto = risultato.structured_content
    if contenuto is None:  # plain dict results come back as JSON text only
        return json.loads(risultato.content[0].text)
    return contenuto["result"] if set(contenuto) == {"result"} else contenuto


def test_studente_vede_i_suoi_voti():
    voti = chiama("voti", utente="luca", studente="luca")
    assert isinstance(voti, list) and voti


def test_studente_non_vede_voti_altrui():
    assert "errore" in chiama("voti", utente="luca", studente="marco")


def test_professore_vede_tutti():
    assert isinstance(chiama("voti", utente="prof.rossi", studente="marco"), list)


def test_studente_non_cambia_voti():
    assert "errore" in chiama("cambia_voto", utente="luca", studente="luca", materia="matematica", voto=9)


def test_professore_cambia_voto():
    chiama("cambia_voto", utente="prof.rossi", studente="luca", materia="matematica", voto=9)
    voti = chiama("voti", utente="prof.rossi", studente="luca")
    assert any(v["materia"] == "matematica" and v["voto"] == 9 for v in voti)


def test_utente_sconosciuto():
    assert "errore" in chiama("voti", utente="pippo", studente="luca")


def test_nome_normalizzato():
    assert chiama("voti", utente="Luca ", studente="luca") == chiama("voti", utente="luca", studente="luca")


def test_data_non_valida():
    risposta = chiama("compiti", utente="luca", data="giovedì")
    assert "errore" in risposta and "AAAA-MM-GG" in risposta["errore"]


def test_promemoria_aggiunto_e_letto():
    chiama("aggiungi_promemoria", utente="luca", testo="Ripassare storia", data="2026-12-02")
    assert any(p["testo"] == "Ripassare storia" for p in chiama("promemoria", utente="luca"))


def test_azzera():
    iniziali = chiama("voti", utente="prof.rossi", studente="luca")
    chiama("cambia_voto", utente="prof.rossi", studente="luca", materia="matematica", voto=2)
    dati.azzera()
    assert chiama("voti", utente="prof.rossi", studente="luca") == iniziali


def test_verifiche_della_classe():
    verifiche = chiama("verifiche", utente="luca")
    assert all({"materia", "data", "argomenti"} <= set(v) for v in verifiche)


def test_descrizioni_senza_regole_di_permesso():
    async def run():
        async with Client(server.server) as client:
            return (await client.list_tools()).tools

    for strumento in asyncio.run(run()):
        assert "solo" not in (strumento.description or "").lower(), strumento.name
