# Modelo para Power BI: pacing de campanhas

Pacote gerado por `analise/scripts/09_powerbi.py`. Todos os CSV estão em UTF-8, separador
vírgula, decimal com ponto e data no formato `AAAA-MM-DD`.

> **As medidas DAX abaixo não foram executadas no Power BI Desktop.** O valor esperado ao lado
> de cada uma vem de `analise/numeros.json`, calculado em Python. Use-o para conferir a medida
> depois de montar o modelo: se o cartão não bater com o valor esperado, a medida está errada,
> não o número.

## Antes de tudo: por que a deduplicação já vem pronta

O plano tem 3 pares de campanha e veículo com janelas de flight que
se cruzam (8 pares de flights). Se você relacionar
`fato_realizado` a `fato_planejado` por campanha e veículo e filtrar a data entre início e fim,
o Power BI vai repetir a mesma entrega uma vez por flight que a contém: 147
linhas cairiam em mais de um flight, uma delas em 4 flights ao
mesmo tempo. O realizado subiria de R$ 1.047.334,48 para
R$ 1.570.037,10, e o pacing de investimento de 100.75%
para 151.32%.

Por isso **não existe relacionamento entre `fato_realizado` e `fato_planejado`** neste modelo. A
coluna `dentro_do_plano`, já calculada em Python pela união das janelas de cada par, é o que
resolve a dedup. Respeite isso: qualquer medida que cruze as duas tabelas por data volta a contar
em dobro.

## Tabelas

| Tabela | Grão de uma linha | Linhas | Papel |
|---|---|---|---|
| `fato_realizado.csv` | um anúncio, num veículo, num dia | 16.764 | fato da entrega |
| `fato_planejado.csv` | um flight: campanha + veículo + janela | 45 | fato do plano |
| `fato_pacing_par.csv` | um par campanha + veículo | 26 | agregado já deduplicado |
| `dim_campanha.csv` | uma campanha | 185 | dimensão |
| `dim_veiculo.csv` | um veículo | 3 | dimensão |
| `dim_par.csv` | um par campanha + veículo com plano | 26 | dimensão-ponte |
| `dim_calendario.csv` | um dia | 585 | dimensão de tempo |

### Colunas que merecem atenção

- `fato_realizado.motivo`: por que a linha entrou ou não na conta. Valores: `dentro do plano`,
  `campanha fora do plano`, `veiculo nao planejado para a campanha`, `data fora da janela do flight`.
- `fato_realizado.dentro_do_plano`: booleano, o filtro que toda medida de pacing usa.
- `fato_realizado.par_com_denominador`: falso para o par cujo plano é vazio. Ver a seção de
  denominadores.
- `fato_planejado.investimento_planejado`: **nulo em 2 flights.**
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
-- esperado: R$ 1.041.385,17

Planejado Investimento =
CALCULATE(
    SUM(fato_planejado[investimento_planejado]),
    fato_planejado[denominador_valido] = TRUE()
)
-- esperado: R$ 1.033.625,08

Pacing Investimento =
DIVIDE([Realizado Investimento], [Planejado Investimento])
-- esperado: 100.7508% ao formatar como percentual

Realizado Impressoes =
CALCULATE(
    SUM(fato_realizado[impressoes]),
    fato_realizado[dentro_do_plano] = TRUE(),
    fato_realizado[par_com_denominador] = TRUE()
)
-- esperado: 166.872.507

Planejado Impressoes =
CALCULATE(
    SUM(fato_planejado[impressoes_planejadas]),
    fato_planejado[denominador_valido] = TRUE()
)
-- esperado: 137.123.083

Pacing Impressoes = DIVIDE([Realizado Impressoes], [Planejado Impressoes])
-- esperado: 121.6954%

Realizado Cliques =
CALCULATE(
    SUM(fato_realizado[cliques]),
    fato_realizado[dentro_do_plano] = TRUE(),
    fato_realizado[par_com_denominador] = TRUE()
)
-- esperado: 296.581

Planejado Cliques =
CALCULATE(
    SUM(fato_planejado[cliques_planejados]),
    fato_planejado[denominador_valido] = TRUE()
)
-- esperado: 626.766

Pacing Cliques = DIVIDE([Realizado Cliques], [Planejado Cliques])
-- esperado: 47.3193%

Cobertura do Plano =
DIVIDE([Realizado Investimento], SUM(fato_realizado[investimento]))
-- esperado: 6.0988%

Investimento Fora do Plano =
CALCULATE(
    SUM(fato_realizado[investimento]),
    fato_realizado[dentro_do_plano] = FALSE()
)
-- esperado: R$ 16.027.790,90

CPM Realizado =
DIVIDE([Realizado Investimento], [Realizado Impressoes]) * 1.000
-- esperado: R$ 6,24

CPC Realizado =
DIVIDE([Realizado Investimento], [Realizado Cliques])
-- esperado: R$ 3,51

CTR Realizado =
DIVIDE([Realizado Cliques], [Realizado Impressoes])
-- esperado: 0.1777%

Deficit de Cliques =
[Planejado Cliques] - [Realizado Cliques]
-- esperado: 330.185
```

Use sempre `DIVIDE` e nunca o operador `/`. `DIVIDE` devolve vazio onde o denominador é zero ou
nulo; a barra devolve infinito e contamina o total.

## Denominadores: o caso que precisa aparecer no painel

2 flights foram planejados com investimento em branco e
zero impressões e zero cliques. Um deles, `Joao Pessoa - Não Pulavel | Youtube Ads`, é o único
flight do seu par, e mesmo assim entregou R$ 5.949,31 e
558.959 impressões dentro da janela.

Esse par tem `denominador_valido = FALSE` e `par_com_denominador = FALSE`, e por isso fica fora
de todas as medidas acima. Não o transforme em zero para "fechar a conta": isso mudaria o
realizado de R$ 1.041.385,17 para R$ 1.047.334,48 sem
denominador que o sustente.

Sugestão de visual: um cartão à parte, com o texto "1 par entregou sem plano" e o valor
R$ 5.949,31.

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
abaixo de 90% vermelho, entre 90% e
110% verde, acima de 110% amarelo. Sempre com
o valor visível no rótulo: a cor não pode ser a única pista.

## Conferência depois de montar

1. Cartão de `Pacing Investimento` precisa mostrar 100.75%. Se mostrar algo
   perto de 151%, há um relacionamento de data entre fato e plano e a
   dedup foi desfeita.
2. Se mostrar algo perto de 362%, o filtro `dentro_do_plano` não foi aplicado.
3. A soma de `Realizado Investimento` quebrada por veículo tem que bater com o total. Em Python a
   diferença é R$ 0,00.
4. `Cobertura do Plano` precisa mostrar 6.10%. Esse número
   baixo está certo: o plano cobre uma fatia pequena do que rodou.
