"""
display_manager.py - Mimi UI for 7" DSI (800x480)
"""

import os
os.environ["SDL_VIDEODRIVER"]       = "x11"
os.environ["SDL_AUDIODRIVER"]       = "alsa"
os.environ["SDL_RENDERDRIVER"]      = "software"   # fixed: no underscore gap
os.environ["LIBGL_ALWAYS_SOFTWARE"] = "1"           # force software GL
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import math
import threading
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DISPLAY_MODE = os.getenv("DISPLAY_MODE", "pygame")
WIDTH, HEIGHT = 800, 480
FPS = 30

# Colors
BG     = (15, 15, 25)
CYAN   = (0, 255, 255)
WHITE  = (255, 255, 255)
GRAY   = (80, 80, 100)
DARK   = (35, 35, 55)
GREEN  = (70, 210, 110)
YELLOW = (255, 205, 50)
PINK   = (255, 110, 160)
RED    = (255, 70, 70)
ACCENT = (90, 170, 255)
PURPLE = (160, 100, 255)
EYE_SCALE = 5.5
EYE_W  = int(30 * EYE_SCALE * 0.7)   # ~115px
EYE_H  = int(22 * EYE_SCALE * 0.7)   # ~85px
EYE_R  = int(7  * EYE_SCALE * 0.7)   # ~27px
EYE_GAP = int(56 * EYE_SCALE * 0.6)  # ~185px 

FACE_CX = WIDTH // 2
FACE_CY = HEIGHT // 2 - 20


class DisplayManager:
    def __init__(self):
        self.state         = "sleep"
        self._lock         = threading.Lock()
        self._running      = False
        self._thread       = None
        self._mode         = DISPLAY_MODE

        # Action animation
        self._anim_action  = None    # "add_todo"|"delete_todo"|"set_timer"|"play_music"
        self._anim_start   = 0.0
        self._anim_dur     = 2.5

        # Timer
        self._timer_total  = 0
        self._timer_start  = None
        self._timer_active = False
        self._timer_label  = "Timer"

        # Task list
        self._tasks        = []
        self._show_tasks   = False
        self._tasks_time   = 0

        # Mouth
        self._mouth_open   = 0.0

        # Pygame
        self._pygame  = None
        self._screen  = None
        self._font_lg = None
        self._font_md = None
        self._font_sm = None
        self._font_xs = None
        self._clock   = None

        self._init_display()

    # ── Public API ────────────────────────────────────────────

    def set_state(self, state: str):
        valid = ["idle","listening","processing","speaking","ack","sleep"]
        with self._lock:
            if state in valid:
                self.state = state

    def notify_action(self, action_name: str):
        self._anim_action = action_name
        self._anim_start  = time.time()

    def set_timer(self, total_seconds: int, label: str = "Timer"):
        self._timer_total  = total_seconds
        self._timer_start  = datetime.now()
        self._timer_active = True
        self._timer_label  = label

    def clear_timer(self):
        self._timer_active = False

    def set_tasks(self, tasks: list):
        self._tasks = [t["task_name"] if isinstance(t, dict) else t for t in tasks]

    def show_tasks(self):
        self._show_tasks = True
        self._tasks_time = time.time()

    def hide_tasks(self):
        self._show_tasks = False

    # ── Init ──────────────────────────────────────────────────

    def _init_display(self):
        if self._mode == "pygame":
            self._init_pygame()
        elif self._mode == "oled":
            self._init_oled()
        else:
            print("[Display] Headless mode.")
            self._mode = "headless"

    def _init_pygame(self):
        try:
            import pygame
            self._pygame = pygame
            # Init only display + font — mixer owned by TTSService
            pygame.display.init()
            pygame.font.init()
            # SWSURFACE = pure-software surface, no GL/hardware needed
            self._screen = pygame.display.set_mode(
                (WIDTH, HEIGHT),
                pygame.SWSURFACE | pygame.NOFRAME
            )
            pygame.display.set_caption("Mimi AI Robot")
            self._clock   = pygame.time.Clock()
            self._font_lg = pygame.font.SysFont("freesans", 96, bold=True)
            self._font_md = pygame.font.SysFont("freesans", 48, bold=True)
            self._font_sm = pygame.font.SysFont("freesans", 28)
            self._font_xs = pygame.font.SysFont("freesans", 18)
            # draw initial black frame so window isn't blank
            self._screen.fill(BG)
            pygame.display.flip()
            print("[Display] Pygame 800x480 ready (software render)")
        except Exception as e:
            import traceback; traceback.print_exc()
            print(f"[Display] Pygame failed: {e}")
            self._mode = "headless"

    def _init_oled(self):
        try:
            from luma.core.interface.serial import i2c
            from luma.oled.device import ssd1306
            self._oled = ssd1306(i2c(port=1, address=0x3C))
            print("[Display] OLED ready")
        except Exception as e:
            print(f"[Display] OLED failed: {e}")
            self._mode = "headless"

    # ── Loop ──────────────────────────────────────────────────

    def start(self):
        """
        Spin up a dedicated render thread.
        The pygame window is created AND drawn inside that same thread
        so that X11/SDL keeps the GL context on one thread only.
        """
        self._running = True
        self._thread  = threading.Thread(target=self._thread_main, daemon=True)
        self._thread.start()
        # Let the thread finish its init before callers use set_state
        time.sleep(0.4)
        print("[Display] Animation loop started.")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)

    def _thread_main(self):
        """Owns the pygame window from creation to destruction."""
        if self._mode == "pygame":
            try:
                pg = self._pygame
                # Tear down the window made in __init__ (wrong thread)
                # and recreate it here so the X11 context is thread-local.
                pg.display.quit()
                pg.display.init()
                self._screen = pg.display.set_mode(
                    (WIDTH, HEIGHT),
                    pg.SWSURFACE | pg.NOFRAME
                )
                pg.display.set_caption("Mimi AI Robot")
                self._screen.fill(BG)
                pg.display.flip()
            except Exception as e:
                print(f"[Display] Thread re-init failed: {e}")
                self._mode = "headless"

        self._loop()

        if self._mode == "pygame" and self._pygame:
            self._pygame.display.quit()

    def _loop(self):
        t0 = time.time()
        while self._running:
            t = (time.time() - t0) % 1.0
            with self._lock:
                state = self.state
            if self._mode == "pygame":
                self._render(state, t)
            elif self._mode == "oled":
                self._render_oled(state, t)
            if self._clock:
                self._clock.tick(FPS)
            else:
                time.sleep(1.0 / FPS)

    # ── Main render ───────────────────────────────────────────

    def _render(self, state: str, t: float):
        pg = self._pygame
        sc = self._screen
        try:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self._running = False
                    return

            sc.fill(BG)

            # Smooth mouth
            target = (0.5 + 0.5 * math.sin(2 * math.pi * 5 * t)) if state == "speaking" else 0.0
            self._mouth_open += (target - self._mouth_open) * 0.35

            # Check task list timeout
            if self._show_tasks and time.time() - self._tasks_time > 4.0:
                self._show_tasks = False

            # Check action anim timeout
            anim_active = self._anim_action and (time.time() - self._anim_start < self._anim_dur)

            # ── select ──
            if anim_active:
                # fullscreen action animation
                self._draw_action_fullscreen(sc, t)
            elif self._show_tasks:
                # fullscreen task list
                self._draw_tasks_fullscreen(sc)
            else:
                # normal
                self._draw_face(sc, state, t)
                self._draw_status(sc, state)
                # timer countdown
                if self._timer_active:
                    self._draw_timer_small(sc)

            # Clock
            self._draw_clock_mini(sc)

            pg.display.flip()
        except Exception as e:
            err = str(e)
            # Suppress noisy GL/BadAccess errors — software render doesn't need GL
            if "GL" not in err and "BadAccess" not in err:
                print(f"[Display] Render error: {e}")

    # ── Clock mini  ─────────────────────

    def _draw_clock_mini(self, sc):
        now  = datetime.now()
        surf = self._font_xs.render(now.strftime("%H:%M"), True, GRAY)
        sc.blit(surf, (12, 10))

    # ── Face ───────────────────────────────────────

    def _draw_face(self, sc, state: str, t: float):
        pg = self._pygame

        cx_l = FACE_CX - EYE_GAP // 2
        cx_r = FACE_CX + EYE_GAP // 2
        cy   = FACE_CY

        blink, squeeze, bounce, xshift = False, 1.0, 0, 0
        color = CYAN

        if state == "sleep":
            squeeze = 0.09 + 0.03 * math.sin(2 * math.pi * t)
            color   = GRAY

        elif state == "idle":
            bounce = int(2.5 * math.sin(2 * math.pi * t))
            blink  = 0.82 < t < 0.89
            color  = CYAN

        elif state == "listening":
            nod    = 3.0 * max(0, math.sin(6 * math.pi * t))
            bounce = int(nod)
            blink  = 0.18 < t < 0.22
            color  = ACCENT

        elif state == "processing":
            xshift  = int(4 * math.sin(9 * math.pi * t))
            squeeze = 0.55 + 0.1 * math.sin(4 * math.pi * t)
            color   = YELLOW

        elif state == "speaking":
            talk    = (math.sin(2 * math.pi * 5 * t) + 1) / 2
            squeeze = 0.55 + 0.45 * talk
            bounce  = int(1.5 * math.sin(2 * math.pi * t))
            blink   = 0.07 < t < 0.11
            color   = CYAN

        elif state == "ack":
            self._draw_happy_eyes(sc, cx_l, cx_r, cy, CYAN)
            self._draw_cheeks(sc, cx_l, cx_r, cy)
            self._draw_mouth(sc, cy, state)
            return

        h = max(6, int(EYE_H * squeeze))
        if blink:
            h = int(EYE_H * 0.08)

        for cx in [cx_l + xshift, cx_r + xshift]:
            self._rrect(sc, cx - EYE_W//2, cy - h//2 - bounce, EYE_W, h, EYE_R, color)

        if state in ["idle", "speaking"]:
            self._draw_cheeks(sc, cx_l + xshift, cx_r + xshift, cy - bounce)

        self._draw_mouth(sc, cy - bounce, state)

    def _rrect(self, sc, x, y, w, h, r, color):
        pg = self._pygame
        r  = max(0, min(r, w//2, h//2))
        pg.draw.rect(sc, color, (x+r, y, w-2*r, h))
        pg.draw.rect(sc, color, (x, y+r, w, h-2*r))
        for cx, cy in [(x+r,y+r),(x+w-r,y+r),(x+r,y+h-r),(x+w-r,y+h-r)]:
            pg.draw.circle(sc, color, (cx, cy), r)

    def _draw_happy_eyes(self, sc, cx_l, cx_r, cy, color):
        pg = self._pygame
        hw = int(EYE_W * 0.6)
        pk = int(EYE_H * 0.5)
        for cx in [cx_l, cx_r]:
            pts = [(cx - hw, cy + pk//2), (cx, cy - pk), (cx + hw, cy + pk//2)]
            pg.draw.lines(sc, color, False, pts, 9)

    def _draw_cheeks(self, sc, cx_l, cx_r, cy):
        pg   = self._pygame
        surf = pg.Surface((int(EYE_W*0.5), int(EYE_H*0.3)), pg.SRCALPHA)
        surf.fill((255, 110, 160, 50))
        off_x = int(EYE_W * 0.1)
        off_y = int(EYE_H * 0.7)
        sc.blit(surf, (cx_l - int(EYE_W*0.1), cy + off_y))
        sc.blit(surf, (cx_r - int(EYE_W*0.4), cy + off_y))

    def _draw_mouth(self, sc, eye_cy, state):
        pg = self._pygame
        mx = FACE_CX
        my = eye_cy + EYE_H // 2 + int(EYE_H * 0.5)
        mo = self._mouth_open
        mw = int(EYE_W * 0.35)  # ความกว้างปาก

        if state == "sleep":
            pg.draw.line(sc, GRAY, (mx - mw//2, my), (mx + mw//2, my), 3)

        elif state == "ack":
            pts = [
                (mx - mw, my - int(mw*0.2)),
                (mx - mw//2, my + int(mw*0.3)),
                (mx, my + int(mw*0.4)),
                (mx + mw//2, my + int(mw*0.3)),
                (mx + mw, my - int(mw*0.2))
            ]
            pg.draw.lines(sc, CYAN, False, pts, 6)

        elif state == "speaking":
            ow = int(mw * (0.6 + 0.4 * mo))
            oh = int(mw * (0.08 + 0.55 * mo))
            if oh > 8:
                pg.draw.ellipse(sc, WHITE, (mx-ow, my-oh//2, ow*2, oh))
                pg.draw.ellipse(sc, CYAN,  (mx-ow, my-oh//2, ow*2, oh), 3)
            else:
                pg.draw.line(sc, CYAN, (mx-ow, my), (mx+ow, my), 3)

        elif state == "listening":
            pg.draw.ellipse(sc, GRAY, (mx - mw//3, my-5, mw//1.5, 12))

        else:
            pg.draw.line(sc, GRAY, (mx - mw//2, my), (mx + mw//2, my), 3)

    # ── Status bar ─────────────────────────────────

    def _draw_status(self, sc, state: str):
        labels = {
            "idle":       ("Ready", GRAY),
            "listening":  ("Listening...", ACCENT),
            "processing": ("Thinking...", YELLOW),
            "speaking":   ("Speaking...", CYAN),
            "ack":        ("Got it!", GREEN),
            "sleep":      ("Say  Hey Mimi  to wake me", GRAY),
        }
        text, color = labels.get(state, ("...", GRAY))
        surf = self._font_xs.render(text, True, color)
        rect = surf.get_rect(centerx=FACE_CX, bottom=HEIGHT - 18)
        sc.blit(surf, rect)

    # ── Timer countdown ───────────

    def _draw_timer_small(self, sc):
        if not self._timer_start:
            return
        elapsed   = (datetime.now() - self._timer_start).total_seconds()
        remaining = max(0, self._timer_total - elapsed)
        if remaining <= 0:
            self._timer_active = False
            return

        pg   = self._pygame
        mins = int(remaining) // 60
        secs = int(remaining) % 60
        pct  = remaining / self._timer_total if self._timer_total > 0 else 0

        color = RED if remaining < 30 else YELLOW if remaining < 60 else WHITE
        time_s = self._font_sm.render(f"⏱  {mins:02d}:{secs:02d}", True, color)
        sc.blit(time_s, (WIDTH - time_s.get_width() - 16, HEIGHT - 44))

        # progress bar
        bw = 180
        bx = WIDTH - bw - 16
        by = HEIGHT - 16
        pg.draw.rect(sc, DARK, (bx, by, bw, 6), border_radius=3)
        fw = int(bw * pct)
        if fw > 0:
            bc = RED if pct < 0.2 else YELLOW if pct < 0.4 else GREEN
            pg.draw.rect(sc, bc, (bx, by, fw, 6), border_radius=3)

    # ── Fullscreen Task List ───────────────────────────────────

    def _draw_tasks_fullscreen(self, sc):
        pg = self._pygame

        title = self._font_md.render("To-Do List", True, CYAN)
        sc.blit(title, (title.get_rect(centerx=FACE_CX).x, 60))

        pg.draw.line(sc, GRAY, (80, 120), (WIDTH-80, 120), 1)

        if not self._tasks:
            empty = self._font_sm.render("All clear!  ✓", True, GREEN)
            sc.blit(empty, (empty.get_rect(centerx=FACE_CX).x, 200))
            return

        for i, task in enumerate(self._tasks[:6]):
            ty   = 140 + i * 48
            pg.draw.circle(sc, CYAN, (100, ty + 16), 8, 2)
            text = task if len(task) < 42 else task[:40] + "…"
            ts   = self._font_sm.render(text, True, WHITE)
            sc.blit(ts, (122, ty))

        if len(self._tasks) > 6:
            more = self._font_xs.render(f"+ {len(self._tasks)-6} more tasks", True, GRAY)
            sc.blit(more, (more.get_rect(centerx=FACE_CX).x, HEIGHT - 50))

    # ── Fullscreen Action Animations ──────────────────────────

    def _draw_action_fullscreen(self, sc, t: float):
        age  = time.time() - self._anim_start
        prog = min(1.0, age / self._anim_dur)
        alpha = int(255 * max(0, 1 - prog * 1.3))

        if self._anim_action == "add_todo":
            self._anim_write(sc, prog, alpha)
        elif self._anim_action == "delete_todo":
            self._anim_trash(sc, prog, alpha)
        elif self._anim_action == "set_timer":
            self._anim_clock(sc, prog, alpha)
        elif self._anim_action == "play_music":
            self._anim_cd(sc, prog, alpha, t)

        if age > self._anim_dur:
            self._anim_action = None

    def _anim_write(self, sc, prog, alpha):
        pg = self._pygame
        cx, cy = FACE_CX, FACE_CY

        # paper
        pw, ph = 280, 320
        px, py = cx - pw//2, cy - ph//2
        surf = pg.Surface((pw, ph), pg.SRCALPHA)
        pg.draw.rect(surf, (240, 235, 210, min(220, alpha)), (0, 0, pw, ph), border_radius=8)
        # line
        for i in range(7):
            if i / 7 > prog:
                break
            ly  = 40 + i * 36
            end = int(24 + (pw-48) * min(1.0, (prog - i/7) * 7))
            pg.draw.line(surf, (100, 100, 100, alpha), (24, ly), (end, ly), 3)
        # pencil
        lp = prog * 7
        cl = min(int(lp), 6)
        px2 = int(24 + (pw-48) * min(1.0, lp - cl))
        py2 = 40 + cl * 36
        pg.draw.line(surf, (255, 200, 50, alpha), (px2, py2), (px2+18, py2-26), 7)
        pg.draw.polygon(surf, (180, 90, 40, alpha),
                        [(px2, py2),(px2+4, py2-6),(px2+7, py2-3)])
        sc.blit(surf, (cx - pw//2, cy - ph//2))

        # label 
        lbl = self._font_sm.render("Adding task...", True, (*GREEN, alpha) if alpha < 256 else GREEN)
        sc.blit(lbl, (lbl.get_rect(centerx=cx).x, cy + ph//2 + 20))

    def _anim_trash(self, sc, prog, alpha):
        """bin — fullscreen"""
        pg = self._pygame
        cx, cy = FACE_CX, FACE_CY + 40

        # bin
        tw, th = 160, 140
        tx, ty = cx - tw//2, cy - th//2 + 40

        pg.draw.rect(sc, (150, 50, 50), (tx, ty, tw, th), border_radius=10)
        pg.draw.rect(sc, (200, 80, 80), (tx-10, ty-20, tw+20, 22), border_radius=6)
        pg.draw.line(sc, (200, 80, 80), (cx-30, ty-40), (cx-30, ty-20), 6)
        pg.draw.line(sc, (200, 80, 80), (cx+30, ty-40), (cx+30, ty-20), 6)
        pg.draw.line(sc, (200, 80, 80), (cx-30, ty-40), (cx+30, ty-40), 6)
        for i in range(3):
            lx = tx + 30 + i * 40
            pg.draw.line(sc, (180, 60, 60), (lx, ty+20), (lx, ty+th-20), 3)

        fy  = int((cy - 200) + 240 * min(1.0, prog * 2))
        rot = prog * 45
        op2 = max(0, int(255 * (1 - prog * 1.5)))
        if op2 > 0:
            paper = pg.Surface((80, 60), pg.SRCALPHA)
            pg.draw.rect(paper, (240, 235, 210, op2), (0, 0, 80, 60), border_radius=5)
            sc.blit(paper, (cx - 40, fy))

        lbl = self._font_sm.render("Removing task...", True, RED)
        sc.blit(lbl, (lbl.get_rect(centerx=cx).x, cy - 200))

    def _anim_clock(self, sc, prog, alpha):
        pg = self._pygame
        cx, cy = FACE_CX, FACE_CY
        r = 160

        # background
        pg.draw.circle(sc, DARK, (cx, cy), r)
        pg.draw.circle(sc, YELLOW, (cx, cy), r, 5)

        for i in range(12):
            a   = math.pi * 2 * i / 12 - math.pi/2
            x1  = int(cx + (r-10) * math.cos(a))
            y1  = int(cy + (r-10) * math.sin(a))
            x2  = int(cx + (r-22 if i % 3 == 0 else r-16) * math.cos(a))
            y2  = int(cy + (r-22 if i % 3 == 0 else r-16) * math.sin(a))
            pg.draw.line(sc, YELLOW, (x1, y1), (x2, y2), 4 if i % 3 == 0 else 2)

        # prog
        angle = -math.pi/2 + 2*math.pi * prog
        ex = int(cx + (r-30) * math.cos(angle))
        ey = int(cy + (r-30) * math.sin(angle))
        pg.draw.line(sc, YELLOW, (cx, cy), (ex, ey), 6)
        pg.draw.circle(sc, YELLOW, (cx, cy), 10)

        lbl = self._font_sm.render("Timer starting...", True, YELLOW)
        sc.blit(lbl, (lbl.get_rect(centerx=cx).x, cy + r + 24))

    def _anim_cd(self, sc, prog, alpha, t):
        """CD  — fullscreen"""
        pg    = self._pygame
        cx, cy = FACE_CX, FACE_CY
        r     = 150
        angle = prog * math.pi * 8

        # CD
        pg.draw.circle(sc, (55, 55, 80), (cx, cy), r)
        # simulate CD shine
        colors = [CYAN, PURPLE, ACCENT, (200, 255, 200), YELLOW]
        for i, c in enumerate(colors):
            ri = r - 10 - i * 22
            if ri > 20:
                pg.draw.circle(sc, c, (cx, cy), ri, 2)

        # CD
        pg.draw.circle(sc, BG, (cx, cy), 22)
        pg.draw.circle(sc, GRAY, (cx, cy), 22, 2)

        for i in range(6):
            a  = angle + i * math.pi / 3
            rx = int(cx + 80 * math.cos(a))
            ry = int(cy + 80 * math.sin(a))
            pg.draw.circle(sc, (255, 255, 255), (rx, ry), 6)

        notes = ["♪", "♫", "♪"]
        for i, note in enumerate(notes):
            na  = angle * 0.4 + i * 2.1
            nr  = r + 35
            nx  = int(cx + nr * math.cos(na))
            ny  = int(cy + nr * math.sin(na))
            ns  = self._font_md.render(note, True, CYAN)
            sc.blit(ns, (nx - ns.get_width()//2, ny - ns.get_height()//2))

        lbl = self._font_sm.render("Playing music!", True, CYAN)
        sc.blit(lbl, (lbl.get_rect(centerx=cx).x, cy + r + 30))

    # ── OLED fallback ─────────────────────────────────────────

    def _render_oled(self, state, t):
        try:
            from PIL import Image, ImageDraw
            img  = Image.new("1", (128, 64), 0)
            draw = ImageDraw.Draw(img)
            cy   = 28
            if state == "sleep":
                draw.rectangle([14, cy+8, 54, cy+12], fill=1)
                draw.rectangle([74, cy+8, 114, cy+12], fill=1)
            else:
                draw.rectangle([14, cy-14, 54, cy+14], fill=1)
                draw.rectangle([74, cy-14, 114, cy+14], fill=1)
            self._oled.display(img)
        except Exception as e:
            print(f"[Display] OLED error: {e}")