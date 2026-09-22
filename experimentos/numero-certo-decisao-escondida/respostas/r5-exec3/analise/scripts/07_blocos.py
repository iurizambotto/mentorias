"""Passo 7: registra o pacing de cada bloco de plano, um id por bloco e metrica.

A tabela de detalhe do dashboard e do Power BI mostra esses valores linha a linha.
Sem registro, seriam numeros visiveis sem lastro no livro.
"""

from __future__ import annotations

import sys
import unicodedata
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, ".claude/skills/analise-de-dados/scripts")

from base import CHAVE, METRICAS, carregar, casar, componentes_de_flight
from numeros import registrar

SCRIPT = __file__
SAIDA = Path("analise/blocos_detalhe.csv")
CURTO = {"Soma de Investimento": "investimento", "Soma de Impressoes": "impressoes", "Soma de Cliques": "cliques"}


def slug(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    limpo = "".join(c.lower() if c.isalnum() else "_" for c in sem_acento)
    return "_".join(p for p in limpo.split("_") if p)


def montar_detalhe() -> pd.DataFrame:
    dados = carregar()
    plan, real = dados.planejado, dados.realizado
    blocos = componentes_de_flight(plan).reset_index(names="id_bloco")
    pares = casar(real, blocos)

    entregue = pares.groupby("id_bloco")[METRICAS].sum()
    dias = pares.groupby("id_bloco")["Data"].nunique().rename("dias_entrega")
    tabela = blocos.set_index("id_bloco").join(entregue.add_prefix("real_")).join(dias)
    for metrica in METRICAS:
        tabela[f"real_{metrica}"] = tabela[f"real_{metrica}"].fillna(0)
    tabela["dias_entrega"] = tabela["dias_entrega"].fillna(0).astype(int)

    for metrica, curto in CURTO.items():
        plano = tabela[f"plan_{metrica}"]
        valido = plano.notna() & (plano != 0)
        tabela[f"pacing_{curto}"] = (tabela[f"real_{metrica}"] / plano).where(valido)

    tabela["slug"] = [slug(f"{c}_{v}") for c, v in zip(tabela["Campanha"], tabela["Veiculo"])]
    # slug repetido quando a mesma campanha e veiculo tem dois blocos em meses diferentes
    tabela["slug"] = tabela["slug"] + "_" + tabela["inicio"].dt.strftime("%m%d")
    return tabela.sort_values(CHAVE + ["inicio"])


def main() -> int:
    tabela = montar_detalhe()
    assert tabela["slug"].is_unique, "slug de bloco repetido"

    for _, linha in tabela.iterrows():
        base_id = f"bloco.{linha['slug']}"
        for curto in CURTO.values():
            valor = linha[f"pacing_{curto}"]
            if pd.isna(valor):
                continue  # bloco sem meta utilizavel: nao existe pacing para registrar
            registrar(f"{base_id}.pacing_{curto}", float(valor),
                      f"Pacing de {curto} em {linha['Campanha']} / {linha['Veiculo']} a partir de {linha['inicio'].date()}",
                      linhas=int(linha["dias_entrega"]), script=SCRIPT)
        # investimento planejado nulo nao vira zero: o plano nao traz o valor, e
        # registrar 0 afirmaria um orcamento de zero real que ninguem definiu
        if pd.notna(linha["plan_Soma de Investimento"]):
            registrar(f"{base_id}.plan_investimento", float(linha["plan_Soma de Investimento"]),
                      f"Investimento planejado em {linha['Campanha']} / {linha['Veiculo']}",
                      linhas=int(linha["n_flights"]), unidade="R$", script=SCRIPT)
        registrar(f"{base_id}.dias_entrega", int(linha["dias_entrega"]),
                  f"Dias de entrega em {linha['Campanha']} / {linha['Veiculo']}",
                  linhas=int(linha["dias_entrega"]), script=SCRIPT)

    colunas = CHAVE + ["inicio", "termino", "n_flights", "dias_entrega"] \
        + [f"plan_{m}" for m in METRICAS] + [f"real_{m}" for m in METRICAS] \
        + [f"pacing_{c}" for c in CURTO.values()] + ["slug"]
    tabela[colunas].to_csv(SAIDA, index=False)
    print(f"gravado {SAIDA} ({len(tabela)} blocos, {tabela['pacing_impressoes'].notna().sum()} com pacing)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
