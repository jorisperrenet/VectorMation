"""Maurer Rose — beautiful geometric patterns from polar curves.

A Maurer rose connects points on a rose curve r = sin(n*theta) at
evenly-spaced angular steps, creating stunning geometric patterns.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/maurer_rose')
canvas.set_background()

# ── Parameters ────────────────────────────────────────────────────────
cx, cy = 960, 540
scale = 250  # radius in pixels
n = 6        # rose petals parameter
d = 71       # angular step (degrees) — prime numbers make nice patterns

# ── Build the Maurer rose path ───────────────────────────────────────
def maurer_rose_path(n_val, d_val, n_points=361):
    """Generate SVG path for a Maurer rose."""
    points = []
    for k in range(n_points):
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

# ── Animated drawing ─────────────────────────────────────────────────
# Draw the Maurer rose progressively
def _growing_path(t):
    """Draw more of the path as time progresses."""
    progress = min(1, t / 5)  # 5 seconds to draw fully
    n_pts = max(2, int(361 * progress))
    points = []
    for k in range(n_pts):
        theta = math.radians(k * d)
        r = scale * math.sin(n * theta)
        x = cx + r * math.cos(theta)
        y = cy + r * math.sin(theta)
        points.append((x, y))
    path_d = f'M{points[0][0]:.1f},{points[0][1]:.1f}'
    for x, y in points[1:]:
        path_d += f'L{x:.1f},{y:.1f}'
    return path_d

maurer = Path('', stroke='#58C4DD', stroke_width=1, fill_opacity=0,
              stroke_opacity=0.6, creation=0)
maurer.d.set_onward(0, _growing_path)
maurer.fadein(0, 0.5)

# ── The underlying rose curve ────────────────────────────────────────
def _rose_path(t):
    progress = min(1, t / 5)
    n_pts = max(2, int(500 * progress))
    points = []
    for k in range(n_pts):
        theta = k * 2 * math.pi / 500
        r = scale * math.sin(n * theta)
        x = cx + r * math.cos(theta)
        y = cy + r * math.sin(theta)
        points.append((x, y))
    path_d = f'M{points[0][0]:.1f},{points[0][1]:.1f}'
    for x, y in points[1:]:
        path_d += f'L{x:.1f},{y:.1f}'
    return path_d

rose = Path('', stroke='#FF6B6B', stroke_width=2, fill_opacity=0, creation=0)
rose.d.set_onward(0, _rose_path)

# ── Labels ───────────────────────────────────────────────────────────
title = Text(text='Maurer Rose', x=960, y=50, font_size=42,
             fill='#fff', stroke_width=0, text_anchor='middle', creation=0)
title.fadein(0, 0.5)

params = Text(text=f'n = {n},  d = {d}\u00b0', x=960, y=100,
              font_size=24, fill='#aaa', stroke_width=0,
              text_anchor='middle', creation=0)
params.fadein(0.3, 0.8)

formula = Text(text='r = sin(n\u03b8),  step = d\u00b0',
               x=960, y=1020, font_size=20, fill='#666', stroke_width=0,
               text_anchor='middle', creation=0)
formula.fadein(0.5, 1)

# ── Parameter transition: change d ───────────────────────────────────
# After drawing, morph to a different d value
def _morph_path(t):
    """Transition from d=71 to d=29 between t=6 and t=8."""
    if t < 6:
        d_val = d
    elif t < 8:
        progress = (t - 6) / 2
        d_val = d + (29 - d) * progress
    else:
        d_val = 29
    return maurer_rose_path(n, d_val)

maurer.d.set_onward(5.5, _morph_path)

# Update parameter text
params2 = Text(text=f'n = {n},  d = 29\u00b0', x=960, y=100,
               font_size=24, fill='#aaa', stroke_width=0,
               text_anchor='middle', creation=0)
params2.show.set_onward(0, False)
params2.show.set_onward(6, True)
params2.fadein(6, 6.5)
params.fadeout(5.8, 6.2)

canvas.add(maurer, rose, title, params, params2, formula)

canvas.browser_display(start=args.start or 0, end=args.end or 10,
                           fps=args.fps, port=args.port)
