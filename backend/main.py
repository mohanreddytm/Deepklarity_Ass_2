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

# CORS (allow all during dev; tighten in prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.post("/generate_quiz")
def generate_quiz(payload: GenerateQuizInput, db: Session = Depends(get_db)) -> Dict[str, Any]:
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

