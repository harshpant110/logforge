import pytest

from app.parsers.apache_parser import parse_apache


def test_parse_apache():

    raw_log = (
        '192.168.1.10 - - '
        '[06/Sep/2026:12:00:01 +0000] '
        '"GET /login HTTP/1.1" 401 512'
    )

    result = parse_apache(raw_log)

    assert result["timestamp"] == (
        "06/Sep/2026:12:00:01 +0000"
    )

    assert result["source_ip"] == "192.168.1.10"
    assert result["method"] == "GET"
    assert result["path"] == "/login"
    assert result["protocol"] == "HTTP/1.1"

    assert result["status_code"] == 401
    assert result["response_size"] == 512

    assert result["process_name"] == "apache"


def test_invalid_apache_log():

    with pytest.raises(
        ValueError,
        match="Invalid Apache access log format"
    ):
        parse_apache("this is not apache")