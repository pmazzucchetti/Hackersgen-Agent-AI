"""La chat nel browser, invece che nel terminale.

Codice già pronto, come la chat di config.py: non serve leggerlo per seguire le lezioni.
Si attiva aggiungendo --web al comando, per esempio:

    uv run lezione4/06_assistente.py --web

Avvia un piccolo server web sul tuo computer (raggiungibile solo da lì) e apre la pagina.
A destra, "dietro le quinte", compare quello che il programma stampa mentre l'assistente
lavora: strumenti chiamati, argomenti, token.
"""

import contextlib
import io
import json
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


def _rispondi_catturando(rispondi, domanda: str) -> dict:
    """Esegue `rispondi` e raccoglie quello che stampa, per mostrarlo nella pagina."""
    stampato = io.StringIO()
    try:
        with contextlib.redirect_stdout(stampato):
            risposta = rispondi(domanda)
    except Exception as errore:  # noqa: BLE001 - qualunque errore va mostrato nella pagina, non perso
        risposta = f"Si è verificato un errore: {errore}"
    righe = [r.strip() for r in stampato.getvalue().splitlines() if r.strip()]
    print("\n".join(righe))  # resta visibile anche nel terminale
    return {"risposta": risposta or "", "dietro": righe}


def _gestore(rispondi, nome: str):
    pagina = PAGINA.replace("{{NOME}}", json.dumps(nome)).encode("utf-8")

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
<title>Assistente della 4B</title>
<style>
  :root { --sfondo:#0b1024; --card:#121933; --bordo:#26304f; --testo:#eef1fa; --tenue:#9aa6c8;
          --arancio:#f08c2b; --verde:#3fd07a; }
  * { box-sizing:border-box; }
  body { margin:0; height:100vh; display:flex; flex-direction:column; color:var(--testo);
         font:16px/1.45 system-ui, sans-serif;
         background:radial-gradient(circle at 20% 0%, #0f5f6b 0, transparent 45%),
                    radial-gradient(circle at 90% 0%, #5b2a72 0, transparent 40%), var(--sfondo); }
  header { padding:18px 24px; font-weight:700; font-size:22px; }
  header span { color:var(--arancio); }
  main { flex:1; display:grid; grid-template-columns:2fr 1fr; gap:16px; padding:0 24px 24px; min-height:0; }
  section { background:var(--card); border:1px solid var(--bordo); border-radius:14px;
            display:flex; flex-direction:column; min-height:0; }
  h2 { margin:0; padding:12px 16px; font-size:13px; letter-spacing:.08em; text-transform:uppercase;
       color:var(--arancio); border-bottom:1px solid var(--bordo); }
  .scorre { flex:1; overflow-y:auto; padding:16px; }
  .msg { max-width:85%; margin:0 0 12px; padding:10px 14px; border-radius:12px; white-space:pre-wrap; }
  .tu { margin-left:auto; background:#24305a; }
  .ada { background:#1a2244; border:1px solid var(--bordo); }
  .attesa { color:var(--tenue); font-style:italic; }
  #dietro div { font:13px/1.5 ui-monospace, Menlo, monospace; color:var(--verde); margin-bottom:6px;
                white-space:pre-wrap; word-break:break-word; }
  #dietro .domanda { color:var(--tenue); margin-top:12px; }
  form { display:flex; gap:8px; padding:12px; border-top:1px solid var(--bordo); }
  input { flex:1; padding:12px; border-radius:10px; border:1px solid var(--bordo);
          background:#0b1024; color:var(--testo); font-size:16px; }
  button { padding:0 20px; border:0; border-radius:10px; background:var(--arancio); color:#111;
           font-weight:700; cursor:pointer; }
  @media (max-width:800px) { main { grid-template-columns:1fr; } }
</style></head>
<body>
<header><span id="nome"></span> · l'assistente della 4B</header>
<main>
  <section><h2>Chat</h2><div class="scorre" id="chat"></div>
    <form id="form"><input id="domanda" autocomplete="off" placeholder="Scrivi la tua domanda…" autofocus>
    <button>Invia</button></form></section>
  <section><h2>Dietro le quinte</h2><div class="scorre" id="dietro"></div></section>
</main>
<script>
const NOME = {{NOME}};
document.getElementById("nome").textContent = NOME;
const chat = document.getElementById("chat"), dietro = document.getElementById("dietro");

function aggiungi(contenitore, testo, classe) {
  const el = document.createElement("div");
  el.className = classe;
  el.textContent = testo;  // sempre testo, mai HTML: quello che scrive il modello non diventa codice
  contenitore.appendChild(el);
  contenitore.scrollTop = contenitore.scrollHeight;
  return el;
}

document.getElementById("form").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  const campo = document.getElementById("domanda"), domanda = campo.value.trim();
  if (!domanda) return;
  campo.value = "";
  aggiungi(chat, domanda, "msg tu");
  aggiungi(dietro, "› " + domanda, "domanda");
  const attesa = aggiungi(chat, NOME + " sta pensando…", "msg ada attesa");
  try {
    const r = await fetch("/domanda", {method: "POST", headers: {"Content-Type": "application/json"},
                                       body: JSON.stringify({domanda})});
    const dati = await r.json();
    attesa.remove();
    dati.dietro.forEach((riga) => aggiungi(dietro, riga, ""));
    aggiungi(chat, dati.risposta, "msg ada");
  } catch (errore) {
    attesa.textContent = "Il programma non risponde: è ancora acceso nel terminale?";
  }
});
</script>
</body></html>
"""
