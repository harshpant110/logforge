import re


CEF_PATTERN = re.compile(
    r"^CEF:(?P<version>\d+)\|"
    r"(?P<vendor>[^|]*)\|"
    r"(?P<product>[^|]*)\|"
    r"(?P<product_version>[^|]*)\|"
    r"(?P<event_id>[^|]*)\|"
    r"(?P<event_name>[^|]*)\|"
    r"(?P<severity>[^|]*)\|"
    r"(?P<extension>.*)$"
)

def unescape_cef(value: str) -> str:
    return (
        value
        .replace(r"\|", "|")
        .replace(r"\=", "=")
        .replace(r"\n", "\n")
        .replace(r"\r", "\r")
        .replace(r"\\", "\\")
    )

def parse_cef(raw_log: str) -> dict:
    """
    Parse a CEF log into structured fields.
    """

    match = CEF_PATTERN.match(raw_log)

    if not match:
        raise ValueError("Invalid CEF format")

    data = match.groupdict()

    extension = data["extension"]

    fields = {}

    matches = re.finditer(
        r"(\w+)=(.*?)(?=\s+\w+=|$)",
        extension,
    )

    for match in matches:
        key = match.group(1)
        value = unescape_cef(match.group(2))
        fields[key] = value

    
    return {
        "timestamp": fields.get("rt"),
        "hostname": fields.get("dvchost"),
        "process_name": None,
        "message": fields.get("msg") or data["event_name"],
        "process_id": None,
        "vendor": data["vendor"],
        "product": data["product"],
        "product_version": data["product_version"],
        "cef_event_id": data["event_id"],
        "event_name": data["event_name"],
        "cef_severity": data["severity"],

        "source_ip": fields.get("src"),
        "destination_ip": fields.get("dst"),
    

        "source_port": (
            int(fields["spt"])
            if fields.get("spt", "").isdigit()
            else None
        ),

        "destination_port": (
            int(fields["dpt"])
            if fields.get("dpt", "").isdigit()
            else None
        ),

        "protocol": fields.get("proto"),
        "action": fields.get("act"),
        "username": fields.get("suser"),
        
    }