import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

# Layout
COLS = 6
COL_W = 1920 // COLS
ROW_H = 170
TITLE_Y = 50
FIRST_ROW = 130
ROW_DUR = 3.5
ANIM_DUR = 1.0
STAGGER = 0.4
FADE_IN_BEFORE = 0.8
COLORS = ['#58C4DD', '#83C167', '#FC6255', '#F0AC5F', '#9A72AC', '#5CD0B3']
N_ROWS = 5

canvas_h = FIRST_ROW + N_ROWS * ROW_H + 40
canvas = VectorMathAnim(width=1920, height=canvas_h, verbose=args.verbose,
                        save_dir='svgs/animations_color')
canvas.set_background()


def col_x(c):
    return COL_W // 2 + c * COL_W


def lbl_y(r):
    return FIRST_ROW + r * ROW_H - 10


def obj_y(r):
    return FIRST_ROW + r * ROW_H + 60


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


# Title
title = Text(text='Color & Style Animations', x=960, y=TITLE_Y,
             font_size=44, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 0.5)
objs = [title]

# ── Row 0: Color transitions ─────────────────────────────────────────
r = 0

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('set_color', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.set_color(start=a, end=a + ANIM_DUR, fill='#FC6255')
objs += [lbl, s]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('fade_color', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.fade_color('#FFFF00', start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('fade_to_color', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.fade_to_color('#9A72AC', start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('color_shift', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.color_shift(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 4; a = row_t(r) + c * STAGGER
lbl = make_lbl('color_wave', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.color_wave(start=a, end=a + ANIM_DUR, wave_color='#FC6255')
objs += [lbl, s]

c = 5; a = row_t(r) + c * STAGGER
lbl = make_lbl('color_gradient_anim', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a)
s.color_gradient_anim(['#58C4DD', '#FC6255', '#FFFF00'], start=a, end=a + ANIM_DUR)
objs += [lbl, s]

# ── Row 1: Color effects ─────────────────────────────────────────────
r = 1

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('color_cycle', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a)
s.color_cycle(['#FC6255', '#FFFF00', '#9A72AC', '#83C167'], start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('flash_color', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.flash_color('#FFFF00', start=a, end=a + 0.8)
objs += [lbl, s]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('pulse_color', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.pulse_color('#FFFF00', start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('set_fill', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.set_fill(color='#FFFF00', start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 4; a = row_t(r) + c * STAGGER
lbl = make_lbl('set_stroke', c, r)
s = Circle(r=35, cx=col_x(c), cy=obj_y(r),
           fill=color(c, r), fill_opacity=0.7, stroke=color(c, r), stroke_width=2)
s.fadein(a - FADE_IN_BEFORE, a); s.set_stroke(color='#FFFF00', width=5, start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 5; a = row_t(r) + c * STAGGER
lbl = make_lbl('morph_style', c, r)
s = make_circle(c, r)
target_style = Circle(r=35, fill='#FC6255', fill_opacity=1.0,
                      stroke='#FFFF00', stroke_width=4)
s.fadein(a - FADE_IN_BEFORE, a); s.morph_style(target_style, start=a, end=a + ANIM_DUR)
objs += [lbl, s]

# ── Row 2: Opacity effects ───────────────────────────────────────────
r = 2

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('set_opacity', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.set_opacity(0.2, start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('dim', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.dim(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('undim', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a)
s.dim(start=a, end=a + 0.1)
s.undim(start=a + 0.2, end=a + ANIM_DUR)
objs += [lbl, s]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('blink', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.blink(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 4; a = row_t(r) + c * STAGGER
lbl = make_lbl('shimmer', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.shimmer(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 5; a = row_t(r) + c * STAGGER
lbl = make_lbl('flicker', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.flicker(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

# ── Row 3: Border / Stroke effects ───────────────────────────────────
r = 3

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('highlight_border', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.highlight_border(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('flash_highlight', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a)
hl_rect = s.flash_highlight(start=a, end=a + ANIM_DUR)
objs += [lbl, s, hl_rect]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('pulse_outline', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.pulse_outline(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('glow', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.glow(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 4; a = row_t(r) + c * STAGGER
lbl = make_lbl('animate_dash', c, r)
s = Circle(r=35, cx=col_x(c), cy=obj_y(r), fill_opacity=0,
           stroke=color(c, r), stroke_width=3)
s.fadein(a - FADE_IN_BEFORE, a); s.animate_dash(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 5; a = row_t(r) + c * STAGGER
lbl = make_lbl('circumscribe', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.circumscribe(start=a, end=a + ANIM_DUR, stroke='#FFFF00')
objs += [lbl, s]

# ── Row 4: Style animation ───────────────────────────────────────────
r = 4

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('set_style', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a)
s.set_style(stroke_width=4, start=a)
s.set_color(start=a, end=a + 0.01, fill='#FFFF00', stroke='#FC6255')
objs += [lbl, s]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('animate_style', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a)
s.animate_style(start=a, end=a + ANIM_DUR, fill='#FC6255', stroke_width=6, stroke='#FFFF00')
objs += [lbl, s]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('drop_shadow', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.drop_shadow(color='#58C4DD', dx=6, dy=6, blur=8, start=a)
objs += [lbl, s]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('cross_out', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a)
cross = s.cross_out(start=a, end=a + ANIM_DUR)
objs += [lbl, s, cross]

c = 4; a = row_t(r) + c * STAGGER
lbl = make_lbl('set_stroke_dash', c, r)
s = Circle(r=35, cx=col_x(c), cy=obj_y(r), fill_opacity=0,
           stroke=color(c, r), stroke_width=3)
s.fadein(a - FADE_IN_BEFORE, a); s.set_stroke_dash('10 5', start=a)
objs += [lbl, s]

c = 5; a = row_t(r) + c * STAGGER
lbl = make_lbl('save_state/restore', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a)
s.save_state(time=a)
s.set_color(start=a + 0.1, end=a + 0.4, fill='#FC6255')
s.scale(1.5, start=a + 0.1, end=a + 0.4)
s.restore(start=a + 0.5, end=a + ANIM_DUR)
objs += [lbl, s]

canvas.add_objects(*objs)

total_dur = row_t(N_ROWS - 1) + (COLS - 1) * STAGGER + ANIM_DUR + 1.0
if args.verbose:
    canvas.export_video('docs/source/_static/videos/animations_color.mp4',
                        fps=30, end=total_dur)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True,
                           end=total_dur)
