"""Environment check for the labs.

Run it from the repository folder:

    uv run verifica.py

If every line is [OK], you are ready for the live sessions.
"""

import asyncio
import json
import platform
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

MODEL = "qwen3:4b-instruct"
EMBEDDING_MODEL = "qwen3-embedding:0.6b"
OLLAMA = "http://localhost:11434"
SCHOOL_SERVER = Path(__file__).parent / "scuola" / "server.py"


def ok(msg: str) -> None:
    print(f"  [OK]  {msg}")


def fail(msg: str, hint: str) -> None:
    print(f"  [NO]  {msg}\n        Cosa fare: {hint}")
    sys.exit(1)


def get_json(path: str) -> dict:
    with urllib.request.urlopen(OLLAMA + path, timeout=5) as resp:
        return json.load(resp)


def check_python() -> None:
    if sys.version_info < (3, 12):
        fail(f"Python {platform.python_version()} è troppo vecchio",
             "lancia lo script con `uv run verifica.py`, non con `python verifica.py`")
    ok(f"Python {platform.python_version()} su {platform.system()} {platform.machine()}")


def check_ollama() -> None:
    try:
        version = get_json("/api/version")["version"]
    except (urllib.error.URLError, TimeoutError, ConnectionError):
        fail("Ollama non risponde", "apri l'app Ollama (su Linux: `ollama serve`) e riprova")
    ok(f"Ollama {version} è acceso")
    names = [m["name"] for m in get_json("/api/tags")["models"]]
    for model in (MODEL, EMBEDDING_MODEL):
        if model not in names and f"{model}:latest" not in names:
            fail(f"Il modello {model} non è scaricato", f"lancia `ollama pull {model}` e riprova")
        ok(f"Il modello {model} è scaricato")


async def check_school_server():
    from mcp import Client
    from mcp.client.stdio import StdioServerParameters

    server = StdioServerParameters(command=sys.executable, args=[str(SCHOOL_SERVER)])
    async with Client(server) as client:
        tools = (await client.list_tools()).tools
        tests = (await client.call_tool("verifiche", {"utente": "luca"})).structured_content["result"]
    ok(f"Il registro della scuola risponde: {len(tools)} strumenti, {len(tests)} verifiche in arrivo")
    return tools


def check_model_uses_tools(tools) -> None:
    from openai import OpenAI

    llm = OpenAI(base_url=f"{OLLAMA}/v1", api_key="ollama")
    schema = [{"type": "function", "function": {"name": t.name, "description": t.description or "",
                                                "parameters": t.input_schema}} for t in tools]
    started = time.monotonic()
    reply = llm.chat.completions.create(
        model=MODEL, tools=schema,
        messages=[{"role": "system", "content": "Stai parlando con Luca (utente: luca)."},
                  {"role": "user", "content": "Quando ho la prossima verifica?"}],
    ).choices[0].message
    seconds = round(time.monotonic() - started, 1)
    if not reply.tool_calls:
        fail("Il modello ha risposto senza usare gli strumenti",
             "rilancia la verifica: i modelli piccoli ogni tanto sbagliano")
    ok(f"Il modello ha scelto lo strumento {reply.tool_calls[0].function.name} in {seconds} s")


def main() -> None:
    print("Verifica dell'ambiente per i laboratori\n")
    check_python()
    check_ollama()
    try:
        tools = asyncio.run(check_school_server())
    except ImportError:
        fail("Mancano le librerie del progetto", "lancia `uv sync` e poi `uv run verifica.py`")
    except (OSError, ExceptionGroup) as exc:
        fail(f"Il registro della scuola non è partito ({exc!r})",
             "lancia `uv sync` e riprova; se non basta, copia questo messaggio in un assistente AI")
    check_model_uses_tools(tools)
    print("\nTutto pronto: ci vediamo in diretta!")


if __name__ == "__main__":
    main()
