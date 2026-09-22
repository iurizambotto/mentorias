"""Passo 5: reconciliacao e o valor das alternativas de cada decisao.

Cada decisao declarada em analise/decisoes.md precisa do numero que ela
produziu e do numero que a alternativa produziria. Este script roda as duas
versoes de cada escolha.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd
from comum import carregar, em_janelas, uniao_janelas
from numeros import registrar

RAIZ = Path(__file__).resolve().parents[1]
plan, real = carregar()
valido = pd.read_csv(RAIZ / "pacing_valido.csv")

BASE_PLAN = valido["inv_plan"].sum()
BASE_REAL = valido["inv_real"].sum()
BASE = BASE_REAL / BASE_PLAN * 100

# Alternativa A: join ingenuo, sem deduplicar linha que cai em varios flights.
ingenuo = real.merge(plan[["Campanha", "Veiculo", "flight_id", "inicio", "fim"]], on=["Campanha", "Veiculo"], how="inner")
ingenuo = ingenuo[(ingenuo["Data"] >= ingenuo["inicio"]) & (ingenuo["Data"] <= ingenuo["fim"])]
pares_validos = set(zip(valido["Campanha"], valido["Veiculo"]))
ing_val = ingenuo[[(c, v) in pares_validos for c, v in zip(ingenuo["Campanha"], ingenuo["Veiculo"])]]
registrar(
    "alt.pacing_sem_dedup",
    ing_val["Soma de Investimento"].sum() / BASE_PLAN * 100,
    "Pacing de investimento se a dupla contagem nao fosse corrigida",
    linhas=len(ing_val),
    script=__file__,
    unidade="%",
)

# Alternativa B: ignorar a janela do flight, usar toda a entrega da campanha no veiculo.
sem_janela = real[[(c, v) in pares_validos for c, v in zip(real["Campanha"], real["Veiculo"])]]
registrar(
    "alt.pacing_sem_janela",
    sem_janela["Soma de Investimento"].sum() / BASE_PLAN * 100,
    "Pacing de investimento se a janela do flight fosse ignorada",
    linhas=len(sem_janela),
    script=__file__,
    unidade="%",
)

# Alternativa C: casar so por campanha, ignorando o veiculo.
janelas_camp = {c: uniao_janelas(g) for c, g in plan.groupby("Campanha")}
pecas = [g[em_janelas(g["Data"], janelas_camp[c])] for c, g in real.groupby("Campanha") if c in janelas_camp]
so_campanha = pd.concat(pecas)
registrar(
    "alt.pacing_sem_veiculo",
    so_campanha["Soma de Investimento"].sum() / plan["Soma de Investimento"].sum() * 100,
    "Pacing de investimento se o veiculo fosse ignorado no match",
    linhas=len(so_campanha),
    script=__file__,
    unidade="%",
)

# Alternativa D: manter no agregado o par sem denominador valido, tratando plano nulo como zero.
todos = pd.read_csv(RAIZ / "pacing_por_par.csv")
registrar(
    "alt.realizado_com_par_invalido",
    todos["inv_real"].sum(),
    "Realizado dentro do plano incluindo o par sem denominador valido",
    linhas=len(todos),
    script=__file__,
    unidade="BRL",
)

# Reconciliacao: as partes somam o total?
por_camp = pd.read_csv(RAIZ / "pacing_por_campanha.csv")
por_veic = pd.read_csv(RAIZ / "pacing_por_veiculo.csv")
assert abs(por_camp["inv_real"].sum() - BASE_REAL) < 0.01, "campanhas nao somam o total"
assert abs(por_veic["inv_real"].sum() - BASE_REAL) < 0.01, "veiculos nao somam o total"
assert abs(por_camp["inv_plan"].sum() - BASE_PLAN) < 0.01, "plano por campanha nao soma o total"
registrar("recon.diferenca_campanha", abs(por_camp["inv_real"].sum() - BASE_REAL), "Diferenca da reconciliacao por campanha", linhas=len(por_camp), script=__file__, unidade="BRL")
registrar("recon.diferenca_veiculo", abs(por_veic["inv_real"].sum() - BASE_REAL), "Diferenca da reconciliacao por veiculo", linhas=len(por_veic), script=__file__, unidade="BRL")

# Cobertura: quanto do gasto total do arquivo o plano explica.
registrar(
    "cobertura.share_realizado_no_plano",
    BASE_REAL / real["Soma de Investimento"].sum() * 100,
    "Share do investimento realizado que o plano cobre",
    linhas=len(real),
    script=__file__,
    unidade="%",
)

registrar(
    "alt.maior_distorcao_razao",
    (sem_janela["Soma de Investimento"].sum() / BASE_PLAN * 100) / BASE,
    "Quantas vezes a pior alternativa de metodo distorce o pacing",
    linhas=len(sem_janela),
    script=__file__,
)
registrar(
    "cobertura.share_realizado_fora",
    (1 - BASE_REAL / real["Soma de Investimento"].sum()) * 100,
    "Share do investimento realizado que fica fora da conta de pacing",
    linhas=len(real),
    script=__file__,
    unidade="%",
)

print(f"base (dedup, na janela, por veiculo): {BASE:.2f}%")
print(f"A sem dedup:      {ing_val['Soma de Investimento'].sum() / BASE_PLAN * 100:.2f}%")
print(f"B sem janela:     {sem_janela['Soma de Investimento'].sum() / BASE_PLAN * 100:.2f}%")
print(f"C sem veiculo:    {so_campanha['Soma de Investimento'].sum() / plan['Soma de Investimento'].sum() * 100:.2f}%")
print(f"cobertura do plano sobre o gasto total: {BASE_REAL / real['Soma de Investimento'].sum() * 100:.2f}%")
