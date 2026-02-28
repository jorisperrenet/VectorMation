"""Base classes (VObject, VCollection) and shared constants."""
import math
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any
from vectormation.pathbbox import path_bbox
from vectormation._constants import (
    CANVAS_WIDTH, CANVAS_HEIGHT,
    SMALL_BUFF, MED_SMALL_BUFF,
    UP, DOWN, LEFT, RIGHT,
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
style.Styling.mix_blend_mode: attributes.String  # type: ignore[reportInvalidTypeForm]

from vectormation._base_helpers import (
    _lerp, _ramp, _ramp_down, _lerp_point, _clip_reveal, _clip_hide,
    _norm_dir, _norm_edge, _coords_of, _set_attr, _parse_path, _path_prefix,
    _DIR_NAMES, _EDGE_NAMES, _EDGE_POINTS,
    _make_brect, _wrap_to_svg, _BBoxMethodsMixin,
)
from vectormation._base_effects import _VObjectEffectsMixin

class VObject(_BBoxMethodsMixin, _VObjectEffectsMixin, ABC):  # Vector Object
    """Base class for all vector objects with time-varying attributes."""

    @abstractmethod
    def __init__(self, creation: float = 0, z: float = 0):
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

    def _apply_shift_func(self, func, start, end, stay=True):
        """Apply a (dx, dy) shift function to all coordinate and real shift attributes."""
        for c in self._shift_coors():
            c.add(start, end, func, stay=stay)
        for xa, ya in self._shift_reals():
            xa.add(start, end, lambda t, _f=func: _f(t)[0], stay=stay)
            ya.add(start, end, lambda t, _f=func: _f(t)[1], stay=stay)

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

    def remove_updater(self, func):
        """Remove a specific updater by function reference."""
        self._updaters = [(f, s, e) for f, s, e in self._updaters if f is not func]
        return self

    def clear_updaters(self):
        """Remove all updaters. Returns self."""
        self._updaters = []
        return self

    # -- Generic implementations --

    @property
    def last_change(self):
        return max(a.last_change for a in [*self._extra_attrs(), self.styling, self.z, self.show])

    def is_on_screen(self, time=0):
        """Return True if the object's bounding box overlaps the visible canvas."""
        x, y, w, h = self.bbox(time)
        if w <= 0 or h <= 0:
            return False
        return x + w > 0 and x < CANVAS_WIDTH and y + h > 0 and y < CANVAS_HEIGHT

    def get_bounds(self, time=0):
        """Return a dict with bounding box properties."""
        bx, by, bw, bh = self.bbox(time)
        return {
            'x': bx, 'y': by, 'width': bw, 'height': bh,
            'left': bx, 'right': bx + bw, 'top': by, 'bottom': by + bh,
            'center': self.center(time),
        }

    def set_x(self, x, start: float = 0, end=None, easing=None):
        """Set the x-coordinate of the center (by shifting)."""
        dx = x - self.get_x(start)
        return self.shift(dx=dx, start=start, end=end, easing=easing or easings.smooth)

    def set_y(self, y, start: float = 0, end=None, easing=None):
        """Set the y-coordinate of the center (by shifting)."""
        dy = y - self.get_y(start)
        return self.shift(dy=dy, start=start, end=end, easing=easing or easings.smooth)

    def _set_dim(self, getter, scale_attr, value, start, end, stretch, easing):
        cur = getter(start)
        if cur == 0:
            return self
        factor = value / cur
        if stretch:
            self._ensure_scale_origin(start)
            scale_attr.set_onward(start, scale_attr.at_time(start) * factor)
        else:
            self.scale(factor, start=start, end=end, easing=easing or easings.smooth)
        return self

    def set_width(self, width, start: float = 0, end: float | None = None,
                  stretch=False, easing=None):
        """Scale so the bounding box has the given width. If stretch=True, only scale X."""
        return self._set_dim(self.get_width, self.styling.scale_x, width, start, end, stretch, easing)

    def set_height(self, height, start: float = 0, end: float | None = None,
                   stretch=False, easing=None):
        """Scale so the bounding box has the given height. If stretch=True, only scale Y."""
        return self._set_dim(self.get_height, self.styling.scale_y, height, start, end, stretch, easing)

    def get_z(self, time: float = 0):
        """Return the current z-order value."""
        return self.z.at_time(time)

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
                    cur.set(s, end, _lerp(s, dur, cur_val, saved_val, easing), stay=True)
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
        """Hide for *duration* seconds from *start*, then show."""
        self._show_from(start + duration)
        return self

    def _show_from(self, time):
        """Hide before time, show from time onward."""
        self.show.set_onward(0, False)
        self.show.set_onward(time, True)

    def _hide_from(self, time):
        """Hide from time onward."""
        self.show.set_onward(time, False)

    def is_visible(self, time=0):
        """Return True if this object is shown at the given time."""
        return bool(self.show.at_time(time))

    def show_during(self, *ranges):
        """Show this object only during the specified time ranges."""
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
        """Hide this object during the specified time ranges, visible otherwise."""
        if len(ranges) == 1 and isinstance(ranges[0], list):
            ranges = ranges[0]
        for start, end in ranges:
            self.show.set_onward(start, False)
            self.show.set_onward(end, True)
        return self

    def set_visible(self, visible, start=0):
        """Show or hide the object at a given time."""
        self.show.set_onward(start, 1 if visible else 0)
        return self

    def visibility_toggle(self, *times):
        """Toggle visibility at each given time (hidden before first, shown, hidden, ...)."""
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

    def always_rotate(self, start: float = 0, end: float | None = None, degrees_per_second: float = 90, cx: float | None = None, cy: float | None = None):
        """Continuously rotate the object around its center (or given cx, cy)."""
        if cx is None or cy is None:
            cx, cy = self.center(start)
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

    def shift(self, dx=0, dy=0, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Shift the object by (dx, dy), optionally animated over [start, end]."""
        if end is not None and end <= start:
            # Instant shift when duration is zero or negative
            end = None
        for c in self._shift_coors():
            if end is None:
                c.add_onward(start, (dx, dy))
            else:
                s, e = start, end
                c.add_onward(s, lambda t, _s=s, _e=e: (dx * easing((t-_s)/(_e-_s)), dy * easing((t-_s)/(_e-_s))), last_change=e)
        for xa, ya in self._shift_reals():
            if end is None:
                xa.add_onward(start, dx)
                ya.add_onward(start, dy)
            else:
                s, e = start, end
                xa.add_onward(s, _ramp(s, e - s, dx, easing), last_change=e)
                ya.add_onward(s, _ramp(s, e - s, dy, easing), last_change=e)
        return self

    def scale_by(self, start, end, factor, easing=easings.smooth):
        """Alias for :meth:`scale` with (start, end, factor) parameter order."""
        return self.scale(factor, start, end, easing=easing)

    def _apply_rotation(self, start: float, end: float, target_deg, cx, cy, easing):
        """Set rotation from current angle to target_deg around (cx, cy)."""
        if cx is None or cy is None:
            cx, cy = self.center(start)
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

    def rotate_by(self, start: float, end: float, degrees: float, cx: float | None = None, cy: float | None = None, easing=easings.smooth):
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

    def teleport(self, x: float, y: float, start: float = 0):
        """Instantly move object center to (x, y) at the given time (no animation)."""
        return self.center_to_pos(posx=x, posy=y, start=start)

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
        parsed, total_length = _parse_path(path_d)
        cx0, cy0 = self.center(start)
        point0 = parsed.point(0)
        off_x, off_y = cx0 - point0.real, cy0 - point0.imag
        s = start
        def pos(t):
            progress = max(0, min(1, easing((t - s) / dur)))
            pt = parsed.point(parsed.ilength(progress * total_length))  # type: ignore[operator]
            return (pt.real + off_x - cx0, pt.imag + off_y - cy0)
        self._apply_shift_func(pos, s, end)
        return self

    def animate_along_object(self, target, start=0, end=1, easing=None):
        """Move along the boundary/path of another VObject."""
        if easing is None:
            easing = easings.smooth
        path_d = target.path(start)
        return self.along_path(start, end, path_d, easing=easing)

    def path_arc(self, tx, ty, start: float = 0, end: float = 1,
                 angle=math.pi / 2, easing=easings.smooth):
        """Move the object's center to (tx, ty) along a circular arc."""
        dur = end - start
        if dur <= 0:
            return self
        sx, sy = self.center(start)
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
        self._apply_shift_func(_pos, start, end)
        return self

    def brect(self, time: float = 0, rx=0, ry=0, buff=SMALL_BUFF, follow=True):
        """Bounding rectangle with buff outward padding."""
        return _make_brect(self.bbox, time, rx, ry, buff, follow)

    def fadein(self, start: float = 0, end: float = 1, shift_dir=None, shift_amount=50,
               scale=None, change_existence=True, easing=easings.smooth):
        """Animate opacity from 0 to current value over [start, end].

        Args:
            shift_dir: optional direction tuple (e.g. UP, DOWN) to slide in from.
            scale: optional starting scale factor (e.g. 0.5 to grow from half size).
        """
        if change_existence:
            self._show_from(start)
        dur = end - start
        if dur <= 0:
            return self
        self.styling.opacity.set(start, end, _ramp(start, dur, self.styling.opacity.at_time(end), easing))
        if shift_dir is not None:
            dx, dy = shift_dir[0] * shift_amount, shift_dir[1] * shift_amount
            self.shift(dx=-dx, dy=-dy, start=start)
            self.shift(dx=dx, dy=dy, start=start, end=end, easing=easing)
        if scale is not None:
            self._ensure_scale_origin(start)
            sx0, sy0 = self._get_scale(start)
            self._set_scale_xy(start, end,
                _lerp(start, dur, sx0 * scale, sx0, easing),
                _lerp(start, dur, sy0 * scale, sy0, easing), stay=True)
        return self

    def fade_shift(self, dx=0, dy=0, start: float = 0, end: float = 1, easing=easings.smooth):
        """Fade out while shifting by (dx, dy) over [start, end]."""
        start_val = self.styling.opacity.at_time(start)
        dur = end - start
        if dur <= 0:
            self._hide_from(start)
            return self
        s, e = start, end
        self.styling.opacity.set(s, e, _ramp_down(s, dur, start_val, easing))
        self.shift(dx=dx, dy=dy, start=s, end=e, easing=easing)
        self._hide_from(e)
        return self

    def fadeout(self, start: float = 0, end: float = 1, shift_dir=None, shift_amount=50,
                scale=None, change_existence=True, easing=easings.smooth):
        """Animate opacity from current value to 0 over [start, end].

        Args:
            shift_dir: optional direction tuple (e.g. UP, DOWN) to slide out toward.
            scale: optional target scale factor (e.g. 0.5 to shrink while fading).
        """
        start_val = self.styling.opacity.at_time(start)
        dur = end - start
        if dur <= 0:
            if change_existence:
                self._hide_from(start)
            return self
        self.styling.opacity.set(start, end, _ramp_down(start, dur, start_val, easing))
        if shift_dir is not None:
            dx, dy = shift_dir[0] * shift_amount, shift_dir[1] * shift_amount
            self.shift(dx=dx, dy=dy, start=start, end=end, easing=easing)
        if scale is not None:
            self._ensure_scale_origin(start)
            sx0, sy0 = self._get_scale(start)
            self._set_scale_xy(start, end,
                _lerp(start, dur, sx0, sx0 * scale, easing),
                _lerp(start, dur, sy0, sy0 * scale, easing), stay=True)
        if change_existence:
            self._hide_from(end)
        return self

    def dissolve_out(self, start: float = 0, end: float = 1,
                     granularity=8, change_existence=True, seed=42):
        """Noisy/flickering opacity fade-out (dissolve effect)."""
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
        assert self.styling._scale_origin is not None
        cx, cy = self.styling._scale_origin
        s, op_base = start, self.styling.fill_opacity.at_time(start)
        if fade_in:
            rot_fn = lambda t, _s=s, _d=dur, _deg=degrees, _cx=cx, _cy=cy: (_deg * (1 - easing((t - _s) / _d)), _cx, _cy)
        else:
            rot_fn = lambda t, _s=s, _d=dur, _deg=degrees, _cx=cx, _cy=cy: (_deg * easing((t - _s) / _d), _cx, _cy)
        op_fn = (_ramp if fade_in else _ramp_down)(s, dur, op_base, easing)
        self.styling.rotation.set(s, end, rot_fn, stay=True)
        self.styling.fill_opacity.set(s, end, op_fn, stay=True)
        if change_existence and not fade_in:
            self._hide_from(end)
        return self

    def rotate_in(self, start: float = 0, end: float = 1, degrees=90,
                    change_existence=True, easing=easings.smooth):
        """Fade in while rotating from an offset angle to 0."""
        return self._rotate_fade_anim(start, end, degrees, True, change_existence, easing)

    def rotate_out(self, start: float = 0, end: float = 1, degrees=90,
                   change_existence=True, easing=easings.smooth):
        """Rotate away while fading out. Reverse of rotate_in."""
        return self._rotate_fade_anim(start, end, degrees, False, change_existence, easing)

    def _pop_anim(self, start, end, overshoot, pop_in, change_existence, easing):
        """Shared helper for pop_in / pop_out."""
        dur = end - start
        if dur <= 0:
            return self
        if change_existence and pop_in:
            self._show_from(start)
        self._ensure_scale_origin(start)
        s = start
        if pop_in:
            def scale_fn(t, _s=s, _d=dur, _v=overshoot, _e=easing):
                p = _e((t - _s) / _d)
                if p < 0.7:
                    return p / 0.7 * _v
                return _v + (1 - _v) * ((p - 0.7) / 0.3)
        else:
            scale_fn = _ramp_down(s, dur, 1, easing)
        self._set_scale_xy(s, end, scale_fn, stay=True)
        if change_existence and not pop_in:
            self._hide_from(end)
        return self

    def pop_in(self, start: float = 0, end: float = 0.3, overshoot=1.2, change_existence=True, easing=easings.smooth):
        """Quick pop-in: scale from 0 to 1 with optional overshoot."""
        return self._pop_anim(start, end, overshoot, True, change_existence, easing)

    def pop_out(self, start: float = 0, end: float = 0.3, change_existence=True, easing=easings.smooth):
        """Quick pop-out: scale from 1 to 0."""
        return self._pop_anim(start, end, 0, False, change_existence, easing)

    def _spin_anim(self, start, end, degrees, growing, change_existence, easing):
        dur = end - start
        if dur <= 0:
            if change_existence and not growing:
                self._hide_from(start)
            return self
        if change_existence and growing:
            self._show_from(start)
        self._ensure_scale_origin(start)
        s, _d = start, max(dur, 1e-9)
        cx, cy = self.center(start)
        ramp = _ramp if growing else _ramp_down
        self._set_scale_xy(s, end, ramp(s, _d, 1, easing), stay=True)
        rot_mult = (lambda p: 1 - p) if growing else (lambda p: p)
        self.styling.rotation.set(s, end,
            lambda t, _s=s, _d=_d, _deg=degrees, _cx=cx, _cy=cy, _e=easing, _m=rot_mult:
                (_deg * _m(_e((t - _s) / _d)), _cx, _cy), stay=True)
        if change_existence and not growing:
            self._hide_from(end)
        return self

    def spin_in(self, start: float = 0, end: float = 1, degrees: float = 360,
                change_existence=True, easing=easings.smooth):
        """Grow from nothing while spinning."""
        return self._spin_anim(start, end, degrees, True, change_existence, easing)

    def spin_out(self, start: float = 0, end: float = 1, degrees: float = 360,
                 change_existence=True, easing=easings.smooth):
        """Shrink to nothing while spinning. Reverse of spin_in."""
        return self._spin_anim(start, end, degrees, False, change_existence, easing)

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
            return _a * math.sin(p * math.tau)
        return self._apply_shift_effect(start, end, dy_func=_dy)

    def _slide_offsets(self, direction, start):
        bx, by, bw, bh = self.bbox(start)
        offsets = {
            'left': (-bx - bw, 0),
            'right': (CANVAS_WIDTH - bx, 0),
            'up': (0, -by - bh),
            'down': (0, CANVAS_HEIGHT - by),
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
            dx = _ramp_down(s, dur, ox, easing) if ox else None
            dy = _ramp_down(s, dur, oy, easing) if oy else None
        else:
            dx = _ramp(s, dur, ox, easing) if ox else None
            dy = _ramp(s, dur, oy, easing) if oy else None
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
            dx_func = _ramp_down(s, dur, dx, easing) if dx else None
            dy_func = _ramp_down(s, dur, dy, easing) if dy else None
        else:
            dx_func = _ramp(s, dur, dx, easing) if dx else None
            dy_func = _ramp(s, dur, dy, easing) if dy else None
        self._apply_shift_effect(start, end, dx_func, dy_func, stay=True)
        if fade_in:
            end_val = self.styling.opacity.at_time(end)
            self.styling.opacity.set(s, end, _ramp(s, dur, end_val, easing))
        else:
            start_val = self.styling.opacity.at_time(start)
            self.styling.opacity.set(s, end, _ramp_down(s, dur, start_val, easing))
            if change_existence:
                self._hide_from(end)
        return self

    def fade_slide_in(self, direction=None, distance=200, start: float = 0, end: float = 1,
                      change_existence=True, easing=easings.smooth):
        """Slide in from *direction* while fading in. Default direction: DOWN."""
        return self._fade_slide_anim(direction, distance, start, end, True, change_existence, easing)

    def fade_slide_out(self, direction=None, distance=200, start: float = 0, end: float = 1,
                       change_existence=True, easing=easings.smooth):
        """Slide away in *direction* while fading out. Reverse of fade_slide_in."""
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
        self.styling.fill_opacity.set(s, e, _ramp(s, dur, end_val, easing))
        self.styling.stroke_width.set(s, e, lambda t, _s=s, _d=dur, _msw=max_stroke_width, _sw=sw: _msw * stroke_easing((t-_s)/_d) + easing((t-_s)/_d) * _sw)
        return self

    def _create_path_anim(self, start, end, reverse, change_existence, easing):
        """Shared helper for create/uncreate path drawing animations."""
        if not reverse and change_existence:
            self._show_from(end)
        if reverse and change_existence:
            self.show.set_onward(end, False)

        p = morphing.Path(self.path(start))
        _dur = end - start
        def f(t): return easing((t - start) / _dur) if _dur > 0 else 1

        from vectormation._shapes import Path
        res = Path('')
        if reverse:
            res.d.set(start, end, lambda t: _path_prefix(p, 1 - f(t)).d())
        else:
            res.d.set(start, end, lambda t: _path_prefix(p, f(t)).d())
        res.styling = deepcopy(self.styling)
        res.styling.fill_opacity.set_onward(0, 0)
        if change_existence:
            res._show_from(start)
            if reverse:
                res.show.set_onward(end, False)
        return res

    def create(self, start: float = 0, end: float = 1, change_existence=True, easing=easings.smooth):
        """Animate drawing the path of this object from start to end."""
        return self._create_path_anim(start, end, False, change_existence, easing)

    def uncreate(self, start: float = 0, end: float = 1, change_existence=True, easing=easings.smooth):
        """Reverse of create — wipes the path from end to start.
        The original object is hidden at `end`."""
        return self._create_path_anim(start, end, True, change_existence, easing)

    def draw_along(self, start: float = 0, end: float = 1, easing=easings.smooth, change_existence=True):
        """Animate drawing the stroke of this object using stroke-dashoffset."""
        _, total_length = _parse_path(self.path(start))

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
            _ramp_down(s, dur, total_length, easing), stay=True)
        return self

    def show_passing_flash(self, start: float = 0, end: float = 1, flash_width=0.15,
                           color='#FFFF00', stroke_width=6, easing=easings.linear):
        """A bright flash that travels along this object's path."""
        _, total = _parse_path(self.path(start))
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
            _ramp_down(s, dur, total, easing), stay=True)
        return flash

    def _ensure_scale_origin(self, time):
        """Set _scale_origin to the object's center if not already set."""
        if self.styling._scale_origin is None:
            self.styling._scale_origin = self.center(time)

    def _get_scale(self, time):
        """Return (scale_x, scale_y) at the given time."""
        return self.styling.scale_x.at_time(time), self.styling.scale_y.at_time(time)

    def _init_scale_anim(self, start):
        """Ensure scale origin is set and return (scale_x, scale_y) at start."""
        self._ensure_scale_origin(start)
        return self._get_scale(start)

    def _set_scale_xy(self, s, e, fx, fy=None, stay=False):
        """Set both scale_x and scale_y.  If *fy* is None, uses *fx* for both."""
        self.styling.scale_x.set(s, e, fx, stay=stay)
        self.styling.scale_y.set(s, e, fy if fy is not None else fx, stay=stay)

    def _scale_effect(self, start, end, make_fns, *, force_origin=False):
        """Apply a transient scale effect.  *make_fns(sx0, sy0, s, d)* returns *(fx, fy)*."""
        dur = end - start
        if dur <= 0:
            return self
        if force_origin:
            self.styling._scale_origin = self.center(start)
        sx0, sy0 = self._init_scale_anim(start)
        fx, fy = make_fns(sx0, sy0, start, max(dur, 1e-9))
        self._set_scale_xy(start, end, fx, fy)
        return self

    def scale_to(self, start: float, end: float, factor, easing=easings.smooth):
        """Animate to an absolute scale factor (e.g. factor=2 → double original size)."""
        self._ensure_scale_origin(start)
        self.styling.scale_x.move_to(start, end, factor, easing=easing)
        self.styling.scale_y.move_to(start, end, factor, easing=easing)
        return self

    def scale_to_size(self, width=None, height=None, start: float = 0,
                      end: float | None = None, easing=easings.smooth):
        """Scale to fit a target pixel width and/or height. Both given = independent axes."""
        _, _, cur_w, cur_h = self.bbox(start)
        self._ensure_scale_origin(start)
        if width is not None and height is not None:
            fx = width / cur_w if cur_w else 1
            fy = height / cur_h if cur_h else 1
        elif width is not None:
            fx = fy = width / cur_w if cur_w else 1
        elif height is not None:
            fx = fy = height / cur_h if cur_h else 1
        else:
            return self
        sx, sy = self.styling.scale_x, self.styling.scale_y
        for attr, f in [(sx, fx), (sy, fy)]:
            _set_attr(attr, start, end, attr.at_time(start) * f, easing)
        return self

    def rotate_to(self, start: float, end: float, degrees: float, cx: float | None = None, cy: float | None = None, easing=easings.smooth):
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
        """Smoothly interpolate fill (or stroke) color to *color* over [start, end]."""
        style_attr = getattr(self.styling, attr)
        target = attributes.Color(0, color)
        interp = style_attr.interpolate(target, start, end, easing=easing)
        setattr(self.styling, attr, interp)
        return self

    def color_wave(self, start: float = 0, end: float = 1,
                    wave_color='#58C4DD', attr='fill', width=0.3, cycles=1):
        """Sweep *wave_color* across the current base color over [start, end]."""
        dur = end - start
        if dur <= 0:
            return self
        style_attr = getattr(self.styling, attr)
        if not isinstance(style_attr, attributes.Color):
            return self
        base_rgb = style_attr.time_func(start)
        from vectormation.colors import _hex_to_rgb
        wave_rgb = _hex_to_rgb(wave_color)
        _s, _d, _w, _cyc = start, max(dur, 1e-9), max(width, 0.01), cycles
        _br, _wr = base_rgb, wave_rgb

        def _sweep_rgb(t, _s=_s, _d=_d, _w=_w, _cyc=_cyc,
                       _br=_br, _wr=_wr):
            # sweep position in [0, 1], repeating for multiple cycles
            p = (((t - _s) / _d) * _cyc) % 1.0
            # Symmetric distance: 1 at edges of sweep, 0 at center
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
        """Animate through a sequence of *colors* over [start, end] via RGB interpolation."""
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
            r0, g0, b0 = parsed[i]
            r1, g1, b1 = parsed[i + 1]
            _t0, _d = t0, seg_dur
            style_attr.set(t0, t1,
                lambda t, _s=_t0, _dd=_d,
                       _r0=r0, _g0=g0, _b0=b0,
                       _r1=r1, _g1=g1, _b1=b1: (
                    _r0 + (_r1 - _r0) * ((t - _s) / _dd),
                    _g0 + (_g1 - _g0) * ((t - _s) / _dd),
                    _b0 + (_b1 - _b0) * ((t - _s) / _dd)),
                stay=(i == n_segs - 1))
        return self

    def next_to(self, other, direction: str | tuple = 'right', buff=SMALL_BUFF, start: float = 0, end: float | None = None, easing=None):
        """Position this object next to another."""
        direction = _norm_dir(direction)
        mx, my, mw, mh = self.bbox(start)
        ox, oy, ow, oh = other.bbox(start)
        mcx, mcy = mx + mw/2, my + mh/2
        ocx, ocy = ox + ow/2, oy + oh/2
        targets = {
            'right': (ox + ow + buff + mw/2, ocy),
            'left':  (ox - buff - mw/2, ocy),
            'down':  (ocx, oy + oh + buff + mh/2),
            'up':    (ocx, oy - buff - mh/2),
        }
        tx, ty = targets[direction]
        if end is not None:
            kw = {'start': start, 'end': end}
            if easing is not None:
                kw['easing'] = easing
            self.center_to_pos(tx, ty, **kw)
        else:
            self.shift(dx=tx - mcx, dy=ty - mcy, start=start)
        return self

    def attach_to(self, other, direction=None, buff=None, start=0, end=None):
        """Continuously position self next to *other* via an updater."""
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
            ocx, ocy = other.center(t)
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

    def always_next_to(self, other, direction=RIGHT, buff=SMALL_BUFF, start=0, end=None):
        """Updater-based ``next_to`` that tracks *other* each frame."""
        _dir = direction
        _buff = buff
        def _update(obj, t):
            obj.next_to(other, _dir, _buff, start=t)
        self.add_updater(_update, start=start, end=end)
        return self

    def set_color_if(self, predicate, color, start=0, end=None):
        """Set fill to *color* when ``predicate(t)`` is True, revert otherwise."""
        _orig_rgb = self.styling.fill.time_func(start)
        _new_color = attributes.Color(0, color)
        _new_rgb = _new_color.time_func(0)
        def _update(obj, t):
            if predicate(t):
                obj.styling.fill.set_onward(t, lambda _, _c=_new_rgb: _c)
            else:
                obj.styling.fill.set_onward(t, lambda _, _c=_orig_rgb: _c)
        self.add_updater(_update, start=start, end=end)
        return self

    def apply_pointwise(self, func, time=0):
        """Apply ``func(x, y) -> (x', y')`` to the object's center position."""
        cx, cy = self.center(time)
        nx, ny = func(cx, cy)
        self.move_to(nx, ny, start=time)
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
        self._set_scale_xy(s, e, f, stay=stay)
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

    def elastic_in(self, start: float = 0, end: float = 1, change_existence=True,
                   easing=easings.ease_out_elastic):
        """Scale in with elastic bounce (overshoot then settle)."""
        return self._scale_in_out(start, end, True, change_existence, easing)

    def elastic_out(self, start: float = 0, end: float = 1, change_existence=True,
                    easing=easings.ease_in_elastic):
        """Scale out with elastic bounce."""
        return self._scale_in_out(start, end, False, change_existence, easing)

    def bounce_in(self, start: float = 0, end: float = 1, change_existence=True,
                  easing=easings.ease_out_bounce):
        """Scale in from 0 with bounce easing."""
        return self._scale_in_out(start, end, True, change_existence, easing)

    def bounce_out(self, start: float = 0, end: float = 1, change_existence=True,
                   easing=easings.ease_in_bounce):
        """Scale out to 0 with bounce easing."""
        return self._scale_in_out(start, end, False, change_existence, easing)

    def _zoom_anim(self, start, end, from_scale, to_scale, fade_in, change_existence, easing):
        """Shared helper for zoom_in / zoom_out."""
        dur = end - start
        if dur <= 0:
            return self
        if change_existence and fade_in:
            self._show_from(start)
        self._ensure_scale_origin(start)
        s = start
        scale_fn = _lerp(s, dur, from_scale, to_scale, easing)
        self._set_scale_xy(s, end, scale_fn, stay=True)
        base_op = self.styling.fill_opacity.at_time(start)
        ramp_fn = _ramp if fade_in else _ramp_down
        self.styling.fill_opacity.set(s, end, ramp_fn(s, dur, base_op, easing), stay=True)
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
        self._set_scale_xy(s, end, scale, stay=True)
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
        """Appear from *source*'s center position, sliding and fading into place."""
        if change_existence:
            self._show_from(start)
        dur = end - start
        if dur <= 0:
            return self
        src_x, src_y = _coords_of(source, start)
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
            xa.set(s, end, _lerp(s, d, ox_val + off_x, ox_val, _easing), stay=True)
            ya.set(s, end, _lerp(s, d, oy_val + off_y, oy_val, _easing), stay=True)
        # Fade in opacity
        end_op = self.styling.opacity.at_time(end)
        self.styling.opacity.set(s, end, _ramp(s, d, end_op, _easing), stay=True)
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

    def skew(self, start: float = 0, end: float = 0.5, x_degrees: float = 0, y_degrees: float = 0, easing=easings.smooth):
        """Animate skew (shear) along X and/or Y axes."""
        dur = end - start
        if dur <= 0:
            return self
        s = start
        if x_degrees:
            self.styling.skew_x.set(s, end, _ramp(s, dur, x_degrees, easing), stay=True)
        if y_degrees:
            self.styling.skew_y.set(s, end, _ramp(s, dur, y_degrees, easing), stay=True)
        return self

    def indicate(self, start: float = 0, end: float = 1, scale_factor=1.2, easing=easings.there_and_back):
        """Briefly scale up and back to draw attention."""
        dur = end - start
        if dur <= 0:
            return self
        self._ensure_scale_origin(start)
        scale = _lerp(start, dur, 1, scale_factor, easing)
        self._set_scale_xy(start, end, scale)
        return self

    def flash(self, start: float = 0, end: float = 1, color='#FFFF00', easing=easings.there_and_back):
        """Briefly flash a fill color and return to original."""
        original = self.styling.fill.time_func(start)
        if not isinstance(original, tuple):
            return self
        _, target_color = attributes.Color(0, color).parse(color)
        if not isinstance(target_color, tuple):
            return self
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
        scale = _lerp(start, dur, 1, scale_factor, easing)
        opacity_f = _lerp(start, dur, 1, 0.6, easing)
        self._set_scale_xy(start, end, scale)
        self.styling.opacity.set(start, end, opacity_f)
        return self

    def pulsate(self, start: float = 0, end: float = 1, scale_factor=1.3,
                 n_pulses=3, easing=easings.smooth):
        """Repeated grow/shrink pulsation over [start, end]."""
        dur = end - start
        if dur <= 0:
            return self
        sx0, sy0 = self._init_scale_anim(start)
        _s, _d, _sf, _p = start, max(dur, 1e-9), scale_factor, n_pulses
        def _make_pulse(s0):
            return lambda t, _s=_s, _d=_d, _sf=_sf, _p=_p, _s0=s0, _e=easing: \
                _s0 * (1 + (_sf - 1) * abs(math.sin(math.pi * _p * _e((t - _s) / _d))))
        self._set_scale_xy(start, end, _make_pulse(sx0), _make_pulse(sy0))
        return self

    def pulse_scale(self, start: float = 0, end: float = 1, count=2, amplitude=0.15, easing=easings.smooth):
        """Oscillate scale by *amplitude* for *count* cycles over [start, end]."""
        dur = end - start
        if dur <= 0:
            return self
        sx0, sy0 = self._init_scale_anim(start)
        _s, _d, _amp, _cnt = start, max(dur, 1e-9), amplitude, count
        def _make_pulse_scale(base):
            return lambda t, _s=_s, _d=_d, _amp=_amp, _cnt=_cnt, _b=base, _e=easing: \
                _b * (1 + _amp * math.sin(math.tau * _cnt * _e((t - _s) / _d)))
        self._set_scale_xy(start, end, _make_pulse_scale(sx0), _make_pulse_scale(sy0))
        return self

    def ripple_scale(self, start: float = 0, end: float = 1, n_ripples=3, max_factor=1.3, easing=easings.smooth):
        """Produce multiple decaying scale pulses."""
        sx0, sy0 = self._init_scale_anim(start)
        s, e, dur = start, end, end - start
        if dur <= 0:
            return self
        def _ripple(t, _s=s, _d=dur, _n=n_ripples, _m=max_factor, _e=easing, _sx0=sx0):
            p = _e((t - _s) / _d)
            decay = 1 - p  # amplitude decreases over time
            wave = math.sin(p * _n * math.tau)
            factor = 1 + (_m - 1) * decay * wave
            return _sx0 * factor
        self.styling.scale_x.set(s, e, _ripple, stay=True)
        self.styling.scale_y.set(s, e, lambda t, _f=_ripple, _r=sy0/sx0 if sx0 else 1: _f(t) * _r, stay=True)
        return self

    def flash_scale(self, factor=1.5, start: float = 0, end: float = 1, easing=easings.smooth):
        """Scale up to *factor* at the midpoint, then back to original size."""
        dur = end - start
        if dur <= 0:
            return self
        sx0, sy0 = self._init_scale_anim(start)
        _s, _d, _f = start, max(dur, 1e-9), factor
        def _make_flash(base):
            return lambda t, _s=_s, _d=_d, _f=_f, _b=base, _e=easing: \
                _b * (1 + (_f - 1) * math.sin(math.pi * _e((t - _s) / _d)))
        self._set_scale_xy(start, end, _make_flash(sx0), _make_flash(sy0))
        return self

    def hover_scale(self, factor=1.2, start: float = 0, end: float = 1):
        """Hold scale at *factor* during [start, end], then snap back."""
        sx0, sy0 = self._init_scale_anim(start)
        self.styling.scale_x.set_onward(start, sx0 * factor)
        self.styling.scale_y.set_onward(start, sy0 * factor)
        self.styling.scale_x.set_onward(end, sx0)
        self.styling.scale_y.set_onward(end, sy0)
        return self

    def spin(self, start: float = 0, end: float = 1, degrees: float = 360, cx: float | None = None, cy: float | None = None, easing=easings.linear):
        """Continuous rotation by degrees over [start, end]."""
        return self._apply_rotation(start, end,
            self.styling.rotation.at_time(start)[0] + degrees, cx, cy, easing)

    def emphasize(self, start: float = 0, end: float = 0.8, color='#FFFF00',
                    scale_factor=1.15, easing=easings.there_and_back):
        """Combine a brief scale pulse with a color flash for emphasis."""
        self.indicate(start, end, scale_factor=scale_factor, easing=easing)
        self.flash(start, end, color=color, easing=easing)
        return self

    def emphasize_scale(self, start: float = 0, end: float = 1,
                        scale_factor: float = 1.2, easing=easings.there_and_back):
        """Single symmetric scale pulse for emphasis (both axes, returns to normal)."""
        dur = end - start
        if dur <= 0:
            return self
        self._ensure_scale_origin(start)
        s = start
        for attr in (self.styling.scale_x, self.styling.scale_y):
            base = attr.at_time(start)
            _sf = scale_factor
            attr.set(s, end, _lerp(s, dur, base, base * _sf, easing))
        return self

    def glow(self, start: float = 0, end: float = 1, color='#FFD700', radius=10):
        """Add an animated glow effect (stroke pulses outward then fades)."""
        dur = end - start
        if dur <= 0:
            return self
        s, d = start, max(dur, 1e-9)
        orig_sw = self.styling.stroke_width.at_time(start)
        _, glow_rgb = attributes.Color(0, color).parse(color)
        self.styling.stroke.set(s, end,
            lambda _, _rgb=glow_rgb: _rgb, stay=False)
        self.styling.stroke_width.set(s, end,
            _lerp(s, d, orig_sw, orig_sw + radius, easings.there_and_back), stay=False)
        self.styling.stroke_opacity.set(s, end,
            _ramp(s, d, 0.7, easings.there_and_back), stay=False)
        return self

    def drop_shadow(self, color='#000000', dx=4, dy=4, blur=6, start=0):
        """Apply an SVG feDropShadow filter, visible from *start* onward."""
        fid = f'ds{id(self)}'
        fdef = (f"<filter id='{fid}' x='-50%' y='-50%' width='200%' height='200%'>"
                f"<feDropShadow dx='{dx}' dy='{dy}' stdDeviation='{blur}' "
                f"flood-color='{color}' flood-opacity='0.5'/></filter>")
        _wrap_to_svg(self, lambda inner, t, _f=fid, _d=fdef:
                     f"<g filter='url(#{_f})'><defs>{_d}</defs>{inner}</g>", start)
        return self

    def pulse_outline(self, start: float = 0, end: float = 1, color='#FFFF00',
                      max_width=8, cycles=2, easing=easings.smooth):
        """Animate the stroke pulsing between current width and *max_width*."""
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
            return amplitude * math.sin(math.tau * n_wiggles * progress) * easing(progress)
        return self._apply_shift_effect(start, end, dx_func=dx)

    def swing(self, start: float = 0, end: float = 1, amplitude=15,
              cx=None, cy=None, easing=easings.smooth):
        """Pendulum-like rotation oscillation that decays to rest."""
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
                _a * math.sin(math.tau * _ease((t - _s) / _d)) * (1 - _ease((t - _s) / _d)),
                _cx, _cy))
        return self

    def wave(self, start: float = 0, end: float = 1, amplitude=20, n_waves=2, direction: str | tuple = 'up', easing=easings.there_and_back):
        """Apply a wave distortion (vertical shift that travels across the object).
        direction: 'up' or 'down' or UP/DOWN constant."""
        dur = end - start
        if dur <= 0:
            return self
        direction = _norm_dir(direction, 'down')
        s = start
        sign = -1 if direction == 'up' else 1
        def dy(t):
            progress = (t - s) / dur
            return sign * amplitude * math.sin(math.tau * n_waves * progress) * easing(progress)
        return self._apply_shift_effect(start, end, dy_func=dy)

    def _scale_anchor_anim(self, origin, start, end, grow, change_existence, easing):
        """Shared helper for grow/shrink from edge, corner, or point."""
        if grow and change_existence:
            self._show_from(start)
        self.styling._scale_origin = origin
        dur = end - start
        if dur <= 0:
            return self
        scale = _ramp(start, dur, 1, easing) if grow else _ramp_down(start, dur, 1, easing)
        self._set_scale_xy(start, end, scale, stay=True)
        if not grow and change_existence:
            self._hide_from(end)
        return self

    def _edge_origin(self, edge, time):
        """Return the scale origin for a named edge."""
        edge = _norm_edge(edge)
        bx, by, bw, bh = self.bbox(time)
        cx, cy = bx + bw / 2, by + bh / 2
        origins = {
            'bottom': (cx, by + bh),
            'top':    (cx, by),
            'left':   (bx, cy),
            'right':  (bx + bw, cy),
        }
        return origins[edge]

    def grow_from_edge(self, edge: str | tuple = 'bottom', start: float = 0, end: float = 1, change_existence=True, easing=easings.smooth):
        """Grow the object from a specific edge (bottom, top, left, right)."""
        return self._scale_anchor_anim(self._edge_origin(edge, start), start, end, True, change_existence, easing)

    def shrink_to_edge(self, edge: str | tuple = 'bottom', start: float = 0, end: float = 1, change_existence=True, easing=easings.smooth):
        """Shrink the object to zero at a specific edge. Reverse of grow_from_edge."""
        return self._scale_anchor_anim(self._edge_origin(edge, start), start, end, False, change_existence, easing)

    def _corner_point(self, corner, time):
        """Return the SVG pixel coordinate for a bbox corner direction."""
        from vectormation._constants import DL
        corner = corner or DL
        x, y, w, h = self.bbox(time)
        return (x if corner[0] <= 0 else x + w,
                y if corner[1] <= 0 else y + h)

    def grow_from_corner(self, start=0, end=1, corner=None, change_existence=True, easing=easings.smooth):
        """Grow from zero size anchored at a corner."""
        return self._scale_anchor_anim(self._corner_point(corner, start), start, end, True, change_existence, easing)

    def shrink_to_corner(self, start=0, end=1, corner=None, change_existence=True, easing=easings.smooth):
        """Shrink to zero size anchored at a corner. Reverse of grow_from_corner."""
        return self._scale_anchor_anim(self._corner_point(corner, start), start, end, False, change_existence, easing)

    def _spiral_anim(self, start, end, n_turns, spiral_in, change_existence, easing):
        """Shared helper for spiral_in / spiral_out."""
        dur = end - start
        if dur <= 0:
            return self
        if change_existence and spiral_in:
            self._show_from(start)
        self._scale_anim(start, end, (lambda p: p) if spiral_in else (lambda p: 1 - p), easing, stay=True)
        assert self.styling._scale_origin is not None
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
        """Animate drawing the stroke first, then fading in the fill."""
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
                _ramp(s2, dur2, target_fo, easing), stay=True)
        else:
            self.styling.fill_opacity.set_onward(mid, target_fo)
        return self

    def _phase_anim(self, start, end, in_method, in_ratio, hold_ratio, easing):
        """Run in_method then fadeout with a hold phase between."""
        dur = end - start
        if dur <= 0:
            return self
        total = in_ratio + hold_ratio + (1 - in_ratio - hold_ratio)
        t_in = start + dur * (in_ratio / total)
        t_hold = t_in + dur * (hold_ratio / total)
        in_method(start=start, end=t_in, change_existence=True, easing=easing)
        self.fadeout(start=t_hold, end=end, change_existence=True, easing=easing)
        return self

    def create_then_fadeout(self, start: float = 0, end: float = 2,
                            create_ratio: float = 0.4, hold_ratio: float = 0.2,
                            easing=easings.smooth):
        """Create the object (stroke draw), hold, then fade out."""
        return self._phase_anim(start, end, self.create, create_ratio, hold_ratio, easing)

    def write_then_fadeout(self, start: float = 0, end: float = 2,
                           write_ratio: float = 0.4, hold_ratio: float = 0.2,
                           easing=easings.smooth):
        """Write the object, hold, then fade out."""
        return self._phase_anim(start, end, self.write, write_ratio, hold_ratio, easing)

    def fadein_then_fadeout(self, start: float = 0, end: float = 2,
                            in_ratio: float = 0.3, hold_ratio: float = 0.4,
                            easing=easings.smooth):
        """Fade in, hold, then fade out."""
        return self._phase_anim(start, end, self.fadein, in_ratio, hold_ratio, easing)

    def blink(self, start: float = 0, end: float | None = None, count: int = 1,
              duration: float = 0.3, easing=easings.smooth, num_blinks: int | None = None):
        """Flash opacity on/off."""
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
                    _t0, _t_mid, _ramp_down(_t0, _h, 1, easing))
                self.styling.opacity.set(
                    _t_mid, t1, _ramp(_t_mid, _h, 1, easing),
                    stay=True)
            return self
        # Legacy single-blink mode: flash to 0 and back over *duration*
        if duration <= 0:
            return self
        mid = start + duration / 2
        blink_end = start + duration
        half = duration / 2
        self.styling.opacity.set(start, mid, _ramp_down(start, half, 1, easing))
        self.styling.opacity.set(mid, blink_end, _ramp(mid, half, 1, easing))
        return self

    def blink_opacity(self, start: float = 0, end: float = 1, frequency: float = 2,
                       min_opacity: float = 0.0, max_opacity: float = 1.0,
                       easing=easings.smooth):
        """Oscillate opacity between *min_opacity* and *max_opacity* at *frequency* Hz."""
        dur = end - start
        if dur <= 0 or frequency <= 0:
            return self
        _s, _d = start, dur
        _min, _max = min_opacity, max_opacity
        _freq, _e = frequency, easing

        def _opacity(t, _s=_s, _d=_d, _min=_min, _max=_max, _freq=_freq, _e=_e):
            progress = _e((t - _s) / _d)
            # sine wave: 0..1..0..-1..0 per cycle; we map to 0..1 range
            wave = 0.5 * (1 - math.cos(math.tau * _freq * progress))
            return _min + (_max - _min) * wave

        self.styling.opacity.set(start, end, _opacity, stay=True)
        return self

    def shimmer(self, start: float = 0, end: float = 1, passes=2, easing=easings.smooth):
        """Create a sweep highlight effect by oscillating opacity."""
        dur = end - start
        if dur <= 0:
            return self
        _s, _d, _p = start, max(dur, 1e-9), passes

        def _shimmer(t, _s=_s, _d=_d, _p=_p):
            progress = easing((t - _s) / _d)
            # Raised cosine wave: oscillates between 0.0 and 1.0
            wave = 0.5 * (1 + math.cos(math.tau * _p * progress))
            # Map to opacity range 0.3..1.0 for a visible shimmer effect
            return 0.3 + 0.7 * wave

        self.styling.opacity.set(start, end, _shimmer, stay=False)
        return self

    def shake(self, start: float = 0, end: float = 0.5, amplitude=5, frequency=20, easing=easings.there_and_back):
        """Rapid random-looking jitter effect for emphasis or error states."""
        dur = end - start
        if dur <= 0:
            return self
        _s, _d, _a, _freq = start, max(dur, 1e-9), amplitude, frequency
        def _dx(t, _s=_s, _d=_d, _a=_a, _freq=_freq, _easing=easing):
            p = (t - _s) / _d
            return _a * math.sin(math.tau * _freq * p) * _easing(p)
        def _dy(t, _s=_s, _d=_d, _a=_a, _freq=_freq, _easing=easing):
            p = (t - _s) / _d
            return _a * math.cos(2.7 * math.pi * _freq * p) * _easing(p)
        return self._apply_shift_effect(start, end, _dx, _dy)

    def undulate(self, start: float = 0, end: float = 1, amplitude=0.15, n_waves=2, easing=easings.smooth):
        """Wavy pulsing scale effect, like a heartbeat or breathing."""
        dur = end - start
        if dur <= 0:
            return self
        self._ensure_scale_origin(start)
        _s, _d = start, max(dur, 1e-9)
        def _scale(t, _s=_s, _d=_d, _a=amplitude, _w=n_waves, _easing=easing):
            p = (t - _s) / _d
            return 1 + _a * math.sin(p * _w * math.tau) * (1 - _easing(p))
        self._set_scale_xy(start, end, _scale)
        return self

    def rubber_band(self, start: float = 0, end: float = 1, x_factor=1.3, y_factor=0.7, easing=easings.there_and_back):
        """Elastic stretch: squash and stretch the object, then snap back."""
        dur = end - start
        if dur <= 0:
            return self
        self._ensure_scale_origin(start)
        _d = max(dur, 1e-9)
        self._set_scale_xy(start, end,
            _lerp(start, _d, 1, x_factor, easing),
            _lerp(start, _d, 1, y_factor, easing), stay=True)
        return self

    def jiggle(self, start: float = 0, end: float = 1, amplitude=5, easing=easings.smooth):
        """Small random-looking position jitter that decays over time."""
        dur = end - start
        if dur <= 0:
            return self
        _s, _d, _amt = start, max(dur, 1e-9), amplitude
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
        obj_cx, obj_cy = self.center(start)
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
        self._apply_shift_func(_pos, start, end)
        return self

    def bounce(self, start: float = 0, end: float = 1, height=50, n_bounces=3, easing=easings.smooth):
        """Bounce the object up and down like a ball."""
        dur = end - start
        if dur <= 0:
            return self
        _s, _d, _h, _b = start, max(dur, 1e-9), height, n_bounces
        def _dy(t, _s=_s, _d=_d, _h=_h, _b=_b, _easing=easing):
            progress = (t - _s) / _d
            phase = progress * _b * math.tau
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
            return _a * math.exp(-_damp * progress) * math.sin(math.tau * _freq * progress)
        dx = _osc if axis in ('x', 'both') else None
        dy = _osc if axis in ('y', 'both') else None
        return self._apply_shift_effect(start, end, dx, dy)

    def ripple(self, start: float = 0, count=3, end: float = 0.5, max_radius=100,
               color='#58C4DD', stroke_width=2):
        """Emit expanding, fading rings from the object's center.
        Returns a VCollection of Circle objects (must be added to canvas)."""
        from vectormation._shapes import Circle as _Circle
        dur = end - start
        cx, cy = self.center(start)
        rings = []
        for i in range(count):
            t0 = start + i * (dur / max(count, 1))
            ring = _Circle(r=1, cx=cx, cy=cy, creation=t0,
                           fill_opacity=0, stroke=color, stroke_width=stroke_width)
            ring._show_from(t0)
            if dur > 0:
                ring.rx.set(t0, t0 + dur, _ramp(t0, dur, max_radius, easings.linear), stay=True)
                ring.ry.set(t0, t0 + dur, _ramp(t0, dur, max_radius, easings.linear), stay=True)
                ring.styling.stroke_opacity.set(t0, t0 + dur,
                    _ramp_down(t0, dur, 1, easings.linear), stay=True)
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
            _ramp_down(s, dur, total, easing), stay=True)
        return self

    # Shared inset clip-path templates: direction = which side gets clipped.
    _CLIP_INSET = {
        'right': lambda pct: f'inset(0 {pct:.1f}% 0 0)',
        'left':  lambda pct: f'inset(0 0 0 {pct:.1f}%)',
        'down':  lambda pct: f'inset(0 0 {pct:.1f}% 0)',
        'up':    lambda pct: f'inset({pct:.1f}% 0 0 0)',
    }
    _CLIP_REVERSE = {'right': 'left', 'left': 'right', 'down': 'up', 'up': 'down',
                     'top': 'bottom', 'bottom': 'top'}

    def wipe(self, direction='right', start: float = 0, end: float = 1,
             easing=easings.smooth, reverse=False):
        """Reveal (or hide if reverse=True) with a clip-path wipe effect."""
        dur = end - start
        if dur <= 0:
            return self
        s = start
        key = self._CLIP_REVERSE.get(direction, direction) if reverse else direction
        tmpl = self._CLIP_INSET[key]
        self.styling.clip_path.set(s, end, _clip_reveal(tmpl, s, dur, easing), stay=True)
        if reverse:
            self._hide_from(end)
        else:
            self._show_from(start)
        return self

    def highlight_border(self, start: float = 0, end: float = 0.5, color='#FFFF00',
                          width=4, easing=easings.there_and_back):
        """Flash the stroke to briefly highlight the object's border."""
        dur = end - start
        if dur <= 0:
            return self
        s = start
        self.styling.stroke = attributes.Color(s, color)
        old_w = self.styling.stroke_width.at_time(s)
        self.styling.stroke_width.set(s, end, _lerp(s, dur, old_w, width, easing), stay=True)
        self.styling.stroke_opacity.set(s, end, _ramp(s, dur, 1, easing), stay=True)
        return self

    def flash_highlight(self, start: float = 0, end: float = 1, color='#FFFF00',
                        width=3, easing=easings.there_and_back):
        """Briefly highlight the object with a colored border flash using a surrounding rectangle."""
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
                _ramp(s, dur, 1, easing), stay=True)
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

    def glitch(self, start: float = 0, end: float = 1, intensity=10, n_flashes=5,
               easing=easings.there_and_back):
        """Random glitch effect: brief jitter flashes over [start, end]."""
        dur = end - start
        if dur <= 0 or n_flashes <= 0:
            return self
        flash_dur = min(0.05, dur / (n_flashes * 3))
        s = start
        for i in range(n_flashes):
            t0 = s + dur * (i + 0.5) / n_flashes
            t1 = t0 + flash_dur
            dx = intensity * (1 if i % 2 == 0 else -1) * (0.5 + (i % 3) * 0.3)
            dy = intensity * (0.3 if i % 3 == 0 else -0.5) * (0.4 + (i % 2) * 0.4)
            self._apply_shift_func(lambda t, _dx=dx, _dy=dy: (_dx, _dy), t0, t1, stay=False)
        return self

    def flash_color(self, color='#FFFF00', start: float = 0, end: float = 0.4,
                     attr='fill'):
        """Flash to a color and back. Quick attention-grabbing effect."""
        return self.pulse_color(color, start=start, end=end, n_pulses=1, attr=attr)

    def pulse_color(self, color='#FFFF00', start: float = 0, end: float = 1,
                     n_pulses=3, attr='fill'):
        """Periodic color pulsing: alternate between current color and *color* N times."""
        dur = end - start
        if dur <= 0 or n_pulses <= 0:
            return self
        src = getattr(self.styling, attr)
        if not isinstance(src, attributes.Color):
            return self
        original_rgb = src.time_func(start)
        pulse_dur = dur / n_pulses
        for i in range(n_pulses):
            seg_s = start + i * pulse_dur
            seg_mid = seg_s + pulse_dur / 2
            seg_e = seg_s + pulse_dur
            src.interpolate(attributes.Color(seg_s, color), seg_s, seg_mid, easing=easings.linear)
            src.interpolate(attributes.Color(seg_s, original_rgb), seg_mid, seg_e, easing=easings.linear)
        return self

    def color_shift(self, hue_shift=30, start=0, end=1, easing=easings.smooth):
        """Animate shifting the fill color's hue by *hue_shift* degrees over [start, end]."""
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
                cx, cy = _obj.center(t)
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

    def reflect(self, axis='vertical', start: float = 0):
        """Mirror/reflect the object across an axis through its center."""
        self.styling._scale_origin = self.center(start)
        attr = self.styling.scale_x if axis == 'vertical' else self.styling.scale_y
        attr.set_onward(start, -attr.at_time(start))
        return self

    def squish(self, start: float = 0, end: float = 1, axis='x', factor=0.5,
                easing=easings.smooth):
        """Squish the object along an axis and bounce back."""
        dur = end - start
        if dur <= 0:
            return self
        self.styling._scale_origin = self.center(start)
        sx0, sy0 = self._get_scale(start)
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
        """Area-preserving squash/stretch: x scales by *factor*, y by 1/factor, then back."""
        dur = end - start
        if dur <= 0:
            return self
        cx, cy = self.center(start)
        self.styling._scale_origin = (cx, cy)
        sx0, sy0 = self._get_scale(start)
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
        self._set_scale_xy(start, end, _ssx, _ssy)
        return self

    def warp(self, start: float = 0, end: float = 1, amplitude=0.15, frequency=3,
             easing=easings.smooth):
        """Wobbly distortion effect — alternating scale_x/scale_y oscillation.
        Creates a jelly-like warping motion that resolves back to normal."""
        _a, _f = amplitude, frequency
        def _make(sx0, sy0, _s, _d):
            def _wx(t, _s=_s, _d=_d, _a=_a, _f=_f, _sx0=sx0, _easing=easing):
                p = _easing((t - _s) / _d)
                envelope = math.sin(math.pi * p)
                return _sx0 * (1 + _a * envelope * math.sin(math.tau * _f * p))
            def _wy(t, _s=_s, _d=_d, _a=_a, _f=_f, _sy0=sy0, _easing=easing):
                p = _easing((t - _s) / _d)
                envelope = math.sin(math.pi * p)
                return _sy0 * (1 + _a * envelope * math.cos(math.tau * _f * p))
            return _wx, _wy
        return self._scale_effect(start, end, _make, force_origin=True)

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
        _rcx, _rcy = self.center(start)
        # Rotation
        self.styling.rotation.set(start, end,
            lambda t, _s=_s, _d=_d, _turns=_turns, _deg0=_deg0, _rcx=_rcx, _rcy=_rcy, _easing=easing:
                (_deg0 + 360 * _turns * _easing((t - _s) / _d), _rcx, _rcy),
            stay=False)
        if shrink:
            def _make_scale(s0):
                return lambda t, _s=_s, _d=_d, _s0=s0, _easing=easing: \
                    _s0 * (1 - 0.5 * math.sin(math.pi * _easing((t - _s) / _d)))
            self._set_scale_xy(start, end,
                _make_scale(self.styling.scale_x.at_time(start)),
                _make_scale(self.styling.scale_y.at_time(start)))
        return self

    def heartbeat(self, start: float = 0, end: float = 1, beats=3,
                   scale_factor=1.3, easing=easings.smooth):
        """ECG-style double-pulse heartbeat: lub-dub + rest, repeated *beats* times."""
        _sf, _beats = scale_factor, beats
        def _make(sx0, sy0, _s, _d):
            def _ecg(t, _s=_s, _d=_d, _sf=_sf, _beats=_beats, _easing=easing):
                beat_dur = _d / _beats
                local = ((t - _s) % beat_dur) / beat_dur
                if local < 0.25:
                    p = _easing(local / 0.25)
                    return 1 + (_sf - 1) * math.sin(math.pi * p)
                if 0.30 <= local < 0.55:
                    p = _easing((local - 0.30) / 0.25)
                    return 1 + (_sf - 1) * 0.75 * math.sin(math.pi * p)
                return 1.0
            return (lambda t, _b=sx0, _fn=_ecg: _b * _fn(t),
                    lambda t, _b=sy0, _fn=_ecg: _b * _fn(t))
        return self._scale_effect(start, end, _make)

    def breathe(self, start: float = 0, end: float = 1, amplitude=0.08,
                speed=1.0, easing=easings.smooth):
        """Steady scale oscillation simulating natural breathing."""
        _amp, _spd = amplitude, speed
        def _make(sx0, sy0, _s, _d):
            def _br(base):
                return lambda t, _s=_s, _d=_d, _amp=_amp, _spd=_spd, _b=base, _e=easing: \
                    _b * (1 + _amp * math.sin(math.tau * _spd * _e((t - _s) / _d) * _d))
            return _br(sx0), _br(sy0)
        return self._scale_effect(start, end, _make)

    def pendulum(self, start: float = 0, end: float = 1, amplitude=20,
                 oscillations=4, cx=None, cy=None, easing=easings.smooth):
        """Damped pendulum oscillation — rotates back and forth with exponential decay."""
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
            angle = _a * math.sin(math.tau * _n * p) * decay
            return (angle, _cx, _cy)

        self.styling.rotation.set(start, end, _rot)
        return self

    def _typewriter_clip(self, start, end, direction, easing, reveal):
        """Shared logic for typewriter_reveal / typewriter_delete."""
        dur = end - start
        if dur <= 0:
            return self
        if reveal:
            self._show_from(start)
        else:
            self._hide_from(end)
        d = max(dur, 1e-9)
        tmpl = self._CLIP_INSET.get(direction, self._CLIP_INSET['right'])
        clip_fn = _clip_reveal(tmpl, start, d, easing) if reveal else _clip_hide(tmpl, start, d, easing)
        self.styling.clip_path.set(start, end, clip_fn, stay=True)
        return self

    def typewriter_reveal(self, start: float = 0, end: float = 1,
                          direction='right', easing=easings.smooth):
        """Clip-path sweep reveal. direction: 'right', 'left', 'down', 'up'."""
        return self._typewriter_clip(start, end, direction, easing, reveal=True)

    def cross_out(self, start: float = 0, end: float = 0.5, color='#FC6255',
                   stroke_width=4, buff=5):
        """Draw an X across this object. Returns the Cross VCollection (add to canvas)."""
        from vectormation._svg_utils import Cross
        _, _, bw, bh = self.bbox(start)
        cx, cy = self.center(start)
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
        tx, ty = _coords_of(target, start)
        cx, cy = self.get_center(start)
        ddx, ddy = tx - cx, ty - cy
        _d = max(dur, 1e-9)
        for xa, ya in self._shift_reals():
            xa.add(start, end, _ramp(start, _d, ddx, easing), stay=True)
            ya.add(start, end, _ramp(start, _d, ddy, easing), stay=True)
        _s, _dd = start, _d
        for c in self._shift_coors():
            c.add(start, end,
                lambda t, _s=_s, _d=_dd, _dx=ddx, _dy=ddy, _easing=easing:
                    (_dx * _easing((t - _s) / _d), _dy * _easing((t - _s) / _d)),
                stay=True)
        return self

    def broadcast(self, start: float = 0, end: float = 0.5, n_copies=3,
                   max_scale=3, color=None):
        """Emit expanding, fading copies from this object's center.
        Returns a VCollection of copies (must be added to canvas)."""
        duration = end - start
        copies = []
        for i in range(n_copies):
            t0 = start + i * (duration / max(n_copies, 1))
            t1 = t0 + duration / max(n_copies, 1)
            copy = deepcopy(self)
            copy._ensure_scale_origin(t0)
            copy.show.set_onward(0, False)
            copy.show.set_onward(t0, True)
            sx0 = copy.styling.scale_x.at_time(t0)
            sy0 = copy.styling.scale_y.at_time(t0)
            dur = max(t1 - t0, 1e-9)
            copy.styling.scale_x.set(t0, t1,
                _lerp(t0, dur, sx0, sx0 * max_scale, easings.linear), stay=True)
            copy.styling.scale_y.set(t0, t1,
                _lerp(t0, dur, sy0, sy0 * max_scale, easings.linear), stay=True)
            copy.styling.fill_opacity.set(t0, t1,
                _ramp_down(t0, dur, 1, easings.linear), stay=True)
            copy.styling.stroke_opacity.set(t0, t1,
                _ramp_down(t0, dur, 1, easings.linear), stay=True)
            if color:
                copy.styling.stroke.set_onward(t0, color)
                copy.styling.fill.set_onward(t0, color)
            copy.show.set_onward(t1, False)
            copies.append(copy)
        return VCollection(*copies)

    def _freeze_position(self, time):
        """Freeze all position attributes at their value at *time*."""
        for xa, ya in self._shift_reals():
            xa.set_onward(time, xa.at_time(time))
            ya.set_onward(time, ya.at_time(time))
        for c in self._shift_coors():
            c.set_onward(time, c.at_time(time))

    def stamp(self, time: float = 0, opacity=0.3):
        """Leave a faded copy (ghost) at the current position. Returns the copy (add to canvas)."""

        ghost = deepcopy(self)
        ghost.styling.fill_opacity.set_onward(time, opacity)
        ghost.styling.stroke_opacity.set_onward(time, opacity)
        # Freeze position: remove all animations after this time
        ghost.show.set_onward(time, True)
        return ghost

    def trail(self, start: float = 0, end: float = 1, n_copies=5, fade=True):
        """Leave fading ghost copies at intervals during [start, end].
        Returns a list of ghost VObjects (must be added to canvas separately)."""

        ghosts = []
        for i in range(n_copies):
            t = start + (end - start) * (i + 1) / (n_copies + 1)
            ghost = deepcopy(self)
            ghost._freeze_position(t)
            ghost.show.set_onward(0, False)
            ghost.show.set_onward(t, True)
            if fade:
                opacity = 0.1 + 0.3 * (i / max(n_copies - 1, 1))
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
                attr.set(s, end, _lerp(s, dur, cur, opacity, easing), stay=True)
        return self

    def undim(self, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Restore full opacity (undo dim)."""
        return self.dim(start=start, end=end, opacity=1.0, easing=easing)

    def clone(self, offset_x=0, offset_y=0, *, count=None, dx=0, dy=0, start=0):
        """Deep copy, optionally shifted. With count=N returns VCollection of N shifted clones."""
        if count is not None:
            clones = []
            for i in range(1, count + 1):
                c = deepcopy(self)
                c.shift(dx=dx * i, dy=dy * i, start=start)
                clones.append(c)
            return VCollection(*clones)
        c = deepcopy(self)
        if offset_x != 0 or offset_y != 0:
            c.shift(dx=offset_x, dy=offset_y)
        return c

    def align_to(self, other, edge: str | tuple = 'left', start: float = 0, end: float | None = None, easing=None):
        """Align an edge of this object with the same edge of another."""
        edge = _norm_edge(edge, 'left')
        mx, my, mw, mh = self.bbox(start)
        ox, oy, ow, oh = other.bbox(start)
        offsets = {
            'left': (ox - mx, 0),
            'right': ((ox + ow) - (mx + mw), 0),
            'top': (0, oy - my),
            'bottom': (0, (oy + oh) - (my + mh)),
        }
        dx, dy = offsets[edge]
        kw = {'start': start}
        if end is not None:
            kw['end'] = end
        if easing is not None:
            kw['easing'] = easing
        self.shift(dx=dx, dy=dy, **kw)
        return self

    @staticmethod
    def fade_transform(source, target, start: float = 0, end: float = 1):
        """Cross-fade: fade out source while fading in target over [start, end].
        Both objects should already be added to the canvas."""
        source.fadeout(start=start, end=end, change_existence=True)
        target.fadein(start=start, end=end, change_existence=True)
        return source

    @staticmethod
    def swap(a, b, start: float = 0, end: float = 1, easing=easings.smooth):
        """Swap positions of two objects over [start, end]."""
        acx, acy = a.center(start)
        bcx, bcy = b.center(start)
        a.move_to(bcx, bcy, start=start, end=end, easing=easing)
        b.move_to(acx, acy, start=start, end=end, easing=easing)
        return a

    def transform_from_copy(self, target, start: float = 0, end: float = 1, easing=easings.smooth):
        """Create a ghost copy of this object and morph it into *target*.

        The original remains unchanged; a MorphObject is returned that
        morphs from a copy of this shape into the target over [start, end].
        The returned object should be added to the canvas.
        """
        from copy import deepcopy
        from vectormation._composites import MorphObject
        ghost_src = deepcopy(self)
        return MorphObject(ghost_src, target, start=start, end=end, easing=easing)

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
        """Animate styling (fill, stroke, opacity, etc.) to match another object's style."""
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

    def scale_about_point(self, factor, px, py, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Scale by *factor* about pivot point (*px*, *py*)."""
        self.styling._scale_origin = (px, py)
        return self.stretch(factor, factor, start, end, easing)

    def _set_color_prop(self, attr_name, color, start, end, easing, color_space):
        """Set or animate a color attribute (fill or stroke)."""
        if end is None:
            setattr(self.styling, attr_name, attributes.Color(start, color))
        else:
            self.set_color(start, end, **{attr_name: color}, easing=easing, color_space=color_space)

    def set_fill(self, color=None, opacity=None, start: float = 0, end: float | None = None, easing=easings.smooth, color_space='rgb'):
        """Set fill color and/or opacity. Animated if end is given."""
        if color is not None:
            self._set_color_prop('fill', color, start, end, easing, color_space)
        if opacity is not None:
            _set_attr(self.styling.fill_opacity, start, end, opacity, easing)
        return self

    def set_stroke(self, color=None, width=None, opacity=None, start: float = 0, end: float | None = None, easing=easings.smooth, color_space='rgb'):
        """Set stroke color, width, and/or opacity. Animated if end is given."""
        if color is not None:
            self._set_color_prop('stroke', color, start, end, easing, color_space)
        if width is not None:
            _set_attr(self.styling.stroke_width, start, end, width, easing)
        if opacity is not None:
            _set_attr(self.styling.stroke_opacity, start, end, opacity, easing)
        return self

    def set_stroke_dash(self, pattern, start: float = 0):
        """Set the stroke dash pattern (string like '5 3' or list/tuple)."""
        if pattern is None:
            pattern_str = ''
        elif isinstance(pattern, (list, tuple)):
            pattern_str = ' '.join(str(v) for v in pattern)
        else:
            pattern_str = str(pattern)
        self.styling.stroke_dasharray.set_onward(start, pattern_str)
        return self

    def set_backstroke(self, color='#000000', width=8, start=0):
        """Add a background stroke (rendered behind fill) for readability."""
        self.set_stroke(color=color, width=width, start=start)
        _wrap_to_svg(self, lambda inner, t: f"<g style='paint-order: stroke fill'>{inner}</g>", start)
        return self

    def set_opacity(self, value, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Set fill_opacity and stroke opacity together. Animated if end is given."""
        for attr in (self.styling.fill_opacity, self.styling.opacity):
            _set_attr(attr, start, end, value, easing)
        return self

    def get_opacity(self, time: float = 0):
        """Return the current opacity value at the given time (matches what set_opacity writes)."""
        return self.styling.opacity.at_time(time)

    def animate_opacity(self, start_opacity: float, end_opacity: float,
                        start: float = 0, end: float = 1,
                        easing=easings.smooth):
        """Animate opacity from *start_opacity* to *end_opacity* over [start, end]."""
        dur = end - start
        if dur <= 0:
            self.styling.opacity.set_onward(start, end_opacity)
            self.styling.fill_opacity.set_onward(start, end_opacity)
            return self
        fn = _lerp(start, dur, start_opacity, end_opacity, easing)
        self.styling.opacity.set(start, end, fn, stay=True)
        self.styling.fill_opacity.set(start, end, fn, stay=True)
        return self

    def set_position(self, x, y, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Move the object's center to (x, y). Shorthand for move_to."""
        return self.move_to(x, y, start=start, end=end, easing=easing)

    def stretch(self, x_factor: float = 1, y_factor: float = 1, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Non-uniform scale. Instant if end is None, animated otherwise."""
        self._ensure_scale_origin(start)
        for attr, factor in [(self.styling.scale_x, x_factor), (self.styling.scale_y, y_factor)]:
            _set_attr(attr, start, end, attr.at_time(start) * factor, easing)
        return self

    def match_width(self, other, time: float = 0):
        """Scale this object so its width matches *other*'s width at *time*."""
        return self._match_dim(other, time, 2)

    def match_height(self, other, time: float = 0):
        """Scale this object so its height matches *other*'s height at *time*."""
        return self._match_dim(other, time, 3)

    def _match_dim(self, other, time, idx):
        my_dim = self.bbox(time)[idx]
        other_dim = other.bbox(time)[idx]
        if my_dim > 0:
            self.scale(other_dim / my_dim, start=time)
        return self

from vectormation._collection import VCollection  # noqa: E402
VGroup = VCollection

