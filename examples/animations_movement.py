import math
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
N_ROWS = 6

canvas_h = FIRST_ROW + N_ROWS * ROW_H + 40
canvas = VectorMathAnim(width=1920, height=canvas_h, verbose=args.verbose,
                        save_dir='svgs/animations_movement')
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


def make_circle(c, r, radius=30):
    return Circle(r=radius, cx=col_x(c), cy=obj_y(r),
                  fill=color(c, r), fill_opacity=0.7)


# Title
title = Text(text='Movement & Transformation', x=960, y=TITLE_Y,
             font_size=44, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 0.5)
objs = [title]

# ── Row 0: Basic movement ────────────────────────────────────────────
r = 0

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('shift', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.shift(80, 0, start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('move_to', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.move_to(col_x(c) + 60, obj_y(r) - 30, start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('path_arc', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a)
s.path_arc(col_x(c) + 60, obj_y(r), start=a, end=a + ANIM_DUR, angle=math.pi)
objs += [lbl, s]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('follow_spline', c, r); s = make_circle(c, r, radius=20)
cx3, cy3 = col_x(c), obj_y(r)
pts = [(cx3 - 60, cy3), (cx3, cy3 - 40), (cx3 + 60, cy3), (cx3, cy3 + 40), (cx3 - 60, cy3)]
s.fadein(a - FADE_IN_BEFORE, a); s.follow_spline(pts, start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 4; a = row_t(r) + c * STAGGER
lbl = make_lbl('orbit', c, r); s = make_circle(c, r, radius=15)
s.fadein(a - FADE_IN_BEFORE, a); s.orbit(col_x(c), obj_y(r), radius=45, start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 5; a = row_t(r) + c * STAGGER
lbl = make_lbl('focus_on', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a)
target_dot = Dot(cx=col_x(c) + 50, cy=obj_y(r) - 30, r=5, fill='#666')
target_dot.fadein(a - FADE_IN_BEFORE, a)
s.focus_on((col_x(c) + 50, obj_y(r) - 30), start=a, end=a + ANIM_DUR)
objs += [lbl, target_dot, s]

# ── Row 1: Scale & stretch ───────────────────────────────────────────
r = 1

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('scale', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.scale(1.5, start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('scale_to', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.scale_to(start=a, end=a + ANIM_DUR, factor=2)
objs += [lbl, s]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('stretch', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.stretch(1.8, 0.6, start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('tilt_towards', c, r)
s = Rectangle(60, 60, x=col_x(c) - 30, y=obj_y(r) - 30,
              fill=color(c, r), fill_opacity=0.7)
s.fadein(a - FADE_IN_BEFORE, a)
s.tilt_towards(col_x(c), obj_y(r) - 60, start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 4; a = row_t(r) + c * STAGGER
lbl = make_lbl('look_at', c, r)
s = Rectangle(60, 60, x=col_x(c) - 30, y=obj_y(r) - 30,
              fill=color(c, r), fill_opacity=0.7)
target_pt = (col_x(c) + 60, obj_y(r) - 40)
s.fadein(a - FADE_IN_BEFORE, a); s.look_at(target_pt, start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 5; a = row_t(r) + c * STAGGER
lbl = make_lbl('scale_about_point', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a)
s.scale_about_point(1.5, col_x(c), obj_y(r) + 40, start=a, end=a + ANIM_DUR)
objs += [lbl, s]

# ── Row 2: Rotation ──────────────────────────────────────────────────
r = 2

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('rotate_by', c, r)
s = Rectangle(60, 60, x=col_x(c) - 30, y=obj_y(r) - 30,
              fill=color(c, r), fill_opacity=0.7)
s.fadein(a - FADE_IN_BEFORE, a); s.rotate_by(a, a + ANIM_DUR, 180)
objs += [lbl, s]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('rotate_to', c, r)
s = Rectangle(60, 60, x=col_x(c) - 30, y=obj_y(r) - 30,
              fill=color(c, r), fill_opacity=0.7)
s.fadein(a - FADE_IN_BEFORE, a); s.rotate_to(start=a, end=a + ANIM_DUR, degrees=45)
objs += [lbl, s]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('spin', c, r)
s = Star(n=5, outer_radius=35, inner_radius=17, cx=col_x(c), cy=obj_y(r),
         fill=color(c, r), fill_opacity=0.7)
s.fadein(a - FADE_IN_BEFORE, a); s.spin(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('flip', c, r)
s = Rectangle(60, 60, x=col_x(c) - 30, y=obj_y(r) - 30,
              fill=color(c, r), fill_opacity=0.7)
s.fadein(a - FADE_IN_BEFORE, a); s.flip(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 4; a = row_t(r) + c * STAGGER
lbl = make_lbl('skew', c, r)
s = Rectangle(60, 60, x=col_x(c) - 30, y=obj_y(r) - 30,
              fill=color(c, r), fill_opacity=0.7)
s.fadein(a - FADE_IN_BEFORE, a); s.skew(start=a, end=a + ANIM_DUR, x_degrees=20)
objs += [lbl, s]

c = 5; a = row_t(r) + c * STAGGER
lbl = make_lbl('reflect', c, r)
s = RegularPolygon(3, radius=40, cx=col_x(c), cy=obj_y(r),
                   fill=color(c, r), fill_opacity=0.7)
s.fadein(a - FADE_IN_BEFORE, a); s.reflect(start=a, axis='vertical')
objs += [lbl, s]

# ── Row 3: Transform & morph ─────────────────────────────────────────
r = 3

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('become', c, r)
s = make_circle(c, r)
target = Rectangle(50, 50, x=col_x(c) - 25, y=obj_y(r) - 25,
                   fill='#FFFF00', fill_opacity=0.7)
s.fadein(a - FADE_IN_BEFORE, a); s.become(target, time=a)
objs += [lbl, s]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('fade_transform', c, r)
s1 = make_circle(c, r)
s2 = Rectangle(50, 50, x=col_x(c) - 25, y=obj_y(r) - 25,
               fill='#FFFF00', fill_opacity=0.7)
s1.fadein(a - FADE_IN_BEFORE, a)
VObject.fade_transform(s1, s2, start=a, end=a + ANIM_DUR)
objs += [lbl, s1, s2]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('swap', c, r)
sa = Circle(r=20, cx=col_x(c) - 35, cy=obj_y(r), fill='#58C4DD', fill_opacity=0.7)
sb = Circle(r=20, cx=col_x(c) + 35, cy=obj_y(r), fill='#FC6255', fill_opacity=0.7)
sa.fadein(a - FADE_IN_BEFORE, a); sb.fadein(a - FADE_IN_BEFORE, a)
VObject.swap(sa, sb, start=a, end=a + ANIM_DUR)
objs += [lbl, sa, sb]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('apply_matrix', c, r)
s = Rectangle(50, 50, x=col_x(c) - 25, y=obj_y(r) - 25,
              fill=color(c, r), fill_opacity=0.7)
s.fadein(a - FADE_IN_BEFORE, a); s.apply_matrix([[1, 0.3], [0, 1]], start=a)
objs += [lbl, s]

c = 4; a = row_t(r) + c * STAGGER
lbl = make_lbl('homotopy', c, r)
s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a)
s.homotopy(lambda x, y, p: (x + 30 * math.sin(p * math.pi * 2), y + 20 * math.cos(p * math.pi * 2)),
           start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 5; a = row_t(r) + c * STAGGER
lbl = make_lbl('transform_from_copy', c, r)
src = Circle(r=20, cx=col_x(c) - 50, cy=obj_y(r) + 30,
             fill='#666', fill_opacity=0.5)
src.fadein(a - FADE_IN_BEFORE, a)
s = make_circle(c, r)
s.fadein(a, a)  # hidden until morph completes
morph = src.transform_from_copy(s, start=a, end=a + ANIM_DUR)
objs += [lbl, src, s, morph]

# ── Row 4: Continuous / tracking ──────────────────────────────────────
r = 4

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('always_rotate', c, r)
s = Star(n=5, outer_radius=35, inner_radius=17, cx=col_x(c), cy=obj_y(r),
         fill=color(c, r), fill_opacity=0.7)
s.fadein(a - FADE_IN_BEFORE, a); s.always_rotate(start=a, end=a + ANIM_DUR, degrees_per_second=180)
objs += [lbl, s]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('always_shift', c, r); s = make_circle(c, r, radius=20)
s.fadein(a - FADE_IN_BEFORE, a); s.always_shift(50, 0, start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('follow', c, r)
leader = Circle(r=15, cx=col_x(c) - 30, cy=obj_y(r), fill='#666', fill_opacity=0.5)
leader.fadein(a - FADE_IN_BEFORE, a)
leader.shift(60, 0, start=a, end=a + ANIM_DUR)
follower = Circle(r=20, cx=col_x(c), cy=obj_y(r), fill=color(c, r), fill_opacity=0.7)
follower.fadein(a - FADE_IN_BEFORE, a)
follower.follow(leader, start=a, end=a + ANIM_DUR)
objs += [lbl, leader, follower]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('skate', c, r); s = make_circle(c, r, radius=20)
s.fadein(a - FADE_IN_BEFORE, a)
s.skate(col_x(c) + 60, obj_y(r), start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 4; a = row_t(r) + c * STAGGER
lbl = make_lbl('slingshot', c, r); s = make_circle(c, r, radius=20)
s.fadein(a - FADE_IN_BEFORE, a)
s.slingshot(col_x(c) + 60, obj_y(r), start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 5; a = row_t(r) + c * STAGGER
lbl = make_lbl('move_towards', c, r)
target2 = Dot(cx=col_x(c) + 60, cy=obj_y(r) - 20, r=5, fill='#666')
target2.fadein(a - FADE_IN_BEFORE, a)
s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a)
s.move_towards(target2, fraction=0.7, start=a, end=a + ANIM_DUR)
objs += [lbl, target2, s]

# ── Row 5: Position utilities ─────────────────────────────────────────
r = 5

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('to_edge', c, r); s = make_circle(c, r, radius=20)
s.fadein(a - FADE_IN_BEFORE, a); s.to_edge('right', start=a)
objs += [lbl, s]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('set_x / set_y', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a)
s.set_x(col_x(c) + 50, start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('align_to', c, r)
ref = Dot(cx=col_x(c) + 40, cy=obj_y(r), r=5, fill='#666')
ref.fadein(a - FADE_IN_BEFORE, a)
s = make_circle(c, r, radius=20)
s.fadein(a - FADE_IN_BEFORE, a)
s.align_to(ref, 'right', start=a, end=a + ANIM_DUR)
objs += [lbl, ref, s]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('place_between', c, r)
pa = Dot(cx=col_x(c) - 50, cy=obj_y(r), r=5, fill='#666')
pb = Dot(cx=col_x(c) + 50, cy=obj_y(r), r=5, fill='#666')
pa.fadein(a - FADE_IN_BEFORE, a); pb.fadein(a - FADE_IN_BEFORE, a)
s = make_circle(c, r, radius=15)
s.fadein(a - FADE_IN_BEFORE, a)
s.place_between(pa, pb, start=a, end=a + ANIM_DUR)
objs += [lbl, pa, pb, s]

c = 4; a = row_t(r) + c * STAGGER
lbl = make_lbl('float_anim', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a)
s.float_anim(start=a, end=a + ANIM_DUR, amplitude=15)
objs += [lbl, s]

c = 5; a = row_t(r) + c * STAGGER
lbl = make_lbl('spin_and_fade', c, r)
s = Star(n=5, outer_radius=40, cx=col_x(c), cy=obj_y(r),
         fill=color(c, r), fill_opacity=0.7)
s.fadein(a - FADE_IN_BEFORE, a)
s.spin_and_fade(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

canvas.add_objects(*objs)

total_dur = row_t(N_ROWS - 1) + (COLS - 1) * STAGGER + ANIM_DUR + 1.0
if args.for_docs:
    canvas.export_video('docs/source/_static/videos/animations_movement.mp4',
                        fps=30, end=total_dur)
if not args.for_docs:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=total_dur)
