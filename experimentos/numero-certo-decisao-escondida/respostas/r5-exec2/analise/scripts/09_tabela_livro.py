"""Passo 10. Registra no livro cada valor exibido na tabela de detalhe.

Numero exibido e numero citado: cada celula da tabela do dashboard precisa do
script que a reproduz, do mesmo jeito que um numero de paragrafo. A fonte e
pacing_campanha_veiculo.csv, gerado por 03_pacing.py.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, ".claude/skills/analise-de-dados/scripts")

from numeros import registrar  # noqa: E402

ESTE = __file__


def slug(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", sem_acento.lower()).strip("_")


def registrar_tabela() -> int:
    pares = pd.read_csv("analise/pacing_campanha_veiculo.csv")
    total = 0
    for _, f in pares.iterrows():
        chave = f"tabela.{slug(f['Campanha'])}__{slug(f['Veiculo'])}"
        rotulo = f"{f['Campanha']} em {f['Veiculo']}"
        dias = int(f["dias_entregues"])
        if f["investimento_nulo"] == 0:
            registrar(
                f"{chave}.plan_investimento",
                float(f["plan_investimento"]),
                f"Investimento planejado em {rotulo}, somando {int(f['flights'])} flight(s)",
                linhas=int(f["flights"]),
                script=ESTE,
                unidade="R$",
            )
            total += 1
        registrar(
            f"{chave}.real_investimento",
            float(f["real_investimento"]),
            f"Investimento entregue na janela em {rotulo}",
            linhas=dias,
            script=ESTE,
            unidade="R$",
        )
        registrar(
            f"{chave}.dias_entregues",
            dias,
            f"Dias de entrega dentro da janela em {rotulo}",
            linhas=dias,
            script=ESTE,
        )
        total += 2
        for metrica in ("investimento", "impressoes"):
            valor = f[f"pacing_{metrica}"]
            if pd.isna(valor):
                continue
            registrar(
                f"{chave}.pacing_{metrica}",
                float(valor) * 100,
                f"Pacing de {metrica} em {rotulo}",
                linhas=dias,
                script=ESTE,
                unidade="%",
            )
            total += 1
    return total


if __name__ == "__main__":
    print(f"{registrar_tabela()} valores da tabela registrados")
