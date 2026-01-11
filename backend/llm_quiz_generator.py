import json
import logging
import os
from typing import Any, Dict

from google import genai


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

PROMPT_TEXT = (
    "You are an AI assistant that reads a Wikipedia article and generates an educational quiz.\n\n"
    "Follow this format strictly (return valid JSON only):\n\n"
    "{{\n"
    "\"url\": \"<article_url>\",\n"
    "\"title\": \"<article_title>\",\n"
    "\"summary\": \"<one paragraph summary>\",\n"
    "\"key_entities\": {{\n"
    "\"people\": [],\n"
    "\"organizations\": [],\n"
    "\"locations\": []\n"
    "}},\n"
    "\"sections\": [],\n"
    "\"quiz\": [\n"
    "{{\n"
    "\"question\": \"\",\n"
    "\"options\": [\"A\", \"B\", \"C\", \"D\"],\n"
    "\"answer\": \"\",\n"
    "\"difficulty\": \"easy/medium/hard\",\n"
    "\"explanation\": \"\"\n"
    "}}\n"
    "],\n"
    "\"related_topics\": []\n"
    "}}\n\n"
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

# Required dependencies for NEW Google Gemini SDK
REQUIRED_PACKAGE = "google.genai"
REQUIRED_PACKAGE_NAME = "google-genai"


def _validate_dependencies() -> None:
    """Validate that required dependencies are installed."""
    try:
        __import__(REQUIRED_PACKAGE)
        logger.info(f"✓ Dependency '{REQUIRED_PACKAGE_NAME}' is installed")
    except ImportError as e:
        logger.error(f"✗ Dependency '{REQUIRED_PACKAGE_NAME}' is missing: {e}")
        raise RuntimeError(
            f"Missing required dependency: {REQUIRED_PACKAGE_NAME}. "
            f"Please install it with: pip install {REQUIRED_PACKAGE_NAME}"
        ) from e


def _mock_quiz(url: str, title: str, content: str) -> Dict[str, Any]:
    """Generate a mock quiz (only used when USE_MOCK_LLM=1 explicitly)."""
    logger.warning("Using MOCK LLM mode - this should only be used for testing!")
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


def _validate_quiz_structure(quiz_json: Dict[str, Any], url: str, title: str) -> None:
    """Validate that the quiz has the expected structure and quality."""
    if not isinstance(quiz_json, dict):
        raise ValueError("Quiz JSON must be a dictionary")
    
    if "quiz" not in quiz_json:
        raise ValueError("Quiz JSON must contain a 'quiz' field")
    
    quiz_list = quiz_json.get("quiz", [])
    if not isinstance(quiz_list, list):
        raise ValueError("Quiz field must be a list")
    
    num_questions = len(quiz_list)
    logger.info(f"Generated quiz contains {num_questions} questions")
    
    if num_questions < 5:
        raise ValueError(
            f"Quiz validation failed: Only {num_questions} questions generated, "
            f"but at least 5 are required. The LLM did not generate enough questions."
        )
    
    if num_questions > 10:
        logger.warning(f"Quiz contains {num_questions} questions (more than recommended 10)")
    
    # Check for difficulty variety
    difficulties = [q.get("difficulty", "unknown") for q in quiz_list if isinstance(q, dict)]
    unique_difficulties = set(difficulties)
    if len(unique_difficulties) < 2:
        logger.warning(f"Quiz has limited difficulty variety: {unique_difficulties}")
    
    # Validate each question structure
    for i, q in enumerate(quiz_list):
        if not isinstance(q, dict):
            raise ValueError(f"Question {i+1} must be a dictionary")
        required_fields = ["question", "options", "answer", "difficulty", "explanation"]
        for field in required_fields:
            if field not in q:
                raise ValueError(f"Question {i+1} is missing required field: '{field}'")
        if not isinstance(q["options"], list) or len(q["options"]) < 2:
            raise ValueError(f"Question {i+1} must have at least 2 options")


def _generate_quiz_with_llm(url: str, title: str, content: str, api_key: str):
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is missing")

    logger.info("Using Google Gemini via google-genai SDK")

    client = genai.Client(api_key=api_key)

    prompt = PROMPT_TEXT.format(url=url, title=title, content=content)

    # Correct contents format: list with text part
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt  # SDK accepts string directly per examples
    )

    text = response.text
    if not text:
        raise RuntimeError("Gemini returned empty response")

    # Parse JSON safely (unchanged)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            return json.loads(text[start:end + 1])
        raise RuntimeError("Gemini response is not valid JSON")



def generate_quiz_json(url: str, title: str, content: str) -> Dict[str, Any]:
    """
    Generate quiz JSON from Wikipedia article content.
    
    This function:
    - Uses real Gemini LLM if GEMINI_API_KEY is present (default behavior)
    - Uses mock LLM ONLY if USE_MOCK_LLM=1 is explicitly set
    - Throws clear errors if LLM cannot be initialized
    - Includes retry logic for quiz quality validation
    """
    # Check for explicit mock mode
    use_mock_env = os.getenv("USE_MOCK_LLM", "0")
    use_mock = use_mock_env.lower() in {"1", "true", "yes"}
    
    # Check for API key
    api_key = os.getenv("GEMINI_API_KEY")
    api_key_present = bool(api_key and api_key.strip())
    
    # Log configuration
    logger.info("=" * 60)
    logger.info("Quiz Generation Configuration:")
    logger.info(f"  USE_MOCK_LLM: {use_mock_env} -> {use_mock}")
    logger.info(f"  GEMINI_API_KEY: {'PRESENT' if api_key_present else 'MISSING'}")
    logger.info("=" * 60)
    
    # Handle mock mode (only if explicitly enabled)
    if use_mock:
        logger.warning("USE_MOCK_LLM=1 is set - using MOCK LLM mode")
        return _mock_quiz(url, title, content)
    
    # If no API key and mock not enabled, throw error
    if not api_key_present:
        error_msg = (
            "GEMINI_API_KEY is not set. "
            "Please provide a valid Gemini API key in your environment variables. "
            "Mock mode is disabled by default. To use mock mode for testing, "
            "explicitly set USE_MOCK_LLM=1"
        )
        logger.error(f"✗ {error_msg}")
        raise RuntimeError(error_msg)
    
    # Use real LLM with retry logic for quality validation
    max_retries = 3
    last_error = None
    
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Attempt {attempt}/{max_retries} to generate quiz")
            quiz_json = _generate_quiz_with_llm(url, title, content, api_key)
            
            # Validate quiz quality (number of questions)
            num_questions = len(quiz_json.get("quiz", []))
            if num_questions >= 5:
                logger.info(f"✓ Quiz generation successful with {num_questions} questions")
                return quiz_json
            else:
                logger.warning(
                    f"Attempt {attempt} generated only {num_questions} questions "
                    f"(need at least 5). Retrying..."
                )
                last_error = ValueError(
                    f"Generated quiz has only {num_questions} questions, "
                    f"need at least 5"
                )
                
        except (ValueError, RuntimeError) as e:
            error_str = str(e).lower()
            # Retry on validation errors about question count
            is_question_count_error = "only" in error_str and "questions" in error_str
            # Retry on JSON parsing errors
            is_json_error = "invalid json" in error_str or "does not contain valid json" in error_str
            
            if (is_question_count_error or is_json_error) and attempt < max_retries:
                error_type = "JSON parsing" if is_json_error else "validation"
                logger.warning(f"Attempt {attempt} failed ({error_type} error): {e}. Retrying...")
                last_error = e
                continue
            # For other errors, raise immediately
            raise
    
    # If we've exhausted retries
    if last_error:
        error_str = str(last_error).lower()
        if "invalid json" in error_str or "does not contain valid json" in error_str:
            error_msg = (
                f"Failed to generate a valid quiz after {max_retries} attempts. "
                f"Last error: {last_error}. "
                f"Gemini consistently returned invalid JSON responses."
            )
        else:
            error_msg = (
                f"Failed to generate a valid quiz after {max_retries} attempts. "
                f"Last error: {last_error}. "
                f"The model consistently generated fewer than 5 questions."
            )
        logger.error(f"✗ {error_msg}")
        raise RuntimeError(error_msg) from last_error
    
    # This should never be reached, but just in case
    raise RuntimeError("Unexpected error in quiz generation")
