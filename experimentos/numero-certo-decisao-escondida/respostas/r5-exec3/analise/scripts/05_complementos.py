"""Passo 5: numeros citados no texto que ainda nao tinham script proprio.

Existem porque o conferidor apontou falta de lastro em analise/decisoes.md.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, ".claude/skills/analise-de-dados/scripts")

from base import METRICAS, carregar, casar, componentes_de_flight
from numeros import carregar as carregar_livro
from numeros import registrar

SCRIPT = __file__


def main() -> int:
    livro = carregar_livro()

    # --- o quanto a falta de deduplicacao inflaria cada metrica
    for curto in ["investimento", "impressoes", "cliques"]:
        escolhido = livro[f"pacing.{curto}"]["valor"]
        alternativa = livro[f"alt.pacing_sem_dedup_{curto}"]["valor"]
        registrar(f"alt.inflacao_sem_dedup_{curto}", alternativa / escolhido - 1,
                  f"Quanto o pacing de {curto} subiria sem deduplicar os flights sobrepostos",
                  linhas=livro[f"pacing.blocos_validos_{curto}"]["linhas"], script=SCRIPT,
                  decisoes=["alternativa: sem deduplicacao"])

    dados = carregar()
    plan, real = dados.planejado, dados.realizado

    # --- o bloco sem meta: quantos dias de entrega recebeu
    blocos = componentes_de_flight(plan).reset_index(names="id_bloco")
    pares = casar(real, blocos)
    sem_meta = blocos[~(blocos["plan_Soma de Impressoes"].notna() & (blocos["plan_Soma de Impressoes"] != 0))]
    ids = set(sem_meta["id_bloco"])
    linhas_sem_meta = pares[pares["id_bloco"].isin(ids)]
    registrar("real.dias_em_blocos_sem_meta", linhas_sem_meta["Data"].nunique(),
              "Dias de entrega em blocos de plano sem meta utilizavel",
              linhas=len(linhas_sem_meta), script=SCRIPT)

    # --- a amplitude de investimento entre blocos, que a media simples ignora
    valida = blocos[blocos["plan_Soma de Impressoes"].notna() & (blocos["plan_Soma de Impressoes"] != 0)]
    registrar("plan.menor_investimento_bloco", float(valida["plan_Soma de Investimento"].min()),
              "Menor investimento planejado em um bloco", linhas=len(valida), unidade="R$", script=SCRIPT)
    registrar("plan.maior_investimento_bloco", float(valida["plan_Soma de Investimento"].max()),
              "Maior investimento planejado em um bloco", linhas=len(valida), unidade="R$", script=SCRIPT)

    # --- qualidade das colunas de classificacao
    bruto = pd.read_csv("BASE DE PACING_v2.csv.xls", encoding="utf-8-sig")
    for coluna in ["Objetivo", "Publico"]:
        registrar(f"qualidade.{coluna.lower()}_nulo_em_texto", int((bruto[coluna] == "N/a").sum()),
                  f"Linhas com {coluna} preenchido com o texto N/a", linhas=len(bruto), script=SCRIPT)

    # --- entrega fora da janela: peso em investimento, separado de quem nao tem plano
    from base import CHAVE
    ids_dentro = set(pares["id_realizado"])
    fora = real[~real["id_realizado"].isin(ids_dentro)]
    pares_plan = set(map(tuple, plan[CHAVE].values))
    fora_janela = fora[fora[CHAVE].apply(tuple, axis=1).isin(pares_plan)]
    registrar("real.investimento_fora_da_janela", float(fora_janela["Soma de Investimento"].sum()),
              "Investimento de campanha e veiculo planejados, entregue fora da janela do flight",
              linhas=len(fora_janela), unidade="R$", script=SCRIPT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
