def map_cef_severity(cef_severity: str | None) -> tuple[int, str]:
        """
        Convert CEF severity (0-10) to OCSF severity.
        """

        if cef_severity is None:
            return 0, "Unknown"

        try:
            severity = int(cef_severity)
        except ValueError:
            return 0, "Unknown"

        if severity <= 3:
            return 2, "Low"

        if severity <= 6:
            return 3, "Medium"

        if severity <= 8:
            return 4, "High"

        return 5, "Critical"
def classify_event(parsed_log: dict) -> dict:
    """
    Classify a parsed_log into an OCSF event.

    Currently supports basic authentication events.
    """
    
    if not parsed_log:
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

    message_lower = parsed_log.get("message", "").lower()
    cef_severity = parsed_log.get("cef_severity")

    # Failed authentication
    if (
        "failed password" in message_lower
        or "authentication failure" in message_lower
        or "login failed" in message_lower
    ):
        severity_id, severity = map_cef_severity(cef_severity)
        if cef_severity is None:
            severity_id, severity = 4, "High"
        return {
            "event_type": "authentication",
            "class_uid": 3002,
            "class_name": "Authentication",

            "category_uid": 3,
            "category_name": "Identity & Access Management",

            "activity_id": 1,
            "activity_name": "Logon",

            "type_name": "Authentication: Logon",

            "severity_id": severity_id,
            "severity": severity,
            "status_id": 2,
            "status": "Failure",
        }

    # Successful authentication
    if (
        "accepted password" in message_lower
        or "login successful" in message_lower
        or "authentication successful" in message_lower
    ):
        severity_id, severity = map_cef_severity(cef_severity)

        if cef_severity is None:
            severity_id = 2
            severity = "Low"
        return {
            "event_type": "authentication",
            "class_uid": 3002,
            "class_name": "Authentication",

            "category_uid": 3,
            "category_name": "Identity & Access Management",

            "activity_id": 1,
            "activity_name": "Logon",

            "type_name": "Authentication: Logon",

            "severity_id": severity_id,
            "severity": severity,

            "status_id": 1,
            "status": "Success",
        }
    # Network / firewall events
    action = parsed_log.get("action")

    if parsed_log.get("source_ip") and (
        parsed_log.get("destination_ip") or action
    ):
        cef_severity = parsed_log.get("cef_severity")

        if cef_severity is not None:
            severity_id, severity = map_cef_severity(
                cef_severity
            )
        else:
            severity_id, severity = 0, "Unknown"

        if action and action.lower() in {
            "blocked",
            "denied",
            "deny",
        }:
            status_id = 2
            status = "Failure"
        else:
            status_id = 1
            status = "Success"

        return {
            "event_type": "network",

            "class_uid": 4001,
            "class_name": "Network Activity",

            "category_uid": 4,
            "category_name": "Network Activity",

            "activity_id": 99,
            "activity_name": "Other",

            "type_name": "Network Activity: Other",

            "severity_id": severity_id,
            "severity": severity,

            "status_id": status_id,
            "status": status,
        }
    # HTTP / Apache events
    status_code = parsed_log.get("status_code")
    method = parsed_log.get("method")

    if status_code is not None and method:

        http_methods = {
            "GET": (3, "Get"),
            "POST": (4, "Post"),
            "PUT": (5, "Put"),
            "DELETE": (2, "Delete"),
            "HEAD": (5, "Head"),
            "OPTIONS": (6, "Options"),
            "CONNECT": (1, "Connect"),
            "TRACE": (7, "Trace"),
            "PATCH": (8, "Patch"),
        }

        activity_id, activity_name = http_methods.get(
            method.upper(),
            (99, "Other"),
        )

        if 200 <= status_code < 400:
            severity_id = 1
            severity = "Low"
            status_id = 1
            status = "Success"

        elif status_code == 401 or status_code == 403:
            severity_id = 3
            severity = "High"
            status_id = 2
            status = "Failure"

        elif 400 <= status_code < 500:
            severity_id = 2
            severity = "Medium"
            status_id = 2
            status = "Failure"

        else:
            severity_id = 4
            severity = "Critical"
            status_id = 2
            status = "Failure"

        return {
            "event_type": "http",

            "class_uid": 4002,
            "class_name": "HTTP Activity",

            "category_uid": 4,
            "category_name": "Network Activity",

            "activity_id": activity_id,
            "activity_name": activity_name,

            "type_name": f"HTTP Activity: {activity_name}",

            "severity_id": severity_id,
            "severity": severity,

            "status_id": status_id,
            "status": status,
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