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
N_ROWS = 7

canvas_h = FIRST_ROW + N_ROWS * ROW_H + 40
canvas = VectorMathAnim(width=1920, height=canvas_h)
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


def make_circle(c, r):
    return Circle(r=40, cx=col_x(c), cy=obj_y(r),
                  fill=color(c, r), fill_opacity=0.7)


# Title
title = Text(text='Creation & Destruction', x=960, y=TITLE_Y,
             font_size=44, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 0.5)
objs = [title]

# ── Row 0: Basic creation ────────────────────────────────────────────
r = 0

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('fadein', c, r); s = make_circle(c, r)
s.fadein(a, a + ANIM_DUR)
objs += [lbl, s]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('write', c, r); s = make_circle(c, r)
s.write(a, a + ANIM_DUR)
objs += [lbl, s]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('create', c, r); s = make_circle(c, r)
s.create(a, a + ANIM_DUR)
objs += [lbl, s]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('draw_along', c, r); s = make_circle(c, r)
s.draw_along(a, a + ANIM_DUR)
objs += [lbl, s]

c = 4; a = row_t(r) + c * STAGGER
lbl = make_lbl('draw_border_then_fill', c, r)
s = make_circle(c, r)
s.draw_border_then_fill(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 5; a = row_t(r) + c * STAGGER
lbl = make_lbl('wipe', c, r); s = make_circle(c, r)
s.wipe(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

# ── Row 1: Pop / Zoom / Elastic / Bounce ─────────────────────────────
r = 1

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('pop_in', c, r); s = make_circle(c, r)
s.pop_in(a, a + ANIM_DUR)
objs += [lbl, s]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('zoom_in', c, r); s = make_circle(c, r)
s.zoom_in(a, a + ANIM_DUR)
objs += [lbl, s]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('elastic_in', c, r); s = make_circle(c, r)
s.elastic_in(a, a + ANIM_DUR)
objs += [lbl, s]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('bounce_in', c, r); s = make_circle(c, r)
s.bounce_in(a, a + ANIM_DUR)
objs += [lbl, s]

c = 4; a = row_t(r) + c * STAGGER
lbl = make_lbl('grow_from_center', c, r); s = make_circle(c, r)
s.grow_from_center(a, a + ANIM_DUR)
objs += [lbl, s]

c = 5; a = row_t(r) + c * STAGGER
lbl = make_lbl('grow_from_edge', c, r); s = make_circle(c, r)
s.grow_from_edge('bottom', start=a, end=a + ANIM_DUR)
objs += [lbl, s]

# ── Row 2: Slide / Rotate / Spiral / Corners ─────────────────────────
r = 2

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('slide_in', c, r); s = make_circle(c, r)
s.slide_in('left', start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('fade_slide_in', c, r); s = make_circle(c, r)
s.fade_slide_in('bottom', start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('rotate_in', c, r)
s = Star(n=5, outer_radius=40, cx=col_x(c), cy=obj_y(r),
         fill=color(c, r), fill_opacity=0.7)
s.rotate_in(a, a + ANIM_DUR)
objs += [lbl, s]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('spin_in', c, r)
s = Star(n=5, outer_radius=40, cx=col_x(c), cy=obj_y(r),
         fill=color(c, r), fill_opacity=0.7)
s.spin_in(a, a + ANIM_DUR)
objs += [lbl, s]

c = 4; a = row_t(r) + c * STAGGER
lbl = make_lbl('spiral_in', c, r)
s = Star(n=5, outer_radius=40, cx=col_x(c), cy=obj_y(r),
         fill=color(c, r), fill_opacity=0.7)
s.spiral_in(a, a + ANIM_DUR)
objs += [lbl, s]

c = 5; a = row_t(r) + c * STAGGER
lbl = make_lbl('grow_from_corner', c, r); s = make_circle(c, r)
s.grow_from_corner(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

# ── Row 3: More creation ─────────────────────────────────────────────
r = 3

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('grow_from_point', c, r); s = make_circle(c, r)
s.grow_from_point(col_x(c), obj_y(r) + 60, start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('dissolve_in', c, r); s = make_circle(c, r)
s.dissolve_in(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('wipe (left)', c, r); s = make_circle(c, r)
s.wipe(start=a, end=a + ANIM_DUR, direction='left')
objs += [lbl, s]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('wipe (up)', c, r); s = make_circle(c, r)
s.wipe(start=a, end=a + ANIM_DUR, direction='up')
objs += [lbl, s]

c = 4; a = row_t(r) + c * STAGGER
lbl = make_lbl('fade_shift', c, r)
s = make_circle(c, r)
s.fadein(a, a + 0.3)
s.fade_shift(dx=0, dy=-40, start=a + 0.3, end=a + ANIM_DUR)
objs += [lbl, s]

c = 5; a = row_t(r) + c * STAGGER
lbl = make_lbl('appear_from', c, r)
src = Dot(cx=col_x(c), cy=obj_y(r) + 80, r=6, fill='#666')
src.fadein(a - FADE_IN_BEFORE, a)
s = make_circle(c, r)
s.appear_from(src, start=a, end=a + ANIM_DUR)
objs += [lbl, src, s]

# ── Row 4: Destruction (basic) ────────────────────────────────────────
r = 4

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('fadeout', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.fadeout(a, a + ANIM_DUR)
objs += [lbl, s]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('pop_out', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.pop_out(a, a + ANIM_DUR)
objs += [lbl, s]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('zoom_out', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.zoom_out(a, a + ANIM_DUR)
objs += [lbl, s]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('elastic_out', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.elastic_out(a, a + ANIM_DUR)
objs += [lbl, s]

c = 4; a = row_t(r) + c * STAGGER
lbl = make_lbl('bounce_out', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.bounce_out(a, a + ANIM_DUR)
objs += [lbl, s]

c = 5; a = row_t(r) + c * STAGGER
lbl = make_lbl('slide_out', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.slide_out('right', start=a, end=a + ANIM_DUR)
objs += [lbl, s]

# ── Row 5: More destruction ───────────────────────────────────────────
r = 5

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('fade_slide_out', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.fade_slide_out('top', start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('spin_out', c, r)
s = Star(n=5, outer_radius=40, cx=col_x(c), cy=obj_y(r),
         fill=color(c, r), fill_opacity=0.7)
s.fadein(a - FADE_IN_BEFORE, a); s.spin_out(a, a + ANIM_DUR)
objs += [lbl, s]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('spiral_out', c, r)
s = Star(n=5, outer_radius=40, cx=col_x(c), cy=obj_y(r),
         fill=color(c, r), fill_opacity=0.7)
s.fadein(a - FADE_IN_BEFORE, a); s.spiral_out(a, a + ANIM_DUR)
objs += [lbl, s]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('dissolve_out', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.dissolve_out(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 4; a = row_t(r) + c * STAGGER
lbl = make_lbl('uncreate', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.uncreate(a, a + ANIM_DUR)
objs += [lbl, s]

c = 5; a = row_t(r) + c * STAGGER
lbl = make_lbl('rotate_out', c, r)
s = Star(n=5, outer_radius=40, cx=col_x(c), cy=obj_y(r),
         fill=color(c, r), fill_opacity=0.7)
s.fadein(a - FADE_IN_BEFORE, a); s.rotate_out(a, a + ANIM_DUR)
objs += [lbl, s]

# ── Row 6: Shrink / Combined ─────────────────────────────────────────
r = 6

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('shrink_to_center', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.shrink_to_center(a, a + ANIM_DUR)
objs += [lbl, s]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('shrink_to_edge', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.shrink_to_edge('bottom', start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('shrink_to_corner', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a); s.shrink_to_corner(start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('shrink_to_point', c, r); s = make_circle(c, r)
s.fadein(a - FADE_IN_BEFORE, a)
s.shrink_to_point(col_x(c), obj_y(r) + 60, start=a, end=a + ANIM_DUR)
objs += [lbl, s]

c = 4; a = row_t(r) + c * STAGGER
lbl = make_lbl('fadein_then_fadeout', c, r); s = make_circle(c, r)
s.fadein_then_fadeout(start=a, end=a + 1.5)
objs += [lbl, s]

c = 5; a = row_t(r) + c * STAGGER
lbl = make_lbl('create_then_fadeout', c, r); s = make_circle(c, r)
s.create_then_fadeout(start=a, end=a + 1.5)
objs += [lbl, s]

canvas.add_objects(*objs)

total_dur = row_t(N_ROWS - 1) + (COLS - 1) * STAGGER + ANIM_DUR + 1.0

canvas.show(end=total_dur)
