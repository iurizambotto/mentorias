"""
Consumer com commit manual: demonstra controle explicito de offset.

Conceitos cobertos:
- enable.auto.commit: False (desabilita commit automatico)
- commit() manual apos processamento bem-sucedido
- Semantica at-least-once: se o processo cair antes do commit, a mensagem e reprocessada
- Diferenca entre at-most-once, at-least-once e exactly-once

Cenario para testar:
  1. Rode este script
  2. Deixe processar algumas mensagens
  3. Pressione Ctrl+C (simula uma queda)
  4. Rode novamente: as mensagens sem commit vao reaparecer

Rodar:
    python 04_consumer_commit_manual.py
"""

import json
import time

from confluent_kafka import Consumer, KafkaException

BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC = "mentoria-eventos-mkt"
GROUP_ID = "grupo-commit-manual"

# Commita a cada N mensagens processadas (micro-batch).
COMMIT_A_CADA = 5


def processar_evento(evento: dict) -> bool:
    """Simula processamento: salvar em banco, chamar API, etc."""
    # Simula latencia de processamento real.
    time.sleep(0.1)
    print(f"    processado: event_type={evento.get('event_type')}  revenue={evento.get('revenue')}")
    return True


def main() -> None:
    consumer = Consumer({
        "bootstrap.servers": BOOTSTRAP_SERVERS,
        "group.id": GROUP_ID,
        "auto.offset.reset": "earliest",
        # CHAVE: desabilitar auto-commit para controlar manualmente.
        "enable.auto.commit": False,
    })

    consumer.subscribe([TOPIC])
    print(f"Consumindo '{TOPIC}' com commit manual a cada {COMMIT_A_CADA} mensagens.")
    print(f"grupo='{GROUP_ID}'")
    print("Pressione Ctrl+C para simular uma queda antes do commit.\n")

    pendentes = 0
    total_commitadas = 0

    try:
        while True:
            msg = consumer.poll(timeout=1.0)

            if msg is None:
                continue

            if msg.error():
                raise KafkaException(msg.error())

            try:
                evento = json.loads(msg.value().decode("utf-8"))
            except json.JSONDecodeError:
                print(f"[AVISO] mensagem invalida no offset={msg.offset()}")
                continue

            print(f"[offset={msg.offset()} partition={msg.partition()}]")
            sucesso = processar_evento(evento)

            if sucesso:
                pendentes += 1

            # Commit em lote: so commita apos processar COMMIT_A_CADA mensagens.
            if pendentes >= COMMIT_A_CADA:
                consumer.commit(asynchronous=False)
                total_commitadas += pendentes
                pendentes = 0
                print(f"  --> COMMIT realizado. Total commitado: {total_commitadas}\n")

    except KeyboardInterrupt:
        print(f"\nQueda simulada! {pendentes} mensagem(s) processadas sem commit.")
        print("Ao reiniciar, essas mensagens serao reprocessadas (at-least-once).")
    finally:
        consumer.close()


if __name__ == "__main__":
    main()
