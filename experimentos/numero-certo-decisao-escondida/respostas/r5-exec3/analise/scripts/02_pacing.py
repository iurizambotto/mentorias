"""Passo 2: pacing = realizado dentro da janela do flight, dividido pelo planejado.

Calcula duas vezes: com deduplicacao (escolhido) e sem (alternativa), para medir o
quanto a sobreposicao de flights inflaria o resultado.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, ".claude/skills/analise-de-dados/scripts")

from base import CHAVE, METRICAS, carregar, casar, componentes_de_flight
from numeros import registrar

SCRIPT = __file__
SAIDA = Path("analise/pacing_por_bloco.csv")
CURTO = {"Soma de Investimento": "investimento", "Soma de Impressoes": "impressoes", "Soma de Cliques": "cliques"}


def main() -> int:
    dados = carregar()
    plan, real = dados.planejado, dados.realizado
    blocos = componentes_de_flight(plan).reset_index(names="id_bloco")

    pares = casar(real, blocos)

    # --- deduplicado: cada linha de Realizado soma em um unico bloco
    entregue = pares.groupby("id_bloco")[METRICAS].sum()
    linhas_por_bloco = pares.groupby("id_bloco").size().rename("linhas_realizado")
    tabela = blocos.set_index("id_bloco").join(entregue.add_prefix("real_")).join(linhas_por_bloco)
    for metrica in METRICAS:
        tabela[f"real_{metrica}"] = tabela[f"real_{metrica}"].fillna(0)
    tabela["linhas_realizado"] = tabela["linhas_realizado"].fillna(0).astype(int)

    for metrica, curto in CURTO.items():
        plano = tabela[f"plan_{metrica}"]
        # denominador zero ou nulo nao vira pacing: fica marcado como indefinido
        valido = plano.notna() & (plano != 0)
        tabela[f"pacing_{curto}"] = (tabela[f"real_{metrica}"] / plano).where(valido)

    tabela.sort_values(["Campanha", "Veiculo"]).to_csv(SAIDA, index=False)
    print(f"gravado {SAIDA} ({len(tabela)} blocos)")

    # --- totais, so sobre blocos com denominador utilizavel
    for metrica, curto in CURTO.items():
        plano = tabela[f"plan_{metrica}"]
        valido = plano.notna() & (plano != 0)
        soma_plan = float(plano[valido].sum())
        soma_real = float(tabela.loc[valido, f"real_{metrica}"].sum())
        n = int(valido.sum())
        registrar(f"plan.total_{curto}", soma_plan, f"{curto} planejado, blocos com denominador utilizavel",
                  linhas=n, unidade="R$" if curto == "investimento" else "", script=SCRIPT)
        registrar(f"real.total_{curto}", soma_real, f"{curto} realizado dentro das janelas, deduplicado",
                  linhas=n, unidade="R$" if curto == "investimento" else "", script=SCRIPT,
                  decisoes=["linha em flights sobrepostos conta uma vez so"])
        registrar(f"pacing.{curto}", soma_real / soma_plan, f"Pacing agregado de {curto}",
                  linhas=n, script=SCRIPT, decisoes=["linha em flights sobrepostos conta uma vez so"])
        registrar(f"pacing.blocos_validos_{curto}", n, f"Blocos com {curto} planejado utilizavel",
                  linhas=len(tabela), script=SCRIPT)

    # --- alternativa: sem deduplicar, cada linha soma em todos os flights que a cobrem
    naive = _sem_deduplicar(real, plan)
    for metrica, curto in CURTO.items():
        plano = plan[metrica]
        valido = plano.notna() & (plano != 0)
        soma_plan = float(plano[valido].sum())
        soma_real = float(naive.reindex(plan.loc[valido, "id_flight"]).fillna(0)[metrica].sum())
        registrar(f"alt.pacing_sem_dedup_{curto}", soma_real / soma_plan,
                  f"Pacing de {curto} contando a linha em cada flight que a cobre (alternativa rejeitada)",
                  linhas=int(valido.sum()), script=SCRIPT, decisoes=["alternativa: sem deduplicacao"])

    # --- quanto do realizado deduplicado esta nos blocos sobrepostos
    sobre = tabela[tabela["n_flights"] > 1]
    registrar("real.investimento_em_blocos_sobrepostos", float(sobre["real_Soma de Investimento"].sum()),
              "Investimento realizado nos blocos que uniram flights sobrepostos",
              linhas=int(sobre["linhas_realizado"].sum()), unidade="R$", script=SCRIPT)

    # --- distribuicao de desempenho
    pi = tabela["pacing_impressoes"].dropna()
    registrar("pacing.blocos_acima_de_100_impressoes", int((pi >= 1).sum()),
              "Blocos que bateram ou passaram a meta de impressoes", linhas=len(pi), script=SCRIPT)
    registrar("pacing.blocos_abaixo_de_80_impressoes", int((pi < 0.8).sum()),
              "Blocos que entregaram menos de 80% das impressoes planejadas", linhas=len(pi), script=SCRIPT)
    registrar("pacing.blocos_sem_entrega", int((tabela["linhas_realizado"] == 0).sum()),
              "Blocos de plano sem nenhuma linha de Realizado na janela", linhas=len(tabela), script=SCRIPT)
    registrar("pacing.mediana_impressoes", float(pi.median()),
              "Pacing mediano de impressoes entre blocos", linhas=len(pi), script=SCRIPT)

    pd.set_option("display.width", 200)
    colunas = CHAVE + ["inicio", "termino", "n_flights", "linhas_realizado",
                       "pacing_investimento", "pacing_impressoes", "pacing_cliques"]
    print("\n--- pacing por bloco ---")
    print(tabela.sort_values("pacing_impressoes", na_position="first")[colunas].to_string(index=False))
    return 0


def _sem_deduplicar(real: pd.DataFrame, plan: pd.DataFrame) -> pd.DataFrame:
    """Soma o realizado em cada flight que cobre a linha, sem tratar a sobreposicao."""
    janelas = plan[["id_flight"] + CHAVE + ["Data de Inicio", "Data de Termino"]].rename(
        columns={"Data de Inicio": "inicio", "Data de Termino": "termino"}
    )
    pares = real[["id_realizado", "Data"] + CHAVE + METRICAS].merge(janelas, on=CHAVE, how="inner")
    dentro = pares[(pares["Data"] >= pares["inicio"]) & (pares["Data"] <= pares["termino"])]
    return dentro.groupby("id_flight")[METRICAS].sum()


if __name__ == "__main__":
    raise SystemExit(main())
