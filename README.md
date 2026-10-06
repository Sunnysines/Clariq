# CLARIQ — Evidence-Powered Decision Intelligence

> **"Turn live information into clear decisions."**

Clariq takes an open-ended decision question, searches the live web through **SerpApi**, collects multi-engine evidence, normalizes and verifies the findings, resolves real-world entities, analyzes positive and negative decision signals, detects hidden contradictions, and computes an explainable decision recommendation with a traceable confidence score.

---

## 🚀 Flagship Use Case

**Career Intelligence:**
> *"Which Indian city is best for an entry-level AI/ML career in 2026?"*

Extensible to:
- **Company Intelligence** (e.g., *"Which Indian companies currently show strong AI hiring signals?"*)
- **Technology Intelligence** (e.g., *"Is AI agent development worth learning for a software engineering student in 2026?"*)
- **Entity Comparison Mode** (Direct side-by-side dimensional comparisons)

---

## 🏛️ Core Pipeline

```
ASK
  ↓
UNDERSTAND
  ↓
PLAN SEARCH
  ↓
SEARCH (SerpApi: Jobs, Search, News, Trends, Local)
  ↓
NORMALIZE
  ↓
VERIFY (Relevance, Freshness, Reliability)
  ↓
RESOLVE ENTITIES
  ↓
ANALYZE SIGNALS (Hiring, Demand, Risk, etc.)
  ↓
DETECT CONFLICTS (Contradiction Engine)
  ↓
SCORE (Category Weights & Aggregation)
  ↓
EXPLAIN ("Why?" Contribution Chains)
  ↓
RECOMMEND & ACT
```

---

## 🛠️ Architecture

```
React (Vite + TypeScript + Tailwind CSS)
   │
   ▼
FastAPI (Python, Pydantic, SQLAlchemy, SQLite)
   │
   ▼
Decision Intelligence Pipeline
   │
   ▼
SearchOrchestrator
   ├── GoogleSearchService (google)
   ├── GoogleJobsService   (google_jobs)
   ├── GoogleNewsService   (google_news)
   ├── GoogleTrendsService (google_trends)
   └── GoogleLocalService  (google_maps)
```

### 🔍 SerpApi Multi-Engine Integration Details

- **`SerpApiClient`**: Production-grade async HTTP client built on `httpx` with timeout management (`REQUEST_TIMEOUT=15`), automatic exponential retry (`MAX_RETRIES=2`), response payload validation, and custom exception hierarchies (`SerpApiAuthError`, `SerpApiTimeoutError`, `SerpApiRateLimitError`).
- **`SearchOrchestrator`**: Dispatches concurrent queries across multiple SerpApi engines. Implements **graceful partial-failure isolation**: if a single engine (e.g., News) encounters a rate limit or timeout, available engines (e.g., Jobs and Search) complete unimpeded and their evidence is preserved.
- **Typed Engine Results**:
  - `GoogleSearchService`: Organic results, snippets, citation links, index positions.
  - `GoogleJobsService`: Job titles, employers, locations, detection extensions, schedule types, application links.
  - `GoogleNewsService`: News headlines, publishers, timestamps, snippets.
  - `GoogleTrendsService`: Time-series interest data, interest-over-time trends.
  - `GoogleLocalService`: Local ecosystem hubs, ratings, place presence.

> **Security Rule:** Neither SerpApi keys nor LLM API keys are ever exposed to the client application. All queries are handled server-side.

---

## 📦 Project Structure

```
clariq/
├── frontend/                     # React + Vite + TypeScript + Tailwind CSS
│   ├── src/
│   │   ├── components/           # Reusable UI components & Navbar
│   │   ├── pages/                # Landing, Analyze, Dashboard, Compare, Evidence, History
│   │   ├── services/             # Typed API client
│   │   ├── hooks/                # useAnalysis state & polling hook
│   │   ├── types/                # Strongly typed domain & API models
│   │   └── App.tsx               # Client routes
│   └── package.json
│
├── backend/                      # Python + FastAPI + SQLAlchemy
│   ├── app/
│   │   ├── api/                  # FastAPI routers (/health, /api/analyze, /api/compare)
│   │   ├── services/             # SerpApi integration, normalizer, signals, scoring
│   │   ├── models/               # SQLAlchemy ORM models (Analysis, Evidence, Entity, Signal, Contradiction)
│   │   ├── schemas/              # Pydantic schemas
│   │   ├── database/             # Database session and setup
│   │   ├── config.py             # App settings (Pydantic Settings)
│   │   └── main.py               # Application entry point
│   ├── tests/                    # Pytest test suite
│   ├── requirements.txt
│   └── .env.example
│
├── README.md
└── .gitignore
```

---

## ⚙️ Environment Variables

Create `backend/.env` based on `backend/.env.example`:

```env
SERPAPI_API_KEY=your_serpapi_key_here
LLM_API_KEY=your_llm_key_here
DATABASE_URL=sqlite+aiosqlite:///./clariq.db
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:5173
MAX_RETRIES=2
REQUEST_TIMEOUT=15
```

---

## 🏃 Running Locally

### Backend
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Health Check: `http://localhost:8000/health`

### Frontend
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.
