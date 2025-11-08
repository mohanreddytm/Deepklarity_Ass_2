import json
import os
from typing import Any, Dict


PROMPT_TEXT = (
    "You are an AI assistant that reads a Wikipedia article and generates an educational quiz.\n\n"
    "Follow this format strictly (return valid JSON only):\n\n"
    "{\n"
    "\"url\": \"<article_url>\",\n"
    "\"title\": \"<article_title>\",\n"
    "\"summary\": \"<one paragraph summary>\",\n"
    "\"key_entities\": {\n"
    "\"people\": [],\n"
    "\"organizations\": [],\n"
    "\"locations\": []\n"
    "},\n"
    "\"sections\": [],\n"
    "\"quiz\": [\n"
    "{\n"
    "\"question\": \"\",\n"
    "\"options\": [\"A\", \"B\", \"C\", \"D\"],\n"
    "\"answer\": \"\",\n"
    "\"difficulty\": \"easy/medium/hard\",\n"
    "\"explanation\": \"\"\n"
    "}\n"
    "],\n"
    "\"related_topics\": []\n"
    "}\n\n"
    "Rules:\n\n"
    "Generate 5–10 questions.\n"
    "Difficulty levels must vary.\n"
    "All facts must come from the article.\n"
    "Do not hallucinate.\n"
    "Keep JSON valid (no markdown, no text outside JSON).\n\n"
    "Article URL: {url}\n"
    "Article Title: {title}\n"
    "Article Content:\n{content}\n"
)


def _mock_quiz(url: str, title: str, content: str) -> Dict[str, Any]:
    # Minimal deterministic mock to support development without an API key
    summary = (content[:400] + "...") if len(content) > 400 else content
    return {
        "url": url,
        "title": title,
        "summary": summary,
        "key_entities": {
            "people": [],
            "organizations": [],
            "locations": [],
        },
        "sections": [],
        "quiz": [
            {
                "question": f"What is the main topic of the article '{title}'?",
                "options": [title, "Science", "History", "Mathematics"],
                "answer": title,
                "difficulty": "easy",
                "explanation": "The article primarily discusses the given title.",
            },
            {
                "question": "Which source was used for this quiz?",
                "options": ["Blog", "Wikipedia", "Newspaper", "Podcast"],
                "answer": "Wikipedia",
                "difficulty": "easy",
                "explanation": "The quiz is generated from a Wikipedia article.",
            },
        ],
        "related_topics": [],
    }


def generate_quiz_json(url: str, title: str, content: str) -> Dict[str, Any]:
    use_mock = os.getenv("USE_MOCK_LLM", "false").lower() in {"1", "true", "yes"}
    api_key = os.getenv("GEMINI_API_KEY")
    if use_mock or not api_key:
        return _mock_quiz(url, title, content)

    # Lazy import LangChain only when actually needed
    try:
        from langchain_core.prompts import PromptTemplate  # type: ignore
        from langchain_google_genai import ChatGoogleGenerativeAI  # type: ignore
    except Exception:
        # Fallback to mock if LangChain stack is not available
        return _mock_quiz(url, title, content)

    prompt = PromptTemplate.from_template(PROMPT_TEXT)
    model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.2, google_api_key=api_key)
    chain = prompt | model
    response = chain.invoke({"url": url, "title": title, "content": content})

    text = response.content if hasattr(response, "content") else str(response)

    # Ensure we return valid JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            candidate = text[start : end + 1]
            return json.loads(candidate)
        raise

