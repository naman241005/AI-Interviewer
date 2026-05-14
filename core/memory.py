class InterviewMemory:
    """Stores all interview data for a single session."""

    def __init__(self):
        self.questions = []
        self.answers = []
        self.scores = []
        self.evaluations = []

    # FIX: class had no methods — completely unusable before
    def store(self, question: str, answer: str, score: float, evaluation: str):
        """Save one Q&A pair with its score and evaluation."""
        self.questions.append(question)
        self.answers.append(answer)
        self.scores.append(score)
        self.evaluations.append(evaluation)

    def average_score(self) -> float:
        """Return average score across all answered questions."""
        if not self.scores:
            return 0.0
        return round(sum(self.scores) / len(self.scores), 2)

    def to_results(self) -> list[dict]:
        """Export data as a list of dicts for report generation."""
        return [
            {
                "question": q,
                "answer": a,
                "score": s,
                "evaluation": e
            }
            for q, a, s, e in zip(
                self.questions, self.answers, self.scores, self.evaluations
            )    ]

    def __len__(self):
        return len(self.questions)
