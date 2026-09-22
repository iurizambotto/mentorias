"""Passo 2. Flights sobrepostos e o tamanho da dupla contagem que eles causam.

Mede o realizado com e sem deduplicacao, para que a escolha de contar cada
entrega uma unica vez esteja declarada com o valor da alternativa.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, ".claude/skills/analise-de-dados/scripts")

from base import CHAVE, METRICAS, Base, carregar, entregas_atribuidas, malha  # noqa: E402
from numeros import registrar  # noqa: E402

ESTE = __file__


def pares_sobrepostos(base: Base) -> pd.DataFrame:
    """Pares de flights da mesma campanha e veiculo com janelas que se cruzam."""
    linhas: list[dict[str, object]] = []
    for (campanha, veiculo), grupo in base.planejado.groupby(CHAVE):
        flights = grupo.sort_values("Data de Inicio").to_dict("records")
        for i, a in enumerate(flights):
            for b in flights[i + 1 :]:
                if a["Data de Inicio"] <= b["Data de Termino"] and (
                    b["Data de Inicio"] <= a["Data de Termino"]
                ):
                    inicio = max(a["Data de Inicio"], b["Data de Inicio"])
                    fim = min(a["Data de Termino"], b["Data de Termino"])
                    linhas.append(
                        {
                            "Campanha": campanha,
                            "Veiculo": veiculo,
                            "flight_a": a["flight_id"],
                            "flight_b": b["flight_id"],
                            "inicio_sobreposicao": inicio,
                            "fim_sobreposicao": fim,
                            "dias": (fim - inicio).days + 1,
                        }
                    )
    return pd.DataFrame(linhas)


def sobreposicao(base: Base) -> None:
    pares = pares_sobrepostos(base)
    registrar(
        "sobreposicao.pares_de_flights",
        len(pares),
        "Pares de flights da mesma campanha e veiculo com janelas que se cruzam",
        linhas=len(base.planejado),
        script=ESTE,
    )
    registrar(
        "sobreposicao.flights_envolvidos",
        len(set(pares["flight_a"]) | set(pares["flight_b"])) if len(pares) else 0,
        "Flights distintos que participam de alguma sobreposicao",
        linhas=len(base.planejado),
        script=ESTE,
    )
    registrar(
        "sobreposicao.combinacoes_afetadas",
        pares.groupby(CHAVE).ngroups if len(pares) else 0,
        "Combinacoes de campanha e veiculo com plano sobreposto",
        linhas=len(base.planejado),
        script=ESTE,
    )
    if len(pares):
        pares.to_csv("analise/sobreposicoes.csv", index=False)

    bruta = malha(base)
    unica = entregas_atribuidas(base)
    registrar(
        "sobreposicao.linhas_malha",
        len(bruta),
        "Pares flight x entrega validos, antes de deduplicar",
        linhas=len(bruta),
        script=ESTE,
    )
    repetidas = bruta["entrega_id"].value_counts()
    repetidas = repetidas[repetidas > 1]
    registrar(
        "sobreposicao.entregas_em_mais_de_um_flight",
        len(repetidas),
        "Linhas de Realizado que casam com mais de um flight",
        linhas=len(bruta),
        script=ESTE,
    )
    registrar(
        "sobreposicao.max_flights_por_entrega",
        int(repetidas.max()) if len(repetidas) else 1,
        "Maior numero de flights que reivindicam a mesma linha de Realizado",
        linhas=len(bruta),
        script=ESTE,
    )

    for metrica, sufixo in zip(METRICAS, ("investimento", "impressoes", "cliques")):
        com = float(bruta[metrica].sum())
        sem = float(unica[metrica].sum())
        registrar(
            f"dupla_contagem.{sufixo}_sem_dedup",
            com,
            f"{metrica} do realizado somando a entrega uma vez por flight que a reivindica",
            linhas=len(bruta),
            script=ESTE,
            decisoes=["alternativa rejeitada: sem deduplicacao"],
        )
        registrar(
            f"dupla_contagem.{sufixo}_com_dedup",
            sem,
            f"{metrica} do realizado com cada entrega contada uma unica vez",
            linhas=len(unica),
            script=ESTE,
            decisoes=["deduplicacao por entrega_id"],
        )
        registrar(
            f"dupla_contagem.{sufixo}_inflacao_pct",
            (com / sem - 1) * 100 if sem else 0.0,
            f"Quanto a nao deduplicacao inflaria {metrica}, em pontos percentuais",
            linhas=len(bruta),
            script=ESTE,
        )


if __name__ == "__main__":
    sobreposicao(carregar())
    print("sobreposicao registrada")
