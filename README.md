# DeepKlarity - AI Wiki Quiz Generator

Full-stack app that generates quizzes from Wikipedia articles using AI.

## Tech Stack
- Backend: Python, FastAPI, SQLAlchemy, LangChain (Gemini), BeautifulSoup
- Database: PostgreSQL (Neon)
- Frontend: React (Vite) + Tailwind CSS

## Project Structure
```
backend/
  main.py
  database.py
  models.py
  scraper.py
  llm_quiz_generator.py
  requirements.txt
frontend/
  index.html
  package.json
  vite.config.js
  tailwind.config.js
  postcss.config.js
  src/
    main.jsx
    index.css
    App.jsx
    services/api.js
    components/
      GenerateQuizTab.jsx
      HistoryTab.jsx
      QuizDisplay.jsx
```

## Environment Variables
Create a `backend/.env` with:
```
DATABASE_URL="postgresql://neondb_owner:npg_KyfkNG7he8vn@ep-summer-unit-a1rynyeh-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
GEMINI_API_KEY="<your_gemini_key>"
# optional: use mock responses without Gemini (true/false)
USE_MOCK_LLM=false
```

Create a `frontend/.env` with:
```
VITE_API_BASE_URL="https://deepklarity-ass-2.onrender.com"
```

## Backend - Local Run
```bash
cd backend
python -m venv .venv && . .venv/Scripts/activate  # Windows PowerShell
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 10000
```
Endpoints:
- POST /generate_quiz  { "url": "https://en.wikipedia.org/wiki/Alan_Turing" }
- GET /history
- GET /quiz/{id}

## Frontend - Local Run
```bash
cd frontend
npm install
npm run dev
```
Open the shown localhost URL.

## Deployment
### Backend (Render)
- New Web Service → Environment: Python
- Start Command:
```
uvicorn main:app --host 0.0.0.0 --port 10000
```
- Deployed Url: https://deepklarity-ass-2.onrender.com/
- Environment variables:
  - DATABASE_URL
  - GEMINI_API_KEY
  - USE_MOCK_LLM (optional)

### Frontend (vercel)
- Build command: `npm run build`
- Publish directory: `dist`
- Deployed Url: https://deepklarity-ass-2.vercel.app/


## Screenshots
![Generate Quiz Page](./images/screenshot1.png)
![History Page](./images/screenshot3.png)
![Quiz Details Modal](./images/screenshot2.png)

## Notes
- The backend includes a mock mode (`USE_MOCK_LLM=true`) so you can test without a Gemini key.
- Only Wikipedia URLs are accepted by `/generate_quiz`.
- Quiz results are stored as JSON in the `quizzes` table (PostgreSQL JSONB).

