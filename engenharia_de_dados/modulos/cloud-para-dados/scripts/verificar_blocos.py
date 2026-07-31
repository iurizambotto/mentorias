#!/usr/bin/env python3
"""Verificacao de nivel 2 dos blocos de codigo da apostila de cloud para dados.

Este modulo nao tem laboratorio executavel, porque subir recurso de verdade numa
nuvem custa dinheiro e exige credencial. O que da para provar sem conta e sem
rede e a sintaxe, e e isso que este script faz.

Nenhuma verificacao aqui toca a rede ou uma conta de nuvem. Cada checagem ou
faz o parse do artefato com a ferramenta dona da sintaxe, ou pede a AWS CLI que
interprete o comando sem executa-lo.

O que ele NAO prova: que a query devolve o resultado certo, que a politica
concede o acesso pretendido, que o bucket existe. Isso e nivel 3 ou 4, e esta
fora do alcance deste modulo.

Uso:
    python3 scripts/verificar_blocos.py

Codigo de saida 0 quando tudo passa, 1 quando qualquer checagem falha.

Requisitos: sqlglot e a AWS CLI v2 no PATH. A ausencia de qualquer um dos dois
e reportada como falha, nunca como aprovacao.
"""

from __future__ import annotations

import json
import logging
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

LOGGER = logging.getLogger("cloud-para-dados.verificar-blocos")

# Fixed environment: no credential, no profile, no region discovery over network.
AMBIENTE_LIMPO = {
    "PATH": "/usr/local/bin:/usr/bin:/bin",
    "AWS_DEFAULT_REGION": "us-east-1",
}

DDL_TABELA_EXTERNA = """
CREATE EXTERNAL TABLE raw.eventos_campanha (
    evento_id   BIGINT,
    campanha_id INT,
    impressoes  BIGINT,
    cliques     BIGINT,
    custo       DECIMAL(12, 2)
)
PARTITIONED BY (data_evento DATE)
STORED AS PARQUET
LOCATION 's3://empresa-data-lake/raw/eventos_campanha/'
"""

QUERY_COM_FILTRO_DE_PARTICAO = """
SELECT canal, sum(custo) AS custo
FROM raw.eventos_campanha
WHERE data_evento BETWEEN DATE '2026-06-01' AND DATE '2026-06-30'
GROUP BY canal
"""

POLITICA_DE_MENOR_PRIVILEGIO = """
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "LerApenasOPrefixoRaw",
      "Effect": "Allow",
      "Action": ["s3:GetObject"],
      "Resource": "arn:aws:s3:::empresa-data-lake/raw/*"
    },
    {
      "Sid": "ListarApenasOPrefixoRaw",
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": "arn:aws:s3:::empresa-data-lake",
      "Condition": {"StringLike": {"s3:prefix": ["raw/*"]}}
    }
  ]
}
"""


@dataclass(frozen=True)
class Resultado:
    """Desfecho de uma checagem, impresso em uma linha."""

    nome: str
    ok: bool
    detalhe: str

    def formatar(self) -> str:
        marca = "OK" if self.ok else "FALHA"
        return f"{marca:<5} {self.nome}: {self.detalhe}"


class VerificadorDeBlocos:
    """Roda toda checagem de nivel 2 dos blocos citados na apostila."""

    def __init__(self) -> None:
        self.resultados: list[Resultado] = []

    def executar(self) -> list[Resultado]:
        self.resultados = [
            self._sql(
                "DDL da tabela externa, dialeto hive", DDL_TABELA_EXTERNA, "hive"
            ),
            self._sql(
                "DDL da tabela externa, dialeto trino", DDL_TABELA_EXTERNA, "trino"
            ),
            self._sql(
                "Query com filtro de particao, dialeto trino",
                QUERY_COM_FILTRO_DE_PARTICAO,
                "trino",
            ),
            self._json(
                "Politica IAM de menor privilegio", POLITICA_DE_MENOR_PRIVILEGIO
            ),
            self._cli(
                "aws s3api create-bucket, modo esqueleto",
                ["s3api", "create-bucket", "--generate-cli-skeleton"],
            ),
            self._cli(
                "aws athena start-query-execution, modo esqueleto",
                ["athena", "start-query-execution", "--generate-cli-skeleton"],
            ),
            self._cli_com_arquivo_temporario(),
        ]
        return self.resultados

    def _sql(self, nome: str, sql: str, dialeto: str) -> Resultado:
        try:
            import sqlglot
        except ImportError:
            return Resultado(nome, False, "sqlglot ausente, nada foi verificado")
        try:
            arvore = sqlglot.parse_one(sql, read=dialeto)
        except Exception as erro:  # noqa: BLE001 - the message itself is the finding
            return Resultado(nome, False, f"{type(erro).__name__}: {erro}")
        return Resultado(nome, True, f"parse ok, raiz {type(arvore).__name__}")

    def _json(self, nome: str, texto: str) -> Resultado:
        try:
            dados = json.loads(texto)
        except json.JSONDecodeError as erro:
            return Resultado(nome, False, str(erro))
        return Resultado(
            nome, True, f"json valido, {len(dados['Statement'])} statements"
        )

    def _cli(self, nome: str, argumentos: list[str]) -> Resultado:
        binario = shutil.which("aws", path=AMBIENTE_LIMPO["PATH"])
        if binario is None:
            return Resultado(nome, False, "AWS CLI ausente, nada foi verificado")
        # Fixed argument list resolved by shutil.which, and no shell involved.
        processo = subprocess.run(
            [binario, *argumentos],
            capture_output=True,
            text=True,
            env=AMBIENTE_LIMPO,
            check=False,
        )
        if processo.returncode != 0:
            return Resultado(nome, False, processo.stderr.strip()[:200])
        linhas = processo.stdout.strip().splitlines()
        primeira = linhas[0] if linhas else ""
        return Resultado(nome, True, f"codigo 0, primeira linha: {primeira[:80]}")

    def _cli_com_arquivo_temporario(self) -> Resultado:
        """O dryrun do `aws s3 cp` precisa de uma origem que exista no disco."""
        nome = "aws s3 cp, modo dryrun"
        with tempfile.TemporaryDirectory() as pasta:
            origem = Path(pasta) / "vendas.parquet"
            origem.write_bytes(b"")
            return self._cli(
                nome,
                [
                    "s3",
                    "cp",
                    str(origem),
                    "s3://empresa-data-lake/raw/vendas/",
                    "--dryrun",
                ],
            )


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    resultados = VerificadorDeBlocos().executar()
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
