# StockSense

StockSense is an AI-powered stock analysis and semantic search platform. It combines structured financial data with natural language understanding to enable deeper exploration of public companies through intelligent search, automated insights, and simulated trading.

## Demo

You can try the live demo of **StockSense** here:

- **Cloudflare Pages**: [https://stocksense.pages.dev](https://stocksense.pages.dev)
- **GitHub Pages**: [https://samgliu.github.io/stocksense](https://samgliu.github.io/stocksense)
- **Backend API Docs**: [API Docs](https://api.samliu.site/docs)

## Features

- **Semantic Search**: Natural language stock search powered by SentenceTransformers and Qdrant vector search.
- **Company Knowledge Base**: Enriched S&P 500 company profiles with industry, sector, and financial metadata.
- **LLM-Powered Insights**: AI-generated company summaries, forecasts, and trading signals using local Ollama or LangGraph agents.
- **SmartTrade Agent**: Simulated auto-trading system with AI-driven buy/sell decisions and job tracking.
- **Company Forecast View**: 30-day price predictions with visualized confidence intervals and insight overlays.
- **Authenticated API**: Firebase-secured backend supporting Google SSO and anonymous auth, integrated with RTK Query.
- **Interactive Frontend**: React + Redux Toolkit with real-time job status polling, semantic search results, and rich visualizations.
- **Kafka Job Queue**: Decoupled, event-driven architecture using Kafka on Kubernetes for background task processing.
- **LangGraph Worker Service**: Kafka consumer running on K8s for AI workflow execution and automated analysis.
- **Serverless Functions**: AWS Lambda functions for modular enrichment tasks like web scraping and sentiment analysis.
- **Redis Caching**: Fast async UX with Redis-powered job status tracking and result caching.
- **Airflow ETL Pipelines**: Automated enrichment and embedding workflows using Airflow DAGs (local dev setup).
- **Testing & CI Pipeline**: GitHub Actions-based testing using Pytest (backend) and Jest (frontend).
- **Dockerized Development**: Fully containerized setup with Docker Compose for local development and testing.
- **Observability & Monitoring**:
  - **Grafana Cloud**: Metrics collection and dashboards using Grafana Alloy and Prometheus Remote Write.
  - **Sentry**: Real-time exception tracking for frontend, backend, and worker services.

## Tech Stack

- **Frontend**: React, Vite, Tailwind CSS, Redux Toolkit  
  Deployed on [GitHub Pages](https://samgliu.github.io/stocksense) and [Cloudflare Pages](https://stocksense.pages.dev)
- **Backend**: FastAPI (Python), deployed on Oracle Cloud Kubernetes
- **Worker**: LangGraph consumer service on Kubernetes, utilizing Kafka, Redis, and LangGraph
- **Serverless Functions**: AWS Lambda
- **Sentiment Analysis via Lambda Cloud Functions**: Uses GCS & Llama-powered Cloudflare function
- **Vector Search**: SentenceTransformers + Qdrant Cloud
- **Authentication**: Firebase (Google SSO, Anonymous)
- **Database**: PostgreSQL (Supabase)
- **Job Queue**: Kafka (KRaft mode, Bitnami Helm) on Kubernetes
- **Caching**: Redis (using Redis on Oracle Cloud Kubernetes, or Upstash, or containerized locally)
- **Orchestration**: Apache Airflow (local setup)
- **Containerization**: Docker + docker-compose
- **Infrastructure**: k3s on Oracle Cloud, Terraform (used to provision Lambda functions, IAM roles, and budgets)

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

### 3. Start the Application Stack

```bash
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Airflow UI: http://localhost:8080

### 4. Load Data

Use Airflow DAGs or manual scripts to:

- Load S&P 500 CSV data into PostgreSQL
- Generate embeddings from summaries
- Upload embeddings and metadata to Qdrant

## Cloud Deployment

- **Frontend**:
  - GitHub Pages: https://samgliu.github.io/stocksense
  - Cloudflare Pages: https://stocksense.pages.dev
- **Backend API**: Deployed on Oracle Cloud Kubernetes

- **Kafka**: K8s on Oracle Cloud
- **LangGraph Worker**: K8s on Oracle Cloud
- **Vector Search**: Qdrant Cloud
- **Database**: Supabase PostgreSQL
- **Redis**: K8s on Oracle Cloud (Upstash or containerized)
- **Job Queue**: Kafka
- **SSL Termination**: Cloudflare Origin CA + HTTPS Proxy

## Future Improvements

StockSense is an ongoing project with several enhancements planned:

- **SmartTrade Enhancements**: Improve agent logic with diversification, economic signals, and historical performance tracking. Add trade alerts via email or webhooks.
- **Agent RAG Capabilities**: Integrate retrieval-augmented generation (RAG) from uploaded documents or financial filings for deeper, context-aware analysis.
- **Real-Time AI Streaming**: Add token-level output streaming for more responsive LLM interactions in the frontend.
- **Historical Data & Forecasting**: Enable CSV-based uploads and integrate ML models for long-term trend forecasting.
- **Grafana Dashboards**: Expand visualizations with SmartTrade history, analysis latency, and real-time system metrics.
- **Behavior Analytics**: Add lightweight user analytics with PostHog to understand interaction patterns.
- **RBAC & Multi-Tenancy**: Introduce role-based access control and per-user data isolation for enterprise readiness.
- **Infra-as-Code Expansion**: Extend Terraform coverage for full provisioning on Oracle, AWS, and GCP.
- **Streaming Architecture**: Explore Redpanda or ClickHouse for high-throughput event ingestion and analytical querying.
