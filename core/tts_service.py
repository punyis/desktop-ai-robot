"""
tts_service.py - Text-to-Speech for Mimi
Uses Edge TTS (Microsoft)
"""

import os
import asyncio
import threading
import tempfile
from dotenv import load_dotenv

load_dotenv()

VOICE = os.getenv("TTS_VOICE", "en-US-AriaNeural")


class TTSService:
    def __init__(self):
        self._lock = threading.Lock()
        import pygame
        self._pygame = pygame
        pygame.mixer.init()
        print(f"[TTS] Using Edge TTS - voice: {VOICE}")

    def speak(self, text: str, blocking: bool = True):
        print(f"[Mimi] {text}")
        if blocking:
            self._speak_now(text)
        else:
            t = threading.Thread(target=self._speak_now, args=(text,), daemon=True)
            t.start()

    def _speak_now(self, text: str):
        with self._lock:
            asyncio.run(self._speak_async(text))

    def play_beep(self):
        try:
            import numpy as np
            import pygame
            sample_rate = 44100

            def make_tone(freq, duration, volume=0.8):
                t = np.linspace(0, duration, int(sample_rate * duration))
                wave = np.sin(2 * np.pi * freq * t)
                # fade out 
                fade = np.linspace(1, 0, len(wave))
                wave = (wave * fade * volume * 32767).astype(np.int16)
                return np.column_stack([wave, wave])

            # ting-tong
            ding = make_tone(880, 0.18)   # hight note
            dong = make_tone(660, 0.28)   # low note
            silence = np.zeros((int(sample_rate * 0.08), 2), dtype=np.int16)

            combined = np.concatenate([ding, silence, dong])
            sound = pygame.sndarray.make_sound(combined)
            sound.play()
            pygame.time.wait(int((0.18 + 0.08 + 0.28) * 1000) + 100)

        except Exception as e:
            print(f"[TTS] Beep error: {e}")

    async def _speak_async(self, text: str):
        import edge_tts
        import soundfile as sf
        import numpy as np
        import pygame

        try:
            communicate = edge_tts.Communicate(text, VOICE, rate="-25%")
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                tmp_path = f.name
            await communicate.save(tmp_path)

            data, sample_rate = sf.read(tmp_path)
            octaves = 8 / 12
            new_rate = int(sample_rate * (2.0 ** octaves))
            pitched_path = tmp_path.replace(".wav", "_pitched.wav")
            sf.write(pitched_path, data, new_rate)

            pygame.mixer.music.load(pitched_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.05)

            pygame.mixer.music.unload()
            for p in [tmp_path, pitched_path]:
                try:
                    os.unlink(p)
                except Exception:
                    pass

        except Exception as e:
            print(f"[TTS] Error: {e}")
