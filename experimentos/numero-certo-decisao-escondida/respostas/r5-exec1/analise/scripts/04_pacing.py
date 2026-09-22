"""Passo 4: o pacing.

Regra: para cada par campanha+veiculo, planejado e a soma dos flights e
realizado e a soma das linhas de Realizado que caem na uniao das janelas
daquele par. A uniao garante que uma linha conte uma vez so, mesmo quando
o plano tem flights sobrepostos.

Pares sem denominador valido saem do agregado e sao reportados a parte, para
que nem o numerador nem o denominador fiquem com metade da historia.
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
g = pd.read_csv(RAIZ / "pacing_por_par.csv")

valido = g[(g["inv_plan"].notna()) & (g["inv_plan"] > 0) & (g["imp_plan"] > 0) & (g["cli_plan"] > 0)].copy()
invalido = g.drop(valido.index)

registrar("pacing.pares_no_agregado", len(valido), "Pares campanha+veiculo no agregado de pacing", linhas=len(g), script=__file__)

for rotulo, pl, rl, unidade in [
    ("investimento", "inv_plan", "inv_real", "BRL"),
    ("impressoes", "imp_plan", "imp_real", ""),
    ("cliques", "cli_plan", "cli_real", ""),
]:
    planejado = valido[pl].sum()
    realizado = valido[rl].sum()
    registrar(f"plan.{rotulo}", planejado, f"Planejado total de {rotulo}", linhas=len(plan), script=__file__, unidade=unidade)
    registrar(f"real.{rotulo}", realizado, f"Realizado total de {rotulo} dentro do plano", linhas=int(valido.shape[0]), script=__file__, unidade=unidade)
    registrar(
        f"pacing.{rotulo}",
        realizado / planejado * 100,
        f"Pacing de {rotulo} (realizado / planejado)",
        linhas=len(valido),
        script=__file__,
        unidade="%",
        decisoes=["uniao de janelas evita dupla contagem", "pares sem denominador valido fora do agregado"],
    )

valido["pacing_inv"] = valido["inv_real"] / valido["inv_plan"] * 100
valido["pacing_imp"] = valido["imp_real"] / valido["imp_plan"] * 100
valido["pacing_cli"] = valido["cli_real"] / valido["cli_plan"] * 100
valido = valido.sort_values("pacing_inv")
valido.to_csv(RAIZ / "pacing_valido.csv", index=False)

registrar("pacing.pares_abaixo_90", int((valido["pacing_inv"] < 90).sum()), "Pares com pacing de investimento abaixo de 90%", linhas=len(valido), script=__file__)
registrar("pacing.pares_acima_110", int((valido["pacing_inv"] > 110).sum()), "Pares com pacing de investimento acima de 110%", linhas=len(valido), script=__file__)
registrar("pacing.pares_na_faixa", int(valido["pacing_inv"].between(90, 110).sum()), "Pares com pacing de investimento entre 90% e 110%", linhas=len(valido), script=__file__)
registrar("pacing.pares_zerados", int((valido["inv_real"] == 0).sum()), "Pares planejados sem nenhuma entrega na janela", linhas=len(valido), script=__file__)
registrar("pacing.mediana_par", valido["pacing_inv"].median(), "Mediana do pacing de investimento por par", linhas=len(valido), script=__file__, unidade="%")

subentrega = valido[valido["pacing_inv"] < 90]
registrar("pacing.verba_nao_entregue", (subentrega["inv_plan"] - subentrega["inv_real"]).sum(), "Verba planejada e nao entregue nos pares abaixo de 90%", linhas=len(subentrega), script=__file__, unidade="BRL")
registrar("pacing.gap_total", valido["inv_plan"].sum() - valido["inv_real"].sum(), "Diferenca entre investimento planejado e realizado", linhas=len(valido), script=__file__, unidade="BRL")
registrar("pacing.excedente_investimento", valido["inv_real"].sum() - valido["inv_plan"].sum(), "Investimento realizado acima do planejado, no agregado", linhas=len(valido), script=__file__, unidade="BRL")

# Por campanha, para o relatorio.
porc = valido.groupby("Campanha")[["inv_plan", "inv_real", "imp_plan", "imp_real", "cli_plan", "cli_real"]].sum()
porc["pacing_inv"] = porc["inv_real"] / porc["inv_plan"] * 100
porc = porc.sort_values("pacing_inv")
porc.to_csv(RAIZ / "pacing_por_campanha.csv")
registrar("pacing.campanhas_no_agregado", len(porc), "Campanhas no agregado de pacing", linhas=len(valido), script=__file__)

# Por veiculo.
porv = valido.groupby("Veiculo")[["inv_plan", "inv_real", "imp_plan", "imp_real", "cli_plan", "cli_real"]].sum()
porv["pacing_inv"] = porv["inv_real"] / porv["inv_plan"] * 100
porv["pacing_imp"] = porv["imp_real"] / porv["imp_plan"] * 100
porv.to_csv(RAIZ / "pacing_por_veiculo.csv")
for veic, linha in porv.iterrows():
    slug = veic.lower().replace(" ", "_")
    registrar(f"veiculo.{slug}.pacing_inv", linha["pacing_inv"], f"Pacing de investimento em {veic}", linhas=len(valido), script=__file__, unidade="%")
    registrar(f"veiculo.{slug}.pacing_imp", linha["pacing_imp"], f"Pacing de impressoes em {veic}", linhas=len(valido), script=__file__, unidade="%")
    registrar(f"veiculo.{slug}.plan_inv", linha["inv_plan"], f"Investimento planejado em {veic}", linhas=len(valido), script=__file__, unidade="BRL")
    registrar(f"veiculo.{slug}.real_inv", linha["inv_real"], f"Investimento realizado em {veic}", linhas=len(valido), script=__file__, unidade="BRL")

print(f"pares no agregado: {len(valido)} | fora por denominador: {len(invalido)}")
print(porv.to_string())
print("\npacing por campanha:")
print(porc.to_string())
