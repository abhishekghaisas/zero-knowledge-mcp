FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 1. Install dependencies first to optimize cache reuse
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. CRITICAL FIX: Copy the rest of the ui/ folder context (including app.py) into /app
COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"]