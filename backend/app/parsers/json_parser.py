import json


def parse_json_log(raw_log: str) -> dict:
    try:
        data = json.loads(raw_log)
    except json.JSONDecodeError as error:
        raise ValueError("Invalid JSON log") from error

    if not isinstance(data, dict):
        raise ValueError("JSON log must be an object")

    return {
        "timestamp": data.get("timestamp"),
        "hostname": data.get("hostname"),
        "process_name": data.get("process_name"),
        "process_id": data.get("process_id"),
        "message": data.get("message", ""),
    }