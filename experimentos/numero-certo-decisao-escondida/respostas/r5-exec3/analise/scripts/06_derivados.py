"""Passo 6: numeros derivados que aparecem no texto das entregas.

Diferencas, folgas e variacoes percentuais que saem dos totais ja registrados.
Existem como script para que o leitor possa refazer a conta, e nao apenas confiar nela.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, ".claude/skills/analise-de-dados/scripts")

from base import CHAVE, carregar, casar, componentes_de_flight
from numeros import carregar as carregar_livro
from numeros import registrar

SCRIPT = __file__


def main() -> int:
    livro = carregar_livro()
    val = {chave: item["valor"] for chave, item in livro.items()}

    # --- folgas e diferencas entre plano e realizado
    registrar("gap.cliques", val["plan.total_cliques"] - val["real.total_cliques"],
              "Cliques planejados que nao foram entregues",
              linhas=livro["real.total_cliques"]["linhas"], script=SCRIPT)
    registrar("gap.investimento", val["real.total_investimento"] - val["plan.total_investimento"],
              "Investimento gasto acima do planejado",
              linhas=livro["real.total_investimento"]["linhas"], unidade="R$", script=SCRIPT)
    registrar("gap.impressoes", val["real.total_impressoes"] - val["plan.total_impressoes"],
              "Impressoes entregues acima do planejado",
              linhas=livro["real.total_impressoes"]["linhas"], script=SCRIPT)

    # --- variacoes percentuais, escritas como excedente e queda
    registrar("var.excedente_impressoes", val["pacing.impressoes"] - 1,
              "Quanto a audiencia superou o plano", linhas=livro["pacing.impressoes"]["linhas"], script=SCRIPT)
    registrar("var.falta_cliques", 1 - val["pacing.cliques"],
              "Quanto o clique ficou abaixo do plano", linhas=livro["pacing.cliques"]["linhas"], script=SCRIPT)
    registrar("var.queda_cpm", 1 - val["real.cpm"] / val["plan.cpm"],
              "Quanto o custo por mil impressoes ficou abaixo da premissa do plano",
              linhas=livro["real.cpm"]["linhas"], script=SCRIPT)
    registrar("var.queda_ctr", 1 - val["real.ctr"] / val["plan.ctr"],
              "Quanto a taxa de clique ficou abaixo da premissa do plano",
              linhas=livro["real.ctr"]["linhas"], script=SCRIPT)

    # --- o flight de Inauguracao no Tiktok, planejado e sem nenhuma entrega
    dados = carregar()
    plan, real = dados.planejado, dados.realizado
    inaug = plan[(plan["Campanha"] == "Inauguracao") & (plan["Veiculo"] == "Tiktok Ads")]
    registrar("inauguracao.investimento_planejado", float(inaug["Soma de Investimento"].sum()),
              "Investimento planejado no flight de Inauguracao no Tiktok, que nao teve entrega",
              linhas=len(inaug), unidade="R$", script=SCRIPT)
    registrar("inauguracao.dias_planejados", float(inaug["Soma de Dias_Veiculacao"].sum()),
              "Dias de veiculacao planejados no flight de Inauguracao no Tiktok",
              linhas=len(inaug), script=SCRIPT)

    # --- verba planejada e nao gasta no Tiktok
    registrar("veiculo.tiktok.verba_nao_gasta",
              val["veiculo.tiktok.plan_investimento"] - val["veiculo.tiktok.real_investimento"],
              "Verba planejada e nao gasta no Tiktok",
              linhas=livro["veiculo.tiktok.plan_investimento"]["linhas"], unidade="R$", script=SCRIPT)

    # --- blocos por veiculo, citados como base das afirmacoes
    blocos = componentes_de_flight(plan).reset_index(names="id_bloco")
    valida = blocos[blocos["plan_Soma de Impressoes"].notna() & (blocos["plan_Soma de Impressoes"] != 0)]
    for veiculo, n in valida["Veiculo"].value_counts().items():
        registrar(f"veiculo.{veiculo.split()[0].lower()}.blocos", int(n),
                  f"Blocos de plano com meta utilizavel em {veiculo}", linhas=len(valida), script=SCRIPT)

    # --- quantos flights sobrevivem ao filtro de denominador
    # nao e 45 menos os 2 flights zerados: um deles divide bloco com um flight que
    # tem meta, entao o bloco continua utilizavel e o flight entra junto
    com_meta = valida["n_flights"].sum()
    registrar("plan.flights_em_blocos_com_meta", int(com_meta),
              "Flights que acabam num bloco com meta utilizavel", linhas=len(plan), script=SCRIPT)

    # --- quantos blocos fecham a verba muito perto do plano
    pares = casar(real, blocos)
    entregue = pares.groupby("id_bloco")["Soma de Investimento"].sum()
    tabela = valida.set_index("id_bloco").join(entregue.rename("real_inv"))
    tabela["real_inv"] = tabela["real_inv"].fillna(0)
    razao = tabela["real_inv"] / tabela["plan_Soma de Investimento"]
    registrar("pacing.blocos_investimento_dentro_de_1pc", int(((razao - 1).abs() < 0.01).sum()),
              "Blocos que fecharam a verba a menos de 1% do plano", linhas=len(tabela), script=SCRIPT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
