from fpdf import FPDF
import re


def _safe(text: str) -> str:
    """Strip non-latin-1 characters to avoid FPDF encoding crashes."""
    return text.encode("latin-1", errors="replace").decode("latin-1")


def generate_pdf(results: list[dict], candidate_name: str = "Candidate") -> str:
    """
    Generate a PDF interview report.

    FIX 1: Now returns the filename so app.py can open it.
    FIX 2: Uses multi_cell instead of cell — long text no longer overflows.
    FIX 3: Handles both 'score' and 'evaluation' keys safely.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ── Title ──────────────────────────────────────────────
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 12, txt="AI Interview Report", ln=True, align="C")

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, txt=f"Candidate: {_safe(candidate_name)}", ln=True, align="C")
    pdf.ln(6)

    # ── Average score ──────────────────────────────────────
    scores = [r.get("score", 5) for r in results if isinstance(r.get("score"), (int, float))]
    avg = round(sum(scores) / len(scores), 1) if scores else "N/A"
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 10, txt=f"Overall Score: {avg}/10", ln=True)
    pdf.ln(4)

    # ── Per question ───────────────────────────────────────
    for i, r in enumerate(results):
        pdf.set_font("Arial", "B", 12)
        label = "Follow-up" if r.get("is_followup") else f"Question {i + 1}"
        pdf.cell(0, 8, txt=f"{label}: {_safe(r.get('question', ''))}", ln=True)

        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 7, txt=f"Answer: {_safe(r.get('answer', ''))}")

        score_val = r.get("score", "N/A")
        pdf.cell(0, 7, txt=f"Score: {score_val}/10", ln=True)

        evaluation = _safe(r.get("evaluation", ""))
        if evaluation:
            pdf.multi_cell(0, 7, txt=f"Feedback: {evaluation}")

        pdf.ln(4)

    filename = "Interview_Report.pdf"
    pdf.output(filename)
    return filename   # FIX: was missing — app.py crashed trying to open None
