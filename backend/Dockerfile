# 1. Pick a slim Python image
FROM python:3.12-slim

# 2. Set working directory
WORKDIR /app

# 3. Install OS deps & Python deps
RUN apt-get update && apt-get install -y --no-install-recommends \
      default-libmysqlclient-dev build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy your code in
COPY . .

# 5. Expose port
EXPOSE 5000

# 6. Entrypoint: run your app
CMD ["python", "app.py"]
