# Preparare l'ambiente

Questa guida ti porta da zero a un computer pronto per i laboratori delle lezioni 3 e 4.
**Va fatta prima della live**: in diretta non c'è tempo per installare, e se qualcosa non
funziona la soluzione è seguire la spiegazione e recuperare dopo (le lezioni sono registrate).

Ci vogliono circa **30-45 minuti**, quasi tutti di download. Alla fine lancerai uno script
di verifica: se è tutto verde, sei pronto.

## Di cosa hai bisogno

- Un computer **Windows 10/11**, **macOS** o **Linux**, con permesso di installare programmi.
- **8 GB di RAM** come minimo (16 GB vanno meglio).
- Circa **7 GB liberi** sul disco: i due modelli di AI ne occupano circa 3.
- Una connessione decente per i download (solo durante la preparazione: in diretta il
  modello gira sul tuo computer, senza internet).

Non serve un account a pagamento, non serve una carta di credito e non serve una scheda
video dedicata.

## Cosa installerai

| Strumento | A cosa serve |
|---|---|
| **Git** | Scaricare il codice del corso e i suoi aggiornamenti |
| **uv** | Installare Python e le librerie del progetto con un solo comando |
| **VS Code** | L'editor in cui scriveremo il codice |
| **Ollama** | Far girare un modello di AI sul tuo computer, gratis e senza account |

Python **non** va installato a parte: ci pensa uv, nella versione giusta.

## Come aprire il terminale

Quasi tutti i passi si fanno scrivendo comandi nel terminale.

- **Windows:** tasto Start, scrivi `PowerShell`, apri **Windows PowerShell**.
- **macOS:** `Cmd + Spazio`, scrivi `Terminale`, premi Invio.
- **Linux:** di solito `Ctrl + Alt + T`.

Dopo ogni installazione **chiudi e riapri il terminale**: i programmi appena installati
vengono trovati solo da un terminale nuovo.

---

## 1. Git

**Windows** — scarica l'installer da [git-scm.com/download/win](https://git-scm.com/download/win)
e lascia le opzioni proposte. In alternativa, da PowerShell:

```powershell
winget install --id Git.Git -e
```

**macOS** — nel terminale:

```bash
xcode-select --install
```

Si apre una finestra: conferma l'installazione degli strumenti per sviluppatori.

**Linux** — con il gestore di pacchetti della tua distribuzione, per esempio:

```bash
sudo apt install git        # Ubuntu, Debian, Mint
sudo dnf install git        # Fedora
sudo pacman -S git          # Arch, Manjaro
```

**Controllo:** `git --version` deve stampare un numero di versione.

## 2. uv

**Windows** (PowerShell):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS e Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Controllo:** chiudi e riapri il terminale, poi `uv --version`.

## 3. VS Code

Scaricalo da [code.visualstudio.com](https://code.visualstudio.com/) e installalo.
Poi aprilo, vai su **Estensioni** (l'icona con i quadratini nella barra a sinistra), cerca
**Python** e installa quella pubblicata da Microsoft.

Usi già **VSCodium** o un altro editor? Va benissimo: nel corso l'editor serve solo per
aprire e modificare i file, gli esercizi si lanciano dal terminale con `uv run`. Su
VSCodium cerca **Python** tra le estensioni; se non la trovi, puoi seguire il corso anche
senza.

## 4. Ollama e il modello

**Windows e macOS** — scarica l'app da [ollama.com/download](https://ollama.com/download) e
installala. Dopo l'installazione Ollama resta acceso in background (su macOS vedi l'icona
del lama nella barra in alto, su Windows nell'area di notifica).

**Linux:**

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Lo script funziona sulle distribuzioni con systemd (Ubuntu, Debian, Fedora, Mint e molte
altre). Se la tua non lo usa, avvia Ollama a mano con `ollama serve` in un terminale e
lascialo aperto.

**Scarica i due modelli** (circa 3 GB in tutto, ci vuole qualche minuto):

```bash
ollama pull qwen3:4b-instruct
ollama pull qwen3-embedding:0.6b
```

Il primo è il modello che risponde; il secondo trasforma i testi in numeri e serve per
cercare nei documenti della scuola (lo vedremo nella lezione 3).

**Controllo:** `ollama run qwen3:4b-instruct "Ciao, chi sei?"` deve rispondere qualcosa.

## 5. Il codice del corso

Scegli una cartella in cui tenere il progetto (per esempio Documenti), spostati lì con il
terminale e scarica la repository:

```bash
git clone https://github.com/pmazzucchetti/Hackersgen-Agent-AI.git
cd Hackersgen-Agent-AI
uv sync
```

`uv sync` scarica la versione giusta di Python e tutte le librerie del progetto. Va fatto
**una volta adesso**, così in diretta non si scarica più niente.

> **Windows su ARM (Snapdragon e simili).** Se `uv sync` si ferma su `cryptography` con un
> errore tipo `link.exe not found`, il motivo è che quella libreria non ha una versione già
> pronta per ARM e uv prova a compilarla. Non serve installare altro: usa il Python per
> x64, che Windows su ARM fa girare in emulazione. Dalla cartella del progetto, in
> PowerShell:
>
> ```powershell
> uv self update
> Remove-Item -Recurse -Force .venv
> uv python pin cpython-3.12-windows-x86_64-none
> uv sync
> uv run python -c "import platform; print(platform.machine())"
> ```
>
> L'ultimo comando deve stampare `AMD64`. Il comando `uv python pin` modifica il file
> `.python-version`: è normale, non serve fare altro.

## 6. La verifica

Sempre dalla cartella `Hackersgen-Agent-AI`:

```bash
uv run verifica.py
```

Se va tutto bene vedi una serie di `[OK]` e alla fine **Tutto pronto**. Se una riga è
`[NO]`, sotto c'è scritto cosa fare.

Per aprire il progetto in VS Code: **File → Apri cartella** e scegli `Hackersgen-Agent-AI`.

---

## Se qualcosa non funziona

1. **Leggi il messaggio di errore**, tutto: spesso dice già qual è il problema.
2. **Chiedi a un assistente AI** (ChatGPT, Gemini, Claude o quello che usi). Funziona bene
   se gli dai il contesto: il tuo sistema operativo, il comando che hai lanciato e il
   messaggio di errore completo, copiato e incollato.
3. **Cerca l'errore online**: qualcuno l'ha quasi sempre già avuto.

### Problemi frequenti

| Problema | Soluzione |
|---|---|
| `comando non trovato` / `is not recognized` subito dopo un'installazione | Chiudi e riapri il terminale. Se non basta, riavvia il computer |
| Windows: "l'esecuzione di script è disabilitata nel sistema" | Usa esattamente il comando di uv riportato sopra, che contiene `-ExecutionPolicy ByPass` |
| `Ollama non risponde` nella verifica | Apri l'app Ollama. Su Linux lancia `ollama serve` in un altro terminale |
| Il modello risponde molto lentamente | Chiudi i programmi pesanti (browser con tante schede, giochi). Con 8 GB di RAM è normale che sia un po' lento |
| `python verifica.py` dà errori strani | Usa sempre `uv run verifica.py`: così parte il Python giusto |

### Una nota sugli assistenti AI e su MCP

Nel corso usiamo la **versione 2** della libreria `mcp`, uscita da poco. Molti assistenti AI
conoscono solo la versione 1 e potrebbero proporti codice con `from mcp.server.fastmcp
import FastMCP`: con la versione 2 non funziona. Se ti capita, diglielo esplicitamente
("uso mcp 2.3, dove FastMCP si chiama MCPServer").
