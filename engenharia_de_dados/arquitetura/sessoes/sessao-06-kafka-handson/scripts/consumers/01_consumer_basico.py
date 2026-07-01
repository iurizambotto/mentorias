"""
Consumer basico: le mensagens do topic 'mentoria-basico'.

Conceitos cobertos:
- Criar um Consumer com group.id
- subscribe() para se inscrever em um topic
- poll() para buscar mensagens
- auto.offset.reset: 'earliest' para ler tudo desde o inicio
- Tratamento de erros e encerramento gracioso

Rodar:
    python 01_consumer_basico.py
"""

from confluent_kafka import Consumer, KafkaException

BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC = "mentoria-basico"
GROUP_ID = "grupo-basico"


def main() -> None:
    consumer = Consumer({
        "bootstrap.servers": BOOTSTRAP_SERVERS,
        "group.id": GROUP_ID,
        # earliest: le desde a primeira mensagem disponivel no topic.
        # latest: le somente mensagens novas a partir de agora.
        "auto.offset.reset": "earliest",
    })

    consumer.subscribe([TOPIC])
    print(f"Consumindo '{TOPIC}' | grupo='{GROUP_ID}'")
    print("Pressione Ctrl+C para encerrar.\n")

    try:
        while True:
            msg = consumer.poll(timeout=1.0)

            if msg is None:
                # Nenhuma mensagem disponivel no momento.
                continue

            if msg.error():
                raise KafkaException(msg.error())

            key = msg.key().decode("utf-8") if msg.key() else None
            value = msg.value().decode("utf-8")

            print(
                f"  topic={msg.topic()}"
                f"  partition={msg.partition()}"
                f"  offset={msg.offset()}"
                f"  key={key}"
                f"  value={value}"
            )

    except KeyboardInterrupt:
        print("\nInterrompido pelo usuario.")
    finally:
        # Fecha o consumer e libera os offsets para o grupo.
        consumer.close()
        print("Consumer encerrado.")


if __name__ == "__main__":
    main()
