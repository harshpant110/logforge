from app.detector.format_detector import detect_format


def test_detect_syslog():
    log = (
        "Sep 6 12:00:01 server "
        "sshd[1234]: Failed password"
    )

    assert detect_format(log) == "syslog"


def test_unknown_format():
    log = "This is some random log"

    assert detect_format(log) == "unknown"
    
def test_detect_json():

    log = '{"message":"User logged in","hostname":"server01"}'

    assert detect_format(log) == "json"
    
def test_detect_apache():

    raw_log = (
        '192.168.1.10 - - '
        '[06/Sep/2026:12:00:01 +0000] '
        '"GET /login HTTP/1.1" 401 512'
    )

    assert detect_format(raw_log) == "apache"