"""Helper functions shared by _base.py and _base_effects.py."""
import math
from copy import deepcopy

import vectormation.easings as easings
import vectormation.attributes as attributes
import vectormation.morphing as morphing
from vectormation._constants import (
    CANVAS_WIDTH, CANVAS_HEIGHT,
    UP, DOWN, LEFT, RIGHT, UL, UR, DL, DR,
    SMALL_BUFF, MED_SMALL_BUFF,
)

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
    return lambda t, _s=start, _d=dur, _a=a, _b=b, _e=easing: (
        _a[0] + (_b[0] - _a[0]) * _e((t - _s) / _d),
        _a[1] + (_b[1] - _a[1]) * _e((t - _s) / _d))


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


def _coords_of(obj, time=0):
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


def _parse_path(d):
    """Lazy-import svgpathtools and parse an SVG path string, returning (parsed, total_length)."""
    import svgpathtools
    parsed = svgpathtools.parse_path(d)
    return parsed, parsed.length()


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
    _cache = [None, None]
    def _bbox(t):
        if _cache[0] != t:
            _cache[0] = t
            _cache[1] = bbox_func(t, **bbox_kw)
        return _cache[1]
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


