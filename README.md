# Gaia Career Studio

Gaia Career Studio is a two-part application:

- `frontend/`: Vite + React environmental-science themed UI
- `backend_app.py`: FastAPI API for resume analysis, job suggestions, and interview coaching

## Features

- PDF resume analysis
- AI-generated summary, gaps, and roadmap
- Job recommendation flow with live or demo fallback
- Voice and text interview coaching
- Eco-themed frontend experience

## Local Run

### Backend

Create `.env` in the project root:

```env
OPENAI_API_KEY=...
APIFY_API_TOKEN=...
```

Run:

```bash
uvicorn backend_app:app --reload --host 127.0.0.1 --port 8000
```

### Frontend

Create `frontend/.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Run:

```bash
cd frontend
npm install
npm run dev
```

## Deploy

See [DEPLOY.md](/C:/Users/sushanth/OneDrive%20-%20Northumbria%20University%20-%20Production%20Azure%20AD/Desktop/JobRecommendationsystem/DEPLOY.md).

Recommended hosting:

- Frontend on Vercel
- Backend on Render

## Deployment Files

- [render.yaml](/C:/Users/sushanth/OneDrive%20-%20Northumbria%20University%20-%20Production%20Azure%20AD/Desktop/JobRecommendationsystem/render.yaml)
- [Procfile](/C:/Users/sushanth/OneDrive%20-%20Northumbria%20University%20-%20Production%20Azure%20AD/Desktop/JobRecommendationsystem/Procfile)
- [frontend/vercel.json](/C:/Users/sushanth/OneDrive%20-%20Northumbria%20University%20-%20Production%20Azure%20AD/Desktop/JobRecommendationsystem/frontend/vercel.json)
