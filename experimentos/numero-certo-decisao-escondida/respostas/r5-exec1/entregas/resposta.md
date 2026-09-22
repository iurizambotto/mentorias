# Pacing das campanhas: entregamos o que foi planejado?

## Resposta direta

Entregamos o **dinheiro**, entregamos as **impressões**, mas não entregamos os **cliques**: o
investimento fechou em 100,75% do planejado e as impressões em 121,70%, enquanto os cliques
pararam em 47,32% do plano.

## As linhas que entraram na conta

| Lado | Linhas |
|---|---|
| Planejado (flights) | 45 |
| Realizado (total no arquivo) | 16.764 |
| Realizado que entrou na conta | 884 |
| Realizado que ficou de fora | 15.880 |

Os motivos de quem ficou de fora:

| Motivo | Linhas |
|---|---|
| Campanha sem nenhuma linha de Planejado | 10.209 |
| Veículo não planejado para aquela campanha | 4.166 |
| Data fora da janela do flight | 1.505 |

O plano cobre 19 campanhas das 185 que aparecem no arquivo, e 26 pares de campanha e veículo.
Em valor, a conta de pacing enxerga 6,10% do investimento realizado. Os outros 93,90%, que são
R$ 16.027.790,90, são entrega que nenhum flight deste plano comprou.

## Dupla contagem: encontrada e corrigida

O plano tem 3 pares de campanha e veículo com flights de janela sobreposta, somando 8 pares de
flights que se cruzam:

| Campanha | Veículo | Flights | Pares cruzados |
|---|---|---|---|
| Freeshop | Meta Ads | 4 | 6 |
| Joao Pessoa | Meta Ads | 2 | 1 |
| Joao Pessoa | Youtube Ads | 2 | 1 |

Se cada linha de Realizado fosse casada com todos os flights que a contêm, o join devolveria
1.107 linhas em vez de 884, ou seja, 223 linhas inventadas. **147 linhas** cairiam em mais de um
flight, e uma delas cairia em **4 flights** ao mesmo tempo.

O efeito em dinheiro é grande: o realizado passaria de R$ 1.047.334,48 para R$ 1.570.037,10, uma
invenção de R$ 522.702,62, e o pacing de investimento saltaria de 100,75% para 151,32%.

Na conta entregue, cada linha de Realizado conta **uma vez só**, pela união das janelas de cada
par campanha e veículo.

## Divisão por zero: uma passou, e foi isolada

Dois flights foram planejados com investimento nulo e 0 impressões e 0 cliques, os dois em
Youtube Ads, com janela de 2024-06-01 a 2024-06-30:

- `Joao Pessoa / Youtube Ads`: o par tem um segundo flight com números válidos, então o
  denominador do par se sustenta.
- `Joao Pessoa - Não Pulavel / Youtube Ads`: este é o único flight do par. O denominador é nulo,
  mas a campanha **entregou de verdade** na janela, R$ 5.949,31 e 558.959 impressões.

Esse par ficou fora do agregado e está reportado à parte. É plano inexistente com entrega real,
não é entrega faltando.

## Os números do pacing

| Métrica | Planejado | Realizado | Pacing |
|---|---|---|---|
| Investimento | R$ 1.033.625,08 | R$ 1.041.385,17 | 100,75% |
| Impressões | 137.123.083 | 166.872.507 | 121,70% |
| Cliques | 626.766 | 296.581 | 47,32% |

Por veículo, no investimento:

| Veículo | Planejado | Realizado | Pacing investimento | Pacing cliques |
|---|---|---|---|---|
| Meta Ads | R$ 825.982,09 | R$ 883.743,03 | 106,99% | 48,34% |
| Youtube Ads | R$ 108.593,16 | R$ 110.351,89 | 101,62% | 111,74% |
| Tiktok Ads | R$ 99.049,83 | R$ 47.290,25 | 47,74% | 12,81% |

Dos 25 pares no agregado, 19 ficaram entre 90% e 110% de pacing de investimento, 3 abaixo de 90%
e 3 acima de 110%. A mediana por par é 99,9999%.

## O que explica o furo de cliques

A mídia saiu mais barata por impressão e muito mais cara por clique:

| Indicador | Planejado | Realizado |
|---|---|---|
| CPM | R$ 7,54 | R$ 6,24 |
| CPC | R$ 1,65 | R$ 3,51 |
| CTR | 0,4571% | 0,1777% |

Compramos 21,70% mais impressões do que o plano pedia, a um CPM menor, mas cada mil impressões
converteu em menos de metade dos cliques previstos. Faltaram 330.185 cliques.

## Onde estão os piores casos

- `Inauguracao / Tiktok Ads` foi planejada com R$ 24.797,50 e **não teve nenhuma entrega** na
  janela. Pacing 0%.
- `Impulsionamentos` fechou em 82,18% do investimento planejado.
- Tiktok Ads como um todo entregou menos da metade da verba planejada.
- No outro extremo, `Maceio` gastou 134,10% e `Freeshop` 128,27% do planejado.

Somando só os pares abaixo de 90%, ficaram R$ 55.132,33 de verba planejada sem entrega.

## O que esta análise não responde

- **Se o plano estava certo.** O pacing compara entrega com orçamento, não julga o orçamento. Um
  flight planejado com 0 impressões é erro de plano, e o pacing não tem como apontar isso.
- **Por que 93,90% do investimento ficou fora do plano.** O arquivo não diz se essas 166 campanhas
  tinham plano em outra planilha ou rodaram sem plano nenhum.
- **Pacing por flight individual** dentro dos grupos sobrepostos de Freeshop e Joao Pessoa. A
  união de janelas acerta o total do par, mas não existe informação no arquivo para dividir um dia
  de entrega entre flights que se cruzam.

## As decisões que mais movem o resultado

| Decisão | Escolhido | Alternativa |
|---|---|---|
| Deduplicar linha que cai em vários flights | 100,75% | 151,32% sem dedup |
| Exigir que a data caia na janela do flight | 100,75% | 361,72% sem filtro de data |
| Exigir o mesmo veículo no match | 100,75% | 103,46% ignorando veículo |

Campanhas de nome parecido, como `Fds1`, `Fds1 Out` e `Fds1 Set`, foram tratadas como campanhas
distintas. O perfil do arquivo sugeriu que fossem variantes, mas são ações comerciais separadas, e
fundi-las transformaria gasto fora do plano em gasto dentro do plano.
