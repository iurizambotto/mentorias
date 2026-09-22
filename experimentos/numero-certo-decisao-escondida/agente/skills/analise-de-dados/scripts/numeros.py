"""Ledger of every number an analysis states.

Any figure that reaches a deliverable must be registered here by the script
that computed it. Non-finite values are refused, so a silent division by zero
stops at registration instead of reaching the report.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from datetime import datetime
from pathlib import Path

LIVRO = Path("analise/numeros.json")
_ID = re.compile(r"^[a-z0-9][a-z0-9_.-]*$")


def carregar(livro: Path = LIVRO) -> dict[str, dict]:
    if not livro.exists():
        return {}
    return json.loads(livro.read_text(encoding="utf-8"))


def registrar(
    id: str,
    valor: float,
    descricao: str,
    *,
    linhas: int | None = None,
    script: str | None = None,
    unidade: str = "",
    decisoes: list[str] | None = None,
    livro: Path = LIVRO,
) -> float:
    if not _ID.match(id):
        raise ValueError(f"id invalido '{id}': use minusculas, digitos, ponto, hifen ou sublinhado")
    valor = float(valor)
    if not math.isfinite(valor):
        raise ValueError(f"valor nao finito para '{id}': {valor}. Verifique divisao por zero ou nulo")
    dados = carregar(livro)
    dados[id] = {
        "valor": valor,
        "descricao": descricao,
        "unidade": unidade,
        "linhas": linhas,
        "script": script,
        "decisoes": decisoes or [],
        "registrado_em": datetime.now().isoformat(timespec="seconds"),
    }
    livro.parent.mkdir(parents=True, exist_ok=True)
    livro.write_text(json.dumps(dados, indent=2, ensure_ascii=False), encoding="utf-8")
    return valor


def main() -> int:
    parser = argparse.ArgumentParser(description="Livro de numeros da analise.")
    parser.add_argument("--livro", type=Path, default=LIVRO)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("listar")
    reg = sub.add_parser("registrar")
    reg.add_argument("--id", required=True)
    reg.add_argument("--valor", required=True, type=float)
    reg.add_argument("--descricao", required=True)
    reg.add_argument("--linhas", type=int)
    reg.add_argument("--script")
    reg.add_argument("--unidade", default="")
    reg.add_argument("--decisao", action="append", dest="decisoes")
    args = parser.parse_args()

    if args.cmd == "registrar":
        registrar(
            args.id,
            args.valor,
            args.descricao,
            linhas=args.linhas,
            script=args.script,
            unidade=args.unidade,
            decisoes=args.decisoes,
            livro=args.livro,
        )
    for chave, item in carregar(args.livro).items():
        linhas = f"{item['linhas']} linhas" if item.get("linhas") is not None else "linhas n/d"
        print(f"{chave:40s} {item['valor']:>20,.4f}  {linhas:>14s}  {item['descricao']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
