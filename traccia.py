"""Il tracciamento del playground: registra cosa succede dietro le quinte.

Codice già pronto, come interfaccia.py: si attiva da solo con --web e non cambia niente
nei file delle lezioni. "Avvolge" il client del modello e il collegamento al registro:
ogni chiamata passa di qui, viene annotata come un passo e poi prosegue normalmente.

È l'osservabilità in piccolo: nelle aziende si usano strumenti come Langfuse o
AgentCore Observability, ma l'idea è la stessa.
"""

import json
import sys
import time
from datetime import datetime

import config

AVVIO = []  # i passi fatti prima della prima domanda (strumenti caricati, documenti indicizzati)
TURNO = []  # i passi della domanda in corso
REGISTRO = []  # l'audit: ogni strumento eseguito, in ogni domanda
_stato = {"domanda": None, "giro": 0, "strumenti_chiesti": {}, "risultati_visti": set(), "id_mcp": 0}

SPIEGA = {
    "contesto": "A ogni giro mandiamo al modello TUTTA la conversazione: il modello non ricorda niente.",
    "modello": "Il modello risponde con del testo, oppure chiede di usare uno strumento.",
    "strumento": "Il modello non esegue niente: scrive un JSON con nome e argomenti. Lo esegue il nostro codice.",
    "mcp": "Il nostro programma chiede al registro (un server MCP) di eseguire lo strumento.",
    "risultato": "Il risultato torna al modello come un messaggio con ruolo \"tool\".",
    "embedding": "Il testo diventa una lista di numeri: così si cercano i pezzi di documento più simili.",
    "risposta": "Il modello non chiede altri strumenti: questa è la risposta finale.",
}


def attiva(client):
    """Avvolge il client del modello e il registro, se presente. Restituisce il client."""
    client.chat.completions.create = _avvolgi_modello(client.chat.completions.create)
    client.embeddings.create = _avvolgi_embedding(client.embeddings.create)
    registro = sys.modules.get("registro")  # solo le lezioni che usano il registro della scuola
    if registro is not None:
        if not getattr(registro.chiama, "_tracciata", False):
            registro.chiama = _avvolgi_mcp(registro.chiama)
            registro.strumenti = _avvolgi_elenco(registro.strumenti)
    return client


def nuovo_turno(domanda):
    """Le chiamate già viste restano in memoria: la conversazione rimanda anche i risultati vecchi."""
    TURNO.clear()
    _stato.update(domanda=domanda, giro=0)


def utente_collegato():
    """Chi usa l'assistente: la variabile `utente` della lezione, se c'è, altrimenti config.UTENTE."""
    return getattr(sys.modules.get("__main__"), "utente", config.UTENTE)


def _passo(tipo, titolo, riassunto, dettaglio=None, ms=None):
    passo = {"tipo": tipo, "titolo": titolo, "riassunto": riassunto, "spiega": SPIEGA[tipo],
             "dettaglio": dettaglio, "ms": ms}
    (TURNO if _stato["domanda"] is not None else AVVIO).append(passo)


def _come_dict(messaggio):
    return messaggio if isinstance(messaggio, dict) else messaggio.model_dump(exclude_none=True)


def _avvolgi_modello(crea):
    def crea_tracciato(**richiesta):
        messaggi = [_come_dict(m) for m in richiesta.get("messages", [])]
        _risultati_nuovi(messaggi)
        _stato["giro"] += 1
        strumenti = [s["function"]["name"] for s in richiesta.get("tools") or []]
        ruoli = ", ".join(m["role"] for m in messaggi)
        _passo("contesto", f"Contesto inviato al modello (giro {_stato['giro']})",
               f"{len(messaggi)} messaggi ({ruoli}) · strumenti offerti: {', '.join(strumenti) or 'nessuno'}",
               {"messages": messaggi, "tools": strumenti})
        inizio = time.monotonic()
        risposta = crea(**richiesta)
        _risposta_modello(risposta, int((time.monotonic() - inizio) * 1000))
        return risposta

    return crea_tracciato


def _risposta_modello(risposta, ms):
    messaggio = risposta.choices[0].message
    uso = risposta.usage
    token = f"{uso.prompt_tokens} token in · {uso.completion_tokens} out" if uso else ""
    if not messaggio.tool_calls:
        _passo("risposta", "Risposta finale del modello", f"{token} · {ms} ms",
               {"content": messaggio.content}, ms)
        return
    _passo("modello", f"Il modello chiede {len(messaggio.tool_calls)} strumento/i", f"{token} · {ms} ms",
           _come_dict(messaggio), ms)
    for chiamata in messaggio.tool_calls:
        nome, argomenti = chiamata.function.name, chiamata.function.arguments or "{}"
        _stato["strumenti_chiesti"][chiamata.id] = (nome, argomenti)
        _passo("strumento", f"Tool call: {nome}", argomenti, {"name": nome, "arguments": json.loads(argomenti)})


def _risultati_nuovi(messaggi):
    """I messaggi "tool" aggiunti dopo l'ultimo giro: i risultati degli strumenti eseguiti."""
    for m in messaggi:
        if m.get("role") != "tool" or m.get("tool_call_id") in _stato["risultati_visti"]:
            continue
        _stato["risultati_visti"].add(m.get("tool_call_id"))
        nome, argomenti = _stato["strumenti_chiesti"].get(m.get("tool_call_id"), ("?", "{}"))
        _passo("risultato", f"Risultato di {nome} rimandato al modello", m.get("content", "")[:160],
               _json_o_testo(m.get("content", "")))
        _annota(nome, argomenti, m.get("content", ""))


def _annota(nome, argomenti, contenuto):
    risultato = _json_o_testo(contenuto)
    errore = risultato.get("errore") if isinstance(risultato, dict) else None
    REGISTRO.append({"ora": datetime.now().strftime("%H:%M:%S"), "utente_collegato": utente_collegato(),
                     "domanda": _stato["domanda"], "strumento": nome, "argomenti": _json_o_testo(argomenti),
                     "esito": f"rifiutato: {errore}" if errore else "eseguito"})


def _json_o_testo(testo):
    try:
        return json.loads(testo)
    except (ValueError, TypeError):
        return testo


def _avvolgi_embedding(crea):
    def crea_tracciato(**richiesta):
        testi = richiesta.get("input", [])
        testi = [testi] if isinstance(testi, str) else list(testi)
        inizio = time.monotonic()
        risposta = crea(**richiesta)
        ms = int((time.monotonic() - inizio) * 1000)
        dimensioni = len(risposta.data[0].embedding) if risposta.data else 0
        _passo("embedding", f"Embedding di {len(testi)} testo/i", f"{dimensioni} numeri per testo · {ms} ms",
               {"testi": [t[:120] for t in testi[:5]], "primi_numeri": risposta.data[0].embedding[:8]}, ms)
        return risposta

    return crea_tracciato


def _avvolgi_mcp(chiama):
    def chiama_tracciata(nome, argomenti):
        _stato["id_mcp"] += 1
        richiesta = {"jsonrpc": "2.0", "id": _stato["id_mcp"], "method": "tools/call",
                     "params": {"name": nome, "arguments": argomenti}}
        inizio = time.monotonic()
        risultato = chiama(nome, argomenti)
        ms = int((time.monotonic() - inizio) * 1000)
        _passo("mcp", f"MCP → registro: tools/call {nome}", f"risponde in {ms} ms",
               {"richiesta": richiesta, "risposta": _json_o_testo(risultato)}, ms)
        return risultato

    chiama_tracciata._tracciata = True
    return chiama_tracciata


def _avvolgi_elenco(strumenti):
    def strumenti_tracciati():
        elenco = strumenti()
        _passo("mcp", "MCP → registro: tools/list", f"{len(elenco)} strumenti: "
               + ", ".join(s["function"]["name"] for s in elenco),
               {"richiesta": {"jsonrpc": "2.0", "id": 0, "method": "tools/list"}, "strumenti": elenco})
        return elenco

    return strumenti_tracciati
