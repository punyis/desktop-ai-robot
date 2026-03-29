"""
display_manager.py - Mimi's face animations
States: idle | listening | processing | speaking | ack | sleep
"""

import os
import math
import threading
import time
import numpy as np
from dotenv import load_dotenv

load_dotenv()

DISPLAY_MODE = os.getenv("DISPLAY_MODE", "pygame")
WIDTH, HEIGHT = 128, 64
CYAN  = np.array([0, 255, 255], dtype=np.uint8)
BLACK = np.array([0, 0, 0],   dtype=np.uint8)
WHITE = np.array([255, 255, 255], dtype=np.uint8)
FPS   = 30


def new_screen():
    return np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)

def set_pixel(s, x, y, c=None):
    c = c if c is not None else CYAN
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        s[y, x] = c

def draw_filled_rect(s, x, y, w, h, c=None):
    c = c if c is not None else CYAN
    x0, y0 = max(0, x),   max(0, y)
    x1, y1 = min(WIDTH, x+w), min(HEIGHT, y+h)
    if x0 < x1 and y0 < y1:
        s[y0:y1, x0:x1] = c

def draw_filled_circle(s, cx, cy, r, c=None):
    c = c if c is not None else CYAN
    for yy in range(cy-r, cy+r+1):
        for xx in range(cx-r, cx+r+1):
            if (xx-cx)**2 + (yy-cy)**2 <= r*r:
                set_pixel(s, xx, yy, c)

def draw_rounded_rect(s, x, y, w, h, r=4, c=None):
    c = c if c is not None else CYAN
    r = max(0, min(r, w//2, h//2))
    draw_filled_rect(s, x+r, y, w-2*r, h, c)
    draw_filled_rect(s, x, y+r, r, h-2*r, c)
    draw_filled_rect(s, x+w-r, y+r, r, h-2*r, c)
    draw_filled_circle(s, x+r,     y+r,     r, c)
    draw_filled_circle(s, x+w-r-1, y+r,     r, c)
    draw_filled_circle(s, x+r,     y+h-r-1, r, c)
    draw_filled_circle(s, x+w-r-1, y+h-r-1, r, c)

def draw_eye(s, cx, cy, w=30, h=22, r=7, c=None):
    draw_rounded_rect(s, cx-w//2, cy-h//2, w, h, r, c)

def draw_eyes(s, cy, w=30, h=22, r=7, gap=56, xshift=0, c=None):
    draw_eye(s, WIDTH//2 - gap//2 + xshift, cy, w, h, r, c)
    draw_eye(s, WIDTH//2 + gap//2 + xshift, cy, w, h, r, c)

def draw_thick_line(s, x1, y1, x2, y2, c=None, t=3):
    c = c if c is not None else CYAN
    dx, dy = x2-x1, y2-y1
    L = max(abs(dx), abs(dy))
    if L == 0:
        return
    rr = t//2
    for i in range(L+1):
        p = i/L
        x = int(round(x1 + p*dx))
        y = int(round(y1 + p*dy))
        for yy in range(y-rr, y+rr+1):
            for xx in range(x-rr, x+rr+1):
                set_pixel(s, xx, yy, c)

def draw_happy_eyes(s, cy, gap=52, w=26, peak=10, t=3):
    for cx in [WIDTH//2 - gap//2, WIDTH//2 + gap//2]:
        draw_thick_line(s, cx-w//2, cy, cx, cy-peak, t=t)
        draw_thick_line(s, cx, cy-peak, cx+w//2, cy, t=t)


def frame_idle(t):
    s  = new_screen()
    cy = 30 - int(round(2 * math.sin(2 * math.pi * t)))
    blink = t > 0.82 or 0.35 < t < 0.40
    draw_eyes(s, cy, h=6 if blink else 26, r=3 if blink else 7, gap=56)
    return s

def frame_listening(t):
    s = new_screen()
    def pulse(center, width, amp):
        d = abs(t - center)
        return amp * ((1-(d/width))**2) if d <= width else 0
    nod = pulse(0.22,0.06,2.2) + pulse(0.52,0.07,2.0) + pulse(0.82,0.06,1.6)
    breathe = 0.5 * math.sin(2 * math.pi * t)
    cy = 30 - int(round(nod + breathe))
    blink = 0.18 < t < 0.20 or 0.68 < t < 0.70
    h = 6 if blink else (20 if nod > 1.5 else 24)
    draw_eyes(s, cy, w=30, h=h, r=3 if blink else 8, gap=52)
    return s

def frame_processing(t):
    s = new_screen()
    xshift = int(round(2 * math.sin(6 * math.pi * t)))
    blink  = 0.92 < t < 0.95
    draw_eyes(s, 30, w=30, h=6 if blink else 14, r=3 if blink else 6, gap=54, xshift=xshift)
    return s

def frame_speaking(t):
    s    = new_screen()
    talk = (math.sin(2 * math.pi * 4 * t) + 1) / 2
    bounce = int(round(math.sin(2 * math.pi * t)))
    cy   = 30 - bounce - int(round(1.2 * (talk > 0.72)))
    blink = 0.08 < t < 0.10
    h = 10 if blink else int(round(14 + (24-14)*talk))
    draw_eyes(s, cy, w=30, h=h, r=4 if blink else 7, gap=52)
    return s

def frame_ack(t):
    s = new_screen()
    cy = 30 - int(round(math.sin(2 * math.pi * t)))
    draw_happy_eyes(s, cy)
    return s

def frame_sleep(t):
    s = new_screen()
    breathe = int(round(math.sin(2 * math.pi * t)))
    cy = 30 + breathe
    twitch = 0.72 < t < 0.76
    draw_eyes(s, cy, w=28 if twitch else 30, h=10 if twitch else 4, r=5 if twitch else 2, gap=56)
    return s

FRAMES = {
    "idle":       frame_idle,
    "listening":  frame_listening,
    "processing": frame_processing,
    "speaking":   frame_speaking,
    "ack":        frame_ack,
    "sleep":      frame_sleep,
}


class DisplayManager:
    def __init__(self):
        self.state    = "idle"
        self._lock    = threading.Lock()
        self._running = False
        self._thread  = None
        self._mode    = DISPLAY_MODE
        self._pygame  = None
        self._screen  = None
        self._oled    = None
        self._init_display()

    def _init_display(self):
        if self._mode == "pygame":
            self._init_pygame()
        elif self._mode == "oled":
            self._init_oled()
        elif self._mode == "headless":
            print("[Display] Running headless.")
        else:
            print(f"[Display] Unknown mode '{self._mode}', running headless.")
            self._mode = "headless"

    def _init_pygame(self):
        try:
            import pygame
            self._pygame = pygame
            pygame.display.init()
            pygame.mixer.init()
            self._screen = pygame.display.set_mode((WIDTH*4, HEIGHT*4))
            pygame.display.set_caption("Mimi AI Robot")
            print("[Display] Pygame window ready")
        except Exception as e:
            print(f"[Display] Pygame init failed: {e}. Running headless.")
            self._mode = "headless"

    def _init_oled(self):
        try:
            from luma.core.interface.serial import i2c
            from luma.oled.device import ssd1306
            serial = i2c(port=1, address=0x3C)
            self._oled = ssd1306(serial)
            print("[Display] OLED (SSD1306) ready")
        except Exception as e:
            print(f"[Display] OLED init failed: {e}. Running headless.")
            self._mode = "headless"

    def set_state(self, state: str):
        with self._lock:
            if state in FRAMES:
                self.state = state

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        print("[Display] Animation loop started.")

    def stop(self):
        self._running = False

    def _loop(self):
        t_start = time.time()
        while self._running:
            t = (time.time() - t_start) % 1.0
            with self._lock:
                state = self.state
            frame = FRAMES[state](t)

            if self._mode == "pygame":
                self._render_pygame(frame)
            elif self._mode == "oled":
                self._render_oled(frame)

            time.sleep(1.0 / FPS)

    def _render_pygame(self, frame: np.ndarray):
        try:
            pygame = self._pygame
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._running = False
                    return
            surface = pygame.surfarray.make_surface(
                np.transpose(frame, (1, 0, 2))
            )
            scaled = pygame.transform.scale(surface, (WIDTH*4, HEIGHT*4))
            self._screen.blit(scaled, (0, 0))
            pygame.display.flip()
        except Exception as e:
            print(f"[Display] Render error: {e}")

    def _render_oled(self, frame: np.ndarray):
        try:
            from PIL import Image
            gray = np.mean(frame, axis=2).astype(np.uint8)
            img  = Image.fromarray(gray, mode="L").convert("1")
            self._oled.display(img)
        except Exception as e:
            print(f"[Display] OLED render error: {e}")
