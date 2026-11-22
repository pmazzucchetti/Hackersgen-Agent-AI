"""The playground tracing: steps of a turn and the audit of every tool run."""

import json
import sys
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import traccia  # noqa: E402


@pytest.fixture(autouse=True)
def traccia_pulita():
    traccia.AVVIO.clear()
    traccia.REGISTRO.clear()
    traccia._stato.update(domanda=None, strumenti_chiesti={}, risultati_visti=set())
    yield


def _risposta(contenuto=None, chiamate=None):
    messaggio = NS(content=contenuto, tool_calls=chiamate,
                   model_dump=lambda **_: {"role": "assistant", "content": contenuto})
    return NS(choices=[NS(message=messaggio)], usage=NS(prompt_tokens=10, completion_tokens=2))


def _chiamata(id_, nome, argomenti):
    return NS(id=id_, function=NS(name=nome, arguments=json.dumps(argomenti)))


def test_turno_con_strumento_e_risposta():
    risposte = iter([_risposta(chiamate=[_chiamata("c1", "voti", {"utente": "luca"})]),
                     _risposta(contenuto="Hai 6 in matematica")])
    crea = traccia._avvolgi_modello(lambda **_: next(risposte))
    traccia.nuovo_turno("i miei voti?")
    crea(messages=[{"role": "user", "content": "i miei voti?"}], tools=[{"function": {"name": "voti"}}])
    crea(messages=[{"role": "user", "content": "i miei voti?"},
                   {"role": "tool", "tool_call_id": "c1", "content": '{"errore": "no"}'}])
    tipi = [p["tipo"] for p in traccia.TURNO]
    assert tipi == ["contesto", "modello", "strumento", "risultato", "contesto", "risposta"]
    assert traccia.REGISTRO[0]["strumento"] == "voti"
    assert traccia.REGISTRO[0]["esito"] == "rifiutato: no"
    assert traccia.REGISTRO[0]["domanda"] == "i miei voti?"


def test_passi_prima_della_prima_domanda_vanno_in_avvio():
    elenco = traccia._avvolgi_elenco(lambda: [{"function": {"name": "voti"}}])
    elenco()
    assert traccia.AVVIO and traccia.AVVIO[0]["tipo"] == "mcp"


def test_chiamata_mcp_mostra_la_richiesta_json_rpc():
    chiama = traccia._avvolgi_mcp(lambda nome, argomenti: '{"fatto": true}')
    traccia.nuovo_turno("prenota")
    assert chiama("prenota_sportello", {"materia": "storia"}) == '{"fatto": true}'
    richiesta = traccia.TURNO[-1]["dettaglio"]["richiesta"]
    assert richiesta["method"] == "tools/call" and richiesta["params"]["name"] == "prenota_sportello"


def test_i_risultati_dei_turni_prima_non_si_ripetono():
    risposte = iter([_risposta(chiamate=[_chiamata("c1", "voti", {})]), _risposta(contenuto="ok"),
                     _risposta(contenuto="ancora ok")])
    crea = traccia._avvolgi_modello(lambda **_: next(risposte))
    conversazione = [{"role": "user", "content": "voti?"}]
    traccia.nuovo_turno("voti?")
    crea(messages=conversazione)
    conversazione.append({"role": "tool", "tool_call_id": "c1", "content": "[]"})
    crea(messages=conversazione)
    traccia.nuovo_turno("grazie")
    crea(messages=conversazione + [{"role": "user", "content": "grazie"}])
    assert len(traccia.REGISTRO) == 1
    assert [p["tipo"] for p in traccia.TURNO] == ["contesto", "risposta"]
