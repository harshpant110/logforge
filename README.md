# LogForge

### Universal Log Pre-processing Framework

LogForge is a scalable, vendor-agnostic log processing framework designed to ingest, detect, parse, classify, normalize, and preserve logs from different infrastructure, network, application, and security environments.

The project is being developed as a solution for **Smart India Hackathon 2026 — SIH26156: Universal Log Pre-processing Framework**.

---

# 📌 Problem Statement

Modern systems generate logs in many different formats such as:

* Linux system logs
* Web server logs
* Application logs
* Network and firewall logs
* Cloud service logs
* Security logs

Because these logs have different structures, analyzing them together becomes difficult.

LogForge provides a common processing layer that converts different log formats into a **standardized event structure** that can later be consumed by SIEM systems, data lakes, monitoring platforms, and AI/ML pipelines.

---

# 🎯 Objectives

The main objectives of LogForge are to:

* Support multiple log formats
* Automatically detect the format of incoming logs
* Parse logs and extract useful fields
* Classify security-related events
* Normalize logs into a common OCSF-based event structure
* Preserve original log information
* Maintain user and application identification
* Make it easy to add new parsers
* Handle processing failures safely
* Support Dead Letter Queue (DLQ) based recovery
* Support scalable log processing
* Provide analytics-ready events
* Support containerized and cloud-based deployment

---

# 🏗️ High-Level Architecture

```text
                         LOG SOURCES
                              │
          ┌───────────────────┼────────────────────┐
          │                   │                    │
        Syslog              JSON                Apache
          │                   │                    │
          │                   │                    │
          └───────────────────┼────────────────────┘
                              │
                              ▼
                        Kafka Topic
                         raw-logs
                              │
                              ▼
                    ┌──────────────────┐
                    │  Kafka Consumer  │
                    └────────┬─────────┘
                             │
                             ▼
                     Format Detection
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
      Syslog               JSON                Apache
        │                    │                    │
        │                  CEF                  │
        └────────────────────┼────────────────────┘
                             │
                             ▼
                       Parser Registry
                             │
                             ▼
                          Parser
                             │
                             ▼
                        Classifier
                             │
                             ▼
                        OCSF Mapper
                             │
                             ▼
                    Normalized OCSF Event
                             │
                  ┌──────────┴───────────┐
                  │                      │
                  ▼                      ▼
             Future Storage        Future Analytics


                  PROCESSING FAILURE
                          │
                          ▼
                    Kafka DLQ Topic
                   logforge-dlq
                          │
                          ▼
                    DLQ Replayer
                          │
                          ▼
                       raw-logs
```

---

# ✅ Work Completed So Far

The backend processing worker has been implemented and tested locally.

The current pipeline supports:

```text
Kafka
  ↓
Consumer
  ↓
Format Detection
  ↓
Parser Registry
  ↓
Parser
  ↓
Event Classification
  ↓
OCSF Mapping
  ↓
Normalized Event
```

It also includes failure handling:

```text
Processing Failure
       ↓
      DLQ
       ↓
DLQ Replayer
       ↓
    raw-logs
       ↓
   Processing
```

---

# 1. Kafka Integration

Kafka is being used as the message queue between log ingestion and processing.

A Kafka topic named:

```text
raw-logs
```

is used to receive incoming log messages.

Each message contains:

```json
{
  "event_id": "unique-event-id",
  "user_id": 1,
  "app_id": 10,
  "raw_log": "original log message"
}
```

### Why this structure?

The event contains:

* `event_id` — uniquely identifies the log event
* `user_id` — identifies the user/tenant
* `app_id` — identifies the application
* `raw_log` — preserves the original log

This allows every processed event to remain associated with the correct user and application.

---

# 2. Kafka Producer

A Kafka producer has been implemented to send raw logs to the `raw-logs` topic.

The producer:

* Creates a unique `event_id`
* Adds `user_id`
* Adds `app_id`
* Preserves the complete original log
* Serializes the message as JSON
* Sends the message to Kafka

Example:

```text
Application
     │
     ▼
Kafka Producer
     │
     ▼
raw-logs
```

---

# 3. Kafka Consumer

A Kafka consumer has been implemented to continuously read logs from the `raw-logs` topic.

The consumer:

1. Receives a Kafka message
2. Decodes the message
3. Validates the JSON
4. Sends the message to the processing pipeline
5. Receives a normalized OCSF event
6. Commits the Kafka offset after successful processing

The consumer uses manual offset commits so that successful processing is explicitly acknowledged.

---

# 4. Automatic Log Format Detection

A format detector has been implemented to automatically identify incoming log formats.

Currently supported formats:

* **Syslog**
* **JSON**
* **Apache Access Log**
* **CEF**

If a log does not match a supported format, it is classified as:

```text
unknown
```

and the processor rejects it.

### Example

Input:

```text
Sep 6 12:00:01 server sshd[1234]: Failed password for amit
```

Detected as:

```text
syslog
```

CEF example:

```text
CEF:0|SecurityVendor|Firewall|1.0|100|Login Failed|5|src=192.168.1.10
```

Detected as:

```text
cef
```

---

# 5. Log Parsers

Log parsers convert raw log strings into structured Python dictionaries.

## Syslog Parser

The Syslog parser extracts:

* Timestamp
* Hostname
* Process name
* Process ID
* Message

Example:

```text
Sep 6 12:00:01 server sshd[1234]: Failed password for amit
```

is converted into structured fields.

---

## JSON Parser

The JSON parser processes structured JSON logs.

Common fields extracted include:

* Timestamp
* Hostname
* Process name
* Process ID
* Message

Example:

```json
{
  "timestamp": "2026-09-06T12:00:01Z",
  "hostname": "server",
  "process_name": "app",
  "process_id": 1234,
  "message": "Application started"
}
```

---

## Apache Access Log Parser

The Apache parser extracts fields such as:

* Source IP
* Timestamp
* HTTP method
* Request path
* HTTP protocol
* Status code
* Response size
* Referrer
* User agent

Example:

```text
192.168.1.10 - - [06/Sep/2026:12:00:01 +0000] "GET /login HTTP/1.1" 401 512 "-" "Mozilla/5.0"
```

These fields are later mapped into the normalized HTTP event structure.

---

## CEF Parser

CEF support has been added to allow LogForge to process **Common Event Format** logs commonly produced by security products, firewalls, SIEM-related systems, and security appliances.

Example:

```text
CEF:0|SecurityVendor|Firewall|1.0|100|Login Failed|5|src=192.168.1.10 dst=10.0.0.5 spt=52144 dpt=443 proto=TCP suser=amit
```

The CEF parser extracts:

* CEF version
* Vendor
* Product
* Product version
* Event ID
* Event name
* CEF severity
* Source IP
* Destination IP
* Source port
* Destination port
* Protocol
* Action
* Username
* Message

The parser also supports CEF extension values containing spaces.

For example:

```text
msg=User login failed from unknown device
```

is preserved as a single message value.

Common CEF escape sequences are also handled, including:

```text
\|
\=
\n
\r
\\
```

---

# 6. Parser Registry

A parser registry has been introduced so that the processor does not require large `if/else` blocks for every log format.

The flow is:

```text
Detected Format
       │
       ▼
Parser Registry
       │
       ├── syslog → Syslog Parser
       ├── json   → JSON Parser
       ├── apache → Apache Parser
       └── cef    → CEF Parser
```

The registry makes the architecture easier to extend.

Adding another format generally requires:

1. Creating the parser
2. Adding format detection
3. Registering the parser
4. Adding tests

---

# 7. Event Classification

A basic event classifier has been implemented to identify the type and security characteristics of processed events.

## Authentication Events

### Failed Authentication

The classifier recognizes messages such as:

```text
Failed password
authentication failure
login failed
```

and classifies them as:

```text
Event:       Authentication
Activity:    Logon
Status:      Failure
Severity:    High
```

---

### Successful Authentication

Messages such as:

```text
Accepted password
login successful
authentication successful
```

are classified as:

```text
Event:       Authentication
Activity:    Logon
Status:      Success
Severity:    Low
```

---

# 8. HTTP / Apache Event Classification

Apache access logs are classified as HTTP activity based on:

* HTTP method
* HTTP status code

Supported HTTP methods include:

```text
GET
POST
PUT
DELETE
HEAD
OPTIONS
CONNECT
TRACE
PATCH
```

Status codes are used to determine the event status and severity.

Examples:

```text
2xx / 3xx
    ↓
Success

401 / 403
    ↓
Failure / High severity

Other 4xx
    ↓
Failure / Medium severity

5xx
    ↓
Failure / Critical severity
```

---

# 9. CEF Severity Mapping

CEF provides severity values on a scale from:

```text
0 - 10
```

LogForge maps these values into OCSF severity levels.

Current mapping:

```text
CEF 0 - 3  → OCSF Low
CEF 4 - 6  → OCSF Medium
CEF 7 - 8  → OCSF High
CEF 9 - 10 → OCSF Critical
```

For example:

```text
CEF severity = 5
        ↓
OCSF severity = Medium
```

This allows security events from different vendors to be represented using a common severity model.

---

# 10. Network and Firewall Events

CEF network/security events containing fields such as:

```text
src
dst
spt
dpt
proto
act
```

can be classified as network activity.

The normalized event can contain:

* Source IP
* Source port
* Destination IP
* Destination port
* Protocol
* Action
* Severity
* Status

Example:

```text
src=192.168.1.10
dst=10.0.0.5
spt=52144
dpt=443
proto=TCP
act=blocked
```

is mapped into source and destination endpoints.

---

# 11. OCSF Normalization

The parsed logs are converted into a common **OCSF-based event structure**.

OCSF stands for:

**Open Cybersecurity Schema Framework**

The normalization flow is:

```text
Raw Log
   │
   ▼
Format Detection
   │
   ▼
Parser
   │
   ▼
Structured Log
   │
   ▼
Classifier
   │
   ▼
OCSF Mapper
   │
   ▼
Normalized Event
```

The current implementation targets:

```text
OCSF 1.8.0
```

The normalized event includes fields such as:

* Category
* Category UID
* Class
* Class UID
* Activity
* Activity ID
* Type
* Type UID
* Severity
* Status
* Disposition
* Timestamp
* Message
* Metadata
* Device
* Process
* User
* Source endpoint
* Destination endpoint
* HTTP information
* Unmapped information

---

# 12. OCSF Event Envelope

LogForge maintains its own application-level envelope around the OCSF event.

Example:

```json
{
  "event_id": "cef-001",
  "user_id": 1,
  "app_id": 10,
  "event": {
    "class_uid": 3002,
    "category_uid": 3,
    "activity_id": 1,
    "type_uid": 300201,
    "severity_id": 3,
    "severity": "Medium",
    "status_id": 2,
    "status": "Failure"
  }
}
```

The fields:

```text
event_id
user_id
app_id
```

belong to the LogForge application layer.

They are not treated as OCSF fields.

This allows the larger LogForge platform to maintain multi-tenant ownership while keeping the event itself OCSF-oriented.

---

# 13. OCSF User and Endpoint Mapping

CEF logs can contain user and network information.

For example:

```text
suser=amit
src=192.168.1.10
spt=52144
dst=10.0.0.5
dpt=443
proto=TCP
```

These are mapped into structured OCSF objects.

### User

```json
{
  "user": {
    "name": "amit"
  }
}
```

### Source Endpoint

```json
{
  "src_endpoint": {
    "ip": "192.168.1.10",
    "port": 52144,
    "protocol": "TCP"
  }
}
```

### Destination Endpoint

```json
{
  "dst_endpoint": {
    "ip": "10.0.0.5",
    "port": 443,
    "protocol": "TCP"
  }
}
```

---

# 14. OCSF Disposition Mapping

Network/security events can contain an action such as:

```text
act=blocked
```

or:

```text
act=allowed
```

LogForge maps these into OCSF disposition information.

Current mappings:

```text
allowed
allow
permitted
permit
        ↓
Allowed

blocked
blocked
denied
deny
        ↓
Blocked
```

Example:

```json
{
  "disposition_id": 2,
  "disposition": "Blocked"
}
```

This allows the normalized event to retain the security-control outcome of a network event.

---

# 15. Timestamp Normalization

Different log formats represent timestamps differently.

LogForge converts supported timestamps into:

```text
Unix Epoch Milliseconds
```

This provides downstream systems with a consistent timestamp representation.

Currently supported timestamp formats include:

### ISO-8601

```text
2026-09-06T12:00:01Z
```

### Apache

```text
06/Sep/2026:12:00:01 +0000
```

### Traditional Syslog

```text
Sep 6 12:00:01
```

Traditional Syslog does not contain a year or timezone, so the current implementation uses configured/default assumptions when converting it.

---

# 16. Dead Letter Queue (DLQ)

A Dead Letter Queue has been implemented for messages that fail during processing.

The DLQ topic is:

```text
logforge-dlq
```

The failure flow is:

```text
raw-logs
    │
    ▼
Kafka Consumer
    │
    ▼
Processing
    │
    X
    │
    ▼
logforge-dlq
```

A DLQ message stores:

* Original message
* Processing error
* Kafka topic
* Kafka partition
* Kafka offset

Example:

```json
{
  "original_message": {
    "event_id": "failed-001",
    "user_id": 1,
    "app_id": 10,
    "raw_log": "invalid log"
  },
  "error": "Unsupported log format",
  "kafka": {
    "topic": "raw-logs",
    "partition": 0,
    "offset": 123
  }
}
```

This preserves enough information to investigate and recover failed events.

---

# 17. DLQ Replayer

A DLQ replayer has been implemented to recover failed messages.

The replayer:

1. Reads messages from `logforge-dlq`
2. Extracts the original message
3. Sends the original message back to `raw-logs`
4. Commits the DLQ message after successful replay

Flow:

```text
logforge-dlq
      │
      ▼
DLQ Replayer
      │
      ▼
original_message
      │
      ▼
raw-logs
      │
      ▼
Normal Worker Pipeline
```

This allows failed logs to be processed again without manually reconstructing the original Kafka message.

---

# 18. Error Handling

The Kafka worker uses manual offset commits.

Successful processing:

```text
Receive Message
      ↓
Process Message
      ↓
Normalize Event
      ↓
Commit Offset
```

Processing failure:

```text
Receive Message
      ↓
Processing Error
      ↓
Send to DLQ
      ↓
Commit Original Offset
```

This prevents a permanently failing message from continuously blocking the consumer.

---

# 19. Testing

Automated tests have been implemented using:

**pytest**

The test suite currently covers:

* Format detection
* Syslog parsing
* JSON parsing
* Apache parsing
* CEF parsing
* CEF escaped characters
* CEF message fields containing spaces
* Event classification
* Authentication classification
* HTTP classification
* Network classification
* CEF severity mapping
* User mapping
* Endpoint mapping
* OCSF mapping
* OCSF disposition mapping
* Timestamp conversion
* Processor behavior
* Unknown format handling
* Kafka-related processing behavior
* DLQ producer behavior
* DLQ replayer behavior
* End-to-end processing

### Current test status

```text
39 tests passed
```

The complete local automated test suite currently passes successfully.

---

# 20. End-to-End Kafka Pipeline

The complete worker pipeline has been tested locally.

```text
Kafka Producer
      │
      ▼
   raw-logs
      │
      ▼
Kafka Consumer
      │
      ▼
   Processor
      │
      ▼
Format Detector
      │
      ▼
Parser Registry
      │
      ▼
    Parser
      │
      ▼
  Classifier
      │
      ▼
  OCSF Mapper
      │
      ▼
Normalized Event
```

The pipeline has been tested with multiple log formats, including:

```text
Syslog
JSON
Apache
CEF
```

---

# 21. Example Normalized Authentication Event

Input:

```text
Sep 6 12:00:01 server sshd[1234]: Failed password for amit
```

The event is detected as Syslog and classified as an authentication failure.

Example normalized result:

```json
{
  "event_id": "unique-event-id",
  "user_id": 1,
  "app_id": 10,
  "event": {
    "category_uid": 3,
    "category_name": "Identity & Access Management",
    "class_uid": 3002,
    "class_name": "Authentication",
    "activity_id": 1,
    "activity_name": "Logon",
    "type_uid": 300201,
    "type_name": "Authentication: Logon",
    "severity_id": 4,
    "severity": "High",
    "status_id": 2,
    "status": "Failure",
    "message": "Failed password for amit"
  }
}
```

---

# 22. Example CEF Event

Input:

```text
CEF:0|SecurityVendor|Firewall|1.0|100|Login Failed|5|src=192.168.1.10 dst=10.0.0.5 spt=52144 dpt=443 proto=TCP suser=amit
```

The event is:

```text
Detected Format
      ↓
CEF
      ↓
CEF Parser
      ↓
Authentication Classification
      ↓
OCSF Mapping
```

The resulting event contains:

```text
Class:
Authentication

Category:
Identity & Access Management

Activity:
Logon

Status:
Failure

CEF Severity:
5

OCSF Severity:
Medium

User:
amit

Source IP:
192.168.1.10

Source Port:
52144

Destination IP:
10.0.0.5

Destination Port:
443

Protocol:
TCP
```

---

# 23. Example Firewall Blocked Event

Input:

```text
CEF:0|SecurityVendor|Firewall|1.0|100|Connection Blocked|8|src=192.168.1.10 dst=10.0.0.5 spt=52144 dpt=443 proto=TCP act=blocked
```

The event is classified as network activity.

Example normalized information:

```text
Category:
Network Activity

Class:
Network Activity

CEF Severity:
8

OCSF Severity:
High

Status:
Failure

Disposition:
Blocked

Source:
192.168.1.10:52144

Destination:
10.0.0.5:443

Protocol:
TCP
```

---

# 📂 Current Backend Structure

```text
backend/
│
├── app/
│   ├── __init__.py
│   │
│   ├── consumer.py
│   ├── producer.py
│   ├── processor.py
│   ├── dlq_replayer.py
│   │
│   ├── detector/
│   │   ├── __init__.py
│   │   └── format_detector.py
│   │
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── syslog_parser.py
│   │   ├── json_parser.py
│   │   ├── apache_parser.py
│   │   ├── cef_parser.py
│   │   └── parser_registry.py
│   │
│   ├── mapper/
│   │   ├── __init__.py
│   │   ├── classifier.py
│   │   └── ocsf_mapper.py
│   │
│   └── models/
│       ├── __init__.py
│       └── event.py
│
├── tests/
│   ├── test_detector.py
│   ├── test_syslog_parser.py
│   ├── test_json_parser.py
│   ├── test_apache_parser.py
│   ├── test_cef_parser.py
│   ├── test_classifier.py
│   ├── test_timestamp.py
│   ├── test_processor.py
│   ├── test_integration.py
│   ├── test_apache_integration.py
│   ├── test_cef_integration.py
│   └── test_dlq_replayer.py
│
├── pyproject.toml
└── .gitignore
```

---

# 🚧 Upcoming Work

The current implementation focuses on the **log processing and normalization worker**.

Planned improvements include:

* Add additional log formats
* Improve format detection
* Add more event classifications
* Expand OCSF coverage
* Improve OCSF Security Control mapping
* Add more network/firewall event mappings
* Add Elasticsearch integration
* Add raw log storage using MinIO/Parquet
* Improve retry and failure handling
* Handle malformed JSON/UTF-8 messages through DLQ
* Add idempotent processing
* Add duplicate-event protection
* Containerize the worker
* Integrate with the complete LogForge ingestion and backend system
* Add monitoring and observability
* Prepare the system for distributed deployment

---

# 🛠️ Technologies Used

* **Python** — Log processing
* **Apache Kafka** — Message streaming
* **Pydantic** — Data validation and event models
* **Pytest** — Automated testing
* **OCSF** — Common cybersecurity event schema
* **Docker** — Local Kafka environment and future containerization
* **Regular Expressions** — Log format detection and parsing
* **JSON** — Log/message serialization

---

# 📈 Current Status

### Backend Worker: 🟢 Working

The current worker successfully performs:

```text
Receive Log
     ↓
Read from Kafka
     ↓
Detect Format
     ↓
Select Parser
     ↓
Parse Log
     ↓
Classify Event
     ↓
Normalize to OCSF
     ↓
Return Structured Event
```

Failure recovery is also implemented:

```text
Processing Failure
       ↓
      DLQ
       ↓
DLQ Replayer
       ↓
    raw-logs
       ↓
Normal Processing
```

### Current Supported Formats

```text
┌─────────────────────────┐
│ Syslog                  │
│ JSON                    │
│ Apache Access Logs      │
│ CEF                     │
└─────────────────────────┘
```

### Current Processing Capabilities

```text
Kafka Integration        ✅
Kafka Producer           ✅
Kafka Consumer           ✅
Format Detection         ✅
Syslog Parser            ✅
JSON Parser              ✅
Apache Parser            ✅
CEF Parser               ✅
Parser Registry          ✅
Event Classification     ✅
HTTP Classification      ✅
Network Classification   ✅
CEF Severity Mapping     ✅
OCSF Normalization       ✅
Timestamp Normalization  ✅
User Mapping             ✅
Endpoint Mapping         ✅
Disposition Mapping      ✅
DLQ Handling             ✅
DLQ Replayer             ✅
Automated Tests          ✅
```

### Test Status

```text
39 tests passed
```

---

# 🔄 Current Worker Pipeline

```text
                     ┌───────────────┐
                     │   Raw Logs    │
                     └───────┬───────┘
                             │
                             ▼
                     ┌───────────────┐
                     │     Kafka     │
                     │   raw-logs    │
                     └───────┬───────┘
                             │
                             ▼
                     ┌───────────────┐
                     │    Consumer   │
                     └───────┬───────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Format Detector │
                    └────────┬────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
         Syslog            JSON            Apache
            │                │                │
            └────────────────┼────────────────┘
                             │
                             ▼
                            CEF
                             │
                             ▼
                    ┌─────────────────┐
                    │ Parser Registry │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     Parser      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   Classifier    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   OCSF Mapper   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Normalized Event│
                    └─────────────────┘
```

Failure path:

```text
                 Processing Error
                       │
                       ▼
                ┌───────────────┐
                │  logforge-dlq │
                └───────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │ DLQ Replayer  │
                └───────┬───────┘
                        │
                        ▼
                     raw-logs
```

---

# 👨‍💻 Development

The project is being developed incrementally.

Each processing component is implemented and tested locally before integration with the complete LogForge platform.

The current focus is building a reliable and extensible **universal log preprocessing pipeline** before adding the downstream storage and analytics components.

---

# 📌 Current Milestone

```text
Milestone: Core Log Processing Worker

Status: 🟢 Completed

Kafka                  ✅
Multiple Parsers       ✅
Format Detection       ✅
Parser Registry        ✅
Classification         ✅
OCSF Normalization     ✅
Timestamp Handling     ✅
CEF Support            ✅
Network Events         ✅
DLQ                    ✅
DLQ Replay             ✅
Automated Testing      ✅

Next:
Storage + Extended Normalization + Reliability
```
