from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from app.mapper.classifier import classify_event
from app.models.event import (
    NormalizedEvent,
    OCSFDevice,
    OCSFEvent,
    OCSFMetadata,
    OCSFProcess,
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
    
    classification = classify_event(
        parsed_log.get("message")
    )

    class_uid = classification["class_uid"]
    category_uid = classification["category_uid"]
    activity_id = classification["activity_id"]

    type_uid = class_uid * 100 + activity_id

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

        unmapped={
            "source_format": log_format,
        },
    )

    return NormalizedEvent(
        event_id=event_id,
        user_id=user_id,
        app_id=app_id,
        event=ocsf_event,
    )