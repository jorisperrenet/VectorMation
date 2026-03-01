"""Helper functions shared by _base.py and _base_effects.py."""
import math
from typing import Any

import vectormation.easings as easings
import vectormation.morphing as morphing
from vectormation._constants import (
    CANVAS_WIDTH, CANVAS_HEIGHT, ORIGIN,
    UP, DOWN, LEFT, RIGHT, UL, UR, DL, DR,
    DEFAULT_OBJECT_TO_EDGE_BUFF,
)

def _clamp01(x):
    """Clamp *x* to [0, 1]."""
    return max(0.0, min(1.0, x))

def _lerp(start, dur, a, b, easing):
    """Return a lambda that interpolates from *a* to *b* over [start, start+dur]."""
    return lambda t, _s=start, _d=dur, _a=a, _b=b, _e=easing: _a + (_b - _a) * _e((t - _s) / _d)


def _ramp(start, dur, val, easing):
    """Return a lambda that ramps from 0 to *val* over [start, start+dur]."""
    return lambda t, _s=start, _d=dur, _v=val, _e=easing: _v * _e((t - _s) / _d)


def _ramp_down(start, dur, val, easing):
    """Return a lambda that ramps from *val* to 0 over [start, start+dur]."""
    return lambda t, _s=start, _d=dur, _v=val, _e=easing: _v * (1 - _e((t - _s) / _d))


def _lerp_point(start, dur, a, b, easing):
    """Return a lambda that interpolates 2D points from *a* to *b* over [start, start+dur]."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    def _fn(t, _s=start, _d=dur, _a=a, _dx=dx, _dy=dy, _e=easing):
        p = _e((t - _s) / _d)
        return (_a[0] + _dx * p, _a[1] + _dy * p)
    return _fn


def _clip_reveal(tmpl, start, dur, easing):
    """Return a clip-path function that reveals (100% clipped → 0%) over [start, start+dur]."""
    return lambda t, _s=start, _d=dur, _tmpl=tmpl, _e=easing: _tmpl(100 * (1 - _e((t - _s) / _d)))


def _clip_hide(tmpl, start, dur, easing):
    """Return a clip-path function that hides (0% clipped → 100%) over [start, start+dur]."""
    return lambda t, _s=start, _d=dur, _tmpl=tmpl, _e=easing: _tmpl(100 * _e((t - _s) / _d))


def _norm_dir(direction, default='right'):
    """Convert a tuple direction constant to its string name."""
    return _DIR_NAMES.get(direction, default) if isinstance(direction, tuple) else direction


def _norm_edge(edge, default='bottom'):
    """Convert a tuple edge constant to its string name."""
    return _EDGE_NAMES.get(edge, default) if isinstance(edge, tuple) else edge


def _coords_of(obj, time: float = 0):
    """Extract (x, y) from an object's center or a raw (x, y) tuple."""
    if hasattr(obj, 'center'):
        return obj.center(time)
    if hasattr(obj, 'get_center'):
        return obj.get_center(time)
    return obj


def _set_attr(attr, start, end, value, easing):
    """Set attr instantly (end=None) or animate to value."""
    if end is None:
        attr.set_onward(start, value)
    else:
        attr.move_to(start, end, value, easing=easing)


def _wrap_to_svg(obj, wrapper_fn, start=0):
    """Replace *obj.to_svg* with a version that wraps output via *wrapper_fn(inner, time)* from *start* onward."""
    _orig = obj.to_svg
    def _wrapped(time, _orig=_orig, _fn=wrapper_fn, _s=start):
        inner = _orig(time)
        return _fn(inner, time) if time >= _s else inner
    obj.to_svg = _wrapped  # type: ignore[assignment]


def _parse_path(d) -> tuple[Any, float]:
    """Lazy-import svgpathtools and parse an SVG path string, returning (parsed, total_length)."""
    import svgpathtools
    parsed = svgpathtools.parse_path(d)
    return parsed, parsed.length()  # type: ignore[return-value]


def _path_prefix(path, t):
    """Return the first t-fraction (0-1) of a morphing.Path by arc length."""
    length_to_keep = t * path.length()
    segs, idx = [], 0
    while length_to_keep > 0 and idx < len(path):
        s = path[idx]
        l = s.length()
        if l <= length_to_keep:
            segs.append(s)
            length_to_keep -= l
        else:
            segs.append(s.split(length_to_keep / l)[0])
            length_to_keep = 0
        idx += 1
    return morphing.Path(*segs)


# Map direction tuples to string names
_DIR_NAMES = {RIGHT: 'right', LEFT: 'left', DOWN: 'down', UP: 'up',
              UR: 'right', UL: 'left', DR: 'down', DL: 'down'}
_EDGE_NAMES = {LEFT: 'left', RIGHT: 'right', UP: 'top', DOWN: 'bottom',
               UL: 'left', DL: 'left', UR: 'right', DR: 'right'}


def _make_brect(bbox_func, time, rx, ry, buff, follow, **bbox_kw):
    """Create a bounding rectangle for any object with a bbox method."""
    from vectormation._shapes import Rectangle  # lazy to avoid circular import
    if not follow:
        x, y, w, h = bbox_func(time, **bbox_kw)
        return Rectangle(w+2*buff, h+2*buff, x-buff, y-buff, rx=rx, ry=ry, creation=time,
                         fill_opacity=0, stroke_opacity=1, stroke='#ff0', stroke_width=2)
    rect = Rectangle(width=0, height=0, rx=rx, ry=ry, creation=time,
                     fill_opacity=0, stroke_opacity=1, stroke='#ff0', stroke_width=2)
    from vectormation._shapes import _make_time_cache
    _bbox = _make_time_cache(lambda t: bbox_func(t, **bbox_kw))
    rect.x.set_onward(time, lambda t: _bbox(t)[0] - buff)
    rect.y.set_onward(time, lambda t: _bbox(t)[1] - buff)
    rect.width.set_onward(time, lambda t: _bbox(t)[2] + 2*buff)
    rect.height.set_onward(time, lambda t: _bbox(t)[3] + 2*buff)
    return rect

def _to_edge_impl(obj, edge, buff, start, end, easing):
    """Shared to_edge logic for VObject and VCollection."""
    edge = _norm_edge(edge)
    _, _, w, h = obj.bbox(start)
    cx, cy = obj.center(start)
    targets = {'bottom': (cx, CANVAS_HEIGHT - buff - h / 2), 'top': (cx, buff + h / 2),
               'left': (buff + w / 2, cy), 'right': (CANVAS_WIDTH - buff - w / 2, cy)}
    tx, ty = targets.get(edge, (cx, cy))
    return obj.center_to_pos(posx=tx, posy=ty, start=start,
                             end=end, easing=easing)


_CORNER_MAP = {UL: 'top_left', UR: 'top_right', DL: 'bottom_left', DR: 'bottom_right'}

_EDGE_POINTS = {
    'center': lambda x, y, w, h: (x + w / 2, y + h / 2),
    'top': lambda x, y, w, h: (x + w / 2, y),
    'bottom': lambda x, y, w, h: (x + w / 2, y + h),
    'left': lambda x, y, w, h: (x, y + h / 2),
    'right': lambda x, y, w, h: (x + w, y + h / 2),
    'top_left': lambda x, y, w, h: (x, y),
    'top_right': lambda x, y, w, h: (x + w, y),
    'bottom_left': lambda x, y, w, h: (x, y + h),
    'bottom_right': lambda x, y, w, h: (x + w, y + h),
}

def _get_edge_impl(bbox_func, edge, time):
    """Shared get_edge for VObject and VCollection."""
    x, y, w, h = bbox_func(time)
    return _EDGE_POINTS[edge](x, y, w, h)

def _to_corner_impl(obj, corner, buff, start, end, easing):
    """Shared to_corner logic for VObject and VCollection."""
    if isinstance(corner, tuple):
        corner = _CORNER_MAP.get(corner, 'bottom_right')
    _, _, w, h = obj.bbox(start)
    tx = buff + w / 2 if 'left' in corner else CANVAS_WIDTH - buff - w / 2
    ty = buff + h / 2 if 'top' in corner else CANVAS_HEIGHT - buff - h / 2
    return obj.center_to_pos(posx=tx, posy=ty, start=start,
                             end=end, easing=easing)


class _BBoxMethodsMixin:
    """Mixin providing bbox-derived measurement and positioning methods.

    Requires subclasses to define ``bbox(time)`` and ``center_to_pos()``.
    Eliminates duplication between VObject and VCollection.
    """

    def center(self, time: float = 0):
        """Return (cx, cy) of the bounding box at the given time."""
        x, y, w, h = self.bbox(time)
        return (x + w / 2, y + h / 2)

    get_center = center

    def get_width(self, time: float = 0):
        """Return the bounding box width."""
        return self.bbox(time)[2]

    def get_height(self, time: float = 0):
        """Return the bounding box height."""
        return self.bbox(time)[3]

    def get_x(self, time: float = 0):
        """Return x-coordinate of the bounding box center."""
        return self.center(time)[0]

    def get_y(self, time: float = 0):
        """Return y-coordinate of the bounding box center."""
        return self.center(time)[1]

    def get_diagonal(self, time: float = 0):
        """Return the diagonal length of the bounding box."""
        _, _, w, h = self.bbox(time)
        return math.hypot(w, h)

    def get_aspect_ratio(self, time: float = 0):
        """Return width/height ratio of the bounding box."""
        _, _, w, h = self.bbox(time)
        return w / h if h != 0 else math.inf

    def distance_to(self, other, time: float = 0):
        """Return the distance between centers."""
        x1, y1 = self.center(time)
        x2, y2 = other.center(time)
        return math.hypot(x2 - x1, y2 - y1)

    def is_overlapping(self, other, time: float = 0):
        """Return True if bounding boxes overlap."""
        x1, y1, w1, h1 = self.bbox(time)
        x2, y2, w2, h2 = other.bbox(time)
        return not (x1 + w1 < x2 or x2 + w2 < x1 or y1 + h1 < y2 or y2 + h2 < y1)

    def get_edge(self, edge, time: float = 0):
        """Return coordinate of a named edge point."""
        return _get_edge_impl(self.bbox, edge, time)

    def get_left(self, time: float = 0): return self.get_edge('left', time)
    def get_right(self, time: float = 0): return self.get_edge('right', time)
    def get_top(self, time: float = 0): return self.get_edge('top', time)
    def get_bottom(self, time: float = 0): return self.get_edge('bottom', time)

    def move_to(self, x, y, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Move the object's center to (x, y), optionally animated over [start, end]."""
        xmin, ymin, w, h = self.bbox(start)
        self.shift(dx=x - (xmin + w / 2), dy=y - (ymin + h / 2),
                   start=start, end=end, easing=easing)
        return self

    def center_to_pos(self, posx: float = ORIGIN[0], posy: float = ORIGIN[1],
                      start: float = 0, end: float | None = None, easing=easings.smooth):
        """Shift the center to (posx, posy), animated from start to end."""
        return self.move_to(posx, posy, start, end, easing)

    def to_edge(self, edge=DOWN, buff=DEFAULT_OBJECT_TO_EDGE_BUFF,
                start: float = 0, end=None, easing=easings.smooth):
        """Move to a canvas edge."""
        return _to_edge_impl(self, edge, buff, start, end, easing)

    def to_corner(self, corner=DR, buff=DEFAULT_OBJECT_TO_EDGE_BUFF,
                  start: float = 0, end=None, easing=easings.smooth):
        """Move to a canvas corner."""
        return _to_corner_impl(self, corner, buff, start, end, easing)


