"""Convolution of two continuous functions.

Inspired by 3Blue1Brown's video on convolutions. Shows a Gaussian kernel
sliding across a rectangular (box) function, with the overlapping product
area building up the convolution result in real time.
"""
from vectormation.objects import *
import math

canvas = VectorMathAnim()
canvas.set_background()

# ── Math helpers ─────────────────────────────────────────────────────
rect = lambda x: 1.0 if -1 <= x <= 1 else 0.0
gauss = lambda x, mu: math.exp(-0.5 * ((x - mu) / 0.6) ** 2)

def conv(s, n=200):
    lo, hi, step = -3.0, 3.0, 6.0 / n
    return sum((0.5 if i in (0, n) else 1.0) * rect(lo + i * step) * gauss(lo + i * step, s) * step
               for i in range(n + 1))

# ── Sliding parameter s ─────────────────────────────────────────────
s_tracker = ValueTracker(-3.5)
s_tracker.animate_value(3.5, start=2, end=9)
s = lambda t: s_tracker.get_value(t)

# ── Axes ─────────────────────────────────────────────────────────────
axes_top = Axes(x_range=(-4, 4, 1), y_range=(-0.2, 1.4, 0.5),
                x=80, y=90, plot_width=1760, plot_height=380, show_grid=True)
axes_bot = Axes(x_range=(-4, 4, 1), y_range=(-0.2, 1.6, 0.5),
                x=80, y=570, plot_width=1760, plot_height=380, show_grid=True)
axes_top.fadein(0, 0.6)
axes_bot.fadein(0, 0.6)

# ── Curves on top axes ──────────────────────────────────────────────
axes_top.plot(rect, stroke='#58C4DD', stroke_width=4,
              num_points=400, x_range=(-3.5, 3.5)).fadein(0.3, 1)
axes_top.plot(lambda x, t: gauss(x, s(t)), stroke='#83C167', stroke_width=3,
              num_points=200, x_range=(-3.9, 3.9)).fadein(0.6, 1.2)
axes_top.get_area(lambda x, t: rect(x) * gauss(x, s(t)),
                  fill='#FFFF00', fill_opacity=0.35, stroke='#FFFF00',
                  stroke_width=1, stroke_opacity=0.6, z=0.5).fadein(1.5, 2)

# ── Convolution result on bottom axes ────────────────────────────────
axes_bot.animate_draw_function(
    lambda x: conv(x, n=100), start=2, end=9,
    x_range=(-3.5, 3.5), num_points=200,
    stroke='#FC6255', stroke_width=3.5, z=2).fadein(2, 2.5)

tracker_dot = Dot(r=6, fill='#FC6255', z=3)
tracker_dot.c.set_onward(0, lambda t: axes_bot.coords_to_point(s(t), conv(s(t), n=100), t))
tracker_dot.fadein(2, 2.5)
axes_bot.objects.append(tracker_dot)

# ── Vertical guide between axes ──────────────────────────────────────
guide = Line(stroke='#fff', stroke_width=2, stroke_opacity=0.6,
             stroke_dasharray='6 4', z=-1)
guide.p1.set_onward(0, lambda t: (axes_top._math_to_svg_x(s(t), t), axes_top.plot_y))
guide.p2.set_onward(0, lambda t: (axes_bot._math_to_svg_x(s(t), t),
                                   axes_bot.plot_y + axes_bot.plot_height))
guide.fadein(2, 2.5)

# ── Labels ───────────────────────────────────────────────────────────
title = TexObject('Continuous Convolution', x=620, y=8, font_size=44, fill='#fff')
title.fadein(0, 0.5)

s_display = TexCountAnimation(value=s_tracker, fmt='s = {:.2f}', font_size=36,
                              text_anchor='middle')
s_display.fadein(2, 2.5)

# ── Canvas ───────────────────────────────────────────────────────────
canvas.add(axes_top, axes_bot, guide, title, s_display)

canvas.show(end=10)
