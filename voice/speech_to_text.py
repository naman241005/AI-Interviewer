import speech_recognition as sr


def listen(timeout: int = 20, phrase_time_limit: int = 120, language: str = "en-IN") -> str:
    """
    Record audio from the microphone and transcribe it.
    Returns: transcribed text, or one of: TIMEOUT | UNKNOWN | ERROR
    """
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 2.0    # wait 2s of silence before stopping (was 1.0)
    recognizer.non_speaking_duration = 1.5

    try:
        with sr.Microphone() as source:
            import streamlit as st
            st.info("🎤 Listening... Speak now (up to 2 minutes)")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            st.info("🧠 Processing your voice...")
            return recognizer.recognize_google(audio, language=language)

    except sr.WaitTimeoutError:
        return "TIMEOUT"
    except sr.UnknownValueError:
        return "UNKNOWN"
    except sr.RequestError:
        return "ERROR"
    except Exception as e:
        return f"ERROR: {str(e)}"
