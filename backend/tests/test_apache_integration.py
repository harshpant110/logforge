from app.processor import process_log


def test_apache_to_ocsf_pipeline():

    message = {
        "event_id": "apache-001",
        "user_id": 1,
        "app_id": 10,
        "raw_log": (
            '192.168.1.10 - - '
            '[06/Sep/2026:12:00:01 +0000] '
            '"GET /login HTTP/1.1" 401 512'
        ),
    }

    result = process_log(message)

    assert result.event_id == "apache-001"
    assert result.user_id == 1
    assert result.app_id == 10

    assert result.event.device.hostname is None

    assert result.event.message == "GET /login HTTP/1.1"

    assert result.event.unmapped["source_format"] == "apache"
    assert result.event.http is not None

    assert result.event.http.method == "GET"
    assert result.event.http.path == "/login"
    assert result.event.http.protocol == "HTTP/1.1"
    assert result.event.http.status_code == 401
    assert result.event.http.response_size == 512
    assert result.event.http.source_ip == "192.168.1.10"