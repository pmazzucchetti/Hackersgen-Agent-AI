"""Collegamento al registro della scuola (il server MCP in scuola/server.py).

La libreria MCP lavora in modo "asincrono" (async/await). Per non complicare le
lezioni, qui la nascondiamo dietro due funzioni normali:

    strumenti()            -> gli strumenti del registro, pronti per il modello
    chiama(nome, argomenti) -> esegue uno strumento e restituisce il risultato come testo

Ogni chiamata avvia il server, fa la richiesta e lo chiude: è lento ma semplice.
"""

import asyncio
import json
import sys
from pathlib import Path

from mcp import Client
from mcp.client.stdio import StdioServerParameters

SERVER = StdioServerParameters(
    command=sys.executable, args=[str(Path(__file__).parent / "scuola" / "server.py")]
)


async def _strumenti():
    async with Client(SERVER) as client:
        return (await client.list_tools()).tools


async def _chiama(nome, argomenti):
    async with Client(SERVER) as client:
        return await client.call_tool(nome, argomenti)


def strumenti() -> list[dict]:
    """Gli strumenti del registro, nel formato che il modello capisce."""
    return [
        {"type": "function",
         "function": {"name": s.name, "description": s.description, "parameters": s.input_schema}}
        for s in asyncio.run(_strumenti())
    ]


def chiama(nome: str, argomenti: dict) -> str:
    """Esegue uno strumento del registro e restituisce il risultato come testo JSON."""
    risultato = asyncio.run(_chiama(nome, argomenti))
    if risultato.structured_content is not None:
        contenuto = risultato.structured_content
        return json.dumps(contenuto.get("result", contenuto), ensure_ascii=False)
    return risultato.content[0].text
