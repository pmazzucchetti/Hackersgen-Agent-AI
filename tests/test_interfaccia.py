"""The browser chat: answers through the lesson's function, refuses foreign requests."""

import json
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import interfaccia  # noqa: E402


@pytest.fixture
def server():
    def rispondi(domanda):
        print(f"  [strumento: eco {domanda}]")
        return f"Hai chiesto: {domanda}"

    srv = interfaccia._server_libero(interfaccia._gestore(rispondi, "Ada"))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_port}"
    srv.shutdown()
    srv.server_close()


def _post(url, corpo, tipo="application/json"):
    richiesta = urllib.request.Request(url + "/domanda", data=corpo, headers={"Content-Type": tipo})
    with urllib.request.urlopen(richiesta, timeout=5) as risposta:
        return json.loads(risposta.read())


def test_pagina_con_il_nome(server):
    with urllib.request.urlopen(server, timeout=5) as risposta:
        assert '"Ada"' in risposta.read().decode()


def test_domanda_risposta_e_dietro_le_quinte(server):
    dati = _post(server, json.dumps({"domanda": "ciao"}).encode())
    assert dati["risposta"] == "Hai chiesto: ciao"
    assert dati["dietro"] == ["[strumento: eco ciao]"]


def test_rifiuta_richieste_non_json(server):
    with pytest.raises(urllib.error.HTTPError) as errore:
        _post(server, b'{"domanda": "ciao"}', tipo="text/plain")
    assert errore.value.code == 403


def test_richiesta_non_valida(server):
    with pytest.raises(urllib.error.HTTPError) as errore:
        _post(server, b"non json")
    assert errore.value.code == 400
