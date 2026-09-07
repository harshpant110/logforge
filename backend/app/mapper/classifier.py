def classify_event(message: str | None) -> dict:
    """
    Classify a log message into an OCSF event.

    Currently supports basic authentication events.
    """

    if not message:
        return {
            "event_type": "unknown",
            "class_uid": 0,
            "category_uid": 0,
            "activity_id": 0,
            "activity_name": "Unknown",
            "severity_id": 0,
            "severity": "Unknown",
            "status_id": 0,
            "status": "Unknown",
        }

    message_lower = message.lower()

    # Failed authentication
    if (
        "failed password" in message_lower
        or "authentication failure" in message_lower
        or "login failed" in message_lower
    ):
        return {
            "event_type": "authentication",
            "class_uid": 2,
            "class_name": "Authentication",

            "category_uid": 3,
            "category_name": "Identity & Access Management",

            "activity_id": 1,
            "activity_name": "Logon",

            "type_name": "Authentication: Logon",

            "severity_id": 3,
            "severity": "High",

            "status_id": 2,
            "status": "Failure",
        }

    # Successful authentication
    if (
        "accepted password" in message_lower
        or "login successful" in message_lower
        or "authentication successful" in message_lower
    ):
        return {
            "event_type": "authentication",
            "class_uid": 2,
            "class_name": "Authentication",

            "category_uid": 3,
            "category_name": "Identity & Access Management",

            "activity_id": 1,
            "activity_name": "Logon",

            "type_name": "Authentication: Logon",

            "severity_id": 1,
            "severity": "Low",

            "status_id": 1,
            "status": "Success",
        }

    return {
        "event_type": "unknown",
        "class_uid": 0,
        "category_uid": 0,
        "activity_id": 0,
        "activity_name": "Unknown",
        "severity_id": 0,
        "severity": "Unknown",
        "status_id": 0,
        "status": "Unknown",
        "category_name": "Unknown",
        "class_name": "Unknown",
        "type_name": "Unknown",
    }