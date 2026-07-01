---
title: Sessão 11 — Kafka na Prática (Producers e Consumers)
date: 2026-06-29
type: apostila
status: active
tags: [kafka, streaming, engenharia-de-dados, mentoria]
---

# Sessão 11 — Kafka na Prática

---

## 1. Arquitetura real do Kafka

Kafka é um **log de eventos distribuído e durável**. Diferente de uma fila tradicional (que remove a mensagem após o consumo), o Kafka guarda as mensagens por tempo ou tamanho configurável. Qualquer consumer pode ler a qualquer momento, do offset que quiser.

O diagrama abaixo mostra uma arquitetura real com todos os componentes que você vai encontrar em produção:

![Arquitetura Kafka](kafka-arquitetura.drawio.png)

### O que cada zona significa

**Producers** — quem escreve eventos no Kafka.
- Apps e APIs enviam eventos de clique, sessão, navegação.
- O PostgreSQL é lido pelo **Debezium**, que captura cada mudança no banco via WAL (Write-Ahead Log) e publica como evento no Kafka. Isso é CDC (Change Data Capture).
- Um Python Producer pode enviar eventos de um pipeline batch.

**Apache Kafka Cluster** — o coração do sistema.
- Organizado em **topics** (canais de mensagens nomeados).
- Cada topic tem N **partições**: subdivisões paralelas que permitem escalar.
- Dentro de cada partição as mensagens têm um número sequencial chamado **offset**.
- O **Schema Registry** é um serviço que fica dentro do cluster e armazena os schemas das mensagens (Avro ou JSON Schema). Producers registram, consumers validam.
- O topic `eventos-mkt.dlq` é a **Dead Letter Queue**: onde mensagens com erro permanente são descartadas sem travar a partição principal.

**Consumers** — quem lê e processa os eventos.
- Um **Consumer Group** distribui as partições entre os consumers do grupo.
- **Kafka Connect** é um framework de integração que conecta Kafka a sistemas externos (MinIO, S3, banco de dados) sem escrever código de consumer.
- **Stream Processor** (Flink ou Spark Streaming) processa eventos em janelas de tempo.
- O **DLQ Consumer** lê o topic de dead letter, tenta corrigir, reencaminha ou notifica.

**Destinos** — onde os dados chegam após o processamento.
- MinIO / S3 como Data Lake em Bronze (raw), Silver (limpo), Gold (agregado).
- Trino / Spark SQL para consultas analíticas.
- Grafana para dashboards em tempo real.
- Alertas (PagerDuty, Slack) para erros e anomalias.

**Monitoramento** — Prometheus coleta métricas JMX do broker. Grafana exibe lag, throughput e latência. kafka-ui permite inspecionar topics, consumer groups e offsets via interface web.

### Cinco conceitos que você precisa saber de cor

| Conceito | O que é | Analogia |
|---|---|---|
| Topic | Canal nomeado de mensagens | Pasta de e-mails por assunto |
| Partição | Subdivide o topic para paralelismo | Caixas de entrada independentes dentro da pasta |
| Offset | Número sequencial da mensagem na partição | Número do e-mail dentro de uma caixa |
| Consumer Group | Grupo que divide as partições entre si | Time de atendentes, cada um com sua caixa |
| Broker | Servidor que armazena e replica as mensagens | Servidor de e-mail |

---

## 2. Subir o ambiente

A stack desta sessão é leve: apenas Kafka + kafka-ui (~1,5 GB de RAM).

```bash
# A partir da raiz do repositório clonado (mentorias/)
cd engenharia_de_dados/arquitetura/sessoes/sessao-11-kafka-handson/infrastructure
docker compose up -d
docker compose ps
```

Aguardar ambos os containers com status `running`.

Acessar o kafka-ui em: http://localhost:8080

O cluster "local" deve aparecer como "online". Explore a interface antes de continuar.

### Como funciona o Docker Compose desta sessão

O Kafka roda em modo **KRaft** (sem Zookeeper). Dois listeners estão configurados:
- `INTERNAL://kafka:29092` — usado pelo kafka-ui (dentro da rede Docker).
- `EXTERNAL://localhost:9092` — usado pelos scripts Python no host.

Isso evita o problema clássico de conectividade em que o Kafka anuncia o endereço errado para clientes externos.

---

## 3. Instalar dependências Python

```bash
# A partir da raiz do repositório clonado (mentorias/)
cd engenharia_de_dados/arquitetura/sessoes/sessao-11-kafka-handson/scripts
python3 -m venv .venv
source .venv/bin/activate      # Linux / Mac
# .venv\Scripts\activate       # Windows PowerShell
pip install -r requirements.txt
```

A única dependência é `confluent-kafka==2.6.0`, a biblioteca padrão de mercado para Python + Kafka.

---

## 4. Producer básico — como uma mensagem chega ao Kafka

**Antes de codar:** entenda o caminho de uma mensagem.

![Fluxo do Producer](d1-fluxo-producer.drawio.png)

A função `produce()` é **assíncrona**: ela coloca a mensagem na fila interna do producer e retorna imediatamente. A confirmação do broker chega depois, via callback. O `flush()` no final aguarda todas as confirmações pendentes.

**Arquivo:** `producers/01_producer_basico.py`

```bash
python producers/01_producer_basico.py
```

Observe no kafka-ui: Topics > `mentoria-basico` > Messages. As mensagens aparecem com topic, partição, offset e chave.

**Agora você faz:** mude o range de 10 para 50 e rode novamente. Veja os offsets aumentando.

### Configurações de confiabilidade do producer

| Config | Valor | O que faz |
|---|---|---|
| `acks` | `all` | O broker só confirma quando todos os ISR gravaram. Sem perda mesmo com falha. |
| `enable.idempotence` | `True` | O broker descarta duplicatas se o producer reenviar. Automático desde Kafka 3.0. |
| `retries` | `int.max` | Retenta indefinidamente em falhas transientes. |

```python
producer = Producer({
    "bootstrap.servers": "localhost:9092",
    "acks": "all",
    "enable.idempotence": True,
})
```

Essa combinação é **producer idempotente**: mesma mensagem entregue exatamente uma vez, mesmo com retries.

---

## 5. Producer de eventos de marketing — chaves e partições

**Antes de codar:** por que usar uma chave na mensagem?

O Kafka decide a partição destino com: `partição = hash(chave) % número_de_partições`

- **Com chave:** todos os eventos do mesmo `session_id` vão para a mesma partição. Isso garante **ordenação por sessão**: a sequência `pageview → click → conversion` chega na ordem certa para o consumer.
- **Sem chave:** distribuição round-robin entre as partições. Sem garantia de ordem entre eventos da mesma sessão.

**Hot partition — o problema mais comum em produção:**

Se 80% dos eventos vierem de um único `session_id` (ex: um bot), uma partição ficará sobrecarregada e o consumer correspondente acumulará lag.

Solução: adicionar entropia à chave quando a ordenação não é crítica:
```python
key = f"{session_id}_{random.randint(0, 3)}"  # distribui em ate 4 particoes
```

**Arquivo:** `producers/02_producer_eventos_mkt.py`

```bash
python producers/02_producer_eventos_mkt.py
python producers/02_producer_eventos_mkt.py --total 60 --intervalo 0.3
```

Observe no kafka-ui: Topic > `mentoria-eventos-mkt` > Partitions. Veja como os eventos se distribuem entre as 3 partições.

**Pergunta:** abra dois eventos com o mesmo `session_id` no kafka-ui. Eles estão na mesma partição?

**Agora você faz:** adicione um campo `country` com valor aleatório no JSON de evento e rode novamente.

---

## 6. Consumer básico — offsets, grupos e semântica de entrega

**Antes de codar:** o modelo de entrega do Kafka.

Ao contrário de uma fila tradicional, o Kafka **não remove mensagens depois do consumo**. O que muda é o **offset commitado** pelo consumer group. Isso define a semântica de entrega:

| Semântica | Como funciona | Risco |
|---|---|---|
| **At-most-once** | Commita o offset ANTES de processar | Pode perder mensagens se cair no meio |
| **At-least-once** | Commita o offset APÓS processar | Pode reprocessar se cair antes do commit |
| **Exactly-once** | Transações atômicas (producer + consumer) | Mais lento, mais complexo |

O padrão em pipelines de dados é **at-least-once**: o processamento deve ser **idempotente** (processar duas vezes o mesmo evento tem o mesmo resultado que processar uma vez).

**Arquivo:** `consumers/01_consumer_basico.py`

Abrir um segundo terminal:
```bash
cd sessions/sessao-11-kafka-handson/scripts
source .venv/bin/activate
python consumers/01_consumer_basico.py
```

O consumer usa `auto.offset.reset: earliest`: lê tudo desde a primeira mensagem disponível no topic, mesmo mensagens antigas.

**Teste:** pare o consumer, mande mais 20 mensagens com o producer, rode o consumer novamente. Ele lê as mensagens que ficaram pendentes.

**Pergunta:** o que acontece se você mudar `earliest` para `latest` e subir o consumer antes de mandar mensagens?

---

## 7. Consumer Group — paralelismo e rebalanceamento

**Antes de codar:** como o Kafka distribui partições em um grupo.

Regra: **cada partição só pode ser atribuída a um consumer do grupo por vez**.

![Distribuição de Partições por Consumer Group](d2-consumer-group.drawio.png)

Quando um consumer entra ou sai do grupo, o Kafka executa um **rebalanceamento**: redistribui as partições entre os consumers ativos. Durante o rebalanceamento, o consumo é pausado brevemente.

**Arquivo:** `consumers/02_consumer_grupo.py`

Abrir **três terminais**:
```bash
# Terminal 1
python consumers/02_consumer_grupo.py --nome A

# Terminal 2
python consumers/02_consumer_grupo.py --nome B

# Terminal 3 (producer)
python producers/02_producer_eventos_mkt.py --total 100 --intervalo 0.1
```

Observe os logs `[REBALANCE]` quando um consumer entra ou sai.

Encerre o consumer B (Ctrl+C) e veja o consumer A assumir todas as partições.

**Observe no kafka-ui:** Consumer Groups > `grupo-analise-mkt` > Members.

### Consumer Lag — a métrica mais importante

**Consumer lag** é a diferença entre o último offset produzido e o último offset commitado pelo grupo.

```
Lag = end_offset_do_broker - offset_commitado_pelo_consumer
```

Ver o lag via CLI:
```bash
docker exec mentoria-s11-kafka /opt/kafka/bin/kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --describe \
  --group grupo-analise-mkt
```

Como interpretar:

| Situação | Lag | Ação |
|---|---|---|
| Lag = 0 | Consumer em dia | Normal |
| Lag pequeno e estável | Pico passageiro | Monitorar |
| Lag crescendo continuamente | Consumer não aguenta o throughput | Adicionar consumer ou otimizar processamento |
| Lag em uma partição específica | Hot partition ou consumer lento nessa partição | Investigar distribuição de chaves |

Em produção: configurar alerta na **taxa de crescimento do lag**, não apenas no valor absoluto.

---

## 8. Consumer com Seek — leitura a partir de offset específico

**Antes de codar:** dois modos de consumo no Kafka.

| Modo | API | Quando usar |
|---|---|---|
| **subscribe()** | Participa do consumer group, recebe partições automaticamente | Produção, pipelines normais |
| **assign() + seek()** | Controle manual da partição e do offset, sem consumer group | Debug, reprocessamento, auditoria |

O `seek()` posiciona o cursor em qualquer ponto do log. Não afeta o consumer group nem o offset commitado.

**Arquivo:** `consumers/03_consumer_seek.py`

```bash
# Le a particao 0 desde o offset 0
python consumers/03_consumer_seek.py

# Le a particao 1 desde o offset 5
python consumers/03_consumer_seek.py --particao 1 --offset 5
```

**Agora você faz:** descubra no kafka-ui o offset da última mensagem na partição 2 e faça um seek a partir dela.

**Caso de uso real:** um pipeline falhou silenciosamente e processou os offsets 100-150 com dados corrompidos. Com seek, você reprocessa exatamente esse intervalo sem tocar nos outros.

---

## 9. Consumer com commit manual — at-least-once garantido

**Antes de codar:** o que é commit de offset.

Por padrão, o Kafka commita os offsets automaticamente a cada 5 segundos (`enable.auto.commit: True`). Se o processo cair nesse intervalo, mensagens processadas mas não commitadas são reprocessadas.

O commit manual dá controle explícito sobre quando o offset avança:

![Semântica at-least-once](d3-atleastonce.drawio.png)

Exigência: o processamento deve ser idempotente. Processar o evento duas vezes não pode criar duplicatas no destino.

**Arquivo:** `consumers/04_consumer_commit_manual.py`

```bash
python consumers/04_consumer_commit_manual.py
```

**Teste:**
1. Rode o consumer.
2. Deixe processar 3 mensagens (antes do commit de 5 mensagens).
3. Pressione Ctrl+C.
4. Rode novamente: as 3 mensagens são reprocessadas.

### Dead Letter Queue (DLQ) e Poison Pill

Um **Poison Pill** é uma mensagem que o consumer não consegue processar independentemente do número de tentativas. Causa mais comum: schema incompatível entre producer e consumer.

O perigo: o Poison Pill trava a partição. Nenhuma mensagem posterior é processada até a mensagem inválida ser resolvida.

Padrão DLQ:

![Padrão Dead Letter Queue](d4-dlq-pattern.drawio.png)

Regra crítica: após publicar no DLQ, **commitar o offset imediatamente** para não travar a partição.

---

## 10. Resumo: padrões de consumer

| Script | Padrão | Quando usar em DE |
|---|---|---|
| `01_consumer_basico.py` | Leitura simples | Prototipagem, pipelines de baixo volume |
| `02_consumer_grupo.py` | Consumer group | Produção, paralelismo horizontal |
| `03_consumer_seek.py` | Seek manual | Debug, reprocessamento, auditoria forense |
| `04_consumer_commit_manual.py` | Commit manual | Pipelines críticos, at-least-once garantido |

---

## 11. Para além desta sessão — temas de produção

### Schema Registry e Avro

O Schema Registry é um serviço que armazena e versiona os schemas das mensagens. Sem ele:

```
Producer manda: {"session_id": "abc", "event_type": "click", "revenue": 9.99}
Consumer espera: {"session_id": "abc", "type": "click", "amount": 9.99}
                                              ^                  ^
                              campo renomeado sem aviso      campo renomeado sem aviso
                              Consumer quebra em producao
```

Com Schema Registry:
- O producer registra o schema antes de enviar.
- O payload inclui um `schema_id` de 4 bytes.
- O consumer busca o schema pelo ID e deserializa corretamente.

Modos de compatibilidade:

| Modo | O que permite |
|---|---|
| BACKWARD | Consumer novo lê dados do producer antigo |
| FORWARD | Consumer antigo lê dados do producer novo |
| FULL | Ambos os sentidos ao mesmo tempo |

Regra segura para evolução: sempre **adicionar campos com `default`**. Nunca renomear ou remover sem default.

### Log Compaction — para dados de estado

Topics com `cleanup.policy=delete` descartam mensagens por idade ou tamanho. Topics com `cleanup.policy=compact` guardam apenas a **última mensagem por chave**.

```
Antes da compactação:
  offset 0: chave=user-42  {"status": "ativo"}
  offset 1: chave=user-17  {"status": "ativo"}
  offset 2: chave=user-42  {"status": "inativo"}   <-- mais recente

Após compactação:
  offset 1: chave=user-17  {"status": "ativo"}
  offset 2: chave=user-42  {"status": "inativo"}   <-- unico sobrevivente
```

Caso de uso: estado atual de entidades (usuários, produtos, configurações). Um consumer que ler do início obtém o estado atual de cada chave sem processar todo o histórico.

Para deletar uma chave: enviar mensagem com valor `null` (tombstone). Após compactação, a chave é removida.

### Kafka Connect e Debezium

Kafka Connect é um framework de integração que dispensa código de producer/consumer:

![Kafka Connect Pipeline](d5-kafka-connect.drawio.png)

**Debezium** é o Source Connector mais usado para CDC. Ele lê o **transaction log do banco** (WAL no PostgreSQL, binlog no MySQL) e publica cada mudança como evento:

```json
{
  "op": "u",
  "before": {"id": 42, "status": "ativo"},
  "after":  {"id": 42, "status": "inativo"},
  "source": {"db": "producao", "table": "usuarios", "ts_ms": 1719600000000}
}
```

Vantagens sobre CDC batch:
- Latência de segundos (vs horas com batch).
- Captura **deletes** (impossível com query de timestamp).
- Sem carga adicional de queries no banco transacional.
- Ordenação garantida (mesma ordem do log do banco).

### Semântica exactly-once

Idempotência do producer (duplicatas descartadas pelo broker) + transações Kafka (commit atômico de offset + mensagem de saída) = **exactly-once end-to-end**.

```python
producer = Producer({
    "bootstrap.servers": "localhost:9092",
    "enable.idempotence": True,
    "transactional.id": "meu-producer-tx-1",
    "acks": "all",
})
producer.init_transactions()

producer.begin_transaction()
producer.produce(topic="saida", value="evento processado")
consumer.commit(...)           # commita offset dentro da transacao
producer.commit_transaction()  # atomico: tudo vai ou nada vai
```

Custo: latência ~2-5ms maior, throughput ~10-20% menor. Use apenas onde duplicatas causam impacto real (financeiro, faturamento).

### Kafka na plataforma de dados

Onde o Kafka se encaixa na arquitetura que vimos nas sessões anteriores:

![Kafka na Plataforma de Dados](d6-kafka-plataforma.drawio.png)

Comparativo com alternativas:

| Serviço | Quando usar |
|---|---|
| **Apache Kafka** | Alta vazão, retenção longa, múltiplos consumers, on-premise ou cloud |
| **Amazon Kinesis** | AWS-only, operação simplificada, custo proporcional ao uso |
| **Amazon MSK** | Kafka gerenciado na AWS (mesma API, menos operação) |
| **Google Pub/Sub** | GCP-only, serverless, sem gerenciar brokers |
| **Confluent Cloud** | Kafka multi-cloud com Schema Registry e Connect incluídos |

Para a maioria dos casos de marketing analytics, **near real-time** (segundos de latência via Kafka Connect + S3 Sink) é suficiente e muito mais simples de operar do que Flink.

---

## 12. O que o engenheiro de dados precisa saber sobre Kafka

| Tópico | Nível mínimo | Nível avançado |
|---|---|---|
| Tópicos, partições, offsets | Entender e explicar | Dimensionar corretamente |
| Producers e Consumers | Escrever código funcional | Tunar throughput e latência |
| Consumer Groups | Usar em produção | Diagnosticar lag e rebalanceamentos |
| Retenção e compaction | Saber quando usar cada um | Configurar por topic |
| Semântica de entrega | Entender os três níveis | Implementar exactly-once |
| Consumer Lag | Monitorar via CLI | Alertas e dashboards Grafana |
| DLQ | Conhecer o padrão | Implementar com retry e backoff |
| Schema Registry | Saber para que serve | Gerenciar evolução de schema |
| Kafka Connect | Saber o que é | Configurar e operar connectors |
| Debezium | Saber o que é | Configurar CDC de banco relacional |
