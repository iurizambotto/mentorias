"""
Consumer com seek: le a partir de um offset especifico.

Conceitos cobertos:
- Diferenca entre subscribe() e assign()
- seek() para posicionar o cursor em qualquer offset
- Util para reprocessar mensagens ou depurar
- Nao usa group.id (leitura direta por particao)

Rodar:
    python 03_consumer_seek.py                  # le particao 0 do offset 0
    python 03_consumer_seek.py --particao 1 --offset 5
"""

import argparse

from confluent_kafka import Consumer, KafkaException, TopicPartition

BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC = "mentoria-eventos-mkt"


def main(particao: int, offset: int) -> None:
    consumer = Consumer({
        "bootstrap.servers": BOOTSTRAP_SERVERS,
        # Sem group.id: leitura direta sem participar de um consumer group.
        "group.id": "grupo-seek-debug",
        "auto.offset.reset": "earliest",
        # Desabilita commit automatico pois este consumer e para inspecao.
        "enable.auto.commit": False,
    })

    # assign() em vez de subscribe(): controle manual da particao e offset.
    tp = TopicPartition(TOPIC, particao, offset)
    consumer.assign([tp])

    # seek() posiciona o cursor exatamente no offset desejado.
    consumer.seek(tp)

    print(f"Lendo '{TOPIC}' | particao={particao} | a partir do offset={offset}")
    print("Pressione Ctrl+C para encerrar.\n")

    lidas = 0
    try:
        while True:
            msg = consumer.poll(timeout=2.0)

            if msg is None:
                print("Sem mensagens novas. Aguardando...")
                continue

            if msg.error():
                raise KafkaException(msg.error())

            import json
            try:
                value = json.loads(msg.value().decode("utf-8"))
                resumo = f"event_type={value.get('event_type')}  campaign={value.get('campaign')}"
            except Exception:
                resumo = msg.value().decode("utf-8")

            lidas += 1
            print(
                f"  [{lidas}] offset={msg.offset()}"
                f"  {resumo}"
            )

    except KeyboardInterrupt:
        print(f"\nEncerrado. Mensagens lidas: {lidas}")
    finally:
        consumer.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Consumer com seek para offset especifico")
    parser.add_argument("--particao", type=int, default=0, help="Numero da particao (default: 0)")
    parser.add_argument("--offset", type=int, default=0, help="Offset de inicio (default: 0)")
    args = parser.parse_args()

    main(particao=args.particao, offset=args.offset)
