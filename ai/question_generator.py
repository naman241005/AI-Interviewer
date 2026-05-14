from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_questions(resume_text: str) -> list[str]:
    """Generate 5 interview questions from a resume."""
    prompt = f"""
    Generate exactly 5 professional interview questions (mix of HR and technical)
    based on this resume. Number each question 1-5. Output only the questions, nothing else.

    {resume_text}
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",   # FIX: llama3-70b-8192 is deprecated
        messages=[{"role": "user", "content": prompt}]
    )
    text = response.choices[0].message.content
    # Strip numbering and blank lines
    questions = [
        line.strip().lstrip("0123456789.)- ").strip()
        for line in text.split("\n")
        if line.strip() and any(c.isalpha() for c in line)
    ]
    return questions[:5]


def generate_question(topic: str) -> str:
    """Generate a single interview question on a given topic.
    Used by InterviewAgent for one-at-a-time question generation."""
    prompt = f"Generate one professional interview question about: {topic}. Output only the question."
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()
