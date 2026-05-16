# HookWatch — Backend

HookWatch is an intelligent webhook reliability and replay analysis platform built for Complyance Hackathon 2026.

The system monitors webhook delivery attempts, analyzes retry patterns, detects anomalies, predicts replay safety, and generates operational recovery recommendations.

---

# Problem Statement

Modern invoice systems rely on webhooks to synchronize important events such as:

* invoice creation
* payment updates
* compliance status

However, webhook deliveries often fail due to:

* endpoint downtime
* invalid signatures
* rate limits
* network timeouts
* malformed responses
* duplicate retries

HookWatch helps reliability engineers and operations teams understand:

* what happened
* why it failed
* whether replaying is safe
* what action should be taken next

---

# Core Features

* Webhook delivery analysis
* Retry pattern intelligence
* Replay safety prediction
* Endpoint reliability monitoring
* Operational recovery recommendations
* Anomaly detection for abnormal webhook behavior
* Delivery state classification
* Risk scoring and replay intelligence

---

# Tech Stack

## Frontend

* React
* Tailwind CSS

## Backend

* FastAPI

## Database

* PostgreSQL

## Data Processing & ML

* Pandas
* XGBoost
* Isolation Forest

---

# Architecture Overview

```text
Webhook Events
        ↓
FastAPI Backend
        ↓
Webhook Processing & Validation
        ↓
PostgreSQL Storage
        ↓
Data Processing (Pandas)
        ↓
Anomaly Detection (Isolation Forest)
        ↓
Prediction & Classification (XGBoost)
        ↓
Replay Intelligence & Dashboard
```

---

# Dataset Information

Synthetic datasets were generated to simulate realistic webhook delivery systems.

## Dataset Statistics

* Webhook Events: 12,720
* Delivery Attempts: 35,436
* Endpoints: 600
* Replay Actions: 3,523
* Train Labels: 12,720
* Test Events: 3,180

## Generated Files

```text
datasets/
├── webhook_events.csv
├── delivery_attempts.csv
├── endpoints.csv
├── replay_actions.csv
├── labels_train.csv
└── events_test.csv
```

---

# Folder Structure

```text
backend/
├── app/
│   ├── api/
│   ├── core/
│   ├── database/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── ml/
│   └── utils/
│
├── datasets/
│   ├── webhook_events.csv
│   ├── delivery_attempts.csv
│   ├── endpoints.csv
│   ├── replay_actions.csv
│   ├── labels_train.csv
│   └── events_test.csv
│
├── scripts/
│   └── generate_dataset.py
│
├── docs/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── README.md
└── main.py
```

---

# ML Workflow

## Data Processing

Pandas is used for:

* feature engineering
* retry pattern analysis
* time-series processing
* preprocessing webhook delivery logs

## Anomaly Detection

Isolation Forest detects:

* retry bursts
* endpoint instability
* replay spikes
* abnormal delivery behavior

## Prediction Engine

XGBoost predicts:

* delivery state
* failure reason
* replay safety
* operational risk score

---

# Delivery States

The system classifies events into:

* delivered
* retrying
* failed
* expired
* duplicate
* recovered
* unsafe_to_replay

---

# Sample Prediction Output

```json
{
  "event_id": "evt_8b21a9",
  "delivery_state": "recovered",
  "failure_reason": "timeout",
  "attempts": 3,
  "safe_to_replay": false,
  "risk_score": 0.91,
  "priority": "mid"
}
```

---

# Setup Instructions

## Clone Repository

```bash
git clone <repo-url>
cd backend
```

## Create Virtual Environment

```bash
python -m venv venv
```

## Activate Environment

### Windows

```bash
venv\\Scripts\\activate
```

### Linux / Mac

```bash
source venv/bin/activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run FastAPI Server

```bash
uvicorn main:app --reload
```

---

# API Endpoints

## Health Check

```http
GET /health
```

## Ingest Webhook Event

```http
POST /webhooks
```

## Fetch Events

```http
GET /events
```

## Analytics & Predictions

```http
GET /analytics
```

---

# MVP Roadmap

## Phase 1

* Dataset Generation
* PostgreSQL Schema
* FastAPI Setup

## Phase 2

* Feature Engineering
* Retry Pattern Analysis
* Rule Engine

## Phase 3

* Classification
* Anomaly Detection
* Replay Intelligence

## Phase 4

* UI/UX Development
* Retry Timeline Visualization
* Endpoint Monitoring

## Phase 5

* Integration
* Demo Flow
* Final Polish

---

# Team

Team 4BIT

* Madhu Sankar S
* Hidesh Balaji C U
* Deepak Krishna Kumar

Complyance Hackathon 2026
Problem Statement ID: 5
