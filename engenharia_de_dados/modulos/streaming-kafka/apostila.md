---
title: "Apostila, Streaming com Apache Kafka"
date: 2026-07-30
type: apostila
status: draft
project: zambotto-mentoria
tags:
  - kafka
  - streaming
---

# Apostila, Streaming com Apache Kafka

> Trilha de Engenharia de Dados. Conduzida por Iuri Zambotto com Paulo Shindi.

## Sumario

- [0. Como usar esta apostila](#0-como-usar-esta-apostila)
- [1. Objetivo pedagogico](#1-objetivo-pedagogico)
- [2. Contexto de negocio](#2-contexto-de-negocio)
- [3. O log particionado](#3-o-log-particionado)
- [4. Chave, particao e ordem](#4-chave-particao-e-ordem)
- [5. Grupo de consumo e offset](#5-grupo-de-consumo-e-offset)
- [6. Semanticas de entrega](#6-semanticas-de-entrega)
- [7. Laboratorio](#7-laboratorio)
- [8. Exercicios e entregaveis](#8-exercicios-e-entregaveis)
- [9. Mini-desafio com solucao](#9-mini-desafio-com-solucao)
- [10. Rubrica de validacao da aprendizagem](#10-rubrica-de-validacao-da-aprendizagem)
- [11. Erros comuns e como corrigir](#11-erros-comuns-e-como-corrigir)
- [12. Plano de continuidade](#12-plano-de-continuidade)
- [13. Glossario](#13-glossario)
- [Referencias](#referencias)
- [Fontes verificadas](#fontes-verificadas)

## 0. Como usar esta apostila

Leitura linear para aprender, sumario para revisar um ponto isolado.

O laboratorio da secao 7 foi executado de ponta a ponta e as saidas registradas sao reais, nao
ilustrativas. Cada `Lab N` existe no `lab.json` deste modulo, com o comando e a saida esperada.

Pre-requisito: o modulo de Docker e ambiente local. Voce precisa conseguir subir um Compose.

## 1. Objetivo pedagogico

Ao terminar este modulo voce consegue:

- explicar por que o Kafka e um log particionado e nao uma fila;
- prever em qual particao uma mensagem vai cair, a partir da chave;
- dizer o que o Kafka garante sobre ordem, e o que ele nao garante;
- ler o offset de um grupo de consumo e interpretar o lag;
- escolher a semantica de entrega adequada, sabendo onde a garantia termina.

## 2. Contexto de negocio

A startup de marketing do Projeto 1 acompanha campanhas pagas. Ate aqui o pipeline era batch:
o dado chegava de hora em hora e o relatorio fechava no dia seguinte.

Surgiu uma pergunta que o batch nao responde: quando uma campanha comeca a queimar orcamento
sem converter, quanto tempo o time leva para perceber? Com carga de hora em hora, ate uma hora.
Com o orcamento diario de uma campanha grande, uma hora e dinheiro.

Streaming entra aqui para reduzir a latencia entre o evento acontecer e alguem poder agir. Nao
para substituir o batch, que continua fazendo o fechamento correto.

## 3. O log particionado

**O que e**

Um topico do Kafka nao e uma fila. E um **log**: uma sequencia de registros que so cresce no
fim, dividida em particoes, e da qual ninguem remove nada ao ler.

Essa diferenca muda tudo. Numa fila, ler consome. No Kafka, ler apenas move um marcador de
posicao, e o mesmo registro pode ser lido de novo, por outro consumidor ou pelo mesmo mais tarde.

**Por que particionar**

A particao e a unidade de paralelismo. Um topico com 3 particoes pode ser lido por ate 3
consumidores do mesmo grupo em paralelo. Com 1 particao, so um consumidor trabalha, por mais
que voce suba dez.

**O que o Lab 3 mostra**

Ao descrever o topico, cada particao aparece com um `Leader`. O lider e o broker responsavel
por aquela particao: toda escrita e leitura passa por ele. Em cluster de um no so, o lider e
sempre o mesmo, e por isso o laboratorio nao demonstra failover.

## 4. Chave, particao e ordem

**A regra**

Quando a mensagem tem chave, o Kafka escolhe a particao por hash da chave. Mesma chave, mesma
particao, sempre. Sem chave, a distribuicao e circular entre as particoes.

**O que isso garante**

Ordem **dentro da particao**, e so. O Kafka nao garante ordem global no topico, e nao tem como:
particoes sao independentes e escritas em paralelo.

Na pratica isso e suficiente quase sempre, porque o que importa e a ordem dos eventos **do
mesmo titular**. Se todos os eventos do usuario `u1` caem na mesma particao, a sequencia
`click`, depois `purchase`, chega nessa ordem.

**O equivoco comum**

Achar que aumentar particoes so melhora. Aumentar particoes aumenta paralelismo e **redistribui
as chaves**: uma chave que caia na particao 1 com 3 particoes pode cair na 4 com 6. Eventos
antigos ficam onde estavam, e a ordem por chave se quebra na fronteira da mudanca.

Por isso o numero de particoes e decisao de projeto, nao de ajuste fino.

**O que o Lab 5 mostra**

A saida real do laboratorio:

```
Partition:0	u2	{"user_id":"u2","evento":"view"}
Partition:1	u1	{"user_id":"u1","evento":"click"}
Partition:1	u1	{"user_id":"u1","evento":"purchase"}
```

As duas mensagens de `u1` cairam na particao 1, e nessa ordem. A de `u2` foi para a 0. A regra
de hash da chave nao e teoria, esta ali.

## 5. Grupo de consumo e offset

**O que e um grupo**

Consumidores que compartilham o mesmo `group.id` dividem as particoes entre si. Cada particao
e lida por exatamente um membro do grupo, o que da paralelismo sem duplicar processamento.

Consumidores de grupos diferentes leem o mesmo topico de forma independente. E por isso que o
mesmo fluxo alimenta o time de analytics e o de operacoes sem um atrapalhar o outro.

**Offset**

O offset e a posicao do grupo em cada particao. Ele fica guardado no proprio Kafka, num topico
interno, e nao no consumidor. Se o consumidor morre e volta, retoma de onde parou.

**Lag**

Lag e a diferenca entre o fim do log e a posicao do grupo. Lag zero significa que o grupo leu
tudo. Lag crescendo significa que a producao esta mais rapida que o consumo, e e a metrica que
merece alerta.

**O que o Lab 6 mostra**

```
GROUP           TOPIC         PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
time-analytics  eventos-mkt   0          1               1               0
time-analytics  eventos-mkt   1          2               2               0
```

O grupo commitou 1 mensagem na particao 0 e 2 na particao 1, que e exatamente a distribuicao
observada no Lab 5. Lag zero nas duas.

Repare que a particao 2 nao aparece: nenhuma mensagem caiu nela, entao o grupo nao tem offset
commitado ali.

## 6. Semanticas de entrega

| Semantica | O que garante | Custo |
|---|---|---|
| At-most-once | Nunca duplica, pode perder | Commit antes de processar |
| At-least-once | Nunca perde, pode duplicar | Commit depois de processar |
| Exactly-once | Cada evento uma vez, **dentro do Kafka** | Producer idempotente e transacao |

**Onde a garantia termina**

O exactly-once do Kafka e `read-process-write`: consumir de um topico, processar, produzir em
outro e commitar o offset, tudo ou nada. E atomico **dentro do Kafka**.

Seu S3, seu Postgres e sua tabela Iceberg nao participam dessa transacao. No instante em que o
dado atravessa essa borda, voce voltou para at-least-once.

Na pratica, o caminho mais simples e mais barato e assumir at-least-once e tornar a duplicata
inofensiva no destino, com chave de negocio explicita e escrita idempotente.

**CDC nao mora aqui**

Change Data Capture aparece com frequencia junto de Kafka, via Debezium. O **conceito** de CDC
pertence ao modulo `cdc`, que cobre captura log-based sem broker. Este modulo trata apenas do
**transporte**: como o evento de mudanca viaja pelo Kafka depois de capturado.

## 7. Laboratorio

Todos os passos abaixo foram executados em 2026-07-30 e as saidas sao reais. O manifesto
`lab.json` deste modulo registra comando e saida esperada de cada um.

Antes de comecar, leia `infrastructure/runbooks/00_pre_requisitos.md`.

- **Lab 1**, subir a stack do Kafka
- **Lab 2**, criar o topico com 3 particoes
- **Lab 3**, inspecionar particoes e lider
- **Lab 4**, produzir eventos com chave
- **Lab 5**, consumir e observar a particao de cada chave
- **Lab 6**, inspecionar offset do grupo de consumo
- **Lab 7**, derrubar a stack

Os scripts Python em `scripts/producers/` e `scripts/consumers/` cobrem os mesmos conceitos com
a biblioteca cliente, para quem quiser ir alem do CLI.

## 8. Exercicios e entregaveis

**Exercicio 1: prever a particao**

Objetivo: aplicar a regra de hash da chave.

Contexto: o topico `eventos-mkt` tem 3 particoes. Voce vai produzir eventos das chaves `u1`,
`u2`, `u3` e `u4`.

Entregavel: antes de rodar, escreva sua previsao de qual chave cai em qual particao. Depois
rode o Lab 4 e o Lab 5 com essas chaves e compare. Explique os acertos e os erros.

---

**Exercicio 2: o efeito de mudar particoes**

Objetivo: entender por que o numero de particoes e decisao de projeto.

Contexto: partindo do topico com 3 particoes ja populado, aumente para 6 com
`kafka-topics.sh --alter --partitions 6`.

Entregavel: produza de novo as mesmas chaves, consuma tudo desde o inicio e mostre uma chave
cujos eventos ficaram divididos entre duas particoes. Explique o impacto na ordem.

---

**Exercicio 3: lag sob pressao**

Objetivo: ler o lag como metrica operacional.

Contexto: produza 1000 eventos e consuma com um unico consumidor lento, com pausa artificial
entre mensagens.

Entregavel: tabela com o lag medido em tres momentos, e uma frase dizendo o que voce alertaria
em producao e a partir de qual limiar.

---

**Exercicio 4: escolher a semantica**

Objetivo: decidir com criterio, nao por reflexo.

Contexto: dois casos. O primeiro contabiliza cliques para cobranca de anunciante. O segundo
atualiza um painel de monitoramento que refaz o calculo a cada minuto.

Entregavel: para cada caso, a semantica escolhida, a justificativa e o que precisa existir no
destino para que a escolha se sustente.

## 9. Mini-desafio com solucao

**Enunciado**

O time de operacoes reclama que o painel mostra o evento de `purchase` de um usuario **antes**
do `click` que o originou. Os dois eventos sao produzidos pelo mesmo servico, na ordem certa,
para o mesmo topico. O topico tem 6 particoes.

Por que isso acontece, e como corrigir sem mudar o numero de particoes?

**Dicas antes do gabarito**

- O Kafka garante ordem em que escopo?
- O que decide a particao de uma mensagem?
- O produtor esta enviando chave?

**Gabarito comentado**

Os eventos estao sendo produzidos **sem chave**. Sem chave, o Kafka distribui de forma circular
entre as 6 particoes, entao `click` e `purchase` do mesmo usuario caem em particoes diferentes.

Particoes sao lidas em paralelo e independentes entre si. O Kafka garante ordem **apenas dentro
da particao**, entao nada impede o consumidor de processar a particao que tem o `purchase`
antes da que tem o `click`. Nao ha bug: e o comportamento correto de um log particionado.

A correcao e produzir com `user_id` como chave. A partir dai, todos os eventos do mesmo usuario
caem na mesma particao e chegam na ordem em que foram produzidos.

Cuidado ao aplicar: a correcao vale para os eventos **novos**. Os que ja estao no topico
continuam onde foram gravados, e a ordem so se restabelece na janela posterior a mudanca.

## 10. Rubrica de validacao da aprendizagem

| Criterio | Insuficiente | Suficiente | Excelente |
|---|---|---|---|
| Ordem | Diz que o Kafka garante ordem | Diz que garante dentro da particao | Explica por que ordem global e impossivel com particoes paralelas |
| Chave | Nao relaciona chave e particao | Sabe que a chave decide a particao | Antecipa o efeito de mudar o numero de particoes sobre a ordem |
| Offset | Confunde offset com posicao do consumidor | Sabe que o offset e do grupo e vive no Kafka | Interpreta lag como sinal operacional e propoe limiar |
| Semantica | Escolhe exactly-once por reflexo | Escolhe com base no caso | Aponta onde a garantia termina e o que fazer no destino |
| Laboratorio | Nao roda | Reproduz os labs | Modifica o cenario e explica a saida diferente |

## 11. Erros comuns e como corrigir

| Sintoma | Causa | Correcao |
|---|---|---|
| Eventos do mesmo usuario fora de ordem | Produzir sem chave | Usar a chave de negocio como chave da mensagem |
| Subir varios consumidores e so um trabalhar | Mais consumidores que particoes no grupo | Aumentar particoes no projeto, ou aceitar o teto |
| Consumidor nao ve mensagem antiga | Grupo novo comeca do fim por padrao | Usar `--from-beginning` ou configurar `auto.offset.reset` |
| Script no host nao conecta | Listener anunciado errado | Conferir `KAFKA_ADVERTISED_LISTENERS`, o EXTERNAL precisa anunciar `localhost:9092` |
| Lag cresce sem parar | Consumo mais lento que producao | Paralelizar por particao ou otimizar o processamento |
| Reprocessar duplica no destino | Confiar no exactly-once atravessando a borda | Escrita idempotente com chave de negocio no destino |

## 12. Plano de continuidade

Proximo passo natural na trilha e o modulo `kubernetes`, que cobre como esse tipo de servico
roda em producao com limite de recurso e reinicio controlado.

Para aprofundar o assunto deste modulo: `cdc`, que e o dono do conceito de Change Data Capture,
e trata da captura que muitas vezes alimenta um topico como este.

## 13. Glossario

| Termo | Significado |
|---|---|
| Broker | Servidor que armazena e serve as particoes |
| Topico | Nome logico do log, dividido em particoes |
| Particao | Unidade de paralelismo e de ordem, um log que so cresce no fim |
| Offset | Posicao de um grupo dentro de uma particao |
| Grupo de consumo | Conjunto de consumidores que divide as particoes entre si |
| Lag | Distancia entre o fim do log e a posicao do grupo |
| KRaft | Modo de consenso do Kafka que dispensa o ZooKeeper |
| Listener | Endereco e protocolo pelo qual o broker aceita conexao |

## Referencias

- Documentacao do Apache Kafka, secao de design e de consumidores. https://kafka.apache.org/documentation/
- Imagem oficial `apache/kafka` no Docker Hub. https://hub.docker.com/r/apache/kafka

## Fontes verificadas

Verificado em 2026-07-30, com Kafka 3.9.0 em modo KRaft, via Docker Compose 2.39.1.

- A saida de particao por chave da secao 4 e a execucao real do Lab 5 neste ambiente.
- A tabela de offset e lag da secao 5 e a execucao real do Lab 6 neste ambiente.
- As imagens `apache/kafka:3.9.0` e `provectuslabs/kafka-ui:v0.7.2` foram confirmadas no
  registry com `docker manifest inspect` na mesma data.
- O manifesto `lab.json` deste modulo registra nivel 3 para os sete laboratorios.
