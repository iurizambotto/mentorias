"""Passo 3: cortes por veiculo, por campanha e por mes, e as metricas de eficiencia
que explicam por que investimento, impressoes e cliques andam em direcoes diferentes.

Tambem faz a reconciliacao: a soma das partes tem que bater com o total do passo 2.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, ".claude/skills/analise-de-dados/scripts")

from base import CHAVE, METRICAS, carregar, casar, componentes_de_flight
from numeros import carregar as carregar_livro
from numeros import registrar

SCRIPT = __file__
CURTO = {"Soma de Investimento": "investimento", "Soma de Impressoes": "impressoes", "Soma de Cliques": "cliques"}


def main() -> int:
    dados = carregar()
    plan, real = dados.planejado, dados.realizado
    blocos = componentes_de_flight(plan).reset_index(names="id_bloco")
    pares = casar(real, blocos)

    entregue = pares.groupby("id_bloco")[METRICAS].sum()
    tabela = blocos.set_index("id_bloco").join(entregue.add_prefix("real_"))
    for metrica in METRICAS:
        tabela[f"real_{metrica}"] = tabela[f"real_{metrica}"].fillna(0)

    # so blocos com denominador utilizavel entram nos agregados
    utilizavel = tabela["plan_Soma de Impressoes"].notna() & (tabela["plan_Soma de Impressoes"] != 0)
    valida = tabela[utilizavel]

    # --- reconciliacao com o passo 2
    livro = carregar_livro()
    for metrica, curto in CURTO.items():
        esperado = livro[f"real.total_{curto}"]["valor"]
        obtido = float(valida[f"real_{metrica}"].sum())
        assert abs(obtido - esperado) < 0.01, f"reconciliacao falhou em {curto}: {obtido} != {esperado}"
    print("reconciliacao com o passo 2: ok")

    # --- corte por veiculo
    por_veiculo = valida.groupby("Veiculo")[
        [f"plan_{m}" for m in METRICAS] + [f"real_{m}" for m in METRICAS]
    ].sum()
    for veiculo, linha in por_veiculo.iterrows():
        chave = veiculo.split()[0].lower()
        n = int((valida["Veiculo"] == veiculo).sum())
        for metrica, curto in CURTO.items():
            registrar(f"veiculo.{chave}.pacing_{curto}", linha[f"real_{metrica}"] / linha[f"plan_{metrica}"],
                      f"Pacing de {curto} em {veiculo}", linhas=n, script=SCRIPT)
        registrar(f"veiculo.{chave}.plan_investimento", float(linha["plan_Soma de Investimento"]),
                  f"Investimento planejado em {veiculo}", linhas=n, unidade="R$", script=SCRIPT)
        registrar(f"veiculo.{chave}.real_investimento", float(linha["real_Soma de Investimento"]),
                  f"Investimento realizado em {veiculo}", linhas=n, unidade="R$", script=SCRIPT)
    por_veiculo.to_csv("analise/pacing_por_veiculo.csv")

    # --- eficiencia: CPM e CTR, planejado contra realizado
    for lado in ["plan", "real"]:
        cpm = valida[f"{lado}_Soma de Investimento"].sum() / valida[f"{lado}_Soma de Impressoes"].sum() * 1000
        ctr = valida[f"{lado}_Soma de Cliques"].sum() / valida[f"{lado}_Soma de Impressoes"].sum()
        rotulo = "planejado" if lado == "plan" else "realizado"
        registrar(f"{lado}.cpm", cpm, f"CPM {rotulo}", linhas=len(valida), unidade="R$", script=SCRIPT)
        registrar(f"{lado}.ctr", ctr, f"CTR {rotulo}", linhas=len(valida), script=SCRIPT)

    # --- corte por campanha
    por_campanha = valida.groupby("Campanha")[
        [f"plan_{m}" for m in METRICAS] + [f"real_{m}" for m in METRICAS]
    ].sum()
    for metrica, curto in CURTO.items():
        por_campanha[f"pacing_{curto}"] = por_campanha[f"real_{metrica}"] / por_campanha[f"plan_{metrica}"]
    por_campanha.sort_values("pacing_impressoes").to_csv("analise/pacing_por_campanha.csv")

    registrar("campanha.n_no_pacing", len(por_campanha), "Campanhas na conta de pacing",
              linhas=len(valida), script=SCRIPT)
    pior = por_campanha["pacing_impressoes"].idxmin()
    melhor = por_campanha["pacing_impressoes"].idxmax()
    registrar("campanha.pior_pacing_impressoes", float(por_campanha.loc[pior, "pacing_impressoes"]),
              f"Menor pacing de impressoes entre campanhas ({pior})", linhas=1, script=SCRIPT)
    registrar("campanha.melhor_pacing_impressoes", float(por_campanha.loc[melhor, "pacing_impressoes"]),
              f"Maior pacing de impressoes entre campanhas ({melhor})", linhas=1, script=SCRIPT)

    # --- peso do que ficou de fora, em investimento
    dentro_inv = float(valida["real_Soma de Investimento"].sum())
    total_real_inv = float(real["Soma de Investimento"].sum())
    registrar("real.investimento_total_arquivo", total_real_inv,
              "Investimento realizado em todo o arquivo", linhas=len(real), unidade="R$", script=SCRIPT)
    registrar("real.share_investimento_no_pacing", dentro_inv / total_real_inv,
              "Fatia do investimento realizado que a conta de pacing cobre",
              linhas=len(real), script=SCRIPT)

    # --- serie mensal do realizado dentro do pacing
    mensal = pares.assign(mes=pares["Data"].dt.to_period("M").astype(str)).groupby("mes")[METRICAS].sum()
    mensal.to_csv("analise/realizado_mensal.csv")
    print("\n--- realizado dentro do pacing, por mes ---")
    print(mensal.to_string())

    print("\n--- por veiculo ---")
    pd.set_option("display.width", 200)
    print(por_veiculo.to_string())
    print("\n--- por campanha ---")
    print(por_campanha[["pacing_investimento", "pacing_impressoes", "pacing_cliques"]].to_string())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
