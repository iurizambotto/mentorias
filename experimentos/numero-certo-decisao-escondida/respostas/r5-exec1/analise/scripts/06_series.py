"""Passo 6: serie temporal do realizado no plano e retrato do gasto fora do plano.

Alimenta o dashboard e a apresentacao. Nenhum numero novo de pacing nasce
aqui; o que nasce e o recorte por mes, por objetivo e por campanha fora do plano.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd
from comum import carregar
from numeros import registrar

RAIZ = Path(__file__).resolve().parents[1]
plan, _ = carregar()
real = pd.read_csv(RAIZ / "realizado_classificado.csv", parse_dates=["Data"])
valido = pd.read_csv(RAIZ / "pacing_valido.csv")
pares_validos = set(zip(valido["Campanha"], valido["Veiculo"]))

dentro = real[real["motivo"] == "dentro do plano"].copy()
dentro = dentro[[(c, v) in pares_validos for c, v in zip(dentro["Campanha"], dentro["Veiculo"])]]

# Serie diaria e mensal do realizado dentro do plano.
diaria = dentro.groupby("Data")[["Soma de Investimento", "Soma de Impressoes", "Soma de Cliques"]].sum()
diaria.to_csv(RAIZ / "serie_diaria.csv")

dentro["mes"] = dentro["Data"].dt.to_period("M").astype(str)
mensal = dentro.groupby("mes")[["Soma de Investimento", "Soma de Impressoes", "Soma de Cliques"]].sum()
mensal.to_csv(RAIZ / "serie_mensal.csv")
for mes, linha in mensal.iterrows():
    registrar(
        f"mes.{mes.replace('-', '_')}.real_inv",
        linha["Soma de Investimento"],
        f"Investimento realizado dentro do plano em {mes}",
        linhas=len(dentro),
        script=__file__,
        unidade="BRL",
    )

registrar("periodo.dias_com_entrega", dentro["Data"].nunique(), "Dias distintos com entrega dentro do plano", linhas=len(dentro), script=__file__)
registrar(
    "periodo.dias_calendario",
    (real["Data"].max() - real["Data"].min()).days + 1,
    "Dias do calendario entre a primeira e a ultima entrega do arquivo",
    linhas=len(real),
    script=__file__,
)
registrar("cpm.fator", 1000, "Fator de mil impressoes usado no calculo do CPM", linhas=len(dentro), script=__file__)

# CPM e CPC planejado x realizado, que e o que explica o furo de cliques.
for rotulo, pl_num, pl_den, rl_num, rl_den, fator in [
    ("cpm", "inv_plan", "imp_plan", "inv_real", "imp_real", 1000),
    ("cpc", "inv_plan", "cli_plan", "inv_real", "cli_real", 1),
]:
    registrar(f"{rotulo}.planejado", valido[pl_num].sum() / valido[pl_den].sum() * fator, f"{rotulo.upper()} planejado", linhas=len(valido), script=__file__, unidade="BRL")
    registrar(f"{rotulo}.realizado", valido[rl_num].sum() / valido[rl_den].sum() * fator, f"{rotulo.upper()} realizado", linhas=len(valido), script=__file__, unidade="BRL")

registrar("ctr.planejado", valido["cli_plan"].sum() / valido["imp_plan"].sum() * 100, "CTR planejado", linhas=len(valido), script=__file__, unidade="%")
registrar("ctr.realizado", valido["cli_real"].sum() / valido["imp_real"].sum() * 100, "CTR realizado", linhas=len(valido), script=__file__, unidade="%")
registrar("cliques.deficit", valido["cli_plan"].sum() - valido["cli_real"].sum(), "Cliques planejados e nao entregues", linhas=len(valido), script=__file__)

# Pacing de cliques por veiculo.
porv = valido.groupby("Veiculo")[["cli_plan", "cli_real"]].sum()
for veic, linha in porv.iterrows():
    registrar(f"veiculo.{veic.lower().replace(' ', '_')}.pacing_cli", linha["cli_real"] / linha["cli_plan"] * 100, f"Pacing de cliques em {veic}", linhas=len(valido), script=__file__, unidade="%")

# Gasto fora do plano, por campanha.
fora = real[real["motivo"] != "dentro do plano"]
top_fora = (
    fora.groupby("Campanha")[["Soma de Investimento", "Soma de Impressoes", "Soma de Cliques"]]
    .sum()
    .sort_values("Soma de Investimento", ascending=False)
)
top_fora.to_csv(RAIZ / "fora_do_plano_por_campanha.csv")
registrar("fora.campanhas", len(top_fora), "Campanhas com gasto fora da conta de pacing", linhas=len(fora), script=__file__)
registrar("fora.top10_share", top_fora.head(10)["Soma de Investimento"].sum() / fora["Soma de Investimento"].sum() * 100, "Share das 10 maiores campanhas no gasto fora do plano", linhas=len(fora), script=__file__, unidade="%")

fora_motivo = fora.groupby("motivo")["Soma de Investimento"].sum()
fora_motivo.to_csv(RAIZ / "fora_do_plano_por_motivo.csv")
for motivo, valor in fora_motivo.items():
    slug = motivo.replace(" ", "_").replace("ã", "a")
    registrar(f"fora.valor.{slug}", valor, f"Investimento fora do plano: {motivo}", linhas=len(fora), script=__file__, unidade="BRL")

registrar("periodo.realizado_inicio_ano", int(real["Data"].min().year), "Primeiro ano com entrega no arquivo", linhas=len(real), script=__file__)
registrar("fora.antes_do_plano", int((real["Data"] < plan["inicio"].min()).sum()), "Linhas de Realizado anteriores ao inicio do plano", linhas=len(real), script=__file__)
registrar("fora.depois_do_plano", int((real["Data"] > plan["fim"].max()).sum()), "Linhas de Realizado posteriores ao fim do plano", linhas=len(real), script=__file__)

print(mensal.to_string())
print("\ntop 10 campanhas fora do plano:")
print(top_fora.head(10).to_string())
print("\nfora por motivo:")
print(fora_motivo.to_string())
