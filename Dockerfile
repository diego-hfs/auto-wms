FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DISPLAY=:99 \
    DRY_RUN=true

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    fluxbox \
    novnc \
    websockify \
    x11vnc \
    x11-utils \
    xvfb \
    fonts-liberation \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "automacao_cadastro_item_wms.py"]
