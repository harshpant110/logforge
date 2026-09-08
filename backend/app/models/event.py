from typing import Any, Optional

from pydantic import BaseModel, Field


class OCSFMetadata(BaseModel):
    version: str = "1.8.0"
    uid: Optional[str] = None
    original_time: Optional[str] = None


class OCSFDevice(BaseModel):
    hostname: Optional[str] = None


class OCSFProcess(BaseModel):
    name: Optional[str] = None
    pid: Optional[int] = None

class OCSFUser(BaseModel):
    name: Optional[str] = None


class OCSFEndpoint(BaseModel):
    ip: Optional[str] = None
    hostname: Optional[str] = None
    port: Optional[int] = None
    protocol: Optional[str] = None


class OCSFHTTP(BaseModel):
    method: Optional[str] = None
    path: Optional[str] = None
    protocol: Optional[str] = None
    status_code: Optional[int] = None
    response_size: Optional[int] = None
    referrer: Optional[str] = None
    user_agent: Optional[str] = None
    source_ip: Optional[str] = None
class OCSFEvent(BaseModel):
    # OCSF classification
    activity_id: int
    activity_name: Optional[str] = None

    category_uid: int
    category_name: Optional[str] = None

    class_uid: int
    class_name: Optional[str] = None

    type_uid: int
    type_name: Optional[str] = None

    # Classification
    severity_id: int
    severity: Optional[str] = None
    
    status_id: int
    status: Optional[str] = None
    disposition_id: Optional[int] = None
    disposition: Optional[str] = None

    # Occurrence
    time: int

    # Primary
    message: Optional[str] = None

    # Context
    metadata: OCSFMetadata
    device: Optional[OCSFDevice] = None
    process: Optional[OCSFProcess] = None

    http: Optional[OCSFHTTP] = None

    user: Optional[OCSFUser] = None
    src_endpoint: Optional[OCSFEndpoint] = None
    dst_endpoint: Optional[OCSFEndpoint] = None
    
    raw_data: Optional[str] = None
    unmapped: Optional[dict[str, Any]] = None


class NormalizedEvent(BaseModel):
    """
    Application envelope around the OCSF event.

    user_id and app_id belong to LogForge's
    multi-tenant system, not the OCSF schema.
    """

    event_id: str
    user_id: int
    app_id: int

    event: OCSFEvent