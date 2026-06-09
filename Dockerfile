# ── Image de base légère avec Python 3.12 ──
FROM python:3.12-slim

# Dépendances système pour Playwright (Chromium)
RUN apt-get update && apt-get install -y \
    wget curl gnupg ca-certificates \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
    libxdamage1 libxfixes3 libxrandr2 libgbm1 \
    libpango-1.0-0 libcairo2 libasound2 \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copie et install des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Chromium via Playwright
RUN playwright install chromium
RUN playwright install-deps chromium

# Copie du code source
COPY . .

# Variable d'environnement du token Discord (à définir au runtime)
ENV DISCORD_TOKEN=""

CMD ["python", "bot.py"]
