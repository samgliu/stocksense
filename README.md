# StockSense

StockSense is an AI-powered stock analysis and semantic search platform. It combines structured financial data with natural language understanding to enable deeper exploration of public companies through intelligent search and analysis.

## Features

- Semantic search for natural language stock queries (powered by Qdrant and SentenceTransformers)
- Company summaries integrated from existing SP500 datasets
- SP500 company enrichment with sector, industry, and financials
- Firebase-authenticated API with RTK Query support
- Frontend state managed with Redux Toolkit
- Company profile view with LLM-generated analysis and forecast
- Forecast chart with 30-day price range prediction and confidence intervals
- Downloadable AI analysis results
- Fully containerized development and deployment via Docker Compose
- Kafka-based background job processing using LangGraph worker (via FastAPI producer)
- Frontend job status polling with seamless async user experience
- Internal Semantic Search Lab for testing vector-based queries
- Airflow DAGs for automated ETL workflows

## Tech Stack

- Frontend: React + Vite + Tailwind CSS + Redux Toolkit
- Backend: FastAPI (Python)
- Vector Search: SentenceTransformers + Qdrant
- Authentication: Firebase
- Database: PostgreSQL
- Orchestration: Apache Airflow
- Background Jobs: Kafka + LangGraph
- Containerization: Docker + docker-compose

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/samgliu/stocksense.git
cd stocksense
```

### 2. Configure Environment Variables

Copy the `.env.sample` file to `.env` and fill in the required values:

```bash
cp .env.sample .env
```

### 3. Start the application stack

```bash
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Airflow UI: http://localhost:8080

### 4. Load data

Use Airflow DAGs or manual scripts to:

- Load SP500 CSV data into PostgreSQL
- Generate embeddings from summaries
- Upload embeddings and metadata to Qdrant

### Cloud Deployment (Planned)

- Frontend: GitHub Pages or Vercel
- Backend: Render or Cloud Run
- Qdrant: Qdrant Cloud
- PostgreSQL: Supabase or Neon
- API security: Cloudflare Zero Trust

## Future Improvements

StockSense is an ongoing project with several enhancements planned:

- **CI/CD & Quality**: Add unit/integration tests (Vitest, Pytest), GitHub Actions pipelines, and Sentry monitoring.
- **Historical Data & ML**: Enable historical CSV upload, price trend prediction, and advanced data visualization.
- **Semantic Search**: Expand Qdrant-powered search with text embeddings and real-time semantic filtering.
- **Async Backend**: Add Redis and Kafka job queues with LangGraph worker consumers for scalable background tasks.
- **Data Pipelines**: Automate enrichment and ETL with Airflow and DBT.
- **Cloud Deployment**: Deploy production-ready app using Terraform and Kubernetes on AWS or GCP.
- **Feature Flags & Analytics**: Add user behavior tracking and controlled feature rollouts.
