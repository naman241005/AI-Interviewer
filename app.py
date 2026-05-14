import streamlit as st
import time
import os

# ── Core modules ─────────────────────────────────────────────────
from voice.speech_to_text import listen
from voice.text_to_speech import speak
from core.evaluator import evaluate_answer, extract_score
from core.report import generate_pdf
from core.parser import extract_text
from core.memory import InterviewMemory
from core.leaderboard import add_to_leaderboard, get_leaderboard

# ── AI modules ───────────────────────────────────────────
from ai.question_generator import generate_questions
from ai.followup_generator import generate_followup
from ai.resume_analyzer import analyze_resume

# ═══════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="HireIQ — AI Interview Coach",
    layout="wide", 
    page_icon="🎯",
    initial_sidebar_state="collapsed",
)


# ═══════════════════════════════════════════════════════════════════
# CSS INJECTION  — loads from style.css to avoid Streamlit parser bugs
# ═══════════════════════════════════════════════════════════════════
def _inject_css():
    css_path = os.path.join(os.path.dirname(__file__), "style.css")
    with open(css_path, "r", encoding="utf-8") as f:
        css = f.read()
    # Wrap in <style> and inject — this is the most reliable method in Streamlit
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

_inject_css()


# ═══════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════
OPENING_QUESTIONS = [
    "Tell me about yourself — your background, what you have been working on, and what brings you here today.",
    "What are your key strengths? Give me a real example of how you have applied one of them.",
]
CLOSING_QUESTION = "Finally — why should we hire you? What makes you stand out from other candidates?"
HIRE_THRESHOLD   = 7.0   # avg score >= this → Congratulations verdict
INTERVIEW_SECS   = 900   # 15-minute session


# ═══════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════
_DEFAULTS = {
    "page"             : "home",
    "q_index"          : 0,
    "spoken"           : False,
    "results"          : [],
    "start_time"       : time.time(),
    "questions"        : [],
    "memory"           : None,
    "candidate_name"   : "",
    "resume_summary"   : "",
    "enable_followup"  : True,
    "awaiting_followup": False,
    "followup_q"       : "",
    "current_answer"   : None,
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ═══════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════
def score_class(s: float) -> str:
    return "score-high" if s >= 7.5 else ("score-mid" if s >= 5 else "score-low")


def navbar(label: str = ""):
    st.markdown(
        f"<div class='hiq-navbar'>"
        f"<div class='hiq-logo'>🎯 HireIQ</div>"
        f"<div class='hiq-nav-badge'>{label}</div>"
        f"</div>", 
        unsafe_allow_html=True, 
    )


def advance():
    st.session_state.q_index       += 1
    st.session_state.spoken         = False
    st.session_state.awaiting_followup = False
    st.session_state.followup_q     = ""
    st.session_state.current_answer = None
    if st.session_state.q_index >= len(st.session_state.questions):
        st.session_state.page = "report"
    st.rerun()


def handle_answer(question: str, answer: str, is_followup: bool = False) -> float:
    with st.spinner("Analysing your answer..."):
        try:
            evaluation = evaluate_answer(question, answer)
            score      = extract_score(evaluation)
        except Exception:
            evaluation = "Evaluation unavailable."
            score      = 5.0

    sc = score_class(score)
    st.markdown(
        f"<div class='hiq-answer-box'>"
        f"<b style='color:#9C88FF;font-size:12px;text-transform:uppercase;letter-spacing:1px'>Your Answer</b>"
        f"<br><br>{answer}</div>"
        f"<div class='hiq-feedback-box'>"
        f"<b style='color:#9C88FF;font-size:12px;text-transform:uppercase;letter-spacing:1px'>AI Feedback</b>"
        f"<br><br>{evaluation}</div>"
        f"<span class='hiq-score-pill {sc}'>Score: {score}/10</span>",
        unsafe_allow_html=True,
    )
    st.session_state.memory.store(question, answer, score, evaluation)
    st.session_state.results.append({
        "question"   : question,
        "answer"     : answer,
        "score"      : score,
        "evaluation" : evaluation,
        "is_followup": is_followup,
    })
    return score


# ═══════════════════════════════════════════════════════════════════
# HOME PAGE
# ═══════════════════════════════════════════════════════════════════
def home():
    navbar("Home")

    st.markdown(
        "<div class='hiq-hero'>"
        "<div class='hiq-hero-tag'>✦ AI-Powered Interview Coach</div>"
        "<div class='hiq-hero-title'>Ace Your Next<br><span>Interview.</span></div>"
        "<div class='hiq-hero-sub'>Upload your resume. Speak your answers.<br>"
        "Get real AI feedback, scores, and a downloadable report.</div>"
        "<div class='hiq-features'>"
        "<div class='hiq-feature-chip'>🎤 Voice Recognition</div>"
        "<div class='hiq-feature-chip'>🧠 AI Evaluation</div>"
        "<div class='hiq-feature-chip'>🔁 Smart Follow-ups</div>"
        "<div class='hiq-feature-chip'>📄 PDF Report</div>"
        "<div class='hiq-feature-chip'>🏆 Leaderboard</div>"
        "<div class='hiq-feature-chip'>✅ Hire Verdict</div>"
        "</div></div>",
        unsafe_allow_html=True,
    )

    _, col_form, _ = st.columns([1, 2, 1])
    with col_form:
        st.markdown("<div class='hiq-card-accent'>", unsafe_allow_html=True)
        st.markdown(
            "<div style='font-family:Syne,sans-serif;font-size:20px;"
            "font-weight:700;margin-bottom:20px;color:#E8EAF0'>Start Your Interview</div>",
            unsafe_allow_html=True,
        )
        name    = st.text_input("👤 Full Name", placeholder="e.g. Rohan Sharma")
        resume  = st.file_uploader(
            "📄 Upload Resume  (PDF · DOCX · Image · TXT)",
            type=["pdf", "png", "jpg", "jpeg", "txt", "docx"],
        )
        followup = st.checkbox("🔁 Enable AI Follow-up Questions", value=True)
        st.markdown("</div>", unsafe_allow_html=True)

        if st.button("🚀 Start Interview"):
            if not name.strip():
                st.warning("Please enter your name before starting.")
                return

            st.session_state.candidate_name  = name.strip()
            st.session_state.enable_followup = followup

            resume_text = ""
            if resume:
                with st.spinner("Reading resume..."):
                    resume_text = extract_text(resume)

            if resume_text.strip():
                with st.spinner("Analysing resume..."):
                    try:
                        st.session_state.resume_summary = analyze_resume(resume_text)
                    except Exception:
                        st.session_state.resume_summary = ""

            with st.spinner("Building your question set..."):
                try:
                    ai_qs = generate_questions(
                        resume_text or "General software engineering interview"
                    )
                except Exception:
                    ai_qs = [
                        "Walk me through a challenging technical project you have worked on.",
                        "How do you approach debugging a complex problem?",
                        "Describe your experience working in a team.",
                    ]

            st.session_state.questions     = OPENING_QUESTIONS + ai_qs + [CLOSING_QUESTION]
            st.session_state.memory        = InterviewMemory()
            st.session_state.q_index       = 0
            st.session_state.results       = []
            st.session_state.spoken        = False
            st.session_state.awaiting_followup = False
            st.session_state.followup_q    = ""
            st.session_state.current_answer = None
            st.session_state.start_time    = time.time()
            st.session_state.page          = "interview"
            st.rerun()

    # ── Leaderboard preview ────────────────────────────────────
    st.markdown("<div class='hiq-page-wrap' style='padding-top:40px'>", unsafe_allow_html=True)
    st.markdown("<div class='hiq-section-title'>🏆 Leaderboard</div>", unsafe_allow_html=True)
    board = get_leaderboard()
    if board:
        for rank, e in enumerate(board[:8], 1):
            rc    = {1: "top1", 2: "top2", 3: "top3"}.get(rank, "")
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")
            st.markdown(
                f"<div class='hiq-lb-row'>"
                f"<div class='hiq-lb-rank {rc}'>{medal}</div>"
                f"<div class='hiq-lb-name'>{e['name']}</div>"
                f"<div class='hiq-lb-score'>{e['score']}/10</div>"
                f"<div class='hiq-lb-date'>{e['date']}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            "<div style='color:#4a5d75;text-align:center;padding:40px;"
            "font-family:DM Sans,sans-serif'>No entries yet — be the first!</div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# INTERVIEW PAGE
# ═══════════════════════════════════════════════════════════════════
def interview():
    navbar("Live Interview")

    total_q = len(st.session_state.questions)
    if total_q == 0:
        st.error("No questions found!")
        st.session_state.page = "home"
        st.rerun()

    # Timer
    elapsed   = int(time.time() - st.session_state.start_time)
    remaining = max(0, INTERVIEW_SECS - elapsed)
    mins, secs = divmod(remaining, 60)
    timer_cls  = "hiq-timer-danger" if remaining < 120 else "hiq-timer"

    st.markdown("<div class='hiq-page-wrap'>", unsafe_allow_html=True)

    # Progress bar + timer row
    c1, c2 = st.columns([3, 1])
    with c1:
        st.progress(min(st.session_state.q_index / total_q, 1.0))
        st.markdown(
            f"<div style='font-size:13px;color:#4a5d75;margin-top:4px'>"
            f"Question {min(st.session_state.q_index+1, total_q)} of {total_q}</div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"<div class='{timer_cls}'>⏱ {mins:02d}:{secs:02d}</div>",
            unsafe_allow_html=True,
        )

    if remaining <= 0:
        st.error("Time is up!")
        st.session_state.page = "report"
        st.rerun()

    if st.session_state.q_index >= total_q:
        st.session_state.page = "report"
        st.rerun()

    if st.session_state.resume_summary:
        with st.expander("📋 Resume Summary", expanded=False):
            st.markdown(st.session_state.resume_summary)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    # ── Follow-up branch ──────────────────────────────────────
    if st.session_state.awaiting_followup:
        fq = st.session_state.followup_q
        st.markdown(
            f"<div class='hiq-card-accent'>"
            f"<span class='hiq-question-badge badge-followup'>🔁 Follow-up</span><br>"
            f"<div class='hiq-q-text'>{fq}</div></div>",
            unsafe_allow_html=True,
        )

        if not st.session_state.spoken:
            st.session_state.spoken = True
            speak(fq)

        st.markdown("<div class='hiq-tip'>Take your time — up to 2 minutes to answer.</div>", unsafe_allow_html=True)
        bc, sc = st.columns([2, 1])
        with bc:
            if st.button("🎙 Speak Your Answer"):
                try:    st.session_state.current_answer = listen()
                except: st.session_state.current_answer = "ERROR"
        with sc:
            if st.button("⏭ Skip"):
                advance()
                return

        ans = st.session_state.current_answer
        if ans is None:
            st.markdown("</div>", unsafe_allow_html=True)
            return
        st.session_state.current_answer = None

        if ans == "TIMEOUT":
            st.warning("No speech detected. Skipping...")
            advance()
            return
        if ans in ("UNKNOWN", "ERROR") or "ERROR:" in str(ans):
            st.error("Could not understand. Please try again.")
            return

        handle_answer(fq, ans, is_followup=True)
        advance()
        return

    # ── Main question branch ──────────────────────────────────
    q   = st.session_state.questions[st.session_state.q_index]
    idx = st.session_state.q_index

    if idx < len(OPENING_QUESTIONS):
        badge_cls, badge_lbl = "badge-fixed", "Opening"
    elif idx == total_q - 1:
        badge_cls, badge_lbl = "badge-final", "Closing"
    else:
        badge_cls, badge_lbl = "badge-main", f"Question {idx + 1}"

    st.markdown(
        f"<div class='hiq-card-accent'>"
        f"<span class='hiq-question-badge {badge_cls}'>{badge_lbl}</span><br>"
        f"<div class='hiq-q-text'>{q}</div></div>",
        unsafe_allow_html=True,
    )

    if not st.session_state.spoken:
        st.session_state.spoken = True
        speak(q)

    st.markdown("<div class='hiq-tip'>Take your time — up to 2 minutes to answer.</div>", unsafe_allow_html=True)
    bc, sc = st.columns([2, 1])
    with bc:
        if st.button("🎙 Speak Your Answer"):
            try:    st.session_state.current_answer = listen()
            except: st.session_state.current_answer = "ERROR"
    with sc:
        if st.button("⏭ Skip Question"):
            advance()
            return

    ans = st.session_state.current_answer
    if ans is None:
        st.markdown("</div>", unsafe_allow_html=True)
        return
    st.session_state.current_answer = None

    if ans == "TIMEOUT":
        st.warning("No speech detected. Skipping...")
        advance()
        return
    if ans in ("UNKNOWN", "ERROR") or "ERROR:" in str(ans):
        st.error("Could not understand. Please try again.")
        return

    handle_answer(q, ans)

    if st.session_state.enable_followup:
        with st.spinner("Generating follow-up question..."):
            try:
                fq = generate_followup(q, ans)
                st.session_state.followup_q        = fq
                st.session_state.awaiting_followup = True
                st.session_state.spoken            = False
                st.rerun()
            except Exception:
                advance()
    else:
        advance()

    st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# REPORT PAGE
# ═══════════════════════════════════════════════════════════════════
def report():
    navbar("Interview Report")

    results = st.session_state.results
    memory  = st.session_state.memory
    name    = st.session_state.candidate_name

    st.markdown("<div class='hiq-page-wrap'>", unsafe_allow_html=True)

    if not results:
        st.warning("No answers were recorded.")
        if st.button("Back to Home"):
            st.session_state.page = "home"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        return

    avg   = memory.average_score() if memory else 0.0
    total = len(results)
    hired = avg >= HIRE_THRESHOLD

    # ── Hire / No-Hire verdict ─────────────────────────────────
    if hired:
        st.markdown(
            f"<div class='hiq-verdict-hired'>"
            f"<div class='hiq-verdict-icon'>🎉</div>"
            f"<div class='hiq-verdict-title' style='color:#00C6A2'>Congratulations, {name}!</div>"
            f"<div class='hiq-verdict-sub'>You scored <b style='color:#00C6A2'>{avg}/10</b> — "
            f"above our hiring threshold of {HIRE_THRESHOLD}/10. "
            f"You showed strong communication, technical depth, and confidence. "
            f"We would be glad to have you on the team!</div></div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<div class='hiq-verdict-nohire'>"
            f"<div class='hiq-verdict-icon'>💪</div>"
            f"<div class='hiq-verdict-title' style='color:#FF6B5D'>Keep Practising, {name}!</div>"
            f"<div class='hiq-verdict-sub'>You scored <b style='color:#FF6B5D'>{avg}/10</b> — "
            f"just below our threshold of {HIRE_THRESHOLD}/10. "
            f"Review the feedback below, work on the weak areas, and come back stronger!</div></div>",
            unsafe_allow_html=True,
        )

    # ── Stats row ─────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Candidate", name)
    c2.metric("Avg Score",  f"{avg}/10")
    c3.metric("Questions",  total)
    c4.metric("Verdict",    "Hired" if hired else "Not Yet")

    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='hiq-section-title'>Detailed Breakdown</div>", unsafe_allow_html=True)

    # ── Per-question cards ─────────────────────────────────────
    for i, r in enumerate(results):
        if r.get("is_followup"):
            badge = "<span class='hiq-question-badge badge-followup'>Follow-up</span>"
        elif i < len(OPENING_QUESTIONS):
            badge = "<span class='hiq-question-badge badge-fixed'>Opening</span>"
        elif i == len(results) - 1:
            badge = "<span class='hiq-question-badge badge-final'>Closing</span>"
        else:
            badge = f"<span class='hiq-question-badge badge-main'>Q{i+1}</span>"

        sc = score_class(r["score"])
        st.markdown(
            f"<div class='hiq-card'>{badge}"
            f"<div style='font-family:Syne,sans-serif;font-size:16px;font-weight:600;"
            f"color:#E8EAF0;margin:10px 0 14px'>{r['question']}</div>"
            f"<div class='hiq-answer-box'>"
            f"<b style='color:#9C88FF;font-size:12px;text-transform:uppercase;letter-spacing:1px'>Your Answer</b>"
            f"<br><br>{r['answer']}</div>"
            f"<div class='hiq-feedback-box'>"
            f"<b style='color:#9C88FF;font-size:12px;text-transform:uppercase;letter-spacing:1px'>AI Feedback</b>"
            f"<br><br>{r['evaluation']}</div>"
            f"<span class='hiq-score-pill {sc}'>Score: {r['score']}/10</span></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── PDF download ───────────────────────────────────────────
    try:
        pdf_path = generate_pdf(results, candidate_name=name)
        with open(pdf_path, "rb") as f:
            st.download_button(
                "📄 Download Full PDF Report",
                f,
                file_name=f"HireIQ_Report_{name.replace(' ', '_')}.pdf",
                mime="application/pdf",
            )
    except Exception as e:
        st.warning(f"PDF generation failed: {e}")

    # ── Leaderboard ────────────────────────────────────────────
    add_to_leaderboard(name, avg, total)
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    st.markdown("<div class='hiq-section-title'>🏆 Leaderboard</div>", unsafe_allow_html=True)

    for rank, e in enumerate(get_leaderboard()[:10], 1):
        rc    = {1: "top1", 2: "top2", 3: "top3"}.get(rank, "")
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")
        hl    = "border-color:rgba(108,99,255,0.5)" if e["name"] == name else ""
        st.markdown(
            f"<div class='hiq-lb-row' style='{hl}'>"
            f"<div class='hiq-lb-rank {rc}'>{medal}</div>"
            f"<div class='hiq-lb-name'>{e['name']}</div>"
            f"<div class='hiq-lb-score'>{e['score']}/10</div>"
            f"<div class='hiq-lb-date'>{e['questions']} Qs · {e['date']}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
    if st.button("🔄 Start New Interview"):
        for k, v in _DEFAULTS.items():
            st.session_state[k] = v
        st.session_state.page = "home"
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════════
{"home": home, "interview": interview, "report": report}.get(
    st.session_state.page, home
)()
