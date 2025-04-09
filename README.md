# StockSense

StockSense is an AI-powered stock analysis and semantic search platform. It combines structured financial data with natural language understanding to enable deeper exploration of public companies through intelligent search and analysis.

## Demo

You can try the live demo of **StockSense** here: <a href="https://samgliu.github.io/stocksense" target="_blank">Live Demo</a>.

## Features

- **Semantic Search** for natural language stock queries (powered by Qdrant and SentenceTransformers)
- **Company Summaries** integrated from existing SP500 datasets
- **SP500 Company Enrichment** with sector, industry, and financials
- **Firebase-Authenticated API** with RTK Query support
- **Frontend State Managed** with Redux Toolkit
- **Company Profile View** with LLM-generated analysis and forecast
- **Forecast Chart** with 30-day price range prediction and confidence intervals
- Fully containerized development and deployment via Docker Compose
- **Kafka-Based Background Job Processing** using LangGraph worker (via FastAPI producer)
- **Redis** used for caching job status and improving async experience
- **Frontend Job Status Polling** with seamless async user experience
- **Semantic Search** for vector-based queries
- **Airflow DAGs** for automated ETL workflows

## Tech Stack

- **Frontend**: React + Vite + Tailwind CSS + Redux Toolkit, hosted on [GitHub Pages](https://samgliu.github.io/stocksense/)
- **Backend**: FastAPI (Python), hosted on Oracle ARM-based K8s instance
- **Vector Search**: SentenceTransformers + Qdrant
- **Authentication**: Firebase (Google SSO + Anonymous)
- **Database**: PostgreSQL (via Supabase or local)
- **Orchestration**: Apache Airflow (local)
- **Background Jobs**: Kafka + Redis + LangGraph Workers
- **Containerization**: Docker + docker-compose
- **Caching**: Redis
- **Messaging Queue**: Kafka (local with Docker)

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

## Cloud Deployment (Current Setup)

- **Frontend**: [GitHub Pages](https://samgliu.github.io/stocksense/)
- **Backend**: Oracle K8s Instance
- **Qdrant**: Qdrant Cloud
- **PostgreSQL**: Supabase
- **Redis**: Upstash or containerized with the app
- **Kafka**: Containerized (local Docker or K8s only)
- **API Security**: Cloudflare Zero Trust
- **SSL Termination**: Cloudflare Origin SSL Certificates for secure API communication

## Future Improvements

StockSense is an ongoing project with several enhancements planned:

- **CI/CD & Quality**: Add unit/integration tests (Vitest, Pytest), GitHub Actions pipelines, and Sentry monitoring.
- **Historical Data & ML**: Enable historical CSV upload, price trend prediction, and advanced data visualization.
- **Streaming LLM**: Stream AI responses token-by-token to frontend for a better user experience.
- **AI Agent**: Add intelligent memory-aware analysis agent to handle free text queries.
- **Semantic Search**: Expand Qdrant-powered search with real-time semantic filtering.
- **Data Pipelines**: Automate enrichment and ETL with Airflow and DBT.
- **Cloud Deployment**: Deploy production-ready app using Terraform and Kubernetes on Oracle or AWS/GCP.
- **Feature Flags & Analytics**: Add user behavior tracking and controlled feature rollouts.
