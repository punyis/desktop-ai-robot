"""
stt_service.py - Speech-to-Text for Mimi
Keeps mic open persistently to avoid PyAudio buffer overflow.
"""

import os
import speech_recognition as sr
from dotenv import load_dotenv

load_dotenv()

STT_LANGUAGE = os.getenv("STT_LANGUAGE", "en-US")


class STTService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 1.0
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.language = STT_LANGUAGE
        self._mic_index = self._find_usb_mic()
        self._mic = sr.Microphone(device_index=self._mic_index, sample_rate=44100)
        self._source = None
        print(f"[STT] Ready. Language: {self.language}, mic index: {self._mic_index}")

    def _find_usb_mic(self):
        for i, name in enumerate(sr.Microphone.list_microphone_names()):
            if "usb" in name.lower() or "pnp" in name.lower():
                print(f"[STT] Found USB mic at SR index {i}: {name}")
                return i
        print("[STT] USB mic not found, using default")
        return None

    def calibrate(self, duration: int = 1):
        """open mic one time"""
        print("[STT] Calibrating microphone...")
        try:
            self._source = self._mic.__enter__()
            self.recognizer.adjust_for_ambient_noise(self._source, duration=duration)
            print(f"[STT] Calibrated. Energy threshold: {self.recognizer.energy_threshold:.0f}")
        except Exception as e:
            print(f"[STT] Calibration warning: {e}")
            self._source = None

    def flush(self):
        pass 

    def listen_once(self, timeout: int = 5, phrase_limit: int = 10):
        if self._source is None:
            return self._listen_fresh(timeout, phrase_limit)
        try:
            print("[STT] Listening...")
            audio = self.recognizer.listen(
                self._source,
                timeout=timeout,
                phrase_time_limit=phrase_limit
            )
            print("[STT] Processing...")
            text = self.recognizer.recognize_google(audio, language=self.language)
            print(f"[STT] Heard: {text}")
            return text
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            print("[STT] Could not understand audio.")
            return None
        except sr.RequestError as e:
            print(f"[STT] Google API error: {e}")
            return None
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"[STT] Error: {e} — reopening mic")
            self._reopen_mic()
            return None

    def _reopen_mic(self):
        try:
            self._mic.__exit__(None, None, None)
        except Exception:
            pass
        try:
            self._source = self._mic.__enter__()
            self.recognizer.adjust_for_ambient_noise(self._source, duration=0.5)
            print("[STT] Mic reopened.")
        except Exception as e:
            print(f"[STT] Reopen failed: {e}")
            self._source = None

    def _listen_fresh(self, timeout, phrase_limit):
        try:
            with sr.Microphone(device_index=self._mic_index, sample_rate=44100) as source:
                print("[STT] Listening (fresh)...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
            text = self.recognizer.recognize_google(audio, language=self.language)
            print(f"[STT] Heard: {text}")
            return text
        except Exception:
            return None

    def stop(self):
        try:
            if self._source:
                self._mic.__exit__(None, None, None)
        except Exception:
            pass