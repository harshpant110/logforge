import re


APACHE_PATTERN = re.compile(
    r'^(?P<source_ip>\S+)\s+'
    r'\S+\s+\S+\s+'
    r'\[(?P<timestamp>[^\]]+)\]\s+'
    r'"(?P<method>\S+)\s+'
    r'(?P<path>\S+)'
    r'(?:\s+(?P<protocol>[^"]+))?"\s+'
    r'(?P<status_code>\d{3})\s+'
    r'(?P<response_size>\S+)'
    r'(?:\s+"(?P<referrer>[^"]*)")?'
    r'(?:\s+"(?P<user_agent>[^"]*)")?$'
)


def parse_apache(raw_log: str) -> dict:
    """
    Parse an Apache Combined Log Format access log.
    """

    match = APACHE_PATTERN.match(raw_log)

    if not match:
        raise ValueError("Invalid Apache access log format")

    data = match.groupdict()

    return {
        "timestamp": data["timestamp"],
        "hostname": None,
        "process_name": "apache",
        "process_id": None,
        "message": (
            f'{data["method"]} {data["path"]} '
            f'{data["protocol"] or ""}'.strip()
        ),
        "source_ip": data["source_ip"],
        "method": data["method"],
        "path": data["path"],
        "protocol": data["protocol"],
        "status_code": int(data["status_code"]),
        "response_size": (
            None
            if data["response_size"] == "-"
            else int(data["response_size"])
        ),
        "referrer": data["referrer"],
        "user_agent": data["user_agent"],
    }