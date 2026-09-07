# LogForge

### Universal Log Pre-processing Framework

LogForge is a scalable, vendor-agnostic log processing framework designed to ingest, parse, normalize, and preserve logs from different infrastructure, network, application, and cloud environments.

The project is being developed as a solution for **Smart India Hackathon 2026 — SIH26156: Universal Log Pre-processing Framework**.

---

## 📌 Problem Statement

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

## 🎯 Objectives

The main objectives of LogForge are to:

* Support multiple log formats
* Automatically detect the format of incoming logs
* Parse logs and extract useful fields
* Normalize logs into a common event structure
* Preserve the original log information
* Maintain user and application identification
* Make it easy to add new parsers
* Support scalable log processing
* Provide analytics-ready events
* Support containerized and cloud-based deployment

---

## 🏗️ High-Level Architecture

```text
                         LOG SOURCES
                              │
             ┌────────────────┼────────────────┐
             │                │                │
           Syslog           JSON            Apache
             │                │                │
             └────────────────┼────────────────┘
                              │
                              ▼
                         Kafka Topic
                         raw-logs
                              │
                              ▼
                     ┌─────────────────┐
                     │ Kafka Consumer   │
                     └────────┬────────┘
                              │
                              ▼
                     Format Detection
                              │
               ┌──────────────┼──────────────┐
               │              │              │
             Syslog          JSON          Apache
               │              │              │
               └──────────────┼──────────────┘
                              │
                              ▼
                         Parser Engine
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
                    ┌─────────┴─────────┐
                    │                   │
                    ▼                   ▼
              Future Storage      Future Analytics
```

---

# ✅ Work Completed So Far

The backend processing pipeline has been implemented and tested locally.

## 1. Kafka Integration

Kafka is being used as the message queue between log ingestion and processing.

A Kafka topic named `raw-logs` is used to receive incoming log messages.

Each message contains:

```json
{
  "event_id": "unique-event-id",
  "user_id": 1,
  "app_id": 10,
  "raw_log": "original log message"
}
```

This allows every log to remain associated with the correct user and application.

---

## 2. Kafka Producer

A Kafka producer has been implemented to send raw logs to the `raw-logs` topic.

The producer:

* Creates a unique `event_id`
* Adds `user_id`
* Adds `app_id`
* Stores the complete original log
* Sends the message to Kafka

---

## 3. Kafka Consumer

A Kafka consumer has been implemented to continuously read logs from the `raw-logs` topic.

The consumer:

1. Receives a Kafka message
2. Decodes the message
3. Validates the JSON
4. Sends the log to the processing pipeline
5. Produces a normalized event

Invalid messages are handled without stopping the worker.

---

## 4. Automatic Log Format Detection

A format detector has been implemented to identify the type of incoming log.

Currently supported detection:

* **Syslog**
* **JSON**
* **Apache Access Log**

Example:

```text
Sep 6 12:00:01 server sshd[1234]: Failed password for User123
```

is detected as:

```text
syslog
```

---

## 5. Log Parsers

Parsers have been implemented for multiple formats.

### Syslog Parser

Extracts fields such as:

* Timestamp
* Hostname
* Process name
* Process ID
* Message

Example:

```text
Sep 6 12:00:01 server sshd[1234]: Failed password for User123
```

is converted into structured data.

### JSON Parser

Processes structured JSON logs and extracts common fields such as:

* Timestamp
* Hostname
* Process name
* Process ID
* Message

### Apache Parser

An Apache access-log parser has also been added.

It can extract fields such as:

* Source IP
* Timestamp
* HTTP method
* Request path
* HTTP protocol
* Status code
* Response size
* Referrer
* User agent

---

## 6. Parser Registry

A parser registry has been introduced so that the processor does not need large `if/else` blocks for every log format.

The flow is:

```text
Detected Format
      │
      ▼
Parser Registry
      │
      ├── syslog → Syslog Parser
      ├── json   → JSON Parser
      └── apache → Apache Parser
```

This makes it easier to add new formats in the future.

For example, adding a CEF parser would only require registering the new parser.

---

## 7. Event Classification

A basic event classifier has been implemented.

It currently identifies authentication-related events such as:

### Failed Authentication

```text
Failed password
authentication failure
login failed
```

These are classified as:

```text
Event: Authentication
Activity: Logon
Status: Failure
Severity: High
```

### Successful Authentication

Messages such as:

```text
Accepted password
login successful
authentication successful
```

are classified as:

```text
Event: Authentication
Activity: Logon
Status: Success
Severity: Low
```

---

## 8. OCSF Normalization

The parsed logs are converted into a common **OCSF-based event structure**.

OCSF stands for **Open Cybersecurity Schema Framework**.

Instead of every log format having a completely different structure, LogForge converts them into a common format.

For example:

```text
Syslog
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

The current implementation includes OCSF fields such as:

* Category
* Class
* Activity
* Type
* Severity
* Status
* Timestamp
* Message
* Device
* Process
* Metadata

The current implementation targets **OCSF 1.8.0**.

---

## 9. Timestamp Normalization

Different log formats can represent timestamps differently.

The mapper converts supported timestamps into:

```text
Unix Epoch Milliseconds
```

This gives downstream systems a consistent timestamp format.

The implementation currently supports:

* ISO-8601 timestamps
* Traditional Syslog timestamps

---

## 10. Multi-Tenant Event Information

Each event keeps:

```text
event_id
user_id
app_id
```

This allows the larger LogForge system to associate processed logs with the correct user and application.

These fields are kept as a **LogForge application envelope** around the OCSF event rather than being treated as OCSF fields.

---

## 11. Testing

Automated tests have been added using **pytest**.

The tests currently cover:

* Format detection
* Syslog parsing
* JSON parsing
* Apache parsing
* Event classification
* Timestamp conversion
* OCSF mapping
* Processor behavior
* End-to-end processing

The complete local test suite currently passes successfully.

---

## 12. End-to-End Kafka Pipeline

The complete worker pipeline has been tested locally:

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

A real Syslog message was successfully sent through Kafka and converted into a normalized OCSF event.

Example result:

```json
{
  "event_id": "unique-event-id",
  "user_id": 1,
  "app_id": 10,
  "event": {
    "category_name": "Identity & Access Management",
    "class_name": "Authentication",
    "activity_name": "Logon",
    "type_name": "Authentication: Logon",
    "severity": "High",
    "status": "Failure"
  }
}
```

---

# 📂 Current Backend Structure

```text
backend/
│
├── app/
│   ├── consumer.py
│   ├── producer.py
│   ├── processor.py
│   │
│   ├── detector/
│   │   └── format_detector.py
│   │
│   ├── parsers/
│   │   ├── syslog_parser.py
│   │   ├── json_parser.py
│   │   ├── apache_parser.py
│   │   └── parser_registry.py
│   │
│   ├── mapper/
│   │   ├── classifier.py
│   │   └── ocsf_mapper.py
│   │
│   └── models/
│       └── event.py
│
├── tests/
│   ├── test_detector.py
│   ├── test_syslog_parser.py
│   ├── test_json_parser.py
│   ├── test_apache_parser.py
│   ├── test_classifier.py
│   ├── test_timestamp.py
│   ├── test_processor.py
│   └── test_integration.py
│
├── pyproject.toml
└── .gitignore
```

---

# 🚧 Upcoming Work

The current implementation focuses on the **log processing and normalization worker**.

Planned improvements include:

* Add more log formats such as CEF
* Improve format detection
* Add more event classifications
* Expand OCSF coverage
* Add Elasticsearch integration
* Add raw log storage using MinIO/Parquet
* Add retry and failure handling
* Add Dead Letter Queue (DLQ) support
* Add idempotent processing
* Containerize the worker
* Integrate with the complete LogForge ingestion and backend system
* Add monitoring and observability
* Prepare the system for distributed deployment

---

# 🛠️ Technologies Used

* **Python** — Log processing
* **Kafka** — Message streaming
* **Pydantic** — Data validation and event models
* **Pytest** — Automated testing
* **OCSF** — Common cybersecurity event schema
* **Docker** — Local Kafka environment and future containerization

---

# 📈 Current Status

### Backend Worker: 🟢 Working

The current worker can successfully:

```text
Receive Log
     ↓
Read from Kafka
     ↓
Detect Format
     ↓
Parse Log
     ↓
Classify Event
     ↓
Normalize to OCSF
     ↓
Return Structured Event
```

The core **Kafka → Parser → Classifier → OCSF** pipeline is working locally and has been covered with automated tests.

---

## 👨‍💻 Development

The project is being developed incrementally, with individual components tested locally before integration with the complete LogForge platform.
