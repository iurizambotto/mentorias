"""Passo 3: denominadores zerados, nulos ou ausentes.

O pacing e realizado / planejado. Onde o planejado e zero ou nulo, a divisao
nao existe e precisa aparecer como achado, nao como celula vazia.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd
from comum import METRICAS, carregar, em_janelas, uniao_janelas
from numeros import registrar

plan, real = carregar()

suspeitos = plan[
    (plan["Soma de Investimento"].isna())
    | (plan["Soma de Investimento"] == 0)
    | (plan["Soma de Impressoes"] == 0)
    | (plan["Soma de Cliques"] == 0)
]
registrar(
    "zero.flights_denominador_invalido",
    len(suspeitos),
    "Flights com alguma metrica planejada zerada ou nula",
    linhas=len(plan),
    script=__file__,
)
registrar(
    "zero.flights_investimento_nulo",
    int(plan["Soma de Investimento"].isna().sum()),
    "Flights sem investimento planejado (nulo)",
    linhas=len(plan),
    script=__file__,
)

janelas = {chave: uniao_janelas(g) for chave, g in plan.groupby(["Campanha", "Veiculo"])}
grupos = plan.groupby(["Campanha", "Veiculo"])[METRICAS].sum(min_count=1)

linhas = []
for chave, planejado in grupos.iterrows():
    sub = real[(real["Campanha"] == chave[0]) & (real["Veiculo"] == chave[1])]
    entregue = sub[em_janelas(sub["Data"], janelas[chave])] if len(sub) else sub
    linhas.append(
        {
            "Campanha": chave[0],
            "Veiculo": chave[1],
            "inv_plan": planejado["Soma de Investimento"],
            "inv_real": entregue["Soma de Investimento"].sum(),
            "imp_plan": planejado["Soma de Impressoes"],
            "imp_real": entregue["Soma de Impressoes"].sum(),
            "cli_plan": planejado["Soma de Cliques"],
            "cli_real": entregue["Soma de Cliques"].sum(),
        }
    )
g = pd.DataFrame(linhas)

quebrados = g[(g["inv_plan"].isna()) | (g["inv_plan"] == 0) | (g["imp_plan"] == 0) | (g["cli_plan"] == 0)]
registrar(
    "zero.pares_denominador_invalido",
    len(quebrados),
    "Pares campanha+veiculo em que o pacing nao pode ser calculado",
    linhas=len(g),
    script=__file__,
)
registrar(
    "zero.realizado_sem_denominador",
    quebrados["inv_real"].sum(),
    "Investimento realizado em pares sem denominador valido",
    linhas=len(quebrados),
    script=__file__,
    unidade="BRL",
)
registrar(
    "zero.impressoes_sem_denominador",
    quebrados["imp_real"].sum(),
    "Impressoes realizadas em pares sem denominador valido",
    linhas=len(quebrados),
    script=__file__,
)

g.to_csv(Path(__file__).resolve().parents[1] / "pacing_por_par.csv", index=False)

print("flights com metrica planejada zerada ou nula:")
print(
    suspeitos[["Campanha", "Veiculo", "inicio", "fim", *METRICAS]].to_string(index=False)
)
print("\npares em que o pacing nao pode ser calculado:")
print(quebrados.to_string(index=False))
