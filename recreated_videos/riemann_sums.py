"""Riemann Sums — visualizing how rectangular approximations converge to the
area under a curve as the number of rectangles increases.

Shows f(x) = 0.5*x^2 + 0.5 on [0, 3] with N = 4, 8, 16, 32 left-endpoint
Riemann rectangles, then the exact shaded area.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/riemann_sums')
canvas.set_background()

# ── Function ─────────────────────────────────────────────────────────
def f(x):
    return 0.5 * x * x + 0.5

X_LO, X_HI = 0, 3

# Exact integral of 0.5*x^2 + 0.5 from 0 to 3:
# = [x^3/6 + 0.5*x] from 0 to 3 = 27/6 + 1.5 = 4.5 + 1.5 = 6.0
EXACT_AREA = 6.0

# ── Axes ─────────────────────────────────────────────────────────────
axes = Axes(x_range=(0, 3.5, 0.5), y_range=(0, 6, 1),
            x=260, y=80, plot_width=1300, plot_height=850,
            show_grid=True, creation=0)
axes.fadein(0, 0.8)

# ── Curve ────────────────────────────────────────────────────────────
curve = axes.plot(f, stroke='#FFFF00', stroke_width=4, x_range=(X_LO, X_HI))
curve.fadein(0.3, 1.0)

# ── Title ────────────────────────────────────────────────────────────
title = Text(text='Riemann Sum Approximation', x=960, y=40,
             font_size=42, fill='#fff', stroke_width=0, text_anchor='middle',
             creation=0)
title.fadein(0, 0.8)

func_label = Text(text='f(x) = 0.5x\u00b2 + 0.5', x=960, y=85,
                  font_size=24, fill='#aaa', stroke_width=0, text_anchor='middle',
                  creation=0)
func_label.fadein(0.3, 1.0)

# ── Helper: compute Riemann sum value ────────────────────────────────
def riemann_sum(n):
    dx = (X_HI - X_LO) / n
    return sum(f(X_LO + i * dx) * dx for i in range(n))

# ── Helper: build Riemann rectangles ─────────────────────────────────
def build_riemann_rects(n, color, creation_time):
    """Build N left-endpoint Riemann rectangles positioned in axes coords."""
    dx = (X_HI - X_LO) / n
    rects = []
    for i in range(n):
        x_left = X_LO + i * dx
        y_val = f(x_left)

        # Convert corners from math coords to SVG pixel coords
        sx_left, sy_top = axes.coords_to_point(x_left, y_val)
        sx_right, sy_bottom = axes.coords_to_point(x_left + dx, 0)

        rect_width = sx_right - sx_left
        rect_height = sy_bottom - sy_top

        rect = Rectangle(
            width=rect_width, height=rect_height,
            x=sx_left, y=sy_top,
            fill=color, fill_opacity=0.5,
            stroke='#fff', stroke_width=1,
            creation=creation_time, z=-1,
        )
        rects.append(rect)
    return rects

# ── Color palette for each N ─────────────────────────────────────────
rect_colors = ['#58C4DD', '#83C167', '#FF79C6', '#BD93F9']
n_values = [4, 8, 16, 32]

# ── Timeline ─────────────────────────────────────────────────────────
# Phase 1 (1.0 - 3.5):  N=4
# Phase 2 (3.5 - 6.0):  N=8
# Phase 3 (6.0 - 8.5):  N=16
# Phase 4 (8.5 - 11.0): N=32
# Phase 5 (11.0 - 12.0): show shaded area
# Phase 6 (12.0 - 14.0): display exact value

phase_starts = [1.0, 3.5, 6.0, 8.5]
phase_ends   = [3.5, 6.0, 8.5, 11.0]

all_rect_groups = []
n_labels = []
area_labels = []

for idx, n in enumerate(n_values):
    t_start = phase_starts[idx]
    t_end = phase_ends[idx]
    color = rect_colors[idx]

    # Build rectangles
    rects = build_riemann_rects(n, color, creation_time=t_start)
    all_rect_groups.append(rects)

    # Fade in rectangles
    fade_in_dur = 0.6
    for rect in rects:
        rect.fadein(t_start, t_start + fade_in_dur)

    # Fade out rectangles before next phase (except last group which fades at area phase)
    if idx < len(n_values) - 1:
        fade_out_start = phase_ends[idx] - 0.5
        fade_out_end = phase_ends[idx]
    else:
        fade_out_start = 10.5
        fade_out_end = 11.0
    for rect in rects:
        rect.fadeout(fade_out_start, fade_out_end)

    # N label
    approx = riemann_sum(n)
    n_label = Text(
        text=f'N = {n}',
        x=1680, y=140,
        font_size=36, fill=color, stroke_width=0, text_anchor='middle',
        creation=t_start,
    )
    n_label.fadein(t_start, t_start + 0.4)
    if idx < len(n_values) - 1:
        n_label.fadeout(phase_ends[idx] - 0.5, phase_ends[idx])
    else:
        n_label.fadeout(10.5, 11.0)
    n_labels.append(n_label)

    # Area approximation label
    area_label = Text(
        text=f'Area \u2248 {approx:.2f}',
        x=1680, y=185,
        font_size=24, fill='#ccc', stroke_width=0, text_anchor='middle',
        creation=t_start,
    )
    area_label.fadein(t_start + 0.3, t_start + 0.7)
    if idx < len(n_values) - 1:
        area_label.fadeout(phase_ends[idx] - 0.5, phase_ends[idx])
    else:
        area_label.fadeout(10.5, 11.0)
    area_labels.append(area_label)

# ── Phase 5: Shaded area under curve ─────────────────────────────────
shaded_area = axes.get_area(f, x_range=(X_LO, X_HI),
                            fill='#FFFF00', fill_opacity=0.3,
                            stroke_width=0, z=-1)
shaded_area.set_opacity(0, start=0)
shaded_area.set_opacity(1, start=11.0, end=11.8)

# ── Phase 6: Exact area text ─────────────────────────────────────────
exact_label = Text(
    text='Exact Area',
    x=1680, y=140,
    font_size=36, fill='#FFFF00', stroke_width=0, text_anchor='middle',
    creation=11.0,
)
exact_label.fadein(11.0, 11.5)

exact_value = Text(
    text=f'= {EXACT_AREA:.2f}',
    x=1680, y=185,
    font_size=28, fill='#fff', stroke_width=0, text_anchor='middle',
    creation=11.5,
)
exact_value.fadein(11.5, 12.0)

convergence_note = Text(
    text='As N \u2192 \u221e, Riemann sum \u2192 exact integral',
    x=960, y=1010,
    font_size=22, fill='#aaa', stroke_width=0, text_anchor='middle',
    creation=12.0,
)
convergence_note.fadein(12.0, 12.8)

# ── Add everything to canvas ─────────────────────────────────────────
canvas.add(axes, curve, title, func_label)

for rects in all_rect_groups:
    canvas.add(*rects)

canvas.add(*n_labels, *area_labels)
canvas.add(shaded_area, exact_label, exact_value, convergence_note)

if not args.no_display:
    canvas.browser_display(start=args.start or 0, end=args.end or 14,
                           fps=args.fps, port=args.port)
