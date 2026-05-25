FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir . \
    && chmod +x scripts/start.sh

EXPOSE 8000

CMD ["scripts/start.sh"]
