from unittest import result

from app.processor import process_log
import pytest


from app.processor import process_log


def test_process_syslog():

    message = {
        "event_id": "test-001",
        "user_id": 1,
        "app_id": 10,
        "raw_log": (
            "Sep 6 12:00:01 server "
            "sshd[1234]: Failed password for User123"
        ),
    }

    result = process_log(message)

    # Application envelope
    assert result.event_id == "test-001"
    assert result.user_id == 1
    assert result.app_id == 10

    # OCSF classification
    assert result.event.class_uid == 3002
    assert result.event.category_uid == 3
    assert result.event.activity_id == 1
    assert result.event.type_uid == 300201

    assert result.event.activity_name == "Logon"

    # Authentication status
    assert result.event.status_id == 2
    assert result.event.status == "Failure"

    # Severity
    assert result.event.severity_id == 4
    assert result.event.severity == "High"

    # OCSF metadata
    assert result.event.metadata.version == "1.8.0"
    assert result.event.metadata.uid == "test-001"

    # Device
    assert result.event.device.hostname == "server"

    # Process
    assert result.event.process.name == "sshd"
    assert result.event.process.pid == 1234

    # Message
    assert result.event.message == "Failed password for User123"

    # Source information
    assert result.event.unmapped["source_format"] == "syslog"


def test_process_unknown_format():

    message = {
        "event_id": "test-002",
        "user_id": 1,
        "app_id": 10,
        "raw_log": "This is not a supported log format",
    }

    try:
        process_log(message)
        assert False, "Expected ValueError"

    except ValueError as error:
        assert str(error) == "Unsupported log format"

    message = {
        "event_id": "test-002",
        "user_id": 1,
        "app_id": 10,
        "raw_log": "This is not a supported log format",
    }

    try:
        process_log(message)
        assert False, "Expected ValueError"

    except ValueError as error:
        assert str(error) == "Unsupported log format"
def test_invalid_syslog():

    message = {
        "event_id": "test-003",
        "user_id": 1,
        "app_id": 10,
        "raw_log": "Sep 6 this looks like syslog but is invalid",
    }

    with pytest.raises(ValueError, match="Unsupported log format"):
        process_log(message)

def test_send_to_dlq(monkeypatch):
    from app.producer import send_to_dlq

    sent_messages = []

    class FakeFuture:
        def get(self, timeout=None):
            return None

    def fake_send(topic, value):
        sent_messages.append((topic, value))
        return FakeFuture()

    monkeypatch.setattr(
        "app.producer.producer.send",
        fake_send,
    )

    message = {
        "event_id": "failed-001",
        "user_id": 1,
        "app_id": 10,
        "raw_log": "invalid log",
    }

    kafka_metadata = {
    "topic": "raw-logs",
    "partition": 0,
    "offset": 123,
}

    send_to_dlq(
        message,
        "Unsupported log format",
        kafka_metadata,
    )
    assert len(sent_messages) == 1

    topic, value = sent_messages[0]

    assert topic == "logforge-dlq"
    assert value["original_message"] == message
    assert value["error"] == "Unsupported log format"
    assert value["kafka"] == kafka_metadata