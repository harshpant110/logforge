from app.parsers.json_parser import parse_json_log
import pytest



def test_invalid_json():

    with pytest.raises(ValueError, match="Invalid JSON log"):
        parse_json_log("this is not json")


def test_parse_json_log():

    log = (
        '{"timestamp":"2026-09-06T13:00:00",'
        '"hostname":"server01",'
        '"process_name":"nginx",'
        '"process_id":1234,'
        '"message":"GET /login 200"}'
    )

    result = parse_json_log(log)

    assert result["timestamp"] == "2026-09-06T13:00:00"
    assert result["hostname"] == "server01"
    assert result["process_name"] == "nginx"
    assert result["process_id"] == 1234
    assert result["message"] == "GET /login 200"