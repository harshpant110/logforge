from app.mapper.classifier import classify_event


def test_failed_authentication():

    result = classify_event(
        "Failed password for User123"
    )

    assert result["event_type"] == "authentication"
    assert result["class_uid"] == 2
    assert result["category_uid"] == 3
    assert result["activity_id"] == 1
    assert result["activity_name"] == "Logon"

    assert result["status_id"] == 2
    assert result["status"] == "Failure"

    assert result["severity_id"] == 3
    assert result["severity"] == "High"


def test_successful_authentication():

    result = classify_event(
        "Accepted password for User123"
    )

    assert result["event_type"] == "authentication"
    assert result["class_uid"] == 2
    assert result["category_uid"] == 3
    assert result["activity_id"] == 1
    assert result["activity_name"] == "Logon"

    assert result["status_id"] == 1
    assert result["status"] == "Success"

    assert result["severity_id"] == 1
    assert result["severity"] == "Low"


def test_unknown_event():

    result = classify_event(
        "Something completely unrelated"
    )

    assert result["event_type"] == "unknown"
    assert result["class_uid"] == 0
    assert result["category_uid"] == 0
    assert result["activity_id"] == 0


def test_empty_message():

    result = classify_event(None)

    assert result["event_type"] == "unknown"