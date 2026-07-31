#!/usr/bin/env python3
"""Verificacao de nivel 2 do codigo Terraform deste modulo.

Este script roda a porta de entrada de qualquer CI de infraestrutura: formatacao,
sintaxe e regras de boa pratica. Ele para exatamente onde o teto deste modulo
esta.

POR QUE NAO EXISTE plan NEM apply AQUI
--------------------------------------
Nao e limitacao tecnica, e regra do ambiente de trabalho. `terraform plan` e
`terraform apply` sao operacoes do operador humano ou do pipeline, nunca de um
agente nem deste script. Portanto o codigo de infraestrutura desta trilha tem
teto no nivel 2 da escada de verificacao, e a apostila declara isso.

O `init` roda com `-backend=false`. Ele apenas baixa o provider declarado, e nao
toca em backend remoto, em state nem em nenhuma conta de nuvem. Sem `init` o
`validate` nao consegue conferir o schema do provider, e a checagem cairia para
sintaxe pura.

O QUE ISSO PROVA
----------------
Que o codigo esta formatado, que a sintaxe e valida contra o schema do provider,
e que ele passa nas regras recomendadas do TFLint.

O QUE ISSO NAO PROVA
--------------------
Que os recursos podem ser criados, que a politica de ciclo de vida faz o que se
espera, ou que o custo e o previsto. Isso exige `plan` e `apply`, que sao do
operador.

Uso:
    python3 scripts/verificar_iac.py

Codigo de saida 0 quando tudo passa, 1 quando qualquer checagem falha.

Requisitos: terraform e tflint no PATH. A ausencia de qualquer um dos dois e
reportada como falha, nunca como aprovacao.
"""

from __future__ import annotations

import argparse
import logging
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

LOGGER = logging.getLogger("infraestrutura-como-codigo.verificar-iac")

# Directories with their own root configuration, relative to `infrastructure/`.
RAIZES = ("ambientes/dev", "modulos/camada-do-lake")

# Guard against this script ever growing a destructive command.
SUBCOMANDOS_PROIBIDOS = frozenset({"plan", "apply", "destroy", "import", "state"})


@dataclass(frozen=True)
class Resultado:
    """Desfecho de uma checagem, impresso em uma linha."""

    nome: str
    ok: bool
    detalhe: str

    def formatar(self) -> str:
        marca = "OK" if self.ok else "FALHA"
        return f"{marca:<5} {self.nome}: {self.detalhe}"


class VerificadorDeIac:
    """Roda a porta de entrada de CI sobre o codigo Terraform do modulo."""

    def __init__(self, infraestrutura: Path) -> None:
        self.infraestrutura = infraestrutura

    def executar(self) -> list[Resultado]:
        resultados = [self._formatacao()]
        for raiz in RAIZES:
            destino = self.infraestrutura / raiz
            resultados.append(self._inicializacao(raiz, destino))
            resultados.append(self._validacao(raiz, destino))
        resultados.append(self._lint())
        return resultados

    # -- checagens ---------------------------------------------------------

    def _formatacao(self) -> Resultado:
        return self._terraform(
            "terraform fmt, recursivo",
            ["fmt", "-check", "-recursive"],
            self.infraestrutura,
        )

    def _inicializacao(self, raiz: str, destino: Path) -> Resultado:
        return self._terraform(
            f"terraform init sem backend, {raiz}",
            ["init", "-backend=false", "-input=false", "-no-color"],
            destino,
        )

    def _validacao(self, raiz: str, destino: Path) -> Resultado:
        return self._terraform(
            f"terraform validate, {raiz}",
            ["validate", "-no-color"],
            destino,
        )

    def _lint(self) -> Resultado:
        nome = "tflint, recursivo"
        binario = shutil.which("tflint")
        if binario is None:
            return Resultado(nome, False, "tflint ausente, nada foi verificado")
        return self._executar(nome, [binario, "--recursive"], self.infraestrutura)

    # -- auxiliares --------------------------------------------------------

    def _terraform(self, nome: str, argumentos: list[str], destino: Path) -> Resultado:
        proibido = SUBCOMANDOS_PROIBIDOS.intersection(argumentos)
        if proibido:
            # Belt and braces: the workspace forbids these, and a future edit
            # must fail loudly instead of silently running them.
            return Resultado(nome, False, f"subcomando proibido: {sorted(proibido)}")
        binario = shutil.which("terraform")
        if binario is None:
            return Resultado(nome, False, "terraform ausente, nada foi verificado")
        if not destino.is_dir():
            return Resultado(nome, False, f"diretorio inexistente: {destino}")
        return self._executar(nome, [binario, *argumentos], destino)

    def _executar(self, nome: str, comando: list[str], destino: Path) -> Resultado:
        # Fixed argument list resolved by shutil.which, and no shell involved.
        processo = subprocess.run(
            comando,
            cwd=destino,
            capture_output=True,
            text=True,
            check=False,
        )
        if processo.returncode != 0:
            saida = (processo.stdout + processo.stderr).strip()
            return Resultado(nome, False, saida.replace("\n", " ")[:200])
        return Resultado(nome, True, "codigo 0")


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verificacao de nivel 2 do codigo Terraform do modulo."
    )
    parser.add_argument(
        "--infraestrutura",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "infrastructure",
        help="diretorio infrastructure/ do modulo",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    args = construir_parser().parse_args(argv)
    resultados = VerificadorDeIac(args.infraestrutura).executar()
    for resultado in resultados:
        LOGGER.info(resultado.formatar())
    falhas = [r for r in resultados if not r.ok]
    if falhas:
        LOGGER.error("%d checagem(ns) falharam", len(falhas))
        return 1
    LOGGER.info("%d checagem(ns), todas em nivel 2", len(resultados))
    return 0


if __name__ == "__main__":
    sys.exit(main())
