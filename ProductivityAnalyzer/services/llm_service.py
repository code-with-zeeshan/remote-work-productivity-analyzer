# services/llm_service.py
"""
LLM-based productivity summaries and natural language queries.
Uses OpenAI API (optional - gracefully falls back if not configured).
"""

import os

from database.models import DailySummary
from utils.logger import setup_logger

logger = setup_logger("services.llm")


class LLMService:
    """Provides AI-powered productivity insights using OpenAI (optional)."""

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self._client = None
        self._available = False
        self._init_client()

    def _init_client(self) -> None:
        """Initialize OpenAI client if available."""
        if not self.api_key:
            logger.info("OpenAI API key not configured. LLM features disabled.")
            return

        try:
            from openai import OpenAI

            self._client = OpenAI(api_key=self.api_key)
            self._available = True
            logger.info("OpenAI LLM service initialized")
        except ImportError:
            logger.info("openai package not installed. LLM features disabled.")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")

    @property
    def is_available(self) -> bool:
        return self._available

    def generate_daily_summary(self, summary: DailySummary) -> str:
        """Generate a natural language summary of the day's productivity."""
        if not self._available:
            return self._fallback_summary(summary)

        prompt = f"""You are a productivity coach. Analyze this daily work data and provide a brief,
encouraging 2-3 sentence summary with one actionable tip.

Data:
- Date: {summary.date}
- Productive time: {summary.productive_minutes:.0f} minutes
- Unproductive time: {summary.unproductive_minutes:.0f} minutes
- Neutral time: {summary.neutral_seconds / 60:.0f} minutes
- Idle time: {summary.idle_seconds / 60:.0f} minutes
- Productivity Score: {summary.score}/100 (Grade: {summary.grade})
- Total tracked entries: {summary.total_entries}

Be concise, specific, and actionable. Do not use emojis."""

        try:
            response = self._client.chat.completions.create(  # type: ignore[union-attr]
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7,
            )
            result = response.choices[0].message.content
            logger.debug(f"LLM summary generated for {summary.date}")
            return result.strip() if result else self._fallback_summary(summary)
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return self._fallback_summary(summary)

    def answer_query(self, question: str, context: str) -> str:
        """Answer a natural language question about productivity data."""
        if not self._available:
            return self._fallback_query(question)

        prompt = f"""You are a productivity analytics assistant. Answer the user's question
based on the provided data context. Be concise and data-driven.

Context:
{context}

Question: {question}

Answer briefly in 1-3 sentences."""

        try:
            response = self._client.chat.completions.create(  # type: ignore[union-attr]
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.5,
            )
            result = response.choices[0].message.content
            return result.strip() if result else "Could not generate an answer."
        except Exception as e:
            logger.error(f"LLM query failed: {e}")
            return self._fallback_query(question)

    @staticmethod
    def _fallback_summary(summary: DailySummary) -> str:
        """Generate a rule-based summary when LLM is not available."""
        if summary.total_seconds == 0:
            return "No activity tracked today. Start tracking to see insights."

        total_min = summary.total_seconds / 60
        prod_pct = (summary.productive_seconds / summary.total_seconds * 100) if summary.total_seconds else 0

        if summary.score >= 80:
            tone = "Excellent day!"
            tip = "Keep up this momentum tomorrow."
        elif summary.score >= 60:
            tone = "Good effort today."
            tip = "Try to reduce distractions by 15 minutes tomorrow."
        elif summary.score >= 40:
            tone = "Mixed day."
            tip = "Consider using Focus Mode during your peak hours."
        else:
            tone = "Room for improvement."
            tip = "Start with a 25-minute focused sprint first thing tomorrow."

        return (
            f"{tone} You tracked {total_min:.0f} minutes with "
            f"{prod_pct:.0f}% productive time (Score: {summary.score}/100). "
            f"{tip}"
        )

    @staticmethod
    def _fallback_query(question: str) -> str:
        """Simple keyword-based query handler."""
        q = question.lower()

        if "score" in q or "productive" in q:
            return "Check the Dashboard for your current productivity score and breakdown."
        elif "focus" in q or "distract" in q:
            return "Try enabling Focus Mode from the Focus Mode page to block distracting apps."
        elif "goal" in q:
            return "You can set and manage goals from the Goals page."
        elif "export" in q or "report" in q:
            return "Go to Reports page to generate charts and export CSV/PDF reports."
        else:
            return "Check the Dashboard for an overview, or navigate to specific pages for details."
