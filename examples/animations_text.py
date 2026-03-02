import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

# Layout — fewer columns, wider cells for text demos
COLS = 4
COL_W = 1920 // COLS
ROW_H = 200
TITLE_Y = 50
FIRST_ROW = 140
ROW_DUR = 3.5
ANIM_DUR = 1.2
STAGGER = 0.5
FADE_IN_BEFORE = 0.8
COLORS = ['#58C4DD', '#83C167', '#FC6255', '#F0AC5F', '#9A72AC', '#5CD0B3']
N_ROWS = 4

canvas_h = FIRST_ROW + N_ROWS * ROW_H + 40
canvas = VectorMathAnim(width=1920, height=canvas_h, verbose=args.verbose,
                        save_dir='svgs/animations_text')
canvas.set_background()


def col_x(c):
    return COL_W // 2 + c * COL_W


def lbl_y(r):
    return FIRST_ROW + r * ROW_H - 15


def obj_y(r):
    return FIRST_ROW + r * ROW_H + 65


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


def make_text(c, r, txt='Hello World'):
    return Text(text=txt, x=col_x(c), y=obj_y(r),
                font_size=36, fill=color(c, r), stroke_width=0, text_anchor='middle')


# Title
title = Text(text='Text Animations', x=960, y=TITLE_Y,
             font_size=44, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 0.5)
objs = [title]

# ── Row 0: Typewriter variants ────────────────────────────────────────
r = 0

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('typewrite', c, r)
s = make_text(c, r, 'Typewrite')
s.typewrite(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('typing', c, r)
s = make_text(c, r, 'Typing Effect')
s.typing(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('untype', c, r)
s = make_text(c, r, 'Vanishing')
s.fadein(a - FADE_IN_BEFORE, a)
s.untype(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('scramble', c, r)
s = make_text(c, r, 'Decoded')
s.scramble(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

# ── Row 1: Reveal / Word ─────────────────────────────────────────────
r = 1

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('reveal_by_word', c, r)
s = make_text(c, r, 'Word By Word')
s.reveal_by_word(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('write (text)', c, r)
s = make_text(c, r, 'Write In')
s.write(a, a + ANIM_DUR)
objs += [lbl, s]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('fadein (text)', c, r)
s = make_text(c, r, 'Fade In')
s.fadein(a, a + ANIM_DUR)
objs += [lbl, s]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('create (text)', c, r)
s = make_text(c, r, 'Create')
s.create(a, a + ANIM_DUR)
objs += [lbl, s]

# ── Row 2: Highlight / Transform ─────────────────────────────────────
r = 2

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('highlight', c, r)
s = make_text(c, r, 'Highlighted')
s.fadein(a - FADE_IN_BEFORE, a)
hl = s.highlight(start=a, end=a + ANIM_DUR, color='#FFFF00')
objs += [lbl, s, hl]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('highlight_substring', c, r)
s = make_text(c, r, 'Partial Light')
s.fadein(a - FADE_IN_BEFORE, a)
hl2 = s.highlight_substring('Partial', color='#FC6255', start=a, end=a + ANIM_DUR)
objs += [lbl, s, hl2]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('set_text', c, r)
s = make_text(c, r, 'Before')
s.fadein(a - FADE_IN_BEFORE, a)
s.set_text(start=a, end=a + ANIM_DUR, new_text='After!')
objs += [lbl, s]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('set_font_size', c, r)
s = make_text(c, r, 'Growing')
s.fadein(a - FADE_IN_BEFORE, a)
s.set_font_size(56, start=a, end=a + ANIM_DUR)
objs += [lbl, s]

# ── Row 3: Special text effects ──────────────────────────────────────
r = 3

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('typewriter_effect', c, r)
s = make_text(c, r, '')
s.typewriter_effect('TypeFX', start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('typewriter_cursor', c, r)
s = make_text(c, r, 'Cursor')
s.fadein(a - FADE_IN_BEFORE, a)
s.typewriter_cursor(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('wipe (reverse)', c, r)
s = make_text(c, r, 'Delete Me')
s.fadein(a - FADE_IN_BEFORE, a)
s.wipe(start=a, end=a + ANIM_DUR, reverse=True)
objs += [lbl, s]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('indicate (text)', c, r)
s = make_text(c, r, 'Notice Me')
s.fadein(a - FADE_IN_BEFORE, a)
s.indicate(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

canvas.add_objects(*objs)

total_dur = row_t(N_ROWS - 1) + (COLS - 1) * STAGGER + ANIM_DUR + 1.0
if args.for_docs:
    canvas.export_video('docs/source/_static/videos/animations_text.mp4',
                        fps=30, end=total_dur)
if not args.for_docs:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=total_dur)
