"""
Producer de eventos de marketing: simula cliques, pageviews e conversoes.

Conceitos cobertos:
- Mensagens em formato JSON
- Chave como session_id (garante que eventos da mesma sessao vao para a mesma particao)
- Producao continua com intervalo (simula fluxo real)
- Topic com 3 particoes (criado automaticamente)

Rodar:
    python 02_producer_eventos_mkt.py
    python 02_producer_eventos_mkt.py --total 50 --intervalo 0.2
"""

import argparse
import json
import random
import time
import uuid

from confluent_kafka import Producer

BOOTSTRAP_SERVERS = "localhost:9092"
TOPIC = "mentoria-eventos-mkt"

TIPOS_EVENTO = ["pageview", "click", "add_to_cart", "conversion"]
PAGINAS = ["/home", "/produto/tenis-abc", "/produto/camiseta-xyz", "/checkout", "/obrigado"]
CAMPANHAS = ["black-friday", "verao-2026", "remarketing-30d", "influencer-q2"]


def ao_entregar(erro, msg) -> None:
    if erro:
        print(f"[ERRO] {erro}")
    else:
        key = msg.key().decode() if msg.key() else "-"
        print(
            f"[OK]  partition={msg.partition()}"
            f"  offset={msg.offset()}"
            f"  session_id={key[:8]}..."
        )


def gerar_evento() -> tuple[str, dict]:
    session_id = str(uuid.uuid4())
    evento = {
        "session_id": session_id,
        "event_type": random.choice(TIPOS_EVENTO),
        "page": random.choice(PAGINAS),
        "campaign": random.choice(CAMPANHAS),
        "revenue": round(random.uniform(0, 500), 2),
        "timestamp_ms": int(time.time() * 1000),
    }
    return session_id, evento


def main(total: int, intervalo: float) -> None:
    producer = Producer({"bootstrap.servers": BOOTSTRAP_SERVERS})
    print(f"Enviando {total} eventos para '{TOPIC}' (intervalo={intervalo}s)...")
    print("Observe as particoes no kafka-ui: http://localhost:8080\n")

    for _ in range(total):
        session_id, evento = gerar_evento()
        producer.produce(
            topic=TOPIC,
            key=session_id,
            value=json.dumps(evento),
            callback=ao_entregar,
        )
        producer.poll(0)
        time.sleep(intervalo)

    producer.flush()
    print("\nProducao encerrada.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Producer de eventos de marketing")
    parser.add_argument("--total", type=int, default=30, help="Numero de eventos (default: 30)")
    parser.add_argument("--intervalo", type=float, default=0.5, help="Segundos entre eventos (default: 0.5)")
    args = parser.parse_args()

    main(total=args.total, intervalo=args.intervalo)
