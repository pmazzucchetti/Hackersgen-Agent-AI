"""Shared modules: the sync school client and the model check."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import config  # noqa: E402
import registro  # noqa: E402


def test_strumenti_formato_openai():
    strumenti = registro.strumenti()
    assert strumenti and all(s["type"] == "function" and s["function"]["name"] for s in strumenti)


def test_chiama_restituisce_testo():
    risposta = registro.chiama("verifiche", {"utente": "luca"})
    assert isinstance(json.loads(risposta), list)


def test_controlla_modello_ollama_spento(monkeypatch, capsys):
    monkeypatch.setattr(config, "INDIRIZZO", "http://localhost:11999/v1")
    with pytest.raises(SystemExit):
        config.controlla_modello()
    assert "Ollama" in capsys.readouterr().out
