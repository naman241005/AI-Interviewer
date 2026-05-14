import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def analyze_resume(text: str) -> str:
    """Extract skills, projects, and strengths from resume text."""
    prompt = f"""
    Analyze this resume and extract:
    - Key technical skills
    - Notable projects
    - Core strengths
    - Years of experience (if mentioned)

    Return a clean, concise bullet-point summary.

    Resume:
    {text}
    """
    res = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # FIX: was misindented causing SyntaxError
        messages=[{"role": "user", "content": prompt}]
    )
    return res.choices[0].message.content
