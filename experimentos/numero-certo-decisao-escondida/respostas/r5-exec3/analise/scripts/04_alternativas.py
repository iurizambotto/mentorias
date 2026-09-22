"""Passo 4: roda as alternativas de cada decisao que mexe num numero, para que
analise/decisoes.md possa mostrar o resultado escolhido ao lado do rejeitado.
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
CURTO = {"Soma de Investimento": "investimento", "Soma de Impressoes": "impressoes", "Soma de Cliques": "cliques"}


def pacing_de(tabela: pd.DataFrame, metrica: str) -> float:
    plano = tabela[f"plan_{metrica}"]
    valido = plano.notna() & (plano != 0)
    return float(tabela.loc[valido, f"real_{metrica}"].sum()) / float(plano[valido].sum())


def montar(plan: pd.DataFrame, real: pd.DataFrame) -> pd.DataFrame:
    blocos = componentes_de_flight(plan).reset_index(names="id_bloco")
    pares = casar(real, blocos)
    entregue = pares.groupby("id_bloco")[METRICAS].sum()
    tabela = blocos.set_index("id_bloco").join(entregue.add_prefix("real_"))
    for metrica in METRICAS:
        tabela[f"real_{metrica}"] = tabela[f"real_{metrica}"].fillna(0)
    return tabela


def main() -> int:
    dados = carregar()
    plan, real = dados.planejado, dados.realizado

    # --- alternativa A: ignorar o veiculo, casar so por campanha e janela
    plan_sv = plan.assign(Veiculo="_todos")
    real_sv = real.assign(Veiculo="_todos")
    tabela_a = montar(plan_sv, real_sv)
    for metrica, curto in CURTO.items():
        registrar(f"alt.sem_veiculo_{curto}", pacing_de(tabela_a, metrica),
                  f"Pacing de {curto} casando so por campanha e janela (alternativa rejeitada)",
                  linhas=len(tabela_a), script=SCRIPT, decisoes=["alternativa: ignorar veiculo no casamento"])

    # --- alternativa B: agrupar variantes de nome por prefixo (Fds1 Set -> Fds1)
    familias = sorted(set(plan["Campanha"]))
    def familia(nome: str) -> str:
        candidatos = [f for f in familias if nome == f or nome.startswith(f + " ")]
        return max(candidatos, key=len) if candidatos else nome
    plan_f = plan.assign(Campanha=plan["Campanha"].map(familia))
    real_f = real.assign(Campanha=real["Campanha"].map(familia))
    tabela_b = montar(plan_f, real_f)
    for metrica, curto in CURTO.items():
        registrar(f"alt.por_familia_{curto}", pacing_de(tabela_b, metrica),
                  f"Pacing de {curto} agrupando variantes de nome por prefixo (alternativa rejeitada)",
                  linhas=len(tabela_b), script=SCRIPT, decisoes=["alternativa: agrupar variantes de nome"])
    absorvidas = int((real["Campanha"].map(familia) != real["Campanha"]).sum())
    registrar("alt.linhas_absorvidas_por_familia", absorvidas,
              "Linhas de Realizado que mudariam de campanha se as variantes fossem agrupadas",
              linhas=len(real), script=SCRIPT)

    # --- alternativa C: tratar denominador zero/nulo como zero em vez de excluir o bloco
    tabela_c = montar(plan, real)
    for metrica, curto in CURTO.items():
        plano = tabela_c[f"plan_{metrica}"].fillna(0)
        real_soma = float(tabela_c[f"real_{metrica}"].sum())
        # com denominador zero incluido, a soma do plano nao muda; o que muda e o
        # numerador, que passa a contar a entrega dos blocos sem meta
        registrar(f"alt.denominador_zero_incluido_{curto}", real_soma / float(plano.sum()),
                  f"Pacing de {curto} somando tambem a entrega dos blocos sem meta (alternativa rejeitada)",
                  linhas=len(tabela_c), script=SCRIPT, decisoes=["alternativa: incluir blocos sem denominador"])

    # --- alternativa D: pacing como media simples dos blocos, nao agregado
    for metrica, curto in CURTO.items():
        plano = tabela_c[f"plan_{metrica}"]
        valido = plano.notna() & (plano != 0)
        razoes = tabela_c.loc[valido, f"real_{metrica}"] / plano[valido]
        registrar(f"alt.media_simples_{curto}", float(razoes.mean()),
                  f"Pacing de {curto} como media simples dos blocos (alternativa rejeitada)",
                  linhas=int(valido.sum()), script=SCRIPT, decisoes=["alternativa: media simples entre blocos"])

    # --- quanto a entrega sem meta pesa
    sem_meta = tabela_c[~(tabela_c["plan_Soma de Impressoes"].notna() & (tabela_c["plan_Soma de Impressoes"] != 0))]
    registrar("real.impressoes_em_blocos_sem_meta", float(sem_meta["real_Soma de Impressoes"].sum()),
              "Impressoes entregues em blocos cujo plano nao tem meta utilizavel",
              linhas=len(sem_meta), script=SCRIPT)
    registrar("real.investimento_em_blocos_sem_meta", float(sem_meta["real_Soma de Investimento"].sum()),
              "Investimento entregue em blocos cujo plano nao tem meta utilizavel",
              linhas=len(sem_meta), unidade="R$", script=SCRIPT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
