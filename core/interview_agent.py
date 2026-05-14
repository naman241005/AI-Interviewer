from ai.question_generator import generate_question    # FIX: was wrong path ai.question_generator (no package init)
from ai.followup_generator import generate_followup    # FIX: same path issue
from core.memory import InterviewMemory                 # FIX: same path issue


class InterviewAgent:
    """
    Orchestrates a dynamic interview session.
    - Asks the first question on a topic
    - Generates context-aware follow-ups based on each answer
    - Stores full session in InterviewMemory
    """

    def __init__(self):
        self.memory = InterviewMemory()

    def next_question(self, topic: str, resume_text: str = None) -> str:
        """Return the next question to ask the candidate."""

        # First question of the session
        if len(self.memory) == 0:
            context = f"{topic} based on this resume:\n{resume_text}" if resume_text else topic
            q = generate_question(context)   # FIX: was generate_questions (plural) — doesn't exist

        # Follow-up based on last answer
        else:
            last_q = self.memory.questions[-1]

            if len(self.memory.answers) == 0:
                # Safety guard: no answer stored yet, re-ask current question
                return last_q

            last_ans = self.memory.answers[-1]
            q = generate_followup(last_q, last_ans)

        self.memory.questions.append(q)
        return q

    def store_answer(self, answer: str, score: float, evaluation: str = ""):
        """Save the candidate's answer along with its score."""
        # FIX: original only stored answer+score, evaluation was lost
        self.memory.answers.append(answer)
        self.memory.scores.append(score)
        self.memory.evaluations.append(evaluation)
