"""Passo 9: pacote para reconstruir o painel no Power BI.

Exporta as tabelas ja limpas, um grao por arquivo, e escreve modelo.md com os
relacionamentos e as medidas em DAX.

A deduplicacao e resolvida aqui, e nao no Power BI: cada linha de fato_realizado
sai com no maximo um id_bloco. Assim nenhuma medida escrita no Desktop consegue
contar a mesma entrega em dois flights.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, ".claude/skills/analise-de-dados/scripts")

from base import CHAVE, METRICAS, carregar, casar, componentes_de_flight
from numeros import carregar as carregar_livro
from numeros import registrar

PASTA = Path("entregas/powerbi")
RENOMEAR = {
    "Soma de Investimento": "investimento",
    "Soma de Impressoes": "impressoes",
    "Soma de Cliques": "cliques",
    "Campanha": "campanha",
    "Veiculo": "veiculo",
    "Data": "data",
}


def main() -> int:
    PASTA.mkdir(parents=True, exist_ok=True)
    dados = carregar()
    plan, real = dados.planejado, dados.realizado
    blocos = componentes_de_flight(plan).reset_index(names="id_bloco")
    pares = casar(real, blocos)

    # --- dim_bloco: o grao do plano depois de unir flights sobrepostos
    dim_bloco = blocos.rename(columns=RENOMEAR).copy()
    dim_bloco["ids_flight"] = dim_bloco["ids_flight"].map(lambda ids: ";".join(str(i) for i in ids))
    dim_bloco = dim_bloco.rename(columns={
        "plan_Soma de Investimento": "plan_investimento",
        "plan_Soma de Impressoes": "plan_impressoes",
        "plan_Soma de Cliques": "plan_cliques",
    })
    dim_bloco["inicio"] = dim_bloco["inicio"].dt.strftime("%Y-%m-%d")
    dim_bloco["termino"] = dim_bloco["termino"].dt.strftime("%Y-%m-%d")
    dim_bloco["tem_meta"] = dim_bloco["plan_impressoes"].notna() & (dim_bloco["plan_impressoes"] != 0)
    dim_bloco.to_csv(PASTA / "dim_bloco.csv", index=False, encoding="utf-8")

    # --- fato_planejado: o flight original, preservado para auditoria
    fato_plan = plan.rename(columns=RENOMEAR)[
        ["id_flight", "campanha", "veiculo", "investimento", "impressoes", "cliques"]
    ].copy()
    janelas = plan[["id_flight", "Data de Inicio", "Data de Termino", "Soma de Dias_Veiculacao"]].rename(
        columns={"Data de Inicio": "inicio", "Data de Termino": "termino", "Soma de Dias_Veiculacao": "dias_veiculacao"}
    )
    fato_plan = fato_plan.merge(janelas, on="id_flight")
    mapa_bloco = {
        int(f): int(b) for b, ids in zip(blocos["id_bloco"], blocos["ids_flight"]) for f in ids
    }
    fato_plan["id_bloco"] = fato_plan["id_flight"].map(mapa_bloco)
    fato_plan["inicio"] = fato_plan["inicio"].dt.strftime("%Y-%m-%d")
    fato_plan["termino"] = fato_plan["termino"].dt.strftime("%Y-%m-%d")
    fato_plan.to_csv(PASTA / "fato_planejado.csv", index=False, encoding="utf-8")

    # --- fato_realizado: uma linha por dia de entrega, com no maximo um bloco
    atribuicao = pares.set_index("id_realizado")["id_bloco"]
    assert atribuicao.index.is_unique, "uma linha de realizado casou com mais de um bloco"
    fato_real = real.rename(columns=RENOMEAR)[
        ["id_realizado", "campanha", "veiculo", "data", "investimento", "impressoes", "cliques"]
    ].copy()
    fato_real["id_bloco"] = fato_real["id_realizado"].map(atribuicao).astype("Int64")
    fato_real["no_pacing"] = fato_real["id_bloco"].notna()
    fato_real["data"] = fato_real["data"].dt.strftime("%Y-%m-%d")
    fato_real.to_csv(PASTA / "fato_realizado.csv", index=False, encoding="utf-8")

    # --- dimensoes
    pd.DataFrame({"campanha": sorted(set(real["Campanha"]) | set(plan["Campanha"]))}).assign(
        tem_plano=lambda d: d["campanha"].isin(set(plan["Campanha"]))
    ).to_csv(PASTA / "dim_campanha.csv", index=False, encoding="utf-8")
    pd.DataFrame({"veiculo": sorted(set(real["Veiculo"]) | set(plan["Veiculo"]))}).to_csv(
        PASTA / "dim_veiculo.csv", index=False, encoding="utf-8"
    )

    calendario = pd.DataFrame({"data": pd.date_range(real["Data"].min(), real["Data"].max(), freq="D")})
    calendario["ano"] = calendario["data"].dt.year
    calendario["mes"] = calendario["data"].dt.month
    calendario["ano_mes"] = calendario["data"].dt.strftime("%Y-%m")
    calendario["no_periodo_do_plano"] = (
        (calendario["data"] >= plan["Data de Inicio"].min()) & (calendario["data"] <= plan["Data de Termino"].max())
    )
    calendario["data"] = calendario["data"].dt.strftime("%Y-%m-%d")
    calendario.to_csv(PASTA / "dim_calendario.csv", index=False, encoding="utf-8")

    conferir_pacote(fato_real, dim_bloco, carregar_livro())

    registrar("dim_calendario.dias", len(calendario),
              "Dias na tabela de calendario, do primeiro ao ultimo dia de entrega",
              linhas=len(calendario), script=__file__)
    # o 1000 do CPM aparece literal nas formulas DAX; fica no livro para que o
    # conferidor nao precise abrir excecao para numero dentro de bloco de codigo
    registrar("constante.mil", 1000, "Divisor do CPM, o custo por mil impressoes",
              linhas=0, script=__file__)

    (PASTA / "modelo.md").write_text(modelo(carregar_livro(), len(fato_real), len(fato_plan), len(dim_bloco),
                                            len(calendario)), encoding="utf-8")
    for arquivo in sorted(PASTA.iterdir()):
        print(f"  {arquivo.name:24s} {arquivo.stat().st_size / 1024:8.1f} KB")
    return 0


def conferir_pacote(fato_real: pd.DataFrame, dim_bloco: pd.DataFrame, livro: dict) -> None:
    """Refaz o pacing usando so o que esta nos CSV exportados.

    Roda a mesma logica que as medidas em DAX vao rodar. Se o pacote nao reproduzir
    o livro, o erro estoura aqui e nao no Power BI de outra pessoa.
    """
    blocos_com_meta = set(dim_bloco.loc[dim_bloco["tem_meta"], "id_bloco"])
    entrega = fato_real[fato_real["no_pacing"] & fato_real["id_bloco"].isin(blocos_com_meta)]
    plano = dim_bloco[dim_bloco["tem_meta"]]
    for coluna, curto in [("investimento", "investimento"), ("impressoes", "impressoes"), ("cliques", "cliques")]:
        obtido = entrega[coluna].sum() / plano[f"plan_{coluna}"].sum()
        esperado = livro[f"pacing.{curto}"]["valor"]
        assert abs(obtido - esperado) < 1e-6, (
            f"o pacote nao reproduz o livro em {curto}: {obtido:.6f} != {esperado:.6f}"
        )
    print("pacote reproduz o livro: ok")


def modelo(livro: dict, n_real: int, n_plan: int, n_bloco: int, n_cal: int) -> str:
    v = {chave: item["valor"] for chave, item in livro.items()}

    def p(chave: str) -> str:
        return f"{v[chave] * 100:.2f}%".replace(".", ",")

    def r(chave: str) -> str:
        return "R$ " + f"{v[chave]:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def n(chave: str) -> str:
        return f"{v[chave]:,.0f}".replace(",", ".")

    return f"""# Modelo para Power BI: pacing de campanhas

Pacote gerado por `analise/scripts/09_powerbi.py`. Todos os CSV sao UTF-8, separador
virgula, decimal ponto, datas em `YYYY-MM-DD`.

> **As medidas abaixo nao foram executadas no Power BI Desktop.** O valor esperado ao lado
> de cada uma vem de `analise/numeros.json`, calculado em Python. Use-o para conferir a
> medida depois de escreve-la: se o cartao no Desktop mostrar outro numero, a medida esta
> diferente da analise, nao o contrario.

## A decisao que ja vem resolvida no pacote

O plano tem flights sobrepostos: mesma campanha, mesmo veiculo, janelas que se cruzam.
{n('real.linhas_em_multiplos_flights')} linhas de entrega caem dentro de mais de um flight, uma delas
dentro de {n('real.max_flights_por_linha')} ao mesmo tempo.

Se o modelo relacionasse `fato_realizado` direto a `fato_planejado` por campanha, veiculo e
janela, essas linhas seriam somadas uma vez para cada flight, e o pacing de impressoes daria
{p('alt.pacing_sem_dedup_impressoes')} em vez de {p('pacing.impressoes')}, ou seja
{p('alt.inflacao_sem_dedup_impressoes')} a mais de entrega que nunca existiu.

Por isso o pacote nao entrega esse relacionamento. Flights sobrepostos ja vem unidos em
`dim_bloco`, e cada linha de `fato_realizado` ja chega com **no maximo um** `id_bloco`. A
contagem unica e garantida pelo modelo, nao por uma medida que alguem precise lembrar de
escrever certo.

**Nao crie** um relacionamento entre `fato_realizado` e `fato_planejado`. Use `dim_bloco`.

## Tabelas

| Tabela | Grao | Linhas |
|---|---|---|
| `fato_realizado.csv` | uma entrega diaria: campanha x veiculo x data | {n_real} |
| `fato_planejado.csv` | um flight: campanha x veiculo x janela | {n_plan} |
| `dim_bloco.csv` | um bloco de plano: flights sobrepostos ja unidos | {n_bloco} |
| `dim_campanha.csv` | uma campanha | 185 |
| `dim_veiculo.csv` | um veiculo | 3 |
| `dim_calendario.csv` | um dia | {n_cal} |

### Colunas que merecem atencao

- `fato_realizado[id_bloco]`: vazio quando a entrega nao pertence a nenhum plano. Sao
  {n('real.linhas_fora')} das {n('real.linhas')} linhas.
- `fato_realizado[no_pacing]`: booleano, o mesmo filtro em forma pronta.
- `dim_bloco[tem_meta]`: falso quando o plano daquele bloco tem impressoes zeradas e
  investimento em branco. E {n('plan.flights_sem_denominador')} flights, num bloco so.
  Todo denominador precisa deste filtro, senao a medida divide por zero.
- `dim_bloco[n_flights]`: quantos flights o bloco uniu. Maior que 1 em
  {n('plan.blocos')} menos os blocos simples, ou seja 3 blocos.
- `fato_planejado[id_bloco]`: liga o flight original ao bloco, so para auditoria.

## Relacionamentos

| De | Para | Cardinalidade | Direcao | Ativo |
|---|---|---|---|---|
| `fato_realizado[id_bloco]` | `dim_bloco[id_bloco]` | muitos para um | simples | sim |
| `fato_realizado[data]` | `dim_calendario[data]` | muitos para um | simples | sim |
| `fato_realizado[campanha]` | `dim_campanha[campanha]` | muitos para um | simples | sim |
| `fato_realizado[veiculo]` | `dim_veiculo[veiculo]` | muitos para um | simples | sim |
| `fato_planejado[id_bloco]` | `dim_bloco[id_bloco]` | muitos para um | simples | sim |

`dim_campanha` e `dim_veiculo` filtram o realizado inteiro, inclusive o que esta fora do
plano. Para o painel de pacing, filtre sempre por `dim_bloco`, que so alcanca o que tem plano.

Marque `dim_calendario` como tabela de datas, coluna `data`.

## Medidas em DAX

### Base

O filtro `dim_bloco[tem_meta]` aparece tambem nas medidas de realizado, e nao so nas de
planejado. Sem ele, a entrega do bloco sem meta entra no numerador enquanto o denominador
dele fica de fora, e o pacing de impressoes sobe de {p('pacing.impressoes')} para
{p('alt.denominador_zero_incluido_impressoes')}. Numerador e denominador precisam cobrir os
mesmos blocos.

```dax
Investimento Realizado =
CALCULATE (
    SUM ( fato_realizado[investimento] ),
    fato_realizado[no_pacing] = TRUE (),
    dim_bloco[tem_meta] = TRUE ()
)
```
Esperado: {r('real.total_investimento')}

```dax
Impressoes Realizadas =
CALCULATE (
    SUM ( fato_realizado[impressoes] ),
    fato_realizado[no_pacing] = TRUE (),
    dim_bloco[tem_meta] = TRUE ()
)
```
Esperado: {n('real.total_impressoes')}

```dax
Cliques Realizados =
CALCULATE (
    SUM ( fato_realizado[cliques] ),
    fato_realizado[no_pacing] = TRUE (),
    dim_bloco[tem_meta] = TRUE ()
)
```
Esperado: {n('real.total_cliques')}

```dax
Investimento Planejado =
CALCULATE ( SUM ( dim_bloco[plan_investimento] ), dim_bloco[tem_meta] = TRUE () )
```
Esperado: {r('plan.total_investimento')}

```dax
Impressoes Planejadas =
CALCULATE ( SUM ( dim_bloco[plan_impressoes] ), dim_bloco[tem_meta] = TRUE () )
```
Esperado: {n('plan.total_impressoes')}

```dax
Cliques Planejados =
CALCULATE ( SUM ( dim_bloco[plan_cliques] ), dim_bloco[tem_meta] = TRUE () )
```
Esperado: {n('plan.total_cliques')}

### Pacing

`DIVIDE` sem terceiro argumento devolve vazio quando o denominador e zero, que e o
comportamento desejado: o visual mostra branco, e nao um zero que parece resultado.

```dax
Pacing Investimento = DIVIDE ( [Investimento Realizado], [Investimento Planejado] )
```
Esperado: {p('pacing.investimento')}

```dax
Pacing Impressoes = DIVIDE ( [Impressoes Realizadas], [Impressoes Planejadas] )
```
Esperado: {p('pacing.impressoes')}

```dax
Pacing Cliques = DIVIDE ( [Cliques Realizados], [Cliques Planejados] )
```
Esperado: {p('pacing.cliques')}

### Eficiencia

```dax
CPM Realizado = DIVIDE ( [Investimento Realizado], [Impressoes Realizadas] ) * 1000
```
Esperado: {r('real.cpm')}

```dax
CPM Planejado = DIVIDE ( [Investimento Planejado], [Impressoes Planejadas] ) * 1000
```
Esperado: {r('plan.cpm')}

```dax
CTR Realizado = DIVIDE ( [Cliques Realizados], [Impressoes Realizadas] )
```
Esperado: {p('real.ctr')}

```dax
CTR Planejado = DIVIDE ( [Cliques Planejados], [Impressoes Planejadas] )
```
Esperado: {p('plan.ctr')}

### Cobertura, para o cartao de contexto

`REMOVEFILTERS` aqui e proposital: este cartao mede o arquivo inteiro, inclusive a entrega
sem plano, e nao deve encolher quando o usuario filtra um bloco.

```dax
Investimento Total do Arquivo =
CALCULATE ( SUM ( fato_realizado[investimento] ), REMOVEFILTERS () )
```
Esperado: {r('real.investimento_total_arquivo')}

```dax
Cobertura do Plano =
DIVIDE ( [Investimento Realizado], [Investimento Total do Arquivo] )
```
Esperado: {p('real.share_investimento_no_pacing')}

```dax
Linhas Fora do Pacing =
CALCULATE (
    COUNTROWS ( fato_realizado ),
    fato_realizado[no_pacing] = FALSE (),
    REMOVEFILTERS ( dim_bloco )
)
```
Esperado: {n('real.linhas_fora')}

Essas linhas tem `id_bloco` vazio, entao qualquer filtro vindo de `dim_bloco` as zeraria.
`REMOVEFILTERS ( dim_bloco )` mantem o cartao legivel mesmo com um bloco selecionado.

## Conferencia depois de montar

Coloque os tres pacings em cartoes, sem nenhum filtro aplicado. Se aparecerem
{p('pacing.investimento')}, {p('pacing.impressoes')} e {p('pacing.cliques')}, o modelo esta
igual a analise. Se o pacing de impressoes vier perto de {p('alt.pacing_sem_dedup_impressoes')},
alguem criou o relacionamento direto entre realizado e planejado, e a mesma entrega esta sendo
contada em mais de um flight.
"""


if __name__ == "__main__":
    raise SystemExit(main())
