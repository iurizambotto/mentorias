---
title: "Prompt da rodada 3"
date: 2026-09-21
type: prompt
status: publicado
tags: [experimento, prompt, analise-de-dados]
---

# Prompt da rodada 3

| | |
|---|---|
| Camada acrescentada | A regra de negócio: o que é um flight e que pacing só se mede dentro da janela dele. |
| Hipótese registrada antes de rodar | O modelo casa cada flight com a própria janela e o número cai, mas infla nos flights sobrepostos, perto de 152%. |
| O que aconteceu | Hipótese derrubada. As três ficaram entre 100,8% e 101,3%. Surgiu uma segunda leitura, que tira o flight sem verba orçada. |

O texto abaixo foi enviado sem alteração, em três sessões novas e isoladas.

```text
Analisa esse arquivo aqui e me diz como foi a performance das campanhas.

O que eu quero saber é se a gente entregou o que tinha planejado.

Sobre o arquivo:

- A coluna Base separa duas coisas bem diferentes. Linha "Planejado" é o que foi orçado antes
  de a campanha ir pro ar. Linha "Realizado" é o que de fato foi entregue e cobrado.
- Campanha é o nome da ação comercial. Veiculo é a plataforma onde ela rodou.
- Soma de Investimento é dinheiro, em reais.
- Soma de Impressoes e Soma de Cliques são a entrega da mídia.
- Modalidade, Objetivo e Publico são classificações da campanha, não são métricas.
- Data é o dia a que a linha se refere.

Como a área trabalha:

- Cada linha de Planejado é um flight, que é um pedaço de campanha num veículo específico, com
  janela de veiculação definida em Data de Inicio e Data de Termino.
- Cada linha de Realizado é a entrega de um único dia, de uma campanha, num veículo.
- Pacing é o realizado dividido pelo planejado. Só entra na conta o realizado que caiu dentro da
  janela daquele flight e no mesmo veículo. Entrega fora da janela do flight não pertence àquele
  plano.
- O arquivo tem campanha que rodou sem estar nesse plano. Campanha que não tem linha de Planejado
  fica de fora da conta de pacing.
```
