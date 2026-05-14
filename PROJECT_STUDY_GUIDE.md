# HireIQ Project Study Guide

## 1. What this project is

This project is an AI-powered mock interview system built with Streamlit.

The flow is:

1. The user enters their name and uploads a resume.
2. The app extracts text from the resume.
3. The Groq LLM analyzes the resume and generates interview questions.
4. The app asks questions using text-to-speech.
5. The candidate answers using speech-to-text.
6. The app evaluates each answer with AI and assigns a score.
7. The app may generate a follow-up question.
8. At the end, it shows a verdict, leaderboard, and downloadable PDF report.

This is a strong interview project because it combines:

- frontend UI using Streamlit
- AI/LLM integration using Groq
- OCR and document parsing
- speech recognition
- text-to-speech
- session state management
- report generation
- persistent leaderboard storage

---

## 2. Folder-by-folder explanation

### `app.py`
Main entry point. Controls page routing, UI, state management, question flow, evaluation flow, final report, and leaderboard display.

### `ai/`
Contains all LLM-powered logic.

- `question_generator.py`: creates main interview questions
- `followup_generator.py`: creates one deeper follow-up question
- `resume_analyzer.py`: summarizes skills, projects, and strengths from the resume
- `__init__.py`: marks `ai` as a Python package

### `core/`
Contains support/business logic.

- `evaluator.py`: evaluates answers and extracts score from AI output
- `parser.py`: extracts resume text from PDF, DOCX, TXT, and images
- `memory.py`: stores interview Q/A history for one session
- `leaderboard.py`: saves and loads leaderboard entries from JSON
- `report.py`: creates the PDF report
- `interview_agent.py`: an extra orchestration class for dynamic interviews; not currently used by `app.py`
- `__init__.py`: marks `core` as a Python package

### `voice/`
Contains voice-related features.

- `speech_to_text.py`: microphone input to text
- `text_to_speech.py`: question text to spoken audio
- `__init__.py`: marks `voice` as a Python package

### `style.css`
Custom styling for the Streamlit app. Makes the app look like a polished product instead of default Streamlit.

### `.env`
Stores secrets such as `GROQ_API_KEY`. This should never be committed publicly.

### `leaderboard.json`
Stores previous interview scores and metadata.

### `requirement.txt`
Lists Python dependencies needed to run the project.

### `Interview_Report.pdf`
Generated output PDF from a sample/mock interview run.

### `venv310/`
Local Python virtual environment. This is not project logic; it contains installed packages.

---

## 3. End-to-end architecture you can explain in an interview

Use this simple explanation:

"The application is built around `app.py`, which acts as the controller. It connects the user interface with helper modules. The `ai` package talks to Groq for resume analysis, question generation, follow-up generation, and answer evaluation. The `core` package handles parsing resumes, storing interview memory, generating the PDF report, and managing the leaderboard. The `voice` package handles speech input and output. Streamlit session state acts as the app's temporary memory across pages."

---

## 4. `app.py` line-by-line explanation

File: `app.py`

### Lines 1-3
- Import `streamlit` for UI.
- Import `time` for timer logic.
- Import `os` for file path handling.

### Lines 6-12
- Import helper functions from the `voice` and `core` packages.
- `listen()` captures microphone input.
- `speak()` reads a question aloud.
- `evaluate_answer()` sends answer to LLM for feedback.
- `extract_score()` pulls numeric score from that feedback.
- `generate_pdf()` builds the final report.
- `extract_text()` reads resume contents from uploaded file.
- `InterviewMemory` stores all answers in the current interview.
- `add_to_leaderboard()` and `get_leaderboard()` persist rankings.

### Lines 15-17
- Import the AI modules.
- `generate_questions()` creates main questions.
- `generate_followup()` creates a probing next question.
- `analyze_resume()` creates a short resume summary.

### Lines 22-27
- Configure the Streamlit page.
- `page_title` sets browser tab title.
- `layout="wide"` gives more horizontal space.
- `page_icon` adds branding.
- `initial_sidebar_state="collapsed"` hides the sidebar at start.

### Lines 33-40
- `_inject_css()` loads `style.css`.
- It builds the absolute path relative to the current file.
- Opens the CSS file with UTF-8 encoding.
- Reads all CSS as a string.0
- Injects it into the page using `<style>...</style>`.
- `_inject_css()` is then called immediately, so styles apply as soon as the app loads.

### Lines 46-52
- `OPENING_QUESTIONS` contains fixed warm-up questions.
- `CLOSING_QUESTION` contains the final "why should we hire you?" question.
- `HIRE_THRESHOLD = 7.0` defines the minimum average score for a positive verdict.
- `INTERVIEW_SECS = 900` sets a 15-minute interview time limit.

### Lines 58-75
- `_DEFAULTS` is the template for all Streamlit session variables.
- `page` tracks which screen to show: home, interview, or report.
- `q_index` tracks current question position.
- `spoken` avoids repeating text-to-speech every rerender.
- `results` stores evaluated answers.
- `start_time` stores when interview started.
- `questions` stores the full question set.
- `memory` stores session history object.
- `candidate_name`, `resume_summary` store candidate data.
- `enable_followup` toggles follow-up generation.
- `awaiting_followup`, `followup_q`, `current_answer` manage the follow-up workflow.
- The `for` loop initializes only missing values, so reruns do not wipe the session.

### Lines 81-82
- `score_class()` maps a numeric score to a CSS class.
- High, medium, and low scores get different colors.

### Lines 85-92
- `navbar()` renders the top navigation bar.
- It uses raw HTML via `st.markdown(..., unsafe_allow_html=True)`.
- The badge label changes depending on the page.

### Lines 95-103
- `advance()` moves the interview to the next question.
- Increments `q_index`.
- Resets all follow-up related state.
- If there are no more questions, it switches page to `"report"`.
- `st.rerun()` forces Streamlit to redraw based on the new state.

### Lines 106-134
- `handle_answer()` centralizes answer evaluation logic.
- Shows a spinner while the AI evaluates the answer.
- Calls `evaluate_answer(question, answer)`.
- Calls `extract_score(evaluation)` to get a numeric score.
- If anything fails, it falls back to `"Evaluation unavailable."` and score `5.0`.
- Gets the CSS class for score styling.
- Displays the user answer, AI feedback, and score pill.
- Stores the result in `InterviewMemory`.
- Also appends a dictionary to `st.session_state.results`.
- Returns the numeric score.

### Lines 140-243: `home()`

#### Lines 141-158
- Render the top navbar and hero section.
- This is the landing page branding and feature showcase.

#### Lines 160-174
- Create three columns and use the center one for the interview form.
- Ask for full name.
- Allow resume upload in PDF, image, TXT, or DOCX.
- Allow enabling/disabling AI follow-up questions.

#### Lines 176-179
- When Start Interview is clicked, validate that the candidate entered a name.

#### Lines 181-182
- Save candidate name and follow-up setting in session state.

#### Lines 184-187
- Initialize `resume_text`.
- If a file is uploaded, call `extract_text()` to parse it.

#### Lines 189-194
- If parsed resume text exists, send it to `analyze_resume()`.
- Save the returned summary into session state.
- If the LLM fails, fallback to empty summary.

#### Lines 196-206
- Generate AI interview questions.
- If resume text exists, use it as context.
- Otherwise use a generic software engineering prompt.
- If generation fails, fallback to 3 hardcoded safe questions.

#### Lines 208-218
- Build the full question list: opening + AI-generated + closing.
- Create fresh `InterviewMemory`.
- Reset question index, results, spoken state, follow-up state, current answer, and timer.
- Switch the page to `"interview"`.
- Force rerender.

#### Lines 221-243
- Show a leaderboard preview on the home page.
- Load entries using `get_leaderboard()`.
- Display top 8 entries with rank, name, score, and date.
- If no entries exist, show a placeholder message.

### Lines 249-401: `interview()`

#### Lines 250-256
- Show navbar.
- Check whether questions exist.
- If no questions exist, show an error and send user back home.

#### Lines 259-262
- Compute interview timer values.
- `elapsed` = seconds since start.
- `remaining` = total allowed time minus elapsed.
- `divmod` splits seconds into minutes and seconds.
- Timer color becomes danger red when less than 2 minutes remain.

#### Lines 264-279
- Render page wrapper.
- Show progress bar using `q_index / total_q`.
- Show textual question count.
- Show formatted timer.

#### Lines 281-288
- If time is over, switch to report page.
- If question index exceeds available questions, also switch to report.

#### Lines 290-292
- If a resume summary exists, show it in an expandable panel.

#### Lines 297-337: follow-up branch
- If `awaiting_followup` is true, the app knows it should ask the generated follow-up instead of the next main question.
- Load the follow-up question from session state.
- Render it with a follow-up badge.
- If it has not yet been spoken, call `speak(fq)` and mark it as spoken.
- Show buttons to record answer or skip.
- If the user clicks speak, call `listen()`.
- If the answer is still `None`, the app exits early and waits for the next rerender.
- If answer is `"TIMEOUT"`, skip forward.
- If answer is `"UNKNOWN"`, `"ERROR"`, or contains `"ERROR:"`, show an error and let the user retry.
- Otherwise evaluate the follow-up using `handle_answer(..., is_followup=True)`.
- Then call `advance()` and return.

#### Lines 340-355: main question display
- Load current question from the `questions` list.
- Set badge type based on whether the question is opening, closing, or normal.
- Render the question card with the proper badge.

#### Lines 357-384: main answer capture
- Speak the question if it was not spoken already.
- Show instructions and buttons.
- On click, `listen()` records the answer.
- Skip button immediately advances.
- If answer is still `None`, exit and wait.
- Reset `current_answer` after reading it.
- Handle timeout and recognition errors exactly like the follow-up branch.

#### Lines 386-399: post-answer logic
- Evaluate the answer with `handle_answer(q, ans)`.
- If follow-ups are enabled, ask Groq for a follow-up question.
- Save it to session state.
- Set `awaiting_followup = True`.
- Reset `spoken = False` so the new follow-up can be read aloud.
- Rerun the app.
- If follow-up generation fails, just move to next question.
- If follow-ups are disabled, advance directly.

### Lines 407-528: `report()`

#### Lines 408-422
- Show navbar and load `results`, `memory`, and candidate name.
- If no results exist, show warning and allow returning home.

#### Lines 424-426
- Compute average score from `InterviewMemory`.
- Count total answers.
- Decide whether candidate is "hired" using threshold comparison.

#### Lines 429-449
- Show either a congratulatory banner or a practice-more banner.
- This gives the project a clear hiring decision output.

#### Lines 452-456
- Show four key metrics: candidate, average score, number of questions, and verdict.

#### Lines 458-485
- Loop through each result.
- Decide which badge to show: follow-up, opening, closing, or standard.
- Use `score_class()` for score color.
- Render question, candidate answer, AI feedback, and score.

#### Lines 490-500
- Generate the PDF report.
- Open the PDF file in binary mode.
- Provide a Streamlit download button.
- If PDF generation fails, show a warning.

#### Lines 503-519
- Add this candidate to the leaderboard.
- Then display leaderboard rows from disk.
- Highlight the current candidate row with a custom border color.

#### Lines 522-526
- "Start New Interview" resets state back to defaults.
- Sends user back to home page.

### Lines 534-536
- This is a tiny router.
- It creates a dictionary mapping page names to functions.
- It fetches the correct page handler using the current session value.
- If the page key is missing, it defaults to `home`.
- Final `()` actually calls the function.

---

## 5. `ai/question_generator.py`

### Purpose
Generate main interview questions using the Groq API.

### Explanation
- Lines 1-3 import Groq client, OS utilities, and dotenv.
- Line 5 loads environment variables from `.env`.
- Line 6 creates a Groq client using `GROQ_API_KEY`.
- Lines 9-28 define `generate_questions`.
- Lines 11-16 build a prompt that tells the model to return exactly 5 interview questions.
- Lines 17-20 call Groq chat completion API with `llama-3.3-70b-versatile`.
- Line 21 extracts raw text from the model response.
- Lines 23-27 clean each line by removing numbering and blank lines.
- Line 28 returns only the first 5 cleaned questions.
- Lines 31-39 define `generate_question`, a single-question helper.
- This helper is used by `core/interview_agent.py`, not by `app.py`.

Good interview sentence:
"This module isolates question generation so the UI layer never talks to the LLM directly."

---

## 6. `ai/followup_generator.py`

### Purpose
Generate one deeper follow-up question based on the candidate's answer.

### Explanation
- Lines 1-6 repeat the same Groq client setup pattern.
- Lines 9-22 define `generate_followup(question, answer)`.
- The prompt includes both the original question and the candidate answer.
- It tells the model to ask one short probing follow-up and return only the question.
- The function returns the stripped model output.

Interview sentence:
"This improves realism because the interview becomes adaptive rather than static."

---

## 7. `ai/resume_analyzer.py`

### Purpose
Summarize the uploaded resume into skills, projects, strengths, and experience.

### Explanation
- Lines 1-6 set up the Groq client.
- Lines 9-27 define `analyze_resume(text)`.
- The prompt asks for key technical skills, notable projects, core strengths, and years of experience.
- The output is expected as bullet points.
- The function returns the model response as a summary string.

Interview sentence:
"This lets the system personalize the interview instead of asking the same generic questions to everyone."

---

## 8. `core/evaluator.py`

### Purpose
Evaluate candidate answers and extract a numeric score.

### Explanation
- Lines 1-7 set up Groq and regex support.
- Lines 10-29 define `evaluate_answer`.
- Prompt asks the model to return score, strengths, and improvements.
- The function returns the raw evaluation text.
- Lines 32-35 define `extract_score`.
- It uses regex to find a pattern like `7/10` or `8.5 / 10`.
- If no score is found, it returns default `5.0`.

Important concept:
This file separates "AI generation" from "score parsing". That makes the app easier to maintain.

---

## 9. `core/report.py`

### Purpose
Generate the PDF report.

### Explanation
- Line 1 imports `FPDF`.
- Line 2 imports `re`, though it is currently unused.
- Lines 5-7 define `_safe`, which replaces unsupported characters so `FPDF` does not crash on Unicode.
- Lines 10-57 define `generate_pdf`.
- It creates an `FPDF` object, enables automatic page breaks, and adds the first page.
- It writes the title and candidate name.
- It computes average score from all numeric score values.
- It writes overall score.
- Then it loops through each result.
- For each result it writes the question label, answer, score, and feedback.
- `multi_cell` is used for long text, which is important because normal `cell` would overflow.
- Finally it writes the file as `Interview_Report.pdf` and returns the filename.

Interview sentence:
"I added safe encoding and multi-line cells so real-world long answers would not break PDF export."

---

## 10. `core/parser.py`

### Purpose
Extract resume text from multiple file formats.

### Explanation
- Lines 1-5 import PDF, OCR, image, and DOCX libraries.
- Line 8 hardcodes the Tesseract executable path.
- Lines 11-65 define `extract_text(file)`.
- Lines 17-18 return empty string if no file is provided.
- Lines 20-21 read MIME type and reset file pointer.
- Lines 24-29 handle `.txt` files.
- It first tries UTF-8; if that fails, it falls back to Latin-1.
- Lines 32-47 handle PDFs.
- It first tries direct text extraction using `PyPDF2`.
- If no text is found, it assumes the PDF may be scanned.
- It converts PDF pages to images and runs OCR using Tesseract.
- Lines 50-55 handle DOCX files by reading paragraph text.
- Lines 58-63 handle image resumes by OCR.
- Line 65 returns empty string for unsupported types.
- Lines 68-71 define `_pdf_to_images`, a helper that converts PDF bytes to images using `pdf2image`.

Important concept:
This module supports both digital PDFs and scanned/image resumes, which makes the project much more practical.

---

## 11. `core/memory.py`

### Purpose
Store interview data for the current session.

### Explanation
- Line 1 defines `InterviewMemory`.
- Lines 4-8 initialize parallel lists for questions, answers, scores, and evaluations.
- Lines 11-16 define `store()`, which appends one full evaluated interview item.
- Lines 18-22 define `average_score()`.
- If there are no scores, it returns `0.0`.
- Otherwise it returns the rounded average.
- Lines 24-35 define `to_results()`, which zips all lists into a list of dictionaries.
- Lines 37-38 define `__len__()`, so `len(memory)` returns number of stored questions.

Concept:
This is a lightweight in-memory session model. It behaves like temporary interview storage.

---

## 12. `core/leaderboard.py`

### Purpose
Persist top scores to disk using JSON.

### Explanation
- Lines 1-3 import JSON, OS, and datetime.
- Line 5 stores the leaderboard filename.
- Lines 8-16 define `_load()`.
- If the file exists, it opens and parses JSON.
- If the file is corrupt or unreadable, it safely returns an empty list.
- Lines 19-22 define `_save(data)`.
- It writes leaderboard data back to disk with indentation.
- Lines 25-39 define `add_to_leaderboard`.
- It loads the board, appends a new entry, rounds score, stores question count and timestamp.
- Then it sorts entries by score descending and keeps top 20.
- Finally it saves the result.
- Lines 42-44 return leaderboard contents.
- Lines 47-49 clear leaderboard for testing.

Interview sentence:
"I used a simple JSON file instead of a database because the project scope was small and I wanted a zero-setup persistence layer."

---

## 13. `core/interview_agent.py`

### Purpose
Provide an interview orchestration class abstraction.

### Important note
`app.py` currently does not use this file directly. It looks like an alternate architecture or an earlier refactor.

### Explanation
- Lines 1-3 import question generation, follow-up generation, and memory.
- Lines 6-44 define `InterviewAgent`.
- Constructor creates a new `InterviewMemory`.
- `next_question()` checks whether any questions have been asked yet.
- If none were asked, it generates the first question using topic or resume context.
- Otherwise it generates a follow-up based on the most recent answer.
- It appends the chosen question into memory and returns it.
- `store_answer()` appends answer, score, and evaluation.

Interview-safe explanation:
"I also created an `InterviewAgent` abstraction to separate interview orchestration from the UI, although the current app flow is driven directly from Streamlit state."

---

## 14. `voice/speech_to_text.py`

### Purpose
Capture microphone input and transcribe it to text.

### Explanation
- Line 1 imports the `speech_recognition` library.
- Lines 4-31 define `listen()`.
- Parameters allow custom timeout, max phrase duration, and language code.
- It creates a recognizer object.
- Sets energy threshold and dynamic threshold to better handle background noise.
- `pause_threshold = 2.0` means recording ends after 2 seconds of silence.
- Opens the microphone using `sr.Microphone()`.
- Imports `streamlit` locally so status messages can be shown.
- Displays "Listening..." message.
- Adjusts for ambient noise.
- Records the audio.
- Displays "Processing..." message.
- Sends the audio to Google speech recognition.
- Returns text on success.
- Returns `"TIMEOUT"`, `"UNKNOWN"`, or `"ERROR"` for specific failure modes.
- Any unexpected exception is returned as `ERROR: ...`.

Concept:
Returning status strings instead of crashing makes the interview flow resilient.

---

## 15. `voice/text_to_speech.py`

### Purpose
Read questions aloud.

### Explanation
- Line 1 imports `pyttsx3`.
- Lines 4-26 define `speak(text, lang="en")`.
- Creates a TTS engine.
- Gets available voices from the system.
- If `lang == "hi"`, it tries to choose a Hindi voice.
- If no Hindi voice is found, it falls back to the first voice.
- For English, it uses the first voice directly.
- Sets speaking rate and volume.
- Queues the text using `engine.say(text)`.
- Plays it using `engine.runAndWait()`.
- On failure, it prints an error.

Concept:
This makes the mock interview feel like a real spoken interview instead of a text quiz.

---

## 16. `style.css`

### Purpose
Apply a premium custom design to the Streamlit app.

### Section-by-section explanation
- Imports Google Fonts `Syne` and `DM Sans`.
- Base section sets dark background, text color, font family, scrollbar styling, and hides default Streamlit chrome.
- Button section customizes button gradient, hover effect, shadow, font, and width.
- Input section styles text input fields.
- File uploader section styles upload box and hover state.
- Progress section customizes progress bar colors.
- Metrics section restyles Streamlit metric cards.
- Expander section styles the resume summary dropdown.
- Download button section gives report download a green-blue gradient.
- Misc section handles checkbox, alert, and column spacing.
- Custom component section defines reusable classes used in `app.py` such as:
  - `.hiq-navbar`
  - `.hiq-hero`
  - `.hiq-card`
  - `.hiq-card-accent`
  - `.hiq-question-badge`
  - `.hiq-q-text`
  - `.hiq-timer`
  - `.hiq-verdict-hired`
  - `.hiq-verdict-nohire`
  - `.hiq-lb-row`
  - `.hiq-answer-box`
  - `.hiq-feedback-box`
  - `.hiq-score-pill`
  - `.hiq-page-wrap`

Best interview explanation:
"The CSS file converts default Streamlit widgets into a branded product UI. I separated styling into a standalone CSS file and injected it into Streamlit because that is more reliable than embedding very large style blocks inside the Python file."

---

## 17. Data and config files

### `.env`
- Stores `GROQ_API_KEY`.
- Used by all Groq-based modules through `load_dotenv()` and `os.getenv(...)`.

### `leaderboard.json`
- Current stored leaderboard data.
- Each item has:
  - `name`
  - `score`
  - `questions`
  - `date`

### `requirement.txt`
- `groq`: LLM API access
- `streamlit`: web app framework
- `python-dotenv`: environment variable loading
- `PyPDF2`: PDF text extraction
- `pdf2image`: PDF page to image conversion
- `pytesseract`: OCR wrapper
- `Pillow`: image processing
- `python-docx`: DOCX parsing
- `fpdf`: report PDF generation
- `SpeechRecognition`: speech-to-text wrapper
- `pyttsx3`: offline text-to-speech
- `pyaudio`: microphone access

### `Interview_Report.pdf`
- Sample generated report output.
- Shows that report generation is functioning.

---

## 18. Strong points you can say in the interview

- "I designed the project in modules so UI, AI, voice, parsing, reporting, and persistence stay separated."
- "I used Streamlit session state as the application state manager across multiple pages."
- "I added support for multiple resume formats including scanned PDFs and images using OCR."
- "I made the interview adaptive by generating follow-up questions based on the candidate's answer."
- "I built fault tolerance with fallbacks for AI failures, PDF issues, and speech recognition errors."
- "I generated a downloadable PDF report and stored leaderboard history using a lightweight JSON persistence layer."

---

## 19. Honest limitations you can mention confidently

- The app depends on external services or local tools such as Groq API, Google STT through `SpeechRecognition`, and Tesseract OCR.
- `leaderboard.json` is simple but not ideal for multi-user concurrency.
- `app.py` is feature-rich, but large; it could be split into separate UI/page modules.
- `core/interview_agent.py` exists but is not fully integrated into the main app flow.
- Some UI text contains encoding artifacts because of copied Unicode characters, though functionality is still clear.

---

## 20. Best 60-second explanation

"This project is an AI interview coach built with Streamlit. A candidate uploads a resume, the app extracts and analyzes it, then uses Groq to generate personalized interview questions. The app asks questions aloud using text-to-speech, records spoken answers through speech recognition, evaluates each answer with AI, and optionally asks dynamic follow-up questions. At the end, it computes an average score, gives a hire or practice verdict, generates a downloadable PDF report, and stores the result on a leaderboard. I organized the project into `ai`, `core`, and `voice` modules so the UI stays separated from parsing, evaluation, reporting, and speech logic."

