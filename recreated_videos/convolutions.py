"""Convolution of two continuous functions.

Inspired by 3Blue1Brown's video on convolutions. Shows a Gaussian kernel
sliding across a rectangular (box) function, with the overlapping product
area building up the convolution result in real time.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/convolutions')
canvas.set_background()

DURATION = 10

# ── Function definitions ─────────────────────────────────────────────
def rect_func(x):
    """Rectangular (box) function: 1 on [-1, 1], 0 elsewhere."""
    return 1.0 if -1.0 <= x <= 1.0 else 0.0

def gaussian(x, mu=0, sigma=0.6):
    """Gaussian bell curve."""
    return math.exp(-0.5 * ((x - mu) / sigma) ** 2)

def shifted_gaussian(x, s):
    """Gaussian centered at s (the sliding parameter)."""
    return gaussian(x, mu=s, sigma=0.6)

def product_func(x, s):
    """Product of rect and shifted Gaussian at point x."""
    return rect_func(x) * shifted_gaussian(x, s)

def convolution_value(s, n=200):
    """Numerical convolution (f * g)(s) via trapezoidal rule over [-3, 3]."""
    lo, hi = -3.0, 3.0
    step = (hi - lo) / n
    total = 0.0
    for i in range(n + 1):
        x = lo + i * step
        val = product_func(x, s)
        weight = 0.5 if (i == 0 or i == n) else 1.0
        total += val * weight * step
    return total

# Precompute the full convolution curve for reference
CONV_X_RANGE = (-4, 4)
CONV_SAMPLES = 300
conv_xs = [CONV_X_RANGE[0] + i * (CONV_X_RANGE[1] - CONV_X_RANGE[0]) / CONV_SAMPLES
           for i in range(CONV_SAMPLES + 1)]
conv_ys = [convolution_value(sx) for sx in conv_xs]
conv_max = max(conv_ys) if conv_ys else 1.0

# ── Axes: top — the two functions and their product ──────────────────
axes_top = Axes(x_range=(-4, 4, 1), y_range=(-0.2, 1.4, 0.5),
                x=80, y=30, plot_width=1760, plot_height=420,
                show_grid=True, creation=0)
axes_top.fadein(0, 0.6)

# ── Axes: bottom — the convolution result ────────────────────────────
axes_bot = Axes(x_range=(-4, 4, 1), y_range=(-0.1, 1.2, 0.5),
                x=80, y=530, plot_width=1760, plot_height=420,
                show_grid=True, creation=0)
axes_bot.fadein(0, 0.6)

# ── Static rectangular function on top axes ──────────────────────────
rect_curve = axes_top.plot(rect_func, stroke='#58C4DD', stroke_width=4,
                           num_points=400, x_range=(-3.5, 3.5))
rect_curve.fadein(0.3, 1.0)

rect_label = Text(text='f(x) = rect(x)', x=1700, y=60,
                  font_size=22, fill='#58C4DD', stroke_width=0,
                  text_anchor='end', creation=0)
rect_label.fadein(0.3, 1.0)

# ── ValueTracker for the sliding parameter s ─────────────────────────
# s goes from -3.5 to 3.5 over the main sweep phase
S_START = -3.5
S_END = 3.5
SWEEP_T0 = 2.0   # time when sweep begins
SWEEP_T1 = 9.0   # time when sweep ends

s_tracker = ValueTracker(S_START)
s_tracker.animate_value(S_END, start=SWEEP_T0, end=SWEEP_T1)

# ── Sliding Gaussian (dynamic) on top axes ───────────────────────────
def build_sliding_gaussian(time):
    """Build the sliding Gaussian curve at current s position."""
    s = s_tracker.get_value(time)
    def g_at_s(x):
        return shifted_gaussian(x, s)
    curve = axes_top.plot(g_at_s, stroke='#83C167', stroke_width=3,
                          num_points=200, x_range=(-3.9, 3.9))
    return curve

sliding_gauss = DynamicObject(build_sliding_gaussian, creation=0, z=1)
sliding_gauss.fadein(0.6, 1.2)

gauss_label = Text(text='g(x) = Gaussian', x=1700, y=90,
                   font_size=22, fill='#83C167', stroke_width=0,
                   text_anchor='end', creation=0)
gauss_label.fadein(0.6, 1.2)

# ── Product shading (dynamic): area of f(x) * g(x-s) ────────────────
def build_product_area(time):
    """Build the shaded area representing f(x) * g(x - s)."""
    s = s_tracker.get_value(time)
    # Only shade where both functions are nonzero: x in [-1, 1] for rect
    lo = max(-1.0, -3.0)
    hi = min(1.0, 3.0)
    n = 120
    step = (hi - lo) / n
    pts_top_list = []
    for i in range(n + 1):
        x = lo + i * step
        yval = product_func(x, s)
        sx = axes_top._math_to_svg_x(x, time)
        sy = axes_top._math_to_svg_y(yval, time)
        # Clamp to plot area
        sy = max(axes_top.plot_y, min(axes_top.plot_y + axes_top.plot_height, sy))
        pts_top_list.append((sx, sy))
    if not pts_top_list:
        return Path('', creation=0, fill_opacity=0)
    # Close the path along the baseline
    baseline_y = axes_top._math_to_svg_y(0, time)
    baseline_y = max(axes_top.plot_y, min(axes_top.plot_y + axes_top.plot_height, baseline_y))
    all_pts = pts_top_list + [(pts_top_list[-1][0], baseline_y),
                               (pts_top_list[0][0], baseline_y)]
    d = 'M' + 'L'.join(f'{px},{py}' for px, py in all_pts) + 'Z'
    return Path(d, creation=0, fill='#FFFF00', fill_opacity=0.35,
                stroke='#FFFF00', stroke_width=1, stroke_opacity=0.6)

product_area = DynamicObject(build_product_area, creation=0, z=0.5)
product_area.fadein(1.5, 2.0)

product_label = Text(text='f(x) \u00b7 g(x \u2212 s)', x=960, y=470,
                     font_size=20, fill='#FFFF00', stroke_width=0,
                     text_anchor='middle', creation=0)
product_label.fadein(1.5, 2.0)

# ── Convolution result curve (progressive, on bottom axes) ───────────
def build_conv_curve(time):
    """Build the convolution result curve up to the current s value."""
    s = s_tracker.get_value(time)
    # Build path from S_START to current s
    pts = []
    n = 200
    s_lo = S_START
    s_hi = s
    if s_hi <= s_lo:
        return Path('', creation=0, fill_opacity=0)
    step = (s_hi - s_lo) / n
    for i in range(n + 1):
        sv = s_lo + i * step
        cv = convolution_value(sv, n=100)
        sx = axes_bot._math_to_svg_x(sv, time)
        sy = axes_bot._math_to_svg_y(cv, time)
        pts.append((sx, sy))
    if not pts:
        return Path('', creation=0, fill_opacity=0)
    d = 'M' + 'L'.join(f'{px},{py}' for px, py in pts)
    return Path(d, creation=0, stroke='#FC6255', stroke_width=3.5,
                fill_opacity=0)

conv_curve = DynamicObject(build_conv_curve, creation=0, z=2)
conv_curve.fadein(2.0, 2.5)

# ── Vertical tracker line on bottom axes ─────────────────────────────
def build_tracker_dot(time):
    """A dot on the convolution curve at the current s value."""
    s = s_tracker.get_value(time)
    cv = convolution_value(s, n=100)
    sx = axes_bot._math_to_svg_x(s, time)
    sy = axes_bot._math_to_svg_y(cv, time)
    return Dot(cx=sx, cy=sy, r=6, fill='#FC6255', creation=0)

tracker_dot = DynamicObject(build_tracker_dot, creation=0, z=3)
tracker_dot.fadein(2.0, 2.5)

# ── Dashed vertical line from top axes to bottom axes at current s ───
def build_vertical_guide(time):
    """Dashed vertical guide at the current s position."""
    s = s_tracker.get_value(time)
    sx_top = axes_top._math_to_svg_x(s, time)
    y_top = axes_top.plot_y
    y_bot = axes_bot.plot_y + axes_bot.plot_height
    return Line(x1=sx_top, y1=y_top, x2=sx_top, y2=y_bot,
                stroke='#ffffff', stroke_width=1, stroke_opacity=0.3,
                stroke_dasharray='6 4', creation=0)

vert_guide = DynamicObject(build_vertical_guide, creation=0, z=-1)
vert_guide.fadein(2.0, 2.5)

# ── Labels ───────────────────────────────────────────────────────────
title = Text(text='Continuous Convolution', x=960, y=30,
             font_size=40, fill='#ffffff', stroke_width=0,
             text_anchor='middle', creation=0)
title.fadein(0, 0.5)

formula = Text(text='(f * g)(s) = \u222b f(x) \u00b7 g(x \u2212 s) dx',
               x=960, y=500,
               font_size=22, fill='#aaa', stroke_width=0,
               text_anchor='middle', creation=0)
formula.fadein(1.0, 1.5)

conv_label = Text(text='(f * g)(s)', x=1700, y=560,
                  font_size=24, fill='#FC6255', stroke_width=0,
                  text_anchor='end', creation=0)
conv_label.fadein(2.0, 2.5)

# ── Dynamic s value display ──────────────────────────────────────────
def build_s_display(time):
    """Show the current value of s."""
    s = s_tracker.get_value(time)
    return Text(text=f's = {s:.2f}', x=160, y=500,
                font_size=22, fill='#ffffff', stroke_width=0,
                text_anchor='start', creation=0)

s_display = DynamicObject(build_s_display, creation=0, z=3)
s_display.fadein(2.0, 2.5)

# ── Add everything to canvas ─────────────────────────────────────────
canvas.add(
    axes_top, axes_bot,
    rect_curve, rect_label,
    sliding_gauss, gauss_label,
    product_area, product_label,
    conv_curve, tracker_dot, vert_guide,
    title, formula, conv_label,
    s_display,
)

if not args.no_display:
    canvas.browser_display(start=args.start or 0, end=args.end or DURATION,
                           fps=args.fps, port=args.port)
