"""
Gemini quiz generation helper.

Uses the official Gemini API when the google-generativeai package and an API key
are available. Falls back to a deterministic local generator so tests can still
run offline without network access.
"""

from __future__ import annotations

import itertools
import json
import os
import random
import re
from dataclasses import dataclass
from typing import Dict, List, Sequence

_ENV_LOADED = False

try:
    import google.generativeai as genai
except Exception:  # pragma: no cover - package might not be installed.
    genai = None

DEFAULT_MODEL = "gemini-1.5-flash"
BASE_DIR = os.path.dirname(__file__)


@dataclass
class QuizQuestion:
    question: str
    answer: str
    options: Sequence[str]
    context: str

    def as_dict(self) -> Dict[str, str]:
        """Return dict representation expected by callers."""
        return {
            "question": self.question,
            "answer": self.answer,
            "options": list(self.options),
            "context": self.context,
        }


class GeminiService:
    """
    Generate quiz questions from context using Gemini with a graceful fallback.

    When the Gemini client is configured successfully we request questions in a
    structured JSON format so they can be parsed deterministically. If anything
    goes wrong (missing dependency, network failure, malformed output) we fall
    back to a simple local generator to keep the flow working.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = DEFAULT_MODEL,
        request_timeout: int = 30,
    ) -> None:
        self._ensure_env_loaded()
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name
        self.request_timeout = request_timeout
        self._use_gemini = False
        self._model = None

        if self.api_key and genai is not None:
            try:
                genai.configure(api_key=self.api_key)
                self._model = genai.GenerativeModel(model_name)
                self._use_gemini = True
            except Exception as exc:  # pragma: no cover - requires network.
                print(
                    f"Unable to initialize Gemini model '{model_name}': {exc}. "
                    "Falling back to local generator."
                )
        elif self.api_key and genai is None:
            print(
                "google-generativeai is not installed. "
                "Run `pip install google-generativeai` to enable Gemini responses."
            )
        elif not self.api_key:
            print("GEMINI_API_KEY not set; using local quiz generation fallback.")

    def generate_quiz(self, context: str, num_questions: int = 3) -> List[Dict[str, str]]:
        if self._use_gemini and self._model:
            try:
                return self._generate_with_gemini(context, num_questions)
            except Exception as exc:
                print(f"Gemini API failed ({exc}); using local fallback questions instead.")

        return self._generate_locally(context, num_questions)

    # ------------------------------------------------------------------ #
    # Gemini-powered generation
    # ------------------------------------------------------------------ #
    def _generate_with_gemini(self, context: str, num_questions: int) -> List[Dict[str, str]]:
        prompt = self._build_prompt(context, num_questions)
        response = self._model.generate_content(
            prompt,
            generation_config={"temperature": 0.35},
            request_options={"timeout": self.request_timeout},
        )

        if not response or not getattr(response, "text", "").strip():
            raise ValueError("Gemini returned an empty response.")

        payload = self._extract_json_block(response.text)
        questions = json.loads(payload)
        return [self._normalize_question(item) for item in questions]

    @staticmethod
    def _build_prompt(context: str, num_questions: int) -> str:
        return f"""
You are an AI tutor helping students practice key ideas.

Read the following context and create {num_questions} multiple-choice questions.
Each item must be a JSON object in this exact format:
{{
  "question": "...?",
  "answer": "text of the correct answer taken verbatim from the context",
  "options": ["A", "B", "C", "D"],
  "context": "one or two sentences from the source that justify the answer"
}}

Return ONLY a JSON array (no prose, no markdown). Base every answer strictly on the provided context.

Context:
\"\"\"
{context}
\"\"\"
""".strip()

    @staticmethod
    def _extract_json_block(text: str) -> str:
        """Extract JSON content, handling optional ```json fences."""
        fenced_match = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.DOTALL)
        block = fenced_match.group(1).strip() if fenced_match else text.strip()
        return block

    @staticmethod
    def _normalize_question(raw: Dict[str, str]) -> Dict[str, str]:
        """Ensure required keys exist and options contain at least 4 entries."""
        question = raw.get("question", "").strip()
        answer = raw.get("answer", "").strip()
        context = raw.get("context", "").strip()
        options = raw.get("options") or []

        # Guarantee at least four options by adding simple distractors.
        filler = "None of the other options."
        while len(options) < 4:
            options.append(filler)

        return {
            "question": question,
            "answer": answer,
            "options": options[:4],
            "context": context or answer,
        }

    # ------------------------------------------------------------------ #
    # Local deterministic fallback
    # ------------------------------------------------------------------ #
    def _generate_locally(self, context: str, num_questions: int) -> List[Dict[str, str]]:
        sentences = self._tokenize_sentences(context)
        if not sentences:
            sentences = [context.strip() or "No context provided."]

        rng = random.Random(42)
        questions: List[QuizQuestion] = []

        for sentence in itertools.islice(itertools.cycle(sentences), num_questions):
            answer = sentence
            question = f"What does the following statement describe? \"{sentence}\""
            distractors = self._sample_distractors(rng, sentences, exclude=sentence)
            options = [answer] + distractors
            rng.shuffle(options)

            questions.append(
                QuizQuestion(
                    question=question,
                    answer=answer,
                    options=options,
                    context=sentence,
                )
            )

        return [q.as_dict() for q in questions]

    @staticmethod
    def _tokenize_sentences(text: str) -> List[str]:
        sentences = [
            s.strip()
            for s in re.split(r"(?<=[.!?])\s+", text)
            if s.strip()
        ]
        return sentences

    @staticmethod
    def _sample_distractors(rng: random.Random, sentences: Sequence[str], exclude: str) -> List[str]:
        distractor_pool = [s for s in sentences if s != exclude]
        filler = "The statement is unrelated to the topic."

        if len(distractor_pool) >= 3:
            return rng.sample(distractor_pool, 3)
        else:
            sampled = distractor_pool.copy()
            while len(sampled) < 3:
                sampled.append(filler)
            return sampled

    @staticmethod
    def _ensure_env_loaded() -> None:
        """Load .env/.env.local files sitting next to this module if present."""
        global _ENV_LOADED
        if _ENV_LOADED:
            return

        for filename in (".env", ".env.local"):
            path = os.path.join(BASE_DIR, filename)
            if not os.path.exists(path):
                continue
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    for raw_line in handle:
                        line = raw_line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "=" in line:
                            key, value = line.split("=", 1)
                        elif ":" in line:
                            key, value = line.split(":", 1)
                        else:
                            continue
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key and value and key not in os.environ:
                            os.environ[key] = value
            except OSError:
                continue

        _ENV_LOADED = True


__all__ = ["GeminiService", "QuizQuestion"]
