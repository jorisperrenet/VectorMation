"""Mandelbrot Set Zoom — progressive zoom into the seahorse valley.

Renders the Mandelbrot set on the GPU (numba CUDA) and displays it as
an inline PNG image, smoothly zooming into the seahorse valley region
near -0.75 + 0.1i.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from vectormation.objects import *
import math
import numpy as np
import numba
from numba import cuda
from PIL import Image as PILImage
import io, base64

args = parse_args()

W, H = 960, 540
canvas = VectorMathAnim(verbose=args.verbose, width=W, height=H, save_dir='svgs/mandelbrot_zoom')
canvas.set_background()

# ── Constants ────────────────────────────────────────────────────────
IMG_W, IMG_H = W, H
BASE_ITER = 100

# ── Zoom parameters ──────────────────────────────────────────────────
# Always centered on the seahorse valley — the initial radius is wide
# enough to show the entire set, and we zoom straight in.
CENTER = (-0.7463, 0.1102)
START_RADIUS = 1.5
END_RADIUS = 0.0002

# ── Color palette ────────────────────────────────────────────────────
_STOPS = np.array([
    [  0,   0,   0],  # black
    [  0,   7, 100],  # dark blue
    [ 32, 107, 203],  # medium blue
    [237, 255, 255],  # ice white
    [255, 170,   0],  # gold
    [200,  60,   0],  # dark orange
    [100,   0,  50],  # dark purple
    [  0,  30, 100],  # navy (wraps back)
], dtype=np.float64)

def _build_palette(n):
    """Interpolate smoothly through the color stops."""
    pal = np.zeros((n, 3), dtype=np.uint8)
    ns = len(_STOPS)
    for i in range(n):
        t = (i / n) * ns
        idx = int(t) % ns
        frac = t - int(t)
        c = _STOPS[idx] + frac * (_STOPS[(idx + 1) % ns] - _STOPS[idx])
        pal[i] = np.clip(c, 0, 255).astype(np.uint8)
    return pal

_PALETTE_RGB = _build_palette(512)

def _get_max_iter(radius):
    """Scale max iterations with zoom depth so deep zooms stay detailed."""
    zoom = START_RADIUS / radius
    return int(BASE_ITER + 200 * math.log(max(zoom, 1)))

# ── CUDA kernel (float32, outputs packed RGB as uint32) ──────────────
@cuda.jit
def _mandelbrot_kernel(cx_arr, cy_arr, max_iter, palette, n_colors, packed):
    col, row = cuda.grid(2)
    if row >= packed.shape[0] or col >= packed.shape[1]:
        return
    cx = cx_arr[col]
    cy = cy_arr[row]
    zx = numba.float32(0.0)
    zy = numba.float32(0.0)
    for i in range(max_iter):
        zx2 = zx * zx
        zy2 = zy * zy
        if zx2 + zy2 > numba.float32(4.0):
            log_zn = math.log(max(float(zx2 + zy2), 1.001)) * 0.5
            iters = i + 1 - math.log(max(log_zn, 1e-10)) / math.log(2.0)
            idx = int(math.log(iters + 1.0) * (n_colors / 3.5)) % n_colors
            packed[row, col] = palette[idx]
            return
        zy = numba.float32(2.0) * zx * zy + cy
        zx = zx2 - zy2 + cx
    packed[row, col] = 0

# Build packed uint32 palette (0x00RRGGBB)
_PALETTE_PACKED = (
    _PALETTE_RGB[:, 0].astype(np.uint32) << 16 |
    _PALETTE_RGB[:, 1].astype(np.uint32) << 8 |
    _PALETTE_RGB[:, 2].astype(np.uint32)
)

# Pre-allocate device arrays
_d_cx = cuda.device_array(IMG_W, dtype=np.float32)
_d_cy = cuda.device_array(IMG_H, dtype=np.float32)
_d_packed = cuda.device_array((IMG_H, IMG_W), dtype=np.uint32)
_d_palette = cuda.to_device(_PALETTE_PACKED)

_TPB = (16, 16)
_BPG = ((IMG_W + 15) // 16, (IMG_H + 15) // 16)
_N_COLORS = len(_PALETTE_RGB)

def _compute_mandelbrot(cx_arr, cy_arr, max_iter):
    """Run Mandelbrot on GPU, return RGB pixels."""
    _d_cx.copy_to_device(cx_arr)
    _d_cy.copy_to_device(cy_arr)
    _mandelbrot_kernel[_BPG, _TPB](_d_cx, _d_cy, max_iter, _d_palette, _N_COLORS, _d_packed)
    packed = _d_packed.copy_to_host()
    # Unpack uint32 → (H, W, 3) uint8
    pixels = np.empty((IMG_H, IMG_W, 3), dtype=np.uint8)
    pixels[:, :, 0] = (packed >> 16) & 0xFF
    pixels[:, :, 1] = (packed >> 8) & 0xFF
    pixels[:, :, 2] = packed & 0xFF
    return pixels

# ── View ─────────────────────────────────────────────────────────────
ZOOM_START, ZOOM_END = 2, 16  # zoom active during this time window

def _get_radius(t):
    """Exponential zoom from START_RADIUS to END_RADIUS during t in [ZOOM_START, ZOOM_END]."""
    if t <= ZOOM_START:
        frac = 0.0
    elif t >= ZOOM_END:
        frac = 1.0
    else:
        frac = (t - ZOOM_START) / (ZOOM_END - ZOOM_START)
    log_start = math.log(START_RADIUS)
    log_end = math.log(END_RADIUS)
    return math.exp(log_start + frac * (log_end - log_start))

# ── Render to inline PNG ─────────────────────────────────────────────
def _mandelbrot_href(t):
    """Return a data-URI PNG of the Mandelbrot set at time t."""
    radius = _get_radius(t)
    max_iter = _get_max_iter(radius)
    aspect = W / H
    cx, cy = CENTER
    x_min = cx - radius * aspect
    x_max = cx + radius * aspect
    y_min = cy - radius
    y_max = cy + radius

    cx_arr = (np.linspace(x_min, x_max, IMG_W, endpoint=False) + 0.5 * (x_max - x_min) / IMG_W).astype(np.float32)
    cy_arr = (np.linspace(y_min, y_max, IMG_H, endpoint=False) + 0.5 * (y_max - y_min) / IMG_H).astype(np.float32)

    pixels = _compute_mandelbrot(cx_arr, cy_arr, max_iter)

    # Encode as JPEG data URI
    img = PILImage.fromarray(pixels, 'RGB')
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=85)
    b64 = base64.b64encode(buf.getvalue()).decode('ascii')
    return f'data:image/jpeg;base64,{b64}'

fractal = Image(href=_mandelbrot_href, x=0, y=0, width=W, height=H, creation=0)

# ── Title ────────────────────────────────────────────────────────────
title = Text(text='The Mandelbrot Set', x=W//2, y=30,
             font_size=24, fill='#ffffff', stroke_width=0,
             text_anchor='middle', creation=0)
subtitle = Text(text='Zooming into the Seahorse Valley', x=W//2, y=50,
                font_size=13, fill='#cccccc', stroke_width=0,
                text_anchor='middle', creation=0)
title_group = VCollection(title, subtitle)
title_bg = SurroundingRectangle(title_group, buff=20, corner_radius=14,
                                fill='#000000', fill_opacity=0.85,
                                stroke_width=0, creation=0)
title_bg.fadein(0, 0.5)
title_bg.fadeout(3, 4)
title.fadein(0, 1)
title.fadeout(3, 4)
subtitle.fadein(0.3, 1.3)
subtitle.fadeout(3.3, 4.3)

# ── Live zoom indicator (bottom-right) ───────────────────────────────
def _fmt_zoom(t):
    radius = _get_radius(t)
    zoom = START_RADIUS / radius
    if zoom >= 1000:
        return f'{zoom:,.0f}x'
    elif zoom >= 10:
        return f'{zoom:.1f}x'
    else:
        return f'{zoom:.2f}x'

zoom_live = Text(text='', x=910, y=525, font_size=20, fill='#ffffff',
                 stroke_width=0, text_anchor='middle', creation=ZOOM_START)
zoom_live.text.set_onward(ZOOM_START, _fmt_zoom)
zoom_bg = SurroundingRectangle(zoom_live, buff=12, corner_radius=8,
                                fill='#000000', fill_opacity=0.85,
                                stroke_width=0, creation=ZOOM_START)
zoom_bg.fadein(ZOOM_START, ZOOM_START + 1)
zoom_bg.fadeout(ZOOM_END - 0.5, ZOOM_END)
zoom_live.fadein(ZOOM_START, ZOOM_START + 1)
zoom_live.fadeout(ZOOM_END - 0.5, ZOOM_END)

# ── Info panel at the end ────────────────────────────────────────────
INFO_START = ZOOM_END  # appears after zoom completes

def _fmt_coord(t):
    cx, cy = CENTER
    sign = '+' if cy >= 0 else '-'
    return f'c = {cx:.6f} {sign} {abs(cy):.6f}i'

def _fmt_max_iter(t):
    radius = _get_radius(t)
    return f'max iterations = {_get_max_iter(radius)}'

coord_label = Text(text='', x=W//2, y=985//2, font_size=13, fill='#58C4DD',
                   stroke_width=0, text_anchor='middle', creation=INFO_START)
coord_label.text.set_onward(INFO_START, _fmt_coord)
zoom_label = Text(text='', x=W//2, y=1018//2, font_size=11, fill='#ffffff',
                  stroke_width=0, text_anchor='middle', creation=INFO_START)
zoom_label.text.set_onward(INFO_START, lambda t: f'Zoom: {_fmt_zoom(t)}')
max_iter_label = Text(text='', x=W//2, y=1048//2,
                      font_size=9, fill='#999999', stroke_width=0,
                      text_anchor='middle', creation=INFO_START)
max_iter_label.text.set_onward(INFO_START, _fmt_max_iter)

info_group = VCollection(coord_label, zoom_label, max_iter_label)
info_bg = SurroundingRectangle(info_group, buff=18, corner_radius=12,
                                fill='#000000', fill_opacity=0.85,
                                stroke_width=0, creation=INFO_START)
info_bg.fadein(INFO_START, INFO_START + 0.5)
coord_label.fadein(INFO_START, INFO_START + 0.5)
zoom_label.fadein(INFO_START + 0.2, INFO_START + 0.7)
max_iter_label.fadein(INFO_START + 0.4, INFO_START + 0.9)

# ── Assemble ─────────────────────────────────────────────────────────
canvas.add(fractal)
canvas.add(title_bg, title, subtitle)
canvas.add(zoom_bg, zoom_live)
canvas.add(info_bg, coord_label, zoom_label, max_iter_label)

if args.for_docs:
    canvas.export_video('docs/source/_static/videos/mandelbrot_zoom.mp4', fps=30)
if not args.for_docs:
    canvas.browser_display(start=args.start, end=args.end, fps=args.fps, port=args.port)
