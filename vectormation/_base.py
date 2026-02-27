"""Base classes (VObject, VCollection) and shared constants."""
import math
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any
from vectormation.pathbbox import path_bbox
from vectormation._constants import (
    SMALL_BUFF, DEFAULT_OBJECT_TO_EDGE_BUFF,
    UP, DOWN, LEFT, RIGHT, UL, UR, DL, DR, ORIGIN,
)

import vectormation.easings as easings
import vectormation.attributes as attributes
import vectormation.style as style
import vectormation.morphing as morphing


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
        x, y, w, h = self.bbox(time)
        points = {
            'center': (x + w / 2, y + h / 2),
            'top': (x + w / 2, y), 'bottom': (x + w / 2, y + h),
            'left': (x, y + h / 2), 'right': (x + w, y + h / 2),
            'top_left': (x, y), 'top_right': (x + w, y),
            'bottom_left': (x, y + h), 'bottom_right': (x + w, y + h),
        }
        return points[edge]

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
            # Scale each axis independently — may distort aspect ratio
            x_factor = width / cur_w if cur_w != 0 else 1
            y_factor = height / cur_h if cur_h != 0 else 1
            target_sx = self.styling.scale_x.at_time(start) * x_factor
            target_sy = self.styling.scale_y.at_time(start) * y_factor
            if end is None:
                self.styling.scale_x.set_onward(start, target_sx)
                self.styling.scale_y.set_onward(start, target_sy)
            else:
                self.styling.scale_x.move_to(start, end, target_sx, easing=easing)
                self.styling.scale_y.move_to(start, end, target_sy, easing=easing)
        elif width is not None:
            factor = width / cur_w if cur_w != 0 else 1
            target_s = self.styling.scale_x.at_time(start) * factor
            if end is None:
                self.styling.scale_x.set_onward(start, target_s)
                self.styling.scale_y.set_onward(start, target_s)
            else:
                self.styling.scale_x.move_to(start, end, target_s, easing=easing)
                self.styling.scale_y.move_to(start, end, target_s, easing=easing)
        elif height is not None:
            factor = height / cur_h if cur_h != 0 else 1
            target_s = self.styling.scale_y.at_time(start) * factor
            if end is None:
                self.styling.scale_x.set_onward(start, target_s)
                self.styling.scale_y.set_onward(start, target_s)
            else:
                self.styling.scale_x.move_to(start, end, target_s, easing=easing)
                self.styling.scale_y.move_to(start, end, target_s, easing=easing)
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

    def color_wave(self, start: float = 0, end: float = 1, colors=('#FF6B6B', '#58C4DD', '#83C167'),
                    attr='fill', cycles=1):
        """Cycle through colors in a smooth wave pattern.
        colors: tuple of hex color strings to cycle through.
        attr: 'fill' or 'stroke'. cycles: number of full loops."""
        if len(colors) < 2:
            return self
        n_colors = len(colors)
        dur = end - start
        if dur <= 0:
            return self
        # Parse hex colors to RGB tuples
        parsed = []
        for c in colors:
            parsed.append((int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)))
        _s, _d, _n, _p, _cyc = start, max(dur, 1e-9), n_colors, parsed, cycles
        def _interp_rgb(t, _s=_s, _d=_d, _n=_n, _p=_p, _cyc=_cyc):
            p = ((t - _s) / _d) * _cyc
            p = p % 1.0  # wrap to [0, 1)
            idx = p * _n
            i = int(idx) % _n
            j = (i + 1) % _n
            frac = idx - int(idx)
            c1, c2 = _p[i], _p[j]
            return (c1[0] + (c2[0] - c1[0]) * frac,
                    c1[1] + (c2[1] - c1[1]) * frac,
                    c1[2] + (c2[2] - c1[2]) * frac)
        style_attr = getattr(self.styling, attr)
        # Store the function directly, preserving 'rgb' type
        style_attr.use = 'rgb'
        style_attr.set(start, end, _interp_rgb, stay=False)
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

    def grow_from_center(self, start: float = 0, end: float = 1, change_existence=True, easing=easings.smooth):
        """Animate scaling from 0 to 1 (grow in from nothing), scaling around the object's center."""
        if change_existence:
            self._show_from(start)
        self._scale_anim(start, end, lambda p: p, easing, stay=True)
        return self

    def shrink_to_center(self, start: float = 0, end: float = 1, change_existence=True, easing=easings.smooth):
        """Animate scaling from 1 to 0 (shrink out to nothing), scaling around the object's center."""
        self._scale_anim(start, end, lambda p: 1 - p, easing, stay=True)
        if change_existence:
            self._hide_from(end)
        return self

    def elastic_in(self, start: float = 0, end: float = 1, change_existence=True):
        """Scale in with elastic bounce (overshoot then settle)."""
        if change_existence:
            self._show_from(start)
        self._scale_anim(start, end, lambda p: p, easings.ease_out_elastic, stay=True)
        return self

    def elastic_out(self, start: float = 0, end: float = 1, change_existence=True):
        """Scale out with elastic bounce."""
        self._scale_anim(start, end, lambda p: 1 - p, easings.ease_in_elastic, stay=True)
        if change_existence:
            self._hide_from(end)
        return self

    def bounce_in(self, start: float = 0, end: float = 1, change_existence=True,
                  easing=easings.ease_out_bounce):
        """Appear by scaling from 0 to 1 with bounce easing.

        Gives a "dropped from above" feel — the object lands and settles with
        small bounces.  Uses ease_out_bounce by default, unlike pop_in (which
        uses a custom overshoot curve) or elastic_in (which uses elastic easing).
        """
        if change_existence:
            self._show_from(start)
        self._scale_anim(start, end, lambda p: p, easing, stay=True)
        return self

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
        sx0 = self.styling.scale_x.at_time(start)
        sy0 = self.styling.scale_y.at_time(start)
        scale_x = lambda t, _s=s, _d=dur, _b=sx0: _b * (1 + (factor - 1) * easing((t - _s) / _d))
        scale_y = lambda t, _s=s, _d=dur, _b=sy0: _b * (1 + (factor - 1) * easing((t - _s) / _d))
        self.styling.scale_x.set(s, end, scale_x)
        self.styling.scale_y.set(s, end, scale_y)
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
              duration: float = 0.3, easing=easings.smooth):
        """Flash opacity on/off.

        When *end* is given, divides [start, end] into *count* square-wave cycles:
        each cycle toggles the opacity from 1 to 0 and back using the easing.
        When *end* is None (legacy single-blink mode), blinks once over *duration*
        seconds with a smooth fade to 0 and back.
        """
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
        from vectormation._base import VCollection
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

    def wipe(self, direction='right', start: float = 0, end: float = 1,
             easing=easings.smooth, reverse=False):
        """Reveal (or hide if reverse=True) with a clip-path wipe effect.
        direction: 'right', 'left', 'up', 'down'.
        Uses SVG clip-path inset() to animate a clipping rectangle."""
        dur = end - start
        if dur <= 0:
            return self
        s = start
        # inset(top right bottom left) — percentages from each edge
        if direction in ('right', 'left'):
            if (direction == 'right') != reverse:
                func = lambda t, _s=s, _d=dur: f'inset(0 {100 * (1 - easing((t - _s) / _d)):.1f}% 0 0)'
            else:
                func = lambda t, _s=s, _d=dur: f'inset(0 0 0 {100 * (1 - easing((t - _s) / _d)):.1f}%)'
        else:
            if (direction == 'down') != reverse:
                func = lambda t, _s=s, _d=dur: f'inset(0 0 {100 * (1 - easing((t - _s) / _d)):.1f}% 0)'
            else:
                func = lambda t, _s=s, _d=dur: f'inset({100 * (1 - easing((t - _s) / _d)):.1f}% 0 0 0)'
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
        cx, cy = bx + bw / 2, by + bh / 2
        if axis == 'vertical':
            self.styling.scale_x.set_onward(start_time,
                -self.styling.scale_x.at_time(start_time))
            self.styling._scale_origin = (cx, cy)
        else:
            self.styling.scale_y.set_onward(start_time,
                -self.styling.scale_y.at_time(start_time))
            self.styling._scale_origin = (cx, cy)
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
        cx, cy = bx + bw / 2, by + bh / 2
        self.styling._scale_origin = (cx, cy)
        sx0 = self.styling.scale_x.at_time(start)
        sy0 = self.styling.scale_y.at_time(start)
        _s, _d, _f, _sx0, _sy0 = start, max(dur, 1e-9), factor, sx0, sy0
        if axis == 'x':
            def _sx(t, _s=_s, _d=_d, _f=_f, _sx0=_sx0, _easing=easing):
                p = _easing((t - _s) / _d)
                squeeze = 1 + (_f - 1) * math.sin(math.pi * p)
                return _sx0 * squeeze
            def _sy(t, _s=_s, _d=_d, _f=_f, _sy0=_sy0, _easing=easing):
                p = _easing((t - _s) / _d)
                squeeze = 1 + (_f - 1) * math.sin(math.pi * p)
                return _sy0 / squeeze if squeeze > 1e-9 else _sy0
            self.styling.scale_x.set(start, end, _sx, stay=False)
            self.styling.scale_y.set(start, end, _sy, stay=False)
        else:
            def _sy2(t, _s=_s, _d=_d, _f=_f, _sy0=_sy0, _easing=easing):
                p = _easing((t - _s) / _d)
                squeeze = 1 + (_f - 1) * math.sin(math.pi * p)
                return _sy0 * squeeze
            def _sx2(t, _s=_s, _d=_d, _f=_f, _sx0=_sx0, _easing=easing):
                p = _easing((t - _s) / _d)
                squeeze = 1 + (_f - 1) * math.sin(math.pi * p)
                return _sx0 / squeeze if squeeze > 1e-9 else _sx0
            self.styling.scale_y.set(start, end, _sy2, stay=False)
            self.styling.scale_x.set(start, end, _sx2, stay=False)
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
        """Rhythmic pulsing like a heartbeat — repeated grow/shrink cycles.
        beats: number of pulses. scale_factor: peak scale multiplier."""
        return self.pulsate(start=start, end=end, scale_factor=scale_factor,
                            pulses=beats, easing=easing)

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
        cur_f = self.styling.fill_opacity.at_time(start)
        cur_s = self.styling.stroke_opacity.at_time(start)
        if end is None:
            self.styling.fill_opacity.set_onward(start, opacity)
            self.styling.stroke_opacity.set_onward(start, opacity)
        else:
            dur = end - start
            if dur <= 0:
                return self
            s = start
            self.styling.fill_opacity.set(s, end,
                lambda t, _s=s, _d=dur, _cf=cur_f, _o=opacity: _cf + (_o - _cf) * easing((t - _s) / _d), stay=True)
            self.styling.stroke_opacity.set(s, end,
                lambda t, _s=s, _d=dur, _cs=cur_s, _o=opacity: _cs + (_o - _cs) * easing((t - _s) / _d), stay=True)
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
        if end is None:
            self.styling.fill_opacity.set_onward(start, value)
            self.styling.opacity.set_onward(start, value)
        else:
            self.styling.fill_opacity.move_to(start, end, value, easing=easing)
            self.styling.opacity.move_to(start, end, value, easing=easing)
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
        target_x = self.styling.scale_x.at_time(start) * x_factor
        target_y = self.styling.scale_y.at_time(start) * y_factor
        if end is None:
            self.styling.scale_x.set_onward(start, target_x)
            self.styling.scale_y.set_onward(start, target_y)
        else:
            self.styling.scale_x.move_to(start, end, target_x, easing=easing)
            self.styling.scale_y.move_to(start, end, target_y, easing=easing)
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

    @staticmethod
    def surround(other, buff=SMALL_BUFF, rx=6, ry=6, start_time: float = 0, follow=True):
        """Create a rectangle surrounding another object. Returns a Rectangle."""
        return _make_brect(other.bbox, start_time, rx, ry, buff, follow)


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
        x, y, w, h = self.bbox(time)
        points = {
            'center': (x + w / 2, y + h / 2),
            'top': (x + w / 2, y), 'bottom': (x + w / 2, y + h),
            'left': (x, y + h / 2), 'right': (x + w, y + h / 2),
            'top_left': (x, y), 'top_right': (x + w, y),
            'bottom_left': (x, y + h), 'bottom_right': (x + w, y + h),
        }
        return points[edge]

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
        target_x = self._scale_x.at_time(start) * x_factor
        target_y = self._scale_y.at_time(start) * y_factor
        if end is None:
            self._scale_x.set_onward(start, target_x)
            self._scale_y.set_onward(start, target_y)
        else:
            self._scale_x.move_to(start, end, target_x, easing=easing)
            self._scale_y.move_to(start, end, target_y, easing=easing)
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
        """Animate swapping the positions of children at indices i and j."""
        n = len(self.objects)
        if i < 0 or j < 0 or i >= n or j >= n or i == j:
            return self
        a, b = self.objects[i], self.objects[j]
        ax, ay, aw, ah = a.bbox(start)
        bx, by, bw, bh = b.bbox(start)
        acx, acy = ax + aw / 2, ay + ah / 2
        bcx, bcy = bx + bw / 2, by + bh / 2
        # Move a to b's position and vice versa using path_arc for visual interest
        a.path_arc(bcx, bcy, start=start, end=end, angle=math.pi / 3, easing=easing)
        b.path_arc(acx, acy, start=start, end=end, angle=math.pi / 3, easing=easing)
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
            obj.color_wave(start=t0, end=t1, colors=colors, attr=attr, cycles=1)
        return self

    def stagger_scale(self, start: float = 0, end: float = 1, target_scale=1.5, easing=easings.smooth):
        """Sequentially scale each child up then back to 1."""
        n = len(self.objects)
        if n == 0 or end <= start:
            return self
        dur = end - start
        child_dur = dur / n * 1.5  # overlap
        step = dur / n
        for i, obj in enumerate(self.objects):
            s = start + i * step
            e = min(s + child_dur, end)
            obj.pulsate(start=s, end=e, scale_factor=target_scale, easing=easing)
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


VGroup = VCollection

