import re


SYSLOG_PATTERN = re.compile(
    r"^(?P<timestamp>[A-Z][a-z]{2}\s+\d{1,2}\s+"
    r"\d{2}:\d{2}:\d{2})\s+"
    r"(?P<hostname>\S+)\s+"
    r"(?P<process>\w+)"
    r"(?:\[(?P<pid>\d+)\])?:\s*"
    r"(?P<message>.*)$"
)


def parse_syslog(raw_log: str) -> dict:
    match = SYSLOG_PATTERN.match(raw_log)

    if not match:
        raise ValueError("Invalid syslog format")

    data = match.groupdict()

    return {
        "timestamp": data["timestamp"],
        "hostname": data["hostname"],
        "process_name": data["process"],
        "process_id": int(data["pid"]) if data["pid"] else None,
        "message": data["message"],
    }