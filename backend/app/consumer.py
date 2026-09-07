import json

from kafka import KafkaConsumer

from app.processor import process_log


KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "raw-logs"
CONSUMER_GROUP = "logforge-worker"


consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=KAFKA_BROKER,
    group_id=CONSUMER_GROUP,
    auto_offset_reset="earliest",
    enable_auto_commit=True,
)


print("LogForge worker started...")
print(f"Listening to Kafka topic: {KAFKA_TOPIC}")


for message in consumer:

    try:
        # Decode Kafka message
        raw_value = message.value.decode("utf-8")

        # Convert JSON string → Python dictionary
        raw_message = json.loads(raw_value)

        print("\nReceived log:")
        print(raw_message)

        # Process log
        normalized_event = process_log(raw_message)

        print("\nNormalized event:")
        print(normalized_event.model_dump_json(indent=2))

    except json.JSONDecodeError as error:
        print(f"\nInvalid JSON message: {error}")

    except Exception as error:
        print(f"\nFailed to process log: {error}")