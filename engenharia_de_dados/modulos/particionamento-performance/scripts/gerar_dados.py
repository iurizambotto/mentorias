#!/usr/bin/env python3
"""Gera os dados sinteticos do laboratorio de particionamento.

POR QUE ESTE SCRIPT EXISTE
--------------------------
O laboratorio precisa de um volume de eventos grande o suficiente para que a
diferenca entre ler uma particao e ler a tabela inteira seja visivel. Antes deste
script, o Lab 0 mandava o leitor copiar dois CSV de uma pasta na maquina do
mentor, produzidos por um gerador que nao vive no repositorio publico. Ou seja: o
laboratorio nao rodava para ninguem de fora.

O que este script entrega, sem dependencia externa nenhuma alem da biblioteca
padrao do Python:

  events.csv        eventos de marketing, uma linha por evento
  events__cdc.csv   os mesmos eventos com colunas de captura de mudanca

DETERMINISMO
------------
A semente e fixa. Rodar duas vezes produz byte a byte o mesmo arquivo, e e por
isso que a apostila pode publicar numeros de saida e esperar que eles se
reproduzam na sua maquina.

Uso:
    python3 scripts/gerar_dados.py --destino ./dados
    python3 scripts/gerar_dados.py --destino ./dados --dias 30 --por-dia 2000

Codigo de saida 0 quando os dois arquivos foram escritos.
"""

from __future__ import annotations

import argparse
import csv
import logging
import random
import sys
from dataclasses import dataclass, fields
from datetime import date, datetime, timedelta
from pathlib import Path

LOGGER = logging.getLogger("particionamento.gerar-dados")

# Fixed so the apostila can publish counts that reproduce.
SEMENTE = 20260731

# The lab queries filter on 2025-01-10, so the window must contain it.
PRIMEIRO_DIA = date(2025, 1, 1)

# 15 partitions is not a round number, it is a measured ceiling. The Hive
# Metastore of this laboratory wedges during the partition commit phase of a
# partitioned CTAS above roughly 20 partitions: the query never leaves the
# FINISHING state and the metastore stops answering, with no error in any log.
#
# Measured on 2026-07-31, holding rows constant to isolate the variable:
#
#   particoes  linhas   resultado
#   5          1000     concluiu em 5s
#   5          12000    concluiu em 11s
#   15         12000    concluiu em 10s
#   25         12000    travou
#   30         6000     travou
#   30         60000    travou
#
# O volume de linhas variou 12 vezes sem efeito. A contagem de particoes e a
# variavel. 15 fica com margem abaixo do penhasco.
DIAS_PADRAO = 15
POR_DIA_PADRAO = 800

# 'organic' is queried by the full scan lab, so it has to exist.
CANAIS = ("organic", "paid_search", "paid_social", "email", "display")
DISPOSITIVOS = ("mobile", "desktop", "tablet")
PAISES = ("BR", "AR", "MX", "CL", "CO")
ETAPAS = ("impression", "click", "signup", "purchase")

# Skew on purpose: one campaign concentrates traffic, which is what makes the
# hot partition section of the apostila something the reader can observe.
CAMPANHAS = tuple(f"cmp_{n:03d}" for n in range(1, 21))
CAMPANHA_DOMINANTE = "cmp_001"
PESO_DA_DOMINANTE = 0.35

OPERACOES_CDC = ("insert", "update", "delete")
PESOS_CDC = (0.70, 0.25, 0.05)


@dataclass(frozen=True)
class Evento:
    """Uma linha de events.csv."""

    event_id: str
    event_date: str
    event_ts: str
    user_id: str
    campaign_id: str
    channel: str
    device: str
    country: str
    stage: str
    revenue: str

    @classmethod
    def colunas(cls) -> list[str]:
        return [campo.name for campo in fields(cls)]

    def como_linha(self) -> list[str]:
        return [getattr(self, nome) for nome in self.colunas()]


class GeradorDeEventos:
    """Produz eventos deterministicos para o laboratorio."""

    def __init__(self, dias: int, por_dia: int, semente: int = SEMENTE) -> None:
        self.dias = dias
        self.por_dia = por_dia
        self.aleatorio = random.Random(semente)

    def gerar(self) -> list[Evento]:
        eventos: list[Evento] = []
        sequencial = 0
        for deslocamento in range(self.dias):
            dia = PRIMEIRO_DIA + timedelta(days=deslocamento)
            for _ in range(self.por_dia):
                sequencial += 1
                eventos.append(self._um_evento(sequencial, dia))
        return eventos

    def _um_evento(self, sequencial: int, dia: date) -> Evento:
        etapa = self.aleatorio.choice(ETAPAS)
        return Evento(
            event_id=f"evt_{sequencial:08d}",
            event_date=dia.isoformat(),
            event_ts=self._instante(dia),
            user_id=f"usr_{self.aleatorio.randrange(1, 5001):06d}",
            campaign_id=self._campanha(),
            channel=self.aleatorio.choice(CANAIS),
            device=self.aleatorio.choice(DISPOSITIVOS),
            country=self.aleatorio.choice(PAISES),
            stage=etapa,
            # Only a purchase carries revenue. Every other stage is zero, which
            # is what makes the aggregation sections of the apostila realistic.
            revenue=f"{self.aleatorio.uniform(20, 900):.2f}"
            if etapa == "purchase"
            else "0.00",
        )

    def _campanha(self) -> str:
        if self.aleatorio.random() < PESO_DA_DOMINANTE:
            return CAMPANHA_DOMINANTE
        return self.aleatorio.choice(CAMPANHAS)

    def _instante(self, dia: date) -> str:
        # Naive on purpose: the source system this lab imitates writes local
        # timestamps without offset, and the Hive CSV table reads them as text.
        # Attaching a timezone here would change the string the lab loads.
        momento = datetime(  # noqa: DTZ001
            dia.year,
            dia.month,
            dia.day,
            self.aleatorio.randrange(24),
            self.aleatorio.randrange(60),
            self.aleatorio.randrange(60),
        )
        return momento.isoformat(sep=" ")


class GeradorDeCdc:
    """Deriva o arquivo de captura de mudanca a partir dos eventos."""

    COLUNAS_EXTRA = ("cdc_op", "cdc_event_ts", "cdc_source_table")
    TABELA_DE_ORIGEM = "marketing.events"

    def __init__(self, semente: int = SEMENTE + 1) -> None:
        self.aleatorio = random.Random(semente)

    def colunas(self) -> list[str]:
        return [*Evento.colunas(), *self.COLUNAS_EXTRA]

    def gerar(self, eventos: list[Evento]) -> list[list[str]]:
        """Um insert por evento, mais update e delete para parte deles.

        O resultado tem mais linhas que a origem de proposito: e isso que faz o
        laboratorio de "ultima versao por event_id" ter o que desduplicar.
        """
        linhas: list[list[str]] = []
        for evento in eventos:
            linhas.append(self._linha(evento, "insert", ordem=0))
            operacao = self.aleatorio.choices(OPERACOES_CDC, weights=PESOS_CDC, k=1)[0]
            if operacao != "insert":
                linhas.append(self._linha(evento, operacao, ordem=1))
        return linhas

    def _linha(self, evento: Evento, operacao: str, ordem: int) -> list[str]:
        instante = datetime.fromisoformat(evento.event_ts) + timedelta(
            minutes=ordem * 30
        )
        return [
            *evento.como_linha(),
            operacao,
            instante.isoformat(sep=" ", timespec="milliseconds"),
            self.TABELA_DE_ORIGEM,
        ]


class EscritorDeCsv:
    """Escreve os dois arquivos no destino."""

    def __init__(self, destino: Path) -> None:
        self.destino = destino

    def escrever(self, nome: str, colunas: list[str], linhas: list[list[str]]) -> Path:
        self.destino.mkdir(parents=True, exist_ok=True)
        caminho = self.destino / nome
        with caminho.open("w", encoding="utf-8", newline="") as arquivo:
            escritor = csv.writer(arquivo)
            escritor.writerow(colunas)
            escritor.writerows(linhas)
        return caminho


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Gera os dados sinteticos do laboratorio de particionamento."
    )
    parser.add_argument(
        "--destino",
        type=Path,
        default=Path("dados"),
        help="pasta onde os CSV serao escritos (padrao: ./dados)",
    )
    parser.add_argument(
        "--dias",
        type=int,
        default=DIAS_PADRAO,
        help=f"quantidade de dias, uma particao por dia (padrao: {DIAS_PADRAO})",
    )
    parser.add_argument(
        "--por-dia",
        type=int,
        default=POR_DIA_PADRAO,
        help=f"eventos por dia (padrao: {POR_DIA_PADRAO})",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    args = construir_parser().parse_args(argv)

    if args.dias < 1 or args.por_dia < 1:
        LOGGER.error("dias e por-dia precisam ser maiores que zero")
        return 1

    eventos = GeradorDeEventos(args.dias, args.por_dia).gerar()
    linhas_cdc = GeradorDeCdc().gerar(eventos)

    escritor = EscritorDeCsv(args.destino)
    caminho_eventos = escritor.escrever(
        "events.csv", Evento.colunas(), [e.como_linha() for e in eventos]
    )
    gerador_cdc = GeradorDeCdc()
    caminho_cdc = escritor.escrever(
        "events__cdc.csv", gerador_cdc.colunas(), linhas_cdc
    )

    ultimo_dia = PRIMEIRO_DIA + timedelta(days=args.dias - 1)
    LOGGER.info("%s: %d linhas", caminho_eventos.name, len(eventos))
    LOGGER.info("%s: %d linhas", caminho_cdc.name, len(linhas_cdc))
    LOGGER.info(
        "janela: %s a %s, %d particoes de event_date",
        PRIMEIRO_DIA.isoformat(),
        ultimo_dia.isoformat(),
        args.dias,
    )
    LOGGER.info("destino: %s", args.destino.resolve())
    return 0


if __name__ == "__main__":
    sys.exit(main())
