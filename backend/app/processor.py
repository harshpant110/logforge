from app.detector.format_detector import detect_format
from app.parsers.parser_registry import get_parser
from app.mapper.ocsf_mapper import map_to_ocsf


def process_log(message: dict):

    event_id = message["event_id"]
    user_id = message["user_id"]
    app_id = message["app_id"]
    raw_log = message["raw_log"]

    # 1. Detect format
    log_format = detect_format(raw_log)

    if log_format == "unknown":
        raise ValueError("Unsupported log format")

    # 2. Parse
   

    parser = get_parser(log_format)

    parsed_log = parser(raw_log)

    # 3. Normalize
    normalized_event = map_to_ocsf(
        event_id=event_id,
        user_id=user_id,
        app_id=app_id,
        parsed_log=parsed_log,
        log_format=log_format,
    )

    return normalized_event