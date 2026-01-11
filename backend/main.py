from dotenv import load_dotenv
load_dotenv()

import os
from typing import Any, Dict, List

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Quiz
from scraper import scrape_wikipedia
from llm_quiz_generator import generate_quiz_json


class GenerateQuizInput(BaseModel):
    url: HttpUrl


app = FastAPI(title="AI Wiki Quiz Generator", version="1.0.0")

# CORS configuration for local development
# Allow requests from Vite dev server (localhost:5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://deepklarity-ass-2.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    
    # Temporary debug log: verify GEMINI_API_KEY is loaded
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        # Mask the key for security (show first 8 chars only)
        masked_key = gemini_key[:8] + "..." if len(gemini_key) > 8 else "***"
        print(f"[STARTUP DEBUG] GEMINI_API_KEY is loaded: {masked_key} (length: {len(gemini_key)})")
    else:
        print("[STARTUP DEBUG] GEMINI_API_KEY is NOT loaded")


@app.post("/generate_quiz")
def generate_quiz(payload: GenerateQuizInput, db: Session = Depends(get_db)) -> Dict[str, Any]:
    try:
        url_str = str(payload.url)
        if "wikipedia.org" not in url_str:
            raise HTTPException(status_code=400, detail="Only Wikipedia URLs are supported.")

        title, content = scrape_wikipedia(url_str)
        quiz_json = generate_quiz_json(url=url_str, title=title, content=content)

        # Basic validation of expected fields
        if not isinstance(quiz_json, dict) or "quiz" not in quiz_json:
            raise HTTPException(status_code=502, detail="LLM returned invalid response.")

        record = Quiz(url=url_str, title=quiz_json.get("title", title), data=quiz_json)
        db.add(record)
        db.commit()
        db.refresh(record)
        return quiz_json | {"id": record.id}
    except HTTPException:
        # Re-raise HTTP exceptions as-is (they have proper status codes and CORS headers)
        raise
    except Exception as e:
        # Catch any other exceptions and return a proper error response with CORS headers
        import traceback
        error_msg = str(e)
        error_type = type(e).__name__
        print(f"\n{'='*60}")
        print(f"ERROR in /generate_quiz:")
        print(f"Type: {error_type}")
        print(f"Message: {error_msg}")
        print(f"Traceback:\n{traceback.format_exc()}")
        print(f"{'='*60}\n")
        # Return error with proper HTTP status code so CORS headers are applied
        raise HTTPException(status_code=500, detail=f"Internal server error: {error_msg}")


@app.get("/history")
def history(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    rows = db.query(Quiz).order_by(Quiz.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "title": r.title,
            "url": r.url,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]


@app.get("/quiz/{quiz_id}")
def get_quiz(quiz_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    row = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Quiz not found")
    # Return stored JSON as-is, augmented with id and created_at
    result = dict(row.data)
    result["id"] = row.id
    result["created_at"] = row.created_at.isoformat()
    return result


@app.get("/")
def root() -> Dict[str, str]:
    return {"status": "ok", "service": "AI Wiki Quiz Generator"}

