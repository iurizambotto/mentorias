Sim, em dinheiro: o pacing de investimento fechou em 100,75%, e a mesma verba
comprou 21,70% mais impressões do que o plano previa.

## Antes dos números: as conferências que você pediu

**Quantas linhas entraram de cada lado**

| | Linhas |
|---|---|
| Planejado (flights) | 45 |
| Realizado (dias de entrega) | 16.764 |
| Realizado que entra no pacing | 884 |
| Realizado que fica de fora | 15.880 |

O que fica de fora se decompõe sem sobreposição, e a soma fecha com 15.880:

| Motivo | Linhas | Investimento |
|---|---|---|
| Campanha sem linha de Planejado | 10.209 | R$ 12.098.469,92 |
| Veículo fora do plano daquela campanha | 4.166 | R$ 1.216.656,86 |
| Data fora da janela de qualquer flight | 1.505 | R$ 2.712.664,12 |

Do lado do plano, todos os 45 flights entraram. Um deles, a Inauguracao no Tiktok
Ads, entrou com entrega zero: R$ 24.797,50 planejados e nenhum dia veiculado
dentro da própria janela.

**Dupla contagem: sim, existe, e é grande**

O plano tem 8 pares de flights com janelas cruzadas, em 3 combinações de campanha
e veículo: Freeshop no Meta Ads (4 flights sobrepostos), Joao Pessoa no Meta Ads e
Joao Pessoa no Youtube Ads. Isso faz 147 linhas de Realizado casarem com mais de
um flight, uma delas com 4.

Contei cada uma **uma vez só**. Os dois resultados, medidos:

| | Com deduplicação | Sem deduplicação |
|---|---|---|
| Pacing de investimento | 100,75% | 151,32% |
| Pacing de impressões | 121,70% | 219,66% |

Sem deduplicar, as impressões apareceriam 80,23% maiores do que foram.

Por isso o pacing é calculado por campanha × veículo, não por flight: onde as
janelas se cruzam, a entrega diária não diz a qual flight pertence, e um pacing
por flight ali seria artefato da sobreposição, não resultado.

**Divisão por zero: duas passaram perto, nenhuma passou**

- 2 flights do plano estão sem investimento orçado, e 2 estão com impressões e
  cliques orçados em zero.
- Isso deixa 1 par campanha × veículo sem pacing possível: Joao Pessoa - Não
  Pulavel no Youtube Ads, que teve 26 dias de entrega real sem nada orçado contra
  o que comparar. Ele é reportado à parte e **nunca** aparece como 0%, porque
  ausência de plano não é sub-entrega.
- A função que calcula pacing devolve vazio quando o denominador é zero ou nulo, e
  o livro de números recusa valor não finito. Nada não finito chega a um
  entregável.

Uma conferência que mudou o resultado e vale registrar: a primeira versão do
cruzamento devolveu **zero** entregas atribuídas. O lado Realizado carrega as
colunas de janela sempre nulas, então o join renomeou as datas do plano e a
comparação caiu sobre colunas vazias. O código corrigido derruba as colunas nulas
antes do join e afirma, com `assert`, que a janela não é nula depois dele.

## Os números

| Métrica | Planejado | Realizado na janela | Pacing |
|---|---|---|---|
| Investimento | R$ 1.033.625,08 | R$ 1.041.385,17 | 100,75% |
| Impressões | 137.123.083 | 166.872.507 | 121,70% |
| Cliques | 626.766 | 296.581 | 47,32% |

Três leituras que mudam a conversa:

1. **O Tiktok Ads é o único desvio material.** Entregou 47,74% do investimento e
   24,29% das impressões. Meta Ads ficou em 106,99% e Youtube Ads em 107,10%.
   Metade da diferença do Tiktok é o flight da Inauguracao, de R$ 24.797,50, que
   não foi ao ar.
2. **O pacing de cliques de 47,32% não é déficit de entrega.** O plano deriva
   cliques de uma premissa de CTR por flight que vai de 0,05% a 1,00%. Um único
   flight, a Freeshop no Meta Ads, concentra 52,79% de todos os cliques planejados
   com premissa de 1,00%, quatro vezes a mediana do plano. Sem ele, o pacing de
   cliques é 100,46%.
3. **Este plano cobre pouco do que rodou.** Só 6,13% do investimento realizado no
   arquivo pertence a ele. As 166 campanhas sem linha de planejado somam
   R$ 12.098.469,92.

## O que esta análise não responde

- Pacing de flight isolado onde as janelas se cruzam. Faltaria uma chave de flight
  no realizado.
- Se a sobra de impressões vem de preço ou de formato: não há CPM contratado no
  arquivo.
- Se as 166 campanhas fora do plano pertencem a outro planejamento.
- Uma leitura alternativa da sua pergunta, testada e descartada: se "entregamos o
  planejado" incluísse toda a entrega da campanha, mesmo fora da janela, o pacing
  seria 361,72%. Não responde à pergunta, porque mistura entrega de 2023 com plano
  de 2024.

## Decisões que mais movem o resultado

| Decisão | Escolhido | Alternativa |
|---|---|---|
| Entrega compartilhada conta uma vez | 100,75% | 151,32% |
| Só entrega dentro da janela | 100,75% | 361,72% |
| Data de término inclusiva | 100,75% | 87,47% |
| Campanha casa por nome exato | 100,75% | 100,75%, sem efeito |

A última foi testada porque o arquivo tem nomes como Inauguracao e Inauguracao
Barra. Agrupar por prefixo remapearia 1.361 linhas e não muda nada, porque todas
caem fora das janelas de qualquer forma.
