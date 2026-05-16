import pyttsx3
import threading

engine = pyttsx3.init()

engine.setProperty("rate", 165)
engine.setProperty("volume", 1.0)

speech_lock = threading.Lock()


def speak(text):

    try:
        with speech_lock:

            engine.stop()

            engine.say(text)
            engine.runAndWait()

    except Exception as e:
        print(f"TTS Error: {e}")