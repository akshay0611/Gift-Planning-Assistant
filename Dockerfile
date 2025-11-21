# ---------- Frontend build stage ----------
FROM node:20-bookworm AS web-builder
WORKDIR /webui
COPY webui/package*.json ./
RUN npm install
COPY webui/ .
RUN npm run build

# ---------- Backend stage ----------
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY --from=web-builder /webui/build ./webui/build

EXPOSE 8080

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"]

