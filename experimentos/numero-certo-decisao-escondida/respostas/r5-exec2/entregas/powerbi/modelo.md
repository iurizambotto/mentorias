# Modelo para o Power BI

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
| `fato_planejado.csv` | 45 | Um flight por linha. Grão: campanha × veículo × janela |
| `fato_realizado.csv` | 16.764 | Um dia de entrega por linha. Grão: campanha × veículo × dia |
| `ponte_flight_entrega.csv` | 1.107 | Par flight × entrega válido. Repete a entrega compartilhada, ver aviso abaixo |
| `dim_campanha.csv` | 185 | Campanhas, com a marca de quem tem plano |
| `dim_veiculo.csv` | 3 | Veículos |
| `dim_calendario.csv` | 585 | Calendário diário contínuo, sem buracos |
| `resumo_campanha_veiculo.csv` | 26 | Resultado já agregado, para conferir o modelo |
| `resumo_flight.csv` | 45 | Detalhe por flight, com a marca de entrega disputada |

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
   1.107 linhas para
   884 entregas, porque
   147 delas são reivindicadas por mais de um
   flight, uma delas por 4. Somar por ali infla
   impressões em 80,23%. Use a ponte só para listar o
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

Sem nenhum filtro aplicado, com todas as 16.809 linhas carregadas:

| Medida | Valor esperado | Base |
|---|---|---|
| Investimento Planejado | R$ 1.033.625,08 | 45 flights, dos quais os 25 pares com denominador válido |
| Investimento Realizado | R$ 1.041.385,17 | 884 entregas dentro do plano |
| Pacing Investimento Total | 100,75% | idem |
| Impressoes Realizadas | 166.872.507 | 884 entregas |
| Pacing Impressoes Total | 121,70% | idem |
| Pacing Cliques Total | 47,32% | idem |
| Gap Investimento | R$ 7.760,09 | idem |

Por veículo, com `Pacing Investimento` numa matriz por `dim_veiculo[Veiculo]`:

| Veículo | Valor esperado |
|---|---|
| Meta Ads | 106,99% |
| Youtube Ads | 107,10% |
| Tiktok Ads | 47,74% |

Conferências que pegam erro de modelo cedo:

- `COUNTROWS ( fato_realizado )` = 16.764.
- `CALCULATE ( COUNTROWS ( fato_realizado ), fato_realizado[dentro_do_plano] = TRUE () )` =
  884. Se der
  1.107, o visual está passando pela ponte.
- `COUNTROWS ( ponte_flight_entrega )` = 1.107.
- A matriz por campanha e veículo deve ter uma linha com `Pacing Investimento` vazio, que é
  `Joao Pessoa - Não Pulavel` em Youtube Ads. Se ela aparecer como 0%, o `DIVIDE` recebeu o
  terceiro argumento.
- `resumo_campanha_veiculo.csv` tem o resultado já pronto: compare a matriz contra ele linha a
  linha antes de publicar.

## Filtros que o painel usa

- Período, ligado a `dim_calendario[data]`, com o intervalo do plano de 2024-05-28 a 2024-07-31.
- Veículo, de `dim_veiculo`.
- Campanha, de `dim_campanha`, com `tem_plano` disponível para separar as
  166 campanhas que rodaram fora deste plano.
- `fato_realizado[motivo_fora]` explica, linha a linha, por que uma entrega ficou fora do
  pacing: campanha sem plano, veículo fora do plano da campanha ou data fora da janela.
