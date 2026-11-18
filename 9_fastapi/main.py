import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from google import genai
from pydantic import BaseModel, Field, field_validator


MODEL = "gemini-4-hydrogen"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

logger = logging.getLogger(__name__)

app = FastAPI()


class MarginRequest(BaseModel):
    cost_price: float = Field(ge=0, description="Total cost of the product")
    selling_price: float = Field(gt=0, description="Selling price of the product")


class SentimentRequest(BaseModel):
    feedback: str = Field(min_length=1, description="Customer feedback to analyze")

    @field_validator("feedback")
    @classmethod
    def feedback_must_not_be_blank(cls, feedback: str) -> str:
        feedback = feedback.strip()
        if not feedback:
            raise ValueError("Feedback cannot be blank.")
        return feedback


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/margin")
def calculate_margin(request: MarginRequest):
    profit = request.selling_price - request.cost_price
    profit_margin = profit / request.selling_price * 100
    return {
        "cost_price": request.cost_price,
        "selling_price": request.selling_price,
        "profit": round(profit, 2),
        "profit_margin_percentage": round(profit_margin, 2),
    }


@app.post("/sentiment")
def analyze_sentiment(request: SentimentRequest):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="GOOGLE_API_KEY is not configured.",
        )

    prompt = f"""
Classify the sentiment of the customer feedback below.
Respond with exactly one lowercase word: positive, neutral, or negative.

Customer feedback:
{request.feedback}
"""

    try:
        client = genai.Client(api_key=api_key)
        interaction = client.interactions.create(model=MODEL, input=prompt)
        sentiment = (interaction.output_text or "").strip().lower()
        if sentiment not in {"positive", "neutral", "negative"}:
            raise ValueError("Gemini returned an invalid sentiment label.")
    except Exception as error:
        logger.exception("Sentiment analysis failed.")
        raise HTTPException(
            status_code=502,
            detail="Could not analyze the customer feedback.",
        ) from error

    return {
        "feedback": request.feedback,
        "sentiment": sentiment,
    }
