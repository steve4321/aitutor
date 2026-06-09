FROM python:3.12-slim-bookworm AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim-bookworm

WORKDIR /app

RUN addgroup --system --gid 1001 appgroup && \
    adduser --system --uid 1001 appuser

COPY --from=builder /install /usr/local

COPY . .

USER appuser

EXPOSE 8000

LABEL maintainer="aitutor"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]