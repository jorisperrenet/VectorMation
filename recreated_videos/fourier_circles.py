"""Fourier Circles — epicycles tracing complex shapes.

Demonstrates Fourier series approximation using rotating circles (epicycles).
Starts with a single circle (fundamental frequency) and progressively adds
harmonics. The tip of the last circle traces out a square-wave-like path.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/fourier_circles')
canvas.set_background(fill='#1a1a2e')

# ── Fourier coefficients for a square wave ───────────────────────────
# Square wave: f(t) = sum_{k odd} (4 / (pi*k)) * sin(k*t)
# Each term k gives an epicycle with radius 4/(pi*k) rotating at frequency k.

MAX_HARMONICS = 15  # up to 15 odd harmonics (k = 1, 3, 5, ..., 29)
BASE_FREQ = 1.0     # fundamental angular frequency (rad/s of animation)
AMPLITUDE = 180     # pixel scale for radius of fundamental circle

def fourier_coeffs(n_terms):
    """Return list of (frequency_multiplier, radius) for the first n_terms odd harmonics."""
    coeffs = []
    for i in range(n_terms):
        k = 2 * i + 1  # 1, 3, 5, 7, ...
        r = AMPLITUDE * 4 / (math.pi * k)
        coeffs.append((k, r))
    return coeffs

# ── Layout ───────────────────────────────────────────────────────────
EPICYCLE_CX = 580    # center of the epicycle system
EPICYCLE_CY = 540
TRACE_X_START = 960  # where the traced waveform begins (to the right)

# ── Color palette ────────────────────────────────────────────────────
CIRCLE_COLORS = [
    '#58C4DD', '#83C167', '#FFFF00', '#FF6B6B', '#FC6255',
    '#9B59B6', '#E67E22', '#1ABC9C', '#3498DB', '#E74C3C',
    '#2ECC71', '#F39C12', '#8E44AD', '#16A085', '#D35400',
]

# ── Timing ───────────────────────────────────────────────────────────
# Phase 1 (0-2s):   1 harmonic, draw for 2 full cycles
# Phase 2 (2-4s):   2 harmonics
# Phase 3 (4-6s):   3 harmonics
# Phase 4 (6-8s):   5 harmonics
# Phase 5 (8-10s):  8 harmonics
# Phase 6 (10-14s): 15 harmonics (full detail)
TOTAL_DURATION = 16
PHASE_SCHEDULE = [
    (0.0,  2.0,  1),
    (2.0,  4.0,  2),
    (4.0,  6.0,  3),
    (6.0,  8.0,  5),
    (8.0,  10.0, 8),
    (10.0, 16.0, MAX_HARMONICS),
]

def n_harmonics_at(t):
    """Return the number of harmonics active at time t."""
    for start, end, n in PHASE_SCHEDULE:
        if t < end:
            return n
    return MAX_HARMONICS

# ── Epicycle computation ─────────────────────────────────────────────
def compute_epicycles(t, n_terms):
    """Compute positions of all epicycle centers and the tip point.
    Returns list of (cx, cy, radius) for each circle, plus the tip (x, y)."""
    coeffs = fourier_coeffs(n_terms)
    # Angular speed: the animation completes one full cycle every 2 seconds
    omega = 2 * math.pi / 2.0  # one full revolution in 2s
    cx, cy = EPICYCLE_CX, EPICYCLE_CY
    circles = []
    for k, r in coeffs:
        angle = k * omega * t
        nx = cx + r * math.cos(angle)
        # SVG y is inverted: subtract sin for standard math orientation
        ny = cy - r * math.sin(angle)
        circles.append((cx, cy, r, nx, ny))
        cx, cy = nx, ny
    tip_x, tip_y = cx, cy
    return circles, tip_x, tip_y

# ── DynamicObject: epicycle circles and radii lines ──────────────────
def build_epicycles(time):
    """Build the visual epicycle system for the current frame."""
    n = n_harmonics_at(time)
    circles_data, tip_x, tip_y = compute_epicycles(time, n)

    parts = []
    for i, (cx, cy, r, nx, ny) in enumerate(circles_data):
        color = CIRCLE_COLORS[i % len(CIRCLE_COLORS)]
        # The circle (orbit path)
        orbit = Circle(r=r, cx=cx, cy=cy,
                       stroke=color, stroke_width=1.5, stroke_opacity=0.35,
                       fill_opacity=0, creation=0)
        # Radius line from center to point on circle
        line = Line(x1=cx, y1=cy, x2=nx, y2=ny,
                    stroke=color, stroke_width=2, stroke_opacity=0.7, creation=0)
        # Small dot at the connection point
        dot = Dot(r=3, cx=nx, cy=ny, fill=color, stroke_width=0, creation=0)
        parts.extend([orbit, line, dot])

    # Tip dot (bright white)
    tip_dot = Dot(r=5, cx=tip_x, cy=tip_y, fill='#fff', stroke_width=0, creation=0)
    parts.append(tip_dot)

    # Horizontal connecting line from tip to the waveform area
    conn_line = Line(x1=tip_x, y1=tip_y, x2=TRACE_X_START, y2=tip_y,
                     stroke='#ffffff', stroke_width=1, stroke_opacity=0.25,
                     stroke_dasharray='4 4', creation=0)
    parts.append(conn_line)

    return VCollection(*parts, creation=0)

epicycles_dynamic = DynamicObject(build_epicycles, creation=0, z=1)

# ── Traced waveform (the output curve scrolling to the right) ────────
# We build a scrolling waveform: at time t, the tip y-value is plotted
# at x=TRACE_X_START, and older values scroll to the right.
TRACE_WIDTH = 880   # pixels of trace area
TRACE_SAMPLES = 500

def build_trace_path(time):
    """Build the SVG path 'd' string for the traced waveform."""
    if time < 0.05:
        return ''
    n = n_harmonics_at(time)
    dt = 0.02  # sample interval in seconds
    # How many samples to look back
    n_samples = min(TRACE_SAMPLES, int(time / dt))
    if n_samples < 2:
        return ''

    parts = []
    for i in range(n_samples):
        # Sample from recent past to now
        sample_t = time - (n_samples - 1 - i) * dt
        if sample_t < 0:
            continue
        n_at = n_harmonics_at(sample_t)
        _, _, tip_y = compute_epicycles(sample_t, n_at)
        # x position: most recent at TRACE_X_START, older points scroll right
        x = TRACE_X_START + (i / (n_samples - 1)) * TRACE_WIDTH
        y = tip_y
        cmd = 'M' if len(parts) == 0 else 'L'
        parts.append(f'{cmd}{x:.1f} {y:.1f}')

    return ' '.join(parts)

trace_path = Path('', stroke='#58C4DD', stroke_width=2.5, stroke_opacity=0.9,
                  fill_opacity=0, creation=0, z=0.5)
trace_path.d.set_onward(0, build_trace_path)

# ── Traced shape on the epicycle side (closed loop trail) ────────────
TRAIL_SAMPLES = 300
TRAIL_DURATION = 2.0  # show last 2 seconds of trail (one full period)

def build_trail_path(time):
    """Build a trailing path showing the shape traced by the epicycles."""
    if time < 0.1:
        return ''
    n = n_harmonics_at(time)
    dt = TRAIL_DURATION / TRAIL_SAMPLES
    # Look back up to TRAIL_DURATION seconds
    look_back = min(time, TRAIL_DURATION)
    n_pts = max(2, int(look_back / dt))

    parts = []
    for i in range(n_pts):
        sample_t = time - look_back + i * dt
        if sample_t < 0:
            continue
        n_at = n_harmonics_at(sample_t)
        _, tip_x, tip_y = compute_epicycles(sample_t, n_at)
        cmd = 'M' if len(parts) == 0 else 'L'
        parts.append(f'{cmd}{tip_x:.1f} {tip_y:.1f}')

    return ' '.join(parts)

trail_path = Path('', stroke='#FF6B6B', stroke_width=1.5, stroke_opacity=0.5,
                  fill_opacity=0, creation=0, z=0.3)
trail_path.d.set_onward(0, build_trail_path)

# ── Harmonic counter label ───────────────────────────────────────────
# Use DynamicObject to show changing text
def build_harmonic_label(time):
    n = n_harmonics_at(time)
    max_k = 2 * n - 1  # highest odd harmonic
    txt = Text(text=f'Harmonics: {n}  (k up to {max_k})',
               x=960, y=60, font_size=28, fill='#ffffff',
               stroke_width=0, text_anchor='middle', creation=0)
    return txt

harmonic_label = DynamicObject(build_harmonic_label, creation=0, z=2)

# ── Title ────────────────────────────────────────────────────────────
title = Text(text='Fourier Epicycles', x=960, y=1030, font_size=40,
             fill='#ffffff', stroke_width=0, text_anchor='middle', creation=0)
title.fadein(0, 1)

subtitle = Text(text='Approximating a square wave with rotating circles',
                x=960, y=1060, font_size=18, fill='#888888', stroke_width=0,
                text_anchor='middle', creation=0)
subtitle.fadein(0.3, 1.3)

# ── Formula ──────────────────────────────────────────────────────────
formula = Text(text='f(t) = \u03a3 (4/\u03c0k) sin(k\u03c9t),  k = 1, 3, 5, ...',
               x=960, y=100, font_size=20, fill='#aaaaaa', stroke_width=0,
               text_anchor='middle', creation=0)
formula.fadein(0.5, 1.5)

# ── Phase transition labels ─────────────────────────────────────────
phase_labels = []
for start, end, n in PHASE_SCHEDULE:
    max_k = 2 * n - 1
    if n == 1:
        desc = 'Fundamental only'
    elif n <= 3:
        desc = f'{n} circles'
    else:
        desc = f'{n} circles (k=1..{max_k})'
    lbl = Text(text=desc, x=EPICYCLE_CX, y=EPICYCLE_CY + 280,
               font_size=20, fill='#666666', stroke_width=0,
               text_anchor='middle', creation=0)
    lbl._show_from(start)
    if end < TOTAL_DURATION:
        lbl._hide_from(end)
    lbl.fadein(start, start + 0.3)
    if end < TOTAL_DURATION:
        lbl.fadeout(end - 0.3, end)
    phase_labels.append(lbl)

# ── Legend for the waveform trace ────────────────────────────────────
wave_label = Text(text='Output waveform \u2192', x=TRACE_X_START + 10, y=180,
                  font_size=16, fill='#58C4DD', stroke_width=0,
                  text_anchor='start', creation=0)
wave_label.fadein(0.5, 1.5)

circle_label = Text(text='Epicycle trail', x=EPICYCLE_CX - 100, y=180,
                    font_size=16, fill='#FF6B6B', stroke_width=0,
                    text_anchor='start', creation=0)
circle_label.fadein(0.5, 1.5)

# ── Vertical separator line ─────────────────────────────────────────
separator = Line(x1=TRACE_X_START, y1=150, x2=TRACE_X_START, y2=930,
                 stroke='#333355', stroke_width=1, stroke_dasharray='6 4',
                 creation=0)
separator.fadein(0, 0.5)

# ── Assemble ─────────────────────────────────────────────────────────
canvas.add(separator, trail_path, trace_path, epicycles_dynamic, harmonic_label)
canvas.add(title, subtitle, formula, wave_label, circle_label)
canvas.add(*phase_labels)

canvas.browser_display(start=args.start or 0, end=args.end or TOTAL_DURATION,
                           fps=args.fps, port=args.port)
