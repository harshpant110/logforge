from app.parsers.json_parser import parse_json_log
from app.parsers.syslog_parser import parse_syslog
from app.parsers.apache_parser import parse_apache


PARSERS = {
    "syslog": parse_syslog,
    "json": parse_json_log,
    "apache": parse_apache,
}


def get_parser(log_format: str):
    """
    Return the parser responsible for the given log format.
    """

    parser = PARSERS.get(log_format)

    if parser is None:
        raise ValueError(
            f"No parser available for format: {log_format}"
        )

    return parser