import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()

# Layout
COLS = 4
COL_W = 1920 // COLS
ROW_H = 200
TITLE_Y = 50
FIRST_ROW = 140
ROW_DUR = 3.5
ANIM_DUR = 1.5
STAGGER = 0.5
FADE_IN_BEFORE = 0.8
DOT_COLORS = ['#58C4DD', '#83C167', '#FC6255', '#F0AC5F', '#9A72AC']
N_ROWS = 7

canvas_h = FIRST_ROW + N_ROWS * ROW_H + 40
canvas = VectorMathAnim(width=1920, height=canvas_h, verbose=args.verbose,
                        save_dir='svgs/animations_vcollection')
canvas.set_background()


def col_x(c):
    return COL_W // 2 + c * COL_W


def lbl_y(r):
    return FIRST_ROW + r * ROW_H - 15


def obj_y(r):
    return FIRST_ROW + r * ROW_H + 65


def row_t(r):
    return 0.5 + r * ROW_DUR


def make_lbl(name, c, r):
    a = row_t(r) + c * STAGGER
    lbl = Text(text=name, x=col_x(c), y=lbl_y(r),
               font_size=20, fill='#999', stroke_width=0, text_anchor='middle')
    lbl.fadein(a - FADE_IN_BEFORE, a)
    return lbl


def make_group(c, r, n=5, radius=12, spacing=30):
    """Create a horizontal row of small circles for demonstrating group animations."""
    cx_base = col_x(c) - (n - 1) * spacing / 2
    dots = []
    for i in range(n):
        d = Circle(r=radius, cx=cx_base + i * spacing, cy=obj_y(r),
                   fill=DOT_COLORS[i % len(DOT_COLORS)], fill_opacity=0.8)
        dots.append(d)
    return VCollection(*dots)


def make_grid(c, r, rows=3, cols=4, size=18, gap=8):
    """Create a 2D grid of small squares, suitable for spatial demos."""
    cx0 = col_x(c) - (cols - 1) * (size + gap) / 2
    cy0 = obj_y(r) - (rows - 1) * (size + gap) / 2
    items = []
    for ri in range(rows):
        for ci in range(cols):
            color = DOT_COLORS[(ri * cols + ci) % len(DOT_COLORS)]
            s = Rectangle(width=size, height=size,
                          x=cx0 + ci * (size + gap) - size / 2,
                          y=cy0 + ri * (size + gap) - size / 2,
                          fill=color, fill_opacity=0.8, stroke_width=0)
            items.append(s)
    return VCollection(*items)


# Title
title = Text(text='VCollection Animations', x=960, y=TITLE_Y,
             font_size=44, fill='#58C4DD', stroke_width=0, text_anchor='middle')
title.write(0, 0.5)
objs = [title]

# == Row 0: stagger overlap comparison ======================================
r = 0

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('stagger overlap=0', c, r)
g = make_group(c, r)
g.stagger('fadein', start=a, end=a + ANIM_DUR, overlap=0)
objs += [lbl, g]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('stagger overlap=0.5', c, r)
g = make_group(c, r)
g.stagger('fadein', start=a, end=a + ANIM_DUR, overlap=0.5)
objs += [lbl, g]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('stagger overlap=0.8', c, r)
g = make_group(c, r)
g.stagger('fadein', start=a, end=a + ANIM_DUR, overlap=0.8)
objs += [lbl, g]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('stagger overlap=1', c, r)
g = make_group(c, r)
g.stagger('fadein', start=a, end=a + ANIM_DUR, overlap=1)
objs += [lbl, g]

# == Row 1: Entrance variants ===============================================
r = 1

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('stagger_fadein + shift', c, r)
g = make_group(c, r)
g.stagger_fadein(start=a, end=a + ANIM_DUR, shift_dir=UP, shift_amount=40)
objs += [lbl, g]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('stagger write', c, r)
stars = [Star(n=5, outer_radius=12,
              cx=col_x(c) - 2 * 30 + i * 30, cy=obj_y(r),
              fill=DOT_COLORS[i % len(DOT_COLORS)], fill_opacity=0.8)
         for i in range(5)]
g = VCollection(*stars)
g.stagger('write', start=a, end=a + ANIM_DUR)
objs += [lbl, g]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('reveal', c, r)
g = make_group(c, r)
g.reveal(start=a, end=a + ANIM_DUR)
objs += [lbl, g]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('waterfall', c, r)
g = make_group(c, r)
g.waterfall(start=a, end=a + ANIM_DUR, height=80)
objs += [lbl, g]

# == Row 2: Spatially sorted (2D grids) =====================================
r = 2

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('sorted: left to right', c, r)
g = make_grid(c, r)
g.stagger_fadein_sorted(start=a, end=a + ANIM_DUR, direction='left_to_right')
objs += [lbl, g]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('sorted: top to bottom', c, r)
g = make_grid(c, r)
g.stagger_fadein_sorted(start=a, end=a + ANIM_DUR, direction='top_to_bottom')
objs += [lbl, g]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('sorted: center out', c, r)
g = make_grid(c, r)
g.stagger_fadein_sorted(start=a, end=a + ANIM_DUR, direction='center_out')
objs += [lbl, g]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('stagger_random', c, r)
g = make_grid(c, r)
g.stagger_random('fadein', start=a, end=a + ANIM_DUR)
objs += [lbl, g]

# == Row 3: Stagger effects =================================================
r = 3

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('stagger_scale', c, r)
g = make_group(c, r)
g.stagger_fadein(start=a - FADE_IN_BEFORE, end=a)
g.stagger_scale(start=a, end=a + ANIM_DUR)
objs += [lbl, g]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('stagger_rotate', c, r)
stars = [Star(n=5, outer_radius=12,
              cx=col_x(c) - 2 * 30 + i * 30, cy=obj_y(r),
              fill=DOT_COLORS[i % len(DOT_COLORS)], fill_opacity=0.8)
         for i in range(5)]
g = VCollection(*stars)
g.stagger_fadein(start=a - FADE_IN_BEFORE, end=a)
g.stagger_rotate(start=a, end=a + ANIM_DUR)
objs += [lbl, g]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('stagger_color', c, r)
g = make_group(c, r)
g.stagger_fadein(start=a - FADE_IN_BEFORE, end=a)
g.stagger_color(start=a, end=a + ANIM_DUR)
objs += [lbl, g]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('wave_anim', c, r)
g = make_group(c, r)
g.stagger_fadein(start=a - FADE_IN_BEFORE, end=a)
g.wave_anim(start=a, end=a + ANIM_DUR, amplitude=20)
objs += [lbl, g]

# == Row 4: Wave / motion ===================================================
r = 4

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('wave_effect', c, r)
g = make_group(c, r)
g.stagger_fadein(start=a - FADE_IN_BEFORE, end=a)
g.wave_effect(start=a, end=a + ANIM_DUR, amplitude=20)
objs += [lbl, g]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('shuffle_animate', c, r)
g = make_group(c, r)
g.stagger_fadein(start=a - FADE_IN_BEFORE, end=a)
g.shuffle_animate(start=a, end=a + ANIM_DUR)
objs += [lbl, g]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('swap_children', c, r)
g = make_group(c, r)
g.stagger_fadein(start=a - FADE_IN_BEFORE, end=a)
g.swap_children(0, 4, start=a, end=a + ANIM_DUR)
objs += [lbl, g]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('rotate_children', c, r)
g = make_group(c, r)
g.stagger_fadein(start=a - FADE_IN_BEFORE, end=a)
g.rotate_children(start=a, end=a + ANIM_DUR)
objs += [lbl, g]

# == Row 5: Spatial ==========================================================
r = 5

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('scatter_from', c, r)
g = make_group(c, r, spacing=8)
g.stagger_fadein(start=a - FADE_IN_BEFORE, end=a)
g.scatter_from(col_x(c), obj_y(r), radius=80, start=a, end=a + ANIM_DUR)
objs += [lbl, g]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('gather_to', c, r)
g = make_group(c, r)
g.stagger_fadein(start=a - FADE_IN_BEFORE, end=a)
g.gather_to(col_x(c), obj_y(r), start=a, end=a + ANIM_DUR)
objs += [lbl, g]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('fan_out', c, r)
g = make_group(c, r, spacing=8)
g.stagger_fadein(start=a - FADE_IN_BEFORE, end=a)
g.fan_out(col_x(c), obj_y(r), radius=70, start=a, end=a + ANIM_DUR)
objs += [lbl, g]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('orbit_around', c, r)
g = make_group(c, r, spacing=8)
g.stagger_fadein(start=a - FADE_IN_BEFORE, end=a)
g.orbit_around(col_x(c), obj_y(r), radius=60, start=a, end=a + ANIM_DUR)
objs += [lbl, g]

# == Row 6: Highlight / Exit ================================================
r = 6

c = 0; a = row_t(r) + c * STAGGER
lbl = make_lbl('highlight_child', c, r)
g = make_group(c, r)
g.stagger_fadein(start=a - FADE_IN_BEFORE, end=a)
g.highlight_child(2, start=a, end=a + ANIM_DUR)
objs += [lbl, g]

c = 1; a = row_t(r) + c * STAGGER
lbl = make_lbl('stagger_fadeout', c, r)
g = make_group(c, r)
g.stagger_fadein(start=a - FADE_IN_BEFORE, end=a)
g.stagger_fadeout(start=a, end=a + ANIM_DUR)
objs += [lbl, g]

c = 2; a = row_t(r) + c * STAGGER
lbl = make_lbl('flip_all', c, r)
g = make_group(c, r)
g.stagger_fadein(start=a - FADE_IN_BEFORE, end=a)
g.flip_all(start=a, end=a + ANIM_DUR)
objs += [lbl, g]

c = 3; a = row_t(r) + c * STAGGER
lbl = make_lbl('write (collection)', c, r)
g = make_group(c, r)
g.write(start=a, end=a + ANIM_DUR)
objs += [lbl, g]

canvas.add_objects(*objs)

total_dur = row_t(N_ROWS - 1) + (COLS - 1) * STAGGER + ANIM_DUR + 1.0
if args.verbose:
    canvas.export_video('docs/source/_static/videos/animations_vcollection.mp4',
                        fps=30, end=total_dur)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True,
                           end=total_dur)
