# Deploy

## Architecture

- Frontend: Vite + React in `frontend/`
- Backend: FastAPI in `backend_app.py`

Recommended hosting:

- Frontend: Vercel
- Backend: Render

## Backend on Render

1. Push this repository to GitHub.
2. In Render, create a new `Web Service` from the repo.
3. Render can use [render.yaml](/C:/Users/sushanth/OneDrive%20-%20Northumbria%20University%20-%20Production%20Azure%20AD/Desktop/JobRecommendationsystem/render.yaml), or use these values manually:

```text
Build Command: pip install -r requirements.txt
Start Command: uvicorn backend_app:app --host 0.0.0.0 --port $PORT
```

4. Add backend environment variables:

```env
OPENAI_API_KEY=...
APIFY_API_TOKEN=...
```

5. After deploy, copy the public backend URL, for example:

```text
https://gaia-career-backend.onrender.com
```

## Frontend on Vercel

1. Import the `frontend/` directory as the frontend project.
2. Framework preset: `Vite`
3. Add this environment variable in Vercel:

```env
VITE_API_BASE_URL=https://your-backend-url.onrender.com
```

4. Deploy.

## Local Development

Backend env file:

```env
OPENAI_API_KEY=...
APIFY_API_TOKEN=...
```

Frontend env file in `frontend/.env`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Notes

- The frontend now reads the API base URL from `VITE_API_BASE_URL`.
- If `APIFY_API_TOKEN` is unavailable, the app still works with demo job results.
- If OpenAI calls fail, analysis and chat have fallback behavior, but voice mode still needs a working `OPENAI_API_KEY`.
