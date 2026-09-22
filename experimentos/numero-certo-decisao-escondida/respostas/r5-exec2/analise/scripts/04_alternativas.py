"""Passo 5. Roda as alternativas de cada decisao que muda um numero.

Cada funcao devolve o pacing de investimento e de impressoes sob uma regra
diferente, para que decisoes.md compare o resultado escolhido com o da
alternativa em vez de apenas afirmar a escolha.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, ".claude/skills/analise-de-dados/scripts")

from base import CHAVE, Base, carregar, entregas_atribuidas, malha, pacing  # noqa: E402
from numeros import registrar  # noqa: E402

ESTE = __file__


def _pacing_global(plano: pd.DataFrame, entregue: pd.DataFrame, metrica: str) -> float:
    """Pacing agregado, ignorando pares cujo denominador e zero ou nulo."""
    p = plano.groupby(CHAVE)[metrica].sum()
    r = entregue.groupby(CHAVE)[metrica].sum().reindex(p.index).fillna(0)
    validos = p[(p > 0) & p.notna()].index
    razao = pacing(float(r.loc[validos].sum()), float(p.loc[validos].sum()))
    assert razao is not None
    return razao * 100


def sem_deduplicacao(base: Base) -> tuple[float, float]:
    bruta = malha(base)
    return (
        _pacing_global(base.planejado, bruta, "Soma de Investimento"),
        _pacing_global(base.planejado, bruta, "Soma de Impressoes"),
    )


def janela_fim_exclusivo(base: Base) -> tuple[float, float]:
    entregas = base.realizado.drop(columns=["Data de Inicio", "Data de Termino"])
    cruz = entregas.merge(
        base.planejado[[*CHAVE, "flight_id", "Data de Inicio", "Data de Termino"]],
        on=CHAVE,
        how="inner",
    )
    dentro = (cruz["Data"] >= cruz["Data de Inicio"]) & (cruz["Data"] < cruz["Data de Termino"])
    unica = cruz[dentro].drop_duplicates(subset="entrega_id")
    return (
        _pacing_global(base.planejado, unica, "Soma de Investimento"),
        _pacing_global(base.planejado, unica, "Soma de Impressoes"),
    )


def sem_filtro_de_janela(base: Base) -> tuple[float, float]:
    """Toda entrega da campanha e veiculo conta, mesmo fora da janela."""
    entregas = base.realizado.drop(columns=["Data de Inicio", "Data de Termino"])
    chaves = base.planejado[CHAVE].drop_duplicates()
    unica = entregas.merge(chaves, on=CHAVE, how="inner")
    return (
        _pacing_global(base.planejado, unica, "Soma de Investimento"),
        _pacing_global(base.planejado, unica, "Soma de Impressoes"),
    )


def por_prefixo_de_campanha(base: Base) -> tuple[float, float, int, float]:
    """Trata 'Inauguracao Barra' como entrega da campanha planejada 'Inauguracao'.

    Uma entrega so e reatribuida se o nome do plano for prefixo do nome da
    entrega em limite de palavra, e se aquela campanha nao tiver plano proprio.
    """
    planejadas = sorted(set(base.planejado["Campanha"]), key=len, reverse=True)
    def mapear(nome: str) -> str:
        if nome in planejadas:
            return nome
        for base_nome in planejadas:
            if nome.startswith(base_nome + " "):
                return base_nome
        return nome

    realizado = base.realizado.copy()
    realizado["Campanha"] = [mapear(n) for n in realizado["Campanha"]]
    remapeadas = int((realizado["Campanha"] != base.realizado["Campanha"]).sum())
    alterado = Base(bruto=base.bruto, planejado=base.planejado, realizado=realizado)
    unica = entregas_atribuidas(alterado)
    return (
        _pacing_global(base.planejado, unica, "Soma de Investimento"),
        _pacing_global(base.planejado, unica, "Soma de Impressoes"),
        remapeadas,
        float(unica["Soma de Investimento"].sum()),
    )


def reconciliacao(base: Base) -> None:
    """Passo 4.4. A soma das partes tem de bater com o total."""
    atribuidas = entregas_atribuidas(base)
    total_geral = float(base.realizado["Soma de Investimento"].sum())
    dentro = float(atribuidas["Soma de Investimento"].sum())
    fora_ids = set(base.realizado["entrega_id"]) - set(atribuidas["entrega_id"])
    fora = float(
        base.realizado[base.realizado["entrega_id"].isin(fora_ids)]["Soma de Investimento"].sum()
    )
    assert abs((dentro + fora) - total_geral) < 0.01, "dentro + fora nao reconstroi o total"
    registrar(
        "reconciliacao.investimento_realizado_total",
        total_geral,
        "Investimento de todas as linhas de Realizado do arquivo",
        linhas=len(base.realizado),
        script=ESTE,
        unidade="R$",
    )
    registrar(
        "reconciliacao.share_dentro_do_plano_pct",
        dentro / total_geral * 100,
        "Percentual do investimento realizado que cai dentro de algum flight do plano",
        linhas=len(base.realizado),
        script=ESTE,
        unidade="%",
    )


if __name__ == "__main__":
    base = carregar()
    reconciliacao(base)

    inv, imp = sem_deduplicacao(base)
    registrar(
        "alt.sem_dedup_pacing_investimento",
        inv,
        "Alternativa rejeitada: pacing de investimento contando a entrega uma vez por flight",
        linhas=len(malha(base)),
        script=ESTE,
        unidade="%",
    )
    registrar(
        "alt.sem_dedup_pacing_impressoes",
        imp,
        "Alternativa rejeitada: pacing de impressoes sem deduplicar entregas",
        linhas=len(malha(base)),
        script=ESTE,
        unidade="%",
    )

    inv, imp = janela_fim_exclusivo(base)
    registrar(
        "alt.fim_exclusivo_pacing_investimento",
        inv,
        "Alternativa rejeitada: pacing de investimento com Data de Termino exclusiva",
        linhas=len(base.realizado),
        script=ESTE,
        unidade="%",
    )

    inv, imp = sem_filtro_de_janela(base)
    registrar(
        "alt.sem_janela_pacing_investimento",
        inv,
        "Alternativa rejeitada: pacing de investimento sem exigir que a entrega caia na janela",
        linhas=len(base.realizado),
        script=ESTE,
        unidade="%",
    )
    registrar(
        "alt.sem_janela_pacing_impressoes",
        imp,
        "Alternativa rejeitada: pacing de impressoes sem filtro de janela",
        linhas=len(base.realizado),
        script=ESTE,
        unidade="%",
    )

    inv, imp, remapeadas, valor = por_prefixo_de_campanha(base)
    registrar(
        "alt.prefixo_pacing_investimento",
        inv,
        "Alternativa rejeitada: pacing de investimento agrupando campanhas por prefixo do nome",
        linhas=len(base.realizado),
        script=ESTE,
        unidade="%",
    )
    registrar(
        "alt.prefixo_linhas_remapeadas",
        remapeadas,
        "Linhas de Realizado que mudariam de campanha no agrupamento por prefixo",
        linhas=len(base.realizado),
        script=ESTE,
    )
    print("alternativas registradas")
