"""Passo 3. Pacing por campanha e veiculo, e os totais que vao para a reuniao.

O grao do pacing e campanha x veiculo, nao flight. Onde o plano tem flights
sobrepostos a entrega diaria nao pode ser atribuida a um flight especifico,
entao o denominador soma os flights daquele par e o numerador conta cada
entrega uma unica vez.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, ".claude/skills/analise-de-dados/scripts")

from base import CHAVE, METRICAS, Base, carregar, entregas_atribuidas, pacing  # noqa: E402
from numeros import registrar  # noqa: E402

ESTE = __file__
SUFIXO = {
    "Soma de Investimento": "investimento",
    "Soma de Impressoes": "impressoes",
    "Soma de Cliques": "cliques",
}


def tabela(base: Base) -> pd.DataFrame:
    """Uma linha por campanha x veiculo, com plano, entrega e pacing."""
    plano = (
        base.planejado.groupby(CHAVE)
        .agg(
            flights=("flight_id", "count"),
            inicio=("Data de Inicio", "min"),
            termino=("Data de Termino", "max"),
            plan_investimento=("Soma de Investimento", "sum"),
            plan_impressoes=("Soma de Impressoes", "sum"),
            plan_cliques=("Soma de Cliques", "sum"),
            investimento_nulo=("Soma de Investimento", lambda s: int(s.isna().sum())),
        )
        .reset_index()
    )
    entregue = (
        entregas_atribuidas(base)
        .groupby(CHAVE)
        .agg(
            dias_entregues=("entrega_id", "count"),
            real_investimento=("Soma de Investimento", "sum"),
            real_impressoes=("Soma de Impressoes", "sum"),
            real_cliques=("Soma de Cliques", "sum"),
        )
        .reset_index()
    )
    antes = len(plano)
    juntos = plano.merge(entregue, on=CHAVE, how="left")
    assert len(juntos) == antes, f"join alterou o numero de linhas: {antes} -> {len(juntos)}"

    for coluna in ("dias_entregues", "real_investimento", "real_impressoes", "real_cliques"):
        juntos[coluna] = juntos[coluna].fillna(0)
    for metrica in ("investimento", "impressoes", "cliques"):
        juntos[f"pacing_{metrica}"] = [
            pacing(r, p)
            for r, p in zip(juntos[f"real_{metrica}"], juntos[f"plan_{metrica}"])
        ]
    return juntos


def denominadores(tab: pd.DataFrame, base: Base) -> None:
    """Passo 4.5. Nenhuma divisao por zero pode passar silenciosa."""
    nulos_plano = int(base.planejado["Soma de Investimento"].isna().sum())
    registrar(
        "denominador.flights_investimento_nulo",
        nulos_plano,
        "Flights do plano sem valor de investimento orcado",
        linhas=len(base.planejado),
        script=ESTE,
    )
    zerados = base.planejado[
        (base.planejado["Soma de Impressoes"] == 0)
        | (base.planejado["Soma de Cliques"] == 0)
    ]
    registrar(
        "denominador.flights_entrega_zerada",
        len(zerados),
        "Flights do plano com impressoes ou cliques orcados em zero",
        linhas=len(base.planejado),
        script=ESTE,
    )
    for metrica in ("investimento", "impressoes", "cliques"):
        indefinidos = int(tab[f"pacing_{metrica}"].isna().sum())
        registrar(
            f"denominador.pares_sem_pacing_{metrica}",
            indefinidos,
            f"Pares campanha x veiculo sem pacing de {metrica} por denominador zero ou nulo",
            linhas=len(tab),
            script=ESTE,
        )
    sem_entrega = tab[tab["dias_entregues"] == 0]
    registrar(
        "denominador.pares_sem_entrega",
        len(sem_entrega),
        "Pares campanha x veiculo planejados que nao tiveram nenhum dia de entrega na janela",
        linhas=len(tab),
        script=ESTE,
    )


def totais(tab: pd.DataFrame) -> None:
    """Totais do plano e da entrega. O total usa apenas os pares cujo
    denominador daquela metrica e valido, para nao misturar universos."""
    registrar(
        "plano.pares_campanha_veiculo",
        len(tab),
        "Pares campanha x veiculo no plano",
        linhas=len(tab),
        script=ESTE,
    )
    for metrica in ("investimento", "impressoes", "cliques"):
        validos = tab[tab[f"pacing_{metrica}"].notna()]
        plan = float(validos[f"plan_{metrica}"].sum())
        real = float(validos[f"real_{metrica}"].sum())
        unidade = "R$" if metrica == "investimento" else ""
        registrar(
            f"total.plan_{metrica}",
            plan,
            f"{metrica} planejado, somando os pares com denominador valido",
            linhas=len(validos),
            script=ESTE,
            unidade=unidade,
        )
        registrar(
            f"total.real_{metrica}",
            real,
            f"{metrica} entregue dentro da janela do plano, cada entrega contada uma vez",
            linhas=len(validos),
            script=ESTE,
            unidade=unidade,
        )
        razao = pacing(real, plan)
        assert razao is not None, f"denominador total zerado em {metrica}"
        registrar(
            f"total.pacing_{metrica}",
            razao * 100,
            f"Pacing de {metrica}: entregue sobre planejado, em percentual",
            linhas=len(validos),
            script=ESTE,
            unidade="%",
            decisoes=["grao campanha x veiculo", "entrega deduplicada", "janela do flight"],
        )
        registrar(
            f"total.gap_{metrica}",
            real - plan,
            f"Diferenca entre entregue e planejado em {metrica}",
            linhas=len(validos),
            script=ESTE,
            unidade=unidade,
        )


def por_campanha(tab: pd.DataFrame) -> pd.DataFrame:
    campanha = (
        tab.groupby("Campanha")
        .agg(
            veiculos=("Veiculo", "nunique"),
            flights=("flights", "sum"),
            dias_entregues=("dias_entregues", "sum"),
            plan_investimento=("plan_investimento", "sum"),
            real_investimento=("real_investimento", "sum"),
            plan_impressoes=("plan_impressoes", "sum"),
            real_impressoes=("real_impressoes", "sum"),
            plan_cliques=("plan_cliques", "sum"),
            real_cliques=("real_cliques", "sum"),
        )
        .reset_index()
    )
    for metrica in ("investimento", "impressoes", "cliques"):
        campanha[f"pacing_{metrica}"] = [
            pacing(r, p)
            for r, p in zip(campanha[f"real_{metrica}"], campanha[f"plan_{metrica}"])
        ]
    return campanha.sort_values("plan_investimento", ascending=False)


def destaques(campanha: pd.DataFrame) -> None:
    com_pacing = campanha[campanha["pacing_investimento"].notna()].copy()
    registrar(
        "campanha.com_pacing_investimento",
        len(com_pacing),
        "Campanhas com pacing de investimento calculavel",
        linhas=len(campanha),
        script=ESTE,
    )
    for faixa, condicao in (
        ("abaixo_80", com_pacing["pacing_investimento"] < 0.8),
        ("dentro_80_120", com_pacing["pacing_investimento"].between(0.8, 1.2)),
        ("acima_120", com_pacing["pacing_investimento"] > 1.2),
    ):
        registrar(
            f"campanha.{faixa}",
            int(condicao.sum()),
            f"Campanhas na faixa de pacing de investimento {faixa.replace('_', ' ')}",
            linhas=len(com_pacing),
            script=ESTE,
        )
    pior = com_pacing.nsmallest(1, "pacing_investimento").iloc[0]
    registrar(
        "campanha.pior_pacing_valor",
        pior["pacing_investimento"] * 100,
        f"Menor pacing de investimento entre as campanhas: {pior['Campanha']}",
        linhas=1,
        script=ESTE,
        unidade="%",
    )
    maior = com_pacing.nlargest(1, "pacing_investimento").iloc[0]
    registrar(
        "campanha.maior_pacing_valor",
        maior["pacing_investimento"] * 100,
        f"Maior pacing de investimento entre as campanhas: {maior['Campanha']}",
        linhas=1,
        script=ESTE,
        unidade="%",
    )
    registrar(
        "campanha.maior_gap_absoluto",
        float((com_pacing["real_investimento"] - com_pacing["plan_investimento"]).abs().max()),
        "Maior diferenca absoluta entre investimento entregue e planejado numa campanha",
        linhas=len(com_pacing),
        script=ESTE,
        unidade="R$",
    )


if __name__ == "__main__":
    base = carregar()
    tab = tabela(base)
    denominadores(tab, base)
    totais(tab)
    campanha = por_campanha(tab)
    destaques(campanha)
    tab.to_csv("analise/pacing_campanha_veiculo.csv", index=False)
    campanha.to_csv("analise/pacing_campanha.csv", index=False)
    print(campanha.to_string(index=False))
