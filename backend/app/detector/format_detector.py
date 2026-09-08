import json
import re


def detect_format(raw_log: str) -> str:
    """
    Detect the format of an incoming log.

    Currently supports:
    - syslog
    - json
    - unknown
    """
    APACHE_PATTERN = re.compile(
        r'^\S+\s+\S+\s+\S+\s+\[[^\]]+\]\s+'
        r'"\S+\s+\S+(?:\s+[^"]+)?"\s+\d{3}\s+\S+'
    )
    syslog_pattern = (
        r"^[A-Z][a-z]{2}\s+\d{1,2}\s+"
        r"\d{2}:\d{2}:\d{2}\s+"
    )
    CEF_PATTERN = re.compile(r"^CEF:\d+\|")
    if re.match(APACHE_PATTERN, raw_log):
        return "apache"

    if re.match(syslog_pattern, raw_log):
        return "syslog"

    if re.match(CEF_PATTERN, raw_log):
        return "cef"

    try:
        data = json.loads(raw_log)

        if isinstance(data, dict):
            return "json"

    except json.JSONDecodeError:
        pass

    return "unknown"