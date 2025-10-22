# LLM Daily Report - International Financial News Aggregation System

国际金融新闻聚合系统,每日自动采集、分析并生成金融速览报告。

## Features

- 每日自动聚合国际金融新闻 (Daily International Financial News Aggregation)
- AI智能摘要生成 (AI-powered Summarization)
- 双时标显示 (Dual Timestamps: UTC + CST)
- 权威度评分与排序 (Authority Scoring & Ranking)
- 词云可视化 (Word Cloud Visualization)
- Web管理控制台 (Web Management Console)
- 审计日志导出 (Audit Log Export)

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React + TS)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Intl Latest  │  │   Sources    │  │   Config     │         │
│  │    Cards     │  │  Management  │  │  Management  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                            ↓ REST API
┌─────────────────────────────────────────────────────────────────┐
│                     Backend (FastAPI)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Pipeline   │  │  AI Router   │  │   Storage    │         │
│  │  (Ingest →   │  │  (Multi-     │  │  (Postgres/  │         │
│  │   Clean →    │  │   Provider)  │  │   SQLite)    │         │
│  │   Dedup →    │  └──────────────┘  └──────────────┘         │
│  │   Compose)   │                                               │
│  └──────────────┘                                               │
└─────────────────────────────────────────────────────────────────┘
                            ↓ Metrics
┌─────────────────────────────────────────────────────────────────┐
│          Observability (Prometheus + Grafana)                   │
└─────────────────────────────────────────────────────────────────┘
```

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Async**: asyncio + httpx
- **Crawling**: feedparser, BeautifulSoup4, Playwright
- **Database**: PostgreSQL / SQLite (pluggable)
- **Cache**: Redis
- **AI**: OpenAI, Anthropic Claude, Google Gemini, DeepSeek, Qwen, Cohere

### Frontend
- **Framework**: Vite + React 18 + TypeScript
- **Styling**: Tailwind CSS
- **Forms**: Formik + Yup
- **Visualization**: react-wordcloud

### Observability
- **Logging**: structlog (JSON)
- **Metrics**: Prometheus + Grafana
- **Tracing**: OpenTelemetry (optional)

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ or SQLite 3.40+
- Redis 7+
- Docker & Docker Compose (optional, for local dev)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd LLM_daily_report
   ```

2. **Backend setup**:
   ```bash
   # Create virtual environment
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # Install dependencies
   pip install -e ".[dev]"

   # Install Playwright browsers
   playwright install chromium

   # Setup database
   cp .env.example .env
   # Edit .env with your database credentials

   # Run migrations
   alembic upgrade head
   ```

3. **Frontend setup**:
   ```bash
   cd frontend
   npm install
   ```

4. **Start services (Docker Compose)**:
   ```bash
   docker-compose up -d
   ```

### Configuration

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/llm_daily_report
# Or use SQLite:
# DATABASE_URL=sqlite+aiosqlite:///data/llm_daily_report.db

# Redis
REDIS_URL=redis://localhost:6379/0

# AI Providers (optional)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
DEEPSEEK_API_KEY=...
QWEN_API_KEY=...

# Email (NetEase Mail)
SMTP_USER=example@163.com
SMTP_AUTH_CODE=...  # Authorization code, not password

# Budget
AI_BUDGET_PER_DAY=100  # USD
```

### Running

1. **Start backend**:
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access the application**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Grafana: http://localhost:3000

## Usage

### Generate Daily Report

```bash
# Trigger report generation for today
curl -X POST http://localhost:8000/api/reports/generate \
  -H "Content-Type: application/json" \
  -d '{"date": "2025-10-22"}'
```

### View Latest International News

```bash
# Get latest 50 international news items
curl http://localhost:8000/api/intl-latest?window=24&limit=50&authority_min=80
```

### Export Audit Logs

```bash
# Export audit logs as CSV
curl "http://localhost:8000/api/audit/export?start=2025-10-01&end=2025-10-22&format=csv" \
  -H "Authorization: Bearer <token>" \
  > audit_logs.csv
```

## Development

### Run Tests

```bash
# Backend tests
pytest tests/ --cov=src --cov-report=term

# Frontend tests
cd frontend
npm test
```

### Lint & Format

```bash
# Backend
ruff check src/ tests/
black src/ tests/
mypy src/

# Frontend
cd frontend
npm run lint
npm run format
```

## Project Structure

```
LLM_daily_report/
├── src/                      # Backend source code
│   ├── models/               # Data models
│   ├── crawling/             # Crawlers & parsers
│   ├── pipeline/             # Processing pipeline
│   ├── ai/                   # AI providers & router
│   ├── storage/              # Storage adapters
│   ├── repositories/         # Data repositories
│   ├── api/                  # API endpoints
│   ├── services/             # Business services
│   ├── observability/        # Logging & metrics
│   ├── config/               # Configuration
│   ├── jobs/                 # Scheduled jobs
│   └── main.py               # FastAPI app
├── frontend/                 # Frontend source code
│   ├── src/
│   │   ├── pages/            # React pages
│   │   ├── components/       # React components
│   │   ├── api/              # API client
│   │   └── App.tsx           # Main app
│   └── package.json
├── tests/                    # Backend tests
├── alembic/                  # Database migrations
├── config/                   # Configuration files
├── data/                     # Data storage
├── scripts/                  # Utility scripts
└── docs/                     # Documentation
```

## License

MIT

## Contributing

Contributions are welcome! Please read the contributing guidelines before submitting PRs.

## Support

For issues and questions, please open an issue on GitHub.
