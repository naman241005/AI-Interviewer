```python
import speech_recognition as sr
import tempfile
from audio_recorder_streamlit import audio_recorder
import streamlit as st


def listen(language: str = "en-IN") -> str:
    """
    Record audio from browser microphone and transcribe it.
    Returns:
        transcribed text
        OR TIMEOUT | UNKNOWN | ERROR
    """

    recognizer = sr.Recognizer()

    st.info("🎤 Click record and speak your answer")

    audio_bytes = audio_recorder(
        pause_threshold=2.0,
        sample_rate=41000
    )

    if not audio_bytes:
        return "TIMEOUT"

    try:
        # Save temporary WAV file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio_bytes)
            temp_audio_path = temp_audio.name

        # Read audio file
        with sr.AudioFile(temp_audio_path) as source:
            audio = recognizer.record(source)

        st.info("🧠 Processing your voice...")

        text = recognizer.recognize_google(audio, language=language)

        return text

    except sr.UnknownValueError:
        return "UNKNOWN"

    except sr.RequestError:
        return "ERROR"

    except Exception as e:
        return f"ERROR: {str(e)}"
```
