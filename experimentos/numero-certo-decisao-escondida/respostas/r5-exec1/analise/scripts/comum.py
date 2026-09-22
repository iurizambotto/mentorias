"""Carga e normalizacao unicas da base de pacing.

Todo script da analise importa daqui, para que nenhum numero dependa de uma
leitura diferente do arquivo.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[2]
ARQUIVO = RAIZ / "BASE DE PACING_v2.csv.xls"

sys.path.insert(0, str(RAIZ / ".claude/skills/analise-de-dados/scripts"))

CHAVE = ["Campanha", "Veiculo"]
METRICAS = ["Soma de Investimento", "Soma de Impressoes", "Soma de Cliques"]


def carregar() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Devolve (planejado, realizado) com datas tipadas e id de linha estavel.

    O arquivo tem extensao .xls mas e csv utf-8 com BOM; ler como csv e
    deliberado (ver analise/perfil.md).
    """
    bruto = pd.read_csv(ARQUIVO, encoding="utf-8-sig")
    bruto["linha_id"] = bruto.index

    plan = bruto[bruto["Base"] == "Planejado"].copy()
    real = bruto[bruto["Base"] == "Realizado"].copy()

    for col in ("Data de Inicio", "Data de Termino"):
        plan[col] = pd.to_datetime(plan[col])
    plan = plan.rename(columns={"Data de Inicio": "inicio", "Data de Termino": "fim"})
    plan["flight_id"] = plan["linha_id"]

    real["Data"] = pd.to_datetime(real["Data"])

    return plan.reset_index(drop=True), real.reset_index(drop=True)


def uniao_janelas(grupo: pd.DataFrame) -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    """Funde janelas de flight que se tocam, para que nenhum dia conte duas vezes."""
    janelas = sorted(zip(grupo["inicio"], grupo["fim"]))
    fundidas: list[list[pd.Timestamp]] = []
    for ini, fim in janelas:
        if fundidas and ini <= fundidas[-1][1]:
            fundidas[-1][1] = max(fundidas[-1][1], fim)
        else:
            fundidas.append([ini, fim])
    return [(a, b) for a, b in fundidas]


def em_janelas(datas: pd.Series, janelas: list[tuple[pd.Timestamp, pd.Timestamp]]) -> pd.Series:
    dentro = pd.Series(False, index=datas.index)
    for ini, fim in janelas:
        dentro |= datas.between(ini, fim)
    return dentro
