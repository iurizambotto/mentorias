---
title: Validar o Kafka
date: 2026-06-29
type: runbook
status: active
tags: [kafka, smoke-test, mentoria]
---

# Validar o Kafka

Os scripts do Kafka ficam em `/opt/kafka/bin/` na imagem `apache/kafka`.

## Listar topics existentes

```bash
docker exec mentoria-s11-kafka /opt/kafka/bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --list
```

## Criar topic manualmente (opcional, o auto-create já está ligado)

```bash
docker exec mentoria-s11-kafka /opt/kafka/bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create \
  --topic mentoria-basico \
  --partitions 3 \
  --replication-factor 1
```

## Enviar mensagem pelo terminal (producer de teste)

```bash
docker exec -it mentoria-s11-kafka /opt/kafka/bin/kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic mentoria-basico
```

Digite uma mensagem e pressione Enter. Ctrl+C para sair.

## Ler mensagens pelo terminal (consumer de teste)

```bash
docker exec -it mentoria-s11-kafka /opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic mentoria-basico \
  --from-beginning
```

## Verificar detalhes de um topic

```bash
docker exec mentoria-s11-kafka /opt/kafka/bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --describe \
  --topic mentoria-basico
```

## Verificar consumer lag de um grupo

```bash
docker exec mentoria-s11-kafka /opt/kafka/bin/kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --describe \
  --group grupo-analise-mkt
```

## Verificar via kafka-ui

- Topics: http://localhost:8080/ui/clusters/local/all-topics
- Consumer groups: http://localhost:8080/ui/clusters/local/consumer-groups
