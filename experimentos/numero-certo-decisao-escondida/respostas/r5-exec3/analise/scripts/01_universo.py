"""Passo 1: quantas linhas entram de cada lado da conta de pacing e quantas ficam de fora.

Responde tambem as duas checagens pedidas: linha de Realizado contada em mais de um
flight, e denominador zero ou nulo.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, ".claude/skills/analise-de-dados/scripts")

from base import CHAVE, METRICAS, carregar, casar, componentes_de_flight
from numeros import registrar

SCRIPT = __file__


def main() -> int:
    dados = carregar()
    plan, real = dados.planejado, dados.realizado

    registrar("arquivo.linhas", dados.total_linhas, "Linhas no arquivo", linhas=dados.total_linhas, script=SCRIPT)
    registrar("plan.flights", len(plan), "Linhas de Planejado (flights)", linhas=len(plan), script=SCRIPT)
    registrar("real.linhas", len(real), "Linhas de Realizado (entrega diaria)", linhas=len(real), script=SCRIPT)

    # --- universo temporal de cada lado
    registrar("plan.campanhas", plan["Campanha"].nunique(), "Campanhas com plano", linhas=len(plan), script=SCRIPT)
    registrar("real.campanhas", real["Campanha"].nunique(), "Campanhas com entrega", linhas=len(real), script=SCRIPT)

    blocos = componentes_de_flight(plan)
    registrar("plan.blocos", len(blocos), "Blocos de plano apos unir flights sobrepostos", linhas=len(plan), script=SCRIPT)
    sobrepostos = blocos[blocos["n_flights"] > 1]
    registrar(
        "plan.flights_em_sobreposicao",
        int(sobrepostos["n_flights"].sum()),
        "Flights que dividem janela com outro flight da mesma campanha e veiculo",
        linhas=len(plan), script=SCRIPT,
    )

    # --- casamento
    pares = casar(real, blocos)
    ids_dentro = pares["id_realizado"].unique()
    registrar("real.linhas_no_pacing", len(ids_dentro), "Linhas de Realizado que entram no pacing", linhas=len(real), script=SCRIPT)
    registrar("real.linhas_fora", len(real) - len(ids_dentro), "Linhas de Realizado fora de qualquer flight", linhas=len(real), script=SCRIPT)

    # --- dupla contagem: quantas linhas de Realizado caem em mais de um FLIGHT
    flights_por_linha = _flights_por_linha(real, plan)
    multi = flights_por_linha[flights_por_linha > 1]
    registrar(
        "real.linhas_em_multiplos_flights", len(multi),
        "Linhas de Realizado dentro da janela de mais de um flight",
        linhas=len(real), script=SCRIPT,
        decisoes=["linha em flights sobrepostos conta uma vez so"],
    )
    registrar(
        "real.max_flights_por_linha", int(flights_por_linha.max()),
        "Maior numero de flights que cobrem a mesma linha de Realizado",
        linhas=len(real), script=SCRIPT,
    )
    # cada linha casa com no maximo um bloco: e assim que a contagem unica e garantida
    registrar(
        "real.max_blocos_por_linha", int(pares.groupby("id_realizado").size().max()),
        "Maior numero de blocos de plano que cobrem a mesma linha de Realizado",
        linhas=len(pares), script=SCRIPT,
    )

    # --- por que as linhas ficaram de fora
    fora = real[~real["id_realizado"].isin(ids_dentro)]
    pares_plan = set(map(tuple, plan[CHAVE].values))
    sem_plano = fora[~fora[CHAVE].apply(tuple, axis=1).isin(pares_plan)]
    fora_janela = fora[fora[CHAVE].apply(tuple, axis=1).isin(pares_plan)]
    registrar("real.fora_sem_plano", len(sem_plano), "Linhas fora: campanha/veiculo sem nenhum flight", linhas=len(fora), script=SCRIPT)
    registrar("real.fora_da_janela", len(fora_janela), "Linhas fora: campanha/veiculo planejado, data fora da janela", linhas=len(fora), script=SCRIPT)
    registrar(
        "real.investimento_fora", float(fora["Soma de Investimento"].sum()),
        "Investimento realizado fora do pacing", linhas=len(fora), unidade="R$", script=SCRIPT,
    )
    registrar(
        "real.campanhas_sem_plano",
        int(real.loc[~real["Campanha"].isin(set(plan["Campanha"])), "Campanha"].nunique()),
        "Campanhas com entrega e sem nenhuma linha de Planejado", linhas=len(real), script=SCRIPT,
    )

    # --- denominadores: zero ou nulo no planejado
    for metrica in METRICAS:
        alvo = metrica.replace("Soma de ", "").lower()
        registrar(
            f"plan.zero_{alvo}", int((plan[metrica] == 0).sum()),
            f"Flights com {alvo} planejado igual a zero", linhas=len(plan), script=SCRIPT,
        )
        registrar(
            f"plan.nulo_{alvo}", int(plan[metrica].isna().sum()),
            f"Flights com {alvo} planejado nulo", linhas=len(plan), script=SCRIPT,
        )
    ruins = plan[
        (plan["Soma de Impressoes"] == 0) | plan["Soma de Investimento"].isna() | (plan["Soma de Cliques"] == 0)
    ]
    registrar(
        "plan.flights_sem_denominador", len(ruins),
        "Flights sem denominador utilizavel (zero ou nulo em alguma metrica)", linhas=len(plan), script=SCRIPT,
    )
    print("\nFlights sem denominador utilizavel:")
    print(ruins[CHAVE + ["Data de Inicio", "Data de Termino"] + METRICAS].to_string(index=False))

    print("\nBlocos com flights sobrepostos:")
    print(sobrepostos[CHAVE + ["inicio", "termino", "n_flights"]].to_string(index=False))

    # --- cobertura temporal dos dois lados
    print("\nJanela Planejado:", plan["Data de Inicio"].min().date(), "a", plan["Data de Termino"].max().date())
    print("Janela Realizado:", real["Data"].min().date(), "a", real["Data"].max().date())
    dentro_periodo = real[
        (real["Data"] >= plan["Data de Inicio"].min()) & (real["Data"] <= plan["Data de Termino"].max())
    ]
    registrar(
        "real.linhas_no_periodo_do_plano", len(dentro_periodo),
        "Linhas de Realizado dentro do periodo coberto pelo plano, qualquer campanha",
        linhas=len(real), script=SCRIPT,
    )
    return 0


def _flights_por_linha(real: pd.DataFrame, plan: pd.DataFrame) -> pd.Series:
    """Quantos flights individuais cobrem cada linha de Realizado."""
    janelas = plan[["id_flight"] + CHAVE + ["Data de Inicio", "Data de Termino"]].rename(
        columns={"Data de Inicio": "inicio", "Data de Termino": "termino"}
    )
    # o lado Realizado carrega as colunas de janela vazias; so as do plano interessam
    pares = real[["id_realizado", "Data"] + CHAVE].merge(janelas, on=CHAVE, how="left")
    dentro = (pares["Data"] >= pares["inicio"]) & (pares["Data"] <= pares["termino"])
    return pares[dentro].groupby("id_realizado").size().reindex(real["id_realizado"], fill_value=0)


if __name__ == "__main__":
    raise SystemExit(main())
