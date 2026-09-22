"""Carga e separacao das duas tabelas empilhadas na BASE DE PACING_v2.

O arquivo tem extensao .xls mas e CSV UTF-8 com BOM (ver analise/perfil.md).
A coluna Base empilha duas tabelas com graos diferentes:

- Planejado: um flight (campanha x veiculo x janela de veiculacao).
- Realizado: a entrega de um dia (campanha x veiculo x data).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

ARQUIVO = Path("BASE DE PACING_v2.csv.xls")
METRICAS = ["Soma de Investimento", "Soma de Impressoes", "Soma de Cliques"]
CHAVE = ["Campanha", "Veiculo"]


@dataclass(frozen=True)
class Base:
    """As duas tabelas do arquivo, ja separadas e com datas tipadas."""

    planejado: pd.DataFrame
    realizado: pd.DataFrame
    total_linhas: int


def carregar(arquivo: Path = ARQUIVO) -> Base:
    bruto = pd.read_csv(arquivo, encoding="utf-8-sig")
    for coluna in ["Data", "Data de Inicio", "Data de Termino"]:
        bruto[coluna] = pd.to_datetime(bruto[coluna])

    planejado = bruto[bruto["Base"] == "Planejado"].copy().reset_index(drop=True)
    realizado = bruto[bruto["Base"] == "Realizado"].copy().reset_index(drop=True)

    # id estavel por linha de realizado: e por ele que a deduplicacao acontece.
    realizado["id_realizado"] = realizado.index
    planejado["id_flight"] = planejado.index

    return Base(planejado=planejado, realizado=realizado, total_linhas=len(bruto))


def componentes_de_flight(planejado: pd.DataFrame) -> pd.DataFrame:
    """Agrupa flights sobrepostos da mesma campanha e veiculo em um bloco de plano.

    Dois flights entram no mesmo bloco quando as janelas se cruzam. O bloco existe
    porque uma linha de Realizado dentro da intersecao pertence aos dois flights ao
    mesmo tempo: atribui-la a um deles seria arbitrario, e a ambos seria contar duas
    vezes. O bloco soma o planejado dos flights e cobre a uniao das janelas.
    """
    blocos: list[dict] = []
    for (campanha, veiculo), grupo in planejado.groupby(CHAVE, sort=True):
        grupo = grupo.sort_values("Data de Inicio")
        atual: list[dict] = []
        fim_corrente = None
        for _, flight in grupo.iterrows():
            if atual and flight["Data de Inicio"] <= fim_corrente:
                atual.append(flight.to_dict())
                fim_corrente = max(fim_corrente, flight["Data de Termino"])
            else:
                if atual:
                    blocos.append(_fechar(campanha, veiculo, atual))
                atual = [flight.to_dict()]
                fim_corrente = flight["Data de Termino"]
        if atual:
            blocos.append(_fechar(campanha, veiculo, atual))
    return pd.DataFrame(blocos)


def _fechar(campanha: str, veiculo: str, flights: list[dict]) -> dict:
    bloco = {
        "Campanha": campanha,
        "Veiculo": veiculo,
        "inicio": min(f["Data de Inicio"] for f in flights),
        "termino": max(f["Data de Termino"] for f in flights),
        "n_flights": len(flights),
        "ids_flight": [f["id_flight"] for f in flights],
    }
    for metrica in METRICAS:
        # soma com skipna=True: investimento nulo do plano nao vira zero silencioso,
        # mas tambem nao contamina o bloco inteiro com NaN. Os nulos sao contados a parte.
        bloco[f"plan_{metrica}"] = pd.Series([f[metrica] for f in flights]).sum(min_count=1)
    bloco["plan_investimento_nulo"] = sum(
        1 for f in flights if pd.isna(f["Soma de Investimento"])
    )
    return bloco


def casar(realizado: pd.DataFrame, blocos: pd.DataFrame) -> pd.DataFrame:
    """Liga cada linha de Realizado ao bloco de plano da mesma campanha, mesmo veiculo
    e cuja janela contem a Data. Retorna um par (id_realizado, bloco) por casamento."""
    if "id_bloco" not in blocos.columns:
        blocos = blocos.reset_index(names="id_bloco")
    pares = realizado.merge(
        blocos[["id_bloco", "Campanha", "Veiculo", "inicio", "termino"]],
        on=CHAVE,
        how="inner",
    )
    dentro = (pares["Data"] >= pares["inicio"]) & (pares["Data"] <= pares["termino"])
    return pares[dentro].copy()
