"""Carga canonica da base de pacing e montagem da malha flight x entrega.

Toda a analise parte daqui, para que planejado, realizado e a regra de
atribuicao entre os dois tenham uma unica definicao.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

sys.path.insert(0, ".claude/skills/analise-de-dados/scripts")

ARQUIVO = Path("BASE DE PACING_v2.csv.xls")
METRICAS = ["Soma de Investimento", "Soma de Impressoes", "Soma de Cliques"]
CHAVE = ["Campanha", "Veiculo"]


@dataclass(frozen=True)
class Base:
    """As duas tabelas empilhadas no arquivo, ja separadas pelo grao."""

    bruto: pd.DataFrame
    planejado: pd.DataFrame
    realizado: pd.DataFrame


def carregar(arquivo: Path = ARQUIVO) -> Base:
    bruto = pd.read_csv(arquivo, encoding="utf-8-sig")
    for coluna in ("Data", "Data de Inicio", "Data de Termino"):
        bruto[coluna] = pd.to_datetime(bruto[coluna])

    planejado = bruto[bruto["Base"] == "Planejado"].copy()
    planejado["flight_id"] = planejado.index
    realizado = bruto[bruto["Base"] == "Realizado"].copy()
    realizado["entrega_id"] = realizado.index
    return Base(bruto=bruto, planejado=planejado, realizado=realizado)


def malha(base: Base) -> pd.DataFrame:
    """Um par (flight, entrega) por linha, para cada casamento valido.

    Casamento valido = mesma Campanha, mesmo Veiculo e Data da entrega dentro
    de [Data de Inicio, Data de Termino] do flight, com as duas pontas
    incluidas. Uma entrega pode aparecer em mais de um flight quando o plano
    tem janelas sobrepostas; a deduplicacao e feita por quem consome.
    """
    # As colunas de janela existem tambem no lado Realizado, sempre nulas.
    # Se ficarem, o merge renomeia as do plano e a comparacao cai em nulo.
    entregas = base.realizado.drop(columns=["Data de Inicio", "Data de Termino"])
    cruzamento = entregas.merge(
        base.planejado[[*CHAVE, "flight_id", "Data de Inicio", "Data de Termino"]],
        on=CHAVE,
        how="inner",
    )
    assert cruzamento["Data de Inicio"].notna().all(), "janela do flight nula apos o merge"
    dentro = (cruzamento["Data"] >= cruzamento["Data de Inicio"]) & (
        cruzamento["Data"] <= cruzamento["Data de Termino"]
    )
    return cruzamento[dentro].copy()


def entregas_atribuidas(base: Base) -> pd.DataFrame:
    """Entregas que pertencem ao plano, cada uma contada uma unica vez.

    Chave de deduplicacao: entrega_id. Uma entrega coberta por tres flights
    sobrepostos continua sendo uma entrega e um valor de midia.
    """
    return malha(base).drop_duplicates(subset="entrega_id")


def pacing(realizado: float, planejado: float) -> float | None:
    """Razao realizado/planejado. Devolve None quando o denominador e zero
    ou nulo, para que a ausencia de pacing nunca vire infinito ou NaN."""
    if planejado is None or pd.isna(planejado) or planejado == 0:
        return None
    return float(realizado) / float(planejado)
