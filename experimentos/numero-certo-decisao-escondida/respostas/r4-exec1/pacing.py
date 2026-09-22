#!/usr/bin/env python3
# Pacing = Realizado / Planejado, casando Realizado com o flight pelo
# mesmo Veiculo, mesma Campanha e Data dentro de [Data de Inicio, Data de Termino].
# Rodar: python3 pacing.py

import pandas as pd

ARQ = "BASE DE PACING_v2.csv.xls"   # e' CSV UTF-8 com BOM, apesar da extensao
METRICAS = ["Soma de Investimento", "Soma de Impressoes", "Soma de Cliques"]

df = pd.read_csv(ARQ, encoding="utf-8-sig")
for c in ["Data", "Data de Inicio", "Data de Termino"]:
    df[c] = pd.to_datetime(df[c], errors="coerce")

plan = df[df.Base == "Planejado"].copy().reset_index(drop=True)
plan["flight_id"] = plan.index                      # 1 linha Planejado = 1 flight
real = df[df.Base == "Realizado"].copy().reset_index(drop=True)
real["real_id"] = real.index                        # 1 linha Realizado = 1 dia/campanha/veiculo

# ---------------------------------------------------------------- 1) CASAMENTO
# produto cartesiano por (Campanha, Veiculo) e filtro pela janela do flight
m = real.merge(
    plan[["flight_id", "Campanha", "Veiculo", "Data de Inicio", "Data de Termino"]],
    on=["Campanha", "Veiculo"], how="inner", suffixes=("", "_p"),
)
m = m[(m["Data"] >= m["Data de Inicio_p"]) & (m["Data"] <= m["Data de Termino_p"])]

# ------------------------------------------------- 2) GRUPOS DE FLIGHT (OVERLAP)
# flights da mesma Campanha+Veiculo com janelas que se cruzam viram 1 grupo,
# para que a linha de Realizado entre na conta UMA unica vez.
def grupos(g):
    g = g.sort_values("Data de Inicio")
    gid, fim, out = -1, None, []
    for _, f in g.iterrows():
        if fim is None or f["Data de Inicio"] > fim:
            gid += 1
            fim = f["Data de Termino"]
        else:
            fim = max(fim, f["Data de Termino"])
        out.append((f["flight_id"], f"{f['Campanha']} | {f['Veiculo']} | g{gid}"))
    return out

mapa = dict(x for _, g in plan.groupby(["Campanha", "Veiculo"]) for x in grupos(g))
plan["grupo"] = plan.flight_id.map(mapa)
m["grupo"] = m.flight_id.map(mapa)

# uma linha de Realizado conta uma vez por grupo
dedup = m.drop_duplicates(subset=["real_id", "grupo"])

# ------------------------------------------------------------- 3) AUDITORIA
casadas = set(m.real_id)
dup_flights = (m.groupby("real_id").flight_id.nunique() > 1).sum()
dup_grupos  = (dedup.groupby("real_id").grupo.nunique() > 1).sum()

print("=" * 72, "\n1) LINHAS QUE ENTRARAM / FICARAM DE FORA\n")
print(f"Total de linhas no arquivo ............................ {len(df):>6}")
print(f"  Planejado ........................................... {len(plan):>6}  (todas entram)")
print(f"  Realizado ........................................... {len(real):>6}")
print(f"    entraram (campanha+veiculo batem e data na janela) . {len(casadas):>6}")
print(f"    ficaram de fora ................................... {len(real)-len(casadas):>6}")

fora = real[~real.real_id.isin(casadas)]
sem_plano = ~fora.set_index(["Campanha", "Veiculo"]).index.isin(
    plan.set_index(["Campanha", "Veiculo"]).index)
print(f"      campanha/veiculo sem nenhum flight .............. {sem_plano.sum():>6}")
print(f"      tem flight, mas a data caiu fora da janela ...... {(~sem_plano).sum():>6}")
print(f"\nCampanhas: {plan.Campanha.nunique()} planejadas, {real.Campanha.nunique()} no realizado, "
      f"{dedup.Campanha.nunique()} casadas.")
print(f"Janela do plano: {plan['Data de Inicio'].min():%Y-%m-%d} a {plan['Data de Termino'].max():%Y-%m-%d} | "
      f"Realizado vai de {real.Data.min():%Y-%m-%d} a {real.Data.max():%Y-%m-%d}")

print("\n" + "=" * 72, "\n2) DUPLA CONTAGEM POR FLIGHT SOBREPOSTO\n")
ov = plan.groupby("grupo").flight_id.count()
print(f"Flights: {len(plan)} | grupos apos juntar sobrepostos: {plan.grupo.nunique()}")
print("Grupos com mais de um flight (janelas que se cruzam):")
for g, n in ov[ov > 1].items():
    print(f"  {g:<45} {n} flights")
print(f"\nLinhas de Realizado que bateram em >1 flight ......... {dup_flights}")
print(f"Linhas de Realizado que bateriam em >1 GRUPO ......... {dup_grupos}  (0 = sem dupla contagem)")
print(f"Pares (linha x flight) antes do dedup ................ {len(m)}")
print(f"Pares (linha x grupo)  depois do dedup ............... {len(dedup)}")

print("\n" + "=" * 72, "\n3) DIVISAO POR ZERO\n")
pg = plan.groupby("grupo")[METRICAS].sum(min_count=1)
for c in METRICAS:
    ruins = pg[(pg[c].isna()) | (pg[c] == 0)]
    print(f"{c}: {len(ruins)} grupo(s) com planejado zero/nulo -> pacing indefinido")
    for g, v in ruins[c].items():
        print(f"    {g:<45} planejado = {v}")
print(f"\nLinhas de Planejado com Investimento nulo: {plan['Soma de Investimento'].isna().sum()}")
print("Essas linhas somam como 0 no total e sao excluidas do pacing do proprio grupo.")

# ---------------------------------------------------------------- 4) RESULTADO
rg = dedup.groupby("grupo")[METRICAS].sum()
tab = pg.join(rg, lsuffix="_plan", rsuffix="_real").fillna({c + "_real": 0 for c in METRICAS})
for c in METRICAS:
    den = tab[c + "_plan"].where(tab[c + "_plan"].notna() & (tab[c + "_plan"] != 0))
    tab["pacing_" + c.replace("Soma de ", "")] = tab[c + "_real"] / den

print("\n" + "=" * 72, "\n4) PACING POR GRUPO DE FLIGHT\n")
show = tab[["Soma de Investimento_plan", "Soma de Investimento_real", "pacing_Investimento",
            "pacing_Impressoes", "pacing_Cliques"]].sort_values("pacing_Investimento")
print(show.to_string(float_format=lambda v: f"{v:,.2f}"))

val = tab[tab["Soma de Investimento_plan"].notna() & (tab["Soma de Investimento_plan"] != 0)]
print("\n" + "=" * 72, "\n5) TOTAL (so grupos com planejado valido)\n")
for c in METRICAS:
    v = tab[tab[c + "_plan"].notna() & (tab[c + "_plan"] != 0)]
    print(f"{c:<22} planejado {v[c+'_plan'].sum():>16,.0f}   realizado {v[c+'_real'].sum():>16,.0f}"
          f"   pacing {v[c+'_real'].sum()/v[c+'_plan'].sum():>7.1%}")
print(f"\nGrupos no total: {len(val)} de {len(tab)}")

tab.to_csv("pacing_por_grupo.csv")
real[~real.real_id.isin(casadas)].to_csv("realizado_fora_do_plano.csv", index=False)
print("\nArquivos: pacing_por_grupo.csv, realizado_fora_do_plano.csv")
