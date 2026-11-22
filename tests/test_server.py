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


def test_sportelli_di_una_materia():
    sportelli = chiama("sportelli", utente="luca", materia="Matematica")
    assert sportelli and all(s["materia"] == "matematica" for s in sportelli)
    assert all({"data", "ora", "professore", "aula", "posti_liberi", "prenotato"} <= set(s) for s in sportelli)


def test_sportelli_senza_materia_li_elenca_tutti():
    materie = {s["materia"] for s in chiama("sportelli", utente="luca")}
    assert {"matematica", "storia", "inglese"} <= materie


def test_prenota_sportello_toglie_un_posto():
    prima = _sportello("luca", "matematica", "2026-12-02")
    risposta = chiama("prenota_sportello", utente="luca", materia="matematica", data="2026-12-02")
    dopo = _sportello("luca", "matematica", "2026-12-02")
    assert risposta["fatto"] is True
    assert dopo["posti_liberi"] == prima["posti_liberi"] - 1 and dopo["prenotato"] is True


def test_sportello_pieno():
    risposta = chiama("prenota_sportello", utente="luca", materia="matematica", data="2026-12-01")
    assert "pieno" in risposta["errore"]


def test_sportello_gia_prenotato():
    chiama("prenota_sportello", utente="luca", materia="storia", data="2026-12-03")
    risposta = chiama("prenota_sportello", utente="luca", materia="storia", data="2026-12-03")
    assert "già" in risposta["errore"]


def test_sportello_inesistente():
    risposta = chiama("prenota_sportello", utente="luca", materia="storia", data="2026-12-02")
    assert "errore" in risposta and "sportelli" in risposta["errore"]


def test_prenota_sportello_data_non_valida():
    risposta = chiama("prenota_sportello", utente="luca", materia="storia", data="giovedì")
    assert "AAAA-MM-GG" in risposta["errore"]


def _sportello(utente, materia, data):
    return next(s for s in chiama("sportelli", utente=utente, materia=materia) if s["data"] == data)


def test_azzera():
    iniziali = chiama("voti", utente="prof.rossi", studente="luca")
    sportelli = chiama("sportelli", utente="luca")
    chiama("cambia_voto", utente="prof.rossi", studente="luca", materia="matematica", voto=2)
    chiama("prenota_sportello", utente="luca", materia="matematica", data="2026-12-02")
    dati.azzera()
    assert chiama("voti", utente="prof.rossi", studente="luca") == iniziali
    assert chiama("sportelli", utente="luca") == sportelli


def test_verifiche_della_classe():
    verifiche = chiama("verifiche", utente="luca")
    assert all({"materia", "data", "argomenti"} <= set(v) for v in verifiche)


def test_descrizioni_senza_regole_di_permesso():
    async def run():
        async with Client(server.server) as client:
            return (await client.list_tools()).tools

    for strumento in asyncio.run(run()):
        assert "solo" not in (strumento.description or "").lower(), strumento.name


def test_stato_salvato_prima_degli_sportelli():
    dati.STATO_FILE.write_text(json.dumps({"voti": {}, "promemoria": {}}), encoding="utf-8")
    assert chiama("sportelli", utente="luca", materia="storia")
