import json
import uuid

from kafka import KafkaProducer


KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "raw-logs"


producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda value: json.dumps(value).encode("utf-8"),
)


def send_log(user_id: int, app_id: int, raw_log: str):

    message = {
        "event_id": str(uuid.uuid4()),
        "user_id": user_id,
        "app_id": app_id,
        "raw_log": raw_log,
    }

    producer.send(KAFKA_TOPIC, value=message)
    producer.flush()

    print("Log sent to Kafka:")
    print(json.dumps(message, indent=2))


if __name__ == "__main__":

    send_log(
        user_id=1,
        app_id=10,
        raw_log=(
            "Sep 6 12:00:01 server "
            "sshd[1234]: Failed password for User123"
        ),
    )