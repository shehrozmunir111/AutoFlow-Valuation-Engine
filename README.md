## AutoFlow Valuation Engine

SAAS-ready, AI-assisted vehicle valuation and instant offer engine for high-volume auto-buying operations.

---

### Product Spec

This project is intentionally designed to be **demo-friendly** and **client-ready**, with clear boundaries around paid integrations and realistic behavior:

- **300 partners**: generated via a Python seeding script (fake partner records) but persisted in a real database as the source of truth.
- **Real pricing**: randomized output with realistic constraints (partner spreads, zip coverage, pricing strategies), not purely arbitrary values.
- **AI classification**: Anthropic Claude (target: ~$5 credit ≈ ~1000 API calls) for junk vs auction decisions.
- **SMS**: Twilio (target: ~$15 credit ≈ ~500 SMS) for notification workflows.
- **Photo upload**: AWS S3 (free tier ~5GB) using presigned uploads.
- **Zoho CRM**: free tier supported with a **mock-mode switch** for local demos and CI.

---

### Project Overview

**AutoFlow Valuation Engine** is a full‑stack, SAAS-ready boilerplate that lets auto-buying teams generate **instant, AI‑assisted purchase offers** for consumer vehicles.  
It combines structured pricing rules, historical auction data, and Anthropic Claude–powered classification to decide whether a vehicle should be treated as **junk metal** or an **auction candidate**, and calculates a profitable buy price in real time.

The system includes:

- A **FastAPI** backend that exposes a clean, versioned REST API for quote calculation, VIN decoding, photo analysis, and CRM integration.
- A **React + Vite** frontend with a guided, multi‑step quote form (vehicle info, condition, damage, location, and final offer).
- A modular architecture that keeps domain logic (pricing, partners, vehicles) separate from transport, persistence, and integrations.

---

### Key Features

- **AI‑assisted vehicle classification**
  - Uses Anthropic Claude via the `AIClassifier` service to decide whether a vehicle is best treated as **junk** or **auction**.
  - Implements a **rules‑first strategy** (mileage, drivable state, title status) and only falls back to the LLM for edge cases, controlling cost and latency.
  - Provides a resilient **rules‑based fallback** path when the external AI is unavailable, so quoting never fully degrades.

- **Partner‑aware pricing engine**
  - `PricingEngine` selects the best buyer among active partners based on coverage, vehicle attributes, and pricing rules.
  - Supports multiple pricing strategies:
    - **Vehicle‑specific** pricing rules for exact year/make/model combinations.
    - **Category‑based** rules (e.g., sedans vs trucks) with partner‑specific spreads.
    - **Flat‑rate** rules for simple junk‑yard style offers.
    - **Zip‑/weight‑based** rules that approximate scrap value using vehicle weight and zip/postal code.
  - Applies configurable **buyer spreads** to ensure each offer meets minimum margin requirements.
  - Includes unit tests around pricing flows to guard against regressions.

- **Rich damage and condition capture**
  - Frontend provides a **multi‑step quote wizard**:
    - Vehicle information with **VIN lookup**, dynamic makes/models, and year/mileage capture.
    - Condition step with drivable state, title status, and engine/transmission notes.
    - Interactive **SVG‑based damage diagrams** (interior and exterior) that let users click zones and assign severity levels.
    - Location details for pickup logistics and partner geo‑filtering.
  - All input is validated end‑to‑end using **Zod** schemas on the frontend and **Pydantic** models on the backend.

- **Photo and document handling**
  - `S3Service` encapsulates secure upload to AWS S3 via **pre‑signed URLs**, keeping large file transfer off the API server.
  - `AIVisionService` integrates with Claude’s vision models to analyze uploaded vehicle photos and infer visible damage, severity, and estimate ranges.

- **External ecosystem integrations**
  - `VINDecoderService` connects to an external VIN decoding API to auto‑populate year, make, and model and validate VINs client‑side.
  - `ZohoCRMClient` publishes accepted quotes into Zoho CRM, handling OAuth token refresh and mapping core vehicle/quote fields to CRM modules.
  - `AuctionAPIService` fetches historical auction comps and can compute market value from past sale data.

- **Operationally ready backend**
  - Centralized configuration via `pydantic-settings`, pulling secrets and environment details from `.env`.
  - Database access through **SQLAlchemy** with pooled connections, automatic schema creation, and context‑managed sessions.
  - **Rate limiting** middleware and centralized **error handling** for safer public APIs.
  - `/health` endpoint for liveness checks and monitoring, plus Prometheus client integration in the dependencies.

- **Modern, UX‑focused frontend**
  - Built with **React 18**, **Vite**, and **Tailwind CSS** for fast iteration and a clean, responsive UI.
  - Uses **React Hook Form + Zod** for performant, type‑safe form handling.
  - Includes reusable UI primitives (`Button`, `Input`, `Select`, `ProgressBar`) for consistent styling and behavior across steps.

---

### Tech Stack

- **Backend**
  - Language: **Python 3**
  - Web framework: **FastAPI**
  - ORM & DB: **SQLAlchemy**, **PostgreSQL**
  - Caching & rate limiting: **Redis** (configured), custom middleware
  - AI & external APIs: **Anthropic Claude** (text + vision), **httpx** for async HTTP, external VIN decoder, external auction data API
  - Cloud storage: **AWS S3** via **boto3**
  - Validation & config: **Pydantic v2**, **pydantic-settings**, `email-validator`
  - Testing: **pytest**, **pytest-asyncio**
  - Monitoring: **prometheus-client**

- **Frontend**
  - Framework: **React 18**
  - Tooling: **Vite**, **TypeScript**
  - Styling: **Tailwind CSS**, PostCSS, Autoprefixer
  - Forms & validation: **React Hook Form**, **Zod**, `@hookform/resolvers`
  - HTTP client: **Axios**
  - Routing: **React Router**

---

### Architecture & Design

The backend follows a **clean, modular architecture** that separates HTTP concerns, domain logic, and infrastructure:

- **API Layer (FastAPI routers)**
  - `app/main.py` wires up the FastAPI app, CORS, rate limiting middleware, and health checks.
  - Routers under `app/routers` (`quotes`, `vehicles`, `photos`, `partners`) expose versioned endpoints (e.g. `/api/v1/quotes/calculate`) and orchestrate domain services.

- **Domain & Application Layer (services, schemas, models)**
  - **Schemas (`app/schemas`)**: Pydantic models define input/output contracts such as `QuoteRequest` and `QuoteResponse`, ensuring type safety across layers.
  - **Models (`app/models`)**: SQLAlchemy entities (`Vehicle`, `Partner`, `PricingRule`, `Quote`, etc.) represent the persistent domain.
  - **Services (`app/services`)**: Pure application logic lives here:
    - `PricingEngine` encapsulates all partner and pricing strategies and returns rich pricing payloads.
    - `AIClassifier` and `AIVisionService` isolate AI integrations and fallbacks.
    - `VINDecoderService`, `AuctionAPIService`, `ZohoCRMClient`, and `S3Service` handle their respective infrastructure concerns behind clean interfaces.

- **Infrastructure Layer (database, config, middleware, utils)**
  - `database.py` manages SQLAlchemy engine creation, pooled connections, and session lifecycle (`get_db` dependency).
  - `config.py` centralizes environment‑driven configuration and secret management.
  - `middleware/` contains cross‑cutting concerns like rate limiting and exception translation.
  - `utils/` provides shared helpers and validators used across services.

On the frontend, the architecture is similarly modular:

- `components/QuoteForm` holds the multi‑step wizard and sub‑steps (vehicle info, condition, damage, location, offer display).
- `components/common` exposes shared UI primitives (button, input, select, progress bar).
- `hooks/useQuote` abstracts API communication and local state for quotes.
- `types` and `schemas` keep the front of the app type‑aligned with the backend.

---

### Installation & Setup

#### 1. Clone the repository

```bash
git clone https://github.com/your-username/autoflow-valuation-engine.git
cd autoflow-valuation-engine
```

#### 2. Backend setup (FastAPI + PostgreSQL)

1. **Create and activate a virtual environment**:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

2. **Install dependencies**:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3. **Configure environment variables**:

- Copy `.env` (or create one) and set at minimum:
  - `DATABASE_URL` – PostgreSQL connection string (e.g. `postgresql://postgres:password@localhost:5432/autoflow_db`)
  - `REDIS_URL` – Redis instance (optional but recommended for rate limiting / caching)
  - `CLAUDE_API_KEY` – Anthropic API key if you want full AI classification and vision support
  - `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_BUCKET_NAME` – if you plan to use S3 uploads
  - Zoho and VIN/Auction API keys as needed.

4. **Initialize the database**:

- Ensure PostgreSQL is running and the database in `DATABASE_URL` exists.
- The app will run `Base.metadata.create_all` on startup; for a production setup you would typically add Alembic migrations.

5. **Run the backend server**:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Alternatively, you can use `docker-compose` from the `backend` directory to bring up Postgres, Redis, and the API in one step.

#### 3. Frontend setup (React + Vite)

1. **Install Node dependencies**:

```bash
cd ../frontend
npm install
```

2. **Start the development server**:

```bash
npm run dev
```

By default, Vite serves the frontend on `http://localhost:3000` and proxies all `/api` requests to `http://localhost:8000`, so the UI and API work together without additional config.

---

### Demo / Mock Mode (Recommended)

For demos (GitHub/LinkedIn/Upwork) you can run the backend without paid accounts by enabling:

- `MOCK_MODE=true` (global)
- or `ZOHO_MOCK_MODE=true` (Zoho-only)

See `backend/.env.example` for a ready template.

---

### API Documentation

The FastAPI backend automatically exposes interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

From there you can:

- Inspect all available endpoints (`/api/v1/quotes/calculate`, `/health`, etc.).
- Validate request/response shapes defined by Pydantic schemas.
- Manually test quote calculations without leaving the browser.

---

### Future Roadmap

- **Real‑time quote streaming and notifications**
  - Stream quote calculation progress (VIN decode, AI classification, partner pricing) to the frontend using WebSockets or Server‑Sent Events.

- **Deeper data‑driven pricing**
  - Tighten integration with auction and wholesale data providers, including model‑specific residuals, to refine fallback pricing and partner spreads.

- **Underwriting and risk scoring**
  - Add risk models that factor in regional theft trends, title anomalies, and operational constraints, surfacing a risk score alongside each quote.

- **Dealer / partner portal**
  - Build a role‑based portal for partners to adjust their own pricing rules, coverage areas, and performance analytics in real time.

---

### Visuals & Portfolio Notes

- **Screenshots / GIFs** (recommended):
  - Add a GIF or screenshot here showcasing:
    - The **multi‑step quote form** in the frontend, and/or
    - The **Swagger UI** for `/api/v1/quotes/calculate`.
  - Example placeholder:

```markdown
![AutoFlow Valuation Wizard](./docs/quote-wizard.gif)
![API Documentation](./docs/swagger-ui.png)
```