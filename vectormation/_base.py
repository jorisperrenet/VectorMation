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

    def to_edge(self, edge: str | tuple = DOWN, buff=DEFAULT_OBJECT_TO_EDGE_BUFF,
                start_time: float = 0, end_time: float | None = None, easing=easings.smooth):
        """Move object to a canvas edge. edge: UP/DOWN/LEFT/RIGHT or string."""
        if isinstance(edge, tuple):
            edge = _EDGE_NAMES.get(edge, 'bottom')
        x, y, w, h = self.bbox(start_time)
        cx, cy = x + w / 2, y + h / 2
        if edge == 'bottom':
            target_y = 1080 - buff - h / 2
            return self.center_to_pos(posx=cx, posy=target_y, start_time=start_time,
                                      end_time=end_time, easing=easing)
        elif edge == 'top':
            target_y = buff + h / 2
            return self.center_to_pos(posx=cx, posy=target_y, start_time=start_time,
                                      end_time=end_time, easing=easing)
        elif edge == 'left':
            target_x = buff + w / 2
            return self.center_to_pos(posx=target_x, posy=cy, start_time=start_time,
                                      end_time=end_time, easing=easing)
        elif edge == 'right':
            target_x = 1920 - buff - w / 2
            return self.center_to_pos(posx=target_x, posy=cy, start_time=start_time,
                                      end_time=end_time, easing=easing)
        return self

    def to_corner(self, corner: str | tuple = DR, buff=DEFAULT_OBJECT_TO_EDGE_BUFF,
                  start_time: float = 0, end_time: float | None = None, easing=easings.smooth):
        """Move object to a canvas corner. corner: UL/UR/DL/DR or string."""
        corner_map = {UL: 'top_left', UR: 'top_right', DL: 'bottom_left', DR: 'bottom_right'}
        if isinstance(corner, tuple):
            corner = corner_map.get(corner, 'bottom_right')
        _, _, w, h = self.bbox(start_time)
        tx = buff + w / 2 if 'left' in corner else 1920 - buff - w / 2
        ty = buff + h / 2 if 'top' in corner else 1080 - buff - h / 2
        return self.center_to_pos(posx=tx, posy=ty, start_time=start_time,
                                  end_time=end_time, easing=easing)

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
        self.styling.rotation.set_onward(start,
            lambda t: (degrees_per_second * (t - start) % 360, cx, cy))
        if end is not None:
            self.styling.rotation.set_onward(end, self.styling.rotation.at_time(end))
        return self

    def always_shift(self, vx, vy, start: float = 0, end: float | None = None):
        """Continuously shift the object by (vx, vy) pixels per second."""
        if end is None:
            for c in self._shift_coors():
                c.add_onward(start, lambda t: (vx * (t - start), vy * (t - start)))
            for xa, ya in self._shift_reals():
                xa.add_onward(start, lambda t: vx * (t - start))
                ya.add_onward(start, lambda t: vy * (t - start))
        else:
            for c in self._shift_coors():
                c.add_onward(start, lambda t: (vx * (min(t, end) - start), vy * (min(t, end) - start)))
            for xa, ya in self._shift_reals():
                xa.add_onward(start, lambda t: vx * (min(t, end) - start))
                ya.add_onward(start, lambda t: vy * (min(t, end) - start))
        return self

    def shift(self, dx=0, dy=0, start_time: float = 0, end_time: float | None = None, easing=easings.smooth):
        """Shift the object by (dx, dy), optionally animated over [start_time, end_time]."""
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
        start_deg = self.styling.rotation.at_time(start)[0]
        s, e = start, end
        self.styling.rotation.set(s, e,
            lambda t: (start_deg + (target_deg - start_deg) * easing((t - s) / (e - s)), cx, cy),
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

    def along_path(self, start: float, end: float, path_d, easing=easings.smooth):
        """Move the object's center along an SVG path string over [start, end]."""
        import svgpathtools
        parsed = svgpathtools.parse_path(path_d)
        total_length = parsed.length()
        xmin, ymin, w, h = self.bbox(start)
        cx0, cy0 = xmin + w / 2, ymin + h / 2
        point0 = parsed.point(0)
        off_x, off_y = cx0 - point0.real, cy0 - point0.imag
        s, e = start, end
        def pos(t):
            progress = max(0, min(1, easing((t - s) / (e - s))))
            pt = parsed.point(parsed.ilength(progress * total_length))  # type: ignore[operator]
            return (pt.real + off_x - cx0, pt.imag + off_y - cy0)
        for c in self._shift_coors():
            c.add(s, e, pos, stay=True)
        for xa, ya in self._shift_reals():
            xa.add(s, e, lambda t: pos(t)[0], stay=True)
            ya.add(s, e, lambda t: pos(t)[1], stay=True)
        return self

    def brect(self, time: float = 0, rx=0, ry=0, buff=SMALL_BUFF, follow=True):
        """Bounding rectangle with buff outward padding."""
        return _make_brect(self.bbox, time, rx, ry, buff, follow)

    def fadein(self, start: float = 0, end: float = 1, change_existence=True, easing=easings.smooth):
        """Animate opacity from 0 to current value over [start, end]."""
        if change_existence:
            self._show_from(start)
        end_val = self.styling.opacity.at_time(end)
        s, e = start, end
        self.styling.opacity.set(s, e, lambda t: end_val * easing((t-s)/(e-s)))
        return self

    def fadeout(self, start: float = 0, end: float = 1, change_existence=True, easing=easings.smooth):
        """Animate opacity from current value to 0 over [start, end]."""
        start_val = self.styling.opacity.at_time(start)
        s, e = start, end
        self.styling.opacity.set(s, e, lambda t: start_val * (1 - easing((t-s)/(e-s))))
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
        self.styling.fill_opacity.set(s, e, lambda t: end_val * easing((t-s)/(e-s)))
        self.styling.stroke_width.set(s, e, lambda t: max_stroke_width * stroke_easing((t-s)/(e-s)) + easing((t-s)/(e-s)) * sw)
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

        def f(t): return easing((t-start)/(end-start))

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
        self.styling.stroke_dashoffset.set(s, e,
            lambda t: total_length * (1 - easing((t - s) / (e - s))), stay=True)
        return self

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
        f = lambda t: scale_func(easing((t - s) / (e - s)))
        self.styling.scale_x.set(s, e, f, stay=stay)
        self.styling.scale_y.set(s, e, f, stay=stay)

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

    def indicate(self, start: float = 0, end: float = 1, scale_factor=1.2, easing=easings.there_and_back):
        """Briefly scale up and back to draw attention."""
        self._ensure_scale_origin(start)
        s, e = start, end
        scale = lambda t: 1 + (scale_factor - 1) * easing((t - s) / (e - s))
        self.styling.scale_x.set(s, e, scale)
        self.styling.scale_y.set(s, e, scale)
        return self

    def flash(self, start: float = 0, end: float = 1, color='#FFFF00', easing=easings.there_and_back):
        """Briefly flash a fill color and return to original."""
        original = self.styling.fill.time_func(start)
        assert isinstance(original, tuple)
        _, target_color = attributes.Color(0, color).parse(color)
        assert isinstance(target_color, tuple)
        s, e = start, end
        self.styling.fill.set(s, e,
            lambda t: tuple(o + (g - o) * easing((t - s) / (e - s))
                            for o, g in zip(original, target_color)))
        return self

    def pulse(self, start: float = 0, end: float = 1, scale_factor=1.5, easing=easings.there_and_back):
        """Scale up with a fade, then back. Useful for drawing attention to dots/points."""
        self._ensure_scale_origin(start)
        s, e = start, end
        scale = lambda t: 1 + (scale_factor - 1) * easing((t - s) / (e - s))
        opacity_f = lambda t: 1 - 0.4 * easing((t - s) / (e - s))
        self.styling.scale_x.set(s, e, scale)
        self.styling.scale_y.set(s, e, scale)
        self.styling.opacity.set(s, e, opacity_f)
        return self

    def spin(self, start: float = 0, end: float = 1, degrees=360, cx=None, cy=None, easing=easings.linear):
        """Continuous rotation by degrees over [start, end]."""
        return self._apply_rotation(start, end,
            self.styling.rotation.at_time(start)[0] + degrees, cx, cy, easing)

    def circumscribe(self, start: float = 0, end: float = 1, buff=SMALL_BUFF, easing=easings.smooth, **styling_kwargs):
        """Draw and remove a rectangle tracing around this object.
        Returns the rectangle Path (must be added to canvas)."""
        x, y, w, h = self.bbox(start)
        rx, ry = x - buff, y - buff
        rw, rh = w + 2 * buff, h + 2 * buff
        d = f'M{rx},{ry}l{rw},0l0,{rh}l-{rw},0z'
        style = {'stroke': '#FFFF00', 'fill_opacity': 0} | styling_kwargs
        from vectormation._shapes import Path
        rect = Path(d, creation=start, **style)
        rect.draw_along(start=start, end=(start + end) / 2, easing=easing, change_existence=True)
        rect.fadeout(start=(start + end) / 2, end=end, change_existence=True)
        return rect

    def wiggle(self, start: float = 0, end: float = 1, amplitude=12, n_wiggles=4, easing=easings.there_and_back):
        """Shake the object horizontally. amplitude is max displacement in pixels."""
        s, e = start, end
        def dx(t):
            progress = (t - s) / (e - s)
            return amplitude * math.sin(2 * math.pi * n_wiggles * progress) * easing(progress)
        for xa, _ in self._shift_reals():
            xa.add(s, e, dx)
        for c in self._shift_coors():
            c.add(s, e, lambda t: (dx(t), 0))
        return self

    def wave(self, start: float = 0, end: float = 1, amplitude=20, n_waves=2, direction: str | tuple = 'up', easing=easings.there_and_back):
        """Apply a wave distortion (vertical shift that travels across the object).
        direction: 'up' or 'down' or UP/DOWN constant."""
        if isinstance(direction, tuple):
            direction = 'up' if direction == UP else 'down'
        s, e = start, end
        sign = -1 if direction == 'up' else 1
        def dy(t):
            progress = (t - s) / (e - s)
            return sign * amplitude * math.sin(2 * math.pi * n_waves * progress) * easing(progress)
        for _, ya in self._shift_reals():
            ya.add(s, e, dy)
        for c in self._shift_coors():
            c.add(s, e, lambda t: (0, dy(t)))
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
        scale = lambda t: easing((t - s) / (e - s))
        self.styling.scale_x.set(s, e, scale, stay=True)
        self.styling.scale_y.set(s, e, scale, stay=True)
        return self

    def spiral_in(self, start: float = 0, end: float = 1, n_turns=1, change_existence=True, easing=easings.smooth):
        """Spiral the object inward from a distance to its current position."""
        if change_existence:
            self._show_from(start)
        self._scale_anim(start, end, lambda p: p, easing, stay=True)
        cx, cy = self.styling._scale_origin
        s, e = start, end
        self.styling.rotation.set(s, e,
            lambda t: (360 * n_turns * (1 - easing((t - s) / (e - s))), cx, cy), stay=True)
        return self

    def blink(self, start: float = 0, duration=0.3, easing=easings.smooth):
        """Quick opacity flash to 0 and back (like an eye blink)."""
        mid = start + duration / 2
        end = start + duration
        s1, m, s2, e2 = start, mid, mid, end
        self.styling.opacity.set(s1, m, lambda t: 1 - easing((t - s1) / (m - s1)))
        self.styling.opacity.set(s2, e2, lambda t: easing((t - s2) / (e2 - s2)))
        return self

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
        if isinstance(edge, tuple):
            edge = _EDGE_NAMES.get(edge, 'bottom')
        x, y, w, h = self.bbox(start_time)
        cx, cy = x + w / 2, y + h / 2
        if edge == 'bottom':
            return self.center_to_pos(posx=cx, posy=1080 - buff - h / 2, start_time=start_time, end_time=end_time, easing=easing)
        elif edge == 'top':
            return self.center_to_pos(posx=cx, posy=buff + h / 2, start_time=start_time, end_time=end_time, easing=easing)
        elif edge == 'left':
            return self.center_to_pos(posx=buff + w / 2, posy=cy, start_time=start_time, end_time=end_time, easing=easing)
        elif edge == 'right':
            return self.center_to_pos(posx=1920 - buff - w / 2, posy=cy, start_time=start_time, end_time=end_time, easing=easing)
        return self

    def to_corner(self, corner: str | tuple = DR, buff=DEFAULT_OBJECT_TO_EDGE_BUFF,
                  start_time: float = 0, end_time: float | None = None, easing=easings.smooth):
        """Move group to a canvas corner."""
        corner_map = {UL: 'top_left', UR: 'top_right', DL: 'bottom_left', DR: 'bottom_right'}
        if isinstance(corner, tuple):
            corner = corner_map.get(corner, 'bottom_right')
        _, _, w, h = self.bbox(start_time)
        tx = buff + w / 2 if 'left' in corner else 1920 - buff - w / 2
        ty = buff + h / 2 if 'top' in corner else 1080 - buff - h / 2
        return self.center_to_pos(posx=tx, posy=ty, start_time=start_time, end_time=end_time, easing=easing)

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

    def write(self, start: float = 0, end: float = 1, processing=10, max_stroke_width=2, change_existence=True):
        spc = (end - start) / (len(self.objects) + processing)
        for i, obj in enumerate(self.objects):
            obj.write(start=start+spc*i, end=start+spc*(i+processing+1),
                      max_stroke_width=max_stroke_width, change_existence=change_existence)


VGroup = VCollection

