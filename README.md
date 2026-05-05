# 🌾 AgriVision AI

**An AI-powered agriculture platform** that integrates plant identification, disease detection, weather intelligence, and personalised crop advisory into a single, production-ready web application.

---

## 📋 Table of Contents

- [Tech Stack](#tech-stack)
- [Features](#features)
- [Project Structure](#project-structure)
- [API Routes](#api-routes)
- [Quick Start](#quick-start)
- [Environment Variables](#environment-variables)
- [Running with Docker](#running-with-docker)
- [Running Locally](#running-locally)
- [Running Tests](#running-tests)
- [Architecture Overview](#architecture-overview)

---

## 🛠️ Tech Stack

| Layer     | Technology                                   |
|-----------|----------------------------------------------|
| Backend   | **FastAPI** (Python 3.12)                    |
| Frontend  | Vanilla **HTML / CSS / JavaScript**          |
| Plant ID  | **PlantNet** v2 API                          |
| Plant Care| **Perenual** API                             |
| Weather   | **OpenWeatherMap** Current + Forecast API    |
| AI Engine | **Google Gemini 2.5 Flash**                  |
| Container | Docker + Nginx (static frontend proxy)       |

---

## ✨ Features

| Feature               | Description                                                                 |
|-----------------------|-----------------------------------------------------------------------------|
| 🌿 Plant Identifier    | Upload a photo or paste a URL to identify plant species via PlantNet AI     |
| 🔬 Disease Detector    | Upload a leaf image or describe symptoms for AI-powered disease diagnosis   |
| ⛅ Weather Intelligence | Real-time weather + 5-day forecast + AI farming advice for your location   |
| 🤖 AI Advisor          | Multi-turn conversational crop management assistant (Gemini 2.5 Flash)     |
| 📅 Crop Planner        | Browse crops, filter by season/category, generate AI planting plans        |
| 💧 Plant Care Guide    | Search thousands of plants for watering, sunlight, and care information    |

---

## 📁 Project Structure

```
agrivision-ai/
│
├── backend/                          # FastAPI backend application
│   ├── app/
│   │   ├── main.py                   # App factory: FastAPI instance, CORS, router registration
│   │   ├── config.py                 # Pydantic Settings — reads from .env
│   │   ├── dependencies.py           # FastAPI Depends() factories for all services
│   │   │
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── router.py         # Aggregates all v1 endpoint routers
│   │   │       └── endpoints/
│   │   │           ├── plant_id.py   # POST /plants/identify/upload|url
│   │   │           ├── plant_care.py # GET  /plants/care/search, /{id}, /{id}/guide
│   │   │           ├── weather.py    # GET  /weather/current|forecast|insight
│   │   │           ├── ai_advisor.py # POST /advisor/crop|chat|ask
│   │   │           ├── disease.py    # POST /disease/detect/upload, /analyse
│   │   │           └── crops.py      # GET/POST /crops/, /{name}, /{name}/plan|pests
│   │   │
│   │   ├── services/
│   │   │   ├── plantnet_service.py   # PlantNet API client (identify by file/URL)
│   │   │   ├── perenual_service.py   # Perenual API client (search, details, guide)
│   │   │   ├── weather_service.py    # OpenWeatherMap client (current + forecast)
│   │   │   └── gemini_service.py     # Gemini 2.5 Flash client (advisory, chat, disease)
│   │   │
│   │   ├── models/
│   │   │   ├── plant.py              # Pydantic: PlantMatch, PlantCareInfo, DiseaseInfo, …
│   │   │   ├── weather.py            # Pydantic: CurrentWeather, WeatherForecast, …
│   │   │   └── response.py           # Generic SuccessResponse[T], ErrorResponse, Paginated
│   │   │
│   │   ├── core/
│   │   │   ├── exceptions.py         # Custom exception handlers + ExternalAPIError
│   │   │   └── security.py           # Optional X-API-Key header dependency
│   │   │
│   │   └── utils/
│   │       ├── image_utils.py        # Upload validation, resize, base64 helpers
│   │       └── cache.py              # In-memory TTL cache (drop-in Redis replacement)
│   │
│   ├── tests/
│   │   ├── test_plant_id.py          # PlantNet service unit tests (mocked HTTP)
│   │   ├── test_weather.py           # WeatherService unit tests (mocked HTTP)
│   │   └── test_ai_advisor.py        # GeminiService unit tests (mocked SDK)
│   │
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
│
├── frontend/                         # Static HTML/CSS/JS frontend
│   ├── index.html                    # Dashboard — hero, feature cards, weather widget, stats
│   ├── pages/
│   │   ├── plant-identifier.html     # Plant ID (upload/URL/care search tabs)
│   │   ├── disease-detector.html     # Disease detection (image/symptom tabs)
│   │   ├── weather.html              # Weather dashboard + AI insight
│   │   ├── ai-advisor.html           # Full-screen chat interface
│   │   └── crop-planner.html         # Crop browser + AI plan generator
│   │
│   ├── css/
│   │   ├── main.css                  # Design system: tokens, reset, typography, layout
│   │   ├── components.css            # Reusable: tabs, upload zones, cards, badges, alerts
│   │   └── pages/
│   │       ├── dashboard.css
│   │       ├── plant-identifier.css
│   │       ├── weather.css
│   │       ├── ai-advisor.css
│   │       ├── disease-detector.css
│   │       └── crop-planner.css
│   │
│   ├── js/
│   │   ├── api.js                    # Unified API client (PlantAPI, WeatherAPI, AdvisorAPI, …)
│   │   ├── main.js                   # Shared utilities: nav toggle, tabs, Markdown renderer
│   │   └── pages/
│   │       ├── dashboard.js
│   │       ├── plant-identifier.js
│   │       ├── weather.js
│   │       ├── ai-advisor.js
│   │       ├── disease-detector.js
│   │       └── crop-planner.js
│   │
│   └── assets/images/
│       ├── logo.svg                  # AgriVision AI brand logo
│       └── hero-illustration.svg     # Hero section graphic
│
├── docker-compose.yml                # Backend + Nginx frontend services
├── nginx.conf                        # Nginx: proxy /api/* → backend, serve frontend
├── .env.example                      # Root environment variable template
└── README.md
```

---

## 🔌 API Routes

All routes are prefixed with `/api/v1`.
Interactive docs available at [`/api/docs`](http://localhost:8000/api/docs) (Swagger UI).

### Plant Identification

| Method | Path                          | Description                            |
|--------|-------------------------------|----------------------------------------|
| POST   | `/plants/identify/upload`     | Identify plant from uploaded image     |
| POST   | `/plants/identify/url`        | Identify plant from image URL          |

### Plant Care

| Method | Path                          | Description                            |
|--------|-------------------------------|----------------------------------------|
| GET    | `/plants/care/search?q=`      | Search plants by name                  |
| GET    | `/plants/care/{id}`           | Get care details for a plant           |
| GET    | `/plants/care/{id}/guide`     | Get full care guide for a plant        |

### Weather

| Method | Path                          | Description                            |
|--------|-------------------------------|----------------------------------------|
| GET    | `/weather/current`            | Current weather (city or lat/lon)      |
| GET    | `/weather/forecast`           | 5-day forecast (city or lat/lon)       |
| GET    | `/weather/insight`            | AI farming advice from weather data    |

### AI Advisor

| Method | Path                          | Description                            |
|--------|-------------------------------|----------------------------------------|
| POST   | `/advisor/ask`                | Single-shot agricultural Q&A           |
| POST   | `/advisor/chat`               | Multi-turn chat conversation           |
| POST   | `/advisor/crop`               | Crop-specific management advisory      |

### Disease Detection

| Method | Path                          | Description                            |
|--------|-------------------------------|----------------------------------------|
| POST   | `/disease/detect/upload`      | Detect disease from uploaded image     |
| POST   | `/disease/analyse`            | Analyse symptoms via AI                |

### Crop Management

| Method | Path                          | Description                            |
|--------|-------------------------------|----------------------------------------|
| GET    | `/crops/`                     | List supported crops (filterable)      |
| GET    | `/crops/{name}`               | AI overview for a specific crop        |
| POST   | `/crops/{name}/plan`          | Generate AI planting plan              |
| GET    | `/crops/{name}/pests`         | Pest & disease guide for a crop        |

### System

| Method | Path        | Description           |
|--------|-------------|-----------------------|
| GET    | `/health`   | Health check          |
| GET    | `/info`     | Application metadata  |

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/K-vino/PROMPT-DRIVEN.git
cd PROMPT-DRIVEN
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Edit .env and fill in your API keys
```

### 3. Start with Docker Compose (recommended)

```bash
docker-compose up --build
```

- **Frontend** → http://localhost:8080
- **Backend API** → http://localhost:8000
- **Swagger UI** → http://localhost:8000/api/docs

---

## 🔑 Environment Variables

| Variable              | Description                          | Get it at                               |
|-----------------------|--------------------------------------|-----------------------------------------|
| `PLANTNET_API_KEY`    | PlantNet plant identification        | https://my.plantnet.org/                |
| `PERENUAL_API_KEY`    | Perenual plant care database         | https://perenual.com/                   |
| `OPENWEATHER_API_KEY` | OpenWeatherMap weather data          | https://openweathermap.org/api          |
| `GEMINI_API_KEY`      | Google Gemini 2.5 Flash AI           | https://ai.google.dev/                  |

---

## 🐳 Running with Docker

```bash
# Build and start all services
docker-compose up --build -d

# View logs
docker-compose logs -f backend

# Stop
docker-compose down
```

---

## 💻 Running Locally

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # fill in API keys

uvicorn app.main:app --reload --port 8000
```

Open `frontend/index.html` in a browser (or use VS Code Live Server on port 5500).

---

## 🧪 Running Tests

```bash
cd backend
pip install pytest pytest-asyncio
pytest tests/ -v
```

---

## 🏗️ Architecture Overview

```
Browser
  │
  ├── Static files (HTML/CSS/JS) ← Nginx / uvicorn StaticFiles
  │
  └── /api/v1/* ─── FastAPI ──────────────────────────────────────────
                         │
            ┌────────────┼────────────┬─────────────────┐
            │            │            │                 │
       PlantNetService  PerenualSvc  WeatherService  GeminiService
            │            │            │                 │
       plantnet.org  perenual.com  openweathermap.org  ai.google.dev
```

**Request flow:**

1. Browser → Nginx (port 8080) → static asset or `/api/*` proxy
2. Nginx → FastAPI (port 8000) → endpoint handler
3. Handler → Service layer (async HTTP / SDK call)
4. Service → External API (PlantNet / Perenual / OWM / Gemini)
5. Service → typed Pydantic model → endpoint → `SuccessResponse[T]` JSON
6. Browser renders the JSON response

---

## 📄 License

MIT — see [LICENSE](LICENSE)