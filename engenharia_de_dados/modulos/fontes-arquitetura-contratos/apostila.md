---
title: "Apostila, fontes, arquitetura e contratos de dados"
date: 2026-07-31
type: apostila
status: draft
project: zambotto-mentoria
tags: [engenharia_de_dados, arquitetura]
---

# Apostila, fontes, arquitetura e contratos de dados

> Trilha de Engenharia de Dados. Conduzida por Iuri Zambotto e Paulo Shindi.

## Sumário

- [0. Como usar esta apostila](#0-como-usar-esta-apostila)
- [1. Objetivo pedagógico](#1-objetivo-pedagógico)
- [2. Contexto de negócio](#2-contexto-de-negócio)
- [3. As perguntas que a arquitetura precisa responder](#3-as-perguntas-que-a-arquitetura-precisa-responder)
- [4. O modelo de dados, cinco entidades](#4-o-modelo-de-dados-cinco-entidades)
- [5. A natureza de cada fonte](#5-a-natureza-de-cada-fonte)
- [6. Categorias de ferramenta de ingestão](#6-categorias-de-ferramenta-de-ingestão)
- [7. Construir ou comprar](#7-construir-ou-comprar)
- [8. Contratos de dados](#8-contratos-de-dados)
- [9. O architecture canvas](#9-o-architecture-canvas)
- [10. Exercícios e entregáveis](#10-exercícios-e-entregáveis)
- [11. Mini-desafio com solução](#11-mini-desafio-com-solução)
- [12. Rubrica de validação da aprendizagem](#12-rubrica-de-validação-da-aprendizagem)
- [13. Erros comuns e como corrigir](#13-erros-comuns-e-como-corrigir)
- [14. Plano de continuidade](#14-plano-de-continuidade)
- [15. Glossário](#15-glossário)
- [Referências](#referências)
- [Fontes verificadas (2026-07-31)](#fontes-verificadas-2026-07-31)

## 0. Como usar esta apostila

**Leitura linear.** A seção 3 é o ponto de partida de verdade, e ela é uma lista de
perguntas, não de tecnologia. Da 4 à 8 cada seção acrescenta uma camada de decisão.
A 9 junta tudo num desenho.

**Revisão pontual.** Natureza das fontes na 5, mapa de ferramentas na 6, contratos
na 8, diagnóstico na 13.

**Pré-requisitos.** O módulo de SQL com JOINs e o de object storage. Você precisa
saber ler um relacionamento entre tabelas e saber o que é uma camada de dado bruto.

**Este módulo não executa nada, e isso é deliberado.** Não há laboratório, não há
comando, não há arquivo criado. Ele declara `lab: false` no `trilha.yml`. O
entregável é decisão registrada: um canvas de arquitetura e contratos de dados.

Isso não isenta o material de verificação. Toda afirmação sobre ferramenta aqui foi
conferida em documentação oficial, e a seção de fontes verificadas registra o que
foi conferido e o que não foi.

**A parte mais fácil de pular, e a que mais importa.** As tabelas de contrato da
seção 8 vêm em branco de propósito, para você preencher. Há um exemplo preenchido
ao lado de cada uma, como referência. Preencher é o exercício; copiar o exemplo não
é.

## 1. Objetivo pedagógico

Ao terminar este módulo, você consegue:

1. **Partir** de uma pergunta de negócio e chegar às fontes necessárias para
   respondê-la, sem começar pelo diagrama.
2. **Justificar** por que cada fonte exige uma abordagem de ingestão diferente,
   com critério técnico e não por preferência.
3. **Situar** as categorias de ferramenta de ingestão, e saber o que cada categoria
   resolve.
4. **Decidir** entre ferramenta pronta e código próprio a partir do tamanho e da
   capacidade do time.
5. **Escrever** um contrato de dados com schema, formato, partição, SLA e política
   de histórico.
6. **Desenhar** um canvas de arquitetura em camadas, com os pontos de decisão ainda
   abertos marcados como abertos.

## 2. Contexto de negócio

A startup fictícia de marketing e e-commerce da trilha gerencia campanhas pagas em
múltiplos canais, tem base de usuários crescendo, e precisa responder perguntas
semanais e diárias sobre retorno, conversão e risco de perda de cliente.

Dois fatos restringem tudo que vem depois:

**O time de dados é pequeno.** Toda decisão de arquitetura precisa ser sustentável
com poucos engenheiros e sem orçamento de empresa grande. Isso elimina soluções que
funcionam e ninguém consegue manter.

**As fontes são heterogêneas por natureza, não por acidente.** O cadastro está num
banco relacional, o custo de mídia está atrás de uma API de terceiro, e o
comportamento do usuário chega como fluxo de eventos. Nenhuma das três vai virar as
outras duas.

A pergunta deste módulo é: **como integrar fontes que se comportam de formas
diferentes, com contrato claro, de um jeito que um time pequeno mantém.**

**Sobre a escolha de stack aberta**

O projeto usa ferramentas de código aberto por portabilidade e para não ficar preso
a um fornecedor. A lógica é a mesma de qualquer arquitetura de dados madura:
camadas, contratos, qualidade. A ferramenta muda, os princípios não. O módulo de
cloud para dados mostra as equivalências gerenciadas de cada peça.

## 3. As perguntas que a arquitetura precisa responder

A arquitetura não começa pelo diagrama. Começa aqui.

**Diretoria**

- Qual campanha está gerando mais receita este mês?
- Quanto estamos gastando por real faturado em cada canal?
- Quantos clientes novos adquirimos esta semana, contra a semana passada?

**Crescimento e marketing**

- Qual a taxa de conversão do funil por campanha e por canal?
- Em qual etapa estamos perdendo mais usuários?
- Qual canal tem o menor custo de aquisição de cliente?

**Operações**

- Há queda anômala no volume de checkouts hoje?
- Quais usuários estão em risco de sair esta semana?

**Analytics**

- Como evolui o retorno mês a mês por canal?
- Qual o perfil dos usuários que chegam à compra, por campanha?

### 3.1 De cada pergunta para as fontes

| Pergunta | Quem pergunta | Fontes necessárias |
|---|---|---|
| Retorno por campanha | Diretoria e analytics | `costs` (API) + `events` (streaming) + `campaigns` (CDC) |
| Taxa de conversão do funil | Crescimento | `events` (streaming) |
| Clientes novos por semana | Diretoria | `users` (CDC) |
| Risco de perda de cliente | Operações | `crm` (CDC) + `events` (streaming) |
| Custo de aquisição por canal | Crescimento | `costs` (API) + `users` (CDC) + `events` (streaming) |
| Queda de checkouts hoje | Operações | `events` (streaming), exige baixa latência |
| Perfil de quem converte | Analytics | `users` (CDC) + `events` (streaming) + `campaigns` (CDC) |

**O ponto central**

Nenhuma dessas perguntas é respondível com uma fonte só. A arquitetura existe por
causa disso, e não por elegância: integrar fontes heterogêneas com contrato claro é
o trabalho.

**O equívoco comum**

Começar pelo desenho das camadas. O desenho é consequência. Quem desenha antes de
listar as perguntas produz uma arquitetura que responde perguntas que ninguém fez.

## 4. O modelo de dados, cinco entidades

### 4.1 As entidades e os campos que importam

**`users`**, de banco relacional por CDC

| Campo | Tipo | Descrição |
|---|---|---|
| `user_id` | UUID | Chave primária |
| `name` | VARCHAR | Nome |
| `email` | VARCHAR | E-mail, dado pessoal |
| `segment` | VARCHAR | Segmento comercial |
| `created_at` | TIMESTAMP | Criação |
| `updated_at` | TIMESTAMP | Última alteração |

**`campaigns`**, de banco relacional por CDC

| Campo | Tipo | Descrição |
|---|---|---|
| `campaign_id` | UUID | Chave primária |
| `name` | VARCHAR | Nome |
| `channel` | VARCHAR | Canal de mídia |
| `start_date` | DATE | Início |
| `end_date` | DATE | Término |
| `status` | VARCHAR | Situação |
| `updated_at` | TIMESTAMP | Última alteração |

**`events`**, de fluxo de eventos

| Campo | Tipo | Descrição |
|---|---|---|
| `event_id` | UUID | Chave primária |
| `user_id` | UUID | Referência a `users` |
| `campaign_id` | UUID | Referência a `campaigns` |
| `event_type` | VARCHAR | Etapa do funil |
| `occurred_at` | TIMESTAMP | Quando ocorreu |

**`costs`**, de API externa de mídia por lote

| Campo | Tipo | Descrição |
|---|---|---|
| `cost_id` | UUID | Chave primária |
| `campaign_id` | UUID | Referência a `campaigns` |
| `date` | DATE | Data de referência |
| `channel` | VARCHAR | Canal |
| `amount` | DECIMAL | Valor investido |
| `currency` | VARCHAR | Moeda |

**`crm`**, de banco relacional por CDC

| Campo | Tipo | Descrição |
|---|---|---|
| `crm_id` | UUID | Chave primária |
| `user_id` | UUID | Referência a `users` |
| `lifecycle_stage` | VARCHAR | Estágio do ciclo de vida |
| `churn_risk_score` | FLOAT | Score de risco, de 0 a 1 |
| `last_contact_at` | TIMESTAMP | Último contato |
| `updated_at` | TIMESTAMP | Última alteração |

**Um aviso que precisa ser dado aqui, não depois**

`email` é dado pessoal. A decisão sobre mascarar, restringir acesso ou não promover
essa coluna para as camadas de consumo é tomada **no contrato**, na seção 8, e não
quando alguém reclamar. O módulo de governança trata do assunto em profundidade; o
que este módulo cobra é que a coluna esteja marcada.

### 4.2 O tecido que conecta

```
users (user_id)
    |
    |--- events (user_id, campaign_id)
    |--- crm (user_id)

campaigns (campaign_id)
    |
    |--- events (campaign_id)
    |--- costs (campaign_id)
```

Duas chaves sustentam o modelo inteiro. `user_id` une `users`, `events` e `crm`.
`campaign_id` une `campaigns`, `costs` e `events`.

`events` é a entidade central: é a única que conecta usuário, campanha e funil no
mesmo lugar. Isso a torna a mais valiosa e a mais volumosa, e as duas coisas juntas
explicam por que ela é a que exige mais cuidado de particionamento, que é o assunto
do módulo anterior.

## 5. A natureza de cada fonte

### 5.1 Banco relacional, por CDC

**Entidades:** `users`, `campaigns`, `crm`.

**Por que CDC e não lote diário**

Essas entidades são dado mestre que muda ao longo do dia. Um usuário troca de
segmento, uma campanha muda de situação, um score de risco é recalculado várias
vezes.

Com lote diário você captura o estado final do dia e **perde o caminho**. Com CDC
você captura cada alteração, com momento e tipo de operação. Isso permite três
coisas que o lote não permite:

- reconstruir o estado de um registro em qualquer ponto do tempo;
- detectar anomalia de comportamento, como uma campanha que mudou de situação três
  vezes em uma hora;
- alimentar o que vem depois sem esperar a virada do dia.

| Atributo | Valor |
|---|---|
| Frequência | Contínua, ao longo do dia |
| SLA proposto no bruto | Disponível em até 30 minutos após a alteração |

### 5.2 API externa, por lote

**Entidade:** `costs`.

**Por que lote e não CDC nem streaming**

Custo de campanha em API de mídia é imutável por data: o custo do dia 10 é uma foto
do que foi gasto naquele dia. Não há alteração de registro para rastrear.

Somado a isso, API de terceiro tem limite de chamadas e, às vezes, custo por
chamada. Extração contínua seria mais caro sem ganho nenhum, porque o dado muda uma
vez por dia.

| Atributo | Valor |
|---|---|
| Frequência | Uma extração por dia |
| SLA proposto no bruto | Dado do dia anterior disponível até as 8h |

**O equívoco comum**

Tratar dado imutável com a mesma máquina do dado mutável. Aqui a simplicidade é a
decisão certa, e escolher a ferramenta mais poderosa é escolher errado.

### 5.3 Fluxo de eventos, por streaming

**Entidade:** `events`.

**Por que streaming e não lote**

Evento de funil tem valor na latência. Detectar às 14h que os checkouts caíram é
acionável: dá tempo de investigar. Ver no relatório de amanhã não é a mesma coisa.

Além disso, evento é append-only: cada um é imutável depois de ocorrer. Não há
atualização nem exclusão, só inserção. Isso torna o streaming natural, porque não
existe a complexidade de mesclar versões.

| Atributo | Valor |
|---|---|
| Frequência | Contínua, por evento |
| SLA proposto no bruto | Latência máxima de 5 minutos do evento ao bruto |

**O que este módulo deixa claro sobre escopo**

O fluxo de eventos é **projetado** aqui, com contrato e lugar reservado na
arquitetura. A implementação é do módulo de streaming com Kafka. Reservar o lugar
sem implementar é decisão, não pendência esquecida.

## 6. Categorias de ferramenta de ingestão

O objetivo desta seção não é escolher, é abrir o mapa. A escolha é o entregável do
exercício 3.

**Uma advertência que vale mais que as tabelas.** Informação sobre ferramenta
envelhece rápido, e modelo de cobrança de fornecedor muda sem aviso. As tabelas
abaixo foram conferidas em 2026-07-31, e a seção de fontes verificadas diz o que
foi conferido em documentação e o que não foi. Antes de decidir, confira na data da
sua decisão.

### 6.1 Para CDC

| Ferramenta | Natureza | Observação |
|---|---|---|
| Debezium | Aberta | Padrão de mercado para CDC em bancos relacionais |
| Airbyte | Aberta e gerenciada | Tem CDC por leitura de log, e é mais simples de operar |
| Fivetran | Gerenciada | Configuração fácil, cobrança por volume |
| AWS DMS | Gerenciada | Boa opção se o ambiente já está na AWS |
| Kafka Connect JDBC | Aberta | Consulta periódica, não é CDC de log |

**Duas correções que material antigo repete**

A primeira: **Debezium não exige Kafka.** É comum ler que ele "requer Kafka", e
isso descreve apenas um dos três modos de execução. O Debezium Server transmite as
mudanças direto para um destino sem Kafka Connect, e o engine embutido roda dentro
da sua aplicação, sem Kafka nenhum. Isso muda a conta de complexidade de forma
relevante para um time pequeno.

A segunda: **o Kafka Connect JDBC não detecta exclusão.** Os modos incrementais dele
detectam linha nova ou modificada, e exclusão não está entre as capacidades
documentadas. Se a sua entidade sofre `DELETE` e você precisa saber, essa
ferramenta não resolve, e o sintoma é um registro que existe no destino para sempre.

### 6.2 Para API em lote

| Ferramenta | Natureza | Observação |
|---|---|---|
| Airbyte | Aberta e gerenciada | Tem conectores prontos para plataformas de mídia |
| Fivetran | Gerenciada | Conectores prontos, cobrança por volume |
| Meltano | Aberta | Construída sobre a especificação Singer |
| Singer | Especificação aberta | Define extratores e carregadores como programas separados |
| Código próprio | Sua | Controle máximo, e custo de manutenção máximo |

**Outra correção.** É comum ler que o Singer é "a base do Meltano e do Airbyte". Só
metade está certa. O Meltano é construído sobre o Singer. O **Airbyte não é**: ele
tem protocolo próprio, e a própria documentação da empresa explica que a decisão
foi deliberada. O Airbyte é compatível com extratores Singer selecionados, o que é
diferente de ser construído sobre eles.

### 6.3 Para fluxo de eventos

| Ferramenta | Natureza | Observação |
|---|---|---|
| Kafka Connect | Aberta | Conectores de entrada e de saída, ecossistema amplo |
| Confluent Platform | Gerenciada | Kafka com operação simplificada |
| Flink | Aberta | Processamento com estado, janelas e junções em fluxo |
| Spark Structured Streaming | Aberta | Boa opção para time com histórico em Spark |

## 7. Construir ou comprar

Para cada fonte, a pergunta não é qual ferramenta é mais poderosa. É qual ferramenta
o seu time sustenta.

### 7.1 Os critérios

| Critério | Favorece ferramenta pronta | Favorece código próprio |
|---|---|---|
| Número de fontes | Muitas | Poucas e muito específicas |
| Estabilidade do contrato da fonte | Instável, muda com frequência | Estável |
| Capacidade de manutenção do time | Pequeno, sem plantão | Com folga para manter |
| Restrição de orçamento | Licença é aceitável | Sem verba para licença |
| Existe conector pronto | Sim | Não existe adequado |
| Complexidade da regra de negócio | Baixa | Alta, com regra embutida |

### 7.2 O critério que decide de verdade

Ferramenta pronta reduz o custo inicial de engenharia e cria dependência de
fornecedor mais licença recorrente. Código próprio tem custo de manutenção
invisível.

A pergunta mais honesta que existe para essa decisão: **quem mantém isso às duas da
manhã, quando quebrar?** Se a resposta é uma pessoa específica, e ela é a mesma que
escreveu, você não tem uma solução, tem um risco com data de validade.

## 8. Contratos de dados

Um contrato de dados registra o que quem produz promete a quem consome. Sem ele, a
mudança de schema na origem chega como incidente.

Cinco atributos cobrem o essencial:

| Atributo | Pergunta que responde |
|---|---|
| Schema | Quais colunas e tipos, e o que acontece quando mudam |
| Formato de destino | Como o dado é gravado na camada bruta |
| Partição | Como o dado é organizado fisicamente |
| SLA | Em quanto tempo o dado precisa estar disponível |
| Histórico | O que é guardado, por quanto tempo, e o que é descartado |

### 8.1 CDC de banco relacional: `users`, `campaigns`, `crm`

Preencha:

| Atributo | Valor |
|---|---|
| Schema | |
| Formato de destino | |
| Partição | |
| SLA | |
| Histórico | |

Exemplo de referência, para você comparar depois de preencher:

| Atributo | Exemplo |
|---|---|
| Schema | Colunas da seção 4.1 mais as de controle de CDC: operação e momento da mudança. `email` marcado como dado pessoal, não promovido para consumo |
| Formato de destino | Parquet na camada bruta |
| Partição | Data de ingestão, não data de negócio, porque a mesma linha pode chegar várias vezes |
| SLA | 30 minutos entre a alteração na origem e a disponibilidade no bruto |
| Histórico | Todas as versões preservadas no bruto; a camada curada mantém a última versão por chave |

A escolha de particionar por data de **ingestão** e não de negócio é a mais sutil
das cinco, e é a que mais gera retrabalho quando errada. Em CDC, a mesma entidade
volta com alterações; agrupar por data de ingestão mantém o carregamento
idempotente e permite reprocessar um dia sem tocar os outros.

### 8.2 API de mídia: `costs`

Preencha:

| Atributo | Valor |
|---|---|
| Schema | |
| Formato de destino | |
| Partição | |
| SLA | |
| Histórico | |

Exemplo de referência:

| Atributo | Exemplo |
|---|---|
| Schema | Colunas da seção 4.1. Moeda obrigatória, porque valor sem moeda não é valor |
| Formato de destino | Parquet na camada bruta |
| Partição | Data de referência do custo, que aqui coincide com a extração |
| SLA | Dado do dia anterior disponível até as 8h |
| Histórico | Reextração do mesmo dia sobrescreve a partição, porque a origem é imutável por data |

### 8.3 Fluxo de eventos: `events`, contrato projetado

Preencha:

| Atributo | Valor |
|---|---|
| Schema | |
| Tópico | |
| Formato de destino | |
| Partição | |
| SLA | |
| Histórico | |

Exemplo de referência:

| Atributo | Exemplo |
|---|---|
| Schema | Colunas da seção 4.1, com schema registrado e evolução compatível para trás |
| Tópico | Um por domínio de evento, com chave por `user_id` para preservar ordem por usuário |
| Formato de destino | Parquet na camada bruta, com compactação periódica |
| Partição | Data do evento, com atenção à partição do dia corrente recebendo escrita concorrente |
| SLA | 5 minutos do evento ao bruto |
| Histórico | Append-only, sem atualização nem exclusão |

A escolha de chave do tópico não é detalhe: ela decide a ordem. Eventos do mesmo
usuário na mesma partição chegam em ordem; espalhados, não. O módulo de streaming
com Kafka trata disso, e a decisão precisa ser tomada aqui, no contrato.

## 9. O architecture canvas

Um roteiro para desenhar, e a validação que diz se o desenho está certo.

**Passo 1, as fontes.** No canto esquerdo, as três fontes, cada uma com a sua
natureza anotada: CDC, lote, fluxo.

**Passo 2, a camada de ingestão.** Para cada fonte, um espaço para a ferramenta,
marcado como aberto. A escolha é o exercício 3, e marcar como aberto é melhor que
escolher errado agora.

**Passo 3, as camadas de armazenamento.** Bruto, curado e consumo, com o que cada
uma garante:

| Camada | O que garante |
|---|---|
| Bruto | Fidelidade à origem, imutável, particionado por data de ingestão |
| Curado | Deduplicado, junções aplicadas, schema confiável |
| Consumo | Conjuntos que respondem as perguntas da seção 3 |

**Passo 4, o consumo.** No canto direito, quem lê: painéis, análise pontual,
ativação de campanha.

**Passo 5, a validação, e é ela que importa.** Percorra o canvas **de trás para
frente**: pegue uma pergunta da seção 3 e trace o caminho até a fonte. Se o caminho
existe e não tem lacuna, o canvas atende aquela pergunta. Repita com três
perguntas de stakeholders diferentes.

Canvas que não passa nesse teste é bonito e inútil.

## 10. Exercícios e entregáveis

**Exercício 1: de pergunta para fonte**

Objetivo: praticar o rastreio reverso, da pergunta até a origem do dado.

Contexto: as perguntas da seção 3 e o modelo da seção 4.

Entregável: três perguntas, de stakeholders diferentes, cada uma com as entidades
necessárias, as fontes de ingestão de cada entidade, e a chave que conecta as
entidades.

Exemplo do formato, não use como resposta:

| Pergunta | Entidades | Fontes | Chave de conexão |
|---|---|---|---|
| Qual canal tem o menor custo de aquisição? | `costs`, `users`, `events` | Lote, CDC, fluxo | `campaign_id` entre custo e evento, `user_id` entre usuário e evento |

Critério: o caminho fonte, entidade, pergunta precisa ser traçável sem lacuna.

**Exercício 2: contratos preenchidos**

Objetivo: transformar decisão em documento que outra pessoa lê.

Contexto: as três tabelas da seção 8.

Entregável: os três contratos preenchidos com as suas escolhas, **antes** de olhar
os exemplos de referência. Depois compare, e escreva uma frase para cada divergência
explicando por que a sua escolha é melhor ou pior. Divergir é aceitável; não
perceber a divergência não é.

**Exercício 3: a proposta de ferramenta**

Objetivo: decidir com critério explícito.

Contexto: o mapa da seção 6 e os critérios da seção 7.

Entregável: uma ferramenta proposta por tipo de ingestão, com justificativa em
custo, complexidade e manutenção.

| Ingestão | Ferramenta proposta | Justificativa |
|---|---|---|
| CDC | | |
| API em lote | | |
| Fluxo de eventos | | |

Para cada uma, responda também: quem mantém às duas da manhã?

**Exercício 4: o canvas**

Objetivo: desenhar e validar.

Entregável: o canvas da seção 9 desenhado, mais o resultado do passo 5 para três
perguntas. Se alguma não fechou, isso é o achado mais valioso do exercício.
Registre a lacuna em vez de escondê-la.

## 11. Mini-desafio com solução

**Enunciado**

A diretoria pede um painel de retorno por campanha, com atualização diária. Um
engenheiro propõe: uma extração noturna em lote das três tabelas do banco, uma
extração da API de custos, e nada de streaming, porque "o painel é diário mesmo".

Avalie a proposta.

**Dicas**

- A proposta atende o pedido literal. A pergunta é o que ela custa depois.
- Duas perguntas da seção 3 morrem nessa arquitetura. Quais?
- "Diário mesmo" é uma afirmação sobre hoje.

**Gabarito comentado**

Aceito em parte, e a parte que recuso é a que vai doer.

O que está certo: para um painel diário de retorno, lote noturno das três tabelas
mais a API de custos **responde a pergunta**. Streaming não é requisito para retorno
mensal ou diário, e montar Kafka para isso é complexidade sem retorno. Quem propôs
acertou o recorte do pedido.

O que está errado é o efeito colateral, e ele tem duas faces.

A primeira: lote noturno em `crm` e `users` **destrói o histórico de alterações**. O
score de risco é recalculado várias vezes ao dia; o lote captura o último valor.
A pergunta "quais usuários estão em risco esta semana" ainda funciona, mas "por que
esse usuário entrou em risco" deixa de ter resposta, para sempre, porque o caminho
não foi gravado. Dado histórico não é recuperável depois.

A segunda: "queda anômala no volume de checkouts hoje" fica impossível por
construção. Não é lentidão, é ausência: o dado do dia só existe amanhã.

O que eu proporia: lote para `costs`, porque a fonte é imutável por data e lote é a
escolha certa, não a preguiçosa. CDC para `crm` e `users`, porque o custo de
capturar a alteração é baixo hoje e o custo de não ter capturado é infinito depois.
E o lugar do fluxo de eventos reservado no canvas, com contrato escrito e
implementação adiada, exatamente como a seção 5.3 faz.

**Interpretação**

A resposta fraca recusa a proposta inteira e manda montar streaming. A resposta boa
separa as três fontes e decide cada uma pelo seu comportamento. A excelente percebe
que a decisão de lote em CDC é a única das três que **não tem volta**, e usa isso
como critério de prioridade.

## 12. Rubrica de validação da aprendizagem

| Critério | Insuficiente | Suficiente | Excelente |
|---|---|---|---|
| Ponto de partida | Começa pelo diagrama | Começa pelas perguntas de negócio | Recusa desenhar antes de saber quem pergunta o quê |
| Natureza da fonte | Trata as três igual | Justifica CDC, lote e fluxo por comportamento do dado | Identifica qual decisão é irreversível |
| Modelo de dados | Lista tabelas | Explica as chaves que conectam | Aponta a entidade central e o que isso implica |
| Contratos | Deixa em branco | Preenche os cinco atributos | Justifica partição por data de ingestão em CDC |
| Ferramentas | Escolhe a mais conhecida | Usa os critérios da seção 7 | Responde quem mantém às duas da manhã |
| Dado pessoal | Não menciona | Marca a coluna sensível | Decide o tratamento já no contrato |
| Canvas | Desenha e entrega | Valida de trás para frente | Registra a lacuna que a validação achou |
| Honestidade técnica | Repete o que leu | Cita fonte e data | Sabe que informação de ferramenta envelhece |

Checklist para a call:

- [ ] Perguntas mapeadas para fontes, com caminho traçável.
- [ ] Natureza de cada fonte justificada por comportamento do dado.
- [ ] Os três contratos preenchidos, com partição justificada.
- [ ] Proposta de ferramenta por tipo, com o critério de manutenção respondido.
- [ ] Canvas desenhado e validado de trás para frente.
- [ ] Coluna de dado pessoal marcada e com tratamento decidido.

## 13. Erros comuns e como corrigir

**Começar pelo diagrama**

Sintoma: uma arquitetura bonita que ninguém usa, ou que não responde o que foi
pedido.

Causa: o desenho veio antes das perguntas.

Correção: listar as perguntas por stakeholder, e só então desenhar. A validação de
trás para frente da seção 9 existe para pegar isso.

**Lote em dado que muda ao longo do dia**

Sintoma: dá para saber o estado atual e não dá para saber como ele chegou lá.

Causa: lote captura estado, CDC captura mudança.

Correção: CDC nas entidades de dado mestre. Este erro é o mais caro do módulo,
porque o histórico não capturado não é recuperável depois.

**Ferramenta escolhida pela capacidade e não pela manutenção**

Sintoma: pipeline que funciona e que ninguém entende quando quebra.

Causa: a decisão avaliou poder e não sustentação.

Correção: os critérios da seção 7, e a pergunta das duas da manhã.

**Contrato sem política de histórico**

Sintoma: ninguém sabe se pode reprocessar um dia, nem o que acontece se
reprocessar.

Causa: os quatro primeiros atributos do contrato foram preenchidos e o quinto foi
esquecido.

Correção: definir o que é sobrescrito e o que é acrescentado, por fonte. Origem
imutável por data pode sobrescrever a partição; CDC não pode.

**Particionar CDC por data de negócio**

Sintoma: reprocessar um dia mexe em partições de outros dias, e o carregamento
deixa de ser idempotente.

Causa: em CDC a mesma entidade volta com alterações, e a data de negócio dela não
muda.

Correção: particionar o bruto por data de ingestão. A data de negócio é coluna, e a
camada curada usa ela.

**Dado pessoal descoberto na camada de consumo**

Sintoma: alguém encontra e-mail num painel.

Causa: a coluna atravessou as camadas porque ninguém decidiu o contrário.

Correção: marcar no contrato, na seção 8, e decidir ali se ela é mascarada ou não
promovida.

**Achar que informação de ferramenta é estável**

Sintoma: uma decisão baseada em texto de dois anos atrás.

Causa: material sobre ferramenta envelhece mais rápido que material sobre conceito.

Correção: conferir na documentação oficial na data da decisão. Esta apostila mesmo
corrigiu duas afirmações desse tipo, sobre o Debezium e sobre o Airbyte, e as duas
estavam em material anterior.

## 14. Plano de continuidade

**Antes da próxima call**

Faça os exercícios 2 e 3. O contrato preenchido é o entregável que mais se parece
com trabalho real.

**O que estudar em seguida, dentro da trilha**

O módulo de CDC implementa o que aqui é contrato. O de orquestração com Airflow
coloca a sequência de pé. O de streaming com Kafka ocupa o lugar que este módulo
reservou.

Vale reler o módulo de particionamento com a seção 8 desta apostila em mão: a
decisão de particionar por data de ingestão em CDC é exatamente uma decisão de
partição, e o custo dela é o daquele módulo.

**O que aprofundar por conta**

Escreva o contrato de uma fonte do seu trabalho, ou de uma API pública qualquer.
Cinco atributos, uma página. O exercício ensina mais que ler sobre contratos.

**O que não perseguir agora**

Catálogo de dados, linhagem automatizada e ferramenta de contrato como código. Os
três são úteis e chegam depois de existir contrato escrito à mão. Ferramenta de
governança sobre processo inexistente não governa nada.

## 15. Glossário

| Termo | Significado |
|---|---|
| Append-only | Dado que só recebe inserção, sem atualização nem exclusão |
| Camada bruta | Primeira camada, fiel à origem e imutável |
| Camada curada | Camada deduplicada, com junções e schema confiável |
| Camada de consumo | Conjuntos prontos para responder perguntas de negócio |
| Canvas de arquitetura | Desenho das fontes, camadas e consumidores, com decisões abertas marcadas |
| CDC | Captura de mudança de dado, registra cada alteração com momento e operação |
| Contrato de dados | Acordo entre quem produz e quem consome sobre schema, formato, partição, SLA e histórico |
| Dado mestre | Entidade de cadastro que muda ao longo do tempo, como usuário ou campanha |
| Extração em lote | Coleta periódica de um recorte do dado, tipicamente por data |
| Idempotente | Operação que, repetida, produz o mesmo resultado |
| SLA | Prazo acordado entre o dado existir na origem e estar disponível |
| Streaming | Processamento contínuo, evento por evento |
| Tópico | Canal nomeado de um sistema de fluxo de eventos |

## Referências

Documentação oficial, consultada em 2026-07-31:

- Arquitetura e modos de execução do Debezium: https://debezium.io/documentation/reference/stable/architecture.html
- Engine embutido do Debezium: https://debezium.io/documentation/reference/stable/development/engine.html
- Conector JDBC de origem, visão geral e limitações: https://docs.confluent.io/kafka-connectors/jdbc/current/source-connector/overview.html
- Especificação Singer: https://www.singer.io/
- Por que o Airbyte não é construído sobre o Singer, pela própria empresa: https://airbyte.com/blog/airbyte-vs-singer-why-airbyte-is-not-built-on-top-of-singer

## Fontes verificadas (2026-07-31)

- O Debezium **não** exige Apache Kafka. Além do modo baseado em Kafka Connect,
  existem o Debezium Server, que transmite as mudanças direto para um destino sem
  Kafka Connect, e o engine embutido, que roda dentro da aplicação sem cluster
  Kafka. A versão anterior desta apostila afirmava que o Debezium "requer Kafka", e
  isso descreve apenas um dos modos.
  https://debezium.io/documentation/reference/stable/development/engine.html
- O conector JDBC de origem detecta linha nova ou modificada pelos modos
  incrementais, e a detecção de exclusão não aparece entre as capacidades
  documentadas. A afirmação de que ele não é CDC de log e não captura exclusão se
  sustenta.
  https://docs.confluent.io/kafka-connectors/jdbc/current/source-connector/overview.html
- O Airbyte **não** é construído sobre o protocolo Singer. A própria empresa
  publicou que a decisão foi deliberada, e que a compatibilidade com extratores
  Singer selecionados é diferente de ser construída sobre eles. O Meltano, sim, é
  construído sobre o Singer. A versão anterior desta apostila tratava o Singer como
  base dos dois.
  https://airbyte.com/blog/airbyte-vs-singer-why-airbyte-is-not-built-on-top-of-singer
- Os modelos de cobrança citados na seção 6, como cobrança por volume em
  ferramentas gerenciadas, **não** foram conferidos em página de preço nesta data.
  Eles estão descritos de forma genérica de propósito, e o texto pede que você
  confira na data da sua decisão. Preço de fornecedor muda sem aviso.
- Os SLA propostos na seção 5, de 30 minutos para CDC, 8h para o lote diário e 5
  minutos para o fluxo de eventos, são **propostas de projeto** deste material, não
  números medidos nem garantia de ferramenta. Eles existem para serem discutidos e
  ajustados ao caso real.
- Este módulo não tem laboratório e não executa comando, por decisão registrada no
  `trilha.yml` com `lab: false`. Nenhum bloco de código desta apostila é executável,
  e nenhum declara nível acima de 1.
