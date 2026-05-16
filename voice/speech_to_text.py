import speech_recognition as sr
import tempfile
import streamlit as st
from audio_recorder_streamlit import audio_recorder
import os


def listen(language="en-IN"):

    st.info("🎤 Click the microphone and answer the question")

    # Recorder
    audio_bytes = audio_recorder(
        text="🎙 Click to Record",
        recording_color="#ff4b4b",
        neutral_color="#6c63ff",
        icon_name="microphone",
        icon_size="2x",
        pause_threshold=6.0,
        sample_rate=44100
    )

    # Nothing recorded yet
    if audio_bytes is None:
        return None

    # Tiny accidental tap
    if len(audio_bytes) < 8000:
        return "TIMEOUT"

    temp_audio_path = None

    try:
        recognizer = sr.Recognizer()

        # Better recognition settings
        recognizer.energy_threshold = 300
        recognizer.dynamic_energy_threshold = True

        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio_bytes)
            temp_audio_path = temp_audio.name

        # Read audio
        with sr.AudioFile(temp_audio_path) as source:

            recognizer.adjust_for_ambient_noise(
                source,
                duration=0.5
            )

            audio = recognizer.record(source)

        st.success("🧠 Processing your answer...")

        # Speech recognition
        text = recognizer.recognize_google(
            audio,
            language=language
        )

        # Empty transcription
        if not text.strip():
            return "UNKNOWN"

        return text.strip()

    except sr.UnknownValueError:
        return "UNKNOWN"

    except sr.RequestError:
        return "ERROR"

    except Exception as e:
        return f"ERROR: {str(e)}"

    finally:
        # Cleanup temp file
        if temp_audio_path and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)