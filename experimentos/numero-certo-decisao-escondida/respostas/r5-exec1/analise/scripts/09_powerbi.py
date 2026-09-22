"""Passo 9: pacote de dados para reconstruir o painel no Power BI.

A regra de deduplicacao nao sobrevive a um relacionamento comum no Power BI:
um join de data entre fato e flight repete a entrega uma vez por flight
sobreposto. Por isso o pacote entrega a marcacao `dentro_do_plano` ja resolvida
na tabela fato e uma tabela agregada por par, e o modelo.md explica por que.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd
from comum import carregar
from numeros import carregar as carregar_livro

RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ.parent / "entregas" / "powerbi"
DESTINO.mkdir(parents=True, exist_ok=True)

livro = carregar_livro()
plan, _ = carregar()
real = pd.read_csv(RAIZ / "realizado_classificado.csv", parse_dates=["Data"])
valido = pd.read_csv(RAIZ / "pacing_valido.csv")
todos_pares = pd.read_csv(RAIZ / "pacing_por_par.csv")


def n(chave: str) -> float:
    return livro[chave]["valor"]


def _br(v: float, casas: int) -> str:
    return f"{v:,.{casas}f}".replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def brl(v: float) -> str:
    return "R$ " + _br(v, 2)


def mil(v: float) -> str:
    """Inteiro com separador de milhar brasileiro, o que o conferidor espera."""
    return _br(v, 0)


# ---- fato: entrega diaria, grao campaign_name + veiculo + data
fato = real[
    ["campaign_name", "Campanha", "Veiculo", "Data", "Modalidade", "Objetivo", "Publico",
     "Soma de Investimento", "Soma de Impressoes", "Soma de Cliques", "motivo"]
].rename(
    columns={
        "campaign_name": "anuncio",
        "Campanha": "campanha",
        "Veiculo": "veiculo",
        "Data": "data",
        "Modalidade": "modalidade",
        "Objetivo": "objetivo",
        "Publico": "publico",
        "Soma de Investimento": "investimento",
        "Soma de Impressoes": "impressoes",
        "Soma de Cliques": "cliques",
    }
)
fato["dentro_do_plano"] = fato["motivo"] == "dentro do plano"
pares_validos = set(zip(valido["Campanha"], valido["Veiculo"]))
fato["par_com_denominador"] = [(c, v) in pares_validos for c, v in zip(fato["campanha"], fato["veiculo"])]
fato["chave_par"] = fato["campanha"] + " | " + fato["veiculo"]
fato.to_csv(DESTINO / "fato_realizado.csv", index=False, encoding="utf-8")

# ---- fato: flights planejados
flights = plan[["Campanha", "Veiculo", "inicio", "fim", "Soma de Dias_Veiculacao",
                "Soma de Investimento", "Soma de Impressoes", "Soma de Cliques",
                "Modalidade", "Objetivo", "Publico", "flight_id"]].rename(
    columns={
        "Campanha": "campanha", "Veiculo": "veiculo",
        "Soma de Dias_Veiculacao": "dias_veiculacao",
        "Soma de Investimento": "investimento_planejado",
        "Soma de Impressoes": "impressoes_planejadas",
        "Soma de Cliques": "cliques_planejados",
        "Modalidade": "modalidade", "Objetivo": "objetivo", "Publico": "publico",
    }
)
flights["chave_par"] = flights["campanha"] + " | " + flights["veiculo"]
flights["denominador_valido"] = flights["chave_par"].isin(
    valido["Campanha"] + " | " + valido["Veiculo"]
)
flights.to_csv(DESTINO / "fato_planejado.csv", index=False, encoding="utf-8")

# ---- agregado por par, com a deduplicacao ja resolvida
par = todos_pares.rename(columns={"Campanha": "campanha", "Veiculo": "veiculo"}).copy()
par["chave_par"] = par["campanha"] + " | " + par["veiculo"]
par["denominador_valido"] = par["chave_par"].isin(valido["Campanha"] + " | " + valido["Veiculo"])
par.to_csv(DESTINO / "fato_pacing_par.csv", index=False, encoding="utf-8")

# ---- dimensoes
dim_camp = (
    pd.concat([fato[["campanha"]], flights[["campanha"]]])
    .drop_duplicates()
    .sort_values("campanha")
)
dim_camp["tem_plano"] = dim_camp["campanha"].isin(set(flights["campanha"]))
dim_camp.to_csv(DESTINO / "dim_campanha.csv", index=False, encoding="utf-8")

pd.DataFrame({"veiculo": sorted(fato["veiculo"].unique())}).to_csv(
    DESTINO / "dim_veiculo.csv", index=False, encoding="utf-8"
)

dim_par = par[["chave_par", "campanha", "veiculo", "denominador_valido"]].copy()
dim_par.to_csv(DESTINO / "dim_par.csv", index=False, encoding="utf-8")

cal = pd.DataFrame({"data": pd.date_range(fato["data"].min(), fato["data"].max(), freq="D")})
cal["ano"] = cal["data"].dt.year
cal["mes"] = cal["data"].dt.month
cal["ano_mes"] = cal["data"].dt.to_period("M").astype(str)
cal["dia_semana"] = cal["data"].dt.day_name(locale="pt_BR.utf8") if hasattr(cal["data"].dt, "day_name") else ""
cal["na_janela_do_plano"] = cal["data"].between(plan["inicio"].min(), plan["fim"].max())
cal.to_csv(DESTINO / "dim_calendario.csv", index=False, encoding="utf-8")

MODELO = f"""# Modelo para Power BI: pacing de campanhas

Pacote gerado por `analise/scripts/09_powerbi.py`. Todos os CSV estão em UTF-8, separador
vírgula, decimal com ponto e data no formato `AAAA-MM-DD`.

> **As medidas DAX abaixo não foram executadas no Power BI Desktop.** O valor esperado ao lado
> de cada uma vem de `analise/numeros.json`, calculado em Python. Use-o para conferir a medida
> depois de montar o modelo: se o cartão não bater com o valor esperado, a medida está errada,
> não o número.

## Antes de tudo: por que a deduplicação já vem pronta

O plano tem {int(n('sobreposicao.grupos'))} pares de campanha e veículo com janelas de flight que
se cruzam ({int(n('sobreposicao.pares_flight'))} pares de flights). Se você relacionar
`fato_realizado` a `fato_planejado` por campanha e veículo e filtrar a data entre início e fim,
o Power BI vai repetir a mesma entrega uma vez por flight que a contém: {int(n('join.linhas_multiplas'))}
linhas cairiam em mais de um flight, uma delas em {int(n('join.max_flights_por_linha'))} flights ao
mesmo tempo. O realizado subiria de {brl(n('dupla.investimento_dedup'))} para
{brl(n('dupla.investimento_ingenuo'))}, e o pacing de investimento de {n('pacing.investimento'):.2f}%
para {n('alt.pacing_sem_dedup'):.2f}%.

Por isso **não existe relacionamento entre `fato_realizado` e `fato_planejado`** neste modelo. A
coluna `dentro_do_plano`, já calculada em Python pela união das janelas de cada par, é o que
resolve a dedup. Respeite isso: qualquer medida que cruze as duas tabelas por data volta a contar
em dobro.

## Tabelas

| Tabela | Grão de uma linha | Linhas | Papel |
|---|---|---|---|
| `fato_realizado.csv` | um anúncio, num veículo, num dia | {mil(len(fato))} | fato da entrega |
| `fato_planejado.csv` | um flight: campanha + veículo + janela | {len(flights)} | fato do plano |
| `fato_pacing_par.csv` | um par campanha + veículo | {len(par)} | agregado já deduplicado |
| `dim_campanha.csv` | uma campanha | {len(dim_camp)} | dimensão |
| `dim_veiculo.csv` | um veículo | 3 | dimensão |
| `dim_par.csv` | um par campanha + veículo com plano | {len(dim_par)} | dimensão-ponte |
| `dim_calendario.csv` | um dia | {mil(len(cal))} | dimensão de tempo |

### Colunas que merecem atenção

- `fato_realizado.motivo`: por que a linha entrou ou não na conta. Valores: `dentro do plano`,
  `campanha fora do plano`, `veiculo nao planejado para a campanha`, `data fora da janela do flight`.
- `fato_realizado.dentro_do_plano`: booleano, o filtro que toda medida de pacing usa.
- `fato_realizado.par_com_denominador`: falso para o par cujo plano é vazio. Ver a seção de
  denominadores.
- `fato_planejado.investimento_planejado`: **nulo em {int(n('zero.flights_investimento_nulo'))} flights.**
  Não substitua por zero; isso criaria uma divisão por zero silenciosa.
- `chave_par`: texto `campanha | veiculo`, a chave dos relacionamentos com `dim_par`.

## Relacionamentos

| De | Para | Cardinalidade | Direção do filtro |
|---|---|---|---|
| `fato_realizado[campanha]` | `dim_campanha[campanha]` | muitos para um | única, da dimensão para o fato |
| `fato_realizado[veiculo]` | `dim_veiculo[veiculo]` | muitos para um | única |
| `fato_realizado[data]` | `dim_calendario[data]` | muitos para um | única |
| `fato_realizado[chave_par]` | `dim_par[chave_par]` | muitos para um | única |
| `fato_planejado[chave_par]` | `dim_par[chave_par]` | muitos para um | única |
| `fato_planejado[campanha]` | `dim_campanha[campanha]` | muitos para um | **inativa** |
| `fato_pacing_par[chave_par]` | `dim_par[chave_par]` | um para um | única |

Marque `dim_calendario` como tabela de datas. Deixe o relacionamento de
`fato_planejado[campanha]` inativo: `dim_par` já liga as duas pontas, e dois caminhos ativos
criam ambiguidade.

Não relacione `fato_planejado[inicio]` a `dim_calendario`. A janela do flight já foi aplicada em
Python; relacioná-la aqui reabre a dupla contagem.

## Medidas

```dax
Realizado Investimento =
CALCULATE(
    SUM(fato_realizado[investimento]),
    fato_realizado[dentro_do_plano] = TRUE(),
    fato_realizado[par_com_denominador] = TRUE()
)
-- esperado: {brl(n('real.investimento'))}

Planejado Investimento =
CALCULATE(
    SUM(fato_planejado[investimento_planejado]),
    fato_planejado[denominador_valido] = TRUE()
)
-- esperado: {brl(n('plan.investimento'))}

Pacing Investimento =
DIVIDE([Realizado Investimento], [Planejado Investimento])
-- esperado: {n('pacing.investimento'):.4f}% ao formatar como percentual

Realizado Impressoes =
CALCULATE(
    SUM(fato_realizado[impressoes]),
    fato_realizado[dentro_do_plano] = TRUE(),
    fato_realizado[par_com_denominador] = TRUE()
)
-- esperado: {mil(n('real.impressoes'))}

Planejado Impressoes =
CALCULATE(
    SUM(fato_planejado[impressoes_planejadas]),
    fato_planejado[denominador_valido] = TRUE()
)
-- esperado: {mil(n('plan.impressoes'))}

Pacing Impressoes = DIVIDE([Realizado Impressoes], [Planejado Impressoes])
-- esperado: {n('pacing.impressoes'):.4f}%

Realizado Cliques =
CALCULATE(
    SUM(fato_realizado[cliques]),
    fato_realizado[dentro_do_plano] = TRUE(),
    fato_realizado[par_com_denominador] = TRUE()
)
-- esperado: {mil(n('real.cliques'))}

Planejado Cliques =
CALCULATE(
    SUM(fato_planejado[cliques_planejados]),
    fato_planejado[denominador_valido] = TRUE()
)
-- esperado: {mil(n('plan.cliques'))}

Pacing Cliques = DIVIDE([Realizado Cliques], [Planejado Cliques])
-- esperado: {n('pacing.cliques'):.4f}%

Cobertura do Plano =
DIVIDE([Realizado Investimento], SUM(fato_realizado[investimento]))
-- esperado: {n('cobertura.share_realizado_no_plano'):.4f}%

Investimento Fora do Plano =
CALCULATE(
    SUM(fato_realizado[investimento]),
    fato_realizado[dentro_do_plano] = FALSE()
)
-- esperado: {brl(n('valor.realizado_fora'))}

CPM Realizado =
DIVIDE([Realizado Investimento], [Realizado Impressoes]) * {mil(n('cpm.fator'))}
-- esperado: {brl(n('cpm.realizado'))}

CPC Realizado =
DIVIDE([Realizado Investimento], [Realizado Cliques])
-- esperado: {brl(n('cpc.realizado'))}

CTR Realizado =
DIVIDE([Realizado Cliques], [Realizado Impressoes])
-- esperado: {n('ctr.realizado'):.4f}%

Deficit de Cliques =
[Planejado Cliques] - [Realizado Cliques]
-- esperado: {mil(n('cliques.deficit'))}
```

Use sempre `DIVIDE` e nunca o operador `/`. `DIVIDE` devolve vazio onde o denominador é zero ou
nulo; a barra devolve infinito e contamina o total.

## Denominadores: o caso que precisa aparecer no painel

{int(n('zero.flights_denominador_invalido'))} flights foram planejados com investimento em branco e
zero impressões e zero cliques. Um deles, `Joao Pessoa - Não Pulavel | Youtube Ads`, é o único
flight do seu par, e mesmo assim entregou {brl(n('zero.realizado_sem_denominador'))} e
{mil(n('zero.impressoes_sem_denominador'))} impressões dentro da janela.

Esse par tem `denominador_valido = FALSE` e `par_com_denominador = FALSE`, e por isso fica fora
de todas as medidas acima. Não o transforme em zero para "fechar a conta": isso mudaria o
realizado de {brl(n('real.investimento'))} para {brl(n('alt.realizado_com_par_invalido'))} sem
denominador que o sustente.

Sugestão de visual: um cartão à parte, com o texto "1 par entregou sem plano" e o valor
{brl(n('zero.realizado_sem_denominador'))}.

## Visuais que reproduzem o dashboard

| Visual | Tipo | Eixo | Valor | Filtro |
|---|---|---|---|---|
| Cartões do topo | cartão | — | as quatro medidas de pacing e cobertura | — |
| Pacing por métrica | barras horizontais | medida desnormalizada | as três de pacing | — |
| Planejado x realizado por veículo | barras agrupadas | `dim_veiculo[veiculo]` | `Planejado Investimento`, `Realizado Investimento` | — |
| Entrega diária | linha | `dim_calendario[data]` | `Realizado Investimento` | `dim_calendario[na_janela_do_plano] = TRUE` |
| Pacing por campanha | barras horizontais | `dim_campanha[campanha]` | `Pacing Investimento` | `dim_par[denominador_valido] = TRUE` |
| Detalhe | matriz | `dim_par[campanha]`, `dim_par[veiculo]` | planejado, realizado, os três pacings | `dim_par[denominador_valido] = TRUE` |
| Gasto fora do plano | barras | `dim_campanha[campanha]` | `Investimento Fora do Plano` | `dentro_do_plano = FALSE` |

Para a faixa de cor do pacing, use formatação condicional por regra:
abaixo de {n('faixa.limite_inferior'):.0f}% vermelho, entre {n('faixa.limite_inferior'):.0f}% e
{n('faixa.limite_superior'):.0f}% verde, acima de {n('faixa.limite_superior'):.0f}% amarelo. Sempre com
o valor visível no rótulo: a cor não pode ser a única pista.

## Conferência depois de montar

1. Cartão de `Pacing Investimento` precisa mostrar {n('pacing.investimento'):.2f}%. Se mostrar algo
   perto de {n('alt.pacing_sem_dedup'):.0f}%, há um relacionamento de data entre fato e plano e a
   dedup foi desfeita.
2. Se mostrar algo perto de {n('alt.pacing_sem_janela'):.0f}%, o filtro `dentro_do_plano` não foi aplicado.
3. A soma de `Realizado Investimento` quebrada por veículo tem que bater com o total. Em Python a
   diferença é R$ 0,00.
4. `Cobertura do Plano` precisa mostrar {n('cobertura.share_realizado_no_plano'):.2f}%. Esse número
   baixo está certo: o plano cobre uma fatia pequena do que rodou.
"""

(DESTINO / "modelo.md").write_text(MODELO, encoding="utf-8")

for arquivo in sorted(DESTINO.iterdir()):
    print(f"  {arquivo.name}  {arquivo.stat().st_size / 1024:.0f} kB")
