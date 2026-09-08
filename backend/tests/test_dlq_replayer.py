def test_replay_message(monkeypatch):
    from app.dlq_replayer import replay_message

    sent_messages = []

    class FakeFuture:
        def get(self, timeout=None):
            return None

    def fake_send(topic, value):
        sent_messages.append((topic, value))
        return FakeFuture()

    monkeypatch.setattr(
        "app.dlq_replayer.producer.send",
        fake_send,
    )

    original_message = {
        "event_id": "replay-001",
        "user_id": 1,
        "app_id": 10,
        "raw_log": "Sep 6 12:00:01 server sshd[1234]: Failed password",
    }

    dlq_message = {
        "original_message": original_message,
        "error": "Some previous processing error",
        "kafka": {
            "topic": "raw-logs",
            "partition": 0,
            "offset": 123,
        },
    }

    replay_message(dlq_message)

    assert len(sent_messages) == 1

    topic, value = sent_messages[0]

    assert topic == "raw-logs"
    assert value == original_message