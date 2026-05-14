from groq import Groq
import os
import re
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def evaluate_answer(question: str, answer: str) -> str:
    """Evaluate a candidate's answer and return score + feedback."""
    prompt = f"""
    Evaluate this interview answer professionally.

    Question: {question}
    Answer: {answer}

    Provide:
    - Score: X/10
    - Strengths: (one line)
    - Improvements: (one line)

    Be concise and constructive.
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def extract_score(evaluation_text: str) -> float:
    """Parse numeric score from evaluation text. Returns 5.0 as default."""
    match = re.search(r'(\d+(?:\.\d+)?)\s*/\s*10', evaluation_text)
    return float(match.group(1)) if match else 5.0
