"""Passo 2: flights sobrepostos e dupla contagem.

Mede o join ingenuo (uma linha de Realizado casa com todos os flights cuja
janela a contem) contra o join deduplicado (cada linha de Realizado conta uma
vez por par campanha+veiculo). A diferenca entre os dois e a dupla contagem.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd
from comum import carregar, em_janelas, uniao_janelas
from numeros import registrar

plan, real = carregar()

pares_sobrepostos = []
grupos_sobrepostos = []
for (camp, veic), g in plan.groupby(["Campanha", "Veiculo"]):
    voos = list(g.itertuples())
    cruza = [
        (a.flight_id, b.flight_id)
        for i, a in enumerate(voos)
        for b in voos[i + 1 :]
        if a.inicio <= b.fim and b.inicio <= a.fim
    ]
    if cruza:
        pares_sobrepostos.extend(cruza)
        grupos_sobrepostos.append((camp, veic, len(voos), len(cruza)))

registrar(
    "sobreposicao.grupos",
    len(grupos_sobrepostos),
    "Pares campanha+veiculo com flights de janela sobreposta",
    linhas=len(plan),
    script=__file__,
)
registrar(
    "sobreposicao.pares_flight",
    len(pares_sobrepostos),
    "Pares de flights que se sobrepoem",
    linhas=len(plan),
    script=__file__,
)
registrar(
    "sobreposicao.flights_envolvidos",
    len({f for par in pares_sobrepostos for f in par}),
    "Flights envolvidos em alguma sobreposicao",
    linhas=len(plan),
    script=__file__,
)

# Join ingenuo: explode Realizado contra cada flight cuja janela o contem.
ingenuo = real.merge(
    plan[["Campanha", "Veiculo", "flight_id", "inicio", "fim"]], on=["Campanha", "Veiculo"], how="inner"
)
ingenuo = ingenuo[(ingenuo["Data"] >= ingenuo["inicio"]) & (ingenuo["Data"] <= ingenuo["fim"])]

registrar(
    "join.linhas_ingenuo",
    len(ingenuo),
    "Linhas apos join ingenuo Realizado x flight (com dupla contagem)",
    linhas=len(ingenuo),
    script=__file__,
)

# Join deduplicado: uniao das janelas por par campanha+veiculo.
janelas = {chave: uniao_janelas(g) for chave, g in plan.groupby(["Campanha", "Veiculo"])}
marcas = []
for chave, g in real.groupby(["Campanha", "Veiculo"]):
    if chave in janelas:
        marcas.append(g[em_janelas(g["Data"], janelas[chave])])
dedup = pd.concat(marcas) if marcas else real.iloc[0:0]

registrar(
    "join.linhas_dedup",
    len(dedup),
    "Linhas de Realizado apos deduplicacao (cada linha conta uma vez)",
    linhas=len(dedup),
    script=__file__,
    decisoes=["uniao de janelas por par campanha+veiculo"],
)
registrar(
    "join.linhas_infladas",
    len(ingenuo) - len(dedup),
    "Linhas extras criadas pela dupla contagem do join ingenuo",
    linhas=len(ingenuo),
    script=__file__,
)

contagem = ingenuo.groupby("linha_id").size()
registrar(
    "join.linhas_multiplas",
    int((contagem > 1).sum()),
    "Linhas de Realizado que casaram com mais de um flight",
    linhas=len(dedup),
    script=__file__,
)
registrar(
    "join.max_flights_por_linha",
    int(contagem.max()),
    "Maior numero de flights em que uma unica linha de Realizado caiu",
    linhas=len(dedup),
    script=__file__,
)

for rotulo, col in [("investimento", "Soma de Investimento"), ("impressoes", "Soma de Impressoes")]:
    registrar(
        f"dupla.{rotulo}_ingenuo",
        ingenuo[col].sum(),
        f"Realizado de {rotulo} com dupla contagem (join ingenuo)",
        linhas=len(ingenuo),
        script=__file__,
        unidade="BRL" if col.endswith("Investimento") else "",
    )
    registrar(
        f"dupla.{rotulo}_dedup",
        dedup[col].sum(),
        f"Realizado de {rotulo} deduplicado",
        linhas=len(dedup),
        script=__file__,
        unidade="BRL" if col.endswith("Investimento") else "",
    )

registrar(
    "dupla.investimento_inflado",
    ingenuo["Soma de Investimento"].sum() - dedup["Soma de Investimento"].sum(),
    "Investimento que a dupla contagem teria inventado",
    linhas=len(ingenuo),
    script=__file__,
    unidade="BRL",
)

print("grupos com sobreposicao:")
for camp, veic, n, c in grupos_sobrepostos:
    print(f"  {camp} | {veic}: {n} flights, {c} pares cruzados")
print(f"join ingenuo {len(ingenuo)} linhas | dedup {len(dedup)} linhas | infladas {len(ingenuo) - len(dedup)}")
print(f"linhas que casaram com mais de um flight: {(contagem > 1).sum()} (max {contagem.max()} flights)")
print(
    f"investimento ingenuo R$ {ingenuo['Soma de Investimento'].sum():,.2f} "
    f"vs dedup R$ {dedup['Soma de Investimento'].sum():,.2f}"
)
