"""Passo 1: quantas linhas entram de cada lado da conta de pacing e quantas ficam de fora.

Uma linha de Realizado so entra se, para a mesma Campanha e o mesmo Veiculo,
existir plano e a Data cair dentro de alguma janela de flight.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd
from comum import carregar, em_janelas, uniao_janelas
from numeros import registrar

plan, real = carregar()

registrar(
    "linhas.arquivo",
    len(plan) + len(real),
    "Linhas no arquivo inteiro",
    linhas=len(plan) + len(real),
    script=__file__,
)
registrar("linhas.planejado", len(plan), "Linhas de Planejado (flights)", linhas=len(plan), script=__file__)
registrar("linhas.realizado", len(real), "Linhas de Realizado (entrega diaria)", linhas=len(real), script=__file__)

registrar(
    "grao.realizado_dup_campanha_veiculo_data",
    int(real.duplicated(["Campanha", "Veiculo", "Data"]).sum()),
    "Linhas de Realizado duplicadas na chave campanha+veiculo+data (grao e mais fino)",
    linhas=len(real),
    script=__file__,
)
registrar(
    "grao.realizado_dup_campaign_name",
    int(real.duplicated(["campaign_name", "Veiculo", "Data"]).sum()),
    "Linhas de Realizado duplicadas na chave campaign_name+veiculo+data",
    linhas=len(real),
    script=__file__,
)
for col in ("Objetivo", "Publico"):
    registrar(
        f"nulotexto.{col.lower()}",
        int((real[col] == "N/a").sum() + (plan[col] == "N/a").sum()),
        f"Linhas com o texto N/a em {col}",
        linhas=len(plan) + len(real),
        script=__file__,
    )

janelas = {chave: uniao_janelas(g) for chave, g in plan.groupby(["Campanha", "Veiculo"])}

motivo = pd.Series("dentro do plano", index=real.index)
campanhas_planejadas = set(plan["Campanha"])
for idx, linha in real.iterrows():
    chave = (linha["Campanha"], linha["Veiculo"])
    if linha["Campanha"] not in campanhas_planejadas:
        motivo[idx] = "campanha fora do plano"
    elif chave not in janelas:
        motivo[idx] = "veiculo nao planejado para a campanha"
    elif not em_janelas(pd.Series([linha["Data"]]), janelas[chave]).iloc[0]:
        motivo[idx] = "data fora da janela do flight"

real["motivo"] = motivo
real.to_csv(Path(__file__).resolve().parents[1] / "realizado_classificado.csv", index=False)

dentro = real[real["motivo"] == "dentro do plano"]
registrar(
    "linhas.realizado_dentro",
    len(dentro),
    "Linhas de Realizado que entram na conta de pacing",
    linhas=len(dentro),
    script=__file__,
    decisoes=["janela inclusiva nas duas pontas", "match por Campanha + Veiculo"],
)

for rotulo, chave in [
    ("campanha fora do plano", "linhas.fora_campanha"),
    ("veiculo nao planejado para a campanha", "linhas.fora_veiculo"),
    ("data fora da janela do flight", "linhas.fora_janela"),
]:
    sub = real[real["motivo"] == rotulo]
    registrar(chave, len(sub), f"Linhas de Realizado fora: {rotulo}", linhas=len(sub), script=__file__)

fora = real[real["motivo"] != "dentro do plano"]
registrar("linhas.realizado_fora", len(fora), "Linhas de Realizado fora da conta", linhas=len(fora), script=__file__)
registrar(
    "valor.realizado_fora",
    fora["Soma de Investimento"].sum(),
    "Investimento realizado fora da conta de pacing",
    linhas=len(fora),
    script=__file__,
    unidade="BRL",
)
registrar(
    "valor.realizado_total",
    real["Soma de Investimento"].sum(),
    "Investimento realizado no arquivo inteiro",
    linhas=len(real),
    script=__file__,
    unidade="BRL",
)

flights_sem_entrega = [c for c in janelas if c not in set(zip(dentro["Campanha"], dentro["Veiculo"]))]
registrar(
    "plano.pares_sem_entrega",
    len(flights_sem_entrega),
    "Pares campanha+veiculo planejados sem nenhum realizado na janela",
    linhas=len(plan),
    script=__file__,
)
registrar("plano.pares", len(janelas), "Pares campanha+veiculo com plano", linhas=len(plan), script=__file__)
registrar(
    "plano.campanhas",
    plan["Campanha"].nunique(),
    "Campanhas com linha de Planejado",
    linhas=len(plan),
    script=__file__,
)
registrar(
    "arquivo.campanhas",
    pd.concat([plan["Campanha"], real["Campanha"]]).nunique(),
    "Campanhas distintas no arquivo",
    linhas=len(plan) + len(real),
    script=__file__,
)
registrar(
    "arquivo.campanhas_sem_plano",
    len(set(real["Campanha"]) - campanhas_planejadas),
    "Campanhas que rodaram sem linha de Planejado",
    linhas=len(real),
    script=__file__,
)

print(f"planejado {len(plan)} | realizado {len(real)}")
print(real["motivo"].value_counts().to_string())
print("pares planejados sem entrega na janela:", flights_sem_entrega)
