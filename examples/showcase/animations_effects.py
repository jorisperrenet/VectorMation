from vectormation.objects import *

# Layout
COLS = 6
COL_W = 1920 // COLS
ROW_H = 160
TITLE_Y = 50
FIRST_ROW = 130
ROW_DUR = 3.5
ANIM_DUR = 1.0
STAGGER = 0.4
FADE_IN_BEFORE = 0.8
COLORS = ['#58C4DD', '#83C167', '#FC6255', '#F0AC5F', '#9A72AC', '#5CD0B3']
N_ROWS = 8

canvas_h = FIRST_ROW + N_ROWS * ROW_H + 40
canvas = VectorMathAnim(width=1920, height=canvas_h)
canvas.set_background()


def col_x(c):
    return COL_W // 2 + c * COL_W


def lbl_y(r):
    return FIRST_ROW + r * ROW_H - 10


def obj_y(r):
    return FIRST_ROW + r * ROW_H + 55


def row_t(r):
    return 0.5 + r * ROW_DUR


def color(c, r):
    return COLORS[(c + r * COLS) % len(COLORS)]


def make_lbl(name, c, r):
    a = row_t(r) + c * STAGGER
    lbl = Text(text=name, x=col_x(c), y=lbl_y(r),
               font_size=20, fill='#999', stroke_width=0, text_anchor='middle')
    lbl.fadein(a - FADE_IN_BEFORE, a)
    return lbl


def make_circle(c, r, radius=35):
    return Circle(r=radius, cx=col_x(c), cy=obj_y(r),
                  fill=color(c, r), fill_opacity=0.7)


def make_rect(c, r, w=60, h=60):
    return Rectangle(w, h, x=col_x(c) - w // 2, y=obj_y(r) - h // 2,
                     fill=color(c, r), fill_opacity=0.7)


# Title
title = Text(text='Visual Effects & Emphasis', x=960, y=TITLE_Y,
             font_size=44, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 0.5)
objs = [title]

# ── Row 0: Attention grabbers ─────────────────────────────────────────
r = 0

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('indicate', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.indicate(a, a + ANIM_DUR)
objs += [lbl, s]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('pulse', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.pulse(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('pulsate', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.pulsate(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('flash', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.flash(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 4; a = row_t(r) + c * STAGGER
lbl = make_lbl('emphasize', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.emphasize(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 5; a = row_t(r) + c * STAGGER
lbl = make_lbl('telegraph', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.telegraph(start=a, end=a + 0.8)
objs += [lbl, s]

# ── Row 1: Scale effects ─────────────────────────────────────────────
r = 1

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('pulse_scale', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.pulse_scale(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('ripple_scale', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.ripple_scale(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('flash_scale', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.flash_scale(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('emphasize_scale', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.emphasize_scale(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 4; a = row_t(r) + c * STAGGER
lbl = make_lbl('hover_scale', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.hover_scale(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 5; a = row_t(r) + c * STAGGER
lbl = make_lbl('elastic_scale', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.elastic_scale(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

# ── Row 2: Shaking / Jiggling ────────────────────────────────────────
r = 2

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('shake', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.shake(start=a, end=a + ANIM_DUR, amplitude=8)
objs += [lbl, s]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('wiggle', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.wiggle(start=a, end=a + ANIM_DUR, amplitude=12)
objs += [lbl, s]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('jiggle', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.jiggle(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('glitch', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.glitch(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 4; a = row_t(r) + c * STAGGER
lbl = make_lbl('glitch_shift', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.glitch_shift(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 5; a = row_t(r) + c * STAGGER
lbl = make_lbl('wobble', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.wobble(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

# ── Row 3: Bouncing / Spring ─────────────────────────────────────────
r = 3

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('bounce', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.bounce(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('spring', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.spring(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('rubber_band', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.rubber_band(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('elastic_bounce', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.elastic_bounce(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 4; a = row_t(r) + c * STAGGER
lbl = make_lbl('swing', c, r)
s = make_rect(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.swing(start=a, end=a + ANIM_DUR, amplitude=20)
objs += [lbl, s]

c = 5; a = row_t(r) + c * STAGGER
lbl = make_lbl('pendulum', c, r)
s = make_rect(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.pendulum(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

# ── Row 4: Wave / Undulate ────────────────────────────────────────────
r = 4

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('wave', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.wave(start=a, end=a + ANIM_DUR, amplitude=15)
objs += [lbl, s]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('wave_through', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.wave_through(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('undulate', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.undulate(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('warp', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.warp(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 4; a = row_t(r) + c * STAGGER
lbl = make_lbl('swirl', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.swirl(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 5; a = row_t(r) + c * STAGGER
lbl = make_lbl('heartbeat', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.heartbeat(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

# ── Row 5: Breathing / Blinking ───────────────────────────────────────
r = 5

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('breathe', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.breathe(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('blink', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.blink(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('blink_opacity', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.blink_opacity(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('shimmer', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.shimmer(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 4; a = row_t(r) + c * STAGGER
lbl = make_lbl('flicker', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.flicker(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 5; a = row_t(r) + c * STAGGER
lbl = make_lbl('float_anim', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.float_anim(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

# ── Row 6: Drawing effects ───────────────────────────────────────────
r = 6

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('circumscribe', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.circumscribe(start=a, end=a + ANIM_DUR, stroke='#FFFF00')
objs += [lbl, s]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('cross_out', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a)
cross = s.cross_out(start=a, end=a + ANIM_DUR)
objs += [lbl, s, cross]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('animate_dash', c, r)
s = Circle(r=35, cx=col_x(c), cy=obj_y(r), fill_opacity=0,
           stroke=color(c, r), stroke_width=3)
s.fadein(a - FADE_IN_BEFORE, a); s.animate_dash(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('show_passing_flash', c, r)
s = Circle(r=35, cx=col_x(c), cy=obj_y(r), fill_opacity=0,
           stroke=color(c, r), stroke_width=3)
s.fadein(a - FADE_IN_BEFORE, a)
flash = s.show_passing_flash(start=a, end=a + ANIM_DUR)
objs += [lbl, s, flash]

c = 4; a = row_t(r) + c * STAGGER
lbl = make_lbl('ripple', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a)
rings = s.ripple(start=a, end=a + ANIM_DUR)
objs += [lbl, s, rings]

c = 5; a = row_t(r) + c * STAGGER
lbl = make_lbl('broadcast', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a)
copies = s.broadcast(start=a, end=a + ANIM_DUR)
objs += [lbl, s]
if hasattr(copies, 'objects'):
    objs.append(copies)
elif isinstance(copies, list):
    objs += copies

# ── Row 7: Misc effects ──────────────────────────────────────────────
r = 7

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('highlight_border', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.highlight_border(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('glow', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.glow(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('pulse_outline', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.pulse_outline(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('flash_highlight', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a)
hl_rect = s.flash_highlight(start=a, end=a + ANIM_DUR)
objs += [lbl, s, hl_rect]

c = 4; a = row_t(r) + c * STAGGER
lbl = make_lbl('squish', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.squish(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 5; a = row_t(r) + c * STAGGER
lbl = make_lbl('squash_and_stretch', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.squash_and_stretch(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

canvas.add_objects(*objs)

total_dur = row_t(N_ROWS - 1) + (COLS - 1) * STAGGER + ANIM_DUR + 1.0

canvas.show(end=total_dur)
