# LogForge

### Universal Log Pre-processing Framework

LogForge is a scalable, vendor-agnostic log processing framework designed to ingest, parse, normalize, and preserve heterogeneous logs from diverse infrastructure, network, application, and cloud environments.

The project is developed as a solution for **Smart India Hackathon 2026 — SIH26156: Universal Log Pre-processing Framework**.

---

## 📌 Problem Statement

Modern organizations generate massive volumes of logs from different sources such as:

- Linux and Windows servers
- Network devices
- Firewalls
- Cloud platforms
- Applications
- Databases
- Containers
- IoT devices
- Security infrastructure

These systems produce logs in different formats and structures, making centralized analysis difficult.

Before logs can be effectively consumed by systems such as **SIEM platforms, data lakes, monitoring systems, and AI/ML pipelines**, they need to be parsed, standardized, and normalized.

LogForge addresses this problem by providing a common processing layer between heterogeneous log sources and downstream analytics systems.

---

## 🎯 Objectives

The primary objectives of LogForge are to:

- Ingest logs from multiple sources and formats
- Automatically identify supported log formats
- Parse unstructured and semi-structured logs
- Extract meaningful fields and attributes
- Normalize events into a common schema
- Preserve the complete original log
- Maintain traceability between raw and normalized events
- Support easy onboarding of new log sources
- Remain vendor-agnostic
- Provide analytics-ready output
- Support scalable and distributed processing
- Enable deployment in cloud, on-premise, and air-gapped environments
- Provide containerized and reproducible deployments

---

## 🏗️ High-Level Architecture

```text
                       LOG SOURCES
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
      Linux              Firewall             AWS
      Syslog                CEF               JSON
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   INGESTION   │
                    │     LAYER     │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │    PARSER     │
                    │     ENGINE     │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ NORMALIZATION │
                    │     ENGINE    │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │ UNIFIED EVENT │
                    │    SCHEMA     │
                    └───────┬───────┘
                            │
             ┌──────────────┼──────────────┐
             │              │              │
             ▼              ▼              ▼
           SIEM         Data Lake        AI / ML


             RAW LOG PRESERVATION
                     │
                     ▼
               Raw Storage
                     │
                     ▼
               Forensics /
                Auditing