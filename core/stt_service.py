"""
stt_service.py - Speech-to-Text for Mimi
Uses Google Speech Recognition (online) with offline fallback.
"""

import os
import speech_recognition as sr
from dotenv import load_dotenv

load_dotenv()

STT_LANGUAGE = os.getenv("STT_LANGUAGE", "en-US")


class STTService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 1.0   # Wait 1s after speech stops
        self.recognizer.energy_threshold = 300  # Mic sensitivity
        self.recognizer.dynamic_energy_threshold = True
        self.language = STT_LANGUAGE
        print(f"[STT] Ready. Language: {self.language}")

    def calibrate(self, duration: int = 1):
        """Calibrate mic for ambient noise. Call once at startup."""
        print("[STT] Calibrating microphone...")
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=duration)
            print(f"[STT] Calibrated. Energy threshold: {self.recognizer.energy_threshold:.0f}")
        except Exception as e:
            print(f"[STT] Calibration warning: {e}")

    def listen_once(self, timeout: int = 5, phrase_limit: int = 10) -> str | None:
        """
        Listen for one utterance.
        Returns: text string, or None if nothing heard / error.
        """
        try:
            with sr.Microphone() as source:
                print("[STT] Listening...")
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_limit
                )

            print("[STT] Processing...")
            text = self.recognizer.recognize_google(audio, language=self.language)
            print(f"[STT] Heard: {text}")
            return text

        except sr.WaitTimeoutError:
            return None  # Silence — not an error

        except sr.UnknownValueError:
            print("[STT] Could not understand audio.")
            return None

        except sr.RequestError as e:
            print(f"[STT] Google API error: {e}")
            return None

        except Exception as e:
            print(f"[STT] Unexpected error: {e}")
            return None
