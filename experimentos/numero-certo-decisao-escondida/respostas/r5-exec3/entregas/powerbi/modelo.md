# Modelo para Power BI: pacing de campanhas

Pacote gerado por `analise/scripts/09_powerbi.py`. Todos os CSV sao UTF-8, separador
virgula, decimal ponto, datas em `YYYY-MM-DD`.

> **As medidas abaixo nao foram executadas no Power BI Desktop.** O valor esperado ao lado
> de cada uma vem de `analise/numeros.json`, calculado em Python. Use-o para conferir a
> medida depois de escreve-la: se o cartao no Desktop mostrar outro numero, a medida esta
> diferente da analise, nao o contrario.

## A decisao que ja vem resolvida no pacote

O plano tem flights sobrepostos: mesma campanha, mesmo veiculo, janelas que se cruzam.
147 linhas de entrega caem dentro de mais de um flight, uma delas
dentro de 4 ao mesmo tempo.

Se o modelo relacionasse `fato_realizado` direto a `fato_planejado` por campanha, veiculo e
janela, essas linhas seriam somadas uma vez para cada flight, e o pacing de impressoes daria
219,25% em vez de 121,70%, ou seja
80,16% a mais de entrega que nunca existiu.

Por isso o pacote nao entrega esse relacionamento. Flights sobrepostos ja vem unidos em
`dim_bloco`, e cada linha de `fato_realizado` ja chega com **no maximo um** `id_bloco`. A
contagem unica e garantida pelo modelo, nao por uma medida que alguem precise lembrar de
escrever certo.

**Nao crie** um relacionamento entre `fato_realizado` e `fato_planejado`. Use `dim_bloco`.

## Tabelas

| Tabela | Grao | Linhas |
|---|---|---|
| `fato_realizado.csv` | uma entrega diaria: campanha x veiculo x data | 16764 |
| `fato_planejado.csv` | um flight: campanha x veiculo x janela | 45 |
| `dim_bloco.csv` | um bloco de plano: flights sobrepostos ja unidos | 40 |
| `dim_campanha.csv` | uma campanha | 185 |
| `dim_veiculo.csv` | um veiculo | 3 |
| `dim_calendario.csv` | um dia | 585 |

### Colunas que merecem atencao

- `fato_realizado[id_bloco]`: vazio quando a entrega nao pertence a nenhum plano. Sao
  15.880 das 16.764 linhas.
- `fato_realizado[no_pacing]`: booleano, o mesmo filtro em forma pronta.
- `dim_bloco[tem_meta]`: falso quando o plano daquele bloco tem impressoes zeradas e
  investimento em branco. E 2 flights, num bloco so.
  Todo denominador precisa deste filtro, senao a medida divide por zero.
- `dim_bloco[n_flights]`: quantos flights o bloco uniu. Maior que 1 em
  40 menos os blocos simples, ou seja 3 blocos.
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
dele fica de fora, e o pacing de impressoes sobe de 121,70% para
122,10%. Numerador e denominador precisam cobrir os
mesmos blocos.

```dax
Investimento Realizado =
CALCULATE (
    SUM ( fato_realizado[investimento] ),
    fato_realizado[no_pacing] = TRUE (),
    dim_bloco[tem_meta] = TRUE ()
)
```
Esperado: R$ 1.041.385,17

```dax
Impressoes Realizadas =
CALCULATE (
    SUM ( fato_realizado[impressoes] ),
    fato_realizado[no_pacing] = TRUE (),
    dim_bloco[tem_meta] = TRUE ()
)
```
Esperado: 166.872.507

```dax
Cliques Realizados =
CALCULATE (
    SUM ( fato_realizado[cliques] ),
    fato_realizado[no_pacing] = TRUE (),
    dim_bloco[tem_meta] = TRUE ()
)
```
Esperado: 296.581

```dax
Investimento Planejado =
CALCULATE ( SUM ( dim_bloco[plan_investimento] ), dim_bloco[tem_meta] = TRUE () )
```
Esperado: R$ 1.033.625,08

```dax
Impressoes Planejadas =
CALCULATE ( SUM ( dim_bloco[plan_impressoes] ), dim_bloco[tem_meta] = TRUE () )
```
Esperado: 137.123.083

```dax
Cliques Planejados =
CALCULATE ( SUM ( dim_bloco[plan_cliques] ), dim_bloco[tem_meta] = TRUE () )
```
Esperado: 626.766

### Pacing

`DIVIDE` sem terceiro argumento devolve vazio quando o denominador e zero, que e o
comportamento desejado: o visual mostra branco, e nao um zero que parece resultado.

```dax
Pacing Investimento = DIVIDE ( [Investimento Realizado], [Investimento Planejado] )
```
Esperado: 100,75%

```dax
Pacing Impressoes = DIVIDE ( [Impressoes Realizadas], [Impressoes Planejadas] )
```
Esperado: 121,70%

```dax
Pacing Cliques = DIVIDE ( [Cliques Realizados], [Cliques Planejados] )
```
Esperado: 47,32%

### Eficiencia

```dax
CPM Realizado = DIVIDE ( [Investimento Realizado], [Impressoes Realizadas] ) * 1000
```
Esperado: R$ 6,24

```dax
CPM Planejado = DIVIDE ( [Investimento Planejado], [Impressoes Planejadas] ) * 1000
```
Esperado: R$ 7,54

```dax
CTR Realizado = DIVIDE ( [Cliques Realizados], [Impressoes Realizadas] )
```
Esperado: 0,18%

```dax
CTR Planejado = DIVIDE ( [Cliques Planejados], [Impressoes Planejadas] )
```
Esperado: 0,46%

### Cobertura, para o cartao de contexto

`REMOVEFILTERS` aqui e proposital: este cartao mede o arquivo inteiro, inclusive a entrega
sem plano, e nao deve encolher quando o usuario filtra um bloco.

```dax
Investimento Total do Arquivo =
CALCULATE ( SUM ( fato_realizado[investimento] ), REMOVEFILTERS () )
```
Esperado: R$ 17.075.125,38

```dax
Cobertura do Plano =
DIVIDE ( [Investimento Realizado], [Investimento Total do Arquivo] )
```
Esperado: 6,10%

```dax
Linhas Fora do Pacing =
CALCULATE (
    COUNTROWS ( fato_realizado ),
    fato_realizado[no_pacing] = FALSE (),
    REMOVEFILTERS ( dim_bloco )
)
```
Esperado: 15.880

Essas linhas tem `id_bloco` vazio, entao qualquer filtro vindo de `dim_bloco` as zeraria.
`REMOVEFILTERS ( dim_bloco )` mantem o cartao legivel mesmo com um bloco selecionado.

## Conferencia depois de montar

Coloque os tres pacings em cartoes, sem nenhum filtro aplicado. Se aparecerem
100,75%, 121,70% e 47,32%, o modelo esta
igual a analise. Se o pacing de impressoes vier perto de 219,25%,
alguem criou o relacionamento direto entre realizado e planejado, e a mesma entrega esta sendo
contada em mais de um flight.
