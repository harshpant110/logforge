from app.processor import process_log


def test_cef_to_ocsf_pipeline():

    message = {
        "event_id": "cef-001",
        "user_id": 1,
        "app_id": 10,
        "raw_log": (
            "CEF:0|SecurityVendor|Firewall|1.0|100|"
            "Login Failed|5|"
            "src=192.168.1.10 "
            "dst=10.0.0.5 "
            "spt=52144 "
            "dpt=443 "
            "proto=TCP "
            "suser=user"
        ),
    }

    result = process_log(message)

    assert result.event_id == "cef-001"
    assert result.user_id == 1
    assert result.app_id == 10

    assert result.event.message == "Login Failed"

    assert result.event.unmapped["source_format"] == "cef"
    assert result.event.user is not None
    assert result.event.user.name == "user"

    assert result.event.src_endpoint is not None
    assert result.event.src_endpoint.ip == "192.168.1.10"
    assert result.event.src_endpoint.port == 52144
    
    assert result.event.unmapped["cef_severity"] == "5"
    assert result.event.dst_endpoint is not None
    assert result.event.dst_endpoint.ip == "10.0.0.5"
    assert result.event.dst_endpoint.port == 443

    assert result.event.src_endpoint.protocol == "TCP"
    assert result.event.dst_endpoint.protocol == "TCP"

def test_cef_severity_to_ocsf_pipeline():

    message = {
        "event_id": "cef-002",
        "user_id": 1,
        "app_id": 10,
        "raw_log": (
            "CEF:0|SecurityVendor|Firewall|1.0|100|"
            "Login Failed|5|"
            "src=192.168.1.10 suser=user"
        ),
    }

    result = process_log(message)

    assert result.event.message == "Login Failed"

    assert result.event.class_uid == 3002
    assert result.event.category_uid == 3
    assert result.event.activity_id == 1
    assert result.event.type_uid == 300201

    assert result.event.status_id == 2
    assert result.event.status == "Failure"

    assert result.event.severity_id == 3
    assert result.event.severity == "Medium"

    assert result.event.user.name == "user"
    assert result.event.src_endpoint.ip == "192.168.1.10"

    assert result.event.unmapped["cef_severity"] == "5"

def test_cef_blocked_event_maps_disposition():
    message = {
        "event_id": "cef-blocked-001",
        "user_id": 1,
        "app_id": 10,
        "raw_log": (
            "CEF:0|SecurityVendor|Firewall|1.0|100|"
            "Connection Blocked|8|"
            "src=192.168.1.10 "
            "dst=10.0.0.5 "
            "spt=52144 "
            "dpt=443 "
            "proto=TCP "
            "act=blocked"
        ),
    }

    result = process_log(message)

    assert result.event.class_uid == 4001
    assert result.event.category_uid == 4

    assert result.event.disposition_id == 2
    assert result.event.disposition == "Blocked"

def test_cef_allowed_event_maps_disposition():
    message = {
        "event_id": "cef-allowed-001",
        "user_id": 1,
        "app_id": 10,
        "raw_log": (
            "CEF:0|SecurityVendor|Firewall|1.0|101|"
            "Connection Allowed|3|"
            "src=192.168.1.10 "
            "dst=10.0.0.5 "
            "spt=52144 "
            "dpt=443 "
            "proto=TCP "
            "act=allowed"
        ),
    }

    result = process_log(message)

    assert result.event.class_uid == 4001
    assert result.event.category_uid == 4

    assert result.event.disposition_id == 1
    assert result.event.disposition == "Allowed"