# Quran Video Generator

Auto-generate video quotes Al-Quran untuk konten TikTok dengan audio murotal dan background video aesthetic.

## Features

- 🕌 Random ayat selection dari 6236 ayat Al-Quran
- 🎙️ Audio murotal dari berbagai qari (Alafasy, Abdul Basit, Sudais, dll)
- 🎬 Background video pemandangan aesthetic
- 📱 Auto-posting ke TikTok via headless browser
- ✍️ AI-generated caption (OpenAI) atau template
- ⏰ Scheduled auto-generation
- 🐳 Docker deployment

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Pexels API Key (untuk background videos)
- OpenAI API Key (optional, untuk AI caption)

### Setup

1. Clone repository
2. Copy environment file:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` dan masukkan API keys
4. Add background videos ke `data/backgrounds/`
5. Run dengan Docker:
   ```bash
   docker-compose up -d
   ```
6. Akses di `http://localhost:8080`

## Development

### Backend (Python)

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn api.main:app --reload --port 8080
```

### Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

### Run Tests

```bash
pytest tests/ -v
```

## API Endpoints

- `GET /api/videos` - List videos
- `POST /api/generate` - Generate videos
- `GET /api/settings` - Get settings
- `PUT /api/settings` - Update settings
- `GET /api/stats` - Get statistics
- `POST /api/tiktok/login` - TikTok login
- `POST /api/tiktok/post/{id}` - Post to TikTok

## Tech Stack

- Backend: FastAPI, SQLAlchemy, MoviePy, FFmpeg
- Frontend: React, Vite, TailwindCSS
- Browser Automation: Playwright
- Database: SQLite
- Scheduler: APScheduler

## License

MIT
