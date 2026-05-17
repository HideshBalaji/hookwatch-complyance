# HookWatch — Webhook Reliability & Replay Intelligence Platform

HookWatch is an intelligent webhook reliability and replay analysis platform built for the **Complyance Hackathon 2026**. 

The system monitors webhook delivery attempts, analyzes retry patterns, detects anomalies, predicts replay safety, and generates operational recovery recommendations using Machine Learning.

---

## 🚀 Current Project State

We have successfully completed **Phases 1, 2, and 3** of the MVP! The backend is now a fully operational Machine Learning API powered by FastAPI, Supabase PostgreSQL, Pandas, and XGBoost.

**Key Achievements:**
1. **Database Architecture:** Seamlessly converted raw CSV data into a fully relational Supabase PostgreSQL schema using SQLAlchemy ORM.
2. **Automated ETL Pipeline:** Engineered a Pandas script (`load_data.py`) to bulk load 35,000+ delivery logs into the production database.
3. **Analytics Engine:** Built aggregation services to detect endpoint instability, retry decay patterns, and replay frequency.
4. **ML Feature Engineering:** Automated the extraction and transformation of raw logs into a clean, mathematically-ready ML matrix (`features.csv`).
5. **Replay Intelligence (AI):** Trained an **XGBoost Classifier** to predict webhook recovery and an **Isolation Forest** model to flag anomalous webhook traffic.
6. **Live API:** Exposed the entire ML pipeline through RESTful FastAPI endpoints.

---

## 🛠 Tech Stack

### Frontend (Pending - Phase 4)
* React
* Tailwind CSS

### Backend & Database
* **API Framework:** FastAPI
* **Database:** Supabase PostgreSQL
* **ORM:** SQLAlchemy / psycopg2

### Data Processing & Machine Learning
* **ETL & Feature Engineering:** Pandas
* **Classification (Replay Safety):** XGBoost
* **Anomaly Detection:** scikit-learn (Isolation Forest)

---

## 📂 Architecture & Folder Structure

```text
backend/
├── app/
│   ├── api/
│   │   ├── analytics.py       # REST endpoints for dashboard analytics
│   │   └── intelligence.py    # REST endpoint for ML inference
│   ├── database/
│   │   └── db.py              # Supabase PostgreSQL engine configuration
│   ├── models/
│   │   └── webhook.py         # SQLAlchemy DB schemas
│   ├── ml/
│   │   ├── models/            # Serialized .pkl ML models
│   │   ├── feature_engineering.py  # Builds ML features matrix
│   │   └── train_models.py    # Trains XGBoost & Isolation Forest
│   ├── services/
│   │   ├── analytics.py       # Pandas-driven database aggregations
│   │   └── intelligence.py    # Merges ML models with business rules
│   └── utils/
│
├── datasets/                  # Raw simulated logs
│   └── processed/             # Cleaned features.csv for model training
├── scripts/
│   └── load_data.py           # Ingests CSVs to Supabase using Pandas
│
├── requirements.txt
├── .env                       # (Contains DATABASE_URL)
└── main.py                    # FastAPI root application
```

---

## 🧠 Machine Learning Workflow

1. **Feature Engineering:** Pandas computes features like `retry_count`, `timeout_ratio`, and `endpoint_health_score`, explicitly dropping variables that cause data leakage.
2. **Anomaly Detection (Isolation Forest):** Detects highly abnormal payloads, retry bursts, or instability representing the top ~5% outlier events.
3. **Prediction Engine (XGBoost):** Classifies the failed webhook event. It dynamically handles the 85/15 class imbalance using `scale_pos_weight` and predicts if an event will gracefully recover if replayed.

---

## 🌐 Live API Endpoints

### 1. Replay Intelligence
Predicts if a failed event is safe to replay, detects anomalies, and issues operational recommendations.
```http
GET /api/v1/intelligence/{event_id}
```
**Sample Response:**
```json
{
  "event_id": "evt_dup_c43c568e",
  "delivery_state": "recovered",
  "failure_reason": "timeout",
  "safe_to_replay": true,
  "is_anomaly": false,
  "recommended_action": "trigger_auto_replay",
  "metrics": {
    "endpoint_health": 0.85,
    "timeout_ratio": 0.0
  }
}
```

### 2. Analytics Dashboard Routes
Used to populate the upcoming frontend React dashboard.
```http
GET /api/v1/analytics/endpoints/instability
GET /api/v1/analytics/retry/patterns
GET /api/v1/analytics/replays
```

---

## ⚙️ Setup Instructions

### 1. Create Virtual Environment
```bash
cd backend
python -m venv venv
```

### 2. Activate Environment
**Windows:**
```bash
venv\Scripts\activate
```
**Linux / Mac:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Database
Create a `.env` file in the `backend/` directory with your Supabase credentials:
```env
DATABASE_URL=postgresql://postgres.yourproject:encoded%40password@aws-0-region.pooler.supabase.com:6543/postgres
```

### 5. Run the Server
```bash
uvicorn main:app --reload
```
Navigate to `http://127.0.0.1:8000/docs` to test the API!

---

## 🗺 MVP Roadmap

✅ **Phase 1: Foundation**
* Dataset Generation
* PostgreSQL Schema & Config
* FastAPI Setup

✅ **Phase 2: Data Pipeline**
* Bulk DB Ingestion (Pandas)
* Feature Engineering (`features.csv`)
* Retry Pattern Analysis

✅ **Phase 3: Replay Intelligence (AI)**
* Classification Model (XGBoost)
* Anomaly Detection (Isolation Forest)
* Intelligence API Endpoints

🚀 **Phase 4: Frontend (Up Next)**
* React + Tailwind Development
* HookWatch Operational Dashboard
* Replay Timeline Visualization

⏳ **Phase 5: Final Polish**
* End-to-End Integration
* Demo Flow

---

## 👨‍💻 Team 4BIT
**Complyance Hackathon 2026**
*Problem Statement ID: 5*

* Madhu Sankar S
* Hidesh Balaji C U
* Deepak Krishna Kumar
