"""Maurer Rose — beautiful geometric patterns from polar curves.

A Maurer rose connects points on a rose curve r = sin(n*theta) at
evenly-spaced angular steps, creating stunning geometric patterns.
"""
from vectormation.objects import *
from vectormation import attributes
import math

canvas = VectorMathAnim()
canvas.set_background()

# ── Parameters ────────────────────────────────────────────────────────
cx, cy = 960, 540
scale = 250  # radius in pixels
n = 6        # rose petals parameter

d = ValueTracker(71)
d.animate_value(29, 6, 8)

# ── Build the Maurer rose path ───────────────────────────────────────
def maurer_rose_path(n_val, d_val, t):
    """Generate SVG path for a Maurer rose."""
    points = []
    progress = min(1, t / 5)  # 5 seconds to draw fully
    n_pts = max(2, int(361 * progress))
    for k in range(n_pts):
        theta = math.radians(k * d_val)
        r = scale * math.sin(n_val * theta)
        x = cx + r * math.cos(theta)
        y = cy + r * math.sin(theta)
        points.append((x, y))
    d = f'M{points[0][0]:.1f},{points[0][1]:.1f}'
    for x, y in points[1:]:
        d += f'L{x:.1f},{y:.1f}'
    d += 'Z'
    return d

# After drawing, morph to a different d value
def _morph_path(t):
    """Transition from d=71 to d=29 between t=6 and t=8."""
    return maurer_rose_path(n, d.value.at_time(t), t)

maurer = Path('', stroke='#58C4DD', stroke_width=1, fill_opacity=0,
              stroke_opacity=0.6, creation=0)
maurer.d.set_onward(0, _morph_path)
maurer.fadein(0, 0.5)

# ── Labels ───────────────────────────────────────────────────────────
title = TexObject(r'Maurer Rose', x=960, y=50, font_size=52,
                  fill='#fff', stroke_width=0, anchor='center', creation=0)
title.fadein(0, 0.5)

params = TexCountAnimation(fmt=r'$r = \sin(n\theta), \quad \mathrm{step} = {:.0f}\degree$', x=960, y=200, text_anchor='middle', value=d, text_mode=True)
params.fadein(0.3, 0.8)


canvas.add(maurer, title, params)

canvas.show(end=10)
