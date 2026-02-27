"""Base classes (VObject, VCollection) and shared constants."""
import math
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any
from vectormation.pathbbox import path_bbox
from vectormation._constants import (
    SMALL_BUFF, MED_SMALL_BUFF, DEFAULT_OBJECT_TO_EDGE_BUFF,
    UP, DOWN, LEFT, RIGHT, UL, UR, DL, DR,
)

import vectormation.easings as easings
import vectormation.attributes as attributes
import vectormation.style as style
import vectormation.morphing as morphing

# Register mix-blend-mode as a styling attribute so it flows through svg_style().
_BLEND_ENTRY = ('mix_blend_mode', 'mix-blend-mode', attributes.String, '', '')
style._ATTR_SCHEMA.append(_BLEND_ENTRY)
style._STYLE_PAIRS.append(('mix_blend_mode', 'mix-blend-mode'))
style._STYLES.append('mix_blend_mode')
style._GLOBAL_DEFAULTS['mix_blend_mode'] = ''
style._ATTR_NAMES.append('mix_blend_mode')
style._RENDERED_DEFAULTS['mix_blend_mode'] = ''
style.Styling.mix_blend_mode: attributes.String


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

def _to_edge_impl(obj, edge, buff, start_time, end_time, easing):
    """Shared to_edge logic for VObject and VCollection."""
    if isinstance(edge, tuple):
        edge = _EDGE_NAMES.get(edge, 'bottom')
    x, y, w, h = obj.bbox(start_time)
    cx, cy = x + w / 2, y + h / 2
    targets = {'bottom': (cx, 1080 - buff - h / 2), 'top': (cx, buff + h / 2),
               'left': (buff + w / 2, cy), 'right': (1920 - buff - w / 2, cy)}
    tx, ty = targets.get(edge, (cx, cy))
    return obj.center_to_pos(posx=tx, posy=ty, start_time=start_time,
                             end_time=end_time, easing=easing)


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

def _to_corner_impl(obj, corner, buff, start_time, end_time, easing):
    """Shared to_corner logic for VObject and VCollection."""
    if isinstance(corner, tuple):
        corner = _CORNER_MAP.get(corner, 'bottom_right')
    _, _, w, h = obj.bbox(start_time)
    tx = buff + w / 2 if 'left' in corner else 1920 - buff - w / 2
    ty = buff + h / 2 if 'top' in corner else 1080 - buff - h / 2
    return obj.center_to_pos(posx=tx, posy=ty, start_time=start_time,
                             end_time=end_time, easing=easing)


class VObject(ABC):  # Vector Object
    """Base class for all vector objects with time-varying attributes."""

    @abstractmethod
    def __init__(self, creation: float = 0, z=0):
        self.show = attributes.Real(creation, True)
        self.z = attributes.Real(creation, z)
        self.styling: style.Styling
        self._updaters: list = []

    @abstractmethod
    def to_svg(self, time: float) -> str: ...

    @abstractmethod
    def path(self, time: float) -> str: ...

    # -- Attribute declaration (override in subclasses) --

    def _extra_attrs(self):
        """Return class-specific time-varying attributes for last_change."""
        return []

    def _shift_coors(self) -> list[Any]:
        """Return Coor attributes to shift by (dx, dy)."""
        return []

    def _shift_reals(self) -> list[Any]:
        """Return (Real_x, Real_y) pairs to shift by dx, dy separately."""
        return []

    def add_updater(self, func, start=0, end=None):
        """Add an updater function called before each frame's to_svg.
        func(obj, time) should modify obj in-place. Active on [start, end]."""
        self._updaters.append((func, start, end))
        if end is not None:
            self.show.last_change = max(self.show.last_change, end)
        return self

    def _run_updaters(self, time):
        """Execute all active updaters for the given time."""
        for func, start, end in self._updaters:
            if time >= start and (end is None or time <= end):
                func(self, time)

    # -- Generic implementations --

    @property
    def last_change(self):
        return max(a.last_change for a in [*self._extra_attrs(), self.styling, self.z, self.show])

    def center(self, time: float = 0):
        """Return (cx, cy) of the bounding box at the given time."""
        x, y, w, h = self.bbox(time)
        return (x + w / 2, y + h / 2)

    def get_width(self, time=0):
        """Return the bounding box width at the given time."""
        return self.bbox(time)[2]

    def get_height(self, time=0):
        """Return the bounding box height at the given time."""
        return self.bbox(time)[3]

    def get_center(self, time=0):
        """Return (x, y) of the bounding box center."""
        return self.center(time)

    def distance_to(self, other, time=0):
        """Return the distance between this object's center and another's."""
        x1, y1 = self.center(time)
        x2, y2 = other.center(time)
        return math.hypot(x2 - x1, y2 - y1)

    def get_diagonal(self, time=0):
        """Return the diagonal length of the bounding box."""
        _, _, w, h = self.bbox(time)
        return math.hypot(w, h)

    def get_aspect_ratio(self, time=0):
        """Return width/height ratio of the bounding box."""
        _, _, w, h = self.bbox(time)
        return w / h if h != 0 else float('inf')

    def is_overlapping(self, other, time=0):
        """Return True if this object's bbox overlaps with other's bbox."""
        x1, y1, w1, h1 = self.bbox(time)
        x2, y2, w2, h2 = other.bbox(time)
        return not (x1 + w1 < x2 or x2 + w2 < x1 or y1 + h1 < y2 or y2 + h2 < y1)

    def get_edge(self, edge, time=0):
        """Return coordinate of a named edge point.
        edge: 'top', 'bottom', 'left', 'right',
              'top_left', 'top_right', 'bottom_left', 'bottom_right', 'center'."""
        return _get_edge_impl(self.bbox, edge, time)

    def get_bounds(self, time=0):
        """Return a dict with bounding box properties: x, y, width, height, left, right, top, bottom, center."""
        bx, by, bw, bh = self.bbox(time)
        return {
            'x': bx, 'y': by, 'width': bw, 'height': bh,
            'left': bx, 'right': bx + bw, 'top': by, 'bottom': by + bh,
            'center': (bx + bw / 2, by + bh / 2),
        }

    def get_left(self, time=0):
        return self.get_edge('left', time)

    def get_right(self, time=0):
        return self.get_edge('right', time)

    def get_top(self, time=0):
        return self.get_edge('top', time)

    def get_bottom(self, time=0):
        return self.get_edge('bottom', time)

    def get_x(self, time=0):
        """Return x-coordinate of the bounding box center."""
        return self.center(time)[0]

    def get_y(self, time=0):
        """Return y-coordinate of the bounding box center."""
        return self.center(time)[1]

    def set_x(self, x, start: float = 0):
        """Set the x-coordinate of the center (by shifting)."""
        dx = x - self.get_x(start)
        return self.shift(dx=dx, start_time=start)

    def set_y(self, y, start: float = 0):
        """Set the y-coordinate of the center (by shifting)."""
        dy = y - self.get_y(start)
        return self.shift(dy=dy, start_time=start)

    def set_width(self, width, start: float = 0, stretch=False):
        """Scale so the bounding box has the given width. If stretch=True, only scale X."""
        cur = self.get_width(start)
        if cur == 0:
            return self
        factor = width / cur
        if stretch:
            self._ensure_scale_origin(start)
            self.styling.scale_x.set_onward(start, self.styling.scale_x.at_time(start) * factor)
        else:
            self.scale(factor, start=start)
        return self

    def set_height(self, height, start: float = 0, stretch=False):
        """Scale so the bounding box has the given height. If stretch=True, only scale Y."""
        cur = self.get_height(start)
        if cur == 0:
            return self
        factor = height / cur
        if stretch:
            self._ensure_scale_origin(start)
            self.styling.scale_y.set_onward(start, self.styling.scale_y.at_time(start) * factor)
        else:
            self.scale(factor, start=start)
        return self

    def to_edge(self, edge: str | tuple = DOWN, buff=DEFAULT_OBJECT_TO_EDGE_BUFF,
                start_time: float = 0, end_time: float | None = None, easing=easings.smooth):
        """Move object to a canvas edge. edge: UP/DOWN/LEFT/RIGHT or string."""
        return _to_edge_impl(self, edge, buff, start_time, end_time, easing)

    def to_corner(self, corner: str | tuple = DR, buff=DEFAULT_OBJECT_TO_EDGE_BUFF,
                  start_time: float = 0, end_time: float | None = None, easing=easings.smooth):
        """Move object to a canvas corner. corner: UL/UR/DL/DR or string."""
        return _to_corner_impl(self, corner, buff, start_time, end_time, easing)

    def set_z(self, value, start: float = 0):
        """Set the z-order (draw order) of this object."""
        self.z.set_onward(start, value)
        return self

    def to_front(self, start: float = 0):
        """Bring this object to the front (high z-order)."""
        return self.set_z(999, start)

    def to_back(self, start: float = 0):
        """Send this object to the back (low z-order)."""
        return self.set_z(-999, start)

    def save_state(self, time: float = 0):
        """Save the current visual state (position, opacity, scale, color) for later restore."""

        self._saved_state = {
            'time': time,
            'styling': deepcopy(self.styling),
        }
        return self

    def restore(self, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Restore the previously saved state. Animated if end is given."""
        if not hasattr(self, '_saved_state'):
            return self
        saved = self._saved_state
        st = saved['time']
        saved_styling = saved['styling']
        # Restore fill, stroke, opacity, scale
        for attr_name in ('fill_opacity', 'stroke_opacity', 'scale_x', 'scale_y'):
            cur = getattr(self.styling, attr_name)
            saved_val = getattr(saved_styling, attr_name).at_time(st)
            if end is None:
                cur.set_onward(start, saved_val)
            else:
                dur = end - start
                if dur > 0:
                    cur_val = cur.at_time(start)
                    s = start
                    cur.set(s, end,
                        lambda t, _s=s, _d=dur, _cv=cur_val, _sv=saved_val:
                            _cv + (_sv - _cv) * easing((t - _s) / _d), stay=True)
        # Restore colors
        for attr_name in ('fill', 'stroke'):
            cur_c = getattr(self.styling, attr_name)
            saved_c = getattr(saved_styling, attr_name)
            if isinstance(cur_c, attributes.Color) and isinstance(saved_c, attributes.Color):
                saved_rgb = saved_c.time_func(st)
                restore_c = attributes.Color(start, saved_rgb)
                if end is None:
                    cur_c.set_to(restore_c)
                else:
                    cur_c.interpolate(restore_c, start, end, easing=easings.linear)
        return self

    def delay(self, duration, start=0):
        """Hide the object for *duration* seconds starting from *start*, then show it.

        Useful for staggering appearances without complex timing math.

        Parameters
        ----------
        duration:
            How long (in seconds) the object stays hidden.
        start:
            Time at which the hiding begins (default 0).
        """
        self._show_from(start + duration)
        return self

    def _show_from(self, time):
        """Hide before time, show from time onward."""
        self.show.set_onward(0, False)
        self.show.set_onward(time, True)

    def _hide_from(self, time):
        """Hide from time onward."""
        self.show.set_onward(time, False)

    def show_during(self, *ranges):
        """Show this object only during the specified time ranges.

        Each range is a (start, end) tuple. Object is hidden outside all ranges.
        Usage: obj.show_during((0, 1), (3, 5))
        """
        # Flatten if passed a list of tuples
        if len(ranges) == 1 and isinstance(ranges[0], list):
            ranges = ranges[0]
        # Hide from the very beginning, then toggle on/off for each range
        self.show.set_onward(0, False)
        for start, end in ranges:
            self.show.set_onward(start, True)
            self.show.set_onward(end, False)
        return self

    def hide_during(self, *ranges):
        """Hide this object during the specified time ranges, visible otherwise.

        Each range is a (start, end) tuple. Object is visible outside all ranges.
        Usage: obj.hide_during((2, 4))
        """
        if len(ranges) == 1 and isinstance(ranges[0], list):
            ranges = ranges[0]
        for start, end in ranges:
            self.show.set_onward(start, False)
            self.show.set_onward(end, True)
        return self

    def set_visible(self, visible, start=0):
        """Show or hide the object at a given time.

        If visible=True, show the object from *start* onward.
        If visible=False, hide the object from *start* onward.
        Returns self for chaining.

        Usage: obj.set_visible(False, start=2)
        """
        self.show.set_onward(start, 1 if visible else 0)
        return self

    def visibility_toggle(self, *times):
        """Toggle visibility at each given time.

        The times are sorted, then at the first time the object becomes
        visible, at the second it hides, at the third it shows again, and
        so on.  The object is hidden before the first time.

        Parameters
        ----------
        *times:
            One or more time values at which to toggle visibility.

        Returns
        -------
        self
            For method chaining.

        Example
        -------
        >>> c = Circle(r=50)
        >>> c.visibility_toggle(1, 3, 5)
        # visible during [1,3), hidden during [3,5), visible from 5 onward
        """
        sorted_times = sorted(times)
        self.show.set_onward(0, False)
        for i, t in enumerate(sorted_times):
            if i % 2 == 0:
                self.show.set_onward(t, True)
            else:
                self.show.set_onward(t, False)
        return self

    def set_creation(self, time):
        """Set the creation time."""
        self._show_from(time)
        return self

    def __repr__(self):
        return f'{self.__class__.__name__}(z={self.z.at_time(0)})'

    def copy(self):
        return deepcopy(self)

    def always_rotate(self, start: float = 0, end: float | None = None, degrees_per_second=90, cx=None, cy=None):
        """Continuously rotate the object around its center (or given cx, cy)."""
        if cx is None or cy is None:
            bx, by, bw, bh = self.bbox(start)
            cx, cy = bx + bw / 2, by + bh / 2
        s, _cx, _cy, _dps = start, cx, cy, degrees_per_second
        self.styling.rotation.set_onward(s,
            lambda t, _s=s, _cx=_cx, _cy=_cy, _dps=_dps: (_dps * (t - _s) % 360, _cx, _cy))
        if end is not None:
            self.styling.rotation.set_onward(end, self.styling.rotation.at_time(end))
        return self

    def always_shift(self, vx, vy, start: float = 0, end: float | None = None):
        """Continuously shift the object by (vx, vy) pixels per second."""
        s, _vx, _vy = start, vx, vy
        if end is None:
            for c in self._shift_coors():
                c.add_onward(s, lambda t, _s=s, _vx=_vx, _vy=_vy: (_vx * (t - _s), _vy * (t - _s)))
            for xa, ya in self._shift_reals():
                xa.add_onward(s, lambda t, _s=s, _vx=_vx: _vx * (t - _s))
                ya.add_onward(s, lambda t, _s=s, _vy=_vy: _vy * (t - _s))
        else:
            _e = end
            for c in self._shift_coors():
                c.add_onward(s, lambda t, _s=s, _e=_e, _vx=_vx, _vy=_vy: (_vx * (min(t, _e) - _s), _vy * (min(t, _e) - _s)))
            for xa, ya in self._shift_reals():
                xa.add_onward(s, lambda t, _s=s, _e=_e, _vx=_vx: _vx * (min(t, _e) - _s))
                ya.add_onward(s, lambda t, _s=s, _e=_e, _vy=_vy: _vy * (min(t, _e) - _s))
        return self

    def shift(self, dx=0, dy=0, start_time: float = 0, end_time: float | None = None, easing=easings.smooth):
        """Shift the object by (dx, dy), optionally animated over [start_time, end_time]."""
        if end_time is not None and end_time <= start_time:
            # Instant shift when duration is zero or negative
            end_time = None
        for c in self._shift_coors():
            if end_time is None:
                c.add_onward(start_time, (dx, dy))
            else:
                s, e = start_time, end_time
                c.add_onward(s, lambda t, _s=s, _e=e: (dx * easing((t-_s)/(_e-_s)), dy * easing((t-_s)/(_e-_s))), last_change=e)
        for xa, ya in self._shift_reals():
            if end_time is None:
                xa.add_onward(start_time, dx)
                ya.add_onward(start_time, dy)
            else:
                s, e = start_time, end_time
                xa.add_onward(s, lambda t, _s=s, _e=e: dx * easing((t-_s)/(_e-_s)), last_change=e)
                ya.add_onward(s, lambda t, _s=s, _e=e: dy * easing((t-_s)/(_e-_s)), last_change=e)
        return self

    # Alias
    scale_by = lambda self, start, end, factor, easing=easings.smooth: self.scale(factor, start, end, easing=easing)

    def _apply_rotation(self, start: float, end: float, target_deg, cx, cy, easing):
        """Set rotation from current angle to target_deg around (cx, cy)."""
        if cx is None or cy is None:
            bx, by, bw, bh = self.bbox(start)
            cx, cy = bx + bw / 2, by + bh / 2
        if end <= start:
            self.styling.rotation.set_onward(start, (target_deg, cx, cy))
            return self
        start_deg = self.styling.rotation.at_time(start)[0]
        s, e = start, end
        dur = e - s
        self.styling.rotation.set(s, e,
            lambda t, _s=s, _d=dur, _sd=start_deg, _td=target_deg, _cx=cx, _cy=cy:
                (_sd + (_td - _sd) * easing((t - _s) / _d), _cx, _cy),
            stay=True)
        self.styling.rotation.last_change = max(self.styling.rotation.last_change, end)
        return self

    def rotate_by(self, start: float, end: float, degrees, cx=None, cy=None, easing=easings.smooth):
        """Animate rotating by degrees from current rotation."""
        start_deg = self.styling.rotation.at_time(start)[0]
        return self._apply_rotation(start, end, start_deg + degrees, cx, cy, easing)

    def _transform_points(self, points, time):
        """Apply styling transforms (translate, scale, rotate) to a list of (x, y) points.
        Returns the transformed list of points, or None if skew/matrix are present."""
        if not hasattr(self, 'styling'):
            return points
        s = self.styling
        # Bail out for rare transforms that need the slow path
        if (s.skew_x.at_time(time) != 0 or s.skew_y.at_time(time) != 0 or
            s.skew_x_after.at_time(time) != 0 or s.skew_y_after.at_time(time) != 0 or
            s.matrix.at_time(time) != (0, 0, 0, 0, 0, 0)):
            return None
        result = list(points)
        # Apply transforms in reverse SVG order (same order as transform_style builds them)
        sx, sy = s.scale_x.at_time(time), s.scale_y.at_time(time)
        if sx != 1 or sy != 1:
            if s._scale_origin:
                cx, cy = s._scale_origin
                result = [(cx + (x - cx) * sx, cy + (y - cy) * sy) for x, y in result]
            else:
                result = [(x * sx, y * sy) for x, y in result]
        dx, dy = s.dx.at_time(time), s.dy.at_time(time)
        if dx != 0 or dy != 0:
            result = [(x + dx, y + dy) for x, y in result]
        rot = s.rotation.at_time(time)
        if rot != (0, 0, 0):
            deg, rcx, rcy = rot[0] % 360, rot[1], rot[2]
            if deg != 0:
                rad = math.radians(deg)
                cos_r, sin_r = math.cos(rad), math.sin(rad)
                result = [(rcx + cos_r * (x - rcx) - sin_r * (y - rcy),
                           rcy + sin_r * (x - rcx) + cos_r * (y - rcy))
                          for x, y in result]
        return result

    def _bbox_from_points(self, points, time):
        """Compute (xmin, ymin, width, height) from points, applying styling transforms.
        Returns None if transforms can't be handled (caller should use the slow path)."""
        transformed = self._transform_points(points, time)
        if transformed is None:
            return None
        xs = [p[0] for p in transformed]
        ys = [p[1] for p in transformed]
        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)
        return (xmin, ymin, xmax - xmin, ymax - ymin)

    def bbox(self, time):
        """Get the bounding rectangle in (xmin, ymin, width, height) at a certain time."""
        xmin, xmax, ymin, ymax = path_bbox(self.path(time))
        pts = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
        return self._bbox_from_points(pts, time) or (xmin, ymin, xmax - xmin, ymax - ymin)

    def contains_point(self, px, py, time=0):
        """Return True if (px, py) lies inside this object's bounding box at *time*."""
        x, y, w, h = self.bbox(time)
        return x <= px <= x + w and y <= py <= y + h

    def move_to(self, x, y, start_time: float = 0, end_time: float | None = None, easing=easings.smooth):
        """Move the object's center to (x, y), optionally animated over [start_time, end_time]."""
        xmin, ymin, w, h = self.bbox(start_time)
        self.shift(dx=x-(xmin+w/2), dy=y-(ymin+h/2),
                   start_time=start_time, end_time=end_time, easing=easing)
        return self

    def teleport(self, x, y, time: float = 0):
        """Instantly move object center to (x, y) at the given time (no animation)."""
        return self.move_to(x, y, start_time=time)

    def center_to_pos(self, posx: float = 960, posy: float = 540, start_time: float = 0, end_time: float | None = None, easing=easings.smooth):
        """Shifts the center to pos, animated from start_time to end_time."""
        return self.move_to(posx, posy, start_time, end_time, easing)

    def follow_spline(self, points, start: float = 0, end: float = 1, easing=easings.smooth):
        """Move the object's center smoothly through a sequence of (x, y) points.
        Uses cubic Bézier interpolation for smooth curves through all points."""
        n = len(points)
        if n < 2:
            return self
        # Build SVG path through control points using Catmull-Rom → cubic Bézier
        parts = [f'M{points[0][0]},{points[0][1]}']
        for i in range(n - 1):
            p0 = points[max(i - 1, 0)]
            p1 = points[i]
            p2 = points[min(i + 1, n - 1)]
            p3 = points[min(i + 2, n - 1)]
            # Catmull-Rom tangents (tension=0.5)
            c1x = p1[0] + (p2[0] - p0[0]) / 6
            c1y = p1[1] + (p2[1] - p0[1]) / 6
            c2x = p2[0] - (p3[0] - p1[0]) / 6
            c2y = p2[1] - (p3[1] - p1[1]) / 6
            parts.append(f'C{c1x},{c1y} {c2x},{c2y} {p2[0]},{p2[1]}')
        path_d = ' '.join(parts)
        return self.along_path(start, end, path_d, easing)

    def along_path(self, start: float, end: float, path_d, easing=easings.smooth):
        """Move the object's center along an SVG path string over [start, end]."""
        dur = end - start
        if dur <= 0:
            return self
        import svgpathtools
        parsed = svgpathtools.parse_path(path_d)
        total_length = parsed.length()
        xmin, ymin, w, h = self.bbox(start)
        cx0, cy0 = xmin + w / 2, ymin + h / 2
        point0 = parsed.point(0)
        off_x, off_y = cx0 - point0.real, cy0 - point0.imag
        s = start
        def pos(t):
            progress = max(0, min(1, easing((t - s) / dur)))
            pt = parsed.point(parsed.ilength(progress * total_length))  # type: ignore[operator]
            return (pt.real + off_x - cx0, pt.imag + off_y - cy0)
        for c in self._shift_coors():
            c.add(s, end, pos, stay=True)
        for xa, ya in self._shift_reals():
            xa.add(s, end, lambda t, _f=pos: _f(t)[0], stay=True)
            ya.add(s, end, lambda t, _f=pos: _f(t)[1], stay=True)
        return self

    def path_arc(self, tx, ty, start: float = 0, end: float = 1,
                 angle=math.pi / 2, easing=easings.smooth):
        """Move the object's center to (tx, ty) along a circular arc.
        angle: arc angle in radians (positive = clockwise in SVG coords).
        0 = straight line, pi/2 = quarter circle, pi = semicircle."""
        dur = end - start
        if dur <= 0:
            return self
        bx, by, bw, bh = self.bbox(start)
        sx, sy = bx + bw / 2, by + bh / 2
        if abs(angle) < 1e-9:
            return self.move_to(tx, ty, start, end, easing)
        # Compute arc center: perpendicular bisector of (sx,sy)→(tx,ty)
        mx, my = (sx + tx) / 2, (sy + ty) / 2
        dx, dy = tx - sx, ty - sy
        chord = math.hypot(dx, dy)
        if chord < 1e-9:
            return self
        half_angle = angle / 2
        tan_ha = math.tan(half_angle)
        if abs(tan_ha) < 1e-9:
            # angle ≈ n*2π — arc degenerates, fall back to straight line
            return self.move_to(tx, ty, start, end, easing)
        # Distance from midpoint to arc center along perpendicular
        d = (chord / 2) / tan_ha
        # Perpendicular direction (rotated 90°)
        px, py = -dy / chord, dx / chord
        cx, cy = mx + d * px, my + d * py
        # Starting angle from center
        a0 = math.atan2(sy - cy, sx - cx)
        _s, _d, _a0, _ang = start, max(dur, 1e-9), a0, angle
        _cx, _cy, _sx, _sy = cx, cy, sx, sy
        def _pos(t, _s=_s, _d=_d, _a0=_a0, _ang=_ang, _cx=_cx, _cy=_cy, _sx=_sx, _sy=_sy, _easing=easing):
            progress = _easing((t - _s) / _d)
            a = _a0 + _ang * progress
            r = math.hypot(_sx - _cx, _sy - _cy)
            return (_cx + r * math.cos(a) - _sx, _cy + r * math.sin(a) - _sy)
        for c in self._shift_coors():
            c.add(start, end, _pos, stay=True)
        for xa, ya in self._shift_reals():
            xa.add(start, end, lambda t, _f=_pos: _f(t)[0], stay=True)
            ya.add(start, end, lambda t, _f=_pos: _f(t)[1], stay=True)
        return self

    def brect(self, time: float = 0, rx=0, ry=0, buff=SMALL_BUFF, follow=True):
        """Bounding rectangle with buff outward padding."""
        return _make_brect(self.bbox, time, rx, ry, buff, follow)

    def fadein(self, start: float = 0, end: float = 1, shift_dir=None, shift_amount=50,
               change_existence=True, easing=easings.smooth):
        """Animate opacity from 0 to current value over [start, end].
        shift_dir: optional direction tuple (e.g. UP, DOWN) to slide in from."""
        if change_existence:
            self._show_from(start)
        end_val = self.styling.opacity.at_time(end)
        s, e = start, end
        dur = e - s
        if dur <= 0:
            return self
        self.styling.opacity.set(s, e, lambda t, _s=s, _d=dur, _ev=end_val: _ev * easing((t-_s)/_d))
        if shift_dir is not None:
            dx = shift_dir[0] * shift_amount
            dy = shift_dir[1] * shift_amount
            self.shift(dx=-dx, dy=-dy, start_time=start)  # offset to start pos
            self.shift(dx=dx, dy=dy, start_time=start, end_time=end, easing=easing)
        return self

    def fade_shift(self, dx=0, dy=0, start: float = 0, end: float = 1, easing=easings.smooth):
        """Simultaneously fade out while shifting by (dx, dy) over [start, end].

        Animates opacity from its current value to 0 while shifting the object
        by (dx, dy).  The object is hidden at *end*.  Useful as an exit animation
        that moves an element off-screen while it disappears.

        Parameters
        ----------
        dx, dy:
            Total pixel displacement to apply over the animation.
        start, end:
            Time interval for the animation.
        easing:
            Easing function (default ``easings.smooth``).

        Returns
        -------
        self
        """
        start_val = self.styling.opacity.at_time(start)
        dur = end - start
        if dur <= 0:
            self._hide_from(start)
            return self
        s, e = start, end
        self.styling.opacity.set(s, e,
            lambda t, _s=s, _d=dur, _sv=start_val: _sv * (1 - easing((t - _s) / _d)))
        self.shift(dx=dx, dy=dy, start_time=s, end_time=e, easing=easing)
        self._hide_from(e)
        return self

    def fadeout(self, start: float = 0, end: float = 1, shift_dir=None, shift_amount=50,
                change_existence=True, easing=easings.smooth):
        """Animate opacity from current value to 0 over [start, end].
        shift_dir: optional direction tuple (e.g. UP, DOWN) to slide out toward."""
        start_val = self.styling.opacity.at_time(start)
        s, e = start, end
        dur = e - s
        if dur <= 0:
            if change_existence:
                self._hide_from(start)
            return self
        self.styling.opacity.set(s, e, lambda t, _s=s, _d=dur, _sv=start_val: _sv * (1 - easing((t-_s)/_d)))
        if shift_dir is not None:
            dx = shift_dir[0] * shift_amount
            dy = shift_dir[1] * shift_amount
            self.shift(dx=dx, dy=dy, start_time=start, end_time=end, easing=easing)
        if change_existence:
            self._hide_from(end)
        return self

    def dissolve_out(self, start: float = 0, end: float = 1,
                     granularity=8, change_existence=True, seed=42):
        """Scatter/noise opacity fade-out.

        Instead of a smooth linear fade, the opacity flickers with a
        pseudo-random noise pattern, creating a "dissolving into particles"
        effect.  The overall trend goes from the current opacity to zero,
        but individual frames jitter above and below the trend line.

        Parameters
        ----------
        start, end:
            Animation time window.
        granularity:
            Controls the noise frequency -- higher values produce more
            rapid flickering (default 8).
        change_existence:
            If True, hide the object after *end*.
        seed:
            Integer seed for the deterministic noise, ensuring the same
            object always dissolves identically.
        """
        dur = end - start
        if dur <= 0:
            if change_existence:
                self._hide_from(start)
            return self
        start_val = self.styling.opacity.at_time(start)
        _s, _d, _sv, _g, _seed = start, max(dur, 1e-9), start_val, granularity, seed

        def _dissolve(t, _s=_s, _d=_d, _sv=_sv, _g=_g, _seed=_seed):
            p = (t - _s) / _d  # overall progress 0->1
            # Base trend: smooth fade to zero
            base = _sv * (1.0 - p)
            # Deterministic noise using a hash-based approach (no imports needed)
            # Use a sin-based pseudo-noise with multiple frequencies
            n = _seed + p * _g
            noise = (math.sin(n * 127.1 + 311.7) * 43758.5453) % 1.0
            noise = noise * 2 - 1  # range [-1, 1]
            # Noise amplitude decreases as we approach end (so we cleanly reach 0)
            jitter = noise * _sv * 0.4 * (1.0 - p * p)
            return max(0.0, min(_sv, base + jitter))

        self.styling.opacity.set(start, end, _dissolve)
        if change_existence:
            self._hide_from(end)
        return self

    def _rotate_fade_anim(self, start, end, degrees, fade_in, change_existence, easing):
        """Shared helper for rotate_in / rotate_out."""
        dur = end - start
        if dur <= 0:
            return self
        if change_existence and fade_in:
            self._show_from(start)
        self._ensure_scale_origin(start)
        cx, cy = self.styling._scale_origin
        s, op_base = start, self.styling.fill_opacity.at_time(start)
        if fade_in:
            rot_fn = lambda t, _s=s, _d=dur, _deg=degrees, _cx=cx, _cy=cy: (_deg * (1 - easing((t - _s) / _d)), _cx, _cy)
            op_fn = lambda t, _s=s, _d=dur, _b=op_base: _b * easing((t - _s) / _d)
        else:
            rot_fn = lambda t, _s=s, _d=dur, _deg=degrees, _cx=cx, _cy=cy: (_deg * easing((t - _s) / _d), _cx, _cy)
            op_fn = lambda t, _s=s, _d=dur, _b=op_base: _b * (1 - easing((t - _s) / _d))
        self.styling.rotation.set(s, end, rot_fn, stay=True)
        self.styling.fill_opacity.set(s, end, op_fn, stay=True)
        if change_existence and not fade_in:
            self._hide_from(end)
        return self

    def rotate_in(self, start: float = 0, end: float = 1, degrees=90,
                    change_existence=True, easing=easings.smooth):
        """Fade in while rotating from an offset angle to 0."""
        return self._rotate_fade_anim(start, end, degrees, True, change_existence, easing)

    def rotate_out(self, start: float = 0, end: float = 1, angle=90,
                   change_existence=True, easing=easings.smooth):
        """Rotate away while fading out. Reverse of rotate_in."""
        return self._rotate_fade_anim(start, end, angle, False, change_existence, easing)

    def _pop_anim(self, start, end, duration, overshoot, pop_in, change_existence, easing):
        """Shared helper for pop_in / pop_out."""
        dur = duration if duration > 0 else end - start
        if dur <= 0:
            return self
        if change_existence and pop_in:
            self._show_from(start)
        self._ensure_scale_origin(start)
        s = start
        if pop_in:
            def scale_fn(t, _s=s, _d=dur, _o=overshoot, _e=easing):
                p = _e((t - _s) / _d)
                if p < 0.7:
                    return p / 0.7 * _o
                return _o + (1 - _o) * ((p - 0.7) / 0.3)
        else:
            scale_fn = lambda t, _s=s, _d=dur, _e=easing: 1 - _e((t - _s) / _d)
        self.styling.scale_x.set(s, end, scale_fn, stay=True)
        self.styling.scale_y.set(s, end, scale_fn, stay=True)
        if change_existence and not pop_in:
            self._hide_from(end)
        return self

    def pop_in(self, start: float = 0, duration=0.3, overshoot=1.2, change_existence=True, easing=easings.smooth):
        """Quick pop-in: scale from 0 to 1 with optional overshoot."""
        end = start + duration
        return self._pop_anim(start, end, duration, overshoot, True, change_existence, easing)

    def pop_out(self, start: float = 0, duration=0.3, change_existence=True, easing=easings.smooth):
        """Quick pop-out: scale from 1 to 0."""
        end = start + duration
        return self._pop_anim(start, end, duration, 0, False, change_existence, easing)

    def _apply_shift_effect(self, start, end, dx_func=None, dy_func=None, stay=False):
        """Apply displacement functions to all shift attributes.
        dx_func/dy_func: callable(t) -> float, or None to skip that axis."""
        kw = {'stay': True} if stay else {}
        if dx_func and dy_func:
            for xa, ya in self._shift_reals():
                xa.add(start, end, dx_func, **kw)
                ya.add(start, end, dy_func, **kw)
            for c in self._shift_coors():
                c.add(start, end, lambda t, _fdx=dx_func, _fdy=dy_func: (_fdx(t), _fdy(t)), **kw)
        elif dx_func:
            for xa, _ in self._shift_reals():
                xa.add(start, end, dx_func, **kw)
            for c in self._shift_coors():
                c.add(start, end, lambda t, _f=dx_func: (_f(t), 0), **kw)
        elif dy_func:
            for _, ya in self._shift_reals():
                ya.add(start, end, dy_func, **kw)
            for c in self._shift_coors():
                c.add(start, end, lambda t, _f=dy_func: (0, _f(t)), **kw)
        return self

    def float_anim(self, start: float = 0, end: float = 1, amplitude=10, speed=1.0):
        """Gentle floating up/down animation."""
        dur = end - start
        if dur <= 0:
            return self
        _s, _spd, _a = start, speed, amplitude
        def _dy(t, _s=_s, _spd=_spd, _a=_a):
            p = (t - _s) * _spd
            return _a * math.sin(p * 2 * math.pi)
        return self._apply_shift_effect(start, end, dy_func=_dy)

    def _slide_offsets(self, direction, start):
        bx, by, bw, bh = self.bbox(start)
        offsets = {
            'left': (-bx - bw, 0),
            'right': (1920 - bx, 0),
            'up': (0, -by - bh),
            'down': (0, 1080 - by),
        }
        return offsets.get(direction, (0, 0))

    def _slide_anim(self, direction, start, end, slide_in, change_existence, easing):
        """Shared helper for slide_in / slide_out."""
        dur = end - start
        if dur <= 0:
            return self
        if change_existence and slide_in:
            self._show_from(start)
        ox, oy = self._slide_offsets(direction, start)
        s = start
        if slide_in:
            dx = (lambda t, _s=s, _d=dur, _ox=ox, _e=easing: _ox * (1 - _e((t - _s) / _d))) if ox else None
            dy = (lambda t, _s=s, _d=dur, _oy=oy, _e=easing: _oy * (1 - _e((t - _s) / _d))) if oy else None
        else:
            dx = (lambda t, _s=s, _d=dur, _ox=ox, _e=easing: _ox * _e((t - _s) / _d)) if ox else None
            dy = (lambda t, _s=s, _d=dur, _oy=oy, _e=easing: _oy * _e((t - _s) / _d)) if oy else None
        self._apply_shift_effect(start, end, dx, dy, stay=True)
        if change_existence and not slide_in:
            self._hide_from(end)
        return self

    def slide_in(self, direction='left', start: float = 0, end: float = 1,
                  easing=easings.smooth, change_existence=True):
        """Slide in from outside the canvas edge.
        direction: 'left', 'right', 'up', 'down'."""
        return self._slide_anim(direction, start, end, True, change_existence, easing)

    def slide_out(self, direction='right', start: float = 0, end: float = 1,
                   easing=easings.smooth, change_existence=True):
        """Slide out to outside the canvas edge.
        direction: 'left', 'right', 'up', 'down'."""
        return self._slide_anim(direction, start, end, False, change_existence, easing)

    def _fade_slide_anim(self, direction, distance, start, end, fade_in, change_existence, easing):
        """Shared helper for fade_slide_in / fade_slide_out."""
        direction = direction or DOWN
        dur = end - start
        if dur <= 0:
            if not fade_in and change_existence:
                self._hide_from(start)
            return self
        if fade_in and change_existence:
            self._show_from(start)
        # For fade_in: start offset in -direction, slide to current pos
        # For fade_out: slide away in +direction from current pos
        sign = -1 if fade_in else 1
        dx = sign * direction[0] * distance
        dy = sign * direction[1] * distance
        s = start
        if fade_in:
            dx_func = (lambda t, _s=s, _d=dur, _dx=dx, _e=easing: _dx * (1 - _e((t - _s) / _d))) if dx else None
            dy_func = (lambda t, _s=s, _d=dur, _dy=dy, _e=easing: _dy * (1 - _e((t - _s) / _d))) if dy else None
        else:
            dx_func = (lambda t, _s=s, _d=dur, _dx=dx, _e=easing: _dx * _e((t - _s) / _d)) if dx else None
            dy_func = (lambda t, _s=s, _d=dur, _dy=dy, _e=easing: _dy * _e((t - _s) / _d)) if dy else None
        self._apply_shift_effect(start, end, dx_func, dy_func, stay=True)
        if fade_in:
            end_val = self.styling.opacity.at_time(end)
            self.styling.opacity.set(s, end,
                lambda t, _s=s, _d=dur, _ev=end_val, _e=easing: _ev * _e((t - _s) / _d))
        else:
            start_val = self.styling.opacity.at_time(start)
            self.styling.opacity.set(s, end,
                lambda t, _s=s, _d=dur, _sv=start_val, _e=easing: _sv * (1 - _e((t - _s) / _d)))
            if change_existence:
                self._hide_from(end)
        return self

    def fade_slide_in(self, direction=None, distance=200, start: float = 0, end: float = 1,
                      change_existence=True, easing=easings.smooth):
        """Slide in from a direction while fading from 0 to 1.

        Combines a positional shift with an opacity fade-in.  The object
        starts *distance* pixels away in the opposite of *direction* and
        at opacity 0, then moves to its current position at full opacity.

        Parameters
        ----------
        direction:
            Direction tuple to slide in from (e.g. ``DOWN``, ``LEFT``).
            Defaults to ``DOWN``.
        distance:
            How far away (in pixels) the object starts.
        start, end:
            Time interval for the animation.
        change_existence:
            If True the object becomes visible at *start*.
        easing:
            Easing function (default ``easings.smooth``).

        Returns
        -------
        self
        """
        return self._fade_slide_anim(direction, distance, start, end, True, change_existence, easing)

    def fade_slide_out(self, direction=None, distance=200, start: float = 0, end: float = 1,
                       change_existence=True, easing=easings.smooth):
        """Slide away in a direction while fading from 1 to 0.

        The reverse of :meth:`fade_slide_in`.  The object moves *distance*
        pixels in *direction* while its opacity goes from its current value
        to 0.

        Parameters
        ----------
        direction:
            Direction tuple to slide toward (e.g. ``DOWN``, ``LEFT``).
            Defaults to ``DOWN``.
        distance:
            How far (in pixels) the object travels.
        start, end:
            Time interval for the animation.
        change_existence:
            If True the object is hidden at *end*.
        easing:
            Easing function (default ``easings.smooth``).

        Returns
        -------
        self
        """
        return self._fade_slide_anim(direction, distance, start, end, False, change_existence, easing)

    def write(self, start: float = 0, end: float = 1, max_stroke_width=2, change_existence=True, easing=easings.smooth, stroke_easing=easings.there_and_back):
        """Animate fill_opacity from 0 to current with a stroke pulse effect."""
        if change_existence:
            self._show_from(start)
        end_val = self.styling.fill_opacity.at_time(end)
        sw = self.styling.stroke_width.at_time(end)
        s, e = start, end
        dur = e - s
        if dur <= 0:
            return self
        self.styling.fill_opacity.set(s, e, lambda t, _s=s, _d=dur, _ev=end_val: _ev * easing((t-_s)/_d))
        self.styling.stroke_width.set(s, e, lambda t, _s=s, _d=dur, _msw=max_stroke_width, _sw=sw: _msw * stroke_easing((t-_s)/_d) + easing((t-_s)/_d) * _sw)
        return self

    def create(self, start: float = 0, end: float = 1, change_existence=True, easing=easings.smooth):
        """Animate drawing the path of this object from start to end.
        Returns a new Path object that must be added to the canvas.
        The original object becomes visible at `end`."""
        if change_existence:
            self._show_from(end)

        p = morphing.Path(self.path(start))
        _dur = end - start
        def f(t): return easing((t-start)/_dur) if _dur > 0 else 1

        from vectormation._shapes import Path
        res = Path('')
        res.d.set(start, end, lambda t: _path_prefix(p, f(t)).d())
        # Inherit styling from the original object
        res.styling = deepcopy(self.styling)
        res.styling.fill_opacity.set_onward(0, 0)
        if change_existence:
            res._show_from(start)
        return res

    def uncreate(self, start: float = 0, end: float = 1, change_existence=True, easing=easings.smooth):
        """Reverse of create — wipes the path from end to start.
        The original object is hidden at `end`."""
        if change_existence:
            self.show.set_onward(end, False)

        p = morphing.Path(self.path(start))
        _dur = end - start
        def f(t): return easing((t - start) / _dur) if _dur > 0 else 1

        from vectormation._shapes import Path
        res = Path('')
        res.d.set(start, end, lambda t: _path_prefix(p, 1 - f(t)).d())
        res.styling = deepcopy(self.styling)
        res.styling.fill_opacity.set_onward(0, 0)
        if change_existence:
            res._show_from(start)
            res.show.set_onward(end, False)
        return res

    def draw_along(self, start: float = 0, end: float = 1, easing=easings.smooth, change_existence=True):
        """Animate drawing the stroke of this object using stroke-dashoffset.
        Uses svgpathtools to compute total path length, then animates
        stroke-dashoffset from length to 0."""
        import svgpathtools
        p = svgpathtools.parse_path(self.path(start))
        total_length = p.length()

        if change_existence:
            self._show_from(start)

        # Set dasharray to total length so the entire path is one dash
        self.styling.stroke_dasharray.set_onward(start, str(total_length))
        # Animate dashoffset from total_length (hidden) to 0 (fully drawn)
        self.styling.stroke_dashoffset.set_onward(start, total_length)
        s, e = start, end
        dur = e - s
        if dur <= 0:
            self.styling.stroke_dashoffset.set_onward(s, 0)
            return self
        self.styling.stroke_dashoffset.set(s, e,
            lambda t, _s=s, _d=dur, _tl=total_length: _tl * (1 - easing((t - _s) / _d)), stay=True)
        return self

    def show_passing_flash(self, start: float = 0, end: float = 1, flash_width=0.15,
                           color='#FFFF00', stroke_width=6, easing=easings.linear):
        """A bright flash that travels along this object's path.
        Returns a new Path object that must be added to the canvas.
        flash_width: fraction of path visible at any time (0-1)."""
        import svgpathtools
        p = svgpathtools.parse_path(self.path(start))
        total = p.length()
        if total <= 0:
            from vectormation._shapes import Path
            return Path('', creation=start)
        dur = end - start
        if dur <= 0:
            dur = 1
        from vectormation._shapes import Path
        flash = Path(self.path(start), creation=start,
                     stroke=color, stroke_width=stroke_width, fill_opacity=0)
        flash._show_from(start)
        flash._hide_from(end)
        gap = total * (1 - flash_width)
        s = start
        flash.styling.stroke_dasharray.set_onward(s, f'{total * flash_width} {gap}')
        flash.styling.stroke_dashoffset.set(s, end,
            lambda t, _s=s, _d=dur, _tot=total: _tot * (1 - easing((t - _s) / _d)), stay=True)
        return flash

    def _ensure_scale_origin(self, time):
        """Set _scale_origin to the object's center if not already set."""
        if self.styling._scale_origin is None:
            self.styling._scale_origin = self.center(time)

    def scale_to(self, start: float, end: float, factor, easing=easings.smooth):
        """Animate to an absolute scale factor (e.g. factor=2 → double original size)."""
        self._ensure_scale_origin(start)
        self.styling.scale_x.move_to(start, end, factor, easing=easing)
        self.styling.scale_y.move_to(start, end, factor, easing=easing)
        return self

    def scale_to_size(self, width=None, height=None, start: float = 0,
                      end: float | None = None, easing=easings.smooth):
        """Scale the object to fit a target pixel width and/or height.

        If only *width* is given, scale proportionally so the bounding box
        reaches that width.  If only *height* is given, scale proportionally
        to that height.  If *both* are given, scale each axis independently
        (aspect ratio may not be preserved).

        The animation runs from *start* to *end*.  When *end* is ``None`` the
        change is applied instantly at *start*.

        Parameters
        ----------
        width:
            Target bounding-box width in SVG pixels, or ``None`` to skip.
        height:
            Target bounding-box height in SVG pixels, or ``None`` to skip.
        start:
            Time at which the change begins (and from which the current size
            is measured).
        end:
            Time at which the change ends.  ``None`` = instant.
        easing:
            Easing function for the animation.

        Returns
        -------
        self

        Examples
        --------
        >>> rect = Rectangle(200, 100)
        >>> rect.scale_to_size(width=400)          # double width, proportional
        >>> rect.scale_to_size(width=300, height=300, start=0, end=1)
        """
        _, _, cur_w, cur_h = self.bbox(start)
        self._ensure_scale_origin(start)
        if width is not None and height is not None:
            x_factor = width / cur_w if cur_w != 0 else 1
            y_factor = height / cur_h if cur_h != 0 else 1
            target_sx = self.styling.scale_x.at_time(start) * x_factor
            target_sy = self.styling.scale_y.at_time(start) * y_factor
        elif width is not None:
            factor = width / cur_w if cur_w != 0 else 1
            target_sx = self.styling.scale_x.at_time(start) * factor
            target_sy = self.styling.scale_y.at_time(start) * factor
        elif height is not None:
            factor = height / cur_h if cur_h != 0 else 1
            target_sx = self.styling.scale_x.at_time(start) * factor
            target_sy = self.styling.scale_y.at_time(start) * factor
        else:
            return self
        for attr, target in [(self.styling.scale_x, target_sx), (self.styling.scale_y, target_sy)]:
            if end is None:
                attr.set_onward(start, target)
            else:
                attr.move_to(start, end, target, easing=easing)
        return self

    def rotate_to(self, start: float, end: float, degrees, cx=None, cy=None, easing=easings.smooth):
        """Animate rotating this object to the given angle in degrees."""
        return self._apply_rotation(start, end, degrees, cx, cy, easing)

    def set_color(self, start: float, end: float, fill=None, stroke=None, easing=easings.smooth, color_space='rgb'):
        """Animate fill and/or stroke color change over [start, end].
        color_space: 'rgb' or 'hsl' (smoother for hue transitions)."""
        for attr_name, target in [('fill', fill), ('stroke', stroke)]:
            if target is None:
                continue
            attr = getattr(self.styling, attr_name)
            end_color = attributes.Color(0, target)
            interp = attr.interpolate(end_color, start, end, easing=easing, color_space=color_space)
            setattr(self.styling, attr_name, interp)
        return self

    def fade_color(self, color, start: float = 0, end: float = 1,
                   attr: str = 'fill', easing=easings.smooth):
        """Smoothly transition the fill (or stroke) color to *color* over [start, end].

        This is the simplest single-step color animation.  Unlike
        :meth:`set_color` (instant snap at *start*) and
        :meth:`color_gradient_anim` (multi-stop gradient), this method
        interpolates from the current color at *start* to the target *color*
        at *end* using the Color attribute's ``move_to`` method.

        Parameters
        ----------
        color:
            Target color.  Accepts hex strings (``'#ff0000'``), named colors,
            or RGB tuples.
        start, end:
            Animation time window in seconds.
        attr:
            Which styling attribute to animate: ``'fill'`` (default) or
            ``'stroke'``.
        easing:
            Easing function.  Defaults to :func:`easings.smooth`.

        Returns
        -------
        self

        Example
        -------
        >>> circle = Circle(r=60)
        >>> circle.fade_color('#ff0000', start=1, end=2)   # fade fill to red
        >>> circle.fade_color('#00ff00', start=1, end=2, attr='stroke')
        """
        style_attr = getattr(self.styling, attr)
        target = attributes.Color(0, color)
        interp = style_attr.interpolate(target, start, end, easing=easing)
        setattr(self.styling, attr, interp)
        return self

    def color_wave(self, start: float = 0, end: float = 1,
                    wave_color='#58C4DD', attr='fill', width=0.3, cycles=1):
        """Animated color sweep across the object.

        A wave-front of *wave_color* sweeps across the object's current base
        color.  The sweep position advances linearly over [start, end].  At
        any instant the rendered color is an interpolation: the base color
        transitions to *wave_color* and back, with the peak of the wave at
        the current sweep position.

        Parameters
        ----------
        start, end:
            Animation time window.
        wave_color:
            The highlight color that sweeps across.
        attr:
            ``'fill'`` or ``'stroke'``.
        width:
            Width of the wave front as a fraction of the total duration
            (0 < width <= 1).  Smaller values give a sharper sweep.
        cycles:
            Number of complete sweep passes (default 1).
        """
        dur = end - start
        if dur <= 0:
            return self
        style_attr = getattr(self.styling, attr)
        if not isinstance(style_attr, attributes.Color):
            return self
        base_rgb = style_attr.time_func(start)
        wave_rgb = (int(wave_color[1:3], 16), int(wave_color[3:5], 16),
                    int(wave_color[5:7], 16))
        _s, _d, _w, _cyc = start, max(dur, 1e-9), max(width, 0.01), cycles
        _br, _wr = base_rgb, wave_rgb

        def _sweep_rgb(t, _s=_s, _d=_d, _w=_w, _cyc=_cyc,
                       _br=_br, _wr=_wr):
            # sweep position in [0, 1], repeating for multiple cycles
            p = (((t - _s) / _d) * _cyc) % 1.0
            # Symmetric distance: 1 at edges of sweep, 0 at centre
            dist2 = abs(p * 2 - 1)
            envelope = max(0.0, 1.0 - dist2 / _w) if _w > 0 else 0.0
            envelope = envelope * envelope * (3 - 2 * envelope)  # smoothstep
            return (_br[0] + (_wr[0] - _br[0]) * envelope,
                    _br[1] + (_wr[1] - _br[1]) * envelope,
                    _br[2] + (_wr[2] - _br[2]) * envelope)

        style_attr.use = 'rgb'
        style_attr.set(start, end, _sweep_rgb, stay=False)
        return self

    def color_gradient_anim(self, colors, start: float = 0, end: float = 1,
                             attr: str = 'fill'):
        """Animate through a sequence of colors over [start, end].

        Divides the interval into ``len(colors) - 1`` equal segments and linearly
        interpolates between each adjacent pair using RGB blending.

        Parameters
        ----------
        colors:
            Sequence of two or more color strings (hex or named).  Must have at
            least two entries.
        start, end:
            Animation time window in seconds.
        attr:
            Which styling attribute to animate: ``'fill'`` (default) or
            ``'stroke'``.

        Returns
        -------
        self
        """
        if len(colors) < 2:
            return self
        dur = end - start
        if dur <= 0:
            return self
        # Parse all colors to (r, g, b) tuples up front
        from vectormation.colors import _hex_to_rgb, color_from_name
        def _to_rgb(c):
            if not c.startswith('#'):
                c = color_from_name(c.upper())
            return _hex_to_rgb(c)
        parsed = [_to_rgb(c) for c in colors]
        n_segs = len(colors) - 1
        seg_dur = dur / n_segs
        style_attr = getattr(self.styling, attr)
        style_attr.use = 'rgb'
        for i in range(n_segs):
            t0 = start + i * seg_dur
            t1 = t0 + seg_dur
            _r0, _g0, _b0 = parsed[i]
            _r1, _g1, _b1 = parsed[i + 1]
            _t0, _d = t0, seg_dur
            style_attr.set(t0, t1,
                lambda t, _s=_t0, _dd=_d,
                       _r0=_r0, _g0=_g0, _b0=_b0,
                       _r1=_r1, _g1=_g1, _b1=_b1: (
                    _r0 + (_r1 - _r0) * ((t - _s) / _dd),
                    _g0 + (_g1 - _g0) * ((t - _s) / _dd),
                    _b0 + (_b1 - _b0) * ((t - _s) / _dd)),
                stay=(i == n_segs - 1))
        return self

    def next_to(self, other, direction: str | tuple = 'right', buff=SMALL_BUFF, start_time: float = 0):
        """Position this object next to another.
        direction: 'left', 'right', 'up', 'down' or a direction constant (UP, DOWN, LEFT, RIGHT)."""
        if isinstance(direction, tuple):
            direction = _DIR_NAMES.get(direction, 'right')
        mx, my, mw, mh = self.bbox(start_time)
        ox, oy, ow, oh = other.bbox(start_time)
        mcx, mcy = mx + mw/2, my + mh/2
        ocx, ocy = ox + ow/2, oy + oh/2
        offsets = {
            'right': (ox + ow + buff + mw/2 - mcx, ocy - mcy),
            'left':  (ox - buff - mw/2 - mcx, ocy - mcy),
            'down':  (ocx - mcx, oy + oh + buff + mh/2 - mcy),
            'up':    (ocx - mcx, oy - buff - mh/2 - mcy),
        }
        dx, dy = offsets[direction]
        self.shift(dx=dx, dy=dy, start_time=start_time)
        return self

    def attach_to(self, other, direction=None, buff=None, start=0, end=None):
        """Continuously position self next to other from *start* to *end*.

        Uses an updater to track *other*'s position each frame so that
        ``self`` stays anchored even when the target moves.

        Parameters
        ----------
        other:
            The reference object to attach to.
        direction:
            ``(dx, dy)`` direction tuple, e.g. ``RIGHT``.  Defaults to
            ``RIGHT`` if not given.
        buff:
            Pixel buffer between the two objects.  Defaults to
            ``MED_SMALL_BUFF``.
        start:
            Time at which the attachment begins.
        end:
            Time at which the attachment ends (``None`` = forever).
        """
        direction = direction or RIGHT
        buff = buff if buff is not None else MED_SMALL_BUFF
        dir_name = _DIR_NAMES.get(direction, 'right')
        # Snapshot the initial center of self so we can compute deltas
        _init_cx, _init_cy = self.center(start)
        _init_dx = self.styling.dx.at_time(start)
        _init_dy = self.styling.dy.at_time(start)
        _dir = dir_name
        _buff = buff
        def _update(obj, t):
            _, _, mw, mh = obj.bbox(t)
            ox, oy, ow, oh = other.bbox(t)
            ocx, ocy = ox + ow / 2, oy + oh / 2
            targets = {
                'right': (ox + ow + _buff + mw / 2, ocy),
                'left':  (ox - _buff - mw / 2, ocy),
                'down':  (ocx, oy + oh + _buff + mh / 2),
                'up':    (ocx, oy - _buff - mh / 2),
            }
            tx, ty = targets[_dir]
            obj.styling.dx.set_onward(t, tx - _init_cx + _init_dx)
            obj.styling.dy.set_onward(t, ty - _init_cy + _init_dy)
        self.add_updater(_update, start=start, end=end)
        return self

    def follow(self, other, start=0, end=None):
        """Continuously track *other*'s center via an updater."""
        _init_cx, _init_cy = self.center(start)
        _init_dx = self.styling.dx.at_time(start)
        _init_dy = self.styling.dy.at_time(start)
        def _update(obj, t):
            ocx, ocy = other.center(t)
            obj.styling.dx.set_onward(t, ocx - _init_cx + _init_dx)
            obj.styling.dy.set_onward(t, ocy - _init_cy + _init_dy)
        self.add_updater(_update, start=start, end=end)
        return self

    def _scale_anim(self, start, end, scale_func, easing, stay=False):
        """Core helper for scale-based animations around the center."""
        self.styling._scale_origin = self.center(start)
        s, e = start, end
        dur = e - s
        if dur <= 0:
            dur = 1
        f = lambda t, _s=s, _d=dur: scale_func(easing((t - _s) / _d))
        self.styling.scale_x.set(s, e, f, stay=stay)
        self.styling.scale_y.set(s, e, f, stay=stay)
        return self

    def _scale_in_out(self, start, end, fade_in, change_existence, easing):
        """Shared helper for scale-based appear/disappear animations."""
        if fade_in:
            if change_existence:
                self._show_from(start)
            self._scale_anim(start, end, lambda p: p, easing, stay=True)
        else:
            self._scale_anim(start, end, lambda p: 1 - p, easing, stay=True)
            if change_existence:
                self._hide_from(end)
        return self

    def grow_from_center(self, start: float = 0, end: float = 1, change_existence=True, easing=easings.smooth):
        """Animate scaling from 0 to 1 (grow in from nothing), scaling around the object's center."""
        return self._scale_in_out(start, end, True, change_existence, easing)

    def shrink_to_center(self, start: float = 0, end: float = 1, change_existence=True, easing=easings.smooth):
        """Animate scaling from 1 to 0 (shrink out to nothing), scaling around the object's center."""
        return self._scale_in_out(start, end, False, change_existence, easing)

    def elastic_in(self, start: float = 0, end: float = 1, change_existence=True):
        """Scale in with elastic bounce (overshoot then settle)."""
        return self._scale_in_out(start, end, True, change_existence, easings.ease_out_elastic)

    def elastic_out(self, start: float = 0, end: float = 1, change_existence=True):
        """Scale out with elastic bounce."""
        return self._scale_in_out(start, end, False, change_existence, easings.ease_in_elastic)

    def bounce_in(self, start: float = 0, end: float = 1, change_existence=True,
                  easing=easings.ease_out_bounce):
        """Appear by scaling from 0 to 1 with bounce easing.

        Gives a "dropped from above" feel — the object lands and settles with
        small bounces.  Uses ease_out_bounce by default, unlike pop_in (which
        uses a custom overshoot curve) or elastic_in (which uses elastic easing).
        """
        return self._scale_in_out(start, end, True, change_existence, easing)

    def bounce_out(self, start: float = 0, end: float = 1, change_existence=True,
                   easing=easings.ease_in_bounce):
        """Reverse of bounce_in: scale down with bounce while disappearing.

        Scales from 1 to 0 using ease_in_bounce by default, giving a
        "bouncing away" feel before vanishing.
        """
        return self._scale_in_out(start, end, False, change_existence, easing)

    def _zoom_anim(self, start, end, from_scale, to_scale, fade_in, change_existence, easing):
        """Shared helper for zoom_in / zoom_out."""
        dur = end - start
        if dur <= 0:
            return self
        if change_existence and fade_in:
            self._show_from(start)
        self._ensure_scale_origin(start)
        s, fs, ts = start, from_scale, to_scale
        scale_fn = lambda t, _s=s, _d=dur, _fs=fs, _ts=ts: _fs + (_ts - _fs) * easing((t - _s) / _d)
        self.styling.scale_x.set(s, end, scale_fn, stay=True)
        self.styling.scale_y.set(s, end, scale_fn, stay=True)
        base_op = self.styling.fill_opacity.at_time(start)
        if fade_in:
            self.styling.fill_opacity.set(s, end,
                lambda t, _s=s, _d=dur, _bo=base_op: _bo * easing((t - _s) / _d), stay=True)
        else:
            self.styling.fill_opacity.set(s, end,
                lambda t, _s=s, _d=dur, _bo=base_op: _bo * (1 - easing((t - _s) / _d)), stay=True)
        if change_existence and not fade_in:
            self._hide_from(end)
        return self

    def zoom_in(self, start: float = 0, end: float = 1, start_scale=3,
                 change_existence=True, easing=easings.smooth):
        """Zoom in: start large and transparent, end at normal size and opacity."""
        return self._zoom_anim(start, end, start_scale, 1, True, change_existence, easing)

    def zoom_out(self, start: float = 0, end: float = 1, end_scale=3,
                  change_existence=True, easing=easings.smooth):
        """Zoom out: grow large while fading out."""
        return self._zoom_anim(start, end, 1, end_scale, False, change_existence, easing)

    def _scale_from_to_point(self, px, py, start, end, scale_func, change_existence, show_at_start, easing):
        """Shared helper for grow_from_point / shrink_to_point."""
        if change_existence:
            (self._show_from if show_at_start else self._hide_from)(start if show_at_start else end)
        dur = end - start
        if dur <= 0:
            return self
        s = start
        self._ensure_scale_origin(start)
        self.styling._scale_origin = (px, py)
        scale = lambda t, _s=s, _d=dur: scale_func(easing((t - _s) / _d))
        self.styling.scale_x.set(s, end, scale, stay=True)
        self.styling.scale_y.set(s, end, scale, stay=True)
        return self

    def grow_from_point(self, px, py, start: float = 0, end: float = 1,
                         change_existence=True, easing=easings.smooth):
        """Grow from a specific point (px, py) using scale transform."""
        return self._scale_from_to_point(px, py, start, end, lambda p: p, change_existence, True, easing)

    def shrink_to_point(self, px, py, start: float = 0, end: float = 1,
                         change_existence=True, easing=easings.smooth):
        """Shrink to a specific point (px, py) using scale transform. Opposite of grow_from_point."""
        return self._scale_from_to_point(px, py, start, end, lambda p: 1 - p, change_existence, False, easing)

    def appear_from(self, source, start: float = 0, end: float = 1,
                    change_existence=True, easing=easings.smooth):
        """Appear from *source*'s center position, sliding and fading into place.

        source: a VObject (uses get_center) or an (x, y) tuple.
        The object fades in while moving from the source position to its own.
        """
        if change_existence:
            self._show_from(start)
        dur = end - start
        if dur <= 0:
            return self
        if hasattr(source, 'get_center'):
            src_x, src_y = source.get_center(start)
        else:
            src_x, src_y = source
        tgt_x, tgt_y = self.get_center(start)
        off_x, off_y = src_x - tgt_x, src_y - tgt_y
        s, d = start, max(dur, 1e-9)
        # Move all coordinate attrs from source offset back to target
        _easing = easing
        for coor in self._shift_coors():
            ox, oy = coor.at_time(start)
            coor.set(s, end, lambda t, _s=s, _d=d, _ox=ox, _oy=oy, _offx=off_x, _offy=off_y, _e=_easing:
                     (_ox + _offx * (1 - _e((t - _s) / _d)),
                      _oy + _offy * (1 - _e((t - _s) / _d))),
                     stay=True)
        for xa, ya in self._shift_reals():
            ox_val = xa.at_time(start)
            oy_val = ya.at_time(start)
            xa.set(s, end, lambda t, _s=s, _d=d, _o=ox_val, _off=off_x, _e=_easing:
                   _o + _off * (1 - _e((t - _s) / _d)),
                   stay=True)
            ya.set(s, end, lambda t, _s=s, _d=d, _o=oy_val, _off=off_y, _e=_easing:
                   _o + _off * (1 - _e((t - _s) / _d)),
                   stay=True)
        # Fade in opacity
        end_op = self.styling.opacity.at_time(end)
        self.styling.opacity.set(s, end,
            lambda t, _s=s, _d=d, _eo=end_op, _e=_easing: _eo * _e((t - _s) / _d), stay=True)
        return self

    def flip(self, axis='horizontal', start: float = 0, end: float = 0.5, easing=easings.smooth):
        """Quick 3D-like flip by animating scaleX or scaleY to -1 and back."""
        dur = end - start
        if dur <= 0:
            return self
        self._ensure_scale_origin(start)
        s = start
        mid = start + dur / 2
        attr = self.styling.scale_x if axis == 'horizontal' else self.styling.scale_y
        cur = attr.at_time(start)
        attr.set(s, mid, lambda t, _s=s, _m=mid, _c=cur: _c * (1 - 2 * easing((t - _s) / (_m - _s))), stay=True)
        attr.set(mid, end, lambda t, _m=mid, _e=end, _c=cur: _c * (-1 + 2 * easing((t - _m) / (_e - _m))), stay=True)
        return self

    def skew(self, start: float = 0, end: float = 0.5, x_degrees=0, y_degrees=0, easing=easings.smooth):
        """Animate skew (shear) along X and/or Y axes."""
        dur = end - start
        if dur <= 0:
            return self
        s = start
        if x_degrees:
            self.styling.skew_x.set(s, end, lambda t, _s=s, _d=dur, _deg=x_degrees: _deg * easing((t - _s) / _d), stay=True)
        if y_degrees:
            self.styling.skew_y.set(s, end, lambda t, _s=s, _d=dur, _deg=y_degrees: _deg * easing((t - _s) / _d), stay=True)
        return self

    def indicate(self, start: float = 0, end: float = 1, scale_factor=1.2, easing=easings.there_and_back):
        """Briefly scale up and back to draw attention."""
        dur = end - start
        if dur <= 0:
            return self
        self._ensure_scale_origin(start)
        s = start
        scale = lambda t, _s=s, _d=dur: 1 + (scale_factor - 1) * easing((t - _s) / _d)
        self.styling.scale_x.set(s, end, scale)
        self.styling.scale_y.set(s, end, scale)
        return self

    def flash(self, start: float = 0, end: float = 1, color='#FFFF00', easing=easings.there_and_back):
        """Briefly flash a fill color and return to original."""
        original = self.styling.fill.time_func(start)
        assert isinstance(original, tuple)
        _, target_color = attributes.Color(0, color).parse(color)
        assert isinstance(target_color, tuple)
        s, e = start, end
        dur = e - s
        if dur <= 0:
            return self
        self.styling.fill.set(s, e,
            lambda t, _s=s, _d=dur, _o=original, _tc=target_color:
                tuple(o + (g - o) * easing((t - _s) / _d) for o, g in zip(_o, _tc)))
        return self

    def pulse(self, start: float = 0, end: float = 1, scale_factor=1.5, easing=easings.there_and_back):
        """Scale up with a fade, then back. Useful for drawing attention to dots/points."""
        dur = end - start
        if dur <= 0:
            return self
        self._ensure_scale_origin(start)
        s = start
        scale = lambda t, _s=s, _d=dur: 1 + (scale_factor - 1) * easing((t - _s) / _d)
        opacity_f = lambda t, _s=s, _d=dur: 1 - 0.4 * easing((t - _s) / _d)
        self.styling.scale_x.set(s, end, scale)
        self.styling.scale_y.set(s, end, scale)
        self.styling.opacity.set(s, end, opacity_f)
        return self

    def pulsate(self, start: float = 0, end: float = 1, scale_factor=1.3,
                 pulses=3, easing=easings.smooth):
        """Repeated grow/shrink pulsation over [start, end].
        pulses: number of full pulse cycles."""
        dur = end - start
        if dur <= 0:
            return self
        self._ensure_scale_origin(start)
        _s, _d, _sf, _p = start, max(dur, 1e-9), scale_factor, pulses
        def _make_pulse(s0):
            return lambda t, _s=_s, _d=_d, _sf=_sf, _p=_p, _s0=s0, _easing=easing: \
                _s0 * (1 + (_sf - 1) * abs(math.sin(math.pi * _p * _easing((t - _s) / _d))))
        self.styling.scale_x.set(start, end, _make_pulse(self.styling.scale_x.at_time(start)))
        self.styling.scale_y.set(start, end, _make_pulse(self.styling.scale_y.at_time(start)))
        return self

    def pulse_scale(self, start: float = 0, end: float = 1, count=2, amplitude=0.15, easing=easings.smooth):
        """Repeatedly scale up and down by amplitude factor over [start, end].

        Unlike :meth:`pulsate` (which uses abs(sin) and may use opacity) and
        :meth:`emphasize_scale` (a single out-and-back pulse), this method
        produces *count* full up-down cycles using a signed sinusoid, so the
        scale oscillates symmetrically above and below the baseline.

        Parameters
        ----------
        start:
            Animation start time.
        end:
            Animation end time.
        count:
            Number of complete scale oscillation cycles (default 2).
        amplitude:
            Fractional scale deviation from baseline, e.g. 0.15 means the
            object scales between 0.85× and 1.15× its original size.
        easing:
            Easing applied to the normalised time before computing the
            sinusoid (default: smooth).
        """
        dur = end - start
        if dur <= 0:
            return self
        self._ensure_scale_origin(start)
        sx0 = self.styling.scale_x.at_time(start)
        sy0 = self.styling.scale_y.at_time(start)
        _s, _d, _amp, _cnt = start, max(dur, 1e-9), amplitude, count
        def _make_pulse_scale(base):
            return lambda t, _s=_s, _d=_d, _amp=_amp, _cnt=_cnt, _b=base, _e=easing: \
                _b * (1 + _amp * math.sin(2 * math.pi * _cnt * _e((t - _s) / _d)))
        self.styling.scale_x.set(start, end, _make_pulse_scale(sx0))
        self.styling.scale_y.set(start, end, _make_pulse_scale(sy0))
        return self

    def ripple_scale(self, start: float = 0, end: float = 1, num_ripples=3, max_factor=1.3, easing=easings.smooth):
        """Produce multiple decaying scale pulses."""
        self._ensure_scale_origin(start)
        sx0 = self.styling.scale_x.at_time(start)
        sy0 = self.styling.scale_y.at_time(start)
        s, e, dur = start, end, end - start
        if dur <= 0:
            return self
        def _ripple(t, _s=s, _d=dur, _n=num_ripples, _m=max_factor, _e=easing, _sx0=sx0):
            p = _e((t - _s) / _d)
            decay = 1 - p  # amplitude decreases over time
            wave = math.sin(p * _n * 2 * math.pi)
            factor = 1 + (_m - 1) * decay * wave
            return _sx0 * factor
        self.styling.scale_x.set(s, e, _ripple, stay=True)
        self.styling.scale_y.set(s, e, lambda t, _f=_ripple, _r=sy0/sx0 if sx0 else 1: _f(t) * _r, stay=True)
        return self

    def flash_scale(self, factor=1.5, start: float = 0, end: float = 1, easing=easings.smooth):
        """Quickly scale up to *factor* at the midpoint then back to original size.

        Produces a single "flash" or "pop" effect: the object grows to
        *factor* at the midpoint of [start, end] and smoothly returns to its
        original scale by *end*.

        Parameters
        ----------
        factor:
            Peak scale factor reached at the midpoint (default 1.5).
        start:
            Animation start time.
        end:
            Animation end time.
        easing:
            Easing applied to the normalised time (default: smooth).
        """
        dur = end - start
        if dur <= 0:
            return self
        self._ensure_scale_origin(start)
        sx0 = self.styling.scale_x.at_time(start)
        sy0 = self.styling.scale_y.at_time(start)
        _s, _d, _f = start, max(dur, 1e-9), factor
        def _make_flash(base):
            return lambda t, _s=_s, _d=_d, _f=_f, _b=base, _e=easing: \
                _b * (1 + (_f - 1) * math.sin(math.pi * _e((t - _s) / _d)))
        self.styling.scale_x.set(start, end, _make_flash(sx0))
        self.styling.scale_y.set(start, end, _make_flash(sy0))
        return self

    def hover_scale(self, factor=1.2, start: float = 0, end: float = 1):
        """Scale to *factor* at *start* and hold until *end*, then return to 1.0.

        Unlike :meth:`flash_scale` (which peaks at the midpoint and returns),
        this method holds the scaled size for the entire duration and only
        snaps back at *end*.  Useful for hover/emphasis effects where the
        object should stay enlarged while "active".

        Parameters
        ----------
        factor:
            Scale factor to hold during [start, end] (default 1.2).
        start:
            Time at which the object scales to *factor*.
        end:
            Time at which the object returns to its original scale.
        """
        self._ensure_scale_origin(start)
        sx0 = self.styling.scale_x.at_time(start)
        sy0 = self.styling.scale_y.at_time(start)
        self.styling.scale_x.set_onward(start, sx0 * factor)
        self.styling.scale_y.set_onward(start, sy0 * factor)
        self.styling.scale_x.set_onward(end, sx0)
        self.styling.scale_y.set_onward(end, sy0)
        return self

    def spin(self, start: float = 0, end: float = 1, degrees=360, cx=None, cy=None, easing=easings.linear):
        """Continuous rotation by degrees over [start, end]."""
        return self._apply_rotation(start, end,
            self.styling.rotation.at_time(start)[0] + degrees, cx, cy, easing)

    def emphasize(self, start: float = 0, duration=0.8, color='#FFFF00',
                    scale_factor=1.15, easing=easings.there_and_back):
        """Combine a brief scale pulse with a color flash for emphasis."""
        end = start + duration
        self.indicate(start, end, scale_factor=scale_factor, easing=easing)
        self.flash(start, end, color=color, easing=easing)
        return self

    def emphasize_scale(self, start: float = 0, end: float = 1,
                        factor: float = 1.2, easing=easings.there_and_back):
        """Briefly scale up uniformly then return to normal for emphasis.

        Unlike :meth:`pulsate` (which repeats multiple times) and
        :meth:`squash_and_stretch` (which deforms x/y independently),
        this applies a single symmetric scale pulse: both axes grow by
        *factor* at the midpoint and return to their original size by *end*.

        Parameters
        ----------
        start:
            Animation start time.
        end:
            Animation end time.
        factor:
            Peak scale multiplier (e.g. 1.2 → 20% larger at the midpoint).
        easing:
            Easing function (default: there_and_back for a smooth out-and-back).
        """
        dur = end - start
        if dur <= 0:
            return self
        self._ensure_scale_origin(start)
        s = start
        for attr in (self.styling.scale_x, self.styling.scale_y):
            base = attr.at_time(start)
            attr.set(s, end,
                lambda t, _s=s, _d=dur, _b=base: _b * (1 + (factor - 1) * easing((t - _s) / _d)))
        return self

    def glow(self, start: float = 0, end: float = 1, color='#FFD700', radius=10):
        """Add an animated glow effect (stroke pulses outward then fades).

        The stroke expands to ``radius`` extra width at the midpoint, then
        shrinks back while the stroke opacity fades in and out.
        """
        dur = end - start
        if dur <= 0:
            return self
        s, d = start, max(dur, 1e-9)
        orig_sw = self.styling.stroke_width.at_time(start)
        _, glow_rgb = attributes.Color(0, color).parse(color)
        self.styling.stroke.set(s, end,
            lambda t, _rgb=glow_rgb: _rgb, stay=False)
        self.styling.stroke_width.set(s, end,
            lambda t, _s=s, _d=d, _r=radius, _osw=orig_sw: _osw + _r * easings.there_and_back((t - _s) / _d),
            stay=False)
        self.styling.stroke_opacity.set(s, end,
            lambda t, _s=s, _d=d: 0.7 * easings.there_and_back((t - _s) / _d),
            stay=False)
        return self

    def pulse_outline(self, start: float = 0, end: float = 1, color='#FFFF00',
                      max_width=8, cycles=2, easing=easings.smooth):
        """Animate the stroke pulsing between current width and *max_width*.

        The stroke color is set to *color* during the animation and the
        stroke width oscillates sinusoidally for *cycles* full pulses.
        At *end*, the original stroke color and width are restored.
        Returns self.
        """
        dur = end - start
        if dur <= 0:
            return self
        s, d = start, max(dur, 1e-9)
        orig_sw = self.styling.stroke_width.at_time(start)
        _, target_rgb = attributes.Color(0, color).parse(color)
        # Stroke color: target during animation, original after
        self.styling.stroke.set(s, end, lambda t, _rgb=target_rgb: _rgb, stay=False)
        # Stroke width: sinusoidal pulse between orig_sw and max_width
        _osw, _mw, _c = orig_sw, max_width, cycles
        self.styling.stroke_width.set(s, end,
            lambda t, _s=s, _d=d, _osw=_osw, _mw=_mw, _c=_c:
                _osw + (_mw - _osw) * abs(math.sin(math.pi * _c * easing((t - _s) / _d))),
            stay=False)
        return self

    def circumscribe(self, start: float = 0, end: float = 1, buff=SMALL_BUFF, color=None, easing=easings.smooth, **styling_kwargs):
        """Draw and remove a rectangle tracing around this object.
        Returns the rectangle Path (must be added to canvas)."""
        x, y, w, h = self.bbox(start)
        rx, ry = x - buff, y - buff
        rw, rh = w + 2 * buff, h + 2 * buff
        d = f'M{rx},{ry}l{rw},0l0,{rh}l-{rw},0z'
        style = {'stroke': color or '#FFFF00', 'fill_opacity': 0} | styling_kwargs
        from vectormation._shapes import Path
        rect = Path(d, creation=start, **style)
        rect.draw_along(start=start, end=(start + end) / 2, easing=easing, change_existence=True)
        rect.fadeout(start=(start + end) / 2, end=end, change_existence=True)
        return rect

    def wiggle(self, start: float = 0, end: float = 1, amplitude=12, n_wiggles=4, easing=easings.there_and_back):
        """Shake the object horizontally. amplitude is max displacement in pixels."""
        dur = end - start
        if dur <= 0:
            return self
        s = start
        def dx(t):
            progress = (t - s) / dur
            return amplitude * math.sin(2 * math.pi * n_wiggles * progress) * easing(progress)
        return self._apply_shift_effect(start, end, dx_func=dx)

    def swing(self, start: float = 0, end: float = 1, amplitude=15,
              cx=None, cy=None, easing=easings.smooth):
        """Pendulum-like rotation oscillation with natural decay.

        Rotates the object back and forth like a pendulum that gradually comes
        to rest.  The rotation angle follows ``amplitude * sin(2*pi*t) * (1-t)``
        where ``t`` is the normalised time in [0, 1], producing a single-cycle
        swing that decays to zero by the end of the interval.

        Parameters
        ----------
        amplitude:
            Maximum swing angle in degrees (default 15).
        cx, cy:
            Pivot point for the rotation.  Defaults to the top-centre of the
            object's bounding box at ``start``.
        easing:
            Easing applied to the normalised time before computing the
            envelope (default :func:`easings.smooth`).
        """
        dur = end - start
        if dur <= 0:
            return self
        if cx is None or cy is None:
            bx, by, bw, _ = self.bbox(start)
            cx = bx + bw / 2 if cx is None else cx
            cy = by if cy is None else cy
        s = start
        self.styling.rotation.set(s, end,
            lambda t, _s=s, _d=dur, _a=amplitude, _cx=cx, _cy=cy, _ease=easing: (
                _a * math.sin(2 * math.pi * _ease((t - _s) / _d)) * (1 - _ease((t - _s) / _d)),
                _cx, _cy))
        return self

    def wave(self, start: float = 0, end: float = 1, amplitude=20, n_waves=2, direction: str | tuple = 'up', easing=easings.there_and_back):
        """Apply a wave distortion (vertical shift that travels across the object).
        direction: 'up' or 'down' or UP/DOWN constant."""
        dur = end - start
        if dur <= 0:
            return self
        if isinstance(direction, tuple):
            direction = 'up' if direction == UP else 'down'
        s = start
        sign = -1 if direction == 'up' else 1
        def dy(t):
            progress = (t - s) / dur
            return sign * amplitude * math.sin(2 * math.pi * n_waves * progress) * easing(progress)
        return self._apply_shift_effect(start, end, dy_func=dy)

    def grow_from_edge(self, edge: str | tuple = 'bottom', start: float = 0, end: float = 1, change_existence=True, easing=easings.smooth):
        """Grow the object from a specific edge (bottom, top, left, right) or direction constant."""
        if isinstance(edge, tuple):
            edge = _EDGE_NAMES.get(edge, 'bottom')
        if change_existence:
            self._show_from(start)
        bx, by, bw, bh = self.bbox(start)
        origins = {
            'bottom': (bx + bw / 2, by + bh),
            'top':    (bx + bw / 2, by),
            'left':   (bx, by + bh / 2),
            'right':  (bx + bw, by + bh / 2),
        }
        self.styling._scale_origin = origins[edge]
        s, e = start, end
        dur = e - s
        if dur <= 0:
            return self
        scale = lambda t, _s=s, _d=dur: easing((t - _s) / _d)
        self.styling.scale_x.set(s, e, scale, stay=True)
        self.styling.scale_y.set(s, e, scale, stay=True)
        return self

    def _corner_point(self, corner, time):
        """Return the SVG pixel coordinate for a bbox corner direction."""
        from vectormation._constants import DL
        corner = corner or DL
        x, y, w, h = self.bbox(time)
        return (x if corner[0] <= 0 else x + w,
                y if corner[1] <= 0 else y + h)

    def grow_from_corner(self, start=0, end=1, corner=None, change_existence=True, easing=easings.smooth):
        """Grow from zero size anchored at a corner.

        Parameters
        ----------
        start, end:
            Time range for the animation.
        corner:
            Direction tuple indicating which corner to anchor, e.g. UL, UR,
            DL, DR from ``_constants``.  Defaults to DL (bottom-left in SVG).
        change_existence:
            If True, the object is hidden before *start*.
        easing:
            Easing function for the scale interpolation.
        """
        self.styling._scale_origin = self._corner_point(corner, start)
        if change_existence:
            self._show_from(start)
        s, e = start, end
        dur = e - s
        if dur <= 0:
            return self
        scale = lambda t, _s=s, _d=dur: easing((t - _s) / _d)
        self.styling.scale_x.set(s, e, scale, stay=True)
        self.styling.scale_y.set(s, e, scale, stay=True)
        return self

    def shrink_to_corner(self, start=0, end=1, corner=None, change_existence=True, easing=easings.smooth):
        """Shrink to zero size anchored at a corner.

        The reverse of :meth:`grow_from_corner`.  The object scales from its
        current size down to zero, with the specified corner remaining fixed.

        Parameters
        ----------
        start, end:
            Time range for the animation.
        corner:
            Direction tuple indicating which corner to anchor, e.g. UL, UR,
            DL, DR from ``_constants``.  Defaults to DL (bottom-left in SVG).
        change_existence:
            If True, the object is hidden from *end* onward.
        easing:
            Easing function for the scale interpolation.
        """
        self.styling._scale_origin = self._corner_point(corner, start)
        s, e = start, end
        dur = e - s
        if dur <= 0:
            return self
        scale = lambda t, _s=s, _d=dur: 1 - easing((t - _s) / _d)
        self.styling.scale_x.set(s, e, scale, stay=True)
        self.styling.scale_y.set(s, e, scale, stay=True)
        if change_existence:
            self._hide_from(end)
        return self

    def _spiral_anim(self, start, end, n_turns, spiral_in, change_existence, easing):
        """Shared helper for spiral_in / spiral_out."""
        dur = end - start
        if dur <= 0:
            return self
        if change_existence and spiral_in:
            self._show_from(start)
        self._scale_anim(start, end, (lambda p: p) if spiral_in else (lambda p: 1 - p), easing, stay=True)
        cx, cy = self.styling._scale_origin
        s = start
        if spiral_in:
            rot_fn = lambda t, _s=s, _d=dur, _n=n_turns, _cx=cx, _cy=cy: (360 * _n * (1 - easing((t - _s) / _d)), _cx, _cy)
        else:
            rot_fn = lambda t, _s=s, _d=dur, _n=n_turns, _cx=cx, _cy=cy: (360 * _n * easing((t - _s) / _d), _cx, _cy)
        self.styling.rotation.set(s, end, rot_fn, stay=True)
        if change_existence and not spiral_in:
            self._hide_from(end)
        return self

    def spiral_in(self, start: float = 0, end: float = 1, n_turns=1, change_existence=True, easing=easings.smooth):
        """Spiral the object inward from a distance to its current position."""
        return self._spiral_anim(start, end, n_turns, True, change_existence, easing)

    def spiral_out(self, start: float = 0, end: float = 1, n_turns=1, change_existence=True, easing=easings.smooth):
        """Spiral the object outward while shrinking to nothing."""
        return self._spiral_anim(start, end, n_turns, False, change_existence, easing)

    def draw_border_then_fill(self, start: float = 0, end: float = 1,
                              border_fraction=0.5, change_existence=True, easing=easings.smooth):
        """Animate drawing the stroke first, then fading in the fill.

        border_fraction: fraction of [start, end] for the stroke phase.
        """
        if change_existence:
            self._show_from(start)
        mid = start + (end - start) * border_fraction
        # Save the target fill opacity before overriding
        target_fo = self.styling.fill_opacity.at_time(start)
        if not isinstance(target_fo, (int, float)) or target_fo <= 0:
            target_fo = 0.7
        # Phase 1: draw the border (stroke-dashoffset animation)
        self.styling.fill_opacity.set_onward(start, 0)
        self.draw_along(start, mid, easing=easing, change_existence=False)
        s2, e2 = mid, end
        dur2 = e2 - s2
        if dur2 > 0:
            self.styling.fill_opacity.set(s2, e2,
                lambda t, _s=s2, _d=dur2, _tfo=target_fo: _tfo * easing((t - _s) / _d), stay=True)
        else:
            self.styling.fill_opacity.set_onward(mid, target_fo)
        return self

    def blink(self, start: float = 0, end: float | None = None, count: int = 1,
              duration: float = 0.3, easing=easings.smooth, num_blinks: int | None = None):
        """Flash opacity on/off.

        When *num_blinks* is given (with *end*), uses a single step-function
        that rapidly toggles visibility between 0 and 1 for *num_blinks*
        cycles over ``[start, end]``.

        When *end* is given without *num_blinks*, divides [start, end] into
        *count* square-wave cycles: each cycle toggles the opacity from 1 to 0
        and back using the easing.

        When *end* is None (legacy single-blink mode), blinks once over
        *duration* seconds with a smooth fade to 0 and back.
        """
        if num_blinks is not None and end is not None:
            # Step-function blink mode: single .set() with on/off phases
            dur = end - start
            if dur <= 0 or num_blinks <= 0:
                return self
            _s, _d, _nb = start, max(dur, 1e-9), num_blinks

            def _step(t, _s=_s, _d=_d, _nb=_nb):
                progress = easing((t - _s) / _d)
                # Each blink is a full cycle; in the first half of a cycle
                # the object is off (0), in the second half it's on (1)
                phase = (progress * _nb) % 1.0
                return 0.0 if phase < 0.5 else 1.0

            self.styling.opacity.set(start, end, _step, stay=False)
            return self
        if end is not None:
            # Multi-blink square-wave mode
            dur = end - start
            if dur <= 0 or count <= 0:
                return self
            cycle = dur / count
            half = cycle / 2
            for i in range(count):
                t0 = start + i * cycle
                t_mid = t0 + half
                t1 = t0 + cycle
                _t0, _t_mid, _h = t0, t_mid, half
                self.styling.opacity.set(
                    _t0, _t_mid,
                    lambda t, _s=_t0, _hh=_h: 1 - easing((t - _s) / _hh))
                self.styling.opacity.set(
                    _t_mid, t1,
                    lambda t, _m=_t_mid, _hh=_h: easing((t - _m) / _hh),
                    stay=True)
            return self
        # Legacy single-blink mode: flash to 0 and back over *duration*
        if duration <= 0:
            return self
        mid = start + duration / 2
        blink_end = start + duration
        half = duration / 2
        self.styling.opacity.set(start, mid, lambda t, _s=start, _h=half: 1 - easing((t - _s) / _h))
        self.styling.opacity.set(mid, blink_end, lambda t, _m=mid, _h=half: easing((t - _m) / _h))
        return self

    def blink_opacity(self, start: float = 0, end: float = 1, frequency: float = 2,
                       min_opacity: float = 0.0, max_opacity: float = 1.0,
                       easing=easings.smooth):
        """Oscillate opacity between *min_opacity* and *max_opacity*.

        The opacity cycles sinusoidally at the given *frequency* (cycles per
        second) over the interval ``[start, end]``.  The easing function is
        applied to the normalised sine wave so that the transition between
        min and max can be smoothed or shaped.

        Parameters
        ----------
        start, end:
            Time interval during which the oscillation is active.
        frequency:
            Number of full oscillation cycles per second.
        min_opacity, max_opacity:
            The opacity range to oscillate between.
        easing:
            Easing applied to each half-cycle.
        """
        dur = end - start
        if dur <= 0 or frequency <= 0:
            return self
        _s, _d = start, dur
        _min, _max = min_opacity, max_opacity
        _freq = frequency

        def _opacity(t, _s=_s, _d=_d, _min=_min, _max=_max, _freq=_freq):
            progress = (t - _s) / _d
            # sine wave: 0..1..0..-1..0 per cycle; we map to 0..1 range
            wave = 0.5 * (1 - math.cos(2 * math.pi * _freq * progress))
            return _min + (_max - _min) * wave

        self.styling.opacity.set(start, end, _opacity, stay=True)
        return self

    def shimmer(self, start: float = 0, end: float = 1, passes=2, easing=easings.smooth):
        """Create a sweep highlight effect by oscillating opacity.

        The opacity oscillates with brief peaks that sweep through over
        *passes* full cycles during ``[start, end]``.  Uses a raised-cosine
        wave so that opacity dips and peaks create a travelling shimmer.
        Returns self.
        """
        dur = end - start
        if dur <= 0:
            return self
        _s, _d, _p = start, max(dur, 1e-9), passes

        def _shimmer(t, _s=_s, _d=_d, _p=_p):
            progress = easing((t - _s) / _d)
            # Raised cosine wave: oscillates between 0.0 and 1.0
            wave = 0.5 * (1 + math.cos(2 * math.pi * _p * progress))
            # Map to opacity range 0.3..1.0 for a visible shimmer effect
            return 0.3 + 0.7 * wave

        self.styling.opacity.set(start, end, _shimmer, stay=False)
        return self

    def shake(self, start: float = 0, end: float = 0.5, amplitude=5, frequency=20, easing=easings.there_and_back):
        """Rapid random-looking jitter effect for emphasis or error states.

        amplitude: max displacement in pixels.
        frequency: oscillations per unit time.
        """
        dur = end - start
        if dur <= 0:
            return self
        _s, _d, _a, _freq = start, max(dur, 1e-9), amplitude, frequency
        def _dx(t, _s=_s, _d=_d, _a=_a, _freq=_freq, _easing=easing):
            progress = (t - _s) / _d
            return _a * math.sin(_freq * 2 * math.pi * progress) * _easing(progress)
        def _dy(t, _s=_s, _d=_d, _a=_a, _freq=_freq, _easing=easing):
            progress = (t - _s) / _d
            return _a * math.cos(_freq * 2.7 * math.pi * progress) * _easing(progress)
        return self._apply_shift_effect(start, end, _dx, _dy)

    def undulate(self, start: float = 0, end: float = 1, amplitude=0.15, waves=2, easing=easings.smooth):
        """Wavy pulsing scale effect, like a heartbeat or breathing."""
        dur = end - start
        if dur <= 0:
            return self
        self._ensure_scale_origin(start)
        _s, _d = start, max(dur, 1e-9)
        def _scale(t, _s=_s, _d=_d, _a=amplitude, _w=waves, _easing=easing):
            p = (t - _s) / _d
            return 1 + _a * math.sin(p * _w * 2 * math.pi) * (1 - _easing(p))
        self.styling.scale_x.set(start, end, _scale)
        self.styling.scale_y.set(start, end, _scale)
        return self

    def rubber_band(self, start: float = 0, end: float = 1, x_factor=1.3, y_factor=0.7, easing=easings.there_and_back):
        """Elastic stretch: squash and stretch the object, then snap back."""
        dur = end - start
        if dur <= 0:
            return self
        self._ensure_scale_origin(start)
        _s, _d = start, max(dur, 1e-9)
        self.styling.scale_x.set(start, end,
            lambda t, _s=_s, _d=_d, _xf=x_factor, _easing=easing: 1 + (_xf - 1) * _easing((t - _s) / _d), stay=True)
        self.styling.scale_y.set(start, end,
            lambda t, _s=_s, _d=_d, _yf=y_factor, _easing=easing: 1 + (_yf - 1) * _easing((t - _s) / _d), stay=True)
        return self

    def jiggle(self, start: float = 0, end: float = 1, amount=5, easing=easings.smooth):
        """Small random-looking position jitter that decays over time."""
        dur = end - start
        if dur <= 0:
            return self
        _s, _d, _amt = start, max(dur, 1e-9), amount
        def _dx(t, _s=_s, _d=_d, _amt=_amt, _easing=easing):
            p = (t - _s) / _d
            decay = 1 - _easing(p)
            return _amt * math.sin(p * 37.7) * decay
        def _dy(t, _s=_s, _d=_d, _amt=_amt, _easing=easing):
            p = (t - _s) / _d
            decay = 1 - _easing(p)
            return _amt * math.cos(p * 29.3) * decay
        return self._apply_shift_effect(start, end, _dx, _dy)

    def orbit(self, cx, cy, radius=None, start: float = 0, end: float = 1,
              degrees=360, easing=easings.linear):
        """Orbit the object around (cx, cy).
        If radius is None, uses current distance from center."""
        bx, by, bw, bh = self.bbox(start)
        obj_cx, obj_cy = bx + bw / 2, by + bh / 2
        if radius is None:
            radius = math.hypot(obj_cx - cx, obj_cy - cy)
            if radius == 0:
                radius = 100
        start_angle = math.atan2(obj_cy - cy, obj_cx - cx)
        dur = end - start
        if dur <= 0:
            return self
        _s, _d = start, max(dur, 1e-9)
        _rad = math.radians(degrees)
        _sa, _cx, _cy, _r = start_angle, cx, cy, radius
        _ocx, _ocy = obj_cx, obj_cy
        def _pos(t, _s=_s, _d=_d, _rad=_rad, _sa=_sa, _cx=_cx, _cy=_cy,
                 _r=_r, _ocx=_ocx, _ocy=_ocy, _easing=easing):
            progress = _easing((t - _s) / _d)
            angle = _sa + progress * _rad
            target_x = _cx + _r * math.cos(angle)
            target_y = _cy + _r * math.sin(angle)
            return (target_x - _ocx, target_y - _ocy)
        for xa, ya in self._shift_reals():
            xa.add(start, end, lambda t, _f=_pos: _f(t)[0], stay=True)
            ya.add(start, end, lambda t, _f=_pos: _f(t)[1], stay=True)
        for c in self._shift_coors():
            c.add(start, end, _pos, stay=True)
        return self

    def bounce(self, start: float = 0, end: float = 1, height=50, bounces=3, easing=easings.smooth):
        """Bounce the object up and down like a ball."""
        dur = end - start
        if dur <= 0:
            return self
        _s, _d, _h, _b = start, max(dur, 1e-9), height, bounces
        def _dy(t, _s=_s, _d=_d, _h=_h, _b=_b, _easing=easing):
            progress = (t - _s) / _d
            phase = progress * _b * 2 * math.pi
            decay = 1 - progress
            return -abs(math.sin(phase)) * _h * decay * _easing(min(1, progress * 3))
        return self._apply_shift_effect(start, end, dy_func=_dy)

    def spring(self, start: float = 0, end: float = 1, amplitude=30,
                damping=5, frequency=4, axis='y'):
        """Damped spring oscillation: object oscillates with exponential decay.
        axis: 'x', 'y', or 'both'."""
        dur = end - start
        if dur <= 0:
            return self
        _s, _d, _a, _damp, _freq = start, max(dur, 1e-9), amplitude, damping, frequency
        def _osc(t, _s=_s, _d=_d, _a=_a, _damp=_damp, _freq=_freq):
            progress = (t - _s) / _d
            return _a * math.exp(-_damp * progress) * math.sin(2 * math.pi * _freq * progress)
        dx = _osc if axis in ('x', 'both') else None
        dy = _osc if axis in ('y', 'both') else None
        return self._apply_shift_effect(start, end, dx, dy)

    def ripple(self, start: float = 0, count=3, duration=0.5, max_radius=100,
               color='#58C4DD', stroke_width=2):
        """Emit expanding, fading rings from the object's center.
        Returns a VCollection of Circle objects (must be added to canvas)."""
        from vectormation._shapes import Circle as _Circle
        bx, by, bw, bh = self.bbox(start)
        cx, cy = bx + bw / 2, by + bh / 2
        rings = []
        for i in range(count):
            t0 = start + i * (duration / max(count, 1))
            ring = _Circle(r=1, cx=cx, cy=cy, creation=t0,
                           fill_opacity=0, stroke=color, stroke_width=stroke_width)
            ring._show_from(t0)
            dur = duration
            if dur > 0:
                s = t0
                ring.rx.set(s, s + dur, lambda t, _s=s, _d=dur: max_radius * ((t - _s) / _d), stay=True)
                ring.ry.set(s, s + dur, lambda t, _s=s, _d=dur: max_radius * ((t - _s) / _d), stay=True)
                ring.styling.stroke_opacity.set(s, s + dur,
                    lambda t, _s=s, _d=dur: 1 - (t - _s) / _d, stay=True)
            ring.show.set_onward(t0 + dur, False)
            rings.append(ring)
        return VCollection(*rings)

    def animate_dash(self, start=0, end=1, dash_length=10, gap=None, easing=easings.linear):
        """Animate dashes moving along the stroke (marching ants effect).
        Works on any stroked shape (Line, Path, Circle, Rectangle, etc.)."""
        if gap is None:
            gap = dash_length
        total = dash_length + gap
        dur = end - start
        if dur <= 0:
            return self
        s = start
        self.styling.stroke_dasharray.set_onward(s, f'{dash_length} {gap}')
        self.styling.stroke_dashoffset.set(s, end,
            lambda t, _s=s, _d=dur, _tot=total: _tot * (1 - easing((t - _s) / _d)),
            stay=True)
        return self

    # inset(top right bottom left) templates for wipe direction
    _WIPE_TEMPLATES = {
        'right': 'inset(0 {p:.1f}% 0 0)', 'left': 'inset(0 0 0 {p:.1f}%)',
        'down': 'inset(0 0 {p:.1f}% 0)', 'up': 'inset({p:.1f}% 0 0 0)',
    }
    # When reversed, right<->left and down<->up
    _WIPE_REVERSE = {'right': 'left', 'left': 'right', 'down': 'up', 'up': 'down'}

    def wipe(self, direction='right', start: float = 0, end: float = 1,
             easing=easings.smooth, reverse=False):
        """Reveal (or hide if reverse=True) with a clip-path wipe effect.
        direction: 'right', 'left', 'up', 'down'.
        Uses SVG clip-path inset() to animate a clipping rectangle."""
        dur = end - start
        if dur <= 0:
            return self
        s = start
        key = self._WIPE_REVERSE[direction] if reverse else direction
        tmpl = self._WIPE_TEMPLATES[key]
        func = lambda t, _s=s, _d=dur, _t=tmpl: _t.format(p=100 * (1 - easing((t - _s) / _d)))
        self.styling.clip_path.set(s, end, func, stay=True)
        if reverse:
            self._hide_from(end)
        else:
            self._show_from(start)
        return self

    def highlight_border(self, start: float = 0, duration=0.5, color='#FFFF00',
                          width=4, easing=easings.there_and_back):
        """Flash the stroke to briefly highlight the object's border."""
        end = start + duration
        dur = duration
        if dur <= 0:
            return self
        s = start
        self.styling.stroke = attributes.Color(s, color)
        old_w = self.styling.stroke_width.at_time(s)
        self.styling.stroke_width.set(s, end,
            lambda t, _s=s, _d=dur, _ow=old_w, _w=width: _ow + (_w - _ow) * easing((t - _s) / _d),
            stay=True)
        self.styling.stroke_opacity.set(s, end,
            lambda t, _s=s, _d=dur: easing((t - _s) / _d), stay=True)
        return self

    def flash_highlight(self, start: float = 0, end: float = 1, color='#FFFF00',
                        width=3, easing=easings.there_and_back):
        """Briefly highlight the object with a colored border flash using a surrounding rectangle.
        Creates a Rectangle slightly larger than this object whose stroke flashes the given color
        and then fades back out. Returns the highlight rectangle (must be added to canvas).
        """
        from vectormation._shapes import Rectangle  # lazy to avoid circular import
        bx, by, bw, bh = self.bbox(start)
        buff = 6
        rect = Rectangle(bw + 2 * buff, bh + 2 * buff,
                         x=bx - buff, y=by - buff,
                         creation=start, fill_opacity=0,
                         stroke=color, stroke_width=width, stroke_opacity=0)
        dur = end - start
        if dur > 0:
            s = start
            rect.styling.stroke_opacity.set(s, end,
                lambda t, _s=s, _d=dur: easing((t - _s) / _d), stay=True)
        return rect

    def color_cycle(self, colors, start: float = 0, end: float = 1, attr='fill',
                     easing=easings.linear):
        """Cycle through a list of colors over [start, end]."""
        dur = end - start
        if dur <= 0 or len(colors) < 2:
            return self
        src = getattr(self.styling, attr)
        if not isinstance(src, attributes.Color):
            return self
        n = len(colors)
        for i in range(n - 1):
            seg_s = start + dur * i / (n - 1)
            seg_e = start + dur * (i + 1) / (n - 1)
            src.interpolate(attributes.Color(seg_s, colors[i + 1]), seg_s, seg_e, easing=easing)
        return self

    def glitch(self, start: float = 0, end: float = 1, intensity=10, flashes=5):
        """Random glitch effect: brief jitter flashes over [start, end]."""
        dur = end - start
        if dur <= 0 or flashes <= 0:
            return self
        flash_dur = min(0.05, dur / (flashes * 3))
        s = start
        for i in range(flashes):
            t0 = s + dur * (i + 0.5) / flashes
            t1 = t0 + flash_dur
            dx = intensity * (1 if i % 2 == 0 else -1) * (0.5 + (i % 3) * 0.3)
            dy = intensity * (0.3 if i % 3 == 0 else -0.5) * (0.4 + (i % 2) * 0.4)
            for xa, ya in self._shift_reals():
                xa.add(t0, t1, lambda t, _dx=dx: _dx, stay=False)
                ya.add(t0, t1, lambda t, _dy=dy: _dy, stay=False)
            for c in self._shift_coors():
                c.add(t0, t1, lambda t, _dx=dx, _dy=dy: (_dx, _dy), stay=False)
        return self

    def flash_color(self, color='#FFFF00', start: float = 0, duration=0.4,
                     attr='fill'):
        """Flash to a color and back. Quick attention-grabbing effect."""
        end = start + duration
        dur = duration
        if dur <= 0:
            return self
        src = getattr(self.styling, attr)
        if not isinstance(src, attributes.Color):
            return self
        # Get the raw RGB tuple (not the formatted string)
        original_rgb = src.time_func(start)
        flash_c = attributes.Color(start, color)
        mid = start + dur / 2
        restore_c = attributes.Color(start, original_rgb)
        src.interpolate(flash_c, start, mid, easing=easings.linear)
        src.interpolate(restore_c, mid, end, easing=easings.linear)
        return self

    def pulse_color(self, color='#FFFF00', start: float = 0, end: float = 1,
                     pulses=3, attr='fill'):
        """Periodic color pulsing: alternate between current color and color N times."""
        dur = end - start
        if dur <= 0 or pulses <= 0:
            return self
        src = getattr(self.styling, attr)
        if not isinstance(src, attributes.Color):
            return self
        original_rgb = src.time_func(start)
        pulse_dur = dur / pulses
        for i in range(pulses):
            seg_s = start + i * pulse_dur
            seg_mid = seg_s + pulse_dur / 2
            seg_e = seg_s + pulse_dur
            flash_c = attributes.Color(seg_s, color)
            restore_c = attributes.Color(seg_s, original_rgb)
            src.interpolate(flash_c, seg_s, seg_mid, easing=easings.linear)
            src.interpolate(restore_c, seg_mid, seg_e, easing=easings.linear)
        return self

    def color_shift(self, hue_shift=30, start=0, end=1, easing=easings.smooth):
        """Animate shifting the fill color's hue over [start, end].

        Uses HSL color space to rotate the hue by *hue_shift* degrees.

        Parameters
        ----------
        hue_shift:
            Number of degrees to shift the hue (0-360 scale).
        start:
            Start time of the animation.
        end:
            End time of the animation.
        easing:
            Easing function for the transition.

        Returns
        -------
        self
        """
        from vectormation.attributes import _rgb_to_hsl, _hsl_to_rgb
        src = self.styling.fill
        if not isinstance(src, attributes.Color):
            return self
        rgb = src.time_func(start)
        if not isinstance(rgb, tuple) or len(rgb) < 3:
            return self
        h, s, l = _rgb_to_hsl(rgb[0], rgb[1], rgb[2])

        def _color(t, _h=h, _s=s, _l=l, _shift=hue_shift, _e=easing,
                   _start=start, _end=end):
            dur = _end - _start
            progress = _e(max(0.0, min(1.0, (t - _start) / dur))) if dur > 0 else 1.0
            new_h = (_h + _shift / 360.0 * progress) % 1.0
            return _hsl_to_rgb(new_h, _s, _l)

        src.set(start, end, _color, stay=True)
        return self

    def trace_path(self, start: float = 0, end: float = 1, stroke='#58C4DD',
                    stroke_width=2, stroke_opacity=0.6, samples=60):
        """Return a Path that traces this object's center over [start, end].
        The path draws itself progressively. Must be added to the canvas."""
        from vectormation._shapes import Path
        dur = end - start
        if dur <= 0:
            return Path('', x=0, y=0)
        s = start
        obj = self
        def _compute_d(time, _s=s, _dur=dur, _obj=obj, _n=samples):
            progress = min(1, (time - _s) / _dur) if _dur > 0 else 1
            n_pts = max(1, int(progress * _n))
            parts = []
            for i in range(n_pts + 1):
                t = _s + _dur * i / _n
                if t > time:
                    break
                bx, by, bw, bh = _obj.bbox(t)
                cx, cy = bx + bw / 2, by + bh / 2
                parts.append(f'{"M" if i == 0 else "L"}{cx:.1f} {cy:.1f}')
            return ' '.join(parts) if parts else ''
        path = Path('', x=0, y=0, creation=start, stroke=stroke,
                    stroke_width=stroke_width, stroke_opacity=stroke_opacity,
                    fill_opacity=0)
        path.d.set(s, end, _compute_d, stay=True)
        path._show_from(start)
        return path

    def apply_matrix(self, matrix, start: float = 0):
        """Apply a 2x2 transformation matrix [[a, b], [c, d]] via SVG matrix transform.
        matrix: a 2x2 list/tuple, e.g. [[1, 0.5], [0, 1]] for shear."""
        a, b = matrix[0]
        c, d = matrix[1]
        self.styling.matrix.set_onward(start, f'matrix({a},{c},{b},{d},0,0)')
        return self

    def reflect(self, axis='vertical', start_time: float = 0):
        """Mirror/reflect the object across an axis through its center.

        axis: 'vertical' (flip left-right), 'horizontal' (flip top-bottom).
        Applies an instant SVG transform (no animation).
        """
        bx, by, bw, bh = self.bbox(start_time)
        self.styling._scale_origin = (bx + bw / 2, by + bh / 2)
        attr = self.styling.scale_x if axis == 'vertical' else self.styling.scale_y
        attr.set_onward(start_time, -attr.at_time(start_time))
        return self

    def squish(self, start: float = 0, end: float = 1, axis='x', factor=0.5,
                easing=easings.smooth):
        """Squish the object along an axis and bounce back.
        axis: 'x' or 'y'. factor: squish amount (0=flat, 1=no change).
        The complementary axis stretches to compensate (preserves visual area)."""
        dur = end - start
        if dur <= 0:
            return self
        bx, by, bw, bh = self.bbox(start)
        self.styling._scale_origin = (bx + bw / 2, by + bh / 2)
        sx0 = self.styling.scale_x.at_time(start)
        sy0 = self.styling.scale_y.at_time(start)
        _s, _d, _f = start, max(dur, 1e-9), factor
        def _squeeze(t, _s=_s, _d=_d, _f=_f, _easing=easing):
            return 1 + (_f - 1) * math.sin(math.pi * _easing((t - _s) / _d))
        def _make_squish(base):
            return lambda t, _b=base: _b * _squeeze(t)
        def _make_compensate(base):
            return lambda t, _b=base: _b / _squeeze(t) if _squeeze(t) > 1e-9 else _b
        primary = (self.styling.scale_x, sx0) if axis == 'x' else (self.styling.scale_y, sy0)
        compen = (self.styling.scale_y, sy0) if axis == 'x' else (self.styling.scale_x, sx0)
        primary[0].set(start, end, _make_squish(primary[1]), stay=False)
        compen[0].set(start, end, _make_compensate(compen[1]), stay=False)
        return self

    def squash_and_stretch(self, start: float = 0, end: float = 1,
                           factor: float = 1.3, easing=easings.smooth):
        """Classic animation squash-and-stretch: scales x by *factor* while
        y scales by 1/factor (preserving area), then returns to normal.

        The first half squashes/stretches to the peak deformation, the second
        half returns to the original shape.  The effect creates a bouncy,
        organic feel often used when objects land or are hit.

        Parameters
        ----------
        start, end:
            Animation time window.
        factor:
            Peak horizontal scale factor (>1 = wide/squashed).  The vertical
            axis scales by 1/factor to preserve visual area.
        easing:
            Controls the acceleration of the deformation curve.
        """
        dur = end - start
        if dur <= 0:
            return self
        bx, by, bw, bh = self.bbox(start)
        cx, cy = bx + bw / 2, by + bh / 2
        self.styling._scale_origin = (cx, cy)
        sx0 = self.styling.scale_x.at_time(start)
        sy0 = self.styling.scale_y.at_time(start)
        _s, _d, _f, _sx0, _sy0 = start, max(dur, 1e-9), factor, sx0, sy0
        # there_and_back envelope: 0 → peak → 0
        def _ssx(t, _s=_s, _d=_d, _f=_f, _sx0=_sx0, _easing=easing):
            p = _easing((t - _s) / _d)
            envelope = easings.there_and_back(p)
            return _sx0 * (1 + (_f - 1) * envelope)
        def _ssy(t, _s=_s, _d=_d, _f=_f, _sy0=_sy0, _easing=easing):
            p = _easing((t - _s) / _d)
            envelope = easings.there_and_back(p)
            peak = 1 + (_f - 1) * envelope
            return _sy0 / peak if peak > 1e-9 else _sy0
        self.styling.scale_x.set(start, end, _ssx, stay=False)
        self.styling.scale_y.set(start, end, _ssy, stay=False)
        return self

    def warp(self, start: float = 0, end: float = 1, amplitude=0.15, frequency=3,
             easing=easings.smooth):
        """Wobbly distortion effect — alternating scale_x/scale_y oscillation.
        Creates a jelly-like warping motion that resolves back to normal."""
        dur = end - start
        if dur <= 0:
            return self
        bx, by, bw, bh = self.bbox(start)
        cx, cy = bx + bw / 2, by + bh / 2
        self.styling._scale_origin = (cx, cy)
        sx0 = self.styling.scale_x.at_time(start)
        sy0 = self.styling.scale_y.at_time(start)
        _s, _d = start, max(dur, 1e-9)
        _a, _f, _sx0, _sy0 = amplitude, frequency, sx0, sy0
        def _wx(t, _s=_s, _d=_d, _a=_a, _f=_f, _sx0=_sx0, _easing=easing):
            p = _easing((t - _s) / _d)
            envelope = math.sin(math.pi * p)  # 0→1→0
            wave = math.sin(2 * math.pi * _f * p)
            return _sx0 * (1 + _a * envelope * wave)
        def _wy(t, _s=_s, _d=_d, _a=_a, _f=_f, _sy0=_sy0, _easing=easing):
            p = _easing((t - _s) / _d)
            envelope = math.sin(math.pi * p)
            wave = math.cos(2 * math.pi * _f * p)  # phase-shifted from x
            return _sy0 * (1 + _a * envelope * wave)
        self.styling.scale_x.set(start, end, _wx, stay=False)
        self.styling.scale_y.set(start, end, _wy, stay=False)
        return self

    def swirl(self, start: float = 0, end: float = 1, turns=1, shrink=True,
               easing=easings.smooth):
        """Swirling rotation with optional shrink and grow back.
        Creates a vortex-like effect."""
        dur = end - start
        if dur <= 0:
            return self
        self._ensure_scale_origin(start)
        _s, _d, _turns = start, max(dur, 1e-9), turns
        _r0 = self.styling.rotation.at_time(start)  # (degrees, cx, cy)
        _deg0 = _r0[0] if isinstance(_r0, tuple) else _r0
        # Use rotation center from bbox
        bx, by, bw, bh = self.bbox(start)
        _rcx, _rcy = bx + bw / 2, by + bh / 2
        # Rotation
        self.styling.rotation.set(start, end,
            lambda t, _s=_s, _d=_d, _turns=_turns, _deg0=_deg0, _rcx=_rcx, _rcy=_rcy, _easing=easing:
                (_deg0 + 360 * _turns * _easing((t - _s) / _d), _rcx, _rcy),
            stay=False)
        if shrink:
            def _make_scale(s0):
                return lambda t, _s=_s, _d=_d, _s0=s0, _easing=easing: \
                    _s0 * (1 - 0.5 * math.sin(math.pi * _easing((t - _s) / _d)))
            self.styling.scale_x.set(start, end, _make_scale(self.styling.scale_x.at_time(start)), stay=False)
            self.styling.scale_y.set(start, end, _make_scale(self.styling.scale_y.at_time(start)), stay=False)
        return self

    def heartbeat(self, start: float = 0, end: float = 1, beats=3,
                   scale_factor=1.3, easing=easings.smooth):
        """ECG-style double-pulse heartbeat: two quick scale bumps (lub-dub)
        followed by a rest pause, repeated *beats* times.

        Each beat occupies ``duration / beats`` seconds and consists of:
          - A first sharp pulse (the "lub") reaching *scale_factor*,
          - A slightly smaller second pulse (the "dub") at 75% amplitude,
          - A rest period at baseline scale.

        Parameters
        ----------
        start, end:
            Animation time window.
        beats:
            Number of lub-dub cycles.
        scale_factor:
            Peak scale multiplier for the first (stronger) pulse.
        easing:
            Easing applied to each individual pulse envelope.
        """
        dur = end - start
        if dur <= 0:
            return self
        self._ensure_scale_origin(start)
        sx0 = self.styling.scale_x.at_time(start)
        sy0 = self.styling.scale_y.at_time(start)
        _s, _d, _sf, _beats = start, max(dur, 1e-9), scale_factor, beats

        def _ecg_scale(t, _s=_s, _d=_d, _sf=_sf, _beats=_beats,
                       _easing=easing):
            beat_dur = _d / _beats
            # Position within the current beat (0 to 1)
            local = ((t - _s) % beat_dur) / beat_dur
            # First pulse ("lub"): 0.0 - 0.25
            if local < 0.25:
                p = _easing(local / 0.25)
                return 1 + (_sf - 1) * math.sin(math.pi * p)
            # Second pulse ("dub"): 0.30 - 0.55, at 75% amplitude
            elif 0.30 <= local < 0.55:
                p = _easing((local - 0.30) / 0.25)
                return 1 + (_sf - 1) * 0.75 * math.sin(math.pi * p)
            # Rest phase
            else:
                return 1.0

        def _make_ecg(base):
            return lambda t, _base=base, _fn=_ecg_scale: _base * _fn(t)

        self.styling.scale_x.set(start, end, _make_ecg(sx0))
        self.styling.scale_y.set(start, end, _make_ecg(sy0))
        return self

    def breathe(self, start: float = 0, end: float = 1, amplitude=0.08,
                speed=1.0, easing=easings.smooth):
        """Gentle, continuous breathing animation — steady scale oscillation.

        The object smoothly scales up and down in a calm, rhythmic pattern
        without decay, simulating natural breathing.  Unlike :meth:`pulsate`
        (which uses abs(sin) and is intended as a one-shot attention grab)
        and :meth:`undulate` (which decays over time), ``breathe`` produces
        a steady oscillation that looks natural for the entire duration.

        Parameters
        ----------
        start, end:
            Time interval for the animation.
        amplitude:
            Fractional scale deviation from baseline (e.g. 0.08 means the
            object scales between 0.92x and 1.08x).
        speed:
            Breathing cycles per second (default 1.0).
        easing:
            Easing applied to normalised time before computing the oscillation.
        """
        dur = end - start
        if dur <= 0:
            return self
        self._ensure_scale_origin(start)
        sx0 = self.styling.scale_x.at_time(start)
        sy0 = self.styling.scale_y.at_time(start)
        _s, _d, _amp, _spd = start, max(dur, 1e-9), amplitude, speed

        def _make_breathe(base):
            return lambda t, _s=_s, _d=_d, _amp=_amp, _spd=_spd, _b=base, _e=easing: \
                _b * (1 + _amp * math.sin(2 * math.pi * _spd * _e((t - _s) / _d) * _d))
        self.styling.scale_x.set(start, end, _make_breathe(sx0))
        self.styling.scale_y.set(start, end, _make_breathe(sy0))
        return self

    def pendulum(self, start: float = 0, end: float = 1, amplitude=20,
                 oscillations=4, cx=None, cy=None, easing=easings.smooth):
        """Multi-cycle pendulum oscillation with exponential amplitude decay.

        Rotates the object back and forth like a pendulum that gradually loses
        energy.  Unlike :meth:`swing` (a single decaying cycle) this method
        performs multiple oscillations with exponential damping, giving a more
        realistic physical feel.

        Parameters
        ----------
        start, end:
            Time interval for the animation.
        amplitude:
            Initial swing angle in degrees (default 20).
        oscillations:
            Number of full back-and-forth cycles (default 4).
        cx, cy:
            Pivot point for the rotation.  Defaults to the top-centre of the
            object's bounding box (like hanging from a hook).
        easing:
            Easing applied to normalised time before computing the envelope.
        """
        dur = end - start
        if dur <= 0:
            return self
        if cx is None or cy is None:
            bx, by, bw, _ = self.bbox(start)
            cx = bx + bw / 2 if cx is None else cx
            cy = by if cy is None else cy
        _s, _d, _a, _n = start, max(dur, 1e-9), amplitude, oscillations
        _cx, _cy = cx, cy

        def _rot(t, _s=_s, _d=_d, _a=_a, _n=_n, _cx=_cx, _cy=_cy, _e=easing):
            p = _e((t - _s) / _d)
            decay = math.exp(-3 * p)
            angle = _a * math.sin(2 * math.pi * _n * p) * decay
            return (angle, _cx, _cy)

        self.styling.rotation.set(start, end, _rot)
        return self

    # Shared inset templates for typewriter_reveal / typewriter_delete.
    # Each maps a percentage (0 = no clip, 100 = fully clipped) to an
    # ``inset()`` CSS clip-path value.
    _TYPEWRITER_TEMPLATES = {
        'right': lambda pct: f'inset(0 {pct:.1f}% 0 0)',
        'left':  lambda pct: f'inset(0 0 0 {pct:.1f}%)',
        'down':  lambda pct: f'inset(0 0 {pct:.1f}% 0)',
        'up':    lambda pct: f'inset({pct:.1f}% 0 0 0)',
    }

    def _typewriter_clip(self, start, end, direction, easing, reveal):
        """Shared logic for typewriter_reveal / typewriter_delete."""
        dur = end - start
        if dur <= 0:
            return self
        if reveal:
            self._show_from(start)
        else:
            self._hide_from(end)
        _s, _d = start, max(dur, 1e-9)
        tmpl = self._TYPEWRITER_TEMPLATES.get(
            direction, self._TYPEWRITER_TEMPLATES['right'])
        if reveal:
            def _clip(t, _s=_s, _d=_d, _tmpl=tmpl, _e=easing):
                return _tmpl(100 * (1 - _e((t - _s) / _d)))
        else:
            def _clip(t, _s=_s, _d=_d, _tmpl=tmpl, _e=easing):
                return _tmpl(100 * _e((t - _s) / _d))
        self.styling.clip_path.set(start, end, _clip, stay=True)
        return self

    def typewriter_reveal(self, start: float = 0, end: float = 1,
                          direction='right', easing=easings.smooth):
        """Progressively reveal the object with a clip-path sweep.

        Uses ``clip-path: inset()`` to gradually uncover the object from one
        edge, creating a typewriter-like or curtain reveal effect.  Unlike
        :meth:`wipe` (which animates a closing inset and can reverse), this
        method always reveals from fully hidden to fully visible, and the
        object is hidden before *start* and shown from *start* onward.

        Parameters
        ----------
        start, end:
            Time interval for the reveal animation.
        direction:
            Which edge the reveal sweeps from: ``'right'`` (left-to-right
            reveal), ``'left'`` (right-to-left), ``'down'`` (top-to-bottom),
            ``'up'`` (bottom-to-top).
        easing:
            Easing function for the sweep progress.

        Returns
        -------
        self
        """
        return self._typewriter_clip(start, end, direction, easing, reveal=True)

    def cross_out(self, start: float = 0, end: float = 0.5, color='#FC6255',
                   stroke_width=4, buff=5):
        """Draw an X across this object. Returns the Cross VCollection (add to canvas)."""
        from vectormation._composites import Cross
        bx, by, bw, bh = self.bbox(start)
        cx, cy = bx + bw / 2, by + bh / 2
        size = max(bw, bh) + buff * 2
        cross = Cross(size=size, cx=cx, cy=cy, creation=start,
                       stroke=color, stroke_width=stroke_width)
        cross.write(start, end)
        return cross

    def focus_on(self, target=(960, 540), start: float = 0, end: float = 1,
                  easing=easings.smooth):
        """Move this object to a target position (or another object's position).
        target: (x, y) tuple or a VObject whose center to move to."""
        dur = end - start
        if dur <= 0:
            return self
        if hasattr(target, 'get_center'):
            tx, ty = target.get_center(start)
        else:
            tx, ty = target
        cx, cy = self.get_center(start)
        ddx, ddy = tx - cx, ty - cy
        _s, _d = start, max(dur, 1e-9)
        for xa, ya in self._shift_reals():
            xa.add(start, end,
                lambda t, _s=_s, _d=_d, _dx=ddx, _easing=easing: _dx * _easing((t - _s) / _d),
                stay=True)
            ya.add(start, end,
                lambda t, _s=_s, _d=_d, _dy=ddy, _easing=easing: _dy * _easing((t - _s) / _d),
                stay=True)
        for c in self._shift_coors():
            c.add(start, end,
                lambda t, _s=_s, _d=_d, _dx=ddx, _dy=ddy, _easing=easing:
                    (_dx * _easing((t - _s) / _d), _dy * _easing((t - _s) / _d)),
                stay=True)
        return self

    def broadcast(self, start: float = 0, duration=0.5, num_copies=3,
                   max_scale=3, color=None):
        """Emit expanding, fading copies from this object's center.
        Returns a VCollection of copies (must be added to canvas)."""

        copies = []
        for i in range(num_copies):
            t0 = start + i * (duration / max(num_copies, 1))
            t1 = t0 + duration / max(num_copies, 1)
            copy = deepcopy(self)
            copy._ensure_scale_origin(t0)
            copy.show.set_onward(0, False)
            copy.show.set_onward(t0, True)
            sx0 = copy.styling.scale_x.at_time(t0)
            sy0 = copy.styling.scale_y.at_time(t0)
            _s, _d = t0, max(t1 - t0, 1e-9)
            _sx0, _sy0, _ms = sx0, sy0, max_scale
            copy.styling.scale_x.set(t0, t1,
                lambda t, _s=_s, _d=_d, _sx0=_sx0, _ms=_ms:
                    _sx0 * (1 + (_ms - 1) * ((t - _s) / _d)),
                stay=True)
            copy.styling.scale_y.set(t0, t1,
                lambda t, _s=_s, _d=_d, _sy0=_sy0, _ms=_ms:
                    _sy0 * (1 + (_ms - 1) * ((t - _s) / _d)),
                stay=True)
            copy.styling.fill_opacity.set(t0, t1,
                lambda t, _s=_s, _d=_d: max(0, 1 - (t - _s) / _d), stay=True)
            copy.styling.stroke_opacity.set(t0, t1,
                lambda t, _s=_s, _d=_d: max(0, 1 - (t - _s) / _d), stay=True)
            if color:
                copy.styling.stroke.set_onward(t0, color)
                copy.styling.fill.set_onward(t0, color)
            copy.show.set_onward(t1, False)
            copies.append(copy)
        return VCollection(*copies)

    def stamp(self, time: float = 0, opacity=0.3):
        """Leave a faded copy (ghost) at the current position. Returns the copy (add to canvas)."""

        ghost = deepcopy(self)
        ghost.styling.fill_opacity.set_onward(time, opacity)
        ghost.styling.stroke_opacity.set_onward(time, opacity)
        # Freeze position: remove all animations after this time
        ghost.show.set_onward(time, True)
        return ghost

    def trail(self, start: float = 0, end: float = 1, num_copies=5, fade=True):
        """Leave fading ghost copies at intervals during [start, end].
        Returns a list of ghost VObjects (must be added to canvas separately)."""

        ghosts = []
        for i in range(num_copies):
            t = start + (end - start) * (i + 1) / (num_copies + 1)
            ghost = deepcopy(self)
            # Freeze at position at time t
            for xa, ya in ghost._shift_reals():
                xa.set_onward(t, xa.at_time(t))
                ya.set_onward(t, ya.at_time(t))
            for c in ghost._shift_coors():
                c.set_onward(t, c.at_time(t))
            ghost.show.set_onward(0, False)
            ghost.show.set_onward(t, True)
            if fade:
                opacity = 0.1 + 0.3 * (i / max(num_copies - 1, 1))
                ghost.styling.fill_opacity.set_onward(t, opacity)
                ghost.styling.stroke_opacity.set_onward(t, opacity)
            ghosts.append(ghost)
        return ghosts

    def dim(self, start: float = 0, end: float | None = None, opacity=0.3, easing=easings.smooth):
        """Reduce fill and stroke opacity (to de-emphasize). Use undim() to restore."""
        for attr in (self.styling.fill_opacity, self.styling.stroke_opacity):
            if end is None:
                attr.set_onward(start, opacity)
            else:
                dur = end - start
                if dur <= 0:
                    return self
                cur = attr.at_time(start)
                s = start
                attr.set(s, end,
                    lambda t, _s=s, _d=dur, _c=cur, _o=opacity: _c + (_o - _c) * easing((t - _s) / _d), stay=True)
        return self

    def undim(self, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Restore full opacity (undo dim)."""
        return self.dim(start=start, end=end, opacity=1.0, easing=easing)

    def clone(self, offset_x=0, offset_y=0, *, count=None, dx=0, dy=0, start_time=0):
        """Create a deep copy of this object, optionally shifted by an offset.

        **Single-copy form** (default)::

            clone(offset_x=0, offset_y=0)

        Returns one independent deep copy of the object shifted by
        *(offset_x, offset_y)* pixels.  This is the primary use-case — a
        convenient ``copy()`` that also moves the duplicate into position.

        **Multi-copy form** (legacy, for backwards compatibility)::

            clone(count=N, dx=step_x, dy=step_y, start_time=t)

        When *count* is given the method returns a :class:`VCollection` of
        *count* clones where the i-th clone is shifted by *(dx*i, dy*i)*
        from the original position.  The original is **not** included.

        Parameters
        ----------
        offset_x:
            Horizontal pixel offset for the single returned clone.
        offset_y:
            Vertical pixel offset for the single returned clone.
        count:
            When provided, switches to multi-copy mode and returns a
            VCollection of *count* clones.
        dx, dy:
            Per-clone step offset used only in multi-copy mode.
        start_time:
            Animation time at which the positional shift is applied in
            multi-copy mode.

        Returns
        -------
        VObject or VCollection
            A single deep copy when *count* is ``None`` (default), or a
            :class:`VCollection` of *count* clones when *count* is given.

        Examples
        --------
        >>> c = Circle(r=50, cx=100, cy=200)
        >>> c2 = c.clone(offset_x=120)          # one copy 120 px to the right
        >>> copies = c.clone(count=3, dx=100)   # three copies stepped by 100 px
        """
        if count is not None:
            clones = []
            for i in range(1, count + 1):
                c = deepcopy(self)
                c.shift(dx=dx * i, dy=dy * i, start_time=start_time)
                clones.append(c)
            return VCollection(*clones)
        c = deepcopy(self)
        if offset_x != 0 or offset_y != 0:
            c.shift(dx=offset_x, dy=offset_y)
        return c

    def get_angle_to(self, other, time=0):
        """Return the angle (in degrees) from this object's center to another's."""
        cx1, cy1 = self.get_center(time)
        cx2, cy2 = other.get_center(time) if hasattr(other, 'get_center') else other
        return math.degrees(math.atan2(cy2 - cy1, cx2 - cx1))

    def align_to(self, other, edge: str | tuple = 'left', start_time: float = 0):
        """Align an edge of this object with the same edge of another.
        edge: 'left', 'right', 'top', 'bottom' or a direction constant (UP, DOWN, LEFT, RIGHT)."""
        if isinstance(edge, tuple):
            edge = _EDGE_NAMES.get(edge, 'left')
        mx, my, mw, mh = self.bbox(start_time)
        ox, oy, ow, oh = other.bbox(start_time)
        offsets = {
            'left': (ox - mx, 0),
            'right': ((ox + ow) - (mx + mw), 0),
            'top': (0, oy - my),
            'bottom': (0, (oy + oh) - (my + mh)),
        }
        dx, dy = offsets[edge]
        self.shift(dx=dx, dy=dy, start_time=start_time)
        return self

    @staticmethod
    def fade_transform(source, target, start: float = 0, end: float = 1):
        """Cross-fade: fade out source while fading in target over [start, end].
        Both objects should already be added to the canvas."""
        source.fadeout(start=start, end=end, change_existence=True)
        target.fadein(start=start, end=end, change_existence=True)

    @staticmethod
    def swap(a, b, start: float = 0, end: float = 1, easing=easings.smooth):
        """Swap positions of two objects over [start, end]."""
        ax, ay, aw, ah = a.bbox(start)
        bx, by, bw, bh = b.bbox(start)
        acx, acy = ax + aw / 2, ay + ah / 2
        bcx, bcy = bx + bw / 2, by + bh / 2
        a.move_to(bcx, bcy, start_time=start, end_time=end, easing=easing)
        b.move_to(acx, acy, start_time=start, end_time=end, easing=easing)

    def set_style(self, start: float = 0, **kwargs):
        """Set multiple styling attributes at once.
        Example: obj.set_style(fill='#f00', stroke_width=2, opacity=0.5)"""
        for name, value in kwargs.items():
            attr = getattr(self.styling, name)
            if isinstance(attr, attributes.Color):
                setattr(self.styling, name, attributes.Color(start, value))
            else:
                attr.set_onward(start, value)
        return self

    @staticmethod
    def _rgb_to_hex(rgb):
        if isinstance(rgb, str):
            return rgb
        if isinstance(rgb, tuple) and len(rgb) == 3:
            return '#{:02x}{:02x}{:02x}'.format(
                int(min(255, max(0, rgb[0]))),
                int(min(255, max(0, rgb[1]))),
                int(min(255, max(0, rgb[2]))))
        return str(rgb)

    def get_fill_color(self, time=0):
        """Return the fill color (hex string) at the given time."""
        return self._rgb_to_hex(self.styling.fill.time_func(time))

    def get_stroke_color(self, time=0):
        """Return the stroke color (hex string) at the given time."""
        return self._rgb_to_hex(self.styling.stroke.time_func(time))

    def get_stroke_width(self, time=0):
        """Return the stroke width at the given time."""
        return self.styling.stroke_width.at_time(time)

    def get_fill_opacity(self, time=0):
        """Return the fill opacity at the given time."""
        return self.styling.fill_opacity.at_time(time)

    def get_stroke_opacity(self, time=0):
        """Return the stroke opacity at the given time."""
        return self.styling.stroke_opacity.at_time(time)

    def animate_style(self, start: float, end: float, easing=easings.smooth, **kwargs):
        """Animate style changes over [start, end].
        Example: obj.animate_style(1, 2, fill='#f00', fill_opacity=0.5, stroke_width=6)"""
        dur = end - start
        if dur <= 0:
            self.set_style(start, **kwargs)
            return self
        for name, target in kwargs.items():
            attr = getattr(self.styling, name)
            if isinstance(attr, attributes.Color):
                attr.interpolate(attributes.Color(start, target), start, end, easing=easing)
            else:
                attr.move_to(start, end, target, easing=easing)
        return self

    def morph_style(self, target_style, start: float, end: float, easing=easings.smooth):
        """Smoothly transition styling attributes to match another object's style.

        Animates fill color, stroke color, stroke_width, fill_opacity, and
        stroke_opacity from their current values at *start* to the values of
        *target_style* at *start*, over the interval [start, end].

        Parameters
        ----------
        target_style:
            Another VObject whose styling values are used as the animation targets.
        start, end:
            Animation time window in seconds.
        easing:
            Easing function (default: smooth).

        Example
        -------
        >>> r1 = Rectangle(100, 50, fill='#f00', stroke='#fff', stroke_width=4)
        >>> r2 = Rectangle(100, 50, fill='#00f', stroke='#ff0', stroke_width=8)
        >>> r1.morph_style(r2, start=1, end=2)
        """
        morph_attrs = ['fill', 'stroke', 'stroke_width', 'fill_opacity', 'stroke_opacity']
        for attr_name in morph_attrs:
            src = getattr(self.styling, attr_name)
            tgt = getattr(target_style.styling, attr_name)
            if isinstance(src, attributes.Color):
                target_color = attributes.Color(start, tgt.time_func(start))
                new_attr = src.interpolate(target_color, start, end, easing=easing)
                setattr(self.styling, attr_name, new_attr)
            else:
                target_val = tgt.at_time(start)
                src.move_to(start, end, target_val, easing=easing)
        return self

    def become(self, other, time: float = 0):
        """Copy another object's styling at *time*, applied from *time* onward."""
        for attr_name in style._STYLES:
            src = getattr(other.styling, attr_name)
            dst = getattr(self.styling, attr_name)
            val = src.time_func(time) if isinstance(src, attributes.Color) else src.at_time(time)
            dst.set_onward(time, val)
        return self

    def scale(self, factor, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Scale the object by *factor*. Instant if end is None, animated otherwise."""
        return self.stretch(factor, factor, start, end, easing)

    def set_fill(self, color=None, opacity=None, start: float = 0, end: float | None = None, easing=easings.smooth, color_space='rgb'):
        """Set fill color and/or opacity. Animated if end is given."""
        if color is not None:
            if end is None:
                self.styling.fill = attributes.Color(start, color)
            else:
                self.set_color(start, end, fill=color, easing=easing, color_space=color_space)
        if opacity is not None:
            if end is None:
                self.styling.fill_opacity.set_onward(start, opacity)
            else:
                self.styling.fill_opacity.move_to(start, end, opacity, easing=easing)
        return self

    def set_stroke(self, color=None, width=None, opacity=None, start: float = 0, end: float | None = None, easing=easings.smooth, color_space='rgb'):
        """Set stroke color, width, and/or opacity. Animated if end is given."""
        if color is not None:
            if end is None:
                self.styling.stroke = attributes.Color(start, color)
            else:
                self.set_color(start, end, stroke=color, easing=easing, color_space=color_space)
        if width is not None:
            if end is None:
                self.styling.stroke_width.set_onward(start, width)
            else:
                self.styling.stroke_width.move_to(start, end, width, easing=easing)
        if opacity is not None:
            if end is None:
                self.styling.stroke_opacity.set_onward(start, opacity)
            else:
                self.styling.stroke_opacity.move_to(start, end, opacity, easing=easing)
        return self

    def set_stroke_dash(self, pattern, start: float = 0):
        """Set the stroke dash pattern.

        Parameters
        ----------
        pattern:
            A string like ``'5 3'`` or a list/tuple like ``[5, 3]`` specifying
            alternating dash and gap lengths (same as SVG ``stroke-dasharray``).
            Pass an empty string ``''`` or ``None`` to remove dashing.
        start:
            Animation time at which the pattern takes effect.

        Returns
        -------
        self
        """
        if pattern is None:
            pattern_str = ''
        elif isinstance(pattern, (list, tuple)):
            pattern_str = ' '.join(str(v) for v in pattern)
        else:
            pattern_str = str(pattern)
        self.styling.stroke_dasharray.set_onward(start, pattern_str)
        return self

    def set_opacity(self, value, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Set fill_opacity and stroke opacity together. Animated if end is given."""
        for attr in (self.styling.fill_opacity, self.styling.opacity):
            if end is None:
                attr.set_onward(start, value)
            else:
                attr.move_to(start, end, value, easing=easing)
        return self

    def get_opacity(self, time: float = 0):
        """Return the current opacity value at the given time (matches what set_opacity writes)."""
        return self.styling.opacity.at_time(time)

    def animate_opacity(self, start_opacity: float, end_opacity: float,
                        start: float = 0, end: float = 1,
                        easing=easings.smooth):
        """Animate opacity from *start_opacity* to *end_opacity* over [start, end].

        More flexible than :meth:`fadein` (which always goes 0 → current) or
        :meth:`fadeout` (which always goes current → 0).  Use this method when
        you need arbitrary opacity transitions, e.g. from 0.3 to 0.8.

        Parameters
        ----------
        start_opacity:
            Opacity value at the beginning of the animation (0–1).
        end_opacity:
            Opacity value at the end of the animation (0–1).
        start, end:
            Time interval over which the transition occurs.
        easing:
            Easing function (default ``easings.smooth``).

        Returns
        -------
        self

        Example
        -------
        >>> c = Circle()
        >>> c.animate_opacity(0.2, 1.0, start=0, end=1)
        """
        dur = end - start
        if dur <= 0:
            self.styling.opacity.set_onward(start, end_opacity)
            self.styling.fill_opacity.set_onward(start, end_opacity)
            return self
        s, d = start, dur
        sv, ev = start_opacity, end_opacity
        fn = lambda t, _s=s, _d=d, _sv=sv, _ev=ev, _e=easing: _sv + (_ev - _sv) * _e((t - _s) / _d)
        self.styling.opacity.set(start, end, fn, stay=True)
        self.styling.fill_opacity.set(start, end, fn, stay=True)
        return self

    def set_position(self, x, y, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Move the object's center to (x, y). Shorthand for move_to.

        Animated over [start, end] if end is given, instant otherwise.
        """
        return self.move_to(x, y, start_time=start, end_time=end, easing=easing)

    def stretch(self, x_factor: float = 1, y_factor: float = 1, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Non-uniform scale. Instant if end is None, animated otherwise."""
        self._ensure_scale_origin(start)
        for attr, factor in [(self.styling.scale_x, x_factor), (self.styling.scale_y, y_factor)]:
            target = attr.at_time(start) * factor
            if end is None:
                attr.set_onward(start, target)
            else:
                attr.move_to(start, end, target, easing=easing)
        return self

    def match_width(self, other, time: float = 0):
        """Scale this object so its width matches *other*'s width at *time*."""
        _, _, mw, _ = self.bbox(time)
        _, _, ow, _ = other.bbox(time)
        if mw > 0:
            self.scale(ow / mw, start=time)
        return self

    def match_height(self, other, time: float = 0):
        """Scale this object so its height matches *other*'s height at *time*."""
        _, _, _, mh = self.bbox(time)
        _, _, _, oh = other.bbox(time)
        if mh > 0:
            self.scale(oh / mh, start=time)
        return self

    def match_position(self, other, time: float = 0):
        """Move this object so its center matches *other*'s center at *time*."""
        ox, oy = other.center(time) if hasattr(other, 'center') else other
        return self.move_to(ox, oy, start_time=time)

    def telegraph(self, start: float = 0, duration: float = 0.4,
                  scale_factor: float = 1.4, shake_amplitude: float = 8,
                  easing=easings.there_and_back):
        """Quick attention-grabbing burst: scale spike + shake + opacity dip.

        Combines a brief scale-up, a rapid horizontal shake, and an opacity
        dip into a single short "telegraph" pulse.  Useful for signalling
        that something important happened (e.g. an error, a notification).

        Parameters
        ----------
        start:
            Animation start time.
        duration:
            Total duration of the telegraph effect.
        scale_factor:
            Peak scale multiplier at the midpoint.
        shake_amplitude:
            Maximum horizontal displacement in pixels during the shake.
        easing:
            Easing function applied to the scale and opacity envelopes.
        """
        if duration <= 0:
            return self
        end = start + duration
        self._ensure_scale_origin(start)
        _s, _d = start, max(duration, 1e-9)
        # Scale spike
        scale_fn = lambda t, _s=_s, _d=_d, _sf=scale_factor, _e=easing: (
            1 + (_sf - 1) * _e((t - _s) / _d))
        self.styling.scale_x.set(_s, end, scale_fn)
        self.styling.scale_y.set(_s, end, scale_fn)
        # Opacity dip (brief dim at peak)
        opacity_fn = lambda t, _s=_s, _d=_d, _e=easing: (
            1 - 0.3 * _e((t - _s) / _d))
        self.styling.opacity.set(_s, end, opacity_fn)
        # Rapid horizontal shake
        shake_freq = 12
        def _dx(t, _s=_s, _d=_d, _a=shake_amplitude, _freq=shake_freq, _e=easing):
            p = (t - _s) / _d
            return _a * math.sin(_freq * 2 * math.pi * p) * _e(p)
        self._apply_shift_effect(start, end, dx_func=_dx)
        return self

    def skate(self, tx: float, ty: float, start: float = 0, end: float = 1,
              degrees: float = 360, easing=easings.smooth):
        """Slide to a target position while spinning, like skating on ice.

        The object moves from its current center to (tx, ty) while
        simultaneously rotating by *degrees*.

        Parameters
        ----------
        tx, ty:
            Target center position in SVG coordinates.
        start:
            Animation start time.
        end:
            Animation end time.
        degrees:
            Total rotation (in degrees) applied during the slide.
        easing:
            Easing function for both movement and rotation.
        """
        if end <= start:
            return self
        self.center_to_pos(tx, ty, start_time=start, end_time=end, easing=easing)
        self.spin(start=start, end=end, degrees=degrees, easing=easing)
        return self

    def flicker(self, start: float = 0, end: float = 1, frequency: float = 8,
                min_opacity: float = 0.1, easing=easings.smooth):
        """Random-looking opacity flickering, like a failing light bulb.

        The opacity oscillates rapidly between *min_opacity* and 1.0 using
        a pseudo-random pattern built from layered sine waves.  The effect
        fades out toward *end* so the object returns to full opacity.

        Parameters
        ----------
        start:
            Animation start time.
        end:
            Animation end time.
        frequency:
            Base oscillation frequency (higher = faster flicker).
        min_opacity:
            Minimum opacity reached during the deepest flickers.
        easing:
            Decay envelope -- controls how the flicker dies out.
        """
        if end <= start:
            return self
        _s, _d, _freq, _mo = start, max(end - start, 1e-9), frequency, min_opacity
        def _opacity(t, _s=_s, _d=_d, _freq=_freq, _mo=_mo, _e=easing):
            p = (t - _s) / _d
            # Layered sine waves for pseudo-random flicker
            flicker = (math.sin(_freq * 2 * math.pi * p) *
                       math.sin(_freq * 3.7 * math.pi * p) *
                       math.sin(_freq * 5.3 * math.pi * p))
            # flicker is in [-1, 1]; map to [min_opacity, 1]
            # Envelope decays toward end so object returns to full opacity
            envelope = 1 - _e(p)
            depth = (1 - _mo) * max(0, -flicker) * envelope
            return 1 - depth
        self.styling.opacity.set(start, end, _opacity, stay=True)
        return self

    def slingshot(self, tx: float, ty: float, start: float = 0, end: float = 1,
                  pullback: float = 0.3, overshoot: float = 0.15,
                  easing=easings.smooth):
        """Pull back then launch toward the target with overshoot.

        The object first moves away from the target (pullback phase),
        then accelerates through the target and overshoots slightly
        before settling at (tx, ty).

        Parameters
        ----------
        tx, ty:
            Target center position in SVG coordinates.
        start:
            Animation start time.
        end:
            Animation end time.
        pullback:
            Fraction of the total displacement to pull back (0.3 = 30%).
        overshoot:
            Fraction of the total displacement to overshoot past target.
        easing:
            Easing function for the overall progress curve.
        """
        if end <= start:
            return self
        bx, by, bw, bh = self.bbox(start)
        ox, oy = bx + bw / 2, by + bh / 2
        total_dx, total_dy = tx - ox, ty - oy
        _s, _d = start, max(end - start, 1e-9)
        _pb, _os = pullback, overshoot
        _tdx, _tdy = total_dx, total_dy
        def _progress(t, _s=_s, _d=_d, _pb=_pb, _os=_os, _e=easing):
            p = _e((t - _s) / _d)
            # Three phases: pullback (0-0.2), launch (0.2-0.8), settle (0.8-1.0)
            if p < 0.2:
                # Pull back: go from 0 to -pullback
                return -_pb * math.sin(p / 0.2 * math.pi / 2)
            elif p < 0.8:
                # Launch: go from -pullback to (1 + overshoot)
                phase = (p - 0.2) / 0.6
                return -_pb + (-_pb - (1 + _os)) * (math.cos(phase * math.pi) - 1) / 2
            else:
                # Settle: go from (1 + overshoot) to 1
                phase = (p - 0.8) / 0.2
                return (1 + _os) - _os * math.sin(phase * math.pi / 2)
        def _dx(t, _f=_progress, _tdx=_tdx):
            return _f(t) * _tdx
        def _dy(t, _f=_progress, _tdy=_tdy):
            return _f(t) * _tdy
        self._apply_shift_effect(start, end, dx_func=_dx, dy_func=_dy, stay=True)
        return self

    def elastic_bounce(self, start: float = 0, end: float = 1, height=100,
                       bounces=3, squash_factor=1.4, easing=easings.smooth):
        """Bounce the object with squash-and-stretch deformation at each impact.

        Simulates a ball bouncing: the object falls, hits the ground with a
        squash (wide+short), then stretches (narrow+tall) as it rebounds.
        Each successive bounce is smaller than the previous one.

        Parameters
        ----------
        start, end:
            Animation time window.
        height:
            Peak bounce height in pixels for the first bounce.
        bounces:
            Number of bounces.
        squash_factor:
            Peak horizontal scale factor at each impact (>1 = wider).
            The vertical axis squashes by 1/squash_factor.
        easing:
            Easing applied to overall progress.
        """
        dur = end - start
        if dur <= 0:
            return self
        self._ensure_scale_origin(start)
        sx0 = self.styling.scale_x.at_time(start)
        sy0 = self.styling.scale_y.at_time(start)
        _s, _d = start, max(dur, 1e-9)
        _h, _b, _sf = height, bounces, squash_factor
        _sx0, _sy0 = sx0, sy0

        def _bounce_progress(t, _s=_s, _d=_d, _b=_b, _easing=easing):
            """Return (vertical_offset, squash_envelope) at time t.
            vertical_offset: 0 at ground, negative upward.
            squash_envelope: 0 normally, peaks at 1.0 at impact moments."""
            p = _easing((t - _s) / _d)
            if p >= 1.0:
                return (0.0, 0.0)
            # Each bounce occupies a segment; amplitude decays
            phase = p * _b
            bounce_idx = min(int(phase), _b - 1)
            frac = phase - bounce_idx  # 0..1 within each bounce
            # Parabolic arc within each bounce: y = 4*frac*(1-frac) gives 0→1→0
            arc = 4 * frac * (1 - frac)
            # Decay: each bounce is smaller; also fade out near end
            decay = (1.0 - p) / (1 + bounce_idx)
            vert = -arc * decay
            # Squash peaks at impact (frac near 0 or 1)
            # Use a narrow bell curve at frac=0 and frac=1
            impact = max(math.exp(-((frac * 4) ** 2)),
                         math.exp(-(((1 - frac) * 4) ** 2)))
            squash = impact * decay
            return (vert, squash)

        def _dy(t, _h=_h):
            vert, _ = _bounce_progress(t)
            return vert * _h

        def _ssx(t, _sf=_sf, _sx0=_sx0):
            _, squash = _bounce_progress(t)
            return _sx0 * (1 + (_sf - 1) * squash)

        def _ssy(t, _sf=_sf, _sy0=_sy0):
            _, squash = _bounce_progress(t)
            peak = 1 + (_sf - 1) * squash
            return _sy0 / peak if peak > 1e-9 else _sy0

        self._apply_shift_effect(start, end, dy_func=_dy)
        self.styling.scale_x.set(start, end, _ssx, stay=False)
        self.styling.scale_y.set(start, end, _ssy, stay=False)
        return self

    def morph_scale(self, target_scale: float = 2.0, start: float = 0, end: float = 1,
                    overshoot: float = 0.3, oscillations: int = 2,
                    easing=easings.smooth):
        """Scale to *target_scale* with a spring-like overshoot that settles.

        Unlike :meth:`slingshot` (which overshoots in position), this method
        overshoots in *scale*.  The object scales past the target, oscillates
        with decreasing amplitude, and settles exactly at *target_scale*.

        Parameters
        ----------
        target_scale:
            Final scale factor to settle at (e.g. 2.0 = double size).
        start, end:
            Animation time window.
        overshoot:
            Fraction of the scale delta to overshoot (0.3 = 30% past target).
        oscillations:
            Number of damped oscillations before settling.
        easing:
            Easing applied to the overall progress.
        """
        dur = end - start
        if dur <= 0:
            return self
        self._ensure_scale_origin(start)
        sx0 = self.styling.scale_x.at_time(start)
        sy0 = self.styling.scale_y.at_time(start)
        _s, _d = start, max(dur, 1e-9)
        _ts, _os, _osc = target_scale, overshoot, oscillations
        _sx0, _sy0 = sx0, sy0

        # Map overshoot to damping: higher overshoot -> lower damping -> more ring
        _damp = 3.0 / max(_os, 0.01)
        _freq = 2 * math.pi * (_osc + 0.25)

        def _spring_curve(p, _ts=_ts, _damp=_damp, _freq=_freq):
            """Map progress p in [0,1] to a scale multiplier that overshoots
            *_ts* and settles at *_ts*.
            Uses a classic damped oscillation: target + (1-target)*exp(-d*p)*cos(f*p).
            At p=0 this equals 1.0 (original); it decays toward target."""
            if p >= 1.0:
                return _ts
            if p <= 0.0:
                return 1.0
            return _ts + (1.0 - _ts) * math.exp(-_damp * p) * math.cos(_freq * p)

        def _msx(t, _s=_s, _d=_d, _sx0=_sx0, _easing=easing, _sc=_spring_curve):
            p = _easing((t - _s) / _d)
            return _sx0 * _sc(p)

        def _msy(t, _s=_s, _d=_d, _sy0=_sy0, _easing=easing, _sc=_spring_curve):
            p = _easing((t - _s) / _d)
            return _sy0 * _sc(p)

        self.styling.scale_x.set(start, end, _msx, stay=True)
        self.styling.scale_y.set(start, end, _msy, stay=True)
        return self

    def strobe(self, start: float = 0, end: float = 1, flashes: int = 5,
               duty: float = 0.5):
        """Rapid hard on/off blink effect like a strobe light.

        Unlike :meth:`blink_opacity` which uses smooth sinusoidal fading,
        this method produces a sharp square-wave visibility pattern.

        Parameters
        ----------
        start, end:
            Time interval during which the strobe is active.
        flashes:
            Number of on/off cycles.
        duty:
            Fraction of each cycle the object is visible (0.0-1.0).
            0.5 = equal on/off time.  Lower values = shorter flashes.
        """
        dur = end - start
        if dur <= 0 or flashes <= 0:
            return self
        duty = max(0.0, min(1.0, duty))
        _s, _d, _fl, _du = start, dur, flashes, duty

        def _opacity(t, _s=_s, _d=_d, _fl=_fl, _du=_du):
            p = (t - _s) / _d
            cycle_pos = (p * _fl) % 1.0
            return 1.0 if cycle_pos < _du else 0.0

        self.styling.opacity.set(start, end, _opacity, stay=False)
        return self

    def zoom_to(self, canvas, start: float = 0, end: float = 1,
                padding: float = 100, easing=easings.smooth):
        """Animate the camera to zoom in and focus on this object.

        Adjusts the canvas viewBox so that this object fills the frame
        (with *padding* pixels of breathing room).  The aspect ratio of the
        canvas is preserved.  This is a convenience wrapper around the
        camera_zoom/camera_shift primitives that targets a specific object.

        Parameters
        ----------
        canvas:
            The :class:`VectorMathAnim` instance whose camera to control.
        start, end:
            Time interval for the zoom animation.
        padding:
            Extra pixels around the object's bounding box.
        easing:
            Easing function for the camera transition.

        Returns
        -------
        self
        """
        dur = end - start
        if dur <= 0:
            return self
        bx, by, bw, bh = self.bbox(start)
        target_x = bx - padding
        target_y = by - padding
        target_w = bw + 2 * padding
        target_h = bh + 2 * padding
        if target_w <= 0 or target_h <= 0:
            return self
        # Maintain canvas aspect ratio
        aspect = canvas.width / canvas.height
        if target_w / target_h > aspect:
            target_h = target_w / aspect
            target_y = by + bh / 2 - target_h / 2
        else:
            target_w = target_h * aspect
            target_x = bx + bw / 2 - target_w / 2
        canvas.vb_x.move_to(start, end, target_x, easing=easing)
        canvas.vb_y.move_to(start, end, target_y, easing=easing)
        canvas.vb_w.move_to(start, end, target_w, easing=easing)
        canvas.vb_h.move_to(start, end, target_h, easing=easing)
        return self

    def typewriter_delete(self, start: float = 0, end: float = 1,
                          direction='right', easing=easings.smooth):
        """Progressively hide the object with a clip-path sweep.

        The reverse of :meth:`typewriter_reveal`: the object starts fully
        visible and is progressively clipped away, creating a deletion or
        closing-curtain effect.  The object is hidden after *end*.

        Parameters
        ----------
        start, end:
            Time interval for the delete animation.
        direction:
            Which edge the deletion sweeps toward: ``'right'`` (clips from
            left-to-right), ``'left'`` (right-to-left), ``'down'``
            (top-to-bottom), ``'up'`` (bottom-to-top).
        easing:
            Easing function for the sweep progress.

        Returns
        -------
        self
        """
        return self._typewriter_clip(start, end, direction, easing, reveal=False)

    def domino(self, start: float = 0, end: float = 1, direction='right',
               angle: float = 90, easing=easings.smooth):
        """Tip the object over like a falling domino.

        The object rotates around its bottom edge in the given direction,
        as if toppling over.  At the end of the animation the object is
        hidden.

        Parameters
        ----------
        start, end:
            Time interval for the animation.
        direction:
            ``'right'`` to fall rightward (pivot on bottom-right),
            ``'left'`` to fall leftward (pivot on bottom-left).
        angle:
            Rotation angle in degrees (default 90).  Positive values tip
            in the specified direction.
        easing:
            Easing function; defaults to ``smooth`` for a natural-looking fall.

        Returns
        -------
        self
        """
        dur = end - start
        if dur <= 0:
            return self
        self._hide_from(end)
        bx, by, bw, bh = self.bbox(start)
        if direction == 'left':
            pivot_x = bx
            pivot_y = by + bh
            target_angle = -angle
        else:
            pivot_x = bx + bw
            pivot_y = by + bh
            target_angle = angle
        _s, _d = start, max(dur, 1e-9)
        _px, _py, _ta = pivot_x, pivot_y, target_angle

        def _rot(t, _s=_s, _d=_d, _ta=_ta, _px=_px, _py=_py, _e=easing):
            p = _e((t - _s) / _d)
            return (_ta * p, _px, _py)

        self.styling.rotation.set(start, end, _rot, stay=True)
        return self

    def stamp_trail(self, start: float = 0, end: float = 1, count=8,
                    fade_duration=0.5, opacity=0.4):
        """Leave ghostly copies that appear along the path and fade out.

        Unlike ``trail`` which creates copies at fixed moments, stamp_trail
        creates copies that each persist and gradually fade to zero opacity
        over *fade_duration* seconds, producing a smooth afterimage effect.

        Returns a list of ghost VObjects (must be added to canvas separately).
        """
        ghosts = []
        dur = end - start
        if dur <= 0 or count <= 0:
            return ghosts
        for i in range(count):
            t_appear = start + dur * (i + 1) / (count + 1)
            ghost = deepcopy(self)
            # Freeze at position at t_appear
            for xa, ya in ghost._shift_reals():
                xa.set_onward(t_appear, xa.at_time(t_appear))
                ya.set_onward(t_appear, ya.at_time(t_appear))
            for c in ghost._shift_coors():
                c.set_onward(t_appear, c.at_time(t_appear))
            # Hidden before appearance
            ghost.show.set_onward(0, False)
            ghost.show.set_onward(t_appear, True)
            # Fade out over fade_duration
            t_gone = t_appear + fade_duration
            ghost.show.set_onward(t_gone, False)
            fd = max(fade_duration, 1e-9)
            fade_fn = lambda t, _s=t_appear, _fd=fd, _o=opacity: _o * max(0, 1 - (t - _s) / _fd)
            ghost.styling.fill_opacity.set(t_appear, t_gone, fade_fn)
            ghost.styling.stroke_opacity.set(t_appear, t_gone, fade_fn)
            ghosts.append(ghost)
        return ghosts

    def unfold(self, start: float = 0, end: float = 1, direction='right',
               change_existence=True, easing=easings.smooth):
        """Animate the object unfolding from zero width to full size.

        The object scales from 0 to 1 on one axis only, anchored at the
        opposite edge, like paper being unfolded.

        direction: 'right' (unfold leftward anchor), 'left' (rightward anchor),
                   'down' (unfold from top), 'up' (unfold from bottom).
        """
        dur = end - start
        if dur <= 0:
            return self
        if change_existence:
            self._show_from(start)
        bx, by, bw, bh = self.bbox(start)
        # Determine anchor point and which axis to scale
        horizontal = direction in ('left', 'right')
        if direction == 'right':
            self.styling._scale_origin = (bx, by + bh / 2)
        elif direction == 'left':
            self.styling._scale_origin = (bx + bw, by + bh / 2)
        elif direction == 'down':
            self.styling._scale_origin = (bx + bw / 2, by)
        else:  # up
            self.styling._scale_origin = (bx + bw / 2, by + bh)
        scale_fn = lambda t, _s=start, _d=dur, _e=easing: _e((t - _s) / _d)
        if horizontal:
            self.styling.scale_x.set(start, end, scale_fn, stay=True)
        else:
            self.styling.scale_y.set(start, end, scale_fn, stay=True)
        return self

    def glitch_shift(self, start: float = 0, end: float = 1, intensity=20,
                     steps=8, seed=None):
        """Random horizontal displacement with discrete jumps.

        Unlike ``glitch`` which creates brief x+y jitter flashes, glitch_shift
        produces sustained, discrete horizontal offsets that change at each step,
        simulating a digital signal glitch. The displacement returns to zero at
        *end*.

        intensity: maximum horizontal displacement in pixels.
        steps: number of discrete offset changes.
        seed: optional random seed for reproducibility.
        """
        import random
        dur = end - start
        if dur <= 0 or steps <= 0:
            return self
        rng = random.Random(seed)
        step_dur = dur / steps
        for i in range(steps):
            t0 = start + i * step_dur
            t1 = t0 + step_dur
            dx = rng.uniform(-intensity, intensity)
            for xa, _ in self._shift_reals():
                xa.add(t0, t1, lambda t, _dx=dx: _dx, stay=False)
            for c in self._shift_coors():
                c.add(t0, t1, lambda t, _dx=dx: (_dx, 0), stay=False)
        return self

    def wave_through(self, start: float = 0, end: float = 1, amplitude=20,
                     frequency=2, direction='y', easing=easings.smooth):
        """Wave animation: the object follows a sinusoidal path while moving forward.

        The object oscillates perpendicular to the primary movement direction.
        direction: 'y' oscillates vertically while progressing forward,
                   'x' oscillates horizontally while progressing forward.
        amplitude: max displacement in pixels.
        frequency: number of full wave cycles over the duration.
        """
        dur = end - start
        if dur <= 0:
            return self
        _s, _d, _a, _freq = start, max(dur, 1e-9), amplitude, frequency

        def _wave(t, _s=_s, _d=_d, _a=_a, _freq=_freq, _easing=easing):
            progress = (t - _s) / _d
            envelope = _easing(progress) * (1 - _easing(progress)) * 4
            return _a * math.sin(2 * math.pi * _freq * progress) * envelope

        if direction == 'y':
            return self._apply_shift_effect(start, end, dy_func=_wave)
        else:
            return self._apply_shift_effect(start, end, dx_func=_wave)

    def countdown(self, start: float = 0, end: float = 1, from_val=3):
        """For Text objects: display a countdown (from_val, from_val-1, ..., 1).

        Changes the text content at evenly spaced intervals.
        Only works on Text objects (must have a ``text`` attribute of type
        ``attributes.String``).

        Raises TypeError if called on a non-Text object.
        """
        from vectormation._shapes import Text as _Text
        if not isinstance(self, _Text):
            raise TypeError("countdown() can only be called on Text objects")
        dur = end - start
        if dur <= 0 or from_val < 1:
            return self
        step_dur = dur / from_val
        for i in range(from_val):
            t = start + i * step_dur
            val = from_val - i
            self.text.set_onward(t, str(val))
        return self

    def squeeze(self, start: float = 0, end: float = 1, axis='x',
                factor=0.5, easing=easings.smooth):
        """Squeeze the object along one axis, scaling up the other to preserve area.

        axis: 'x' or 'y' — the axis to compress.
        factor: squeeze amount (0.5 means compress to half along that axis).
        The complementary axis scales by 1/factor to preserve visual area.
        Unlike squish(), this animates to the squeezed state and stays there.
        """
        dur = end - start
        if dur <= 0:
            return self
        self._ensure_scale_origin(start)
        sx0 = self.styling.scale_x.at_time(start)
        sy0 = self.styling.scale_y.at_time(start)
        _s, _d, _f = start, max(dur, 1e-9), factor
        compensate = 1.0 / _f if _f > 1e-9 else 1.0

        def _primary(t, _s=_s, _d=_d, _f=_f, _easing=easing):
            progress = _easing((t - _s) / _d)
            return 1 + (_f - 1) * progress

        def _compensate(t, _s=_s, _d=_d, _c=compensate, _easing=easing):
            progress = _easing((t - _s) / _d)
            return 1 + (_c - 1) * progress

        if axis == 'x':
            self.styling.scale_x.set(start, end,
                lambda t, _b=sx0: _b * _primary(t), stay=True)
            self.styling.scale_y.set(start, end,
                lambda t, _b=sy0: _b * _compensate(t), stay=True)
        else:
            self.styling.scale_y.set(start, end,
                lambda t, _b=sy0: _b * _primary(t), stay=True)
            self.styling.scale_x.set(start, end,
                lambda t, _b=sx0: _b * _compensate(t), stay=True)
        return self

    def bind_to(self, other, offset_x=0, offset_y=0, start=0, end=None):
        """Keep this object at a fixed offset relative to another object's center.
        Uses an updater to track other's center and reposition self each frame.
        Returns self."""
        def _bind(obj, time, _other=other, _ox=offset_x, _oy=offset_y):
            bx, by, bw, bh = _other.bbox(time)
            target_x = bx + bw / 2 + _ox
            target_y = by + bh / 2 + _oy
            sx, sy, sw, sh = obj.bbox(time)
            dx = target_x - (sx + sw / 2)
            dy = target_y - (sy + sh / 2)
            if abs(dx) > 0.01 or abs(dy) > 0.01:
                for xa, ya in obj._shift_reals():
                    xa.set_onward(time, xa.at_time(time) + dx)
                    ya.set_onward(time, ya.at_time(time) + dy)
                for c in obj._shift_coors():
                    val = c.at_time(time)
                    c.set_onward(time, (val[0] + dx, val[1] + dy))
        self.add_updater(_bind, start, end)
        return self

    def pin_to(self, other, edge='center', offset_x=0, offset_y=0, start=0, end=None):
        """Anchor this object to a specific edge/corner of *other*.

        Unlike :meth:`bind_to` which tracks the target's center, this tracks
        a specific edge point (e.g. 'top', 'bottom_right') of the target's
        bounding box and maintains the given offset from that point.

        Parameters
        ----------
        other:
            The target object to pin to.
        edge:
            Which point on the target to track. Options: 'center', 'top',
            'bottom', 'left', 'right', 'top_left', 'top_right',
            'bottom_left', 'bottom_right'.
        offset_x, offset_y:
            Additional pixel offset from the computed edge point.
        start, end:
            Time interval during which the updater is active.

        Returns self.
        """
        edge_fn = _EDGE_POINTS.get(edge, _EDGE_POINTS['center'])

        def _pin(obj, time, _other=other, _edge_fn=edge_fn,
                 _ox=offset_x, _oy=offset_y):
            bx, by, bw, bh = _other.bbox(time)
            ex, ey = _edge_fn(bx, by, bw, bh)
            target_x = ex + _ox
            target_y = ey + _oy
            sx, sy, sw, sh = obj.bbox(time)
            dx = target_x - (sx + sw / 2)
            dy = target_y - (sy + sh / 2)
            if abs(dx) > 0.01 or abs(dy) > 0.01:
                for xa, ya in obj._shift_reals():
                    xa.set_onward(time, xa.at_time(time) + dx)
                    ya.set_onward(time, ya.at_time(time) + dy)
                for c in obj._shift_coors():
                    val = c.at_time(time)
                    c.set_onward(time, (val[0] + dx, val[1] + dy))

        self.add_updater(_pin, start, end)
        return self

    def duplicate(self, count=2, direction=RIGHT, buff=MED_SMALL_BUFF):
        """Create count copies of the object arranged in the given direction.
        Returns a VCollection containing the copies (not including self)."""
        col = VCollection(*[deepcopy(self) for _ in range(count)])
        col.arrange(direction=direction, buff=buff)
        return col

    def arc_to(self, x, y, start, end, angle=math.pi / 4, easing=easings.smooth):
        """Animated curved movement to (x, y) following a circular arc.
        angle controls the arc curvature (default PI/4). Uses parametric interpolation."""
        return self.path_arc(x, y, start=start, end=end, angle=angle, easing=easing)

    def typewriter_cursor(self, start, end, blink_rate=0.5, cursor_char='|'):
        """For Text objects: append a blinking cursor character.
        The cursor blinks on/off at blink_rate (seconds per blink cycle).
        Returns self."""
        from vectormation._shapes import Text as _Text
        if not isinstance(self, _Text):
            raise TypeError("typewriter_cursor() can only be called on Text objects")
        _base_text_func = self.text.time_func
        def _blink(t, _s=start, _rate=blink_rate, _char=cursor_char, _base=_base_text_func):
            base = _base(t)
            if int((t - _s) / _rate) % 2 == 0:
                return base + _char
            return base
        self.text.set(start, end, _blink, stay=False)
        return self

    def parallax(self, dx, dy, start=0, end=1, depth_factor=0.5, easing=easings.smooth):
        """Move the object by (dx*depth_factor, dy*depth_factor) instead of the
        full (dx, dy).  This creates a parallax/depth illusion where background
        objects move slower.  Uses shift animation internally.  Returns self."""
        return self.shift(dx=dx * depth_factor, dy=dy * depth_factor,
                          start_time=start, end_time=end, easing=easing)

    _DASH_PRESETS = {
        'solid': '',
        'dashes': '10 5',
        'dots': '2 4',
        'dash_dot': '10 5 2 5',
    }

    def set_dash_pattern(self, pattern='dashes', start=0):
        """Set the stroke-dasharray at a given time.

        Pattern presets: 'solid' -> '', 'dashes' -> '10 5', 'dots' -> '2 4',
        'dash_dot' -> '10 5 2 5'.  Also accepts a custom string.
        Uses set_onward on the stroke_dasharray styling attribute.  Returns self.
        """
        pattern_str = self._DASH_PRESETS.get(pattern, pattern)
        self.styling.stroke_dasharray.set_onward(start, pattern_str)
        return self

    def show_if(self, condition_func, start=0, end=None):
        """Show the object only when condition_func(time) returns True.
        Sets opacity to 0 or 1 based on the condition via a callable.
        Returns self."""
        def _opacity(t):
            return 1 if condition_func(t) else 0
        self.styling.opacity.set_onward(start, _opacity)
        self.styling.fill_opacity.set_onward(start, _opacity)
        if end is not None:
            self.styling.opacity.set_onward(end, self.styling.opacity.at_time(end))
            self.styling.fill_opacity.set_onward(end, self.styling.fill_opacity.at_time(end))
        return self

    @staticmethod
    def surround(other, buff=SMALL_BUFF, rx=6, ry=6, start_time: float = 0, follow=True):
        """Create a rectangle surrounding another object. Returns a Rectangle."""
        return _make_brect(other.bbox, start_time, rx, ry, buff, follow)

    def fade_to_color(self, target_color, start=0, end=1, easing=easings.smooth):
        """Smoothly transition both fill and stroke to target_color over [start, end].
        Returns self."""
        self.set_fill(color=target_color, start=start, end=end, easing=easing)
        self.set_stroke(color=target_color, start=start, end=end, easing=easing)
        return self

    def spin_and_fade(self, start=0, end=1, spins=1.5, direction=1, easing=easings.smooth):
        """Combined animation: rotate and fade out simultaneously over [start, end].
        spins: number of full rotations. direction: 1 = clockwise, -1 = counterclockwise.
        Returns self."""
        degrees = spins * 360 * direction
        self.rotate_by(start, end, degrees, easing=easing)
        self.set_opacity(0, start=start, end=end, easing=easing)
        return self

    def grow_to_size(self, target_width=None, target_height=None, start=0, end=1, easing=easings.smooth):
        """Animate the object to reach a specific width and/or height over [start, end].
        If only one dimension is given, maintain aspect ratio. Returns self."""
        cur_w = self.get_width(start)
        cur_h = self.get_height(start)
        if cur_w <= 0 or cur_h <= 0:
            return self
        if target_width is not None and target_height is not None:
            sx = target_width / cur_w
            sy = target_height / cur_h
            self.stretch(sx, sy, start=start, end=end, easing=easing)
        elif target_width is not None:
            factor = target_width / cur_w
            self.scale(factor, start=start, end=end, easing=easing)
        elif target_height is not None:
            factor = target_height / cur_h
            self.scale(factor, start=start, end=end, easing=easing)
        return self

    def tilt_towards(self, target_x, target_y, max_angle=15, start=0, end=1, easing=easings.smooth):
        """Rotate the object to tilt toward a target point by max_angle degrees.
        Computes the angle from the object's center to (target_x, target_y) and
        rotates in that direction. Returns self."""
        _, cy = self.center(start)
        dy = target_y - cy
        # In SVG coordinates (y-down), positive dy means target is below,
        # so tilt clockwise (positive degrees); negative dy means above.
        tilt = max_angle if dy >= 0 else -max_angle
        self.rotate_by(start, end, tilt, easing=easing)
        return self

    # -- Blend mode --

    _VALID_BLEND_MODES = frozenset({
        'normal', 'multiply', 'screen', 'overlay', 'darken', 'lighten',
        'color-dodge', 'color-burn',
    })

    def set_blend_mode(self, mode, start=0):
        """Set the SVG mix-blend-mode on this object.

        Supported modes: 'normal', 'multiply', 'screen', 'overlay',
        'darken', 'lighten', 'color-dodge', 'color-burn'.

        Parameters
        ----------
        mode:
            One of the supported blend mode strings.
        start:
            Time from which the blend mode is active.

        Returns
        -------
        self
        """
        if mode not in self._VALID_BLEND_MODES:
            raise ValueError(
                f"Unsupported blend mode '{mode}'. "
                f"Must be one of: {', '.join(sorted(self._VALID_BLEND_MODES))}"
            )
        self.styling.mix_blend_mode.set_onward(start, mode)
        return self

    # -- Reveal clip --

    _REVEAL_CLIP_TEMPLATES = {
        'left':   lambda pct: f'inset(0 {pct:.1f}% 0 0)',   # reveals left to right
        'right':  lambda pct: f'inset(0 0 0 {pct:.1f}%)',    # reveals right to left
        'top':    lambda pct: f'inset(0 0 {pct:.1f}% 0)',    # reveals top to bottom
        'bottom': lambda pct: f'inset({pct:.1f}% 0 0 0)',    # reveals bottom to top
    }

    def reveal_clip(self, start=0, end=1, direction='left', easing=easings.smooth):
        """Progressive reveal using SVG clip-path.

        Creates a clip-path inset rect that expands from one side, gradually
        revealing the object.

        Parameters
        ----------
        start, end:
            Time interval for the reveal animation.
        direction:
            Which direction the reveal progresses: ``'left'`` (reveals left
            to right), ``'right'`` (reveals right to left), ``'top'``
            (reveals top to bottom), ``'bottom'`` (reveals bottom to top).
        easing:
            Easing function for the reveal progress.

        Returns
        -------
        self
        """
        dur = end - start
        if dur <= 0:
            return self
        self._show_from(start)
        _s, _d = start, max(dur, 1e-9)
        if direction not in self._REVEAL_CLIP_TEMPLATES:
            raise ValueError(
                f"Unsupported reveal direction '{direction}'. "
                f"Must be one of: {', '.join(sorted(self._REVEAL_CLIP_TEMPLATES))}"
            )
        tmpl = self._REVEAL_CLIP_TEMPLATES[direction]
        def _clip(t, _s=_s, _d=_d, _tmpl=tmpl, _e=easing):
            return _tmpl(100 * (1 - _e((t - _s) / _d)))
        self.styling.clip_path.set(start, end, _clip, stay=True)
        return self

    # -- Repeat animation --

    def repeat_animation(self, method_name, count=2, start=0, end=1, **kwargs):
        """Repeat an animation method *count* times within [start, end].

        Divides the time evenly into *count* sub-intervals and calls
        ``getattr(self, method_name)`` for each with the appropriate
        ``start`` and ``end`` keyword arguments.

        Parameters
        ----------
        method_name:
            Name of an animation method on this object (e.g. ``'pulsate'``,
            ``'shake'``, ``'fadein'``).
        count:
            Number of repetitions.
        start, end:
            Overall time interval.
        **kwargs:
            Extra keyword arguments forwarded to each invocation (excluding
            ``start`` and ``end``).

        Returns
        -------
        self
        """
        if count <= 0:
            return self
        dur = end - start
        if dur <= 0:
            return self
        slice_dur = dur / count
        method = getattr(self, method_name)
        for i in range(count):
            s = start + i * slice_dur
            e = s + slice_dur
            method(start=s, end=e, **kwargs)
        return self

    # -- Elastic scale --

    def elastic_scale(self, start=0, end=1, factor=1.5, easing=easings.smooth):
        """Scale up elastically then bounce back to original size.

        The object overshoots to *factor* at the start and then oscillates
        back to its original scale using a damped cosine envelope.

        Parameters
        ----------
        start, end:
            Time interval for the animation.
        factor:
            Peak scale multiplier at the overshoot.
        easing:
            Easing function for overall progress.

        Returns
        -------
        self
        """
        dur = end - start
        if dur <= 0:
            return self
        self._ensure_scale_origin(start)
        sx0 = self.styling.scale_x.at_time(start)
        sy0 = self.styling.scale_y.at_time(start)
        _s, _d, _f = start, max(dur, 1e-9), factor
        _damp = 6.0
        _freq = 2 * math.pi * 2.5

        def _elastic_envelope(p):
            """Damped cosine: 1 at p=0, oscillates toward 0 at p=1."""
            if p <= 0:
                return 1.0
            if p >= 1:
                return 0.0
            return math.cos(_freq * p) * math.exp(-_damp * p)

        def _make_elastic(s0):
            def _es(t, _s=_s, _d=_d, _f=_f, _s0=s0, _easing=easing):
                p = _easing((t - _s) / _d)
                return _s0 * (1 + (_f - 1) * _elastic_envelope(p))
            return _es

        self.styling.scale_x.set(start, end, _make_elastic(sx0), stay=True)
        self.styling.scale_y.set(start, end, _make_elastic(sy0), stay=True)
        return self

    def snap_to_grid(self, grid_size=50, start=0, end=1, easing=easings.smooth):
        """Animate the object's center to the nearest grid point.

        Computes the nearest grid-aligned position from the current center,
        then uses shift to move there.

        Parameters
        ----------
        grid_size : float
            Spacing of the grid (in pixels).
        start : float
            Animation start time.
        end : float
            Animation end time.
        easing : callable
            Easing function for the movement.

        Returns
        -------
        self
        """
        cx, cy = self.center(start)
        target_x = round(cx / grid_size) * grid_size
        target_y = round(cy / grid_size) * grid_size
        dx = target_x - cx
        dy = target_y - cy
        if dx != 0 or dy != 0:
            self.shift(dx=dx, dy=dy, start_time=start, end_time=end, easing=easing)
        return self

    def add_background(self, color='#000000', opacity=0.5, padding=20, creation=0, z=-1):
        """Create a semi-transparent Rectangle behind the object as a readability backdrop.

        Computes dimensions from the object's bounding box plus padding.
        Returns the Rectangle (the caller should add it to the canvas).

        Parameters
        ----------
        color : str
            Fill color for the background rectangle.
        opacity : float
            Fill opacity for the background rectangle.
        padding : float
            Extra space around the object's bounding box.
        creation : float
            Creation time for the rectangle.
        z : float
            Z-index for the rectangle (default -1, behind most objects).

        Returns
        -------
        Rectangle
            The background rectangle.
        """
        from vectormation._shapes import Rectangle  # lazy to avoid circular import
        x, y, w, h = self.bbox(creation)
        rect = Rectangle(
            width=w + 2 * padding,
            height=h + 2 * padding,
            x=x - padding,
            y=y - padding,
            creation=creation,
            z=z,
            fill=color,
            fill_opacity=opacity,
            stroke_width=0,
        )
        return rect

    def cycle_colors(self, colors, start=0, end=1, easing=easings.linear):
        """Cycle the fill color through a list of colors over [start, end].

        Each color gets an equal time slice. Uses set_fill for each transition.

        Parameters
        ----------
        colors : list[str]
            List of color strings to cycle through.
        start : float
            Animation start time.
        end : float
            Animation end time.
        easing : callable
            Easing function for each color transition.

        Returns
        -------
        self
        """
        dur = end - start
        if dur <= 0 or len(colors) < 2:
            return self
        n = len(colors)
        # Parse all colors to RGB tuples
        parsed = []
        for c in colors:
            _, rgb = attributes.Color(0, '#000').parse(c)
            parsed.append(rgb)
        # Set initial color at start
        self.set_fill(color=colors[0], start=start)
        # Use Color.set to define each interpolation segment
        src = self.styling.fill
        def _make_interp(_cf, _ct, _ss, _dd, _easing):
            def _interp(t):
                p = _easing((t - _ss) / _dd)
                return tuple(_cf[j] + (_ct[j] - _cf[j]) * p for j in range(len(_cf)))
            return _interp
        for i in range(n - 1):
            seg_s = start + dur * i / (n - 1)
            seg_e = start + dur * (i + 1) / (n - 1)
            c_from = parsed[i]
            c_to = parsed[i + 1]
            _d = max(seg_e - seg_s, 1e-9)
            src.set(seg_s, seg_e, _make_interp(c_from, c_to, seg_s, _d, easing), stay=(i == n - 2))
        return self

    def freeze(self, start, end=None):
        """Freeze the object's appearance at time *start*.

        All animated attributes stop changing — an updater saves the object's
        styling state at *start* and continuously restores it so the object
        appears constant.

        Parameters
        ----------
        start:
            Time at which to capture the frozen state.
        end:
            Time at which the freeze ends.  ``None`` means forever.

        Returns self.
        """
        _captured = {}

        def _capture(obj, t):
            if not _captured:
                # Snapshot every styling attribute at the freeze time
                for name, _, cls, _, _ in style._ATTR_SCHEMA:
                    attr = getattr(obj.styling, name)
                    if cls is attributes.Color:
                        # Store raw RGB tuple from the time function
                        _captured[name] = ('color', attr.time_func(start))
                    else:
                        _captured[name] = ('val', attr.at_time(start))
                _captured['_z'] = ('val', obj.z.at_time(start))
            # Restore all attributes to their frozen values
            for name, _, cls, _, _ in style._ATTR_SCHEMA:
                kind, val = _captured[name]
                attr = getattr(obj.styling, name)
                if kind == 'color':
                    attr.time_func = lambda _t, _v=val: _v
                else:
                    attr.set_onward(t, val)
            _, z_val = _captured['_z']
            obj.z.set_onward(t, z_val)

        self.add_updater(_capture, start, end)
        return self

    def delay_animation(self, method_name, delay, *args, **kwargs):
        """Schedule an animation to start after a delay.

        Calls ``getattr(self, method_name)(*args, start=<adjusted>, **rest)``
        where the ``start`` (or ``start_time``) keyword is increased by
        *delay*.  Convenience for offsetting animation timing.

        Returns self.
        """
        import inspect
        method = getattr(self, method_name)
        sig = inspect.signature(method)
        params = sig.parameters
        if 'start_time' in params:
            kwargs['start_time'] = kwargs.get('start_time', 0) + delay
        elif 'start' in params:
            kwargs['start'] = kwargs.get('start', 0) + delay
        method(*args, **kwargs)
        return self

    def wobble(self, start=0, end=1, intensity=5, frequency=3, easing=easings.smooth):
        """Organic wobbling motion combining small rotations and position shifts.

        Combines sine waves at slightly different frequencies to produce a
        natural-looking oscillation that is not perfectly periodic.

        Parameters
        ----------
        intensity:
            Max displacement in pixels (shift) and degrees (rotation).
        frequency:
            Base oscillation frequency (cycles per time unit).
        easing:
            Envelope easing — controls how the wobble fades out.

        Returns self.
        """
        dur = end - start
        if dur <= 0:
            return self
        _s, _d = start, max(dur, 1e-9)
        _a, _freq = intensity, frequency

        # Shift component: two different sine frequencies for organic feel
        def _dx(t, _s=_s, _d=_d, _a=_a, _freq=_freq, _easing=easing):
            p = (t - _s) / _d
            envelope = 1 - _easing(p)
            return _a * math.sin(2 * math.pi * _freq * p) * envelope

        def _dy(t, _s=_s, _d=_d, _a=_a, _freq=_freq, _easing=easing):
            p = (t - _s) / _d
            envelope = 1 - _easing(p)
            return _a * 0.7 * math.sin(2 * math.pi * _freq * 1.3 * p) * envelope

        self._apply_shift_effect(start, end, _dx, _dy)

        # Rotation component: slight wobbling rotation
        bx, by, bw, bh = self.bbox(start)
        cx, cy = bx + bw / 2, by + bh / 2
        self.styling.rotation.set(start, end,
            lambda t, _s=_s, _d=_d, _a=_a, _freq=_freq, _cx=cx, _cy=cy, _easing=easing: (
                _a * math.sin(2 * math.pi * _freq * 0.7 * ((t - _s) / _d)) * (1 - _easing((t - _s) / _d)),
                _cx, _cy))
        return self


class VCollection:
    """Container for a group of VObjects, delegating operations to children."""

    def __init__(self, *objects, creation: float = 0, z=0):
        self.objects = list(objects)
        self.show = attributes.Real(creation, True)
        self.z = attributes.Real(creation, z)
        self._scale_x = attributes.Real(creation, 1)
        self._scale_y = attributes.Real(creation, 1)
        self._scale_origin: tuple[float, float] | None = None

    def add(self, *objs):
        """Add one or more objects to this collection."""
        self.objects.extend(objs)
        return self

    def remove(self, obj):
        """Remove an object from this collection."""
        self.objects.remove(obj)
        return self

    def remove_at(self, index):
        """Remove and return the child at the given index."""
        return self.objects.pop(index)

    def clear(self):
        """Remove all children."""
        self.objects.clear()
        return self

    def send_to_back(self, child):
        """Move a child to the back (rendered first, behind others)."""
        if isinstance(child, int):
            child = self.objects[child]
        if child in self.objects:
            self.objects.remove(child)
            self.objects.insert(0, child)
        return self

    def bring_to_front(self, child):
        """Move a child to the front (rendered last, on top).

        Parameters
        ----------
        child:
            Either the child object itself or its integer index in
            ``self.objects``.
        """
        if isinstance(child, int):
            child = self.objects[child]
        if child in self.objects:
            self.objects.remove(child)
            self.objects.append(child)
        return self

    def get_child(self, index):
        """Return the child object at *index*.

        Supports both positive and negative indices (Python convention).
        Raises :exc:`IndexError` with a descriptive message when the index is
        out of range.

        Parameters
        ----------
        index:
            Integer position.  Negative indices count from the end
            (e.g. ``-1`` is the last child).

        Returns
        -------
        The child VObject or VCollection at *index*.

        Raises
        ------
        IndexError
            When *index* is out of the valid range.

        Example
        -------
        >>> col = VCollection(Circle(), Rectangle(100, 50))
        >>> col.get_child(0)   # first child
        >>> col.get_child(-1)  # last child
        """
        n = len(self.objects)
        if index < -n or index >= n:
            raise IndexError(
                f"child index {index} out of range for collection with {n} object(s)"
            )
        return self.objects[index]

    def nth(self, n):
        """Return the nth child (0-indexed).  Negative indices are supported.

        This is a convenience alias for :meth:`get_child` with a slightly
        shorter name, matching the ``first()`` / ``last()`` naming style.

        Parameters
        ----------
        n:
            Integer index.  Negative values count from the end.

        Returns
        -------
        The child at position *n*.

        Raises
        ------
        IndexError
            When *n* is out of range.

        Example
        -------
        >>> col = VCollection(Circle(), Rectangle(100, 50), Dot())
        >>> col.nth(0)   # first child
        >>> col.nth(2)   # third child
        >>> col.nth(-1)  # last child
        """
        return self.get_child(n)

    def first(self):
        """Return the first child object.

        Raises :exc:`IndexError` if the collection is empty.

        Example
        -------
        >>> col = VCollection(Circle(), Rectangle(100, 50))
        >>> col.first()  # same as col.get_child(0)
        """
        return self.get_child(0)

    def last(self):
        """Return the last child object.

        Raises :exc:`IndexError` if the collection is empty.

        Example
        -------
        >>> col = VCollection(Circle(), Rectangle(100, 50))
        >>> col.last()  # same as col.get_child(-1)
        """
        return self.get_child(-1)

    def _delegate(self, method, *args, **kwargs):
        """Call method on each child object, return self."""
        for obj in self.objects:
            getattr(obj, method)(*args, **kwargs)
        return self

    @property
    def last_change(self):
        candidates = [obj.last_change for obj in self.objects]
        candidates.append(self.z.last_change)
        candidates.append(self.show.last_change)
        return max(candidates)

    def __repr__(self):
        return f'{self.__class__.__name__}({len(self.objects)} objects)'

    def __iter__(self):
        return iter(self.objects)

    def __getitem__(self, idx):
        return self.objects[idx]

    def __len__(self):
        return len(self.objects)

    def count(self):
        """Return the number of child objects in this collection."""
        return len(self.objects)

    def __contains__(self, obj):
        return obj in self.objects

    def copy(self):
        return deepcopy(self)

    def to_svg(self, time):
        visible = [(getattr(o, 'z', attributes.Real(0, 0)).at_time(time), o)
                    for o in self.objects if o.show.at_time(time)]
        inner = '\n'.join(o.to_svg(time) for _, o in sorted(visible, key=lambda x: x[0]))
        sx, sy = self._scale_x.at_time(time), self._scale_y.at_time(time)
        transform = ''
        if sx != 1 or sy != 1:
            if self._scale_origin:
                cx, cy = self._scale_origin
                transform = f' transform="translate({cx},{cy}) scale({sx},{sy}) translate({-cx},{-cy})"'
            else:
                transform = f' transform="scale({sx},{sy})"'
        return f'<g{transform}>\n{inner}\n</g>'

    def bbox(self, time, start_idx=0, end_idx=None):
        objs = self.objects[start_idx:end_idx]
        if not objs:
            return (0, 0, 0, 0)
        boxes = [o.bbox(time) for o in objs]
        xmin = min(b[0] for b in boxes)
        ymin = min(b[1] for b in boxes)
        xmax = max(b[0] + b[2] for b in boxes)
        ymax = max(b[1] + b[3] for b in boxes)
        return (xmin, ymin, xmax - xmin, ymax - ymin)

    def brect(self, time, start_idx=0, end_idx=None, rx=0, ry=0, buff=SMALL_BUFF, follow=True):
        """Bounding rectangle with buff outward padding."""
        return _make_brect(self.bbox, time, rx, ry, buff, follow,
                           start_idx=start_idx, end_idx=end_idx)

    def move_to(self, x, y, start_time: float = 0, end_time: float | None = None, easing=easings.smooth):
        """Move the collection's center to (x, y)."""
        xmin, ymin, w, h = self.bbox(start_time)
        self.shift(dx=x-(xmin+w/2), dy=y-(ymin+h/2),
                   start_time=start_time, end_time=end_time, easing=easing)
        return self

    def center_to_pos(self, posx: float = 960, posy: float = 540, start_time: float = 0, end_time: float | None = None, easing=easings.smooth):
        """Move the collection's center to (posx, posy)."""
        return self.move_to(posx, posy, start_time, end_time, easing)

    def center(self, time: float = 0):
        x, y, w, h = self.bbox(time)
        return (x + w / 2, y + h / 2)

    get_center = center

    def get_x(self, time=0):
        return self.center(time)[0]

    def get_y(self, time=0):
        return self.center(time)[1]

    def get_width(self, time=0):
        return self.bbox(time)[2]

    def get_height(self, time=0):
        return self.bbox(time)[3]

    def total_width(self, time=0):
        """Return the sum of all children's individual bounding-box widths at *time*.

        Useful after :meth:`arrange` to know the combined span before padding.
        Unlike :meth:`get_width` (which returns the overall bbox width including gaps),
        this sums each child's width independently.
        """
        return sum(obj.bbox(time)[2] for obj in self.objects)

    def total_height(self, time=0):
        """Return the sum of all children's individual bounding-box heights at *time*.

        Useful after a vertical :meth:`arrange` to know the combined span before padding.
        Unlike :meth:`get_height` (which returns the overall bbox height including gaps),
        this sums each child's height independently.
        """
        return sum(obj.bbox(time)[3] for obj in self.objects)

    def get_diagonal(self, time=0):
        """Return the diagonal length of the bounding box."""
        _, _, w, h = self.bbox(time)
        return math.hypot(w, h)

    def get_aspect_ratio(self, time=0):
        """Return width/height ratio of the bounding box."""
        _, _, w, h = self.bbox(time)
        return w / h if h != 0 else float('inf')

    def distance_to(self, other, time=0):
        """Return the distance between this collection's center and another object's center."""
        x1, y1 = self.center(time)
        x2, y2 = other.center(time)
        return math.hypot(x2 - x1, y2 - y1)

    def is_overlapping(self, other, time=0):
        """Return True if this collection's bbox overlaps with other's bbox."""
        x1, y1, w1, h1 = self.bbox(time)
        x2, y2, w2, h2 = other.bbox(time)
        return not (x1 + w1 < x2 or x2 + w2 < x1 or y1 + h1 < y2 or y2 + h2 < y1)

    def get_edge(self, edge, time=0):
        """Return coordinate of a named edge point (same API as VObject.get_edge)."""
        return _get_edge_impl(self.bbox, edge, time)

    def get_left(self, time=0):
        return self.get_edge('left', time)

    def get_right(self, time=0):
        return self.get_edge('right', time)

    def get_top(self, time=0):
        return self.get_edge('top', time)

    def get_bottom(self, time=0):
        return self.get_edge('bottom', time)

    def to_edge(self, edge: str | tuple = DOWN, buff=DEFAULT_OBJECT_TO_EDGE_BUFF,
                start_time: float = 0, end_time: float | None = None, easing=easings.smooth):
        """Move group to a canvas edge."""
        return _to_edge_impl(self, edge, buff, start_time, end_time, easing)

    def to_corner(self, corner: str | tuple = DR, buff=DEFAULT_OBJECT_TO_EDGE_BUFF,
                  start_time: float = 0, end_time: float | None = None, easing=easings.smooth):
        """Move group to a canvas corner."""
        return _to_corner_impl(self, corner, buff, start_time, end_time, easing)

    def filter(self, predicate):
        """Return a new VCollection with only children matching predicate(obj) -> bool."""
        return VCollection(*(obj for obj in self.objects if predicate(obj)))

    def filter_by_type(self, cls):
        """Return a new VCollection with only children of the given type."""
        return self.filter(lambda obj: isinstance(obj, cls))

    def find(self, predicate, time=0):
        """Return the first child satisfying predicate(obj, time), or None."""
        for obj in self.objects:
            if predicate(obj, time):
                return obj
        return None

    def find_by_type(self, cls):
        """Return a list of all children that are instances of cls."""
        return [obj for obj in self.objects if isinstance(obj, cls)]

    def find_index(self, predicate, time=0):
        """Return the index of the first child satisfying predicate, or -1."""
        for i, obj in enumerate(self.objects):
            if predicate(obj, time):
                return i
        return -1

    def group_by(self, key_func):
        """Group children by the result of *key_func*.

        Parameters
        ----------
        key_func:
            A callable that takes a single child object and returns a hashable
            key.  For example ``type`` groups by class, ``lambda o: o.z``
            groups by z-order.

        Returns
        -------
        dict
            A mapping from each distinct key value to a :class:`VCollection`
            containing all children that produced that key.

        Examples
        --------
        >>> circles = VCollection(Circle(), Circle(), Rectangle())
        >>> groups = circles.group_by(type)
        >>> groups[Circle]   # VCollection of two circles
        >>> groups[Rectangle]  # VCollection of one rectangle
        """
        groups: dict = {}
        for obj in self.objects:
            k = key_func(obj)
            groups.setdefault(k, []).append(obj)
        return {k: VCollection(*objs) for k, objs in groups.items()}

    def partition(self, predicate):
        """Split into two VCollections: (matching, non_matching)."""
        yes, no = [], []
        for obj in self.objects:
            (yes if predicate(obj) else no).append(obj)
        return VCollection(*yes), VCollection(*no)

    def chunk(self, size: int):
        """Split children into sub-collections of at most *size* elements each.

        Returns a list of :class:`VCollection` objects.  The last chunk may
        contain fewer than *size* elements when the number of children is not
        exactly divisible by *size*.

        Parameters
        ----------
        size:
            Maximum number of children per chunk.  Must be >= 1.

        Returns
        -------
        list of VCollection

        Raises
        ------
        ValueError
            If *size* is less than 1.

        Examples
        --------
        >>> col = VCollection(*[Circle() for _ in range(10)])
        >>> chunks = col.chunk(3)
        >>> [len(c.objects) for c in chunks]
        [3, 3, 3, 1]
        """
        if size < 1:
            raise ValueError(f"chunk size must be >= 1, got {size!r}")
        objs = self.objects
        return [VCollection(*objs[i:i + size]) for i in range(0, len(objs), size)]

    def sort_by_position(self, axis='x', reverse=False):
        """Sort children in-place by their x or y position.

        Parameters
        ----------
        axis:
            ``'x'`` to sort by centre x coordinate (left-to-right),
            ``'y'`` to sort by centre y coordinate (top-to-bottom).
        reverse:
            If ``True``, sort in descending order.

        Returns self.
        """
        if axis == 'x':
            self.objects.sort(key=lambda obj: obj.center(0)[0], reverse=reverse)
        elif axis == 'y':
            self.objects.sort(key=lambda obj: obj.center(0)[1], reverse=reverse)
        return self

    def group_into(self, n):
        """Split the collection into *n* sub-collections of roughly equal size.

        Returns a :class:`VCollection` whose children are themselves
        :class:`VCollection` instances.

        Parameters
        ----------
        n:
            Number of groups.  Must be >= 1.

        Raises
        ------
        ValueError
            If *n* is less than 1.

        Returns a VCollection of VCollections.
        """
        if n < 1:
            raise ValueError(f"n must be >= 1, got {n!r}")
        objs = self.objects
        total = len(objs)
        groups = []
        base, remainder = divmod(total, n)
        idx = 0
        for i in range(n):
            size = base + (1 if i < remainder else 0)
            groups.append(VCollection(*objs[idx:idx + size]))
            idx += size
        return VCollection(*groups)

    def enumerate_children(self):
        """Return a list of (index, child) tuples for all children.

        Convenience wrapper around the built-in ``enumerate`` so callers do
        not need to access ``self.objects`` directly.

        Returns
        -------
        list of (int, VObject)
            Index-object pairs in insertion order.

        Example
        -------
        >>> col = VCollection(Circle(), Rectangle(100, 50))
        >>> for i, obj in col.enumerate_children():
        ...     print(i, obj)
        """
        return list(enumerate(self.objects))

    def select(self, start=0, end=None):
        """Return a new VCollection with children at indices [start:end]."""
        return VCollection(*self.objects[start:end])

    def take(self, n):
        """Return a new VCollection with the first *n* children.

        Equivalent to ``select(0, n)``.  If *n* is greater than or equal to
        the number of children the full collection is returned.  If *n* is
        zero an empty VCollection is returned.

        Parameters
        ----------
        n:
            Number of children to keep from the start of the collection.

        Returns
        -------
        VCollection
        """
        return VCollection(*self.objects[:n])

    def skip(self, n):
        """Return a new VCollection skipping the first *n* children.

        Equivalent to ``select(n)``.  If *n* is greater than or equal to the
        number of children an empty VCollection is returned.  If *n* is zero
        the full collection is returned unchanged.

        Parameters
        ----------
        n:
            Number of children to skip from the start of the collection.

        Returns
        -------
        VCollection
        """
        return VCollection(*self.objects[n:])

    def interleave(self, other):
        """Merge two collections by alternating their children.

        Returns a new VCollection with elements interleaved as
        [a1, b1, a2, b2, ...].  If one collection is longer than the other,
        the remaining elements are appended at the end.

        Parameters
        ----------
        other:
            Another VCollection (or subclass) whose children to interleave with
            this collection's children.

        Returns
        -------
        VCollection
            A new collection containing the interleaved children.  The original
            collections are not modified.

        Example
        -------
        >>> a = VCollection(Circle(), Circle())
        >>> b = VCollection(Rectangle(10,10), Rectangle(10,10), Rectangle(10,10))
        >>> c = a.interleave(b)
        >>> len(c)   # 5 — circle, rect, circle, rect, rect
        """
        result = []
        a_list = list(self.objects)
        b_list = list(other.objects)
        max_len = max(len(a_list), len(b_list))
        for i in range(max_len):
            if i < len(a_list):
                result.append(a_list[i])
            if i < len(b_list):
                result.append(b_list[i])
        return VCollection(*result)

    def flatten(self):
        """Flatten nested VCollections into a single-level collection in-place.

        Any child that is itself a :class:`VCollection` (or subclass) has its
        children extracted and inserted into this collection at the child's
        position.  The process repeats until no nested collections remain.

        Returns
        -------
        self

        Examples
        --------
        >>> inner = VCollection(Circle(), Rectangle(50, 50))
        >>> outer = VCollection(inner, Dot())
        >>> outer.flatten()
        >>> len(outer.objects)  # 3: Circle, Rectangle, Dot
        3
        """
        changed = True
        while changed:
            changed = False
            new_objects = []
            for obj in self.objects:
                if isinstance(obj, VCollection):
                    new_objects.extend(obj.objects)
                    changed = True
                else:
                    new_objects.append(obj)
            self.objects = new_objects
        return self

    def sort_objects(self, key=None, reverse=False, time=0):
        """Sort children in-place. Default key: x position at given time."""
        if key is None:
            key = lambda obj: obj.bbox(time)[0]
        self.objects.sort(key=key, reverse=reverse)
        return self

    def sort_by_y(self, reverse=False, time=0):
        """Sort children by y position (top to bottom by default)."""
        return self.sort_objects(key=lambda obj: obj.bbox(time)[1], reverse=reverse, time=time)

    def sort_by_z(self, reverse=False, time=0):
        """Sort children by z-depth."""
        return self.sort_objects(key=lambda obj: obj.z.at_time(time), reverse=reverse, time=time)

    def sort_by(self, key_func, reverse=False):
        """Sort children by key_func(child). Does not animate — instant reorder."""
        self.objects.sort(key=key_func, reverse=reverse)
        return self

    def max_by(self, key):
        """Return the child with the maximum key value."""
        if not self.objects:
            return None
        return max(self.objects, key=key)

    def min_by(self, key):
        """Return the child with the minimum key value."""
        if not self.objects:
            return None
        return min(self.objects, key=key)

    def sum_by(self, key):
        """Sum the result of key(child) across all children."""
        return sum(key(obj) for obj in self.objects)

    def shuffle(self):
        """Randomly shuffle the order of children in-place."""
        import random
        random.shuffle(self.objects)
        return self

    def reverse_children(self):
        """Reverse the order of children in-place."""
        self.objects.reverse()
        return self

    def reverse(self):
        """Reverse the order of children in-place. Alias for reverse_children."""
        self.objects.reverse()
        return self

    def rotate_order(self, n=1):
        """Rotate children order by *n* positions.

        Positive *n* moves the first *n* children to the end (like
        ``collections.deque.rotate(-n)``).  Returns *self*.
        """
        if not self.objects:
            return self
        n = n % len(self.objects)
        self.objects = self.objects[n:] + self.objects[:n]
        return self

    def set_z_order(self, order):
        """Reorder children by index list.

        ``order[i]`` is the index of the child to place at position *i*.
        The length of *order* must equal the number of children and must
        contain each index exactly once (i.e. a permutation).

        Parameters
        ----------
        order:
            List of integer indices specifying the new order.

        Returns
        -------
        self

        Example
        -------
        >>> col = VCollection(a, b, c)
        >>> col.set_z_order([2, 0, 1])  # new order: c, a, b
        """
        self.objects = [self.objects[i] for i in order]
        return self

    def index_of(self, obj):
        """Find object index by identity. Returns -1 if not found."""
        try:
            return self.objects.index(obj)
        except ValueError:
            return -1

    def replace(self, old, new):
        """In-place swap: replace *old* child with *new*."""
        idx = self.index_of(old)
        if idx >= 0:
            self.objects[idx] = new
        return self

    def map_objects(self, func):
        """Apply *func* to each child and return a new VCollection."""
        return VCollection(*(func(obj) for obj in self.objects))

    def set_z_values(self, start=0):
        """Assign ascending z-order values starting from *start*."""
        for i, obj in enumerate(self.objects):
            obj.z.set_onward(start, i)
        return self

    def set_color_by_gradient(self, *colors, attr='fill', start=0):
        """Assign interpolated colors across children.
        colors: two or more hex color strings to interpolate between."""
        n = len(self.objects)
        if n < 2 or len(colors) < 2:
            if colors and n:
                for obj in self.objects:
                    if attr == 'fill':
                        obj.set_fill(colors[0], start=start)
                    else:
                        obj.set_stroke(colors[0], start=start)
            return self
        from vectormation.colors import interpolate_color
        for i, obj in enumerate(self.objects):
            t = i / (n - 1)
            seg = t * (len(colors) - 1)
            idx = min(int(seg), len(colors) - 2)
            local_t = seg - idx
            color = interpolate_color(colors[idx], colors[idx + 1], local_t)
            if attr == 'fill':
                obj.set_fill(color, start=start)
            else:
                obj.set_stroke(color, start=start)
        return self

    def set_opacity_by_gradient(self, start_opacity, end_opacity, attr='fill', start=0):
        """Set linearly interpolated opacity across children."""
        n = len(self.objects)
        if n < 2:
            if n:
                self.objects[0].set_opacity(start_opacity, start)
            return self
        for i, obj in enumerate(self.objects):
            t = i / (n - 1)
            opacity = start_opacity + (end_opacity - start_opacity) * t
            if attr == 'fill':
                obj.styling.fill_opacity.set_onward(start, opacity)
            else:
                obj.styling.stroke_opacity.set_onward(start, opacity)
        return self

    def __getattr__(self, name):
        """Delegate unknown methods to children if all children support them."""
        if name.startswith('_'):
            raise AttributeError(name)
        if all(hasattr(obj, name) for obj in self.objects):
            def delegated(*args, **kwargs):
                return self._delegate(name, *args, **kwargs)
            return delegated
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def _resolve_center(self, start, cx, cy):
        if cx is None or cy is None:
            bx, by, bw, bh = self.bbox(start)
            return bx + bw / 2, by + bh / 2
        return cx, cy

    def scale(self, factor, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Scale all children around the group center."""
        return self.stretch(factor, factor, start, end, easing)

    def stretch(self, x_factor: float = 1, y_factor: float = 1, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Non-uniform scale of all children around the group center."""
        if self._scale_origin is None:
            self._scale_origin = self._resolve_center(start, None, None)
        for attr, factor in [(self._scale_x, x_factor), (self._scale_y, y_factor)]:
            target = attr.at_time(start) * factor
            if end is None:
                attr.set_onward(start, target)
            else:
                attr.move_to(start, end, target, easing=easing)
        return self

    def rotate_to(self, start: float, end: float, degrees, cx=None, cy=None, easing=easings.smooth):
        cx, cy = self._resolve_center(start, cx, cy)
        return self._delegate('rotate_to', start, end, degrees, cx=cx, cy=cy, easing=easing)

    def rotate_by(self, start: float, end: float, degrees, cx=None, cy=None, easing=easings.smooth):
        cx, cy = self._resolve_center(start, cx, cy)
        return self._delegate('rotate_by', start, end, degrees, cx=cx, cy=cy, easing=easing)

    def arrange(self, direction: str | tuple = 'right', buff=SMALL_BUFF, start_time: float = 0):
        """Lay out children in a row or column with spacing.
        direction: 'right', 'left', 'down', 'up' or a direction constant."""
        if isinstance(direction, tuple):
            direction = _DIR_NAMES.get(direction, 'right')
        if not self.objects:
            return self
        horizontal = direction in ('right', 'left')
        sign = 1 if direction in ('right', 'down') else -1
        cursor = 0
        for obj in self.objects:
            x, y, w, h = obj.bbox(start_time)
            size = w if horizontal else h
            offset = cursor - (x if horizontal else y)
            if horizontal:
                obj.shift(dx=sign * offset, start_time=start_time)
            else:
                obj.shift(dy=sign * offset, start_time=start_time)
            cursor += size + buff
        return self

    def distribute(self, direction: str | tuple = 'right', buff=0, start_time: float = 0):
        """Distribute children evenly within the group's bounding box.
        Unlike arrange(), this spaces children evenly to fill the available space.
        direction: 'right', 'left', 'down', 'up' or a direction constant."""
        if isinstance(direction, tuple):
            direction = _DIR_NAMES.get(direction, 'right')
        if len(self.objects) < 2:
            return self
        horizontal = direction in ('right', 'left')
        boxes = [obj.bbox(start_time) for obj in self.objects]
        total_size = sum(b[2] if horizontal else b[3] for b in boxes)
        group_box = self.bbox(start_time)
        available = (group_box[2] if horizontal else group_box[3]) - total_size
        spacing = available / (len(self.objects) - 1) if len(self.objects) > 1 else 0
        spacing = max(spacing, buff)
        cursor = 0
        for obj, box in zip(self.objects, boxes):
            x, y, w, h = box
            size = w if horizontal else h
            offset = cursor - (x if horizontal else y)
            if horizontal:
                obj.shift(dx=offset, start_time=start_time)
            else:
                obj.shift(dy=offset, start_time=start_time)
            cursor += size + spacing
        return self

    def space_evenly(self, direction: str | tuple = 'right', total_span=None,
                     start_pos=None, start_time: float = 0):
        """Distribute children so they fill exactly *total_span* pixels.

        Unlike :meth:`arrange` (fixed gap between children) and :meth:`distribute`
        (uses existing group bbox), ``space_evenly`` lets you specify an explicit
        span and optional start position, then positions children so their combined
        widths (or heights) plus equal gaps exactly fill that span.

        Parameters
        ----------
        direction:
            ``'right'`` / ``'left'`` (horizontal) or ``'down'`` / ``'up'``
            (vertical).
        total_span:
            Total pixel width (horizontal) or height (vertical) to fill.
            Defaults to the group's current bounding-box dimension.
        start_pos:
            Left edge (horizontal) or top edge (vertical) of the first child.
            Defaults to the current leftmost / topmost edge of the group.
        start_time:
            Time at which to read current positions.

        Returns
        -------
        self
        """
        if isinstance(direction, tuple):
            direction = _DIR_NAMES.get(direction, 'right')
        if len(self.objects) == 0:
            return self
        horizontal = direction in ('right', 'left')
        boxes = [obj.bbox(start_time) for obj in self.objects]
        sizes = [b[2] if horizontal else b[3] for b in boxes]
        total_child_size = sum(sizes)
        group_box = self.bbox(start_time)
        if total_span is None:
            total_span = group_box[2] if horizontal else group_box[3]
        if start_pos is None:
            start_pos = group_box[0] if horizontal else group_box[1]
        n = len(self.objects)
        gap = (total_span - total_child_size) / (n - 1) if n > 1 else 0
        cursor = start_pos
        for obj, box, size in zip(self.objects, boxes, sizes):
            edge = box[0] if horizontal else box[1]
            offset = cursor - edge
            if horizontal:
                obj.shift(dx=offset, start_time=start_time)
            else:
                obj.shift(dy=offset, start_time=start_time)
            cursor += size + gap
        return self

    def distribute_radial(self, cx=960, cy=540, radius=200, start_angle=0,
                           start_time: float = 0, end_time: float | None = None,
                           easing=easings.smooth):
        """Arrange children in a circle around (cx, cy).
        With end_time=None, positions instantly. With end_time, animates."""
        n = len(self.objects)
        if n == 0:
            return self
        for i, obj in enumerate(self.objects):
            angle = start_angle + 2 * math.pi * i / n
            tx = cx + radius * math.cos(angle)
            ty = cy + radius * math.sin(angle)
            bx, by, bw, bh = obj.bbox(start_time)
            obj_cx, obj_cy = bx + bw / 2, by + bh / 2
            dx, dy = tx - obj_cx, ty - obj_cy
            if end_time is None:
                obj.shift(dx=dx, dy=dy, start_time=start_time)
            else:
                obj.shift(dx=dx, dy=dy, start_time=start_time,
                          end_time=end_time, easing=easing)
        return self

    def radial_arrange(self, radius=200, start_angle=0, center=None,
                       start_time: float = 0):
        """Arrange children in a circle with given radius and starting angle.

        Unlike :meth:`distribute_radial` which accepts animated end_time,
        this is a simple instant layout method.  center defaults to the
        collection's bounding-box center.

        Parameters
        ----------
        radius: distance from center to each child's center.
        start_angle: angle in radians for the first child (0 = right).
        center: (cx, cy) tuple, or None to use the collection center.
        """
        n = len(self.objects)
        if n == 0:
            return self
        if center is None:
            gx, gy, gw, gh = self.bbox(start_time)
            center = (gx + gw / 2, gy + gh / 2)
        cx, cy = center
        for i, obj in enumerate(self.objects):
            angle = start_angle + 2 * math.pi * i / n
            tx = cx + radius * math.cos(angle)
            ty = cy + radius * math.sin(angle)
            bx, by, bw, bh = obj.bbox(start_time)
            obj_cx, obj_cy = bx + bw / 2, by + bh / 2
            dx, dy = tx - obj_cx, ty - obj_cy
            obj.shift(dx=dx, dy=dy, start_time=start_time)
        return self

    def arrange_in_grid(self, rows=None, cols=None, buff=SMALL_BUFF, start_time: float = 0):
        """Lay out children in a grid. If rows/cols omitted, picks a square-ish grid."""
        n = len(self.objects)
        if not n:
            return self
        if rows is None and cols is None:
            cols = math.ceil(math.sqrt(n))
            rows = math.ceil(n / cols)
        elif rows is None:
            rows = math.ceil(n / cols)
        elif cols is None:
            cols = math.ceil(n / rows)
        # Measure max cell size
        boxes = [obj.bbox(start_time) for obj in self.objects]
        max_w = max(b[2] for b in boxes)
        max_h = max(b[3] for b in boxes)
        cell_w, cell_h = max_w + buff, max_h + buff
        # Position each object centered in its cell
        for idx, (obj, box) in enumerate(zip(self.objects, boxes)):
            r, c = divmod(idx, cols)
            target_cx = c * cell_w + max_w / 2
            target_cy = r * cell_h + max_h / 2
            cur_cx = box[0] + box[2] / 2
            cur_cy = box[1] + box[3] / 2
            obj.shift(dx=target_cx - cur_cx, dy=target_cy - cur_cy, start_time=start_time)
        return self

    def stagger(self, method_name, delay, **kwargs):
        """Call method on each child with staggered timing offsets."""
        for i, obj in enumerate(self.objects):
            kw = dict(kwargs)
            for key in ('start', 'end', 'start_time', 'end_time'):
                if key in kw:
                    kw[key] = kw[key] + i * delay
            getattr(obj, method_name)(**kw)
        return self

    def stagger_random(self, method_name, start=0, end=1, seed=None, **kwargs):
        """Call method_name on each child in random order with equal stagger delay."""
        import random
        n = len(self.objects)
        if n == 0:
            return self
        dur = end - start
        if dur <= 0:
            return self
        delay = dur / n
        shuffled = random.Random(seed).sample(self.objects, n)
        for i, obj in enumerate(shuffled):
            obj_start = start + i * delay
            obj_end = obj_start + delay
            kw = dict(kwargs, start=obj_start, end=obj_end)
            getattr(obj, method_name)(**kw)
        return self

    def wave_anim(self, start: float = 0, end: float = 1, amplitude=20, waves=1):
        """Staggered wave animation: children bob up and down with phase offsets."""
        n = len(self.objects)
        if n == 0:
            return self
        dur = end - start
        if dur <= 0:
            return self
        for i, obj in enumerate(self.objects):
            phase = 2 * math.pi * i / max(n, 1)
            s, d, a, p = start, dur, amplitude, phase
            w = waves
            def _dy(t, _s=s, _d=d, _a=a, _p=p, _w=w):
                progress = (t - _s) / _d
                return -_a * math.sin(2 * math.pi * _w * progress + _p) * (1 - progress)
            for _, ya in obj._shift_reals():
                ya.add(start, end, _dy)
            for c in obj._shift_coors():
                c.add(start, end, lambda t, _f=_dy: (0, _f(t)))
        return self

    def sequential(self, method_name, start: float = 0, end: float = 1, **kwargs):
        """Run an animation method on children one after another with no overlap.
        Equivalent to cascade with overlap=0."""
        return self.cascade(method_name, start=start, end=end, overlap=0, **kwargs)

    def apply_sequentially(self, method_name, start=0, end=1, **kwargs):
        """Apply method to each child in sequence, dividing [start, end] equally.

        Unlike :meth:`sequential` / :meth:`cascade`, this directly computes
        equal-duration time slices without any overlap logic, making it a
        simpler and more predictable alternative.

        Parameters
        ----------
        method_name:
            Name of the animation method to call on each child (e.g. ``'fadein'``).
        start, end:
            Overall time range to divide among the children.
        **kwargs:
            Additional keyword arguments forwarded to each child method call.
        """
        n = len(self.objects)
        if n == 0:
            return self
        dt = (end - start) / n
        for i, obj in enumerate(self.objects):
            getattr(obj, method_name)(start=start + i * dt, end=start + (i + 1) * dt, **kwargs)
        return self

    def apply_sequential(self, method_name, start=0, end=1, **kwargs):
        """Alias for :meth:`apply_sequentially`."""
        return self.apply_sequentially(method_name, start=start, end=end, **kwargs)

    def spread(self, x1, y1, x2, y2, start_time: float = 0):
        """Distribute children evenly along a line from (x1, y1) to (x2, y2)."""
        n = len(self.objects)
        if n == 0:
            return self
        for i, obj in enumerate(self.objects):
            t = i / max(n - 1, 1)
            tx = x1 + (x2 - x1) * t
            ty = y1 + (y2 - y1) * t
            bx, by, bw, bh = obj.bbox(start_time)
            cx, cy = bx + bw / 2, by + bh / 2
            obj.shift(dx=tx - cx, dy=ty - cy, start_time=start_time)
        return self

    def align_submobjects(self, edge='left', start_time: float = 0):
        """Align all children to a common edge: 'left', 'right', 'top', 'bottom', 'center_x', 'center_y'.
        Shifts each child so their specified edge aligns with the collection's edge."""
        n = len(self.objects)
        if n == 0:
            return self
        if isinstance(edge, tuple):
            edge = _EDGE_NAMES.get(edge, 'left')
        # Find the target value from the collection's bbox
        gx, gy, gw, gh = self.bbox(start_time)
        targets = {
            'left': lambda bx, by, bw, bh: (gx - bx, 0),
            'right': lambda bx, by, bw, bh: ((gx + gw) - (bx + bw), 0),
            'top': lambda bx, by, bw, bh: (0, gy - by),
            'bottom': lambda bx, by, bw, bh: (0, (gy + gh) - (by + bh)),
            'center_x': lambda bx, by, bw, bh: (gx + gw / 2 - (bx + bw / 2), 0),
            'center_y': lambda bx, by, bw, bh: (0, gy + gh / 2 - (by + bh / 2)),
        }
        func = targets.get(edge)
        if func is None:
            return self
        for obj in self.objects:
            bx, by, bw, bh = obj.bbox(start_time)
            dx, dy = func(bx, by, bw, bh)
            if dx != 0 or dy != 0:
                obj.shift(dx=dx, dy=dy, start_time=start_time)
        return self

    def cascade(self, method_name, start: float = 0, end: float = 1, overlap=0.5, **kwargs):
        """Call an animation method on children with overlapping timing.
        overlap: 0 = sequential, 1 = all simultaneous. 0.5 = half overlap."""
        n = len(self.objects)
        if n == 0:
            return self
        dur = end - start
        if dur <= 0:
            return self
        overlap = max(0.0, min(1.0, overlap))
        if n == 1:
            child_dur = dur
            step = 0
        else:
            child_dur = dur / (1 + (1 - overlap) * (n - 1))
            step = child_dur * (1 - overlap)
        for i, obj in enumerate(self.objects):
            s = start + i * step
            e = s + child_dur
            getattr(obj, method_name)(start=s, end=e, **kwargs)
        return self

    def stagger_fadein(self, start: float = 0, end: float = 1,
                        shift_dir=None, shift_amount=50, overlap=0.5,
                        easing=easings.smooth):
        """Fade in children with staggered timing and optional shift direction.
        Convenience wrapper around cascade + fadein."""
        kwargs = {'shift_dir': shift_dir, 'shift_amount': shift_amount, 'easing': easing}
        return self.cascade('fadein', start=start, end=end, overlap=overlap, **kwargs)

    def stagger_fadeout(self, start: float = 0, end: float = 1,
                         shift_dir=None, shift_amount=50, overlap=0.5,
                         easing=easings.smooth):
        """Fade out children with staggered timing and optional shift direction.
        Convenience wrapper around cascade + fadeout."""
        kwargs = {'shift_dir': shift_dir, 'shift_amount': shift_amount, 'easing': easing}
        return self.cascade('fadeout', start=start, end=end, overlap=overlap, **kwargs)

    def fade_in_one_by_one(self, start: float = 0, end: float = 1,
                            overlap=0.0, easing=easings.smooth):
        """Fade in each child sequentially with optional overlap.

        Each child gets an equal-duration window in which it fades in.
        When *overlap* is 0 the windows are strictly sequential (no two
        children animate at the same time).  Positive overlap values let
        consecutive windows overlap so the next child starts fading in
        before the previous one finishes.

        Parameters
        ----------
        start, end:
            Overall time interval.
        overlap:
            Fraction of each child's window that overlaps with the next
            (0 = sequential, positive = overlapping).
        easing:
            Easing function for each child's fade.

        Returns
        -------
        self
        """
        n = len(self.objects)
        if n == 0:
            return self
        dur = end - start
        if dur <= 0:
            return self
        if n == 1:
            slot = dur
        else:
            slot = (dur + overlap * (n - 1)) / n
        for i, obj in enumerate(self.objects):
            obj_start = start + i * (slot - overlap)
            obj_end = obj_start + slot
            obj.fadein(start=obj_start, end=min(obj_end, end), easing=easing)
        return self

    def reveal(self, start: float = 0, end: float = 1, direction='left',
                easing=easings.smooth, shift_amount=30):
        """Reveal children one by one from a direction (curtain effect).
        direction: 'left' (left-to-right), 'right', 'top', 'bottom'.
        Each child fades in with a small shift from the given direction."""
        n = len(self.objects)
        if n == 0:
            return self
        dur = end - start
        if dur <= 0:
            return self
        per_child = dur / n
        shift_map = {'left': (-shift_amount, 0), 'right': (shift_amount, 0),
                     'top': (0, -shift_amount), 'bottom': (0, shift_amount)}
        sdx, sdy = shift_map.get(direction, (-shift_amount, 0))
        for i, obj in enumerate(self.objects):
            t0 = start + i * per_child
            t1 = min(t0 + per_child * 1.5, end)  # slight overlap
            obj.fadein(t0, t1, shift_dir=None)
            # Temporary shift: offset→0 via .add() (additive, non-persistent)
            _dur = max(t1 - t0, 1e-9)
            if sdx != 0:
                _sdx, _t0, _d = sdx, t0, _dur
                def _dx(t, _sdx=_sdx, _t0=_t0, _d=_d, _easing=easing):
                    return _sdx * (1 - _easing((t - _t0) / _d))
                for xa, ya in obj._shift_reals():
                    xa.add(t0, t1, _dx)
                for c in obj._shift_coors():
                    c.add(t0, t1, lambda t, _f=_dx: (_f(t), 0))
            if sdy != 0:
                _sdy, _t0, _d = sdy, t0, _dur
                def _dy(t, _sdy=_sdy, _t0=_t0, _d=_d, _easing=easing):
                    return _sdy * (1 - _easing((t - _t0) / _d))
                for xa, ya in obj._shift_reals():
                    ya.add(t0, t1, _dy)
                for c in obj._shift_coors():
                    c.add(t0, t1, lambda t, _f=_dy: (0, _f(t)))
        return self

    def highlight_child(self, index, start: float = 0, end: float = 1,
                         dim_opacity=0.2, easing=easings.smooth):
        """Emphasize child at `index` by dimming all others.
        At `end`, all opacities are restored."""
        for i, obj in enumerate(self.objects):
            if i != index:
                obj.dim(start=start, end=start + (end - start) * 0.3,
                        opacity=dim_opacity, easing=easing)
                obj.undim(start=start + (end - start) * 0.7, end=end, easing=easing)
        return self

    def swap_children(self, i, j, start: float = 0, end: float = 1,
                       easing=easings.smooth):
        """Animate swapping the positions of children at indices i and j.
        Each child moves along an arc to the other's position, using
        opposite arc directions to avoid overlapping.  Returns self."""
        n = len(self.objects)
        if i < 0 or j < 0 or i >= n or j >= n or i == j:
            return self
        a, b = self.objects[i], self.objects[j]
        ax, ay, aw, ah = a.bbox(start)
        bx, by, bw, bh = b.bbox(start)
        acx, acy = ax + aw / 2, ay + ah / 2
        bcx, bcy = bx + bw / 2, by + bh / 2
        a.path_arc(bcx, bcy, start=start, end=end, angle=math.pi / 3, easing=easing)
        b.path_arc(acx, acy, start=start, end=end, angle=-math.pi / 3, easing=easing)
        return self

    def swap_animated(self, i, j, start=0, end=1, easing=easings.smooth):
        """Animate swapping the positions of children at indices i and j.
        Alias for :meth:`swap_children`."""
        return self.swap_children(i, j, start=start, end=end, easing=easing)

    def highlight_nth(self, n, start=0, end=1, color='#FFFF00', easing=easings.smooth):
        """Highlight the nth child by temporarily changing its fill color while
        dimming others.  At end, restore all original colors.  Returns self."""
        if n < 0 or n >= len(self.objects):
            return self
        mid = start + (end - start) * 0.5
        # Dim non-target children
        for i, obj in enumerate(self.objects):
            if i != n:
                obj.dim(start=start, end=start + (end - start) * 0.3,
                        opacity=0.3, easing=easing)
                obj.undim(start=start + (end - start) * 0.7, end=end, easing=easing)
        # Change nth child fill to highlight color, then restore
        target = self.objects[n]
        # Save original fill as raw tuple for reliable round-tripping
        orig_fill_raw = target.styling.fill.time_func(start)
        target.set_fill(color=color, start=start, end=mid, easing=easing)
        target.set_fill(color=orig_fill_raw, start=mid, end=end, easing=easing)
        return self

    def shuffle_positions(self, start: float = 0, end: float = 1,
                           easing=easings.smooth, seed=None):
        """Randomly rearrange children positions with animation (visual shuffle).
        Unlike shuffle() which reorders the list, this animates children to each
        other's positions. seed: optional random seed for reproducibility."""
        import random
        n = len(self.objects)
        if n <= 1:
            return self
        rng = random.Random(seed)
        centers = []
        for obj in self.objects:
            bx, by, bw, bh = obj.bbox(start)
            centers.append((bx + bw / 2, by + bh / 2))
        indices = list(range(n))
        rng.shuffle(indices)
        for i, obj in enumerate(self.objects):
            target = centers[indices[i]]
            obj.move_to(target[0], target[1], start_time=start, end_time=end, easing=easing)
        return self

    def for_each(self, method_name, **kwargs):
        """Call a method with the same arguments on all children simultaneously.
        Example: group.for_each('set_color', color='red', start=1)"""
        for obj in self.objects:
            getattr(obj, method_name)(**kwargs)
        return self

    def each(self, func):
        """Call ``func(child)`` for every child and return self.

        Unlike :meth:`for_each` (named method) and :meth:`apply` (passes
        ``(child, index)``), this accepts a plain callable.
        """
        for obj in self.objects:
            func(obj)
        return self

    def flip_all(self, start: float = 0, end: float | None = None, axis='x',
                  easing=easings.smooth):
        """Flip (mirror) all children along an axis through the group's center.
        axis: 'x' (horizontal flip, reflect about vertical center line)
              'y' (vertical flip, reflect about horizontal center line)."""
        n = len(self.objects)
        if n == 0:
            return self
        gx, gy, gw, gh = self.bbox(start)
        gcx, gcy = gx + gw / 2, gy + gh / 2
        for obj in self.objects:
            bx, by, bw, bh = obj.bbox(start)
            cx, cy = bx + bw / 2, by + bh / 2
            if axis == 'x':
                new_cx = 2 * gcx - cx
                obj.move_to(new_cx, cy, start_time=start, end_time=end, easing=easing)
            else:
                new_cy = 2 * gcy - cy
                obj.move_to(cx, new_cy, start_time=start, end_time=end, easing=easing)
        return self

    def stagger_color(self, start: float = 0, end: float = 1, colors=('#FF6B6B', '#58C4DD'),
                       attr='fill'):
        """Propagate a color wave through children — each child transitions
        through the color sequence with a delay."""
        n = len(self.objects)
        if n == 0 or len(colors) < 2:
            return self
        dur = end - start
        if dur <= 0:
            return self
        per_child = dur / n
        for i, obj in enumerate(self.objects):
            t0 = start + i * per_child
            t1 = min(t0 + per_child * 2, end)
            obj.color_gradient_anim(colors=colors, start=t0, end=t1, attr=attr)
        return self

    def stagger_scale(self, start: float = 0, end: float = 1,
                       scale_factor=1.5, delay=0.2, easing=easings.smooth,
                       target_scale=None):
        """Scale each child up then back down with a stagger delay between children.

        Creates a "popping" wave effect where each child grows to *scale_factor*
        and shrinks back to its original size, with *delay* seconds between
        successive children starting their animation.

        scale_factor: peak scale factor for each child's pop.
        delay: time offset between successive children starting.
        target_scale: deprecated alias for scale_factor (backward compatibility).
        """
        if target_scale is not None:
            scale_factor = target_scale
        n = len(self.objects)
        if n == 0 or end <= start:
            return self
        dur = end - start
        # Each child gets a pop duration: total time minus all delays, but
        # at least enough for one cycle
        pop_dur = max(dur - (n - 1) * delay, dur / n) if n > 1 else dur
        for i, obj in enumerate(self.objects):
            s = start + i * delay
            e = min(s + pop_dur, end)
            if e <= s:
                continue
            obj._ensure_scale_origin(s)
            _sx0 = obj.styling.scale_x.at_time(s)
            _sy0 = obj.styling.scale_y.at_time(s)
            _d = max(e - s, 1e-9)
            def _make_pop(base, _s=s, _d=_d, _sf=scale_factor, _easing=easing):
                return lambda t, _b=base: \
                    _b * (1 + (_sf - 1) * math.sin(math.pi * _easing((t - _s) / _d)))
            obj.styling.scale_x.set(s, e, _make_pop(_sx0))
            obj.styling.scale_y.set(s, e, _make_pop(_sy0))
        return self

    def stagger_rotate(self, start: float = 0, end: float = 1, degrees=360, easing=easings.smooth):
        """Sequentially rotate each child."""
        n = len(self.objects)
        if n == 0 or end <= start:
            return self
        dur = end - start
        child_dur = dur / n * 1.5
        step = dur / n
        for i, obj in enumerate(self.objects):
            s = start + i * step
            e = min(s + child_dur, end)
            obj.rotate_by(s, e, degrees, easing=easing)
        return self

    def animate_each(self, method, start: float = 0, end: float = 1,
                     delay=None, reverse=False, **method_kwargs):
        """Call *method* on each child with staggered timing.

        method: string name of a VObject method (e.g. 'fadein', 'wiggle', 'indicate').
        delay: time between each child's start (auto-computed from duration if None).
        reverse: iterate children in reverse order.
        Extra keyword arguments are forwarded to the method.
        """
        n = len(self.objects)
        if n == 0:
            return self
        dur = end - start
        if dur <= 0:
            return self
        if delay is None:
            delay = dur / max(n, 1) * 0.5
        # Clamp delay so children don't overflow past end
        max_delay = dur / max(n, 2)
        delay = min(delay, max_delay)
        child_dur = max(dur - (n - 1) * delay, 0.01)
        items = list(reversed(self.objects)) if reverse else list(self.objects)
        for i, obj in enumerate(items):
            obj_start = start + i * delay
            obj_end = obj_start + child_dur
            getattr(obj, method)(start=obj_start, end=obj_end, **method_kwargs)
        return self

    def scatter_from(self, cx=None, cy=None, radius=300,
                      start: float = 0, end: float = 1, easing=easings.smooth):
        """Explode children outward from a center point.
        Each child moves along the ray from (cx, cy) through its center."""
        n = len(self.objects)
        if n == 0:
            return self
        gx, gy, gw, gh = self.bbox(start)
        cx = cx if cx is not None else gx + gw / 2
        cy = cy if cy is not None else gy + gh / 2
        for i, obj in enumerate(self.objects):
            bx, by, bw, bh = obj.bbox(start)
            ocx, ocy = bx + bw / 2, by + bh / 2
            dx, dy = ocx - cx, ocy - cy
            dist = math.hypot(dx, dy)
            if dist < 1e-6:
                # At center: use evenly-spaced angles
                angle = 2 * math.pi * i / max(n, 1)
                dx, dy = math.cos(angle), math.sin(angle)
                dist = 1
            tx = ocx + dx / dist * radius
            ty = ocy + dy / dist * radius
            obj.move_to(tx, ty, start_time=start, end_time=end, easing=easing)
        return self

    def gather_to(self, cx=None, cy=None,
                   start: float = 0, end: float = 1, easing=easings.smooth):
        """Converge children to a center point (reverse of scatter_from)."""
        n = len(self.objects)
        if n == 0:
            return self
        gx, gy, gw, gh = self.bbox(start)
        cx = cx if cx is not None else gx + gw / 2
        cy = cy if cy is not None else gy + gh / 2
        for obj in self.objects:
            obj.move_to(cx, cy, start_time=start, end_time=end, easing=easing)
        return self

    def rotate_children(self, degrees=90, start: float = 0, end: float | None = None,
                         easing=easings.smooth):
        """Rotate all children around the group's center.
        Moves each child to its new angular position around the centroid."""
        n = len(self.objects)
        if n == 0:
            return self
        gx, gy, gw, gh = self.bbox(start)
        gcx, gcy = gx + gw / 2, gy + gh / 2
        rad = math.radians(degrees)
        for obj in self.objects:
            bx, by, bw, bh = obj.bbox(start)
            cx, cy = bx + bw / 2, by + bh / 2
            # Rotate (cx, cy) around (gcx, gcy)
            dx, dy = cx - gcx, cy - gcy
            new_cx = gcx + dx * math.cos(rad) - dy * math.sin(rad)
            new_cy = gcy + dx * math.sin(rad) + dy * math.cos(rad)
            obj.move_to(new_cx, new_cy, start_time=start, end_time=end, easing=easing)
        return self

    def wave_effect(self, start: float = 0, end: float = 1, amplitude=20, axis='y',
                    easing=easings.smooth):
        """Propagate a wave through children — each child shifts up/down (or left/right)
        with a phase offset creating a traveling wave effect."""
        n = len(self.objects)
        if n == 0:
            return self
        dur = end - start
        if dur <= 0:
            return self
        for i, obj in enumerate(self.objects):
            phase = i / max(n - 1, 1)
            _s, _d, _a, _ph = start, max(dur, 1e-9), amplitude, phase
            def _wave(t, _s=_s, _d=_d, _a=_a, _ph=_ph, _easing=easing):
                p = _easing((t - _s) / _d)
                envelope = math.sin(math.pi * p)  # 0→1→0
                return _a * math.sin(2 * math.pi * (p - _ph)) * envelope
            if axis == 'y':
                for xa, ya in obj._shift_reals():
                    ya.add(start, end, _wave)
                for c in obj._shift_coors():
                    c.add(start, end, lambda t, _w=_wave: (0, _w(t)))
            else:
                for xa, ya in obj._shift_reals():
                    xa.add(start, end, _wave)
                for c in obj._shift_coors():
                    c.add(start, end, lambda t, _w=_wave: (_w(t), 0))
        return self

    def sort_children(self, key='x', start: float = 0, end: float | None = None,
                       easing=easings.smooth):
        """Animate children to sorted positions along their arrangement axis.
        key: 'x' (sort left-to-right by x), 'y' (sort top-to-bottom by y),
             or a callable(obj, time) -> number.
        With end=None, reorders instantly. With end set, animates moves."""
        n = len(self.objects)
        if n <= 1:
            return self
        # Get current centers
        centers = []
        for obj in self.objects:
            bx, by, bw, bh = obj.bbox(start)
            centers.append((bx + bw / 2, by + bh / 2))
        # Determine sort key for values
        if key == 'x':
            val_key = lambda i: centers[i][0]
        elif key == 'y':
            val_key = lambda i: centers[i][1]
        else:
            val_key = lambda i: key(self.objects[i], start)
        # value_order: indices sorted by value (value_order[0] has smallest value)
        value_order = sorted(range(n), key=val_key)
        if end is None:
            self.objects[:] = [self.objects[i] for i in value_order]
            return self
        # Position slots: sorted by position (leftmost/topmost first)
        pos_axis = 0 if key != 'y' else 1
        slot_order = sorted(range(n), key=lambda i: centers[i][pos_axis])
        # Object value_order[rank] should move to center of slot_order[rank]
        for rank in range(n):
            obj_idx = value_order[rank]
            slot_idx = slot_order[rank]
            if obj_idx == slot_idx:
                continue
            target = centers[slot_idx]
            cur = centers[obj_idx]
            dx, dy = target[0] - cur[0], target[1] - cur[1]
            if abs(dx) > 0.5 or abs(dy) > 0.5:
                self.objects[obj_idx].shift(dx=dx, dy=dy,
                    start_time=start, end_time=end, easing=easing)
        return self

    def apply(self, func):
        """Apply a function to each child. The function receives (child, index).
        Returns self for chaining."""
        for i, obj in enumerate(self.objects):
            func(obj, i)
        return self

    def apply_function(self, func):
        """Apply a transformation function to each child.

        The function receives the child and its index: ``func(child, index)``.
        Returns self for chaining.

        Example
        -------
        >>> col.apply_function(lambda obj, i: obj.set_color(0, 1, fill='red'))
        """
        for i, obj in enumerate(self.objects):
            func(obj, i)
        return self

    def zip_with(self, other, method_name_or_func, time=0, **kwargs):
        """Apply a method or function pairwise to children of this and another collection.

        Two calling styles are supported:

        * **Method-name string** — ``method_name_or_func`` is a ``str``; the
          named method is called on each child of *self* with the corresponding
          child of *other* as its first positional argument, followed by any
          extra ``**kwargs``::

              col_a.zip_with(col_b, 'become')
              col_a.zip_with(col_b, 'set_color', start=1, end=2)

        * **Callable** — ``method_name_or_func`` is a callable; it is invoked
          as ``func(obj_a, obj_b, time)`` for each pair (legacy behaviour)::

              col_a.zip_with(col_b, lambda a, b, t: a.move_to(*b.center(t), t))

        Iteration stops at the shorter collection's length.

        Parameters
        ----------
        other:
            Another :class:`VCollection` or any iterable of objects.
        method_name_or_func:
            Either a ``str`` naming a method on each child object, or a
            callable with signature ``(obj_a, obj_b, time)``.
        time:
            Passed through to the callable form; ignored in the method-name
            form unless it is also part of ``**kwargs``.
        **kwargs:
            Extra keyword arguments forwarded to the method when using the
            string form.  Ignored in the callable form.
        """
        other_objs = other.objects if hasattr(other, 'objects') else list(other)
        if isinstance(method_name_or_func, str):
            for a, b in zip(self.objects, other_objs):
                getattr(a, method_name_or_func)(b, **kwargs)
        else:
            for a, b in zip(self.objects, other_objs):
                method_name_or_func(a, b, time)
        return self

    def align_to(self, target, edge='left', start_time: float = 0):
        """Align the collection's edge to match *target*'s edge.
        target: another VObject/VCollection.
        edge: 'left', 'right', 'top', 'bottom' or direction constant."""
        if isinstance(edge, tuple):
            edge = _EDGE_NAMES.get(edge, 'left')
        mx, my, mw, mh = self.bbox(start_time)
        ox, oy, ow, oh = target.bbox(start_time)
        offsets = {
            'left': (ox - mx, 0),
            'right': ((ox + ow) - (mx + mw), 0),
            'top': (0, oy - my),
            'bottom': (0, (oy + oh) - (my + mh)),
        }
        dx, dy = offsets.get(edge, (0, 0))
        for obj in self.objects:
            obj.shift(dx=dx, dy=dy, start_time=start_time)
        return self

    def write(self, start: float = 0, end: float = 1, processing=10, max_stroke_width=2, change_existence=True, easing=easings.smooth):
        if not self.objects:
            return self
        spc = (end - start) / (len(self.objects) + processing)
        for i, obj in enumerate(self.objects):
            obj.write(start=start+spc*i, end=start+spc*(i+processing+1),
                      max_stroke_width=max_stroke_width, change_existence=change_existence,
                      easing=easing)
        return self


    def snake_layout(self, cols=None, buff=SMALL_BUFF, start_time: float = 0):
        """Arrange children in a snake/zigzag grid pattern.

        Like :meth:`arrange_in_grid`, but alternates row direction: the first
        row goes left-to-right, the second row goes right-to-left, and so on.
        This creates a continuous reading path that avoids large jumps between
        row endings and beginnings, useful for flowcharts, timelines, or any
        sequential layout where visual continuity matters.

        Parameters
        ----------
        cols:
            Number of columns per row.  Defaults to ``ceil(sqrt(n))``.
        buff:
            Pixel spacing between cells (default ``SMALL_BUFF``).
        start_time:
            Time at which to read current positions and apply shifts.

        Returns
        -------
        self
        """
        n = len(self.objects)
        if not n:
            return self
        if cols is None:
            cols = math.ceil(math.sqrt(n))
        boxes = [obj.bbox(start_time) for obj in self.objects]
        max_w = max(b[2] for b in boxes)
        max_h = max(b[3] for b in boxes)
        cell_w, cell_h = max_w + buff, max_h + buff
        for idx, (obj, box) in enumerate(zip(self.objects, boxes)):
            r, c = divmod(idx, cols)
            # Reverse column order on odd rows (snake pattern)
            if r % 2 == 1:
                c = cols - 1 - c
            target_cx = c * cell_w + max_w / 2
            target_cy = r * cell_h + max_h / 2
            cur_cx = box[0] + box[2] / 2
            cur_cy = box[1] + box[3] / 2
            obj.shift(dx=target_cx - cur_cx, dy=target_cy - cur_cy,
                      start_time=start_time)
        return self

    def arrange_along_path(self, path_d, start_time: float = 0,
                           easing=None):
        """Position children evenly along an arbitrary SVG path.

        Each child's center is moved to a point on the path.  The children
        are spaced equally by arc length so they distribute uniformly along
        curves, straight segments, or any combination.

        Parameters
        ----------
        path_d:
            An SVG path ``d`` attribute string (e.g.
            ``'M100,500 C300,100 600,100 800,500'``).
        start_time:
            Time at which to read current positions and apply shifts.
        easing:
            Optional easing function to remap the parameter distribution.
            When ``None`` children are spaced uniformly by arc length.

        Returns
        -------
        self
        """
        n = len(self.objects)
        if n == 0:
            return self
        import svgpathtools
        parsed = svgpathtools.parse_path(path_d)
        total_length = parsed.length()
        if total_length <= 0:
            return self
        for i, obj in enumerate(self.objects):
            t = i / max(n - 1, 1)
            if easing is not None:
                t = easing(t)
            target_len = t * total_length
            pt = parsed.point(parsed.ilength(target_len))
            tx, ty = pt.real, pt.imag
            bx, by, bw, bh = obj.bbox(start_time)
            cx, cy = bx + bw / 2, by + bh / 2
            obj.shift(dx=tx - cx, dy=ty - cy, start_time=start_time)
        return self

    def converge(self, x: float = 960, y: float = 540,
                 start: float = 0, end: float = 1, easing=easings.smooth):
        """Animate all children moving toward a common point.

        Each child slides from its current center to the target point (x, y)
        over [start, end].  This is useful for gathering scattered objects
        into a single location.

        Parameters
        ----------
        x, y:
            Target convergence point in SVG coordinates.
            Defaults to the canvas center (960, 540).
        start:
            Animation start time.
        end:
            Animation end time.
        easing:
            Easing function for the movement.

        Returns
        -------
        self
        """
        if not self.objects or end <= start:
            return self
        for obj in self.objects:
            bx, by, bw, bh = obj.bbox(start)
            ox, oy = bx + bw / 2, by + bh / 2
            dx, dy = x - ox, y - oy
            if dx == 0 and dy == 0:
                continue
            obj.shift(dx=dx, dy=dy, start_time=start, end_time=end, easing=easing)
        return self

    def diverge(self, factor: float = 2.0, cx: float | None = None,
                cy: float | None = None, start: float = 0, end: float = 1,
                easing=easings.smooth):
        """Animate all children moving away from a common center.

        Each child slides outward from the collection's center (or the
        specified center) by a distance equal to *factor* times its
        current offset.  A factor of 2.0 doubles each child's distance
        from the center.

        Parameters
        ----------
        factor:
            Expansion multiplier.  Values > 1 spread children apart;
            values between 0 and 1 bring them closer together (but see
            :meth:`converge` for bringing them to a single point).
        cx, cy:
            Center of expansion.  Defaults to the collection's bounding
            box center at *start*.
        start:
            Animation start time.
        end:
            Animation end time.
        easing:
            Easing function for the movement.

        Returns
        -------
        self
        """
        if not self.objects or end <= start:
            return self
        if cx is None or cy is None:
            bx, by, bw, bh = self.bbox(start)
            cx = bx + bw / 2
            cy = by + bh / 2
        for obj in self.objects:
            bx, by, bw, bh = obj.bbox(start)
            obj_cx, obj_cy = bx + bw / 2, by + bh / 2
            dx = (obj_cx - cx) * (factor - 1)
            dy = (obj_cy - cy) * (factor - 1)
            if dx == 0 and dy == 0:
                continue
            obj.shift(dx=dx, dy=dy, start_time=start, end_time=end, easing=easing)
        return self

    def all_match(self, predicate):
        """Return True if all children match the predicate."""
        return all(predicate(obj) for obj in self.objects)

    def any_match(self, predicate):
        """Return True if any child matches the predicate."""
        return any(predicate(obj) for obj in self.objects)

    def pair_up(self):
        """Group adjacent children into pairs.

        Returns a list of :class:`VCollection` objects, each containing
        exactly two children.  If the number of children is odd, the last
        child is placed alone in a final single-element collection.

        This is useful for pairing labels with shapes, creating before/after
        pairs, or processing children two at a time.

        Returns
        -------
        list of VCollection
            Each collection contains two adjacent children (or one if the
            total count is odd).

        Raises
        ------
        ValueError
            If the collection is empty.

        Examples
        --------
        >>> col = VCollection(a, b, c, d)
        >>> pairs = col.pair_up()
        >>> len(pairs)
        2
        >>> len(pairs[0].objects)
        2
        """
        if len(self.objects) == 0:
            raise ValueError("Cannot pair_up an empty collection")
        result = []
        objs = self.objects
        for i in range(0, len(objs), 2):
            group = objs[i:i + 2]
            result.append(VCollection(*group))
        return result

    def sliding_window(self, size: int, step: int = 1):
        """Yield overlapping sub-collections using a sliding window.

        Slides a window of *size* elements across the children list,
        advancing by *step* each time.  Each window is returned as a
        :class:`VCollection`.

        Parameters
        ----------
        size:
            Number of children in each window.  Must be >= 1.
        step:
            Number of positions to advance between windows.  Must be >= 1.

        Returns
        -------
        list of VCollection
            Each sub-collection contains *size* children (the last window
            may contain fewer if *step* does not divide evenly).

        Raises
        ------
        ValueError
            If *size* or *step* is less than 1.

        Examples
        --------
        >>> col = VCollection(a, b, c, d, e)
        >>> windows = col.sliding_window(3, step=1)
        >>> len(windows)
        3
        >>> [len(w.objects) for w in windows]
        [3, 3, 3]
        """
        if size < 1:
            raise ValueError(f"window size must be >= 1, got {size!r}")
        if step < 1:
            raise ValueError(f"step must be >= 1, got {step!r}")
        objs = self.objects
        result = []
        i = 0
        while i + size <= len(objs):
            result.append(VCollection(*objs[i:i + size]))
            i += step
        return result

    def waterfall(self, start: float = 0, end: float = 1, height: float = 200,
                  stagger_frac: float = 0.3, easing=easings.smooth):
        """Staggered gravity-like entrance: children drop in from above.

        Each child starts above its final position (offset by *height* pixels)
        and falls down into place with a cascading delay.  Children also fade
        in during the fall.  Earlier children in the list start falling first.

        Parameters
        ----------
        start, end:
            Overall time interval for the waterfall.
        height:
            How far above its resting position each child starts (pixels).
        stagger_frac:
            Fraction of each child's duration that overlaps with the next
            child's start (0 = fully sequential, 1 = all start at once).
        easing:
            Easing function for each child's fall; ``easings.smooth`` gives
            a decelerating landing feel.

        Returns
        -------
        self
        """
        n = len(self.objects)
        if n == 0:
            return self
        dur = end - start
        if dur <= 0:
            return self
        # Compute per-child window with stagger overlap
        if n == 1:
            child_dur = dur
            delay = 0
        else:
            # Each child gets a window; consecutive windows overlap by stagger_frac
            child_dur = dur / (1 + (1 - stagger_frac) * (n - 1))
            delay = child_dur * (1 - stagger_frac)

        for i, obj in enumerate(self.objects):
            cs = start + i * delay
            ce = cs + child_dur
            # Hide before entrance
            obj.show.set_onward(0, False)
            obj.show.set_onward(cs, True)
            # Fade in
            _cs, _cd = cs, max(ce - cs, 1e-9)
            end_opacity = obj.styling.opacity.at_time(cs)
            obj.styling.opacity.set(cs, ce,
                lambda t, _s=_cs, _d=_cd, _ev=end_opacity, _e=easing:
                    _ev * _e((t - _s) / _d))
            # Drop from above: shift up by height, then animate down
            _h = height
            def _dy(t, _s=_cs, _d=_cd, _h=_h, _e=easing):
                p = _e((t - _s) / _d)
                return -_h * (1 - p)
            for xa, ya in obj._shift_reals():
                ya.add(cs, ce, _dy, stay=True)
            for c in obj._shift_coors():
                c.add(cs, ce, lambda t, _f=_dy: (0, _f(t)), stay=True)
        return self

    def orbit_around(self, cx=None, cy=None, radius=None,
                     start: float = 0, end: float = 1, revolutions: float = 1,
                     easing=easings.linear):
        """Animate children orbiting around a center point.

        Each child is placed on a circle at equal angular intervals and
        then rotated around (cx, cy) over the time interval.  Children
        maintain their angular spacing while revolving.

        Parameters
        ----------
        cx, cy:
            Center of the orbit.  Defaults to the collection's bounding-box
            center.
        radius:
            Orbit radius in pixels.  Defaults to the average distance from
            each child's center to (cx, cy) at *start*.
        start, end:
            Time interval for the orbit animation.
        revolutions:
            Number of full revolutions (1.0 = 360 degrees).
        easing:
            Easing function applied to the angular progress.  Use
            ``easings.linear`` for constant-speed orbiting.

        Returns
        -------
        self
        """
        n = len(self.objects)
        if n == 0:
            return self
        dur = end - start
        if dur <= 0:
            return self
        # Resolve center
        if cx is None or cy is None:
            bx, by, bw, bh = self.bbox(start)
            cx = bx + bw / 2 if cx is None else cx
            cy = by + bh / 2 if cy is None else cy
        # Compute initial angle and radius for each child
        child_data = []
        for obj in self.objects:
            bx, by, bw, bh = obj.bbox(start)
            ocx, ocy = bx + bw / 2, by + bh / 2
            dx, dy = ocx - cx, ocy - cy
            dist = math.hypot(dx, dy)
            angle0 = math.atan2(dy, dx)
            child_data.append((angle0, dist, ocx, ocy))
        if radius is None:
            radius = sum(d[1] for d in child_data) / max(n, 1)
            # Use at least a small radius to avoid degenerate orbits
            if radius < 1:
                radius = 100
        _s, _d = start, max(dur, 1e-9)
        _cx, _cy, _r, _rev = cx, cy, radius, revolutions

        for i, obj in enumerate(self.objects):
            angle0, _, ocx, ocy = child_data[i]
            _a0, _ocx, _ocy = angle0, ocx, ocy
            def _dx(t, _s=_s, _d=_d, _cx=_cx, _r=_r, _rev=_rev,
                    _a0=_a0, _ocx=_ocx, _e=easing):
                p = _e((t - _s) / _d)
                angle = _a0 + 2 * math.pi * _rev * p
                return _cx + _r * math.cos(angle) - _ocx
            def _dy(t, _s=_s, _d=_d, _cy=_cy, _r=_r, _rev=_rev,
                    _a0=_a0, _ocy=_ocy, _e=easing):
                p = _e((t - _s) / _d)
                angle = _a0 + 2 * math.pi * _rev * p
                return _cy + _r * math.sin(angle) - _ocy
            for xa, ya in obj._shift_reals():
                xa.add(start, end, _dx)
                ya.add(start, end, _dy)
            for c in obj._shift_coors():
                c.add(start, end,
                      lambda t, _fdx=_dx, _fdy=_dy: (_fdx(t), _fdy(t)))
        return self

    def cascade_scale(self, start: float = 0, end: float = 1, factor=1.5,
                      delay=0.15, easing=easings.smooth):
        """Stagger scale animations across children with a fixed delay.

        Each child scales from its current size to *factor* times its size
        and back, with each successive child starting *delay* seconds after
        the previous one.  The per-child animation duration is automatically
        computed so that the last child finishes at *end*.

        Parameters
        ----------
        start, end:
            Overall time window for the staggered animation.
        factor:
            Peak scale multiplier for each child's pulse.
        delay:
            Seconds between the start of one child's animation and the next.
        easing:
            Easing used for the there-and-back scale motion.
        """
        n = len(self.objects)
        if n == 0:
            return self
        dur = end - start
        if dur <= 0:
            return self
        # Per-child animation duration
        total_delay = delay * (n - 1) if n > 1 else 0
        child_dur = max(dur - total_delay, 0.01)
        for i, obj in enumerate(self.objects):
            s = start + i * delay
            e = min(s + child_dur, end)
            obj._ensure_scale_origin(s)
            sx0 = obj.styling.scale_x.at_time(s)
            sy0 = obj.styling.scale_y.at_time(s)
            _s, _d, _f = s, max(e - s, 1e-9), factor
            def _make_there_and_back(base, _s=_s, _d=_d, _f=_f, _easing=easing):
                return lambda t, _s=_s, _d=_d, _f=_f, _b=base, _easing=_easing: \
                    _b * (1 + (_f - 1) * math.sin(math.pi * _easing((t - _s) / _d)))
            obj.styling.scale_x.set(s, e, _make_there_and_back(sx0))
            obj.styling.scale_y.set(s, e, _make_there_and_back(sy0))
        return self

    def distribute_along_arc(self, cx=960, cy=540, radius=200,
                              start_angle=0, end_angle=None,
                              start_time: float = 0,
                              end_time: float | None = None,
                              easing=easings.smooth):
        """Arrange children evenly along a circular arc.

        Unlike :meth:`distribute_radial` (which places children around a
        full circle), this method distributes children along an arc spanning
        from *start_angle* to *end_angle* (in radians).

        Parameters
        ----------
        cx, cy:
            Center of the arc (default: canvas center).
        radius:
            Arc radius in pixels.
        start_angle:
            Starting angle in radians (0 = right, pi/2 = down).
        end_angle:
            Ending angle in radians.  Defaults to ``start_angle + pi``
            (a semicircle).
        start_time:
            Time at which to read current positions and apply the layout.
        end_time:
            If given, animate the children into position over
            [start_time, end_time].  If ``None``, positions are set
            instantly.
        easing:
            Easing for the animated version.
        """
        n = len(self.objects)
        if n == 0:
            return self
        if end_angle is None:
            end_angle = start_angle + math.pi
        # For a single object, place it at the midpoint of the arc
        if n == 1:
            angle = (start_angle + end_angle) / 2
        for i, obj in enumerate(self.objects):
            if n > 1:
                t_frac = i / (n - 1)
                angle = start_angle + (end_angle - start_angle) * t_frac
            tx = cx + radius * math.cos(angle)
            ty = cy + radius * math.sin(angle)
            bx, by, bw, bh = obj.bbox(start_time)
            obj_cx, obj_cy = bx + bw / 2, by + bh / 2
            dx, dy = tx - obj_cx, ty - obj_cy
            if end_time is None:
                obj.shift(dx=dx, dy=dy, start_time=start_time)
            else:
                obj.shift(dx=dx, dy=dy, start_time=start_time,
                          end_time=end_time, easing=easing)
        return self

    def fan_out(self, cx: float | None = None, cy: float | None = None,
                radius: float = 200, start: float = 0, end: float = 1,
                easing=easings.smooth):
        """Animate children spreading radially from a center point.

        All children move from their current positions to evenly spaced points
        on a circle of the given radius around (cx, cy).  If cx/cy are None,
        the collection's bounding box center is used.

        This is a creation/reveal animation: children fan outward like
        cards being dealt from a deck.
        """
        n = len(self.objects)
        if n == 0:
            return self
        if cx is None or cy is None:
            gx, gy, gw, gh = self.bbox(start)
            if cx is None:
                cx = gx + gw / 2
            if cy is None:
                cy = gy + gh / 2
        for i, obj in enumerate(self.objects):
            angle = 2 * math.pi * i / n
            tx = cx + radius * math.cos(angle)
            ty = cy + radius * math.sin(angle)
            bx, by, bw, bh = obj.bbox(start)
            obj_cx, obj_cy = bx + bw / 2, by + bh / 2
            dx, dy = tx - obj_cx, ty - obj_cy
            obj.shift(dx=dx, dy=dy, start_time=start, end_time=end, easing=easing)
        return self

    def align_centers(self, axis='x', value: float | None = None,
                      start_time: float = 0, end_time: float | None = None,
                      easing=easings.smooth):
        """Align all children's centers along a common axis line.

        axis: 'x' to align vertically (same x center) or 'y' to align
              horizontally (same y center).
        value: the target coordinate. If None, uses the collection's
               bounding box center for that axis.
        """
        n = len(self.objects)
        if n == 0:
            return self
        if value is None:
            gx, gy, gw, gh = self.bbox(start_time)
            value = (gx + gw / 2) if axis == 'x' else (gy + gh / 2)
        for obj in self.objects:
            bx, by, bw, bh = obj.bbox(start_time)
            if axis == 'x':
                dx = value - (bx + bw / 2)
                dy = 0
            else:
                dx = 0
                dy = value - (by + bh / 2)
            if dx != 0 or dy != 0:
                obj.shift(dx=dx, dy=dy, start_time=start_time,
                          end_time=end_time, easing=easing)
        return self

    def distribute_evenly(self, start_x, start_y, end_x, end_y):
        """Distribute children evenly along a line from (start_x, start_y) to (end_x, end_y).

        The first child is centered at the start point, the last child at the
        end point, and the rest are evenly spaced between them.  With a single
        child, it is placed at the start point.  Returns self.
        """
        n = len(self.objects)
        if n == 0:
            return self
        if n == 1:
            self.objects[0].center_to_pos(posx=start_x, posy=start_y)
            return self
        for i, obj in enumerate(self.objects):
            frac = i / (n - 1)
            px = start_x + frac * (end_x - start_x)
            py = start_y + frac * (end_y - start_y)
            obj.center_to_pos(posx=px, posy=py)
        return self

    def cascade_fadein(self, start=0, end=1, direction='left_to_right', easing=easings.smooth):
        """Fade in children with a cascade effect based on spatial ordering.

        direction determines sort order:
          'left_to_right' - sorts by x-position (ascending)
          'top_to_bottom' - sorts by y-position (ascending)
          'center_out' - sorts by distance from collection center (ascending)

        Each child gets a staggered fadein. Returns self.
        """
        n = len(self.objects)
        if n == 0:
            return self
        dur = end - start
        if dur <= 0:
            return self
        # Sort children by spatial criteria
        if direction == 'left_to_right':
            sorted_objs = sorted(self.objects, key=lambda o: o.center(start)[0])
        elif direction == 'top_to_bottom':
            sorted_objs = sorted(self.objects, key=lambda o: o.center(start)[1])
        elif direction == 'center_out':
            group_cx, group_cy = self.center(start)
            def _dist(o):
                ox, oy = o.center(start)
                return math.hypot(ox - group_cx, oy - group_cy)
            sorted_objs = sorted(self.objects, key=_dist)
        else:
            sorted_objs = list(self.objects)
        if n == 1:
            sorted_objs[0].fadein(start=start, end=end, easing=easing)
            return self
        # Compute staggered timing with overlap
        overlap = 0.5
        child_dur = dur / (1 + (1 - overlap) * (n - 1))
        step = child_dur * (1 - overlap)
        for i, obj in enumerate(sorted_objs):
            s = start + i * step
            e = s + child_dur
            obj.fadein(start=s, end=e, easing=easing)
        return self


    def label_children(self, labels, direction=UP, buff=20, font_size=None, creation=0):
        """Create Text labels positioned relative to each child.

        Parameters
        ----------
        labels : list[str]
            List of label strings, one per child.
        direction : tuple
            Direction to place labels relative to children (e.g. UP, DOWN).
        buff : float
            Buffer space between child and label.
        font_size : float or None
            Font size for labels. If None, uses the default (48).
        creation : float
            Creation time for the label objects.

        Returns
        -------
        VCollection
            A new VCollection containing the Text labels.
        """
        from vectormation._shapes import Text  # lazy to avoid circular import
        label_objects = []
        for i, obj in enumerate(self.objects):
            if i >= len(labels):
                break
            text_kwargs = {'creation': creation}
            if font_size is not None:
                text_kwargs['font_size'] = font_size
            label = Text(labels[i], **text_kwargs)
            label.next_to(obj, direction=direction, buff=buff, start_time=creation)
            label_objects.append(label)
        return VCollection(*label_objects)

    def batch_animate(self, method_name, start=0, end=1, param_name=None, values=None, **kwargs):
        """Call a method on each child with a different parameter value.

        The *start* and *end* timing parameters are passed to the target
        method using whichever naming convention it expects.  If *kwargs*
        already contains explicit timing keys (``start``, ``end``,
        ``start_time``, ``end_time``), those take precedence.  Otherwise
        this method inspects the target to choose the right names.

        Parameters
        ----------
        method_name : str
            Name of the method to call on each child.
        start : float
            Start time for the animation.
        end : float
            End time for the animation.
        param_name : str or None
            If given, this keyword argument varies per child.
        values : list or None
            List of values, one per child. If param_name is given, each value
            is passed as that kwarg. Otherwise, each value is passed as the
            first positional argument after start/end.
        **kwargs
            Additional keyword arguments passed to every child's method call.

        Returns
        -------
        self
        """
        import inspect
        if values is None:
            values = [None] * len(self.objects)
        for i, obj in enumerate(self.objects):
            if i >= len(values):
                break
            method = getattr(obj, method_name)
            kw = dict(kwargs)
            # Add timing parameters if not already provided by caller
            has_timing = any(k in kw for k in ('start', 'end', 'start_time', 'end_time'))
            if not has_timing:
                sig = inspect.signature(method)
                params = sig.parameters
                if 'start_time' in params:
                    kw['start_time'] = start
                    if 'end_time' in params:
                        kw['end_time'] = end
                elif 'start' in params:
                    kw['start'] = start
                    if 'end' in params:
                        kw['end'] = end
            if param_name is not None:
                kw[param_name] = values[i]
                method(**kw)
            else:
                method(values[i], **kw)
        return self


VGroup = VCollection

