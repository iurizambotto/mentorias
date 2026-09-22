## As conferências, antes dos números

**Quantas linhas entraram de cada lado**

O arquivo tem extensão `.xls` mas é CSV UTF-8 com BOM, e empilha duas tabelas: 45 linhas de
Planejado (um flight cada) e 16.764 de Realizado (um dia de entrega cada).

| | Linhas | Entraram | Ficaram de fora |
|---|---|---|---|
| Planejado | 45 | 44 flights, em 39 blocos com meta utilizável | 1 flight, num bloco sem denominador |
| Realizado | 16.764 | 884 | 15.880 |

Das 15.880 que ficaram de fora: 14.375 são de campanha e veículo sem nenhum flight, e 1.505
são de campanha planejada mas com data fora da janela. São 166 campanhas com entrega e sem
nenhuma linha de plano.

**Linha de Realizado contada em mais de um flight: sim, 147 delas**

Existem 3 grupos de flights sobrepostos: Freeshop no Meta (4 flights), Joao Pessoa no Meta (2)
e Joao Pessoa no YouTube (2). 147 linhas de Realizado caem na janela de mais de um flight, e
uma delas é coberta por 4 ao mesmo tempo.

Uni os flights sobrepostos num bloco só, que soma o planejado e cobre a união das janelas.
Os 45 flights viraram 40 blocos, e cada linha de Realizado passa a casar com no máximo 1
bloco, o que garante a contagem única por construção. **Isso importa muito:** sem esse
cuidado, o pacing de impressões daria 219,25% em vez de 121,70%, ou seja 80,16% de entrega
que nunca existiu.

**Divisão por zero: havia duas, e não passaram**

`Joao Pessoa / Youtube Ads` e `Joao Pessoa - Não Pulavel / Youtube Ads` estão no plano com
impressões e cliques zerados e investimento em branco. O primeiro divide bloco com um flight
que tem meta, então o bloco fica utilizável. O segundo é um bloco inteiro sem meta: recebeu
26 dias de entrega, 558.959 impressões e R$ 5.949,31, e ficou fora do pacing, marcado como
indefinido e nunca como zero.

O livro de números recusa valor não finito, então nenhuma divisão por zero chega a um número
citado. Também conferi o inverso: incluir esse bloco mudaria o pacing de impressões de
121,70% para 122,10%.

## A resposta

**O dinheiro foi entregue como planejado, a audiência veio acima, e o clique veio pela
metade.**

| | Planejado | Realizado | Pacing |
|---|---|---|---|
| Investimento | R$ 1.033.625,08 | R$ 1.041.385,17 | 100,75% |
| Impressões | 137.123.083 | 166.872.507 | 121,70% |
| Cliques | 626.766 | 296.581 | 47,32% |

Base: 39 blocos de plano contra 884 linhas de entrega dentro das janelas.

As três divergem por um motivo só. A mídia saiu a R$ 6,24 por mil impressões contra R$ 7,54
previstos, 17,21% mais barata, e o mesmo dinheiro comprou mais audiência. Só que essa mídia
converte menos: a taxa de clique foi 0,18% contra 0,46% planejados, 61,12% abaixo. Faltaram
330.185 cliques.

Por veículo, o TikTok é o único abaixo da meta nas três métricas: 47,74% da verba, 24,29% da
audiência e 12,81% dos cliques. Dentro dele, a ação Inauguração tinha R$ 24.797,50 e 12 dias
reservados e não registrou um único dia de entrega. O Meta entregou 135,01% da audiência e
48,34% dos cliques; o YouTube fez o inverso, 87,84% e 111,74%.

## O que esta análise não responde

- **A operação inteira.** O plano cobre 6,10% do investimento realizado no arquivo. O plano
  vai de 2024-05-28 a 2024-07-31 e o Realizado vai de 2023-01-03 a 2024-08-09.
- **Resultado de negócio.** O arquivo tem mídia entregue, não venda nem conversão. Um pacing
  de clique em 47,32% é grave se a meta era tráfego e pode ser irrelevante se era alcance.
- **Outra leitura da pergunta.** Respondi comparando o realizado dentro da janela de cada
  flight contra o plano daquele flight. A outra leitura seria comparar tudo que a área
  entregou no período contra tudo que foi planejado, sem casar por campanha. Daria um número
  maior e menos honesto, porque somaria entrega de campanha que nunca teve plano.
- **Pacing de flight isolado** nos 3 blocos sobrepostos.

## As decisões que mais movem o resultado

| Decisão | Escolhido | Alternativa |
|---|---|---|
| Linha em flights sobrepostos conta uma vez só | Impressões 121,70% | 219,25% sem deduplicar |
| Somar tudo antes de dividir | Cliques 47,32% | 146,23% como média simples entre blocos |
| Casar por campanha **e** veículo | Impressões 121,70% | 122,80% ignorando o veículo |
| Bloco sem meta fica fora | Impressões 121,70% | 122,10% incluindo |
| Nome de campanha casa exato | Impressões 121,70% | 121,70% agrupando variantes por prefixo |

A última não muda nada porque as 1.361 linhas que mudariam de nome são de 2023, fora de
qualquer janela. Registrei mesmo assim, já que o perfil apontou as variantes.
