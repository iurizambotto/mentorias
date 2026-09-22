---
title: "Prompt da rodada 5"
date: 2026-09-21
type: prompt
status: publicado
tags: [experimento, prompt, analise-de-dados]
---

# Prompt da rodada 5

| | |
|---|---|
| Camada acrescentada | As quatro skills da pasta agente e o pedido dos entregáveis de uma reunião de resultados. |
| Hipótese registrada antes de rodar | Com o livro de números e o registro de decisões, todo número tem lastro e toda decisão aparece escrita. |
| O que aconteceu | As três entregaram documento, dashboard, dados para Power BI e apresentação. 865 números nos nove entregáveis, todos com lastro. |

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

Antes de me dar qualquer número, faça o seguinte e me mostre o resultado:

- Diga quantas linhas entraram de cada lado da conta, e quantas ficaram de fora.
- Confira se alguma linha de Realizado foi contada em mais de um flight. O plano tem flight
  sobreposto, quer dizer, mesma campanha e mesmo veículo com janelas que se cruzam. Quando isso
  acontecer, aquela linha de Realizado entra na conta uma vez só.
- Cheque se alguma divisão por zero passou despercebida.
- Me mostre o código que gerou cada número, para eu conseguir rodar de novo.

No final, quero o trabalho pronto para levar para a reunião de resultados:

- Um documento com os insights, em Word e em PDF, para quem não vai abrir a planilha.
- Um dashboard que eu consiga abrir no navegador e mandar por email, e os dados já preparados
  para alguém montar o mesmo painel no Power BI.
- Uma apresentação em PowerPoint com os resultados, de uns dez slides.

Este projeto tem skills de análise de dados, de documento de insights, de dashboard e de
apresentação. Use elas. Coloque tudo que for entregável na pasta entregas.
```
