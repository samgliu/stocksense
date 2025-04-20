FROM python:3.11-slim

WORKDIR /app

COPY . . 
RUN pip install -r requirements.txt

CMD ["sh", "-c", "python -m app.main"]
EXPOSE 8001
