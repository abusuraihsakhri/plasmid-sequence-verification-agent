# Plasmid Sequence Verification Agent

> **Domain:** Clinical Decision Support & Biomedical Computing  
> **Reference Guidelines & Standards:** `Standard Clinical Formulations & ISO/IEC Quality Frameworks`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## 📖 What It Does

**Plasmid Sequence Verification Agent** is an advanced analytical and computational platform implementing Gibson / Golden Gate assembly junction boundary, ORF & cassette auditor. It provides a multi-worker evaluation pipeline that classifies task payloads by urgency, enforces zero-PHI outbound data protection, and maintains a tamper-evident HMAC-SHA256 audit trail.

---

## ⚙️ Key Capabilities & Algorithmic Modules

- **Deterministic Calculation Engine**: Strict compliance with standard reference formulations and thresholds.
- **Risk & Urgency Classification**: Multi-tier categorization (ROUTINE, ELEVATED, CRITICAL_STAT) with automated clinical/operational action recommendations.
- **Validation & Guardrails**: Rigorous input bounds checking, length limits, and anomaly detection.
- **Multi-Worker Evaluation Pipeline**: InvariantQCWorker, SafetyEscalationWorker, and ProtocolConformanceWorker.

---

## 💻 CLI Quickstart & Usage

### Installation
```bash
pip install -e .
```

### 1. Run Single Audit
```bash
python cli.py audit --task-id TASK-001 --target KEY-01 --primary 28.5 --secondary 14.2 --critical --status DISCORDANT
```

### 2. Supervisory Chat
```bash
python cli.py chat "What is the system status?"
```

### 3. Batch CSV Processing
```bash
python cli.py batch -i sample.csv -o results.csv
```

### 4. Verify Audit Trail Integrity
```bash
python cli.py verify-audit
```

### 5. Launch REST API Server
```bash
python cli.py serve --host 127.0.0.1 --port 8000
```

### Input Data Schema

| Field | Type | Description | Requirement |
|:------|:-----|:------------|:------------|
| `task_id` | string | Unique task / case identifier | Required |
| `target_identifier` | string | Entity or genomic target | Required |
| `primary_metric` | float | Primary measurement or score | Required |
| `secondary_metric` | float | Secondary kinetic or confidence score | Optional (default: 0.0) |
| `is_critical_flag` | bool | Emergency escalation trigger | Optional (default: false) |
| `status_descriptor` | string | Status code or phenotype descriptor | Optional (default: "NOMINAL") |

---

## 🛡️ Security & Enterprise Architecture

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, emails, DOB, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs for every evaluation and state transition.
* **Input Validation:** Pydantic models enforce maximum field lengths and strip whitespace.
* **Path Traversal Protection:** Batch file operations resolve and validate paths securely.
* **Secure Key Management:** Audit signing key sourced from `AUDIT_SECRET_KEY` environment variable; falls back to a random session key with a logged warning if unset.
* **Air-Gapped LLM Reasoning Adapter:** Agnostic integration for local Ollama instances (`llama3`, `mistral`), Claude 3.5 Sonnet, GPT-4o, and deterministic test mocks.
* **Active Learning Bayesian Calibration:** Dynamic tracker updating worker reliability weights and monitoring Brier calibration drift.
* **FastAPI & Prometheus Telemetry:** Exposes OpenAPI 3.1 REST endpoints and operational Prometheus metrics (`/metrics`).

---

## 🧪 Testing & Verification

Run the automated test suite:

```bash
pytest -v
```

Execute high-throughput batch simulation benchmarks:

```bash
python simulator.py 1000
```

---

## 🐳 Container Deployment

### Docker
```bash
docker build -t plasmid-sequence-verification-agent .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secret-key plasmid-sequence-verification-agent
```

### Docker Compose
Create a `.env` file:
```
AUDIT_SECRET_KEY=your-production-secret-key
```

Then run:
```bash
docker compose up --build
```

---

## 📁 Project Structure

```
plasmid-sequence-verification-agent/
├── agents/                  # Core agent modules (supervisor, workers, audit, PHI guard)
│   ├── api.py               # FastAPI REST server
│   ├── base.py              # Security, PHI guard, HMAC audit trail
│   ├── models.py            # Pydantic data models
│   ├── supervisor.py        # Multi-worker orchestrator
│   ├── workers.py           # Specialized evaluation workers
│   ├── llm_factory.py       # LLM provider factory
│   ├── learning.py          # Bayesian calibration engine
│   ├── metrics.py           # Prometheus metrics collector
│   └── streamer.py          # WebSocket telemetry broadcaster
├── plasmid_check/           # Frontier domain engine
│   ├── agents.py            # Sub-agent implementations
│   ├── engine.py            # Core algorithmic engine
│   ├── models.py            # Data models
│   ├── cli.py               # Frontier CLI
│   └── server.py            # Frontier FastAPI server
├── tests/                   # Pytest test suite
├── web/index.html           # Operations console UI
├── cli.py                   # Main CLI entry point
├── enrichment.py            # Enrichment feature engines
├── simulator.py             # High-throughput simulation
├── pyproject.toml           # Project configuration
├── Dockerfile               # Container build
└── docker-compose.yml       # Multi-service orchestration
```
