from app.processor import process_log


def test_syslog_to_ocsf_pipeline():

    message = {
        "event_id": "integration-001",
        "user_id": 1,
        "app_id": 10,
        "raw_log": (
            "Sep 6 12:00:01 server "
            "sshd[1234]: Failed password for User123"
        ),
    }

    result = process_log(message)

    # Application information
    assert result.event_id == "integration-001"
    assert result.user_id == 1
    assert result.app_id == 10

    # OCSF classification
    assert result.event.category_uid == 3
    assert result.event.category_name == (
        "Identity & Access Management"
    )

    assert result.event.class_uid == 2
    assert result.event.class_name == "Authentication"

    assert result.event.activity_id == 1
    assert result.event.activity_name == "Logon"

    assert result.event.type_uid == 201
    assert result.event.type_name == "Authentication: Logon"

    # Status
    assert result.event.status_id == 2
    assert result.event.status == "Failure"

    # Severity
    assert result.event.severity_id == 3
    assert result.event.severity == "High"

    # Parsed information
    assert result.event.device.hostname == "server"
    assert result.event.process.name == "sshd"
    assert result.event.process.pid == 1234
    assert result.event.message == "Failed password for User123"

    # Source
    assert result.event.unmapped["source_format"] == "syslog"