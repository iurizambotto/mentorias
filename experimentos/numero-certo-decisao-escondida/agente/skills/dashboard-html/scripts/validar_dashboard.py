"""Check that a dashboard is a single self-contained HTML file.

Loading anything from the network is refused: the file must open offline,
by email attachment, years from now. Plain reading links are allowed.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_EXTERNOS = [
    (re.compile(r"<script[^>]+src\s*=\s*[\"']?(?:https?:)?//", re.I), "script carregado de fora"),
    (re.compile(r"<link[^>]+href\s*=\s*[\"']?(?:https?:)?//", re.I), "link de recurso externo (css, fonte ou preload)"),
    (
        re.compile(r"<(?:img|iframe|video|audio|source)[^>]+src\s*=\s*[\"']?(?:https?:)?//", re.I),
        "midia carregada de fora",
    ),
    (re.compile(r"url\(\s*[\"']?(?:https?:)?//", re.I), "url( ) externa em css"),
    (re.compile(r"@import", re.I), "@import em css"),
    (re.compile(r"\bfetch\s*\(|XMLHttpRequest|new\s+WebSocket", re.I), "chamada de rede em javascript"),
]
_LIMITE_BYTES = 5 * 1024 * 1024


def validar(caminho: Path) -> list[str]:
    html = caminho.read_text(encoding="utf-8")
    problemas = [f"{motivo}" for padrao, motivo in _EXTERNOS if padrao.search(html)]
    titulo = re.search(r"<title>\s*([^<]+?)\s*</title>", html, re.I)
    if not titulo:
        problemas.append("sem <title> preenchido")
    if not re.search(r"<html[^>]+lang\s*=", html, re.I):
        problemas.append("sem atributo lang no <html>")
    if not re.search(r"<meta[^>]+name\s*=\s*[\"']viewport", html, re.I):
        problemas.append("sem meta viewport, quebra no celular")
    if not re.search(r"<svg|<canvas|<img[^>]+src\s*=\s*[\"']data:", html, re.I):
        problemas.append("nenhum grafico encontrado (svg, canvas ou imagem embutida)")
    if caminho.stat().st_size > _LIMITE_BYTES:
        problemas.append(f"arquivo acima de {_LIMITE_BYTES // 1024 // 1024} MB")
    return problemas


def main() -> int:
    parser = argparse.ArgumentParser(description="Valida um dashboard HTML autocontido.")
    parser.add_argument("arquivo", type=Path)
    args = parser.parse_args()
    problemas = validar(args.arquivo)
    for p in problemas:
        print(f"PROBLEMA: {p}")
    print("ok: dashboard autocontido" if not problemas else f"{len(problemas)} problema(s)")
    return 1 if problemas else 0


if __name__ == "__main__":
    sys.exit(main())
