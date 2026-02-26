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
    _cache = {}
    def _bbox(t):
        if t not in _cache:
            _cache.clear()
            _cache[t] = bbox_func(t, **bbox_kw)
        return _cache[t]
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
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

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
        from copy import deepcopy
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

    def move_to(self, x, y, start_time: float = 0, end_time: float | None = None, easing=easings.smooth):
        """Move the object's center to (x, y), optionally animated over [start_time, end_time]."""
        xmin, ymin, w, h = self.bbox(start_time)
        self.shift(dx=x-(xmin+w/2), dy=y-(ymin+h/2),
                   start_time=start_time, end_time=end_time, easing=easing)
        return self

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
        chord = math.sqrt(dx * dx + dy * dy)
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
            r = math.sqrt((_sx - _cx) ** 2 + (_sy - _cy) ** 2)
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

    def rotate_in(self, start: float = 0, end: float = 1, degrees=90,
                    change_existence=True, easing=easings.smooth):
        """Fade in while rotating from an offset angle to 0."""
        dur = end - start
        if dur <= 0:
            return self
        if change_existence:
            self._show_from(start)
        self._ensure_scale_origin(start)
        cx, cy = self.styling._scale_origin
        s = start
        self.styling.rotation.set(s, end,
            lambda t, _s=s, _d=dur, _deg=degrees, _cx=cx, _cy=cy: (_deg * (1 - easing((t - _s) / _d)), _cx, _cy),
            stay=True)
        target_op = self.styling.fill_opacity.at_time(start)
        self.styling.fill_opacity.set(s, end,
            lambda t, _s=s, _d=dur, _to=target_op: _to * easing((t - _s) / _d), stay=True)
        return self

    def pop_in(self, start: float = 0, duration=0.3, overshoot=1.2, change_existence=True, easing=easings.smooth):
        """Quick pop-in: scale from 0 to 1 with optional overshoot."""
        if change_existence:
            self._show_from(start)
        end = start + duration
        dur = duration
        if dur <= 0:
            return self
        self._ensure_scale_origin(start)
        s = start
        def _scale(t):
            p = easing((t - s) / dur)
            if p < 0.7:
                return p / 0.7 * overshoot
            return overshoot + (1 - overshoot) * ((p - 0.7) / 0.3)
        self.styling.scale_x.set(s, end, _scale, stay=True)
        self.styling.scale_y.set(s, end, _scale, stay=True)
        return self

    def pop_out(self, start: float = 0, duration=0.3, change_existence=True, easing=easings.smooth):
        """Quick pop-out: scale from 1 to 0."""
        end = start + duration
        dur = duration
        if dur <= 0:
            return self
        self._ensure_scale_origin(start)
        s = start
        self.styling.scale_x.set(s, end,
            lambda t, _s=s, _d=dur: 1 - easing((t - _s) / _d), stay=True)
        self.styling.scale_y.set(s, end,
            lambda t, _s=s, _d=dur: 1 - easing((t - _s) / _d), stay=True)
        if change_existence:
            self._hide_from(end)
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
        for xa, ya in self._shift_reals():
            ya.add(start, end, _dy)
        for c in self._shift_coors():
            c.add(start, end, lambda t, _f=_dy: (0, _f(t)))
        return self

    def slide_in(self, direction='left', start: float = 0, end: float = 1,
                  easing=easings.smooth, change_existence=True):
        """Slide in from outside the canvas edge.
        direction: 'left', 'right', 'up', 'down'."""
        dur = end - start
        if dur <= 0:
            return self
        if change_existence:
            self._show_from(start)
        bx, by, bw, bh = self.bbox(start)
        offsets = {
            'left': (-bx - bw, 0),     # slide from left edge
            'right': (1920 - bx, 0),    # slide from right edge
            'up': (0, -by - bh),        # slide from top
            'down': (0, 1080 - by),     # slide from bottom
        }
        ox, oy = offsets.get(direction, (0, 0))
        s = start
        def _shift(t, _s=s, _d=dur, _ox=ox, _oy=oy):
            p = 1 - easing((t - _s) / _d)
            return (_ox * p, _oy * p)
        for xa, ya in self._shift_reals():
            xa.add(s, end, lambda t, _f=_shift: _f(t)[0], stay=True)
            ya.add(s, end, lambda t, _f=_shift: _f(t)[1], stay=True)
        for c in self._shift_coors():
            c.add(s, end, _shift, stay=True)
        return self

    def slide_out(self, direction='right', start: float = 0, end: float = 1,
                   easing=easings.smooth, change_existence=True):
        """Slide out to outside the canvas edge.
        direction: 'left', 'right', 'up', 'down'."""
        dur = end - start
        if dur <= 0:
            return self
        bx, by, bw, bh = self.bbox(start)
        offsets = {
            'left': (-bx - bw, 0),
            'right': (1920 - bx, 0),
            'up': (0, -by - bh),
            'down': (0, 1080 - by),
        }
        ox, oy = offsets.get(direction, (0, 0))
        s = start
        def _shift(t, _s=s, _d=dur, _ox=ox, _oy=oy):
            p = easing((t - _s) / _d)
            return (_ox * p, _oy * p)
        for xa, ya in self._shift_reals():
            xa.add(s, end, lambda t, _f=_shift: _f(t)[0], stay=True)
            ya.add(s, end, lambda t, _f=_shift: _f(t)[1], stay=True)
        for c in self._shift_coors():
            c.add(s, end, _shift, stay=True)
        if change_existence:
            self._hide_from(end)
        return self

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

        def _sample_by_length(path, t):
            """Sample a path at time 0<=t<=1 based on arc length."""
            tot_length = path.length()
            length_to_draw = t * tot_length
            segs = []
            idx = 0
            while length_to_draw > 0 and idx < len(path):
                s = path[idx]
                l = s.length()
                if l <= length_to_draw:
                    segs.append(s)
                    length_to_draw -= l
                else:
                    segs.append(s.split(length_to_draw / l)[0])
                    length_to_draw = 0
                idx += 1
            return morphing.Path(*segs)

        _dur = end - start
        def f(t): return easing((t-start)/_dur) if _dur > 0 else 1

        from vectormation._shapes import Path
        res = Path('')
        res.d.set(start, end, lambda t: _sample_by_length(p, f(t)).d())
        # Inherit styling from the original object
        res.styling = deepcopy(self.styling)
        res.styling.fill_opacity.set_onward(0, 0)
        if change_existence:
            res._show_from(start)
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

    def zoom_in(self, start: float = 0, end: float = 1, start_scale=3,
                 change_existence=True, easing=easings.smooth):
        """Zoom in: start large and transparent, end at normal size and opacity."""
        dur = end - start
        if dur <= 0:
            return self
        if change_existence:
            self._show_from(start)
        self._ensure_scale_origin(start)
        s = start
        self.styling.scale_x.set(s, end,
            lambda t, _s=s, _d=dur, _ss=start_scale: _ss + (1 - _ss) * easing((t - _s) / _d), stay=True)
        self.styling.scale_y.set(s, end,
            lambda t, _s=s, _d=dur, _ss=start_scale: _ss + (1 - _ss) * easing((t - _s) / _d), stay=True)
        target_op = self.styling.fill_opacity.at_time(start)
        self.styling.fill_opacity.set(s, end,
            lambda t, _s=s, _d=dur, _to=target_op: _to * easing((t - _s) / _d), stay=True)
        return self

    def zoom_out(self, start: float = 0, end: float = 1, end_scale=3,
                  change_existence=True, easing=easings.smooth):
        """Zoom out: grow large while fading out."""
        dur = end - start
        if dur <= 0:
            return self
        self._ensure_scale_origin(start)
        s = start
        self.styling.scale_x.set(s, end,
            lambda t, _s=s, _d=dur, _es=end_scale: 1 + (_es - 1) * easing((t - _s) / _d), stay=True)
        self.styling.scale_y.set(s, end,
            lambda t, _s=s, _d=dur, _es=end_scale: 1 + (_es - 1) * easing((t - _s) / _d), stay=True)
        cur_op = self.styling.fill_opacity.at_time(start)
        self.styling.fill_opacity.set(s, end,
            lambda t, _s=s, _d=dur, _co=cur_op: _co * (1 - easing((t - _s) / _d)), stay=True)
        if change_existence:
            self._hide_from(end)
        return self

    def grow_from_point(self, px, py, start: float = 0, end: float = 1,
                         change_existence=True, easing=easings.smooth):
        """Grow from a specific point (px, py) using scale transform."""
        if change_existence:
            self._show_from(start)
        dur = end - start
        if dur <= 0:
            return self
        s = start
        self._ensure_scale_origin(start)
        self.styling._scale_origin = (px, py)
        scale = lambda t, _s=s, _d=dur: easing((t - _s) / _d)
        self.styling.scale_x.set(s, end, scale, stay=True)
        self.styling.scale_y.set(s, end, scale, stay=True)
        return self

    def shrink_to_point(self, px, py, start: float = 0, end: float = 1,
                         change_existence=True, easing=easings.smooth):
        """Shrink to a specific point (px, py) using scale transform. Opposite of grow_from_point."""
        if change_existence:
            self._hide_from(end)
        dur = end - start
        if dur <= 0:
            return self
        s = start
        self._ensure_scale_origin(start)
        self.styling._scale_origin = (px, py)
        scale = lambda t, _s=s, _d=dur: 1 - easing((t - _s) / _d)
        self.styling.scale_x.set(s, end, scale, stay=True)
        self.styling.scale_y.set(s, end, scale, stay=True)
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
        sx0 = self.styling.scale_x.at_time(start)
        sy0 = self.styling.scale_y.at_time(start)
        _s, _d, _sf, _p = start, max(dur, 1e-9), scale_factor, pulses
        def _scale_x(t, _s=_s, _d=_d, _sf=_sf, _p=_p, _sx0=sx0, _easing=easing):
            progress = _easing((t - _s) / _d)
            return _sx0 * (1 + (_sf - 1) * abs(math.sin(math.pi * _p * progress)))
        def _scale_y(t, _s=_s, _d=_d, _sf=_sf, _p=_p, _sy0=sy0, _easing=easing):
            progress = _easing((t - _s) / _d)
            return _sy0 * (1 + (_sf - 1) * abs(math.sin(math.pi * _p * progress)))
        self.styling.scale_x.set(start, end, _scale_x)
        self.styling.scale_y.set(start, end, _scale_y)
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
        for xa, _ in self._shift_reals():
            xa.add(s, end, dx)
        for c in self._shift_coors():
            c.add(s, end, lambda t, _f=dx: (_f(t), 0))
        return self

    def swing(self, start: float = 0, end: float = 1, amplitude=15, n_swings=3,
              cx=None, cy=None, easing=easings.there_and_back):
        """Pendulum-like oscillation around a pivot point.

        amplitude: max swing angle in degrees.
        n_swings: number of oscillation cycles.
        cx, cy: pivot point (default: top-center of bounding box).
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
            lambda t, _s=s, _d=dur, _a=amplitude, _n=n_swings, _cx=cx, _cy=cy: (_a * math.sin(2 * math.pi * _n * (t - _s) / _d) * easing((t - _s) / _d), _cx, _cy))
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
        for _, ya in self._shift_reals():
            ya.add(s, end, dy)
        for c in self._shift_coors():
            c.add(s, end, lambda t, _f=dy: (0, _f(t)))
        return self

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

    def spiral_in(self, start: float = 0, end: float = 1, n_turns=1, change_existence=True, easing=easings.smooth):
        """Spiral the object inward from a distance to its current position."""
        dur = end - start
        if dur <= 0:
            return self
        if change_existence:
            self._show_from(start)
        self._scale_anim(start, end, lambda p: p, easing, stay=True)
        cx, cy = self.styling._scale_origin
        s = start
        self.styling.rotation.set(s, end,
            lambda t, _s=s, _d=dur, _n=n_turns, _cx=cx, _cy=cy: (360 * _n * (1 - easing((t - _s) / _d)), _cx, _cy), stay=True)
        return self

    def spiral_out(self, start: float = 0, end: float = 1, n_turns=1, change_existence=True, easing=easings.smooth):
        """Spiral the object outward while shrinking to nothing."""
        dur = end - start
        if dur <= 0:
            return self
        self._scale_anim(start, end, lambda p: 1 - p, easing, stay=True)
        cx, cy = self.styling._scale_origin
        s = start
        self.styling.rotation.set(s, end,
            lambda t, _s=s, _d=dur, _n=n_turns, _cx=cx, _cy=cy: (360 * _n * easing((t - _s) / _d), _cx, _cy), stay=True)
        if change_existence:
            self._hide_from(end)
        return self

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

    def blink(self, start: float = 0, duration=0.3, easing=easings.smooth):
        """Quick opacity flash to 0 and back (like an eye blink)."""
        if duration <= 0:
            return self
        mid = start + duration / 2
        end = start + duration
        half = duration / 2
        self.styling.opacity.set(start, mid, lambda t, _s=start, _h=half: 1 - easing((t - _s) / _h))
        self.styling.opacity.set(mid, end, lambda t, _m=mid, _h=half: easing((t - _m) / _h))
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
        for xa, ya in self._shift_reals():
            xa.add(start, end, _dx)
            ya.add(start, end, _dy)
        for c in self._shift_coors():
            c.add(start, end, lambda t, _fdx=_dx, _fdy=_dy: (_fdx(t), _fdy(t)))
        return self

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
        for xa, ya in self._shift_reals():
            xa.add(start, end, _dx)
            ya.add(start, end, _dy)
        for c in self._shift_coors():
            c.add(start, end, lambda t, _fdx=_dx, _fdy=_dy: (_fdx(t), _fdy(t)))
        return self

    def orbit(self, cx, cy, radius=None, start: float = 0, end: float = 1,
              degrees=360, easing=easings.linear):
        """Orbit the object around (cx, cy).
        If radius is None, uses current distance from center."""
        bx, by, bw, bh = self.bbox(start)
        obj_cx, obj_cy = bx + bw / 2, by + bh / 2
        if radius is None:
            radius = math.sqrt((obj_cx - cx) ** 2 + (obj_cy - cy) ** 2)
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
        for xa, ya in self._shift_reals():
            ya.add(start, end, _dy)
        for c in self._shift_coors():
            c.add(start, end, lambda t, _f=_dy: (0, _f(t)))
        return self

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
        if axis in ('y', 'both'):
            for xa, ya in self._shift_reals():
                ya.add(start, end, _osc)
            for c in self._shift_coors():
                c.add(start, end, lambda t, _f=_osc: (0, _f(t)))
        if axis in ('x', 'both'):
            for xa, ya in self._shift_reals():
                xa.add(start, end, _osc)
            for c in self._shift_coors():
                c.add(start, end, lambda t, _f=_osc: (_f(t), 0))
        return self

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
            sx0 = self.styling.scale_x.at_time(start)
            sy0 = self.styling.scale_y.at_time(start)
            def _scale(t, _s=_s, _d=_d, _sx0=sx0, _easing=easing):
                p = _easing((t - _s) / _d)
                factor = 1 - 0.5 * math.sin(math.pi * p)
                return _sx0 * factor
            def _scale_y(t, _s=_s, _d=_d, _sy0=sy0, _easing=easing):
                p = _easing((t - _s) / _d)
                factor = 1 - 0.5 * math.sin(math.pi * p)
                return _sy0 * factor
            self.styling.scale_x.set(start, end, _scale, stay=False)
            self.styling.scale_y.set(start, end, _scale_y, stay=False)
        return self

    def heartbeat(self, start: float = 0, end: float = 1, beats=3,
                   scale_factor=1.3, easing=easings.smooth):
        """Rhythmic pulsing like a heartbeat — repeated grow/shrink cycles.
        beats: number of pulses. scale_factor: peak scale multiplier."""
        dur = end - start
        if dur <= 0 or beats <= 0:
            return self
        self._ensure_scale_origin(start)
        sx0 = self.styling.scale_x.at_time(start)
        sy0 = self.styling.scale_y.at_time(start)
        _s, _d, _b, _f = start, max(dur, 1e-9), beats, scale_factor
        def _hbx(t, _s=_s, _d=_d, _b=_b, _f=_f, _sx0=sx0, _easing=easing):
            p = _easing((t - _s) / _d)
            pulse = abs(math.sin(math.pi * _b * p))
            return _sx0 * (1 + (_f - 1) * pulse)
        def _hby(t, _s=_s, _d=_d, _b=_b, _f=_f, _sy0=sy0, _easing=easing):
            p = _easing((t - _s) / _d)
            pulse = abs(math.sin(math.pi * _b * p))
            return _sy0 * (1 + (_f - 1) * pulse)
        self.styling.scale_x.set(start, end, _hbx, stay=False)
        self.styling.scale_y.set(start, end, _hby, stay=False)
        return self

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

    def stamp(self, time: float = 0, opacity=0.3):
        """Leave a faded copy (ghost) at the current position. Returns the copy (add to canvas)."""
        from copy import deepcopy
        ghost = deepcopy(self)
        ghost.styling.fill_opacity.set_onward(time, opacity)
        ghost.styling.stroke_opacity.set_onward(time, opacity)
        # Freeze position: remove all animations after this time
        ghost.show.set_onward(time, True)
        return ghost

    def trail(self, start: float = 0, end: float = 1, num_copies=5, fade=True):
        """Leave fading ghost copies at intervals during [start, end].
        Returns a list of ghost VObjects (must be added to canvas separately)."""
        from copy import deepcopy
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

    def clone(self, count=1, dx=0, dy=0, start_time=0):
        """Create copies of this object with position offsets.
        Returns a VCollection of the clones (does NOT include the original)."""
        from copy import deepcopy
        clones = []
        for i in range(1, count + 1):
            c = deepcopy(self)
            c.shift(dx=dx * i, dy=dy * i, start_time=start_time)
            clones.append(c)
        return VCollection(*clones)

    def copy(self):
        """Return a deep copy of this object."""
        from copy import deepcopy
        return deepcopy(self)

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

    def set_opacity(self, value, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Set fill_opacity and stroke opacity together. Animated if end is given."""
        if end is None:
            self.styling.fill_opacity.set_onward(start, value)
            self.styling.opacity.set_onward(start, value)
        else:
            self.styling.fill_opacity.move_to(start, end, value, easing=easing)
            self.styling.opacity.move_to(start, end, value, easing=easing)
        return self

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

    def _delegate(self, method, *args, **kwargs):
        """Call method on each child object, return self."""
        for obj in self.objects:
            getattr(obj, method)(*args, **kwargs)
        return self

    @property
    def last_change(self):
        return max(max(obj.last_change for obj in self.objects), self.z.last_change, self.show.last_change)

    def __repr__(self):
        return f'{self.__class__.__name__}({len(self.objects)} objects)'

    def __iter__(self):
        return iter(self.objects)

    def __getitem__(self, idx):
        return self.objects[idx]

    def __len__(self):
        return len(self.objects)

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

    def partition(self, predicate):
        """Split into two VCollections: (matching, non_matching)."""
        yes, no = [], []
        for obj in self.objects:
            (yes if predicate(obj) else no).append(obj)
        return VCollection(*yes), VCollection(*no)

    def select(self, start=0, end=None):
        """Return a new VCollection with children at indices [start:end]."""
        return VCollection(*self.objects[start:end])

    def sort_objects(self, key=None, reverse=False, time=0):
        """Sort children in-place. Default key: x position at given time."""
        if key is None:
            key = lambda obj: obj.bbox(time)[0]
        self.objects.sort(key=key, reverse=reverse)
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

    def set_color_by_gradient(self, *colors, attr='fill', start=0):
        """Assign interpolated colors across children.
        colors: two or more hex color strings to interpolate between."""
        n = len(self.objects)
        if n < 2 or len(colors) < 2:
            if colors and n:
                for obj in self.objects:
                    obj.set_color(colors[0], start)
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
            for xa, ya in obj._shift_reals():
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
            dist = math.sqrt(dx * dx + dy * dy)
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

    def write(self, start: float = 0, end: float = 1, processing=10, max_stroke_width=2, change_existence=True):
        if not self.objects:
            return self
        spc = (end - start) / (len(self.objects) + processing)
        for i, obj in enumerate(self.objects):
            obj.write(start=start+spc*i, end=start+spc*(i+processing+1),
                      max_stroke_width=max_stroke_width, change_existence=change_existence)
        return self


VGroup = VCollection

