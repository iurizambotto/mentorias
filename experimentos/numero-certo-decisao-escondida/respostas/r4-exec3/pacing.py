#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pacing = Realizado / Planejado.

Regras aplicadas (conforme briefing):
  - Planejado  -> 1 linha = 1 flight (campanha x veiculo x janela Inicio..Termino)
  - Realizado  -> 1 linha = entrega de 1 dia (campanha x veiculo x data)
  - Um realizado so entra no pacing se casar Campanha + Veiculo E a Data estiver
    DENTRO da janela do flight (inclusive nas duas pontas).
  - Flights sobrepostos existem. Cada linha de Realizado conta UMA VEZ SO no
    numerador (dedupe por indice da linha).
  - Campanha sem linha de Planejado fica fora do pacing.

Uso: python3 pacing.py
"""

import pandas as pd

ARQ = "BASE DE PACING_v2.csv.xls"  # e um CSV UTF-8 com BOM, apesar da extensao
METRICAS = ["Soma de Investimento", "Soma de Impressoes", "Soma de Cliques"]


def norm(s):
    """Normaliza chave textual (case/espacos) para o join Campanha x Veiculo."""
    return s.astype(str).str.strip().str.casefold()


# ----------------------------------------------------------------------------
# 1. Carga
# ----------------------------------------------------------------------------
df = pd.read_csv(ARQ, encoding="utf-8-sig")
df["Data"] = pd.to_datetime(df["Data"])
df["Data de Inicio"] = pd.to_datetime(df["Data de Inicio"])
df["Data de Termino"] = pd.to_datetime(df["Data de Termino"])
df["k_camp"] = norm(df["Campanha"])
df["k_veic"] = norm(df["Veiculo"])

plan = df[df["Base"] == "Planejado"].copy()
real = df[df["Base"] == "Realizado"].copy()
plan["flight_id"] = plan.index          # id estavel do flight
real["real_id"] = real.index            # id estavel da linha de entrega

print(f"Linhas no arquivo ............... {len(df)}")
print(f"  Planejado (flights) ........... {len(plan)}")
print(f"  Realizado (entregas diarias) .. {len(real)}")

# ----------------------------------------------------------------------------
# 2. Sanidade do Planejado: denominadores zerados / nulos
# ----------------------------------------------------------------------------
print("\n--- Denominadores problematicos no Planejado ---")
ruim = plan[
    plan[METRICAS].isna().any(axis=1) | (plan[METRICAS].fillna(0) == 0).any(axis=1)
]
print(
    ruim[["Campanha", "Veiculo", "Data de Inicio", "Data de Termino"] + METRICAS]
    .to_string(index=False)
    if len(ruim)
    else "nenhum"
)
for m in METRICAS:
    print(f"  {m}: {int((plan[m].fillna(0) == 0).sum())} zerado(s), "
          f"{int(plan[m].isna().sum())} nulo(s)")
print(f"  Realizado com Investimento nulo: {int(real['Soma de Investimento'].isna().sum())}")

# ----------------------------------------------------------------------------
# 3. Flights sobrepostos (mesma campanha + veiculo, janelas que se cruzam)
# ----------------------------------------------------------------------------
print("\n--- Flights sobrepostos no plano ---")
pares = plan.merge(plan, on=["k_camp", "k_veic"], suffixes=("_a", "_b"))
pares = pares[
    (pares["flight_id_a"] < pares["flight_id_b"])
    & (pares["Data de Inicio_a"] <= pares["Data de Termino_b"])
    & (pares["Data de Inicio_b"] <= pares["Data de Termino_a"])
]
if len(pares):
    print(
        pares[["Campanha_a", "Veiculo_a", "flight_id_a", "Data de Inicio_a",
               "Data de Termino_a", "flight_id_b", "Data de Inicio_b",
               "Data de Termino_b"]].to_string(index=False)
    )
else:
    print("nenhum")
print(f"  pares sobrepostos: {len(pares)}")

# ----------------------------------------------------------------------------
# 4. Match Realizado x Flight (campanha + veiculo + data dentro da janela)
# ----------------------------------------------------------------------------
cand = real.merge(
    plan[["k_camp", "k_veic", "flight_id", "Data de Inicio", "Data de Termino"]],
    on=["k_camp", "k_veic"],
    how="inner",
    suffixes=("", "_p"),
)
match = cand[
    (cand["Data"] >= cand["Data de Inicio_p"]) & (cand["Data"] <= cand["Data de Termino_p"])
]

n_por_linha = match.groupby("real_id").size()
dupes = n_por_linha[n_por_linha > 1]
print("\n--- Dupla contagem de Realizado ---")
print(f"  linhas de Realizado que casaram com >1 flight: {len(dupes)}")
if len(dupes):
    det = (
        match[match["real_id"].isin(dupes.index)]
        .groupby(["Campanha", "Veiculo"])["real_id"]
        .nunique()
        .sort_values(ascending=False)
    )
    print(det.to_string())
    print(f"  (soma bruta com dupla contagem = {len(match)} pareamentos "
          f"para {match['real_id'].nunique()} linhas distintas)")

# dedupe: cada linha de Realizado entra uma unica vez
real_in = real[real["real_id"].isin(match["real_id"].unique())].copy()

# ----------------------------------------------------------------------------
# 5. Quem entrou / quem ficou de fora
# ----------------------------------------------------------------------------
camp_plan = set(zip(plan["k_camp"], plan["k_veic"]))
tem_plano_camp = set(plan["k_camp"])

real["motivo"] = "sem plano (campanha nao esta no plano)"
real.loc[real["k_camp"].isin(tem_plano_camp), "motivo"] = "campanha no plano, veiculo fora do plano"
mask_cv = pd.Series(list(zip(real["k_camp"], real["k_veic"])), index=real.index).isin(camp_plan)
real.loc[mask_cv, "motivo"] = "campanha+veiculo no plano, data FORA da janela"
real.loc[real["real_id"].isin(real_in["real_id"]), "motivo"] = "ENTROU no pacing"

print("\n--- Linhas de Realizado por situacao ---")
print(real["motivo"].value_counts().to_string())

flights_sem_entrega = plan[~plan["flight_id"].isin(match["flight_id"].unique())]
print(f"\n--- Flights ---")
print(f"  flights com pelo menos 1 entrega casada: {match['flight_id'].nunique()} de {len(plan)}")
if len(flights_sem_entrega):
    print("  flights SEM nenhuma entrega casada:")
    print(flights_sem_entrega[["Campanha", "Veiculo", "Data de Inicio",
                               "Data de Termino"] + METRICAS].to_string(index=False))

# ----------------------------------------------------------------------------
# 6. Pacing
# ----------------------------------------------------------------------------
def pacing(plan_df, real_df, chaves):
    p = plan_df.groupby(chaves)[METRICAS].sum(min_count=1)
    r = real_df.groupby(chaves)[METRICAS].sum(min_count=1)
    out = p.join(r, how="left", lsuffix="_plan", rsuffix="_real").fillna(
        {f"{m}_real": 0 for m in METRICAS}
    )
    for m in METRICAS:
        den = out[f"{m}_plan"]
        # divisao por zero/nulo -> NaN explicito, nao 0 e nao inf
        out[f"pacing_{m.replace('Soma de ', '')}"] = out[f"{m}_real"].where(
            den.notna() & (den != 0)
        ) / den.where(den.notna() & (den != 0))
    return out


# campanhas que cruzam Planejado x Realizado precisam do mesmo recorte de chave
plan_k = plan.assign(Campanha=plan["k_camp"], Veiculo=plan["k_veic"])
real_k = real_in.assign(Campanha=real_in["k_camp"], Veiculo=real_in["k_veic"])

por_cv = pacing(plan_k, real_k, ["Campanha", "Veiculo"])
por_c = pacing(plan_k, real_k, ["Campanha"])

print("\n--- Pacing por Campanha x Veiculo ---")
print(por_cv.round(3).to_string())
print("\n--- Pacing por Campanha ---")
print(por_c.round(3).to_string())

print("\n--- Total (somente campanhas/veiculos do plano, realizado dentro da janela) ---")
tot_p = plan[METRICAS].sum(min_count=1)
tot_r = real_in[METRICAS].sum(min_count=1)
for m in METRICAS:
    d = tot_p[m]
    val = tot_r[m] / d if pd.notna(d) and d != 0 else float("nan")
    print(f"  {m:<22} planejado={d:>15,.2f}  realizado={tot_r[m]:>15,.2f}  pacing={val:.1%}")

# 6b. Total limpo: fora as campanhas cujo plano nao tem denominador valido.
# 'Joao Pessoa - Nao Pulavel' so casa com o flight de plano zerado/nulo, entao
# entraria no numerador sem ter denominador -> infla o total.
camp_ruins = set(ruim["k_camp"])
so_ruim = camp_ruins - set(
    plan[~plan["flight_id"].isin(ruim["flight_id"])]["k_camp"]
)  # campanhas em que TODOS os flights sao invalidos
print(f"\n  campanhas cujo plano e 100% zerado/nulo: {sorted(so_ruim)}")
plan_ok = plan[~plan["k_camp"].isin(so_ruim)]
real_ok = real_in[~real_in["k_camp"].isin(so_ruim)]
print("--- Total excluindo campanhas sem denominador valido ---")
for m in METRICAS:
    d = plan_ok[m].sum(min_count=1)
    r = real_ok[m].sum(min_count=1)
    print(f"  {m:<22} planejado={d:>15,.2f}  realizado={r:>15,.2f}  pacing={r/d:.1%}  "
          f"delta={r-d:>+15,.2f}")

# ----------------------------------------------------------------------------
# 6c. Sensibilidade: casar tambem por Publico + Modalidade
# (os flights sobrepostos se distinguem por essas colunas)
# ----------------------------------------------------------------------------
CH = ["k_camp", "k_veic", "Publico", "Modalidade"]
cand2 = real.merge(
    plan[CH + ["flight_id", "Data de Inicio", "Data de Termino"]], on=CH, how="inner",
    suffixes=("", "_p"),
)
m2 = cand2[
    (cand2["Data"] >= cand2["Data de Inicio_p"]) & (cand2["Data"] <= cand2["Data de Termino_p"])
]
n2 = m2.groupby("real_id").size()
print("\n--- Sensibilidade: match com Campanha+Veiculo+Publico+Modalidade ---")
print(f"  linhas de Realizado que entram: {m2['real_id'].nunique()}")
print(f"  ainda casam com >1 flight: {int((n2 > 1).sum())}")
real_in2 = real[real["real_id"].isin(m2["real_id"].unique())]
for m in METRICAS:
    d = plan[m].sum(min_count=1)
    r = real_in2[m].sum(min_count=1)
    print(f"  {m:<22} planejado={d:>15,.2f}  realizado={r:>15,.2f}  pacing={r/d:.1%}")

# ----------------------------------------------------------------------------
# 7. Volume que ficou fora do pacing
# ----------------------------------------------------------------------------
fora = real[real["motivo"] != "ENTROU no pacing"]
print("\n--- Realizado FORA do pacing (por motivo) ---")
print(fora.groupby("motivo")[METRICAS].sum().round(2).to_string())
