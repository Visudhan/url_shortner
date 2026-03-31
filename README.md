# 🔗 URL Shortener

A full-stack URL shortener built with **Django REST Framework** and **React**, featuring Redis caching, Celery-powered async analytics, and PostgreSQL storage. Fully containerized with Docker.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.2-092E20?logo=django&logoColor=white)
![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

---

## ✨ Features

- **Shorten URLs** — Generate random Base62 short codes (56 billion+ combinations)
- **Custom Aliases** — Set memorable slugs like `/my-brand` instead of random codes
- **Link Expiry** — Optionally set an expiration date for temporary links
- **Click Analytics** — Track total clicks, clicks by date, country, and referrer
- **Redis Caching** — Sub-millisecond redirects via Redis cache-first architecture
- **Async Click Logging** — Celery workers log clicks in the background so redirects stay fast
- **Soft Deletes** — Deactivate URLs without losing analytics history
- **UUID Primary Keys** — No sequential IDs exposed in the API

---

## 🏗️ Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   React      │────▶│   Django     │────▶│  PostgreSQL  │
│   Frontend   │     │   REST API   │     │   Database   │
│  (Vite)      │     │              │     │              │
└──────────────┘     └──────┬───────┘     └──────────────┘
                            │
                    ┌───────┴───────┐
                    │               │
               ┌────▼────┐   ┌─────▼─────┐
               │  Redis  │   │  Celery   │
               │  Cache  │   │  Worker   │
               └─────────┘   └───────────┘
```

**Redirect Flow (optimized for speed):**

1. User visits `/<short_code>`
2. Check **Redis cache** → if hit, redirect immediately (~1ms)
3. Cache miss → query **PostgreSQL** → cache result in Redis → redirect
4. **Celery** logs the click asynchronously (doesn't block the redirect)

---

## 🛠️ Tech Stack

| Layer        | Technology                          |
| ------------ | ----------------------------------- |
| **Frontend** | React 19, Vite 7, Axios            |
| **Backend**  | Django 4.2, Django REST Framework   |
| **Database** | PostgreSQL 15                       |
| **Cache**    | Redis 7 (via django-redis)          |
| **Task Queue** | Celery 5.4 (Redis as broker)     |
| **Server**   | Gunicorn (production), WhiteNoise   |
| **DevOps**   | Docker, Docker Compose              |

---

## 🚀 Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)
- (Or for local dev: Python 3.11, Node.js 18+, PostgreSQL, Redis)

### Quick Start with Docker

**1. Clone the repository**

```bash
git clone https://github.com/your-username/url_shortner.git
cd url_shortner
```

**2. Create your environment file**

```bash
cp .env.example .env
```

Edit `.env` and set your values:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=1

# PostgreSQL
POSTGRES_DB=url_shortener
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0
```

**3. Build and run**

```bash
docker compose up --build
```

**4. Open the app**

| Service   | URL                          |
| --------- | ---------------------------- |
| Frontend  | http://localhost:5173        |
| Backend   | http://localhost:8000        |
| Admin     | http://localhost:8000/admin/ |

---

### Local Development (without Docker)

**Backend**

```bash
cd app
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

pip install -r ../requirements.txt
python manage.py migrate
python manage.py runserver
```

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

**Celery Worker** (in a separate terminal)

```bash
cd app
celery -A config worker -l INFO
```

> **Note:** You'll need PostgreSQL and Redis running locally, or update the connection settings in `.env`.

---

## 📡 API Reference

### Create a Short URL

```
POST /api/urls/
```

**Request Body:**

```json
{
  "original_url": "https://example.com/very/long/path",
  "custom_alias": "my-brand",
  "expires_at": "2026-12-31T23:59:59Z"
}
```

> `custom_alias` and `expires_at` are optional.

**Response** `201 Created`:

```json
{
  "id": "a1b2c3d4-...",
  "original_url": "https://example.com/very/long/path",
  "short_code": "aB3xZ9",
  "custom_alias": "my-brand",
  "short_url": "http://localhost:8000/my-brand",
  "created_at": "2026-03-31T12:00:00Z",
  "expires_at": "2026-12-31T23:59:59Z",
  "is_active": true
}
```

---

### Redirect

```
GET /<short_code>
```

Redirects (HTTP 302) to the original URL.

---

### Get Click Analytics

```
GET /api/urls/<short_code>/stats/
```

**Response** `200 OK`:

```json
{
  "total_clicks": 142,
  "clicks_by_date": {
    "2026-03-30": 45,
    "2026-03-29": 97
  },
  "clicks_by_country": {
    "US": 80,
    "IN": 50,
    "Unknown": 12
  },
  "clicks_by_referer": {
    "https://twitter.com": 60,
    "Direct": 82
  }
}
```

---

## 📁 Project Structure

```
url_shortner/
├── app/                        # Django backend
│   ├── config/                 # Project configuration
│   │   ├── settings/
│   │   │   ├── base.py         # Shared settings
│   │   │   ├── development.py  # Dev overrides (DEBUG=True)
│   │   │   └── production.py   # Prod overrides (Gunicorn, HTTPS)
│   │   ├── celery.py           # Celery app configuration
│   │   ├── urls.py             # Root URL routing
│   │   └── wsgi.py
│   ├── shortener/              # URL shortening app
│   │   ├── models.py           # URL model (short_code, alias, expiry)
│   │   ├── views.py            # Create & Redirect endpoints
│   │   ├── serializers.py      # DRF serializers
│   │   └── utils.py            # Base62 short code generator
│   ├── analytics/              # Click tracking app
│   │   ├── models.py           # Click model (IP, user agent, country)
│   │   ├── views.py            # Analytics stats endpoint
│   │   ├── tasks.py            # Celery async click logging
│   │   └── serializers.py
│   ├── users/                  # Custom user model
│   │   └── models.py           # UUID-based User with API key
│   └── manage.py
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   └── index.css
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml          # Multi-service orchestration
├── Dockerfile                  # Backend Docker image
├── build.sh                    # Production build script (Render)
├── requirements.txt            # Python dependencies
├── .env.example                # Environment variable template
└── README.md
```

---

## 🔧 Environment Variables

| Variable            | Description                    | Default                   |
| ------------------- | ------------------------------ | ------------------------- |
| `SECRET_KEY`        | Django secret key              | fallback key (dev only)   |
| `DEBUG`             | Enable debug mode              | `1`                       |
| `POSTGRES_DB`       | Database name                  | `url_shortener`           |
| `POSTGRES_USER`     | Database user                  | —                         |
| `POSTGRES_PASSWORD` | Database password              | —                         |
| `POSTGRES_HOST`     | Database host                  | `db` (Docker service)     |
| `POSTGRES_PORT`     | Database port                  | `5432`                    |
| `REDIS_URL`         | Redis connection URL           | `redis://redis:6379/0`    |

---

## 🚢 Deployment

The project includes a `build.sh` script configured for deployment on **[Render](https://render.com/)**:

```bash
# build.sh handles:
# 1. Installing Python dependencies
# 2. Collecting static files
# 3. Running database migrations
```

Set the environment variables in your Render dashboard and point the build command to `build.sh`.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
