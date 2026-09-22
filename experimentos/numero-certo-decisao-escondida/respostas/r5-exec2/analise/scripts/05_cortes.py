"""Passo 6. Cortes por veiculo e por mes, e a tabela de flights para o detalhe.

Alimenta o documento, o dashboard e a apresentacao. Nada aqui inventa recorte
novo: e a mesma malha deduplicada do passo 3, agregada por outras chaves.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, ".claude/skills/analise-de-dados/scripts")

from base import CHAVE, Base, carregar, entregas_atribuidas, malha, pacing  # noqa: E402
from numeros import registrar  # noqa: E402

ESTE = __file__


def por_veiculo(base: Base) -> pd.DataFrame:
    plano = base.planejado.groupby("Veiculo").agg(
        flights=("flight_id", "count"),
        plan_investimento=("Soma de Investimento", "sum"),
        plan_impressoes=("Soma de Impressoes", "sum"),
        plan_cliques=("Soma de Cliques", "sum"),
    )
    real = entregas_atribuidas(base).groupby("Veiculo").agg(
        dias_entregues=("entrega_id", "count"),
        real_investimento=("Soma de Investimento", "sum"),
        real_impressoes=("Soma de Impressoes", "sum"),
        real_cliques=("Soma de Cliques", "sum"),
    )
    tab = plano.join(real, how="left").fillna(0).reset_index()
    for metrica in ("investimento", "impressoes", "cliques"):
        tab[f"pacing_{metrica}"] = [
            pacing(r, p) for r, p in zip(tab[f"real_{metrica}"], tab[f"plan_{metrica}"])
        ]
    for _, linha in tab.iterrows():
        chave = linha["Veiculo"].split()[0].lower()
        registrar(
            f"veiculo.{chave}.pacing_investimento",
            linha["pacing_investimento"] * 100,
            f"Pacing de investimento em {linha['Veiculo']}",
            linhas=int(linha["dias_entregues"]),
            script=ESTE,
            unidade="%",
        )
        registrar(
            f"veiculo.{chave}.pacing_impressoes",
            linha["pacing_impressoes"] * 100,
            f"Pacing de impressoes em {linha['Veiculo']}",
            linhas=int(linha["dias_entregues"]),
            script=ESTE,
            unidade="%",
        )
        registrar(
            f"veiculo.{chave}.plan_investimento",
            float(linha["plan_investimento"]),
            f"Investimento planejado em {linha['Veiculo']}",
            linhas=int(linha["flights"]),
            script=ESTE,
            unidade="R$",
        )
        registrar(
            f"veiculo.{chave}.real_investimento",
            float(linha["real_investimento"]),
            f"Investimento entregue na janela em {linha['Veiculo']}",
            linhas=int(linha["dias_entregues"]),
            script=ESTE,
            unidade="R$",
        )
    return tab


def por_mes(base: Base) -> pd.DataFrame:
    """Entrega dentro do plano, mes a mes. O plano nao tem grao diario, entao
    o mes usa a data da entrega e serve para mostrar ritmo, nao pacing."""
    atrib = entregas_atribuidas(base).copy()
    atrib["mes"] = atrib["Data"].dt.to_period("M").astype(str)
    tab = (
        atrib.groupby("mes")
        .agg(
            dias=("entrega_id", "count"),
            real_investimento=("Soma de Investimento", "sum"),
            real_impressoes=("Soma de Impressoes", "sum"),
            real_cliques=("Soma de Cliques", "sum"),
        )
        .reset_index()
    )
    registrar(
        "mes.quantidade",
        len(tab),
        "Meses com entrega dentro de alguma janela do plano",
        linhas=len(atrib),
        script=ESTE,
    )
    return tab


def flights_detalhe(base: Base) -> pd.DataFrame:
    """Um flight por linha, com a entrega que ele reivindica.

    A coluna entrega_compartilhada avisa quando aquele realizado tambem e
    reivindicado por outro flight, caso em que o pacing do flight isolado
    nao pode ser somado com o dos vizinhos.
    """
    bruta = malha(base)
    contagem = bruta["entrega_id"].value_counts()
    bruta = bruta.assign(compartilhada=bruta["entrega_id"].map(contagem) > 1)
    agregado = (
        bruta.groupby("flight_id")
        .agg(
            dias_entregues=("entrega_id", "count"),
            dias_compartilhados=("compartilhada", "sum"),
            real_investimento=("Soma de Investimento", "sum"),
            real_impressoes=("Soma de Impressoes", "sum"),
            real_cliques=("Soma de Cliques", "sum"),
        )
    )
    colunas = [
        "flight_id", *CHAVE, "Modalidade", "Objetivo", "Publico",
        "Data de Inicio", "Data de Termino", "Soma de Dias_Veiculacao",
        "Soma de Investimento", "Soma de Impressoes", "Soma de Cliques",
    ]
    tab = base.planejado[colunas].merge(
        agregado, left_on="flight_id", right_index=True, how="left"
    )
    assert len(tab) == len(base.planejado), "detalhe de flight mudou o numero de linhas"
    tab = tab.rename(
        columns={
            "Soma de Investimento": "plan_investimento",
            "Soma de Impressoes": "plan_impressoes",
            "Soma de Cliques": "plan_cliques",
            "Soma de Dias_Veiculacao": "dias_planejados",
        }
    )
    for coluna in ("dias_entregues", "dias_compartilhados", "real_investimento",
                   "real_impressoes", "real_cliques"):
        tab[coluna] = tab[coluna].fillna(0)
    for metrica in ("investimento", "impressoes", "cliques"):
        tab[f"pacing_{metrica}"] = [
            pacing(r, p) for r, p in zip(tab[f"real_{metrica}"], tab[f"plan_{metrica}"])
        ]
    tab["entrega_compartilhada"] = tab["dias_compartilhados"] > 0
    registrar(
        "flight.com_entrega_compartilhada",
        int(tab["entrega_compartilhada"].sum()),
        "Flights cujo realizado e disputado com outro flight sobreposto",
        linhas=len(tab),
        script=ESTE,
    )
    registrar(
        "flight.sem_entrega_na_janela",
        int((tab["dias_entregues"] == 0).sum()),
        "Flights que nao tiveram nenhum dia de entrega dentro da propria janela",
        linhas=len(tab),
        script=ESTE,
    )
    registrar(
        "flight.investimento_sem_entrega",
        float(tab[tab["dias_entregues"] == 0]["plan_investimento"].sum()),
        "Investimento planejado em flights que nao registraram entrega na janela",
        linhas=int((tab["dias_entregues"] == 0).sum()),
        script=ESTE,
        unidade="R$",
    )
    return tab


if __name__ == "__main__":
    base = carregar()
    veiculo = por_veiculo(base)
    mes = por_mes(base)
    flights = flights_detalhe(base)
    veiculo.to_csv("analise/pacing_veiculo.csv", index=False)
    mes.to_csv("analise/entrega_por_mes.csv", index=False)
    flights.to_csv("analise/flights_detalhe.csv", index=False)
    print(veiculo.to_string(index=False))
    print()
    print(mes.to_string(index=False))
