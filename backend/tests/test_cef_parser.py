import pytest

from app.parsers.cef_parser import parse_cef


def test_parse_cef():

    raw_log = (
        "CEF:0|SecurityVendor|Firewall|1.0|100|"
        "Login Failed|8|"
        "src=192.168.1.10 suser=user"
    )

    result = parse_cef(raw_log)

    assert result["vendor"] == "SecurityVendor"
    assert result["product"] == "Firewall"
    assert result["product_version"] == "1.0"

    assert result["cef_event_id"] == "100"
    assert result["event_name"] == "Login Failed"
    assert result["cef_severity"] == "8"

    assert result["source_ip"] == "192.168.1.10"
    assert result["username"] == "user"

    assert result["message"] == "Login Failed"

def test_parse_cef_network_fields():

    raw_log = (
        "CEF:0|SecurityVendor|Firewall|1.0|200|"
        "Connection Blocked|8|"
        "src=192.168.1.10 "
        "dst=10.0.0.5 "
        "spt=52144 "
        "dpt=443 "
        "proto=TCP "
        "act=blocked "
        "msg=Connection blocked"
    )

    result = parse_cef(raw_log)

    assert result["source_ip"] == "192.168.1.10"
    assert result["destination_ip"] == "10.0.0.5"

    assert result["source_port"] == 52144
    assert result["destination_port"] == 443

    assert result["protocol"] == "TCP"
    assert result["action"] == "blocked"

    assert result["message"] == "Connection blocked"

def test_cef_parser_handles_message_with_spaces():
    raw_log = (
        "CEF:0|SecurityVendor|Firewall|1.0|100|"
        "Login Failed|5|"
        "src=192.168.1.10 "
        "msg=User login failed from unknown device "
        "suser=user"
    )

    result = parse_cef(raw_log)

    assert result["source_ip"] == "192.168.1.10"
    assert result["message"] == "User login failed from unknown device"
    assert result["username"] == "user"

def test_cef_parser_unescapes_pipe_in_message():
    raw_log = (
        "CEF:0|SecurityVendor|Firewall|1.0|100|"
        "Connection Blocked|5|"
        "msg=Connection\\|blocked "
        "src=192.168.1.10"
    )

    result = parse_cef(raw_log)

    assert result["message"] == "Connection|blocked"

def test_cef_parser_unescapes_common_characters():
    raw_log = (
        "CEF:0|SecurityVendor|Firewall|1.0|100|"
        "Test Event|5|"
        "msg=Error\\=Invalid\\nSecond line "
        "path=C:\\\\server"
    )

    result = parse_cef(raw_log)

    assert result["message"] == "Error=Invalid\nSecond line"
def test_invalid_cef():

    with pytest.raises(
        ValueError,
        match="Invalid CEF format"
    ):
        parse_cef("this is not CEF")