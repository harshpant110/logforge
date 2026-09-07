from app.parsers.syslog_parser import parse_syslog


def test_parse_syslog():

    log = (
        "Sep 6 12:00:01 server "
        "sshd[1234]: Failed password for amit"
    )

    result = parse_syslog(log)

    assert result["hostname"] == "server"
    assert result["process_name"] == "sshd"
    assert result["process_id"] == 1234
    assert result["message"] == "Failed password for amit"