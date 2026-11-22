"""La chat nel browser, invece che nel terminale.

Codice già pronto, come la chat di config.py: non serve leggerlo per seguire le lezioni.
Si attiva aggiungendo --web al comando, per esempio:

    uv run lezione4/06_assistente.py --web

Avvia un piccolo server web sul tuo computer (raggiungibile solo da lì) e apre la pagina.
A destra, il playground: i passi fatti dietro le quinte per ogni domanda (contesto mandato
al modello, strumenti chiesti, chiamate MCP, risultati) e il registro di tutte le azioni.
"""

import contextlib
import io
import json
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

INDIRIZZO = "127.0.0.1"  # solo il tuo computer: nessun altro può collegarsi
PORTE = range(8000, 8010)


def avvia(rispondi, nome: str) -> None:
    """Serve la pagina e passa ogni domanda a `rispondi`, come la chat nel terminale."""
    server = _server_libero(_gestore(rispondi, nome))
    url = f"http://{INDIRIZZO}:{server.server_port}"
    print(f"La chat è aperta nel browser: {url}  (Ctrl+C per chiudere)")
    webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    print("\nCiao!")


def _server_libero(gestore) -> HTTPServer:
    for porta in PORTE:
        try:
            return HTTPServer((INDIRIZZO, porta), gestore)
        except OSError:  # porta già occupata: proviamo la successiva
            continue
    raise SystemExit(f"Nessuna porta libera fra {PORTE.start} e {PORTE.stop - 1}: chiudi le altre chat")


def _traccia():
    """Il modulo del tracciamento, se il client del modello è stato avvolto (vedi traccia.py)."""
    return sys.modules.get("traccia")


def _rispondi_catturando(rispondi, domanda: str) -> dict:
    """Esegue `rispondi`, raccoglie quello che stampa e i passi fatti dietro le quinte."""
    traccia = _traccia()
    if traccia:
        traccia.nuovo_turno(domanda)
    stampato = io.StringIO()
    try:
        with contextlib.redirect_stdout(stampato):
            risposta = rispondi(domanda)
    except Exception as errore:  # noqa: BLE001 - qualunque errore va mostrato nella pagina, non perso
        risposta = f"Si è verificato un errore: {errore}"
    righe = [r.strip() for r in stampato.getvalue().splitlines() if r.strip()]
    print("\n".join(righe))  # resta visibile anche nel terminale
    passi = list(traccia.TURNO) if traccia else []
    registro = list(traccia.REGISTRO) if traccia else []
    return {"risposta": risposta or "", "dietro": righe, "passi": passi, "registro": registro}


def _gestore(rispondi, nome: str):
    traccia = _traccia()
    avvio = json.dumps(traccia.AVVIO if traccia else [], ensure_ascii=False).replace("</", "<\\/")
    pagina = PAGINA.replace("{{NOME}}", json.dumps(nome)).replace("{{AVVIO}}", avvio).encode("utf-8")

    class Gestore(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802 - nome imposto da http.server
            if self.path != "/":
                return self._invia(404, b"Non trovato", "text/plain; charset=utf-8")
            self._invia(200, pagina, "text/html; charset=utf-8")

        def do_POST(self):  # noqa: N802 - nome imposto da http.server
            if self.path != "/domanda":
                return self._invia(404, b"Non trovato", "text/plain; charset=utf-8")
            if not self._dalla_nostra_pagina():
                return self._invia(403, b'{"errore": "richiesta non ammessa"}', "application/json")
            lunghezza = min(int(self.headers.get("Content-Length", 0)), 20_000)
            try:
                domanda = str(json.loads(self.rfile.read(lunghezza))["domanda"]).strip()
            except (ValueError, KeyError, TypeError):
                return self._invia(400, b'{"errore": "richiesta non valida"}', "application/json")
            corpo = _rispondi_catturando(rispondi, domanda)
            self._invia(200, json.dumps(corpo, ensure_ascii=False).encode("utf-8"), "application/json")

        def _dalla_nostra_pagina(self) -> bool:
            """Accetta solo richieste JSON fatte dalla nostra pagina, non da altri siti aperti nel browser."""
            porta = self.server.server_port
            host_ok = self.headers.get("Host") in (f"{INDIRIZZO}:{porta}", f"localhost:{porta}")
            json_ok = self.headers.get("Content-Type", "").startswith("application/json")
            return host_ok and json_ok

        def _invia(self, stato, corpo, tipo):
            self.send_response(stato)
            self.send_header("Content-Type", tipo)
            self.send_header("Content-Length", str(len(corpo)))
            self.end_headers()
            self.wfile.write(corpo)

        def log_message(self, *argomenti):  # niente righe di log del server nel terminale
            pass

    return Gestore


PAGINA = """<!doctype html>
<html lang="it"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Playground dell'assistente</title>
<style>
  :root { --sfondo:#0b1024; --card:#121933; --card2:#0e1530; --bordo:#26304f; --testo:#eef1fa;
          --tenue:#9aa6c8; --arancio:#f08c2b; --verde:#3fd07a; --azzurro:#7fb2ff; --rosso:#ff7a7a; }
  * { box-sizing:border-box; }
  body { margin:0; height:100vh; display:flex; flex-direction:column; color:var(--testo);
         font:15px/1.45 system-ui, sans-serif;
         background:radial-gradient(circle at 20% 0%, #0f5f6b 0, transparent 45%),
                    radial-gradient(circle at 90% 0%, #5b2a72 0, transparent 40%), var(--sfondo); }
  header { padding:16px 24px; font-weight:700; font-size:21px; }
  header span { color:var(--arancio); }
  header small { font-weight:400; color:var(--tenue); font-size:14px; margin-left:8px; }
  main { flex:1; display:grid; grid-template-columns:1fr 1.25fr; gap:16px; padding:0 24px 24px; min-height:0; }
  section { background:var(--card); border:1px solid var(--bordo); border-radius:14px;
            display:flex; flex-direction:column; min-height:0; }
  .testa { display:flex; gap:4px; padding:8px 10px 0; border-bottom:1px solid var(--bordo); }
  .testa h2, .testa button { margin:0; padding:8px 12px; font-size:12px; letter-spacing:.08em;
            text-transform:uppercase; color:var(--tenue); background:none; border:0; font-weight:700;
            border-bottom:2px solid transparent; cursor:pointer; }
  .testa h2 { color:var(--arancio); cursor:default; }
  .testa button.attiva { color:var(--arancio); border-bottom-color:var(--arancio); }
  .scorre { flex:1; overflow-y:auto; padding:14px; }
  .nascosto { display:none; }
  .msg { max-width:88%; margin:0 0 12px; padding:10px 14px; border-radius:12px; white-space:pre-wrap; }
  .tu { margin-left:auto; background:#24305a; }
  .ada { background:#1a2244; border:1px solid var(--bordo); }
  .attesa { color:var(--tenue); font-style:italic; }
  form { display:flex; gap:8px; padding:12px; border-top:1px solid var(--bordo); }
  input { flex:1; padding:12px; border-radius:10px; border:1px solid var(--bordo);
          background:#0b1024; color:var(--testo); font-size:15px; }
  form button { padding:0 20px; border:0; border-radius:10px; background:var(--arancio); color:#111;
                font-weight:700; cursor:pointer; }
  .turno { margin:4px 0 10px; padding:6px 10px; border-radius:8px; background:#24305a; font-weight:600; }
  .passo { display:grid; grid-template-columns:30px 1fr; gap:4px 10px; padding:9px 10px; margin-bottom:8px;
           background:var(--card2); border:1px solid var(--bordo); border-radius:10px; }
  .icona { grid-row:span 3; font-size:19px; line-height:1.3; text-align:center; }
  .titolo { font-weight:650; }
  .titolo .ms { float:right; font-weight:400; color:var(--tenue); font-size:12px; }
  .riassunto { font:12.5px/1.45 ui-monospace, Menlo, monospace; color:var(--verde); word-break:break-word; }
  .spiega { font-size:12.5px; color:var(--tenue); }
  details { grid-column:2; }
  summary { cursor:pointer; color:var(--azzurro); font-size:12.5px; }
  pre { margin:6px 0 0; padding:8px; max-height:280px; overflow:auto; background:#070b1a;
        border-radius:8px; font:12px/1.4 ui-monospace, Menlo, monospace; color:#d6def5; white-space:pre-wrap; }
  .avvio { color:var(--tenue); font-size:13px; margin-bottom:6px; }
  table { width:100%; border-collapse:collapse; font-size:13px; }
  th { text-align:left; color:var(--tenue); font-weight:600; padding:6px; border-bottom:1px solid var(--bordo);
       position:sticky; top:-14px; background:var(--card); }
  td { padding:6px; border-bottom:1px solid var(--bordo); vertical-align:top; word-break:break-word; }
  td.mono { font:12px/1.4 ui-monospace, Menlo, monospace; }
  td.stretto, td.si, td.no { white-space:nowrap; }
  td.no { color:var(--rosso); } td.si { color:var(--verde); }
  .vuoto { color:var(--tenue); font-style:italic; }
  @media (max-width:900px) { main { grid-template-columns:1fr; } }
</style></head>
<body>
<header><span id="nome"></span> · l'assistente della 4B <small>playground</small></header>
<main>
  <section>
    <div class="testa"><h2>Chat</h2></div>
    <div class="scorre" id="chat"></div>
    <form id="form"><input id="domanda" autocomplete="off" placeholder="Scrivi la tua domanda…" autofocus>
    <button>Invia</button></form>
  </section>
  <section>
    <div class="testa">
      <button class="attiva" data-scheda="passi">Dietro le quinte</button>
      <button data-scheda="registro">Registro delle azioni</button>
    </div>
    <div class="scorre" id="passi"></div>
    <div class="scorre nascosto" id="registro">
      <table><thead><tr><th>Ora</th><th>Utente collegato</th><th>Domanda</th><th>Strumento</th>
      <th>Argomenti</th><th>Esito</th></tr></thead><tbody id="righe"></tbody></table>
      <p class="vuoto" id="registro-vuoto">Nessuna azione per ora: le azioni compaiono quando l'assistente usa uno strumento.</p>
    </div>
  </section>
</main>
<script>
const NOME = {{NOME}};
const AVVIO = {{AVVIO}};
const ICONE = {contesto: "🧾", modello: "🧠", strumento: "🔧", mcp: "🔌", risultato: "↩️",
               embedding: "📚", risposta: "✅"};
document.getElementById("nome").textContent = NOME;
const chat = document.getElementById("chat"), passi = document.getElementById("passi");

function el(tag, classe, testo) {
  const e = document.createElement(tag);
  if (classe) e.className = classe;
  if (testo !== undefined) e.textContent = testo;  // sempre testo, mai HTML
  return e;
}

function scorriInFondo(contenitore) { contenitore.scrollTop = contenitore.scrollHeight; }

function mostraPasso(p, dove) {
  const box = el("div", "passo");
  box.appendChild(el("div", "icona", ICONE[p.tipo] || "•"));
  const titolo = el("div", "titolo", p.titolo);
  if (p.ms !== null && p.ms !== undefined) titolo.appendChild(el("span", "ms", p.ms + " ms"));
  box.appendChild(titolo);
  box.appendChild(el("div", "riassunto", p.riassunto));
  box.appendChild(el("div", "spiega", p.spiega));
  if (p.dettaglio !== null && p.dettaglio !== undefined) {
    const d = el("details");
    d.appendChild(el("summary", "", "vedi i dati veri (JSON)"));
    d.appendChild(el("pre", "", JSON.stringify(p.dettaglio, null, 2)));
    box.appendChild(d);
  }
  dove.appendChild(box);
}

function mostraRegistro(righe) {
  const corpo = document.getElementById("righe");
  corpo.textContent = "";
  document.getElementById("registro-vuoto").style.display = righe.length ? "none" : "block";
  righe.slice().reverse().forEach((r) => {
    const tr = el("tr");
    tr.appendChild(el("td", "stretto", r.ora));
    tr.appendChild(el("td", "", r.utente_collegato));
    tr.appendChild(el("td", "", r.domanda));
    tr.appendChild(el("td", "mono", r.strumento));
    tr.appendChild(el("td", "mono", JSON.stringify(r.argomenti)));
    tr.appendChild(el("td", r.esito === "eseguito" ? "si" : "no", r.esito));
    corpo.appendChild(tr);
  });
}

document.querySelectorAll(".testa button").forEach((b) => b.addEventListener("click", () => {
  document.querySelectorAll(".testa button").forEach((x) => x.classList.toggle("attiva", x === b));
  document.getElementById("passi").classList.toggle("nascosto", b.dataset.scheda !== "passi");
  document.getElementById("registro").classList.toggle("nascosto", b.dataset.scheda !== "registro");
}));

if (AVVIO.length) {
  passi.appendChild(el("div", "avvio", "All'avvio del programma:"));
  AVVIO.forEach((p) => mostraPasso(p, passi));
}

document.getElementById("form").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const campo = document.getElementById("domanda"), domanda = campo.value.trim();
  if (!domanda) return;
  campo.value = "";
  chat.appendChild(el("div", "msg tu", domanda));
  passi.appendChild(el("div", "turno", "› " + domanda));
  const attesa = el("div", "msg ada attesa", NOME + " sta pensando…");
  chat.appendChild(attesa);
  scorriInFondo(chat); scorriInFondo(passi);
  try {
    const r = await fetch("/domanda", {method: "POST", headers: {"Content-Type": "application/json"},
                                       body: JSON.stringify({domanda})});
    const dati = await r.json();
    attesa.remove();
    dati.passi.forEach((p) => mostraPasso(p, passi));
    if (!dati.passi.length) dati.dietro.forEach((riga) => passi.appendChild(el("div", "riassunto", riga)));
    mostraRegistro(dati.registro);
    chat.appendChild(el("div", "msg ada", dati.risposta));
  } catch (errore) {
    attesa.textContent = "Il programma non risponde: è ancora acceso nel terminale?";
  }
  scorriInFondo(chat); scorriInFondo(passi);
});
</script>
</body></html>
"""
