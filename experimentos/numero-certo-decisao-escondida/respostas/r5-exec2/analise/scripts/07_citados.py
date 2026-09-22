"""Passo 8. Registra os valores de campanhas e casos citados nominalmente nos
entregaveis, para que nenhum numero do texto, do painel ou do slide fique sem
script que o reproduza."""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, ".claude/skills/analise-de-dados/scripts")

from base import Base, carregar, entregas_atribuidas  # noqa: E402
from numeros import registrar  # noqa: E402

ESTE = __file__
CITADAS = [
    "Maceio", "Freeshop", "Impulsionamentos", "Fortaleza", "Uberlandia",
    "Feira de Santana", "Inauguracao", "Mega Day", "Cashback",
    "Joao Pessoa - Não Pulavel",
]


def slug(nome: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", sem_acento.lower()).strip("_")


def citados(base: Base) -> None:
    campanha = pd.read_csv("analise/pacing_campanha.csv")
    for nome in CITADAS:
        linha = campanha[campanha["Campanha"] == nome]
        assert len(linha) == 1, f"campanha citada nao encontrada no pacing: {nome}"
        linha = linha.iloc[0]
        chave = slug(nome)
        registrar(
            f"camp.{chave}.plan_investimento",
            float(linha["plan_investimento"]),
            f"Investimento planejado na campanha {nome}",
            linhas=int(linha["flights"]),
            script=ESTE,
            unidade="R$",
        )
        registrar(
            f"camp.{chave}.real_investimento",
            float(linha["real_investimento"]),
            f"Investimento entregue na janela na campanha {nome}",
            linhas=int(linha["dias_entregues"]),
            script=ESTE,
            unidade="R$",
        )
        registrar(
            f"camp.{chave}.real_impressoes",
            float(linha["real_impressoes"]),
            f"Impressoes entregues na janela na campanha {nome}",
            linhas=int(linha["dias_entregues"]),
            script=ESTE,
        )
        for metrica in ("investimento", "impressoes", "cliques"):
            valor = linha[f"pacing_{metrica}"]
            if pd.isna(valor):
                continue
            registrar(
                f"camp.{chave}.pacing_{metrica}",
                float(valor) * 100,
                f"Pacing de {metrica} da campanha {nome}",
                linhas=int(linha["dias_entregues"]),
                script=ESTE,
                unidade="%",
            )

    # O caso sem denominador, citado nominalmente no documento.
    atrib = entregas_atribuidas(base)
    sem_plano = atrib[atrib["Campanha"] == "Joao Pessoa - Não Pulavel"]
    registrar(
        "sem_denominador.dias_entregues",
        len(sem_plano),
        "Dias de entrega da campanha planejada sem nenhum valor orcado",
        linhas=len(sem_plano),
        script=ESTE,
    )

    livro = __import__("json").loads(Path("analise/numeros.json").read_text(encoding="utf-8"))
    registrar(
        "total.excedente_impressoes_pct",
        livro["total.pacing_impressoes"]["valor"] - 100,
        "Quanto a entrega de impressoes superou o plano, em pontos percentuais",
        linhas=livro["total.pacing_impressoes"]["linhas"],
        script=ESTE,
        unidade="%",
    )
    registrar(
        "total.share_fora_do_plano_pct",
        100 - livro["reconciliacao.share_dentro_do_plano_pct"]["valor"],
        "Percentual do investimento realizado que nao cai em nenhum flight do plano",
        linhas=len(base.realizado),
        script=ESTE,
        unidade="%",
    )
    for limite, nome in ((80, "inferior"), (120, "superior")):
        registrar(
            f"faixa.limite_{nome}_pct",
            limite,
            f"Limite {nome} da faixa de pacing considerada dentro do esperado",
            linhas=len(campanha),
            script=ESTE,
            unidade="%",
        )

    # Concentracao do plano, usada no slide de qualidade da base.
    plano_camp = campanha.nlargest(5, "plan_investimento")["plan_investimento"].sum()
    registrar(
        "plano.top5_share_pct",
        plano_camp / campanha["plan_investimento"].sum() * 100,
        "Participacao das cinco maiores campanhas no investimento planejado",
        linhas=len(campanha),
        script=ESTE,
        unidade="%",
    )
    registrar(
        "plano.dias_cobertos",
        int((base.planejado["Data de Termino"].max() - base.planejado["Data de Inicio"].min()).days) + 1,
        "Dias corridos entre o inicio do primeiro flight e o fim do ultimo",
        linhas=len(base.planejado),
        script=ESTE,
    )


if __name__ == "__main__":
    citados(carregar())
    print("citados registrados")
