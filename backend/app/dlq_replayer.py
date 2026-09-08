import json

from kafka import KafkaConsumer, KafkaProducer


KAFKA_BROKER = "localhost:9092"
DLQ_TOPIC = "logforge-dlq"
RAW_LOG_TOPIC = "raw-logs"


producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda value: json.dumps(value).encode("utf-8"),
)


def replay_message(dlq_message: dict):
    original_message = dlq_message["original_message"]

    producer.send(
        RAW_LOG_TOPIC,
        value=original_message,
    )

    producer.flush()

    print(
        f"Replayed event "
        f"{original_message.get('event_id')} "
        f"to {RAW_LOG_TOPIC}"
    )
consumer = KafkaConsumer(
    DLQ_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    group_id="logforge-dlq-replayer",
    auto_offset_reset="earliest",
    enable_auto_commit=False,
)


def run_replayer():
    print("LogForge DLQ replayer started...")
    print(f"Listening to: {DLQ_TOPIC}")

    for message in consumer:
        try:
            dlq_message = json.loads(
                message.value.decode("utf-8")
            )

            replay_message(dlq_message)

            consumer.commit()

            print("DLQ message replayed and committed")

        except Exception as error:
            print(f"Failed to replay DLQ message: {error}")
if __name__ == "__main__":
    run_replayer()