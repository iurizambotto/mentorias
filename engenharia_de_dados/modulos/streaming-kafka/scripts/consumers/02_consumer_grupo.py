"""
Consumer group: demonstra distribuicao de particoes entre consumers.

Conceitos cobertos:
- Mesmo group.id compartilhado por multiplos consumers
- Cada consumer recebe um subconjunto das particoes (rebalanceamento)
- Quando um consumer entra ou sai, o Kafka redistribui as particoes
- Como observar o rebalanceamento no kafka-ui

COMO USAR:
  Terminal 1: python 02_consumer_grupo.py --nome A
  Terminal 2: python 02_consumer_grupo.py --nome B
  Terminal 3: python 02_consumer_grupo.py --nome C  (opcional)

  Observe no kafka-ui quais particoes cada consumer recebeu.
  Encerre um dos consumers e veja o rebalanceamento acontecer.
"""

import argparse

from confluent_kafka import Consumer, KafkaException

BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC = "mentoria-eventos-mkt"
GROUP_ID = "grupo-analise-mkt"


def ao_atribuir(consumer, particoes):
    print(f"\n[REBALANCE] Consumer '{nome}' recebeu: {[p.partition for p in particoes]}")


def ao_revogar(consumer, particoes):
    print(f"\n[REBALANCE] Consumer '{nome}' perdeu: {[p.partition for p in particoes]}")


def main(nome: str) -> None:
    global nome_consumer
    nome_consumer = nome

    consumer = Consumer({
        "bootstrap.servers": BOOTSTRAP_SERVERS,
        "group.id": GROUP_ID,
        "auto.offset.reset": "earliest",
    })

    consumer.subscribe([TOPIC], on_assign=ao_atribuir, on_revoke=ao_revogar)
    print(f"Consumer '{nome}' | topic='{TOPIC}' | grupo='{GROUP_ID}'")
    print("Pressione Ctrl+C para encerrar.\n")

    try:
        while True:
            msg = consumer.poll(timeout=1.0)

            if msg is None:
                continue

            if msg.error():
                raise KafkaException(msg.error())

            import json
            try:
                value = json.loads(msg.value().decode("utf-8"))
                event_type = value.get("event_type", "?")
            except Exception:
                event_type = msg.value().decode("utf-8")

            print(
                f"[{nome}] partition={msg.partition()}"
                f"  offset={msg.offset()}"
                f"  event_type={event_type}"
            )

    except KeyboardInterrupt:
        print(f"\nConsumer '{nome}' encerrado.")
    finally:
        consumer.close()


# Alias global para os callbacks de rebalance acessarem o nome.
nome = "?"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Consumer de grupo para demonstracao")
    parser.add_argument("--nome", default="A", help="Nome identificador deste consumer (A, B, C...)")
    args = parser.parse_args()

    nome = args.nome
    main(nome=args.nome)
