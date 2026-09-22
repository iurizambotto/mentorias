"""Passo 1. Quantas linhas entram de cada lado da conta de pacing e por que
as demais ficam de fora."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, ".claude/skills/analise-de-dados/scripts")

from base import Base, carregar, entregas_atribuidas  # noqa: E402
from numeros import registrar  # noqa: E402

ESTE = __file__


def escopo(base: Base) -> None:
    registrar(
        "linhas.arquivo",
        len(base.bruto),
        "Linhas do arquivo, somando as duas tabelas empilhadas",
        linhas=len(base.bruto),
        script=ESTE,
    )
    registrar(
        "linhas.planejado",
        len(base.planejado),
        "Linhas de Planejado, uma por flight",
        linhas=len(base.planejado),
        script=ESTE,
    )
    registrar(
        "linhas.realizado",
        len(base.realizado),
        "Linhas de Realizado, uma por dia de entrega de campanha em veiculo",
        linhas=len(base.realizado),
        script=ESTE,
    )

    atribuidas = entregas_atribuidas(base)
    registrar(
        "linhas.realizado_no_plano",
        len(atribuidas),
        "Linhas de Realizado que entram no pacing: campanha e veiculo do plano, "
        "data dentro da janela do flight, contadas uma unica vez",
        linhas=len(atribuidas),
        script=ESTE,
        decisoes=["deduplicacao por entrega_id em flights sobrepostos"],
    )
    fora = len(base.realizado) - len(atribuidas)
    registrar(
        "linhas.realizado_fora",
        fora,
        "Linhas de Realizado que ficam fora do pacing",
        linhas=fora,
        script=ESTE,
    )

    # Decomposicao do que fica de fora, em tres motivos mutuamente exclusivos.
    planejadas = set(zip(base.planejado["Campanha"], base.planejado["Veiculo"]))
    campanhas_plano = set(base.planejado["Campanha"])
    realizado = base.realizado.copy()
    realizado["campanha_no_plano"] = realizado["Campanha"].isin(campanhas_plano)
    realizado["par_no_plano"] = [
        (c, v) in planejadas for c, v in zip(realizado["Campanha"], realizado["Veiculo"])
    ]
    atribuidos = set(atribuidas["entrega_id"])

    sem_campanha = realizado[~realizado["campanha_no_plano"]]
    registrar(
        "fora.campanha_sem_plano",
        len(sem_campanha),
        "Linhas de Realizado de campanha que nao tem nenhuma linha de Planejado",
        linhas=len(sem_campanha),
        script=ESTE,
    )
    registrar(
        "fora.campanha_sem_plano_investimento",
        float(sem_campanha["Soma de Investimento"].sum()),
        "Investimento das entregas de campanha sem plano",
        linhas=len(sem_campanha),
        script=ESTE,
        unidade="R$",
    )
    registrar(
        "fora.campanhas_sem_plano_distintas",
        sem_campanha["Campanha"].nunique(),
        "Campanhas distintas que rodaram sem estar no plano",
        linhas=len(sem_campanha),
        script=ESTE,
    )

    veiculo_fora = realizado[realizado["campanha_no_plano"] & ~realizado["par_no_plano"]]
    registrar(
        "fora.veiculo_sem_plano",
        len(veiculo_fora),
        "Linhas de Realizado de campanha planejada, mas em veiculo que aquela campanha "
        "nao tinha no plano",
        linhas=len(veiculo_fora),
        script=ESTE,
    )
    registrar(
        "fora.veiculo_sem_plano_investimento",
        float(veiculo_fora["Soma de Investimento"].sum()),
        "Investimento das entregas em veiculo fora do plano da campanha",
        linhas=len(veiculo_fora),
        script=ESTE,
        unidade="R$",
    )

    janela_fora = realizado[
        realizado["par_no_plano"] & ~realizado["entrega_id"].isin(atribuidos)
    ]
    registrar(
        "fora.janela",
        len(janela_fora),
        "Linhas de Realizado com campanha e veiculo do plano, mas data fora de "
        "qualquer janela de flight",
        linhas=len(janela_fora),
        script=ESTE,
    )
    registrar(
        "fora.janela_investimento",
        float(janela_fora["Soma de Investimento"].sum()),
        "Investimento das entregas fora da janela dos flights",
        linhas=len(janela_fora),
        script=ESTE,
        unidade="R$",
    )

    soma = len(sem_campanha) + len(veiculo_fora) + len(janela_fora)
    assert soma == fora, f"decomposicao do fora nao fecha: {soma} != {fora}"
    assert len(base.planejado) + len(base.realizado) == len(base.bruto)

    registrar(
        "plano.campanhas",
        base.planejado["Campanha"].nunique(),
        "Campanhas distintas no plano",
        linhas=len(base.planejado),
        script=ESTE,
    )
    registrar(
        "realizado.campanhas",
        base.realizado["Campanha"].nunique(),
        "Campanhas distintas com entrega registrada",
        linhas=len(base.realizado),
        script=ESTE,
    )


if __name__ == "__main__":
    escopo(carregar())
    print("escopo registrado")
