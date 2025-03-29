FROM apache/airflow:latest-python3.11

USER root

# Install basic build dependencies (for torch)
RUN apt-get update && apt-get install -y git gcc g++ && apt-get clean

USER airflow

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt