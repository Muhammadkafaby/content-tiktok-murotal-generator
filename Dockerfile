# Stage 1: Build frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Python backend
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    fonts-noto-cjk \
    fonts-noto-color-emoji \
    fonts-dejavu-core \
    fonts-freefont-ttf \
    fonts-noto-core \
    fonts-arabeyes \
    wget \
    unzip \
    libglib2.0-0 \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    && rm -rf /var/lib/apt/lists/*

# Download and install Amiri Quran font (best Arabic font available)
RUN mkdir -p /usr/share/fonts/truetype/amiri && \
    wget -q "https://github.com/aliftype/amiri/releases/download/1.000/Amiri-1.000.zip" -O /tmp/amiri.zip && \
    unzip -q /tmp/amiri.zip -d /tmp/amiri && \
    find /tmp/amiri -name "*.ttf" -exec cp {} /usr/share/fonts/truetype/amiri/ \; && \
    rm -rf /tmp/amiri /tmp/amiri.zip

# Download Scheherazade New font (excellent Quran font)
RUN mkdir -p /usr/share/fonts/truetype/scheherazade && \
    wget -q "https://github.com/nicolo-ribaudo/quran-fonts/raw/main/fonts/Scheherazade-Regular.ttf" \
    -O "/usr/share/fonts/truetype/scheherazade/Scheherazade-Regular.ttf" || \
    wget -q "https://software.sil.org/downloads/r/scheherazade/ScheherazadeNew-3.300.zip" -O /tmp/scheherazade.zip && \
    unzip -q /tmp/scheherazade.zip -d /tmp/scheherazade && \
    find /tmp/scheherazade -name "*.ttf" -exec cp {} /usr/share/fonts/truetype/scheherazade/ \; && \
    rm -rf /tmp/scheherazade /tmp/scheherazade.zip || true

# Update font cache
RUN fc-cache -f -v

# Fix ImageMagick security policy to allow text operations
RUN if [ -f /etc/ImageMagick-6/policy.xml ]; then \
    mv /etc/ImageMagick-6/policy.xml /etc/ImageMagick-6/policy.xml.bak && \
    cat /etc/ImageMagick-6/policy.xml.bak | sed 's/rights="none"/rights="read|write"/g' > /etc/ImageMagick-6/policy.xml; \
    fi

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium

# Copy application code
COPY api/ ./api/
COPY generator/ ./generator/
COPY tiktok/ ./tiktok/

# Copy built frontend
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create data directories
RUN mkdir -p /app/data/videos /app/data/backgrounds /app/data/db /app/data/sessions /app/data/logs /app/data/assets

# Copy logo
COPY logo.png /app/data/assets/logo.png

# Environment variables
ENV PORT=8080
ENV DATA_DIR=/app/data
ENV PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright

EXPOSE 8080

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
