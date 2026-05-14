import pyttsx3


def speak(text: str, lang: str = "en"):
    """Convert text to speech using the system TTS engine."""
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")

        if lang == "hi":
            for voice in voices:
                if "hindi" in voice.name.lower():
                    engine.setProperty("voice", voice.id)
                    break
            else:
                engine.setProperty("voice", voices[0].id)
        else:
            engine.setProperty("voice", voices[0].id)

        engine.setProperty("rate", 170)
        engine.setProperty("volume", 1.0)
        engine.say(text)
        engine.runAndWait()

    except Exception as e:
        print(f"TTS Error: {e}")
