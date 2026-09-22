#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pacing de campanhas - BASE DE PACING_v2.csv.xls

Regras aplicadas:
  * Planejado = flight (campanha x veiculo x janela Data de Inicio..Data de Termino).
  * Realizado = entrega diaria (campanha x veiculo x Data).
  * Uma linha de Realizado so entra no pacing se casar campanha E veiculo E a Data
    estiver DENTRO da janela do flight (limites inclusivos).
  * Flights sobrepostos (mesma campanha+veiculo, janelas que se cruzam) NAO podem
    contar a mesma linha de Realizado duas vezes: dedup por indice da linha.
  * Campanha sem linha de Planejado fica fora do pacing.
  * Denominador zero/NaN => pacing indefinido (NaN), nunca divisao por zero.

Uso: python3 pacing.py
"""

import pandas as pd
import numpy as np

ARQ = "BASE DE PACING_v2.csv.xls"
METRICAS = ["Soma de Investimento", "Soma de Impressoes", "Soma de Cliques"]

# ---------------------------------------------------------------- 1. carga
df = pd.read_csv(ARQ, encoding="utf-8-sig")

for c in ["Data", "Data de Inicio", "Data de Termino"]:
    df[c] = pd.to_datetime(df[c], errors="coerce").dt.normalize()

plan = df[df["Base"] == "Planejado"].copy().reset_index(drop=True)
real = df[df["Base"] == "Realizado"].copy().reset_index(drop=True)
plan["flight_id"] = plan.index
real["real_id"] = real.index

# chave de casamento (nomes ja vem sem espaco sobrando; normalizo por seguranca)
for d in (plan, real):
    d["k_camp"] = d["Campanha"].str.strip().str.casefold()
    d["k_veic"] = d["Veiculo"].str.strip().str.casefold()

# ------------------------------------------------- 2. casamento flight x dia
pares = plan[["flight_id", "k_camp", "k_veic", "Data de Inicio", "Data de Termino"]].rename(
    columns={"Data de Inicio": "ini", "Data de Termino": "fim"})
cand = real.merge(pares, on=["k_camp", "k_veic"], how="inner")
match = cand[
    (cand["Data"] >= cand["ini"]) & (cand["Data"] <= cand["fim"])
].copy()

# quantas vezes cada linha de Realizado foi capturada por algum flight
vezes = match.groupby("real_id").size()
dupes = vezes[vezes > 1]

# conjunto DEDUPLICADO de linhas de Realizado que entram no pacing
real_ids_in = sorted(vezes.index)
real_in = real[real["real_id"].isin(real_ids_in)]
real_out = real[~real["real_id"].isin(real_ids_in)]

# motivo de exclusao das linhas de Realizado
pares_plan = set(zip(plan["k_camp"], plan["k_veic"]))
tem_par = real_out.apply(lambda r: (r["k_camp"], r["k_veic"]) in pares_plan, axis=1)
fora_sem_plano = int((~tem_par).sum())      # campanha/veiculo nao existe no plano
fora_da_janela = int(tem_par.sum())         # existe no plano, mas data fora do flight

# ------------------------- 3. atribuicao 1-para-1 (visao por flight, sem dupla contagem)
# regra deterministica: vence o flight com denominador valido; depois a janela mais
# curta (mais especifica); empate -> inicio mais cedo -> menor flight_id
plan["den_invalido"] = (
    plan[METRICAS].isna().any(axis=1) | (plan[METRICAS] <= 0).any(axis=1)
).astype(int)
match["dur"] = (match["fim"] - match["ini"]).dt.days
match = match.merge(plan[["flight_id", "den_invalido"]], on="flight_id", how="left")
atrib = (
    match.sort_values(["real_id", "den_invalido", "dur", "ini", "flight_id"])
    .drop_duplicates(subset="real_id", keep="first")
)

# ---------------------------------------------------------------- 4. auditoria
print("=" * 78)
print("AUDITORIA")
print("=" * 78)
print(f"Linhas no arquivo .............................. {len(df):>7,}")
print(f"  Planejado (flights) .......................... {len(plan):>7,}")
print(f"  Realizado (entregas diarias) ................. {len(real):>7,}")
print()
print("PLANEJADO")
print(f"  flights no total ............................. {len(plan):>7,}")
print(f"  pares campanha x veiculo ..................... {plan.groupby(['k_camp','k_veic']).ngroups:>7,}")
sem_real = plan[~plan["flight_id"].isin(match["flight_id"])]
print(f"  flights que NAO capturaram nenhum realizado .. {len(sem_real):>7,}")
if len(sem_real):
    for _, f in sem_real.iterrows():
        print(f"      - {f['Campanha']} / {f['Veiculo']} "
              f"({f['Data de Inicio'].date()} a {f['Data de Termino'].date()})")
print()
print("REALIZADO")
print(f"  linhas que ENTRARAM no pacing ................ {len(real_in):>7,}")
print(f"  linhas que ficaram de FORA ................... {len(real_out):>7,}")
print(f"      campanha/veiculo sem plano ............... {fora_sem_plano:>7,}")
print(f"      dentro do plano, mas fora da janela ...... {fora_da_janela:>7,}")
print(f"  soma confere ({len(real_in)} + {len(real_out)} = {len(real_in)+len(real_out)}): "
      f"{len(real_in)+len(real_out) == len(real)}")
print()
print("DUPLA CONTAGEM (flights sobrepostos)")
print(f"  pares (linha realizado x flight) antes do dedup {len(match):>7,}")
print(f"  linhas de realizado distintas .................. {len(real_ids_in):>7,}")
print(f"  linhas capturadas por MAIS DE UM flight ....... {len(dupes):>7,}")
if len(dupes):
    d = real.set_index("real_id").loc[dupes.index]
    resumo = (d.assign(n=dupes).groupby(["Campanha", "Veiculo"])
                .agg(linhas=("n", "size"), max_flights=("n", "max"),
                     invest_R=("Soma de Investimento", "sum")))
    print(resumo.to_string())
    inflado = (match[match["real_id"].isin(dupes.index)]["Soma de Investimento"].sum()
               - d["Soma de Investimento"].sum())
    print(f"  -> R$ {inflado:,.2f} entrariam em duplicidade se nao houvesse dedup")
print()
print("FLIGHTS SOBREPOSTOS NO PLANO (mesma campanha+veiculo, janelas que se cruzam)")
ov = []
for (c, v), g in plan.groupby(["k_camp", "k_veic"]):
    g = g.sort_values("Data de Inicio")
    rows = g.to_dict("records")
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            a, b = rows[i], rows[j]
            if a["Data de Inicio"] <= b["Data de Termino"] and b["Data de Inicio"] <= a["Data de Termino"]:
                ov.append((a["Campanha"], a["Veiculo"],
                           f"{a['Data de Inicio'].date()}..{a['Data de Termino'].date()}",
                           f"{b['Data de Inicio'].date()}..{b['Data de Termino'].date()}"))
print(f"  pares de flights sobrepostos: {len(ov)}")
for o in ov:
    print(f"      {o[0]} / {o[1]}: {o[2]}  x  {o[3]}")
print()
print("DIVISAO POR ZERO (denominador planejado <= 0 ou ausente)")
z = plan[(plan[METRICAS].isna().any(axis=1)) | ((plan[METRICAS] <= 0).any(axis=1))]
print(f"  flights com denominador zerado/ausente: {len(z)}")
if len(z):
    print(z[["Campanha", "Veiculo", "Data de Inicio", "Data de Termino"] + METRICAS].to_string(index=False))
print("  -> tratados como NaN (pacing indefinido); nenhuma divisao por zero executada.")
print(f"  Realizado com investimento nulo: {int(real['Soma de Investimento'].isna().sum())}")
print()

# ---------------------------------------------------------------- 5. pacing
def pacing(num, den):
    """Divisao segura: denominador 0, negativo ou NaN => NaN."""
    den = pd.to_numeric(den, errors="coerce")
    num = pd.to_numeric(num, errors="coerce")
    return np.where((den.notna()) & (den > 0), num / den.replace({0: np.nan}), np.nan)

# 5a. visao por campanha x veiculo (uniao dos flights; realizado deduplicado)
plan_g = plan.groupby(["Campanha", "Veiculo"], as_index=False)[METRICAS].sum(min_count=1)
real_g = (atrib.merge(plan[["flight_id", "Campanha", "Veiculo"]], on="flight_id",
                      suffixes=("", "_p"))
          .groupby(["Campanha_p", "Veiculo_p"], as_index=False)[METRICAS].sum()
          .rename(columns={"Campanha_p": "Campanha", "Veiculo_p": "Veiculo"}))
tab = plan_g.merge(real_g, on=["Campanha", "Veiculo"], how="left",
                   suffixes=("_plan", "_real")).fillna({f"{m}_real": 0 for m in METRICAS})
for m in METRICAS:
    tab[f"pacing_{m.replace('Soma de ','').lower()}"] = pacing(tab[f"{m}_real"], tab[f"{m}_plan"])

# 5b. visao por flight (atribuicao 1-para-1)
real_f = atrib.groupby("flight_id", as_index=False)[METRICAS].sum()
fl = plan.merge(real_f, on="flight_id", how="left", suffixes=("_plan", "_real"))
for m in METRICAS:
    fl[f"{m}_real"] = fl[f"{m}_real"].fillna(0)
    fl[f"pacing_{m.replace('Soma de ','').lower()}"] = pacing(fl[f"{m}_real"], fl[f"{m}_plan"])

# 5c. total
print("=" * 78)
print("PACING POR CAMPANHA x VEICULO  (realizado dentro da janela, sem dupla contagem)")
print("=" * 78)
out = tab.copy()
out.columns = [c.replace("Soma de ", "") for c in out.columns]
for c in ["Investimento_plan", "Investimento_real"]:
    out[c] = out[c].map(lambda x: f"{x:,.0f}" if pd.notna(x) else "-")
for c in ["Impressoes_plan", "Impressoes_real", "Cliques_plan", "Cliques_real"]:
    out[c] = out[c].map(lambda x: f"{x:,.0f}")
for c in [c for c in out.columns if c.startswith("pacing")]:
    out[c] = out[c].map(lambda x: f"{x:.1%}" if pd.notna(x) else "n/d")
print(out.to_string(index=False))
print()

print("=" * 78)
print("TOTAL DO PLANO")
print("=" * 78)
val = plan[METRICAS].sum(min_count=1)
ent = atrib[METRICAS].sum()
for m in METRICAS:
    nome = m.replace("Soma de ", "")
    p = ent[m] / val[m] if val[m] and val[m] > 0 else float("nan")
    print(f"  {nome:<13} planejado {val[m]:>15,.0f}   realizado {ent[m]:>15,.0f}   pacing {p:>7.1%}")

# sensibilidade: excluir o par sem denominador valido (Joao Pessoa - Nao Pulavel / Youtube)
mask_ok = ~plan["flight_id"].isin(z["flight_id"])
fids_ok = set(plan.loc[mask_ok, "flight_id"])
val2 = plan.loc[mask_ok, METRICAS].sum(min_count=1)
ent2 = atrib[atrib["flight_id"].isin(fids_ok)][METRICAS].sum()
print()
print("  [sensibilidade] excluindo os flights com denominador zerado/ausente:")
for m in METRICAS:
    nome = m.replace("Soma de ", "")
    p = ent2[m] / val2[m] if val2[m] and val2[m] > 0 else float("nan")
    print(f"  {nome:<13} planejado {val2[m]:>15,.0f}   realizado {ent2[m]:>15,.0f}   pacing {p:>7.1%}")

# ---------------------------------------------------------------- 6. exports
tab.to_csv("pacing_por_campanha_veiculo.csv", index=False, encoding="utf-8-sig")
fl.drop(columns=["k_camp", "k_veic"]).to_csv("pacing_por_flight.csv", index=False, encoding="utf-8-sig")
real_out.drop(columns=["k_camp", "k_veic"]).to_csv("realizado_fora_do_pacing.csv", index=False, encoding="utf-8-sig")
print("\nArquivos gerados: pacing_por_campanha_veiculo.csv, pacing_por_flight.csv, realizado_fora_do_pacing.csv")
