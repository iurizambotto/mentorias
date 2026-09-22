"""Passo 11. Pacote para reconstruir o painel no Power BI.

Exporta as tabelas ja limpas, uma por grao, com fatos separados de dimensoes,
e o modelo com relacionamentos e medidas em DAX. A regra que mais erra na
remontagem e a deduplicacao: aqui ela vem resolvida na coluna dentro_do_plano
do fato de entrega, para que somar a coluna nunca conte a mesma entrega duas
vezes, independente do visual que o usuario montar.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))

sys.path.insert(0, ".claude/skills/analise-de-dados/scripts")

from base import carregar, entregas_atribuidas, malha  # noqa: E402
from numeros import registrar  # noqa: E402

DESTINO = Path("entregas/powerbi")
LIVRO = Path("analise/numeros.json")


def br(valor: float, casas: int = 2) -> str:
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def exportar() -> dict[str, int]:
    base = carregar()
    DESTINO.mkdir(parents=True, exist_ok=True)
    atribuidas = set(entregas_atribuidas(base)["entrega_id"])
    contagem: dict[str, int] = {}

    planejado = base.planejado.rename(
        columns={
            "Soma de Investimento": "investimento_planejado",
            "Soma de Impressoes": "impressoes_planejadas",
            "Soma de Cliques": "cliques_planejados",
            "Soma de Dias_Veiculacao": "dias_planejados",
            "Data de Inicio": "data_inicio",
            "Data de Termino": "data_termino",
        }
    )[
        [
            "flight_id", "Campanha", "Veiculo", "Modalidade", "Objetivo", "Publico",
            "data_inicio", "data_termino", "dias_planejados",
            "investimento_planejado", "impressoes_planejadas", "cliques_planejados",
        ]
    ]
    planejado.insert(3, "campanha_veiculo", planejado["Campanha"] + " | " + planejado["Veiculo"])

    realizado = base.realizado.rename(
        columns={
            "Soma de Investimento": "investimento_realizado",
            "Soma de Impressoes": "impressoes_realizadas",
            "Soma de Cliques": "cliques_realizados",
            "Data": "data",
        }
    )[
        [
            "entrega_id", "campaign_name", "Campanha", "Veiculo", "Modalidade",
            "Objetivo", "Publico", "data",
            "investimento_realizado", "impressoes_realizadas", "cliques_realizados",
        ]
    ].copy()
    realizado.insert(4, "campanha_veiculo", realizado["Campanha"] + " | " + realizado["Veiculo"])
    # Deduplicacao resolvida na origem: a coluna e por entrega, nunca por par
    # flight x entrega, entao somar nunca conta a mesma entrega duas vezes.
    realizado["dentro_do_plano"] = realizado["entrega_id"].isin(atribuidas)
    planejadas_camp = set(base.planejado["Campanha"])
    pares = set(zip(base.planejado["Campanha"], base.planejado["Veiculo"]))
    realizado["motivo_fora"] = [
        "dentro do plano"
        if dentro
        else (
            "campanha sem plano"
            if camp not in planejadas_camp
            else ("veiculo fora do plano da campanha" if (camp, vei) not in pares else "data fora da janela")
        )
        for dentro, camp, vei in zip(
            realizado["dentro_do_plano"], realizado["Campanha"], realizado["Veiculo"]
        )
    ]

    # Ponte flight x entrega, so para quem quiser olhar o detalhe de flight.
    # NAO deve ser usada para somar entrega: ela repete a entrega compartilhada.
    ponte = malha(base)[["flight_id", "entrega_id"]].copy()
    ocorrencias = ponte["entrega_id"].value_counts()
    ponte["entrega_compartilhada"] = ponte["entrega_id"].map(ocorrencias) > 1
    ponte["flights_que_reivindicam"] = ponte["entrega_id"].map(ocorrencias)

    dim_campanha = (
        pd.concat([base.planejado["Campanha"], base.realizado["Campanha"]])
        .drop_duplicates()
        .sort_values()
        .to_frame("Campanha")
    )
    dim_campanha["tem_plano"] = dim_campanha["Campanha"].isin(planejadas_camp)
    dim_veiculo = (
        pd.concat([base.planejado["Veiculo"], base.realizado["Veiculo"]])
        .drop_duplicates()
        .sort_values()
        .to_frame("Veiculo")
    )
    datas = pd.date_range(
        base.realizado["Data"].min(), base.realizado["Data"].max(), freq="D"
    )
    calendario = pd.DataFrame({"data": datas})
    calendario["ano"] = calendario["data"].dt.year
    calendario["mes"] = calendario["data"].dt.month
    calendario["ano_mes"] = calendario["data"].dt.to_period("M").astype(str)
    calendario["dentro_do_periodo_do_plano"] = (
        calendario["data"] >= base.planejado["Data de Inicio"].min()
    ) & (calendario["data"] <= base.planejado["Data de Termino"].max())

    registrar(
        "powerbi.dias_calendario",
        len(calendario),
        "Dias do calendario continuo exportado para o Power BI, do primeiro ao ultimo "
        "dia de entrega registrado",
        linhas=len(calendario),
        script=__file__,
    )

    tabelas = {
        "fato_planejado": planejado,
        "fato_realizado": realizado,
        "ponte_flight_entrega": ponte,
        "dim_campanha": dim_campanha,
        "dim_veiculo": dim_veiculo,
        "dim_calendario": calendario,
        "resumo_campanha_veiculo": pd.read_csv("analise/pacing_campanha_veiculo.csv"),
        "resumo_flight": pd.read_csv("analise/flights_detalhe.csv"),
    }
    for nome, tabela in tabelas.items():
        caminho = DESTINO / f"{nome}.csv"
        tabela.to_csv(caminho, index=False, encoding="utf-8")
        contagem[nome] = len(tabela)
    return contagem


def modelo(contagem: dict[str, int]) -> str:
    L = json.loads(LIVRO.read_text(encoding="utf-8"))

    def v(chave: str, casas: int = 2) -> str:
        return br(L[chave]["valor"], casas)

    def linhas_de(chave: str) -> str:
        return br(L[chave]["linhas"], 0)

    linhas_tabelas = "\n".join(
        f"| `{nome}.csv` | {br(n, 0)} | {descricao} |"
        for nome, n, descricao in [
            ("fato_planejado", contagem["fato_planejado"], "Um flight por linha. Grão: campanha × veículo × janela"),
            ("fato_realizado", contagem["fato_realizado"], "Um dia de entrega por linha. Grão: campanha × veículo × dia"),
            ("ponte_flight_entrega", contagem["ponte_flight_entrega"], "Par flight × entrega válido. Repete a entrega compartilhada, ver aviso abaixo"),
            ("dim_campanha", contagem["dim_campanha"], "Campanhas, com a marca de quem tem plano"),
            ("dim_veiculo", contagem["dim_veiculo"], "Veículos"),
            ("dim_calendario", contagem["dim_calendario"], "Calendário diário contínuo, sem buracos"),
            ("resumo_campanha_veiculo", contagem["resumo_campanha_veiculo"], "Resultado já agregado, para conferir o modelo"),
            ("resumo_flight", contagem["resumo_flight"], "Detalhe por flight, com a marca de entrega disputada"),
        ]
    )

    return f"""# Modelo para o Power BI

Reconstrói no Power BI o mesmo painel de `entregas/dashboard.html`. Os arquivos são CSV UTF-8
com vírgula como separador e ponto como separador decimal, no padrão que o Power BI lê sem
ajuste de locale.

> **As medidas abaixo não foram executadas no Power BI Desktop.** O valor esperado ao lado de
> cada uma vem de `analise/numeros.json`, calculado em Python. Use-o para conferir a medida
> depois de montar: se o cartão não bater com o valor esperado, o erro está no modelo, não no
> dado.

## Tabelas

| Arquivo | Linhas | Grão |
|---|---|---|
{linhas_tabelas}

## Relacionamentos

| De | Para | Cardinalidade | Direção do filtro | Ativo |
|---|---|---|---|---|
| `dim_campanha[Campanha]` | `fato_planejado[Campanha]` | 1 para muitos | única | sim |
| `dim_campanha[Campanha]` | `fato_realizado[Campanha]` | 1 para muitos | única | sim |
| `dim_veiculo[Veiculo]` | `fato_planejado[Veiculo]` | 1 para muitos | única | sim |
| `dim_veiculo[Veiculo]` | `fato_realizado[Veiculo]` | 1 para muitos | única | sim |
| `dim_calendario[data]` | `fato_realizado[data]` | 1 para muitos | única | sim |
| `dim_calendario[data]` | `fato_planejado[data_inicio]` | 1 para muitos | única | **não**, inativo |
| `fato_planejado[flight_id]` | `ponte_flight_entrega[flight_id]` | 1 para muitos | única | sim |
| `fato_realizado[entrega_id]` | `ponte_flight_entrega[entrega_id]` | 1 para muitos | única | sim |

Duas observações que evitam erro de montagem:

1. **O relacionamento do calendário com o plano fica inativo.** Um flight ocupa um intervalo, não
   uma data. Deixá-lo ativo faz o plano ser filtrado pelo primeiro dia da janela e o realizado
   pelo dia da entrega, e o pacing passa a comparar recortes diferentes. Marque `dim_calendario`
   como tabela de datas e ligue o filtro de período apenas ao realizado.
2. **Nunca some entrega passando pela ponte.** `ponte_flight_entrega` tem
   {br(contagem["ponte_flight_entrega"], 0)} linhas para
   {v("linhas.realizado_no_plano", 0)} entregas, porque
   {v("sobreposicao.entregas_em_mais_de_um_flight", 0)} delas são reivindicadas por mais de um
   flight, uma delas por {v("sobreposicao.max_flights_por_entrega", 0)}. Somar por ali infla
   impressões em {v("dupla_contagem.impressoes_inflacao_pct")}%. Use a ponte só para listar o
   detalhe de flight; para qualquer soma, use `fato_realizado[dentro_do_plano]`.

## Medidas em DAX

A deduplicação já está resolvida na coluna `dentro_do_plano`, que é por entrega. Por isso as
medidas de realizado são somas simples com um filtro, e não precisam de `DISTINCT` nem de
`SUMMARIZE`.

```dax
Investimento Planejado =
    SUM ( fato_planejado[investimento_planejado] )

Investimento Realizado =
    CALCULATE (
        SUM ( fato_realizado[investimento_realizado] ),
        fato_realizado[dentro_do_plano] = TRUE ()
    )

Impressoes Planejadas =
    SUM ( fato_planejado[impressoes_planejadas] )

Impressoes Realizadas =
    CALCULATE (
        SUM ( fato_realizado[impressoes_realizadas] ),
        fato_realizado[dentro_do_plano] = TRUE ()
    )

Cliques Planejados =
    SUM ( fato_planejado[cliques_planejados] )

Cliques Realizados =
    CALCULATE (
        SUM ( fato_realizado[cliques_realizados] ),
        fato_realizado[dentro_do_plano] = TRUE ()
    )
```

O `DIVIDE` sem terceiro argumento devolve vazio quando o denominador é zero ou nulo, que é
exatamente o tratamento da análise: ausência de plano aparece como célula vazia, nunca como 0%.
**Não coloque um `0` ali**, senão o par sem orçamento entra no visual como se tivesse
sub-entregado.

```dax
Pacing Investimento =
    DIVIDE ( [Investimento Realizado], [Investimento Planejado] )

Pacing Impressoes =
    DIVIDE ( [Impressoes Realizadas], [Impressoes Planejadas] )

Pacing Cliques =
    DIVIDE ( [Cliques Realizados], [Cliques Planejados] )

Gap Investimento =
    [Investimento Realizado] - [Investimento Planejado]
```

O total geral precisa ignorar os pares sem denominador, senão o realizado deles entra no
numerador do total sem nada no denominador e o índice sobe sem motivo:

```dax
Pacing Investimento Total =
VAR Pares =
    FILTER (
        SUMMARIZE (
            fato_planejado,
            fato_planejado[Campanha],
            fato_planejado[Veiculo],
            "Plano", [Investimento Planejado],
            "Real", [Investimento Realizado]
        ),
        [Plano] > 0
    )
RETURN
    DIVIDE ( SUMX ( Pares, [Real] ), SUMX ( Pares, [Plano] ) )
```

## Valores esperados

Sem nenhum filtro aplicado, com todas as {v("linhas.arquivo", 0)} linhas carregadas:

| Medida | Valor esperado | Base |
|---|---|---|
| Investimento Planejado | R$ {v("total.plan_investimento")} | {v("linhas.planejado", 0)} flights, dos quais os {linhas_de("total.plan_investimento")} pares com denominador válido |
| Investimento Realizado | R$ {v("total.real_investimento")} | {v("linhas.realizado_no_plano", 0)} entregas dentro do plano |
| Pacing Investimento Total | {v("total.pacing_investimento")}% | idem |
| Impressoes Realizadas | {v("total.real_impressoes", 0)} | {v("linhas.realizado_no_plano", 0)} entregas |
| Pacing Impressoes Total | {v("total.pacing_impressoes")}% | idem |
| Pacing Cliques Total | {v("total.pacing_cliques")}% | idem |
| Gap Investimento | R$ {v("total.gap_investimento")} | idem |

Por veículo, com `Pacing Investimento` numa matriz por `dim_veiculo[Veiculo]`:

| Veículo | Valor esperado |
|---|---|
| Meta Ads | {v("veiculo.meta.pacing_investimento")}% |
| Youtube Ads | {v("veiculo.youtube.pacing_investimento")}% |
| Tiktok Ads | {v("veiculo.tiktok.pacing_investimento")}% |

Conferências que pegam erro de modelo cedo:

- `COUNTROWS ( fato_realizado )` = {v("linhas.realizado", 0)}.
- `CALCULATE ( COUNTROWS ( fato_realizado ), fato_realizado[dentro_do_plano] = TRUE () )` =
  {v("linhas.realizado_no_plano", 0)}. Se der
  {br(contagem["ponte_flight_entrega"], 0)}, o visual está passando pela ponte.
- `COUNTROWS ( ponte_flight_entrega )` = {br(contagem["ponte_flight_entrega"], 0)}.
- A matriz por campanha e veículo deve ter uma linha com `Pacing Investimento` vazio, que é
  `Joao Pessoa - Não Pulavel` em Youtube Ads. Se ela aparecer como 0%, o `DIVIDE` recebeu o
  terceiro argumento.
- `resumo_campanha_veiculo.csv` tem o resultado já pronto: compare a matriz contra ele linha a
  linha antes de publicar.

## Filtros que o painel usa

- Período, ligado a `dim_calendario[data]`, com o intervalo do plano de 2024-05-28 a 2024-07-31.
- Veículo, de `dim_veiculo`.
- Campanha, de `dim_campanha`, com `tem_plano` disponível para separar as
  {v("fora.campanhas_sem_plano_distintas", 0)} campanhas que rodaram fora deste plano.
- `fato_realizado[motivo_fora]` explica, linha a linha, por que uma entrega ficou fora do
  pacing: campanha sem plano, veículo fora do plano da campanha ou data fora da janela.
"""


if __name__ == "__main__":
    contagem = exportar()
    (DESTINO / "modelo.md").write_text(modelo(contagem), encoding="utf-8")
    for nome, n in contagem.items():
        print(f"  {nome}.csv: {n} linhas")
    print(f"modelo: {DESTINO / 'modelo.md'}")
