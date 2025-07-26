FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Install Chrome and Chromedriver
RUN apt-get update && apt-get install -y \
    chromium-driver \
    chromium \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

ENV PATH="/usr/lib/chromium-browser/:${PATH}"

CMD ["python", "app.py"]

