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


def test_chiama_errore_di_validazione_resta_json():
    risposta = json.loads(registro.chiama("cambia_voto", {"utente": "luca"}))
    assert "errore" in risposta


def test_controlla_modello_mancante(capsys):
    with pytest.raises(SystemExit):
        config.controlla_modello("modello-che-non-esiste")
    assert "ollama pull modello-che-non-esiste" in capsys.readouterr().out


def _input_da(righe):
    iteratore = iter(righe)

    def finto_input(_prompt=""):
        riga = next(iteratore)
        if isinstance(riga, BaseException):
            raise riga
        return riga

    return finto_input


def test_chat_passa_le_domande_e_stampa_le_risposte(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", _input_da(["ciao", "come va?", "esci"]))
    ricevute = []
    config.chat(lambda domanda: ricevute.append(domanda) or f"eco: {domanda}")
    assert ricevute == ["ciao", "come va?"]
    assert "eco: come va?" in capsys.readouterr().out


def test_chat_ignora_le_righe_vuote(monkeypatch):
    monkeypatch.setattr("builtins.input", _input_da(["", "   ", "esci"]))
    ricevute = []
    config.chat(lambda domanda: ricevute.append(domanda) or "")
    assert ricevute == []


def test_chat_ctrl_c_durante_la_risposta(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", _input_da(["domanda"]))

    def interrotta(_domanda):
        raise KeyboardInterrupt

    config.chat(interrotta)
    assert "Ciao" in capsys.readouterr().out


def test_chat_fine_input(monkeypatch):
    monkeypatch.setattr("builtins.input", _input_da([EOFError()]))
    config.chat(lambda domanda: "mai chiamata")
