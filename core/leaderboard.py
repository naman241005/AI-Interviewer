import json
import os
from datetime import datetime

LEADERBOARD_FILE = "leaderboard.json"


def _load() -> list[dict]:
    """Load leaderboard from disk. Returns empty list if file missing."""
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def _save(data: list[dict]):
    """Persist leaderboard to disk."""
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(data, f, indent=2)


def add_to_leaderboard(name: str, score: float, total_questions: int):
    """
    Add a new entry to the leaderboard.
    FIX: This entire file was just `[]` before — completely unimplemented.
    """
    board = _load()
    board.append({
        "name": name,
        "score": round(score, 1),
        "questions": total_questions,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    # Keep top 20 by score
    board = sorted(board, key=lambda x: x["score"], reverse=True)[:20]
    _save(board)


def get_leaderboard() -> list[dict]:
    """Return leaderboard sorted by score (highest first)."""
    return _load()


def clear_leaderboard():
    """Reset leaderboard (for testing)."""
    _save([])
