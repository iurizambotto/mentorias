"""Passo 7: destaques nomeados que aparecem no texto.

Cada campanha citada nos entregaveis precisa do seu numero no livro, senao o
conferidor a recusa. Registra tambem os limites da faixa de pacing aceitavel,
que sao convencao da area e nao resultado de calculo.
"""

from __future__ import annotations

import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd
from comum import ARQUIVO  # noqa: F401  (registra o caminho do livro de numeros no sys.path)
from numeros import registrar

RAIZ = Path(__file__).resolve().parents[1]
porc = pd.read_csv(RAIZ / "pacing_por_campanha.csv")
valido = pd.read_csv(RAIZ / "pacing_valido.csv")

registrar("faixa.limite_inferior", 90, "Limite inferior da faixa de pacing aceitavel (convencao da area)", linhas=len(valido), script=__file__, unidade="%")
registrar("faixa.limite_superior", 110, "Limite superior da faixa de pacing aceitavel (convencao da area)", linhas=len(valido), script=__file__, unidade="%")


def slug(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return "".join(c if c.isalnum() else "_" for c in sem_acento.lower()).strip("_")


for _, linha in porc.iterrows():
    s = slug(linha["Campanha"])
    registrar(f"campanha.{s}.pacing_inv", linha["pacing_inv"], f"Pacing de investimento de {linha['Campanha']}", linhas=len(valido), script=__file__, unidade="%")
    registrar(f"campanha.{s}.plan_inv", linha["inv_plan"], f"Investimento planejado de {linha['Campanha']}", linhas=len(valido), script=__file__, unidade="BRL")
    registrar(f"campanha.{s}.real_inv", linha["inv_real"], f"Investimento realizado de {linha['Campanha']}", linhas=len(valido), script=__file__, unidade="BRL")
    if linha["cli_plan"] > 0:
        registrar(f"campanha.{s}.pacing_cli", linha["cli_real"] / linha["cli_plan"] * 100, f"Pacing de cliques de {linha['Campanha']}", linhas=len(valido), script=__file__, unidade="%")
    if linha["imp_plan"] > 0:
        registrar(f"campanha.{s}.pacing_imp", linha["imp_real"] / linha["imp_plan"] * 100, f"Pacing de impressoes de {linha['Campanha']}", linhas=len(valido), script=__file__, unidade="%")

# Excedente de impressoes, em pontos percentuais acima do plano.
imp_plan, imp_real = valido["imp_plan"].sum(), valido["imp_real"].sum()
registrar("excedente.impressoes_pp", (imp_real / imp_plan - 1) * 100, "Impressoes entregues acima do plano, em pontos percentuais", linhas=len(valido), script=__file__, unidade="%")
registrar("excedente.impressoes_abs", imp_real - imp_plan, "Impressoes entregues acima do plano", linhas=len(valido), script=__file__)

# Razao entre CPC realizado e planejado, citada como "mais caro por clique".
cpc_plan = valido["inv_plan"].sum() / valido["cli_plan"].sum()
cpc_real = valido["inv_real"].sum() / valido["cli_real"].sum()
registrar("cpc.razao", cpc_real / cpc_plan, "Quantas vezes o CPC realizado supera o planejado", linhas=len(valido), script=__file__)

print(porc[["Campanha", "inv_plan", "inv_real", "pacing_inv"]].to_string(index=False))
