from app.mapper.classifier import classify_event, map_cef_severity

def test_map_cef_severity():

    assert map_cef_severity("2") == (2, "Low")
    assert map_cef_severity("5") == (3, "Medium")
    assert map_cef_severity("8") == (4, "High")
    assert map_cef_severity("10") == (5, "Critical")

def test_cef_severity_affects_classification():

    result = classify_event({
        "message": "Login Failed",
        "cef_severity": "5",
    })

    assert result["event_type"] == "authentication"
    assert result["severity_id"] == 3
    assert result["severity"] == "Medium"

def test_failed_authentication():

    result = classify_event(
        {
            "message": "Failed password for user"
        }
    )

    assert result["event_type"] == "authentication"
    assert result["class_uid"] == 3002
    assert result["category_uid"] == 3
    assert result["activity_id"] == 1
    assert result["activity_name"] == "Logon"

    assert result["status_id"] == 2
    assert result["status"] == "Failure"

    assert result["severity_id"] == 4
    assert result["severity"] == "High"


def test_successful_authentication():

    result = classify_event(
        {
            "message": "Accepted password for User123"
        }
    )

    assert result["event_type"] == "authentication"
    assert result["class_uid"] == 3002
    assert result["category_uid"] == 3
    assert result["activity_id"] == 1
    assert result["activity_name"] == "Logon"

    assert result["status_id"] == 1
    assert result["status"] == "Success"

    assert result["severity_id"] == 2
    assert result["severity"] == "Low"


def test_unknown_event():

    result = classify_event(
        {
            "message": "Something completely unrelated"
        }
    )

    assert result["event_type"] == "unknown"
    assert result["class_uid"] == 0
    assert result["category_uid"] == 0
    assert result["activity_id"] == 0

def test_http_unauthorized():

    result = classify_event({
        "message": "GET /login HTTP/1.1",
        "method": "GET",
        "status_code": 401,
    })

    assert result["event_type"] == "http"
    assert result["class_uid"] == 4002
    assert result["class_name"] == "HTTP Activity"
    assert result["category_uid"] == 4
    assert result["category_name"] == "Network Activity"
    assert result["activity_id"] == 3
    assert result["activity_name"] == "Get"
    assert result["status_id"] == 2
    assert result["status"] == "Failure"
    assert result["severity"] == "High"

def test_cef_network_blocked():

    result = classify_event({
        "message": "Connection blocked",
        "source_ip": "192.168.1.10",
        "destination_ip": "10.0.0.5",
        "action": "blocked",
        "cef_severity": "8",
    })

    assert result["event_type"] == "network"
    assert result["category_uid"] == 4
    assert result["class_uid"] == 4001
    assert result["status_id"] == 2
    assert result["status"] == "Failure"
    assert result["severity_id"] == 4
    assert result["severity"] == "High"
    
def test_empty_message():

    result = classify_event(None)

    assert result["event_type"] == "unknown"