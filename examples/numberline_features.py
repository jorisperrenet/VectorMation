import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

COLS = 2
ROWS = 2
COL_W = 1920 // COLS
ROW_H = 400
TITLE_Y = 50
FIRST_ROW = 130
ANIM_DUR = 3.0
STAGGER = 0.5
FADE_IN_BEFORE = 0.5

canvas_h = FIRST_ROW + ROWS * ROW_H + 40
canvas = VectorMathAnim(width=1920, height=canvas_h, verbose=args.verbose,
                        save_dir='svgs/numberline_features')
canvas.set_background()

def col_x(c): return COL_W // 2 + c * COL_W
def lbl_y(r): return FIRST_ROW + r * ROW_H - 10
def obj_y(r): return FIRST_ROW + r * ROW_H + 100

title = Text(text='NumberLine Features', x=960, y=TITLE_Y, font_size=44,
             fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 0.5)
objs = [title]

# --- (0,0): add_pointer + animate_pointer ---
c, r = 0, 0
t0 = (c + r * COLS) * STAGGER
lbl0 = Text(text='add_pointer + animate', x=col_x(c), y=lbl_y(r),
            font_size=22, fill='#aaa', stroke_width=0, text_anchor='middle')
lbl0.fadein(t0, t0 + FADE_IN_BEFORE)
objs.append(lbl0)

nl0 = NumberLine(x_range=(-5, 5, 1), length=400, x=col_x(c) - 200, y=obj_y(r),
                 include_arrows=True, include_numbers=True, tick_size=20, font_size=16)
nl0.fadein(t0, t0 + FADE_IN_BEFORE)

ptr = nl0.add_pointer(-3, label='x', color='#FF6B6B', size=10, creation=t0 + FADE_IN_BEFORE)
nl0.animate_pointer(ptr, 3, start=t0 + FADE_IN_BEFORE, end=t0 + FADE_IN_BEFORE + ANIM_DUR * 0.5)
nl0.animate_pointer(ptr, 0, start=t0 + FADE_IN_BEFORE + ANIM_DUR * 0.55,
                    end=t0 + FADE_IN_BEFORE + ANIM_DUR)
objs.append(nl0)

# --- (1,0): point_to_number ---
c, r = 1, 0
t1 = (c + r * COLS) * STAGGER
lbl1 = Text(text='point_to_number', x=col_x(c), y=lbl_y(r),
            font_size=22, fill='#aaa', stroke_width=0, text_anchor='middle')
lbl1.fadein(t1, t1 + FADE_IN_BEFORE)
objs.append(lbl1)

nl1 = NumberLine(x_range=(-5, 5, 1), length=400, x=col_x(c) - 200, y=obj_y(r),
                 include_arrows=True, include_numbers=True, tick_size=20, font_size=16)
nl1.fadein(t1, t1 + FADE_IN_BEFORE)

# Place a dot at value 2.7 and show the converted number
test_val = 2.7
px1, py1 = nl1.number_to_point(test_val)
dot1 = Dot(cx=px1, cy=py1, r=8, fill='#83C167', stroke_width=0)
dot1.fadein(t1 + FADE_IN_BEFORE, t1 + FADE_IN_BEFORE + 0.3)
dot1.pulsate(t1 + FADE_IN_BEFORE + 0.3, t1 + FADE_IN_BEFORE + 0.8, scale_factor=1.4)

# Show the returned number value as text
num_result = nl1.point_to_number(px1)
val_text1 = Text(text=f'= {num_result:.1f}', x=px1, y=py1 - 30,
                 font_size=20, fill='#83C167', stroke_width=0, text_anchor='middle')
val_text1.fadein(t1 + FADE_IN_BEFORE + 0.5, t1 + FADE_IN_BEFORE + 0.8)

# Second dot at value -1.3
test_val2 = -1.3
px2, py2 = nl1.number_to_point(test_val2)
dot2 = Dot(cx=px2, cy=py2, r=8, fill='#FFFF00', stroke_width=0)
dot2.fadein(t1 + FADE_IN_BEFORE + 1.0, t1 + FADE_IN_BEFORE + 1.3)
dot2.pulsate(t1 + FADE_IN_BEFORE + 1.3, t1 + FADE_IN_BEFORE + 1.8, scale_factor=1.4)

num_result2 = nl1.point_to_number(px2)
val_text2 = Text(text=f'= {num_result2:.1f}', x=px2, y=py2 - 30,
                 font_size=20, fill='#FFFF00', stroke_width=0, text_anchor='middle')
val_text2.fadein(t1 + FADE_IN_BEFORE + 1.5, t1 + FADE_IN_BEFORE + 1.8)

objs.extend([nl1, dot1, val_text1, dot2, val_text2])

# --- (0,1): snap_to_tick ---
c, r = 0, 1
t2 = (c + r * COLS) * STAGGER
lbl2 = Text(text='snap_to_tick', x=col_x(c), y=lbl_y(r),
            font_size=22, fill='#aaa', stroke_width=0, text_anchor='middle')
lbl2.fadein(t2, t2 + FADE_IN_BEFORE)
objs.append(lbl2)

nl2 = NumberLine(x_range=(-4, 4, 1), length=400, x=col_x(c) - 200, y=obj_y(r),
                 include_arrows=True, include_numbers=True, tick_size=20, font_size=16)
nl2.fadein(t2, t2 + FADE_IN_BEFORE)

# Show dots snapping from non-tick positions to tick positions
snap_values = [1.3, -2.7, 0.4]
snap_colors = ['#FF6B6B', '#58C4DD', '#9B59B6']
for i, (val, clr) in enumerate(zip(snap_values, snap_colors)):
    snapped = nl2.snap_to_tick(val)
    orig_px, orig_py = nl2.number_to_point(val)
    snap_px, _ = nl2.number_to_point(snapped)

    st = t2 + FADE_IN_BEFORE + i * 0.8
    d = Dot(cx=orig_px, cy=orig_py, r=7, fill=clr, stroke_width=0)
    d.fadein(st, st + 0.2)
    # Animate dot sliding to the snapped position
    d.shift(dx=snap_px - orig_px, dy=0, start=st + 0.3, end=st + 0.7)

    snap_lbl = Text(text=f'{val} -> {snapped:g}', x=orig_px, y=orig_py - 22,
                    font_size=14, fill=clr, stroke_width=0, text_anchor='middle')
    snap_lbl.fadein(st + 0.2, st + 0.4)
    # Move label along with dot
    snap_lbl.shift(dx=snap_px - orig_px, dy=0, start=st + 0.3, end=st + 0.7)
    objs.extend([d, snap_lbl])

objs.append(nl2)

# --- (1,1): highlight_range ---
c, r = 1, 1
t3 = (c + r * COLS) * STAGGER
lbl3 = Text(text='highlight_range', x=col_x(c), y=lbl_y(r),
            font_size=22, fill='#aaa', stroke_width=0, text_anchor='middle')
lbl3.fadein(t3, t3 + FADE_IN_BEFORE)
objs.append(lbl3)

nl3 = NumberLine(x_range=(-5, 5, 1), length=400, x=col_x(c) - 200, y=obj_y(r),
                 include_arrows=True, include_numbers=True, tick_size=20, font_size=16)
nl3.fadein(t3, t3 + FADE_IN_BEFORE)

# Multiple colored highlights, staggered
ranges = [
    (-4, -1, '#FF6B6B', 0.5),
    (-1,  2, '#58C4DD', 0.4),
    ( 2,  4, '#83C167', 0.5),
]
for i, (sv, ev, clr, op) in enumerate(ranges):
    st = t3 + FADE_IN_BEFORE + i * 0.7
    hr = nl3.highlight_range(sv, ev, color=clr, height=18, opacity=op, creation=st)
    hr.fadein(st, st + 0.4)

objs.append(nl3)

canvas.add_objects(*objs)

total_dur = (COLS * ROWS - 1) * STAGGER + ANIM_DUR + 2.0
if args.for_docs:
    canvas.export_video('docs/source/_static/videos/numberline_features.mp4',
                        fps=30, end=total_dur)
if not args.for_docs:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=total_dur)
