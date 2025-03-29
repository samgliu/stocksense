# StockSense

StockSense is an AI-powered stock analysis and semantic search platform. It combines structured financial data with natural language understanding to enable deeper exploration of public companies through intelligent search and analysis.

## Features

- Semantic search for natural language stock queries (powered by Qdrant and SentenceTransformers)
- Company summaries integrated from existing SP500 datasets
- SP500 company enrichment with sector, industry, and financials
- Firebase-authenticated API with RTK Query support
- Fully containerized development and deployment via Docker Compose
- Internal Semantic Search Lab for testing vector-based queries
- Airflow DAGs for automated ETL workflows

## Tech Stack

- **Frontend**: React + Vite + Tailwind CSS
- **Backend**: FastAPI (Python)
- **Vector Search**: SentenceTransformers + Qdrant
- **Authentication**: Firebase
- **Database**: PostgreSQL
- **Orchestration**: Apache Airflow
- **Containerization**: Docker + docker-compose

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/samgliu/stocksense.git
cd stocksense
```

### 2. Start the application stack

```bash
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Airflow UI: http://localhost:8080

### 3. Load data

Use Airflow DAGs or manual scripts to:

- Load SP500 CSV data into PostgreSQL
- Generate embeddings from summaries
- Upload embeddings and metadata to Qdrant
