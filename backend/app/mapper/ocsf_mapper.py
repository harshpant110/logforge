from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from app.mapper.classifier import classify_event
from app.models.event import (
    NormalizedEvent,
    OCSFDevice,
    OCSFEndpoint,
    OCSFEvent,
    OCSFHTTP,
    OCSFMetadata,
    OCSFProcess,
    OCSFUser,
)

def convert_timestamp(
    timestamp: str | None,
    *,
    syslog_year: int | None = None,
    syslog_timezone: str = "UTC",
) -> int:
    """
    Convert a log timestamp into Unix epoch milliseconds.

    Supports:
    - ISO-8601 timestamps
    - Traditional syslog timestamps

    Example ISO:
        2026-09-06T13:00:00Z

    Example syslog:
        Sep 6 12:00:01

    Traditional syslog does not contain a year, so the current
    year is used unless syslog_year is explicitly provided.
    """

    # No timestamp → use processing time
    if not timestamp:
        return int(datetime.now(timezone.utc).timestamp() * 1000)

    # Try ISO-8601
    try:
        dt = datetime.fromisoformat(
            timestamp.replace("Z", "+00:00")
        )

        # If timezone is missing, treat it as UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        return int(dt.astimezone(timezone.utc).timestamp() * 1000)

    except ValueError:
        pass
    try:
        dt = datetime.strptime(
            timestamp,
            "%d/%b/%Y:%H:%M:%S %z",
        )
    
        return int(
            dt.astimezone(timezone.utc).timestamp() * 1000
        )
    
    except ValueError:
        pass
    # Try traditional syslog format
    try:
        year = syslog_year or datetime.now(timezone.utc).year

        dt = datetime.strptime(
            f"{year} {timestamp}",
            "%Y %b %d %H:%M:%S",
        )

        dt = dt.replace(
            tzinfo=ZoneInfo(syslog_timezone)
        )

        return int(
            dt.astimezone(timezone.utc).timestamp() * 1000
        )

    except ValueError as error:
        raise ValueError(
            f"Invalid timestamp format: {timestamp}"
        ) from error

   
def map_to_ocsf(
    event_id: str,
    user_id: int,
    app_id: int,
    parsed_log: dict,
    log_format: str,
) -> NormalizedEvent:

    # Base Event
    
    classification = classify_event(parsed_log)

    class_uid = classification["class_uid"]
    category_uid = classification["category_uid"]
    activity_id = classification["activity_id"]

    type_uid = class_uid * 100 + activity_id
    http_data = None

    if log_format == "apache":
        http_data = OCSFHTTP(
            method=parsed_log.get("method"),
            path=parsed_log.get("path"),
            protocol=parsed_log.get("protocol"),
            status_code=parsed_log.get("status_code"),
            response_size=parsed_log.get("response_size"),
            referrer=parsed_log.get("referrer"),
            user_agent=parsed_log.get("user_agent"),
            source_ip=parsed_log.get("source_ip"),
        )
    user_data = None
    src_endpoint_data = None

    if parsed_log.get("username"):
        user_data = OCSFUser(
            name=parsed_log["username"]
        )

    if parsed_log.get("source_ip"):
        src_endpoint_data = OCSFEndpoint(
            ip=parsed_log["source_ip"],
            port=parsed_log.get("source_port"),
            protocol=parsed_log.get("protocol"),
        )
    dst_endpoint_data = None

    if parsed_log.get("destination_ip"):
        dst_endpoint_data = OCSFEndpoint(
            ip=parsed_log["destination_ip"],
            port=parsed_log.get("destination_port"),
            protocol=parsed_log.get("protocol"),

        )
    disposition_id = None
    disposition = None

    if parsed_log.get("action"):
        action = parsed_log["action"].lower()

        if action in {"blocked", "denied", "deny"}:
            disposition_id = 2
            disposition = "Blocked"
        elif action in {"allowed", "allow", "permitted", "permit"}:
            disposition_id = 1
            disposition = "Allowed"
    ocsf_event = OCSFEvent(
        activity_id=activity_id,
        activity_name=classification["activity_name"],

        category_uid=category_uid,
        category_name=classification["category_name"],

        class_uid=class_uid,
        class_name=classification["class_name"],

        type_uid=type_uid,
        type_name=classification["type_name"],

        severity_id=classification["severity_id"],
        severity=classification["severity"],
        status_id=classification["status_id"],
        status=classification["status"],
        time=convert_timestamp(
            parsed_log.get("timestamp")
        ),

        message=parsed_log.get("message"),

        metadata=OCSFMetadata(
            version="1.8.0",
            uid=event_id,
            original_time=parsed_log.get("timestamp"),
        ),

        device=OCSFDevice(
            hostname=parsed_log.get("hostname")
        ),

        process=OCSFProcess(
            name=parsed_log.get("process_name"),
            pid=parsed_log.get("process_id"),
        ),

        http=http_data,
        user=user_data,
        src_endpoint=src_endpoint_data,
        dst_endpoint=dst_endpoint_data,
        disposition_id=disposition_id,
        disposition=disposition,
        unmapped={
            "source_format": log_format,
            "cef_severity": parsed_log.get("cef_severity"),
        },
    )

    return NormalizedEvent(
        event_id=event_id,
        user_id=user_id,
        app_id=app_id,
        event=ocsf_event,
    )