"""Shared constants, direction maps, and standalone helper functions."""
import math

# ── Size constants (converted for 1920x1080 canvas, 1 unit = 135px) ──
UNIT = 135
SMALL_BUFF = 14
MED_SMALL_BUFF = 34
MED_LARGE_BUFF = 68
LARGE_BUFF = 135
DEFAULT_STROKE_WIDTH = 5
DEFAULT_FONT_SIZE = 48
DEFAULT_DOT_RADIUS = 11
DEFAULT_SMALL_DOT_RADIUS = 5
DEFAULT_ARROW_TIP_LENGTH = 47
DEFAULT_ARROW_TIP_WIDTH = 47
DEFAULT_OBJECT_TO_EDGE_BUFF = 68
DEFAULT_OBJECT_TO_OBJECT_BUFF = 34
CHAR_WIDTH_FACTOR = 0.6  # Approximate character width as fraction of font_size
TEXT_Y_OFFSET = 0.35  # Vertical centering offset for text (fraction of font_size)

# Default chart color palette (used by PieChart, BarChart, GanttChart, etc.)
DEFAULT_CHART_COLORS = [
    '#58C4DD', '#83C167', '#FF6B6B', '#FFFF00',
    '#FF79C6', '#B8BB26', '#BD93F9', '#FFB86C',
]

# Canvas dimensions
CANVAS_WIDTH = 1920
CANVAS_HEIGHT = 1080

# Direction constants (pixel vectors)
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)
UL = (-1, -1)
UR = (1, -1)
DL = (-1, 1)
DR = (1, 1)
ORIGIN = (CANVAS_WIDTH // 2, CANVAS_HEIGHT // 2)  # Screen center


def _distance(x1, y1, x2, y2):
    """Euclidean distance between two points."""
    return math.hypot(x2 - x1, y2 - y1)


def _rotate_point(px, py, ox, oy, angle_rad):
    """Rotate point (px,py) around origin (ox,oy) by angle_rad radians."""
    cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
    return (ox + cos_a * (px - ox) - sin_a * (py - oy),
            oy + sin_a * (px - ox) + cos_a * (py - oy))

def _normalize(x, y):
    """Return the unit vector (ux, uy) for vector (x, y). Returns (0, 0) for zero-length vectors."""
    mag = math.hypot(x, y)
    if mag == 0:
        return (0.0, 0.0)
    return (x / mag, y / mag)

def _sample_function(func, x_min, x_max, y_range, num_points, px, py, pw, ph,
                     extra_xs=None):
    """Sample func over [x_min, x_max] and map to SVG coordinates in (px, py, pw, ph)."""
    x_span = x_max - x_min or 1
    xs = [x_min + i * x_span / num_points for i in range(num_points + 1)]
    if extra_xs:
        xs_set = set(xs)
        xs.extend(v for v in extra_xs if v not in xs_set)
        xs.sort()
    ys = [func(xv) for xv in xs]
    if y_range is None:
        finite = [yv for yv in ys if math.isfinite(yv)]
        y_min = min(finite) if finite else -1
        y_max = max(finite) if finite else 1
        if y_min == y_max:
            y_min -= 1; y_max += 1
        pad = (y_max - y_min) * 0.05
        y_min -= pad; y_max += pad
    else:
        y_min, y_max = y_range
    y_span = y_max - y_min or 1
    # Convert to SVG coordinates
    points = []  # (sx, sy) or None for non-finite
    clamped = []
    for xv, yv in zip(xs, ys):
        if math.isfinite(yv):
            sx = px + (xv - x_min) / (x_span or 1) * pw
            sy = py + (1 - (yv - y_min) / y_span) * ph
            points.append((sx, sy))
            clamped.append((sx, max(py, min(py + ph, sy))))
        else:
            points.append(None)
    # Split into in-bounds segments with interpolated boundary crossings
    sy_lo, sy_hi = py, py + ph
    segments = []
    current = []
    prev = None  # (sx, sy) or None
    for pt in points:
        if pt is None:
            if current:
                segments.append(current)
                current = []
            prev = None
            continue
        sx, sy = pt
        in_bounds = sy_lo <= sy <= sy_hi
        if prev is not None:
            psx, psy = prev
            prev_in = sy_lo <= psy <= sy_hi
            if in_bounds and not prev_in:
                # Entry from out of bounds — add interpolated boundary point
                edge = sy_lo if psy < sy_lo else sy_hi
                t = (edge - psy) / (sy - psy) if sy != psy else 0
                current.append((psx + t * (sx - psx), edge))
            elif not in_bounds and prev_in:
                # Exit to out of bounds — add interpolated boundary point
                edge = sy_lo if sy < sy_lo else sy_hi
                t = (edge - psy) / (sy - psy) if sy != psy else 0
                current.append((psx + t * (sx - psx), edge))
                segments.append(current)
                current = []
            elif not in_bounds and not prev_in:
                # Both out — check if line passes through visible area
                crossings = []
                for edge in (sy_lo, sy_hi):
                    if (psy - edge) * (sy - edge) < 0:
                        t = (edge - psy) / (sy - psy)
                        crossings.append((t, psx + t * (sx - psx), edge))
                if len(crossings) == 2:
                    crossings.sort()
                    segments.append([(c[1], c[2]) for c in crossings])
        if in_bounds:
            current.append((sx, sy))
        prev = (sx, sy)
    if current:
        segments.append(current)
    return y_min, y_max, segments, clamped


def _label_text(text, x, y, font_size, creation: float = 0, z: float = 0, **overrides):
    """Create a centered white text label (common pattern in composites)."""
    from vectormation._shapes import Text  # lazy to avoid circular import
    kw = {'fill': '#fff', 'stroke_width': 0} | overrides
    return Text(text=str(text), x=x, y=y + font_size * TEXT_Y_OFFSET,
                font_size=font_size, text_anchor='middle', creation=creation, z=z, **kw)


def _get_arrow():
    """Lazy import of Arrow to avoid circular imports."""
    from vectormation._arrows import Arrow
    return Arrow


def interpolate_value(a, b, alpha):
    """Linearly interpolate between two scalar values."""
    return a + (b - a) * alpha


def smooth_index(lst, real_index):
    """Smoothly index into a list with a float index in [0, 1]."""
    n = len(lst)
    if n == 0:
        raise ValueError('Cannot index into an empty list')
    if n == 1:
        return lst[0]
    scaled = real_index * (n - 1)
    i = int(scaled)
    if i >= n - 1:
        return lst[-1]
    alpha = scaled - i
    a, b = lst[i], lst[i + 1]
    if isinstance(a, (tuple, list)):
        return tuple(ai + (bi - ai) * alpha for ai, bi in zip(a, b))
    return a + (b - a) * alpha


def _circumcenter(p1, p2, p3):
    """Return (cx, cy, r) of the circumscribed circle through three points."""
    ax, ay = p1; bx, by = p2; cx, cy = p3
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    if abs(d) < 1e-10:
        raise ValueError("Points are collinear; no unique circle exists.")
    a2, b2, c2 = ax*ax + ay*ay, bx*bx + by*by, cx*cx + cy*cy
    ux = (a2 * (by - cy) + b2 * (cy - ay) + c2 * (ay - by)) / d
    uy = (a2 * (cx - bx) + b2 * (ax - cx) + c2 * (bx - ax)) / d
    return ux, uy, math.hypot(ax - ux, ay - uy)
