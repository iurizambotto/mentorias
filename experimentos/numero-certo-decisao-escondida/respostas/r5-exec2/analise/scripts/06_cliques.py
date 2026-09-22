"""Passo 7. Por que o pacing de cliques destoa dos outros dois.

O plano nao mede cliques, ele os deriva de uma premissa de CTR por flight.
Este script mede a dispersao dessa premissa e a concentracao do denominador,
para separar falha de entrega de premissa de planejamento.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, ".claude/skills/analise-de-dados/scripts")

from base import Base, carregar, entregas_atribuidas, pacing  # noqa: E402
from numeros import registrar  # noqa: E402

ESTE = __file__


def cliques(base: Base) -> None:
    plano = base.planejado.copy()
    ctr = plano["Soma de Cliques"] / plano["Soma de Impressoes"].replace(0, float("nan"))
    ctr = ctr.dropna() * 100
    registrar(
        "ctr.plano_mediana",
        float(ctr.median()),
        "CTR mediano assumido pelo plano, cliques sobre impressoes de cada flight",
        linhas=len(ctr),
        script=ESTE,
        unidade="%",
    )
    registrar(
        "ctr.plano_maximo",
        float(ctr.max()),
        "Maior CTR assumido por um flight do plano",
        linhas=len(ctr),
        script=ESTE,
        unidade="%",
    )
    registrar(
        "ctr.plano_minimo",
        float(ctr.min()),
        "Menor CTR assumido por um flight do plano",
        linhas=len(ctr),
        script=ESTE,
        unidade="%",
    )
    registrar(
        "ctr.flights_com_premissa",
        len(ctr),
        "Flights com premissa de CTR calculavel, isto e, com impressoes planejadas",
        linhas=len(plano),
        script=ESTE,
    )

    maior = plano.nlargest(1, "Soma de Cliques").iloc[0]
    registrar(
        "cliques.concentracao_maior_flight_pct",
        float(maior["Soma de Cliques"]) / float(plano["Soma de Cliques"].sum()) * 100,
        f"Participacao do maior flight ({maior['Campanha']} em {maior['Veiculo']}) "
        "no total de cliques planejados",
        linhas=len(plano),
        script=ESTE,
        unidade="%",
    )

    atrib = entregas_atribuidas(base)
    ctr_real = pacing(float(atrib["Soma de Cliques"].sum()), float(atrib["Soma de Impressoes"].sum()))
    assert ctr_real is not None
    registrar(
        "ctr.realizado",
        ctr_real * 100,
        "CTR efetivo da entrega que caiu dentro do plano",
        linhas=len(atrib),
        script=ESTE,
        unidade="%",
    )

    # Pacing de cliques excluindo o flight que domina o denominador.
    sem_maior = plano[plano["flight_id"] != maior["flight_id"]]
    chaves = set(zip(sem_maior["Campanha"], sem_maior["Veiculo"]))
    atrib_sem = atrib[[(c, v) in chaves for c, v in zip(atrib["Campanha"], atrib["Veiculo"])]]
    razao = pacing(float(atrib_sem["Soma de Cliques"].sum()), float(sem_maior["Soma de Cliques"].sum()))
    assert razao is not None
    registrar(
        "cliques.pacing_sem_maior_flight",
        razao * 100,
        "Pacing de cliques desconsiderando o flight de premissa de CTR atipica",
        linhas=len(atrib_sem),
        script=ESTE,
        unidade="%",
    )


if __name__ == "__main__":
    cliques(carregar())
    print("cliques registrados")
