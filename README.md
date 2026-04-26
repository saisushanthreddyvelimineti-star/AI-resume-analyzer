# AI Resume Analyzer

This repository now presents as a GitHub-profile style project showcase for `saisushanthreddyvelimineti-star`.

It combines:

- `frontend/`: Next.js portfolio-style interface with animated GitHub/project presentation
- `backend_app.py`: FastAPI API for resume analysis, job suggestions, and interview coaching
- `src/multimodal_ai.py`: OCR, layout-aware parsing, screenshot-to-profile extraction, and resume-to-job matching helpers

## Features

- PDF resume analysis
- AI-generated summary, gaps, and roadmap
- Job recommendation flow with live or demo fallback
- Voice and text interview coaching
- Animated GitHub-profile project landing page
- OCR-based parsing for PDF/image resumes and screenshots
- Layout-style section detection for skills, experience, education, and projects
- Multimodal-style job matching with embedding support when available

## Multimodal Upgrades

The backend now supports three higher-value AI upgrades:

1. Resume parsing via computer vision
   Upload a PDF or image to `/api/vision/parse` and get extracted text, detected sections, and a structured profile.
2. Skill detection from screenshots
   Upload a LinkedIn or resume screenshot to `/api/vision/profile-from-screenshot` and get structured profile output.
3. Job matching with multimodal understanding
   Send resume text plus job descriptions to `/api/multimodal/job-match` for ranked role matching.

These routes work in fallback mode without heavy CV models, and improve automatically when OCR and embedding dependencies are installed.

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

Optional upgrade dependencies:

- `pytesseract` + local Tesseract install for OCR
- `sentence-transformers` for semantic job matching
- `Pillow` for image loading

### Frontend

Create `frontend/.env`:

```env
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
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
