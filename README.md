# StockSense

StockSense is an AI-powered stock analysis and semantic search platform. It combines structured financial data with natural language understanding to enable deeper exploration of public companies through intelligent search and analysis.

## Demo

You can try the live demo of **StockSense** here:

- **Cloudflare Pages**: [https://stocksense.pages.dev](https://stocksense.pages.dev)
- **GitHub Pages**: [https://samgliu.github.io/stocksense](https://samgliu.github.io/stocksense)
- **Backend API Docs**: [API Docs](https://api.samliu.site/docs)

## Features

- **Semantic Search** for natural language stock queries (powered by Qdrant and SentenceTransformers)
- **Company Summaries** integrated from SP500 datasets
- **SP500 Enrichment** with sector, industry, and financials
- **LLM-Generated Insights** enriched using a local Ollama-hosted model
- **Firebase-Authenticated API** with RTK Query support
- **Frontend State Managed** with Redux Toolkit
- **Company Profile View** with LLM-generated insights and price forecast
- **Forecast Chart** with 30-day prediction and confidence intervals
- **Kafka-Based Job Queue on Kubernetes** for decoupled analysis processing
- **LangGraph Worker** consuming from Kafka topics for AI-driven analysis
- **Serverless Cloud Functions** for modular, scalable data enrichment (AWS Lambda for web scraping and sentiment analysis)
- **Redis Caching** for job tracking and faster async UX
- **Frontend Job Status Polling** with seamless experience
- **Airflow DAGs** for automated ETL pipelines
- **Testing Pipeline** with Pytest and Jest integrated into GitHub Actions
- Fully containerized local development via Docker Compose

## Tech Stack

- **Frontend**: React, Vite, Tailwind CSS, Redux Toolkit  
  Deployed on [GitHub Pages](https://samgliu.github.io/stocksense) and [Cloudflare Pages](https://stocksense.pages.dev)
- **Backend**: FastAPI (Python), deployed on Oracle Cloud Kubernetes
- **Worker**: LangGraph consumer service on Kubernetes, utilizing Kafka, Redis, and LangGraph
- **Serverless Functions**: AWS Lambda
- **Sentiment Analysis via Lambda Cloud Functions**: Uses CSE & Llama-powered Cloudflare function
- **Vector Search**: SentenceTransformers + Qdrant Cloud
- **Authentication**: Firebase (Google SSO, Anonymous)
- **Database**: PostgreSQL (Supabase)
- **Job Queue**: Kafka (KRaft mode, Bitnami Helm) on Kubernetes
- **Caching**: Redis (using Redis [async] on Oracle Cloud Kubernetes, or Upstash, or containerized locally)
- **Orchestration**: Apache Airflow (local setup)
- **Containerization**: Docker + docker-compose
- **Infrastructure**: K8s on Oracle Cloud, Terraform (used to provision Lambda functions, IAM roles, and budgets)

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

## Cloud Deployment

- **Frontend**:
  - GitHub Pages: https://samgliu.github.io/stocksense
  - Cloudflare Pages: https://stocksense.pages.dev
- **Backend API**: Deployed on Oracle Cloud K8s
- **Kafka**: K8s on Oracle Cloud
- **LangGraph Worker**: K8s on Oracle Cloud
- **Vector Search**: Qdrant Cloud
- **Database**: Supabase PostgreSQL
- **Redis**: K8s on Oracle Cloud (Upstash or containerized)
- **Job Queue**: Kafka
- **SSL Termination**: Cloudflare Origin CA + HTTPS Proxy

## Future Improvements

StockSense is an ongoing project with several enhancements planned:

- **Auto-Trader (Simulated)**: Build an AI-powered auto-trading system where users subscribe to tickers with configurable rules (e.g. wash sale settings). Periodic analysis is triggered via Kubernetes CronJobs, publishing jobs to Kafka. A LangGraph-based agent running in the worker processes each job by aggregating real-time signals—price trends, Gemini insights, and live sentiment from Reddit/X (via deployed AWS Lambda functions). Trade decisions are simulated and logged, with notifications and analysis delivered via email or dashboard.
- **CI/CD & Observability**: Add automated GitHub Actions pipelines, unit/integration tests (Vitest, Pytest), and monitoring tools like Sentry or Prometheus.
- **Historical Data & ML**: Enable CSV uploads for historical stock data, integrate trend forecasting models, and build rich visualizations.
- **Streaming LLM Responses**: Implement token-by-token streaming of AI outputs for real-time feedback.
- **AI Agent**: Introduce a memory-aware, context-retaining agent to analyze and respond to complex user queries.
- **Advanced Semantic Search**: Enhance vector-based search with real-time filters, rankings, and multilingual support.
- **ETL & Data Pipelines**: Scale up enrichment pipelines with Airflow, and optionally integrate DBT for transformation layers.
- **Cloud Infra-as-Code**: Improve production deployment with Terraform modules for full Oracle/GCP/AWS setup.
- **Feature Flags & Analytics**: Add LaunchDarkly-style toggles and user behavior tracking with tools like PostHog or RudderStack.
- **Multi-Tenant & Role-Based Access**: Add per-user data isolation and RBAC for enterprise readiness.
