import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_followup(question: str, answer: str) -> str:
    """Generate one deeper follow-up question based on the candidate's answer."""
    prompt = f"""
    The interviewer asked: {question}
    The candidate answered: {answer} 

    Ask one short, deeper follow-up question that probes the candidate's answer further.
    Output only the follow-up question, nothing else.
    """
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


