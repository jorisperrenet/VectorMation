"""Mandelbrot Set Zoom — progressive zoom into the seahorse valley.

Renders the Mandelbrot set as a grid of colored rectangles and
smoothly zooms into the seahorse valley region near -0.75 + 0.1i,
revealing the fractal's infinite self-similar detail.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/mandelbrot_zoom')
canvas.set_background()

# ── Constants ────────────────────────────────────────────────────────
T = 12
W, H = 1920, 1080
COLS, ROWS = 96*2, 54*2  # grid resolution
CELL_W = W / COLS
CELL_H = H / ROWS
MAX_ITER = 100

# ── Zoom parameters ──────────────────────────────────────────────────
# Start: full Mandelbrot set view
START_CENTER = (-0.5, 0.0)
START_RADIUS = 1.8  # half-width in complex plane

# Target: seahorse valley
END_CENTER = (-0.7463, 0.1102)
END_RADIUS = 0.005

# ── Color palette ────────────────────────────────────────────────────
def _build_palette(n):
    """Build a smooth cycling palette of n colors (dark blues -> cyans -> yellows -> magentas)."""
    palette = []
    for i in range(n):
        t = i / n
        # Smooth cycling through a pleasant fractal colormap
        r = int(127.5 * (1 + math.cos(2 * math.pi * (t + 0.0))))
        g = int(127.5 * (1 + math.cos(2 * math.pi * (t + 0.33))))
        b = int(127.5 * (1 + math.cos(2 * math.pi * (t + 0.67))))
        palette.append(f'#{r:02x}{g:02x}{b:02x}')
    return palette

PALETTE = _build_palette(256)

def _iter_color(iters, max_iter):
    """Map iteration count to a palette color. Points in the set are black."""
    if iters >= max_iter:
        return '#000000'
    # Smooth coloring using normalized iteration count
    idx = int(iters * 256 / max_iter) % 256
    return PALETTE[idx]

# ── Mandelbrot computation ───────────────────────────────────────────
def _mandelbrot_iter(cx, cy, max_iter):
    """Return iteration count for point c = cx + cy*i."""
    zx, zy = 0.0, 0.0
    for i in range(max_iter):
        zx2 = zx * zx
        zy2 = zy * zy
        if zx2 + zy2 > 4.0:
            # Smooth iteration count for nicer coloring
            return i + 1 - math.log(math.log(max(math.sqrt(zx2 + zy2), 1.001))) / math.log(2)
        zy = 2.0 * zx * zy + cy
        zx = zx2 - zy2 + cx
    return max_iter

# ── View interpolation ──────────────────────────────────────────────
def _get_view(t):
    """Return (center_x, center_y, radius) for the current time.
    Zoom is exponential (linear in log-space) during t in [1, 10]."""
    if t <= 1.0:
        frac = 0.0
    elif t >= 10.0:
        frac = 1.0
    else:
        frac = (t - 1.0) / 9.0
    # Exponential interpolation for radius (linear in log-space)
    log_start = math.log(START_RADIUS)
    log_end = math.log(END_RADIUS)
    radius = math.exp(log_start + frac * (log_end - log_start))
    # Linear interpolation for center
    cx = START_CENTER[0] + frac * (END_CENTER[0] - START_CENTER[0])
    cy = START_CENTER[1] + frac * (END_CENTER[1] - START_CENTER[1])
    return cx, cy, radius

# ── Raw SVG wrapper ──────────────────────────────────────────────────
class _RawSVG:
    """Minimal object with a to_svg(time) method returning pre-built SVG."""
    def __init__(self, svg_str):
        self._svg = svg_str
    def to_svg(self, _time):
        return self._svg
    def path(self, _time):
        return ''
    def bbox(self, _time):
        return (0, 0, W, H)

# ── Render function ──────────────────────────────────────────────────
def _render_mandelbrot(t):
    """Render the Mandelbrot set grid for the current time."""
    cx, cy, radius = _get_view(t)
    aspect = W / H
    x_min = cx - radius * aspect
    x_max = cx + radius * aspect
    y_min = cy - radius
    y_max = cy + radius

    parts = ['<g>']
    cw = CELL_W
    ch = CELL_H
    for row in range(ROWS):
        # Complex y for this row (center of cell)
        iy = y_min + (row + 0.5) * (y_max - y_min) / ROWS
        sy = row * ch
        for col in range(COLS):
            # Complex x for this column (center of cell)
            ix = x_min + (col + 0.5) * (x_max - x_min) / COLS
            sx = col * cw
            iters = _mandelbrot_iter(ix, iy, MAX_ITER)
            color = _iter_color(iters, MAX_ITER)
            parts.append(
                f"<rect x='{sx:.1f}' y='{sy:.1f}' "
                f"width='{cw:.1f}' height='{ch:.1f}' "
                f"fill='{color}' stroke='none'/>"
            )
    parts.append('</g>')
    return _RawSVG('\n'.join(parts))

fractal = DynamicObject(_render_mandelbrot, creation=0)

# ── Title ────────────────────────────────────────────────────────────
title = Text(text='The Mandelbrot Set', x=960, y=55,
             font_size=44, fill='#ffffff', stroke_width=0,
             text_anchor='middle', creation=0)
title.fadein(0, 1)
title.fadeout(2, 3)

subtitle = Text(text='Zooming into the Seahorse Valley', x=960, y=100,
                font_size=24, fill='#cccccc', stroke_width=0,
                text_anchor='middle', creation=0)
subtitle.fadein(0.3, 1.3)
subtitle.fadeout(2.3, 3.3)

# ── Background overlay for title readability ─────────────────────────
title_bg = Rectangle(x=960, y=70, width=520, height=100,
                     fill='#000000', fill_opacity=0.6,
                     stroke_width=0, rx=12, creation=0)
title_bg.fadein(0, 0.5)
title_bg.fadeout(2, 3)

# ── Coordinate labels at the end ─────────────────────────────────────
def _fmt_coord(t):
    """Format current view center as a complex number string."""
    cx, cy, _ = _get_view(t)
    sign = '+' if cy >= 0 else '-'
    return f'c = {cx:.6f} {sign} {abs(cy):.6f}i'

def _fmt_zoom(t):
    """Format current zoom level."""
    _, _, radius = _get_view(t)
    zoom = START_RADIUS / radius
    if zoom >= 1000:
        return f'Zoom: {zoom:.0f}x'
    elif zoom >= 10:
        return f'Zoom: {zoom:.1f}x'
    else:
        return f'Zoom: {zoom:.2f}x'

# Info background
info_bg = Rectangle(x=960, y=1010, width=600, height=80,
                    fill='#000000', fill_opacity=0.7,
                    stroke_width=0, rx=10, creation=10)
info_bg.fadein(10, 10.5)

coord_label = Text(text='', x=960, y=998, font_size=22, fill='#58C4DD',
                   stroke_width=0, text_anchor='middle', creation=10)
coord_label.text.set_onward(10, _fmt_coord)
coord_label.fadein(10, 10.5)

zoom_label = Text(text='', x=960, y=1028, font_size=20, fill='#aaaaaa',
                  stroke_width=0, text_anchor='middle', creation=10)
zoom_label.text.set_onward(10, _fmt_zoom)
zoom_label.fadein(10.2, 10.7)

max_iter_label = Text(text=f'max iterations = {MAX_ITER}', x=960, y=1055,
                      font_size=16, fill='#666666', stroke_width=0,
                      text_anchor='middle', creation=10)
max_iter_label.fadein(10.4, 10.9)

# ── Live zoom indicator (bottom-right) ───────────────────────────────
zoom_live = Text(text='', x=1850, y=1060, font_size=16, fill='#555555',
                 stroke_width=0, text_anchor='end', creation=1)
zoom_live.text.set_onward(1, _fmt_zoom)
zoom_live.fadein(1, 2)
zoom_live.fadeout(9.5, 10)

# ── Assemble ─────────────────────────────────────────────────────────
canvas.add(fractal)
canvas.add(title_bg, title, subtitle)
canvas.add(zoom_live)
canvas.add(info_bg, coord_label, zoom_label, max_iter_label)

canvas.browser_display(start=args.start or 0, end=args.end or T,
                           fps=args.fps, port=args.port)
