"""
Producer basico: envia 10 mensagens para o topic 'mentoria-basico'.

Conceitos cobertos:
- Criar um Producer
- Enviar mensagens com chave e valor
- Callback de entrega (confirmacao assincrona)
- flush() para garantir envio antes de encerrar
"""

from confluent_kafka import Producer

BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC = "mentoria-basico"


def ao_entregar(erro, msg):
    """Chamado pelo Kafka apos confirmar (ou falhar) a entrega de cada mensagem."""
    if erro:
        print(f"[ERRO] mensagem nao entregue: {erro}")
    else:
        print(
            f"[OK]  topic={msg.topic()}"
            f"  partition={msg.partition()}"
            f"  offset={msg.offset()}"
            f"  key={msg.key().decode() if msg.key() else None}"
        )


def main() -> None:
    producer = Producer({"bootstrap.servers": BOOTSTRAP_SERVERS})

    for i in range(10):
        chave = f"chave-{i}"
        valor = f"mensagem numero {i}"

        # produce() e assincrono: apenas coloca na fila interna do producer.
        producer.produce(
            topic=TOPIC,
            key=chave,
            value=valor,
            callback=ao_entregar,
        )

        # poll() dispara os callbacks pendentes (incluindo ao_entregar).
        producer.poll(0)

    # flush() aguarda todas as mensagens serem confirmadas pelo broker.
    producer.flush()
    print("\nProducao encerrada.")


if __name__ == "__main__":
    main()
