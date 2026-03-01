"""Extended shape classes: Line, Text, Arc, Path, and derivatives."""
import math
from xml.sax.saxutils import escape as _xml_escape
import vectormation.easings as easings
import vectormation.attributes as attributes
import vectormation.style as style
from vectormation.pathbbox import path_bbox
from vectormation._constants import (
    SMALL_BUFF, DEFAULT_STROKE_WIDTH, DEFAULT_ARROW_TIP_LENGTH, DEFAULT_ARROW_TIP_WIDTH,
    CHAR_WIDTH_FACTOR, ORIGIN,
    _rotate_point, _sample_function, _distance, _normalize, _circumcenter,
)
from vectormation._base import VObject, VCollection, _ramp, _ramp_down, _set_attr
from vectormation._base_helpers import _clamp01
from vectormation._shapes import Polygon, Rectangle, Lines

class Line(VObject):
    def __init__(self, x1: float = 0, y1: float = 0, x2: float = 100, y2: float = 100, creation: float = 0, z: float = 0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        self.p1 = attributes.Coor(creation, (x1, y1))
        self.p2 = attributes.Coor(creation, (x2, y2))
        self.styling = style.Styling(styling_kwargs, creation=creation, stroke='#fff', stroke_width=DEFAULT_STROKE_WIDTH)

    def _extra_attrs(self):
        return [self.p1, self.p2]

    def _shift_coors(self):
        return [self.p1, self.p2]

    def snap_points(self, time):
        """Return the two endpoint positions as snap points."""
        p1, p2 = self.p1.at_time(time), self.p2.at_time(time)
        return [(float(p1[0]), float(p1[1])), (float(p2[0]), float(p2[1]))]

    def bbox(self, time: float = 0):
        """Return the bounding box enclosing both endpoints."""
        return self._bbox_from_points([self.p1.at_time(time), self.p2.at_time(time)], time) or super().bbox(time)

    def _ep(self, time):
        """Return (x1, y1, x2, y2) endpoints at *time*."""
        p1, p2 = self.p1.at_time(time), self.p2.at_time(time)
        return p1[0], p1[1], p2[0], p2[1]

    def path(self, time):
        """Return the SVG path data string for this line."""
        x1, y1, x2, y2 = self._ep(time)
        return f'M{x1},{y1}L{x2},{y2}'

    def to_svg(self, time):
        """Return the SVG <line> element string."""
        x1, y1, x2, y2 = self._ep(time)
        return f"<line x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}'{self.styling.svg_style(time)} />"

    def get_start(self, time: float = 0):
        """Return the start point (x, y) of the line."""
        p = self.p1.at_time(time); return (float(p[0]), float(p[1]))

    def get_end(self, time: float = 0):
        """Return the end point (x, y) of the line."""
        p = self.p2.at_time(time); return (float(p[0]), float(p[1]))

    def get_length(self, time: float = 0):
        """Return the length of the line in pixels."""
        return _distance(*self._ep(time))
    length = get_length

    def get_angle(self, time: float = 0):
        """Return the angle of the line in degrees (atan2 of dy, dx)."""
        x1, y1, x2, y2 = self._ep(time); return math.degrees(math.atan2(y2 - y1, x2 - x1))

    def get_midpoint(self, time: float = 0):
        """Return the midpoint (x, y) of the line."""
        x1, y1, x2, y2 = self._ep(time); return ((x1 + x2) / 2, (y1 + y2) / 2)

    def split_at(self, t: float = 0.5, time: float = 0):
        """Split the line at parameter *t* and return two new Line objects."""
        t = _clamp01(t)
        x1, y1, x2, y2 = self._ep(time)
        mx = x1 + t * (x2 - x1)
        my = y1 + t * (y2 - y1)
        return Line(float(x1), float(y1), float(mx), float(my)), \
               Line(float(mx), float(my), float(x2), float(y2))

    def get_direction(self, time: float = 0):
        """Return the normalized unit vector ``(dx, dy)`` from p1 to p2."""
        x1, y1, x2, y2 = self._ep(time)
        return _normalize(x2 - x1, y2 - y1)

    get_unit_vector = get_direction

    def get_vector(self, time: float = 0):
        """Return the direction vector (dx, dy) from start to end."""
        x1, y1, x2, y2 = self._ep(time); return (x2 - x1, y2 - y1)

    def get_normal(self, time: float = 0):
        """Return the unit normal vector perpendicular to the line."""
        dx, dy = self.get_direction(time); return (-dy, dx)

    def angle_to(self, other, time: float = 0):
        """Return the angle in degrees [0, 180] between this line and *other*."""
        d1 = self.get_direction(time)
        d2 = other.get_direction(time)
        dot = d1[0] * d2[0] + d1[1] * d2[1]
        dot = max(-1.0, min(1.0, dot))  # clamp for numerical safety
        return math.degrees(math.acos(dot))

    angle_with = angle_to

    def is_parallel(self, other, time: float = 0, tol=1e-6):
        """Return True if cross product of directions is within *tol* of zero."""
        d1 = self.get_direction(time)
        d2 = other.get_direction(time)
        cross = d1[0] * d2[1] - d1[1] * d2[0]
        return abs(cross) < tol

    def is_perpendicular(self, other, time: float = 0, tol=1e-6):
        """Return True if dot product of directions is within *tol* of zero."""
        d1 = self.get_direction(time)
        d2 = other.get_direction(time)
        dot_val = d1[0] * d2[0] + d1[1] * d2[1]
        return abs(dot_val) < tol

    def get_slope(self, time: float = 0):
        """Return the slope (dy/dx) of the line, or math.inf for vertical lines.
        Uses SVG coordinates (y increases downward)."""
        x1, y1, x2, y2 = self._ep(time)
        dx = x2 - x1
        if abs(dx) < 1e-10:
            return math.inf
        return (y2 - y1) / dx

    def angle(self, time: float = 0):
        """Return the angle of this line in degrees (0 = right, CCW positive)."""
        x1, y1, x2, y2 = self._ep(time)
        return math.degrees(math.atan2(-(y2 - y1), x2 - x1))

    def _is_aligned(self, axis, time, tol):
        """Return True if start and end differ by less than *tol* on *axis* (0=x, 1=y)."""
        return abs(self.get_end(time)[axis] - self.get_start(time)[axis]) < tol

    def is_horizontal(self, time: float = 0, tol=1e-3):
        """Return True if the line is horizontal within tolerance."""
        return self._is_aligned(1, time, tol)

    def is_vertical(self, time: float = 0, tol=1e-3):
        """Return True if the line is vertical within tolerance."""
        return self._is_aligned(0, time, tol)

    def set_start(self, point, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Animate or set the start point of the line."""
        _set_attr(self.p1, start, end, point, easing)
        return self

    def set_end(self, point, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Animate or set the end point of the line."""
        _set_attr(self.p2, start, end, point, easing)
        return self

    def set_points(self, p1, p2, start: float = 0):
        """Set both endpoints at once."""
        self.p1.set_onward(start, p1)
        self.p2.set_onward(start, p2)
        return self

    def set_length(self, length, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Set absolute length while keeping the midpoint fixed."""
        x1, y1, x2, y2 = self._ep(start)
        cur = _distance(x1, y1, x2, y2)
        if cur < 1e-9:
            return self
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = _normalize(x2 - x1, y2 - y1)
        half = length / 2
        _set_attr(self.p1, start, end, (mx - dx * half, my - dy * half), easing)
        _set_attr(self.p2, start, end, (mx + dx * half, my + dy * half), easing)
        return self

    def extend_to(self, length, anchor='start', start: float = 0, end: float | None = None, easing=easings.smooth):
        """Extend or shrink the line to *length*, keeping one endpoint fixed."""
        x1, y1, x2, y2 = self._ep(start)
        cur = _distance(x1, y1, x2, y2)
        if cur < 1e-9:
            return self
        factor = length / cur
        if anchor == 'start':
            # Keep p1 fixed, move p2
            new_p2 = (x1 + (x2 - x1) * factor, y1 + (y2 - y1) * factor)
            _set_attr(self.p2, start, end, new_p2, easing)
        else:
            # Keep p2 fixed, move p1
            new_p1 = (x2 - (x2 - x1) * factor, y2 - (y2 - y1) * factor)
            _set_attr(self.p1, start, end, new_p1, easing)
        return self

    def get_perpendicular_point(self, px, py, time: float = 0):
        """Find the point on the line closest to ``(px, py)``."""
        x1, y1, x2, y2 = self._ep(time)
        dx, dy = x2 - x1, y2 - y1
        seg_len_sq = dx * dx + dy * dy
        if seg_len_sq < 1e-18:
            return (float(x1), float(y1))
        t = ((px - x1) * dx + (py - y1) * dy) / seg_len_sq
        t = _clamp01(t)
        return (float(x1 + t * dx), float(y1 + t * dy))

    get_projection = get_perpendicular_point

    def set_angle(self, angle_deg, about='midpoint', start: float = 0, end: float | None = None, easing=easings.smooth):
        """Rotate the line to the given angle (degrees) about its midpoint or start."""
        x1, y1, x2, y2 = self._ep(start)
        target = math.radians(angle_deg)
        length = _distance(x1, y1, x2, y2)
        if about == 'start':
            new_p2 = (x1 + length * math.cos(target), y1 + length * math.sin(target))
            _set_attr(self.p2, start, end, new_p2, easing)
        else:
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            half = length / 2
            _set_attr(self.p1, start, end, (mx - half * math.cos(target), my - half * math.sin(target)), easing)
            _set_attr(self.p2, start, end, (mx + half * math.cos(target), my + half * math.sin(target)), easing)
        return self

    def put_start_and_end_on(self, p1, p2, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Position the line between two points."""
        _set_attr(self.p1, start, end, p1, easing)
        _set_attr(self.p2, start, end, p2, easing)
        return self

    @classmethod
    def between(cls, p1, p2, **kwargs):
        """Create a Line from two (x, y) tuples."""
        return cls(p1[0], p1[1], p2[0], p2[1], **kwargs)

    from_points = between

    @classmethod
    def vertical(cls, x, y1, y2, **kwargs):
        """Create a vertical line at x from y1 to y2."""
        return cls(x, y1, x, y2, **kwargs)

    @classmethod
    def horizontal(cls, y, x1, x2, **kwargs):
        """Create a horizontal line at y from x1 to x2."""
        return cls(x1, y, x2, y, **kwargs)

    @classmethod
    def from_direction(cls, origin, direction, length=100, **kwargs):
        """Create a Line from *origin* along *direction* for *length* pixels."""
        ox, oy = origin
        dx, dy = direction
        mag = math.hypot(dx, dy)
        if mag < 1e-10:
            return cls(ox, oy, ox, oy, **kwargs)
        nx, ny = dx / mag, dy / mag
        return cls(ox, oy, ox + nx * length, oy + ny * length, **kwargs)

    @classmethod
    def from_angle(cls, origin, angle_deg, length=100, **kwargs):
        """Create a Line from *origin* at *angle_deg* degrees for *length* pixels."""
        ox, oy = origin
        rad = math.radians(angle_deg)
        dx = math.cos(rad)
        dy = -math.sin(rad)  # negate because SVG y-axis points downward
        return cls(ox, oy, ox + dx * length, oy + dy * length, **kwargs)

    @classmethod
    def from_slope_point(cls, slope, point, length=200, **kwargs):
        """Create a Line passing through *point* with the given *slope*."""
        px, py = point
        half = length / 2
        if math.isinf(slope):
            # Vertical line
            return cls(px, py - half, px, py + half, **kwargs)
        dx = 1.0 / math.sqrt(1 + slope * slope)
        dy = slope * dx
        return cls(px - dx * half, py - dy * half,
                   px + dx * half, py + dy * half, **kwargs)

    @classmethod
    def from_objects(cls, obj_a, obj_b, buff: float = 0, **kwargs):
        """Create a Line connecting the nearest edges of two objects."""
        ca = obj_a.center(0)
        cb = obj_b.center(0)
        dx = cb[0] - ca[0]
        dy = cb[1] - ca[1]
        if abs(dx) >= abs(dy):
            # Horizontal: use right/left edges
            if dx >= 0:
                p1 = obj_a.get_edge('right', 0)
                p2 = obj_b.get_edge('left', 0)
            else:
                p1 = obj_a.get_edge('left', 0)
                p2 = obj_b.get_edge('right', 0)
        else:
            # Vertical: use bottom/top edges
            if dy >= 0:
                p1 = obj_a.get_edge('bottom', 0)
                p2 = obj_b.get_edge('top', 0)
            else:
                p1 = obj_a.get_edge('top', 0)
                p2 = obj_b.get_edge('bottom', 0)
        # Apply buff to shorten both endpoints
        if buff > 0:
            ldx = p2[0] - p1[0]
            ldy = p2[1] - p1[1]
            length = math.hypot(ldx, ldy)
            if length > 2 * buff:
                ux, uy = ldx / length, ldy / length
                p1 = (p1[0] + ux * buff, p1[1] + uy * buff)
                p2 = (p2[0] - ux * buff, p2[1] - uy * buff)
        return cls(p1[0], p1[1], p2[0], p2[1], **kwargs)

    def lerp(self, t, time: float = 0):
        """Return point (x, y) at parameter t (0=start, 1=end) along the line."""
        x1, y1, x2, y2 = self._ep(time)
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))

    def subdivide_into(self, n=2, time: float = 0, **kwargs):
        """Divide this line into *n* equal segments."""
        if n < 1:
            n = 1
        x1, y1, x2, y2 = self._ep(time)
        dx, dy = (x2 - x1) / n, (y2 - y1) / n
        return [Line(x1=x1 + i * dx, y1=y1 + i * dy,
                     x2=x1 + (i + 1) * dx, y2=y1 + (i + 1) * dy, **kwargs)
                for i in range(n)]

    def divide(self, n=2, time: float = 0):
        """Return *n* + 1 points that divide the line into *n* equal segments."""
        if n < 1:
            n = 1
        x1, y1, x2, y2 = self._ep(time)
        return [(x1 + i * (x2 - x1) / n, y1 + i * (y2 - y1) / n)
                for i in range(n + 1)]

    def distance_to_point(self, px, py, time: float = 0):
        """Return the shortest distance from point ``(px, py)`` to this line segment."""
        cp = self.get_perpendicular_point(px, py, time)
        return math.hypot(px - cp[0], py - cp[1])

    def contains_point(self, px, py, time: float = 0, tol=2):
        """Return True if ``(px, py)`` is within *tol* pixels of this segment."""
        return self.distance_to_point(px, py, time) <= tol

    def add_tip(self, end=True, start=False, tip_length=None, tip_width=None, creation: float = 0):
        """Create arrowhead tip polygon(s) at line endpoints."""

        tl = tip_length if tip_length is not None else DEFAULT_ARROW_TIP_LENGTH
        tw = tip_width if tip_width is not None else DEFAULT_ARROW_TIP_WIDTH
        hw = tw / 2
        x1, y1, x2, y2 = self._ep(creation)
        stroke_color = self.styling.stroke.time_func(creation)
        objects = [self]

        # Build tip at each requested endpoint: (tip_point, direction toward tip)
        tips = []
        if end:
            tips.append(((x2, y2), (x2 - x1, y2 - y1)))
        if start:
            tips.append(((x1, y1), (x1 - x2, y1 - y2)))
        for (tx, ty), (dx, dy) in tips:
            ux, uy = _normalize(dx, dy)
            px, py = -uy, ux
            bx, by = tx - ux * tl, ty - uy * tl
            objects.append(Polygon(
                (tx, ty), (bx + px * hw, by + py * hw), (bx - px * hw, by - py * hw),
                creation=creation, z=self.z,
                fill=stroke_color, fill_opacity=1, stroke_width=0,
            ))

        return VCollection(*objects, creation=creation, z=self.z)

    def __repr__(self):
        x1, y1, x2, y2 = self._ep(0)
        return f'Line(({x1:.0f},{y1:.0f})->({x2:.0f},{y2:.0f}))'

    def perpendicular(self, at_proportion=0.5, length=None, time: float = 0, **kwargs):
        """Return a new Line perpendicular to this line at the given proportion."""
        x1, y1, x2, y2 = self._ep(time)
        dx, dy = x2 - x1, y2 - y1
        line_len = math.hypot(dx, dy)
        if length is None:
            length = line_len
        px = x1 + dx * at_proportion
        py = y1 + dy * at_proportion
        if line_len == 0:
            return Line(px, py, px, py, **kwargs)
        nx, ny = -dy / line_len, dx / line_len
        half = length / 2
        return Line(px - nx * half, py - ny * half,
                    px + nx * half, py + ny * half, **kwargs)

    def perpendicular_at(self, t=0.5, length=None, time: float = 0, **kwargs):
        """Return a Line perpendicular to this line at parameter t (0=start, 1=end)."""
        x1, y1, x2, y2 = self._ep(time)
        dx, dy = -(y2 - y1), x2 - x1  # perpendicular direction
        mag = math.hypot(dx, dy)
        if length is None:
            length = max(0, mag)
        px = x1 + t * (x2 - x1)
        py = y1 + t * (y2 - y1)
        if mag > 0:
            dx, dy = dx / mag * length / 2, dy / mag * length / 2
        else:
            dx, dy = 0, 0
        return Line(x1=px - dx, y1=py - dy, x2=px + dx, y2=py + dy, **kwargs)

    def extend(self, factor=1.5, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Scale the line length by *factor* while keeping the midpoint fixed."""
        x1, y1, x2, y2 = self._ep(start)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = (x2 - x1) / 2 * factor, (y2 - y1) / 2 * factor
        _set_attr(self.p1, start, end, (mx - dx, my - dy), easing)
        _set_attr(self.p2, start, end, (mx + dx, my + dy), easing)
        return self

    def scale_length(self, factor=2.0, time: float = 0):
        """Scale line length by *factor* in place, keeping the midpoint fixed."""
        return self.extend(factor=factor, start=time)

    def parallel(self, offset=50, time: float = 0, **kwargs):
        """Return a new Line parallel to this one, offset perpendicular by offset pixels.
        Extra kwargs are forwarded to the new Line constructor."""
        x1, y1, x2, y2 = self._ep(time)
        dx, dy = x2 - x1, y2 - y1
        line_len = math.hypot(dx, dy)
        if line_len == 0:
            return Line(x1, y1, x2, y2, **kwargs)
        nx, ny = -dy / line_len, dx / line_len
        return Line(x1 + nx * offset, y1 + ny * offset,
                    x2 + nx * offset, y2 + ny * offset, **kwargs)

    def parallel_through(self, point, time: float = 0, **kwargs):
        """Return a new Line parallel to this one, passing through the given point."""
        x1, y1, x2, y2 = self._ep(time)
        dx, dy = x2 - x1, y2 - y1
        px, py = point
        # Center the parallel line on the given point
        return Line(x1=px - dx / 2, y1=py - dy / 2,
                    x2=px + dx / 2, y2=py + dy / 2, **kwargs)

    def rotate_around_midpoint(self, angle_deg, time: float = 0):
        """Rotate line endpoints around the midpoint by angle_deg degrees."""
        x1, y1, x2, y2 = self._ep(time)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        c, s = math.cos(math.radians(angle_deg)), math.sin(math.radians(angle_deg))
        for p, px, py in [(self.p1, x1, y1), (self.p2, x2, y2)]:
            dx, dy = px - mx, py - my
            p.set_onward(time, (mx + dx * c - dy * s, my + dx * s + dy * c))
        return self

    def _intersect_params(self, other, time: float = 0):
        """Return (t, u) line-line intersection parameters, or None if parallel."""
        x1, y1, x2, y2 = self._ep(time)
        x3, y3, x4, y4 = other._ep(time)
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(denom) < 1e-10:
            return None
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
        return (t, u)

    def intersect_line(self, other, time: float = 0):
        """Return intersection point (x, y) of this line with another, or None if parallel."""
        params = self._intersect_params(other, time)
        if params is None:
            return None
        t = params[0]
        x1, y1, x2, y2 = self._ep(time)
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))

    def intersect_segment(self, other, time: float = 0):
        """Return the intersection point only if it lies within both segments."""
        params = self._intersect_params(other, time)
        if params is None:
            return None
        t, u = params
        if t < -1e-10 or t > 1 + 1e-10 or u < -1e-10 or u > 1 + 1e-10:
            return None
        x1, y1, x2, y2 = self._ep(time)
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))

    def _line_param_at(self, px, py, time: float = 0):
        """Return (t, x1, y1, dx, dy) for projection of (px,py) onto the line."""
        x1, y1, x2, y2 = self._ep(time)
        dx, dy = x2 - x1, y2 - y1
        len_sq = dx * dx + dy * dy
        if len_sq < 1e-20:
            return (0.0, x1, y1, dx, dy)
        return (((px - x1) * dx + (py - y1) * dy) / len_sq, x1, y1, dx, dy)

    def project_point(self, px, py, time: float = 0):
        """Return the closest point on this line (extended) to point (px, py)."""
        t, x1, y1, dx, dy = self._line_param_at(px, py, time)
        return (x1 + t * dx, y1 + t * dy)

    closest_point_on_segment = get_perpendicular_point

    def parameter_at(self, px, py, time: float = 0):
        """Return the parameter t for the projection of (px, py) onto the line."""
        return float(self._line_param_at(px, py, time)[0])

    def project_onto(self, other, time: float = 0, **kwargs):
        """Project this line segment onto another line and return the projection."""
        p1 = other.project_point(*self.get_start(time), time=time)
        p2 = other.project_point(*self.get_end(time), time=time)
        return Line(x1=p1[0], y1=p1[1], x2=p2[0], y2=p2[1], **kwargs)

    get_normal_line = perpendicular_at

    def intersection(self, other, time: float = 0):
        """Return the intersection of this line with *other*."""
        if isinstance(other, Line):
            return self.intersect_segment(other, time)
        # Circle (subclass of Ellipse) or any object with intersect_line
        if hasattr(other, 'intersect_line'):
            return other.intersect_line(self, time)
        raise TypeError(f"intersection not supported between Line and {type(other).__name__}")

    def reflect_over(self, other, time: float = 0, **kwargs):
        """Reflect this line's endpoints over another line and return the result."""
        s1 = self.get_start(time)
        s2 = self.get_end(time)
        proj1 = other.project_point(s1[0], s1[1], time=time)
        proj2 = other.project_point(s2[0], s2[1], time=time)
        r1 = (2 * proj1[0] - s1[0], 2 * proj1[1] - s1[1])
        r2 = (2 * proj2[0] - s2[0], 2 * proj2[1] - s2[1])
        return Line(x1=r1[0], y1=r1[1], x2=r2[0], y2=r2[1], **kwargs)

    def bisector(self, time: float = 0, length=None, **kwargs):
        """Return the perpendicular bisector of this line."""
        mx, my = self.get_midpoint(time)
        nx, ny = self.get_normal(time)
        if length is None:
            length = self.get_length(time)
        half = length / 2
        return Line(x1=mx - nx * half, y1=my - ny * half,
                    x2=mx + nx * half, y2=my + ny * half, **kwargs)

class Text(VObject):
    """Plain SVG text element."""
    _NARROW = set('iIlj1|!.,;:\'"()[]{}')
    _WIDE = set('mMwWOQD@')

    def __init__(self, text='', x: float = ORIGIN[0], y: float = ORIGIN[1], font_size: float = 48, text_anchor=None, font_family=None, creation: float = 0, z: float = 0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        self.text = attributes.String(creation, text)
        self.x = attributes.Real(creation, x)
        self.y = attributes.Real(creation, y)
        self.font_size = attributes.Real(creation, font_size)
        self._text_anchor = text_anchor
        self._font_family = font_family
        self._font_weight = None
        self._font_style = None
        self.styling = style.Styling(styling_kwargs, creation=creation,
                                     fill='#fff', fill_opacity=1, stroke_width=0)

    def _extra_attrs(self):
        return [self.text, self.x, self.y, self.font_size]

    def _shift_reals(self):
        return [(self.x, self.y)]

    def snap_points(self, time):
        """Return the text anchor position as a snap point."""
        return [(float(self.x.at_time(time)), float(self.y.at_time(time)))]

    @staticmethod
    def _estimate_width(text, fs):
        return sum(fs * (0.35 if ch in Text._NARROW else 0.75 if ch in Text._WIDE
                         else 0.3 if ch == ' ' else 0.65 if ch.isupper() else 0.55)
                   for ch in str(text))

    def _text_left(self, x, w):
        if self._text_anchor == 'middle':
            return x - w / 2
        if self._text_anchor == 'end':
            return x - w
        return x

    def path(self, time):
        """Return an SVG path approximating the text bounding rectangle."""
        x, y, fs = self.x.at_time(time), self.y.at_time(time), self.font_size.at_time(time)
        w = self._estimate_width(self.text.at_time(time), fs)
        xl = self._text_left(x, w)
        return f'M{xl},{y-fs}L{xl+w},{y-fs}L{xl+w},{y}L{xl},{y}Z'

    def bbox(self, time: float = 0):
        """Return the estimated bounding box of the text."""
        x, y, fs = self.x.at_time(time), self.y.at_time(time), self.font_size.at_time(time)
        w = self._estimate_width(self.text.at_time(time), fs)
        return (self._text_left(x, w), y - fs, w, fs)

    def get_text(self, time: float = 0):
        """Return the text string at the given time."""
        return self.text.at_time(time)

    def get_font_size(self, time: float = 0):
        """Return the font size at the given time."""
        return self.font_size.at_time(time)

    def starts_with(self, prefix, time: float = 0):
        """Return True if the text starts with the given prefix."""
        return self.text.at_time(time).startswith(prefix)

    def ends_with(self, suffix, time: float = 0):
        """Return True if the text ends with the given suffix."""
        return self.text.at_time(time).endswith(suffix)

    def __repr__(self):
        t = self.text.at_time(0)
        return f'Text({t!r})' if len(t) <= 20 else f'Text({t[:17]!r}...)'

    def _text_anim_setup(self, start, end, change_existence):
        """Shared setup for text animations. Returns ``(full_text, dur)`` or ``None`` on early exit."""
        full_text = self.text.at_time(start)
        if not full_text:
            return None
        if change_existence:
            self._show_from(start)
        dur = end - start
        if dur <= 0:
            self.text.set_onward(start, full_text)
            return None
        return full_text, dur

    def typing(self, start: float = 0, end: float = 1, change_existence=True):
        """Typewriter effect: reveal text character by character over [start, end]."""
        setup = self._text_anim_setup(start, end, change_existence)
        if setup is None:
            return self
        full_text, dur = setup
        n = len(full_text)
        self.text.set(start, end, lambda t, _s=start, _d=dur, _n=n: full_text[:max(1, int(_n * (t - _s) / _d))], stay=True)
        return self

    def reveal_by_word(self, start: float = 0, end: float = 1, change_existence=True, easing=None):
        """Reveal text word by word over [start, end]."""
        easing = easing or easings.linear
        setup = self._text_anim_setup(start, end, change_existence)
        if setup is None:
            return self
        full_text, dur = setup
        words = full_text.split()
        if not words:
            return self
        n = len(words)

        def _text_at(t, _words=words, _full=full_text, _n=n, _e=easing,
                     _s=start, _d=dur):
            p = _e((t - _s) / _d)
            count = int(p * _n)
            count = max(0, min(_n, count))
            if count >= _n:
                return _full
            return ' '.join(_words[:count]) if count > 0 else ''

        self.text.set(start, end, _text_at, stay=True)
        return self

    @staticmethod
    def _highlight_rect(rect, start, end, opacity, easing):
        """Apply fade-in/out opacity animation to a highlight rectangle."""
        dur = end - start
        if dur > 0:
            rect.styling.fill_opacity.set(start, end,
                _ramp(start, dur, opacity, easing), stay=True)
        return rect

    def highlight(self, start: float = 0, end: float = 1, color='#FFFF00', opacity: float = 0.3, padding: float = 4, easing=easings.there_and_back):
        """Highlight the text with a colored background rectangle that fades in/out.
        Returns the highlight Rectangle (must be added to canvas separately)."""
        bx, by, bw, bh = self.bbox(start)
        rect = Rectangle(bw + 2 * padding, bh + 2 * padding,
                         x=bx - padding, y=by - padding,
                         creation=start, fill=color, fill_opacity=0, stroke_width=0)
        return self._highlight_rect(rect, start, end, opacity, easing)

    def highlight_substring(self, substring, color='#FFFF00', start: float = 0, end: float = 1,
                            opacity=0.3, easing=easings.there_and_back):
        """Highlight a substring with a colored background rectangle.
        Returns the highlight Rectangle (must be added to canvas)."""
        text_val = str(self.text.at_time(start))
        idx = text_val.find(substring)
        if idx < 0:
            return Rectangle(0, 0, x=0, y=0)
        fs = self.font_size.at_time(start)
        x, y = self.x.at_time(start), self.y.at_time(start)
        total_w = self._estimate_width(text_val, fs)
        xl = self._text_left(x, total_w)
        prefix_w = self._estimate_width(text_val[:idx], fs)
        sub_w = self._estimate_width(substring, fs)
        rect = Rectangle(sub_w, fs * 1.2, x=xl + prefix_w, y=y - fs * 0.8,
                         creation=start, fill=color, fill_opacity=0, stroke_width=0)
        return self._highlight_rect(rect, start, end, opacity, easing)

    def typewrite(self, start: float = 0, end: float = 1, cursor='|', change_existence=True):
        """Reveal text character by character like a typewriter.
        The text attribute is updated progressively with an optional cursor character."""
        setup = self._text_anim_setup(start, end, change_existence)
        if setup is None:
            return self
        full_text, dur = setup
        n = len(full_text)
        def _typed(t, _s=start, _d=dur):
            progress = min(1, (t - _s) / _d)
            chars = int(progress * n)
            shown = full_text[:chars]
            if chars < n:
                return shown + cursor
            return shown
        self.text.set(start, end, _typed, stay=True)
        self.text.set_onward(end, full_text)
        return self

    def untype(self, start: float = 0, end: float = 1, change_existence=True):
        """Reverse typewriter: remove characters right-to-left."""
        full_text = self.text.at_time(start)
        n = len(full_text)
        if n == 0:
            return self
        dur = end - start
        if dur <= 0:
            return self
        def _untyped(t, _s=start, _d=dur, _n=n, _ft=full_text):
            progress = min(1, (t - _s) / _d)
            remaining = _n - int(progress * _n)
            return _ft[:max(0, remaining)]
        self.text.set(start, end, _untyped, stay=True)
        self.text.set_onward(end, '')
        if change_existence:
            self._hide_from(end)
        return self

    word_by_word = reveal_by_word  # alias

    def scramble(self, start: float = 0, end: float = 1, charset=None, change_existence=True):
        """Decode/reveal text from random characters. Characters settle left-to-right."""
        setup = self._text_anim_setup(start, end, change_existence)
        if setup is None:
            return self
        full_text, dur = setup
        n = len(full_text)
        if charset is None:
            charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%&*'
        import random
        rng = random.Random(42)  # deterministic for reproducibility
        _randoms = [[rng.choice(charset) for _ in range(20)] for _ in range(n)]
        def _scrambled(t, _s=start, _d=dur):
            progress = min(1, (t - _s) / _d)
            settled = int(progress * n)
            result = list(full_text[:settled])
            frame = int((t - _s) * 15) % 20  # cycle through pre-generated randoms
            for i in range(settled, n):
                if full_text[i] == ' ':
                    result.append(' ')
                else:
                    result.append(_randoms[i][frame])
            return ''.join(result)
        self.text.set(start, end, _scrambled, stay=True)
        self.text.set_onward(end, full_text)
        return self

    def set_font_size(self, size, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Animate font size to new value."""
        _set_attr(self.font_size, start, end, size, easing)
        return self

    def bold(self, weight='bold'):
        """Set the font weight to bold."""
        self._font_weight = weight if weight != 'normal' else None
        return self

    def italic(self, style='italic'):
        """Set the font style to italic."""
        self._font_style = style if style != 'normal' else None
        return self

    def set_font_family(self, family):
        """Set the font family for this text element."""
        self._font_family = family
        return self

    def set_text(self, start: float, end: float, new_text, easing=easings.smooth):
        """Fade out old text and fade in new text over [start, end].
        Opacity goes to 0 at midpoint, text changes, opacity returns."""
        if start >= end:
            self.text.set_onward(start, new_text)
            return self
        mid = (start + end) / 2
        dur1, dur2 = mid - start, end - mid
        self.styling.opacity.set(start, mid,
            _ramp_down(start, dur1, 1, easing), stay=True)
        self.text.set_onward(mid, new_text)
        self.styling.opacity.set(mid, end,
            _ramp(mid, dur2, 1, easing), stay=True)
        return self

    def update_text(self, new_text, start: float = 0):
        """Instantly change the displayed text from *start* onward."""
        self.text.set_onward(start, new_text)
        return self

    def reverse_text(self, time: float = 0):
        """Reverse the text at the given time."""
        text = self.text.at_time(time)
        if isinstance(text, str):
            self.text.set_onward(time, text[::-1])
        return self

    def reverse(self, time: float = 0):
        """Return the text content reversed (does not modify the object)."""
        return self.text.at_time(time)[::-1]

    def _text_split_ctx(self, time):
        """Return (full_text, x, y, font_size, char_width, fill) for split methods."""
        full = str(self.text.at_time(time))
        return (full, self.x.at_time(time), self.y.at_time(time),
                self.font_size.at_time(time),
                self.font_size.at_time(time) * CHAR_WIDTH_FACTOR,
                self.styling.fill.time_func(time))


    def split_chars(self, time: float = 0):
        """Split text into a VCollection of individual character Text objects."""

        full, x, y, fs, cw, fill = self._text_split_ctx(time)
        if not full:
            return VCollection()
        return VCollection(*(Text(text=ch, x=x + i * cw, y=y, font_size=fs,
                                  creation=time, stroke_width=0, fill=fill)
                             for i, ch in enumerate(full) if ch != ' '))

    def char_count(self, time: float = 0):
        """Return the number of characters in the text content at the given time."""
        return len(self.text.at_time(time))

    def word_count(self, time: float = 0):
        """Return the number of whitespace-separated words."""
        return len(self.text.at_time(time).split())

    def word_at(self, index, time: float = 0):
        """Return the word at the given index."""
        text = self.text.at_time(time)
        if isinstance(text, str):
            words = text.split()
            if 0 <= index < len(words):
                return words[index]
        return ''

    def split_lines(self, time: float = 0, line_spacing=1.4):
        """Split multi-line text (containing newlines) into separate Text objects."""

        full, x, y, fs, _, fill = self._text_split_ctx(time)
        step = fs * line_spacing
        return VCollection(*(Text(text=lt, x=x, y=y + i * step, font_size=fs,
                                  text_anchor=self._text_anchor, creation=time,
                                  stroke_width=0, fill=fill)
                             for i, lt in enumerate(full.split('\n'))))

    def fit_to_box(self, max_width, max_height=None, time: float = 0):
        """Adjust font_size so the text fits within the given box dimensions."""
        text = self.text.at_time(time)
        if not text:
            return self
        current_fs = self.font_size.at_time(time)
        current_width = self._estimate_width(text, current_fs)
        if current_width > 0 and max_width > 0:
            scale = max_width / current_width
            new_fs = current_fs * scale
            if max_height is not None:
                # Estimate line height as ~1.2x font size; cap so text height fits
                max_fs_from_height = max_height / 1.2
                new_fs = min(new_fs, max_fs_from_height)
            self.font_size.set_onward(time, new_fs)
        return self

    def to_upper(self, time: float = 0):
        """Change text to uppercase at given time."""
        return self._case_transform('upper', time)

    def to_lower(self, time: float = 0):
        """Change text to lowercase at given time."""
        return self._case_transform('lower', time)

    def _case_transform(self, method, time):
        full = self.text.at_time(time)
        if isinstance(full, str):
            self.text.set_onward(time, getattr(full, method)())
        return self

    def char_at(self, index, time: float = 0):
        """Return the character at the given index."""
        text = self.text.at_time(time)
        if isinstance(text, str) and 0 <= index < len(text):
            return text[index]
        return ''

    def truncate(self, n, ellipsis='...', time: float = 0):
        """Truncate the text to at most *n* characters, appending *ellipsis* if trimmed."""
        elen = len(ellipsis)
        if n < elen:
            raise ValueError(f"n ({n}) must be >= length of ellipsis ({elen})")
        full = self.text.at_time(time)
        if not isinstance(full, str):
            full = str(full)
        if len(full) <= n:
            return self
        truncated = full[:n - elen] + ellipsis
        self.text.set_onward(time, truncated)
        return self

    def split_into_words(self, time: float = 0, **kwargs):
        """Split text into a VCollection of individual word Text objects."""

        full = str(self.text.at_time(time))
        words = full.split()
        if not words:
            return VCollection()
        x = self.x.at_time(time)
        y = self.y.at_time(time)
        fs = self.font_size.at_time(time)
        total_w = self._estimate_width(full, fs)
        xl = self._text_left(x, total_w)
        style_kw = dict(font_size=fs, creation=time, stroke_width=0,
                        fill=self.styling.fill.time_func(time))
        style_kw.update(kwargs)
        parts = []
        cursor = 0
        for word in words:
            idx = full.index(word, cursor)
            prefix_w = self._estimate_width(full[:idx], fs)
            wx = xl + prefix_w
            t = Text(text=word, x=wx, y=y, **style_kw)
            parts.append(t)
            cursor = idx + len(word)
        return VCollection(*parts)

    split_words = split_into_words

    def add_background_rectangle(self, color='#000000', opacity=0.5, padding=10, time: float = 0):
        """Create a Rectangle behind the text, sized from bbox + padding."""

        bx, by, bw, bh = self.bbox(time)
        rect = Rectangle(
            bw + 2 * padding, bh + 2 * padding,
            x=bx - padding, y=by - padding,
            creation=time, z=self.z.at_time(time) - 1,
            fill=color, fill_opacity=opacity, stroke_width=0,
        )
        return VCollection(rect, self, creation=time)

    def wrap(self, max_width, time: float = 0):
        """Word-wrap text to fit within *max_width* pixels."""

        full = str(self.text.at_time(time))
        words = full.split()
        if not words:
            return VCollection()
        fs = self.font_size.at_time(time)
        x = self.x.at_time(time)
        y = self.y.at_time(time)
        fill_color = self.styling.fill.time_func(time)
        line_height = fs * 1.2
        lines = []
        current_words = []
        current_width = 0
        space_width = self._estimate_width(' ', fs)
        for word in words:
            word_width = self._estimate_width(word, fs)
            test_width = current_width + (space_width if current_words else 0) + word_width
            if current_words and test_width > max_width:
                lines.append(' '.join(current_words))
                current_words = [word]
                current_width = word_width
            else:
                current_words.append(word)
                current_width = test_width
        if current_words:
            lines.append(' '.join(current_words))
        parts = []
        for i, line_text in enumerate(lines):
            t = Text(text=line_text, x=x, y=y + i * line_height,
                     font_size=fs, creation=time, stroke_width=0,
                     fill=fill_color)
            for attr in ('_text_anchor', '_font_family', '_font_weight', '_font_style'):
                val = getattr(self, attr)
                if val:
                    setattr(t, attr, val)
            parts.append(t)
        return VCollection(*parts)

    def _font_attrs(self):
        parts = []
        for attr, name in ((self._text_anchor, 'text-anchor'), (self._font_weight, 'font-weight'),
                           (self._font_style, 'font-style'), (self._font_family, 'font-family')):
            if attr:
                parts.append(f" {name}='{attr}'")
        return ''.join(parts)

    def to_svg(self, time):
        """Return the SVG <text> element string."""
        font_attrs = self._font_attrs()
        txt = _xml_escape(str(self.text.at_time(time)))
        return (f"<text x='{self.x.at_time(time)}' y='{self.y.at_time(time)}'"
                f" font-size='{self.font_size.at_time(time)}'{font_attrs}{self.styling.svg_style(time)}"
                f">{txt}</text>")

class CountAnimation(Text):
    """Text that animates a number counting from start_val to end_val."""
    def __init__(self, start_val=0, end_val=100, start: float = 0, end: float = 1,
                 fmt='{:.0f}', easing=easings.smooth,
                 x: float = ORIGIN[0], y: float = ORIGIN[1], font_size: float = 60, text_anchor=None, creation: float = 0, z: float = 0, **styling_kwargs):
        super().__init__(text=fmt.format(start_val), x=x, y=y,
                         font_size=font_size, text_anchor=text_anchor,
                         creation=creation, z=z, **styling_kwargs)
        self._fmt = fmt
        self._last_val = end_val
        self._count_anim(start_val, end_val, start, end, easing)

    def __repr__(self):
        return f'CountAnimation({self._last_val})'

    def _count_anim(self, from_val, to_val, start, end, easing):
        """Set up counting animation between two values."""
        fmt = self._fmt
        dur = end - start
        if dur <= 0:
            self.text.set_onward(start, fmt.format(to_val))
        else:
            self.text.set(start, end,
                lambda t, _f=from_val, _t=to_val, _s=start, _d=dur, _fmt=fmt, _e=easing:
                    _fmt.format(_f + (_t - _f) * _e((t - _s) / _d)),
                stay=True)

    def count_to(self, target, start, end, easing=easings.smooth):
        """Animate counting from the current value to a new target."""
        self._count_anim(self._last_val, target, start, end, easing)
        self._last_val = target
        return self

class ValueTracker:
    """Convenience wrapper around a time-varying Real attribute."""
    def __init__(self, value=0, creation: float = 0):
        self.value = attributes.Real(creation, value)
        self.show = attributes.Real(creation, True)

    @property
    def last_change(self):
        """Return the time of the last change to the tracked value."""
        return self.value.last_change

    def get_value(self, time: float = 0):
        """Return the tracked value at the given time."""
        return self.value.at_time(time)

    at_time = get_value

    def set_value(self, val, start: float = 0):
        """Set the tracked value from the given start time onward."""
        self.value.set_onward(start, val)
        return self

    def animate_value(self, target, start, end, easing=easings.smooth):
        """Animate the tracked value to a target over [start, end]."""
        self.value.move_to(start, end, target, easing=easing)
        return self

    def increment_value(self, delta, start: float = 0):
        """Add *delta* to the current value at *start*."""
        self.value.set_onward(start, self.value.at_time(start) + delta)
        return self

    def _ov(self, other):
        return other.get_value() if isinstance(other, ValueTracker) else other

    def __add__(self, other): return ValueTracker(self.get_value() + self._ov(other))
    def __sub__(self, other): return ValueTracker(self.get_value() - self._ov(other))
    def __mul__(self, other): return ValueTracker(self.get_value() * self._ov(other))
    def __truediv__(self, other): return ValueTracker(self.get_value() / self._ov(other))

    def __iadd__(self, other):
        self.increment_value(self._ov(other)); return self

    def __isub__(self, other):
        self.increment_value(-self._ov(other)); return self

    def __repr__(self):
        return f'ValueTracker({self.value.at_time(0)})'

class ComplexValueTracker:
    """ValueTracker for complex numbers with real and imaginary parts."""
    def __init__(self, value=0+0j, creation: float = 0):
        if isinstance(value, (int, float)):
            value = complex(value)
        self.real = attributes.Real(creation, value.real)
        self.imag = attributes.Real(creation, value.imag)
        self.show = attributes.Real(creation, True)

    def get_value(self, time: float = 0):
        """Return the complex value at the given time."""
        return complex(self.real.at_time(time), self.imag.at_time(time))

    def set_value(self, val, start: float = 0):
        """Set the complex value from the given start time onward."""
        if isinstance(val, (int, float)):
            val = complex(val)
        self.real.set_onward(start, val.real)
        self.imag.set_onward(start, val.imag)
        return self

    def animate_value(self, target, start, end, easing=easings.smooth):
        """Animate the complex value to a target over [start, end]."""
        if isinstance(target, (int, float)):
            target = complex(target)
        self.real.move_to(start, end, target.real, easing=easing)
        self.imag.move_to(start, end, target.imag, easing=easing)
        return self

    def __repr__(self):
        return f'ComplexValueTracker({self.get_value(0)})'

class DecimalNumber(Text):
    """Text that dynamically displays a numeric value, updating each frame."""
    def __init__(self, value: 'float | ValueTracker | attributes.Real' = 0, fmt='{:.2f}', x=ORIGIN[0], y=ORIGIN[1], font_size=48,
                 text_anchor=None, creation: float = 0, z: float = 0, **styling_kwargs):
        if isinstance(value, ValueTracker):
            tracker = value.value
        elif isinstance(value, attributes.Real):
            tracker = value
        else:
            tracker = attributes.Real(creation, value)
        self._tracker = tracker
        super().__init__(text=fmt.format(tracker.at_time(creation)), x=x, y=y,
                         font_size=font_size, text_anchor=text_anchor,
                         creation=creation, z=z, **styling_kwargs)
        self.text.set_onward(creation, lambda t: fmt.format(tracker.at_time(t)))

    @property
    def tracker(self):
        """Return the underlying numeric attribute being tracked."""
        return self._tracker

    def set_value(self, val, start: float = 0):
        """Set the displayed numeric value from the given start time onward."""
        self._tracker.set_onward(start, val)
        return self

    def animate_value(self, target, start, end, easing=easings.smooth):
        """Animate the displayed numeric value to a target over [start, end]."""
        self._tracker.move_to(start, end, target, easing=easing)
        return self

    def __repr__(self):
        return f'DecimalNumber({self._tracker.at_time(0)})'

class Integer(DecimalNumber):
    """DecimalNumber that displays as an integer (no decimal places)."""
    def __init__(self, value=0, x=ORIGIN[0], y=ORIGIN[1], font_size=48,
                 text_anchor=None, creation: float = 0, z: float = 0, **styling_kwargs):
        super().__init__(value, fmt='{:.0f}', x=x, y=y, font_size=font_size,
                         text_anchor=text_anchor, creation=creation, z=z, **styling_kwargs)

    def __repr__(self):
        return f'Integer({self._tracker.at_time(0):.0f})'

class Trace(VObject):
    """Follows a point every dt and renders as a polyline."""
    def __init__(self, point, start: float = 0, end: float | None = None, dt=1/60, z: float = 0, **styling_kwargs):
        super().__init__(creation=start, z=z)
        self.start = start
        self.end = end
        self.dt = max(dt, 1e-9)
        self.p = point
        self.styling = style.Styling(styling_kwargs, creation=start, stroke='#fff', stroke_width=DEFAULT_STROKE_WIDTH)
        self._vert_cache = []
        self._str_parts = []  # List of "x,y" strings

    def _extra_attrs(self):
        return [self.p]

    def snap_points(self, time):
        """Return the current traced point position as a snap point."""
        pos = self.p.at_time(time)
        return [(float(pos[0]), float(pos[1]))]

    def shift(self, dx=0, dy=0, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Shift via styling transform (Trace points are immutable)."""
        if end is None:
            self.styling.dx.add_onward(start, dx)
            self.styling.dy.add_onward(start, dy)
        else:
            d = max(end - start, 1e-9)
            self.styling.dx.add_onward(start, _ramp(start, d, dx, easing), last_change=end)
            self.styling.dy.add_onward(start, _ramp(start, d, dy, easing), last_change=end)
        return self

    def path(self, time):
        """Return the SVG path data string for the traced polyline."""
        verts = self.vertices(time)
        if not verts:
            return ''
        parts = [f'M {verts[0][0]},{verts[0][1]}']
        parts.extend(f'L {x},{y}' for x, y in verts[1:])
        return ' '.join(parts)

    def vertices(self, time):
        """Return the list of sampled (x, y) vertices up to the given time."""
        steps = self._steps(time)
        verts = self._vert_cache[:steps]
        t = self.start + len(verts) * self.dt
        prev_len = len(verts)
        for _ in range(steps - prev_len):
            verts.append(self.p.at_time(t))
            t += self.dt
        if len(verts) > prev_len:
            self._vert_cache = verts
            self._str_parts.extend(f'{x},{y}' for x, y in verts[prev_len:])
        return verts

    def _steps(self, time):
        end = min(self.end, time) if self.end is not None else time
        return int((end - self.start) / self.dt)

    def to_svg(self, time):
        """Return the SVG <polyline> element string for the trace."""
        self.vertices(time)
        steps = self._steps(time)
        if steps == 0:
            return ''
        pts = ' '.join(self._str_parts[:steps])
        cur = self.p.at_time(time)
        return f"<polyline points='{pts} {cur[0]},{cur[1]}'{self.styling.svg_style(time)} />"

    def to_polygon(self, time):
        """Convert the traced vertices into a Polygon object."""
        return Polygon(*self.vertices(time), creation=time, z=self.z.at_time(time), **self.styling.kwargs())

    def __repr__(self):
        return f'Trace({len(self._vert_cache)} points)'

class Path(VObject):
    """SVG path element with a 'd' attribute."""
    def __init__(self, path, x=0, y=0, creation: float = 0, z: float = 0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        self.d = attributes.String(creation, path)
        self.styling = style.Styling(styling_kwargs, creation=creation, stroke='#fff')
        self.styling.dx.add_onward(creation, lambda t: x * self.styling.scale_x.at_time(t))
        self.styling.dy.add_onward(creation, lambda t: y * self.styling.scale_y.at_time(t))

    def _extra_attrs(self):
        return [self.d]

    def snap_points(self, time):
        """Return the four corners of the path bounding box as snap points."""
        d = self.d.at_time(time)
        if d:
            xmin, xmax, ymin, ymax = path_bbox(d)
            return [(float(xmin), float(ymin)), (float(xmax), float(ymin)),
                    (float(xmax), float(ymax)), (float(xmin), float(ymax))]
        return []

    def shift(self, dx=0, dy=0, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Shift via transform styling, accounting for current rotation."""
        rot = self.styling.rotation.at_time(0)
        if rot[0] != 0:
            dx, dy = _rotate_point(dx, dy, rot[1], rot[2], -rot[0] * math.pi / 180)
        if end is None:
            self.styling.dx.add_onward(start, dx)
            self.styling.dy.add_onward(start, dy)
        else:
            d = max(end - start, 1e-9)
            self.styling.dx.add_onward(start, _ramp(start, d, dx, easing), last_change=end)
            self.styling.dy.add_onward(start, _ramp(start, d, dy, easing), last_change=end)
        return self

    def __repr__(self):
        d = self.d.at_time(0)
        short = d[:30] + '...' if len(d) > 30 else d
        return f"Path(d='{short}')"

    _STYLE_NAMES = ('fill_opacity', 'stroke_width', 'stroke_opacity', 'opacity',
                     'stroke_dasharray', 'stroke_dashoffset', 'stroke_linecap',
                     'stroke_linejoin', 'fill_rule')

    def _copy_style(self, time: float = 0):
        """Return a dict of styling kwargs capturing this path's style at *time*."""
        kw = {n: getattr(self.styling, n).at_time(time) for n in self._STYLE_NAMES}
        for n in ('fill', 'stroke'):
            kw[n] = getattr(self.styling, n).time_func(time)
        return kw

    @staticmethod
    def _parse_path_lazy(d):
        try:
            from svgpathtools import parse_path
        except ImportError:
            raise ImportError("svgpathtools is required for path operations")
        return parse_path(d)

    def get_length(self, time: float = 0):
        """Return the total length of the path."""
        d = self.d.at_time(time)
        return self._parse_path_lazy(d).length() if d else 0.0

    def point_from_proportion(self, proportion, time: float = 0):
        """Return (x, y) at a proportional distance along the path (0-1)."""
        d = self.d.at_time(time)
        if not d:
            return (0, 0)
        parsed = self._parse_path_lazy(d)
        total = parsed.length()
        if total == 0:
            pt = parsed.point(0)
            return (pt.real, pt.imag)
        pt = parsed.point(parsed.ilength(total * _clamp01(proportion)))
        return (pt.real, pt.imag)

    def tangent_at(self, proportion, time: float = 0):
        """Return the unit tangent direction (dx, dy) at a proportional distance along the path."""
        d = self.d.at_time(time)
        if not d:
            return (0.0, 0.0)
        parsed = self._parse_path_lazy(d)
        total = parsed.length()
        if total == 0:
            return (0.0, 0.0)
        t_param = parsed.ilength(total * _clamp01(proportion))
        # derivative() returns a complex number (dx + dy*j)
        deriv = parsed.derivative(t_param)
        dx, dy = deriv.real, deriv.imag
        mag = math.hypot(dx, dy)
        if mag < 1e-12:
            return (0.0, 0.0)
        return (dx / mag, dy / mag)

    def trim(self, t_start: float = 0.0, t_end: float = 1.0, time: float = 0):
        """Return a new Path representing the sub-path between proportions."""
        d = self.d.at_time(time)
        if not d:
            return Path('')
        parsed = self._parse_path_lazy(d)
        total = parsed.length()
        if total == 0:
            return Path(d)
        t_start = _clamp01(t_start)
        t_end = _clamp01(t_end)
        if t_start >= t_end:
            return Path('')
        T0 = parsed.ilength(total * t_start)
        T1 = parsed.ilength(total * t_end)
        sub = parsed.cropped(T0, T1)
        return Path(sub.d(), **self._copy_style(time))

    def reverse(self, time: float = 0):
        """Return a new Path with the segments reversed."""
        d = self.d.at_time(time)
        if not d:
            return Path('')
        parsed = self._parse_path_lazy(d)
        reversed_d = parsed.reversed().d()
        return Path(reversed_d, **self._copy_style(time))

    def path(self, time):
        """Return the SVG path data string."""
        return self.d.at_time(time)

    def to_svg(self, time):
        """Return the SVG <path> element string."""
        return f"<path d='{self.d.at_time(time)}'{self.styling.svg_style(time)} />"

    @classmethod
    def from_points(cls, points, closed=False, smooth=False, **kwargs):
        """Create a Path from a list of (x, y) points."""
        pts = list(points)
        if not pts:
            return cls('', **kwargs)
        if len(pts) == 1:
            x, y = pts[0]
            return cls(f'M{x},{y}', **kwargs)

        if not smooth:
            parts = [f'M{pts[0][0]},{pts[0][1]}']
            parts.extend(f'L{x},{y}' for x, y in pts[1:])
            if closed:
                parts.append('Z')
            return cls(' '.join(parts), **kwargs)

        # Smooth: Catmull-Rom → cubic Bezier conversion
        n = len(pts)
        parts = [f'M{pts[0][0]},{pts[0][1]}']
        for i in range(n - 1 if not closed else n):
            # Catmull-Rom: p0=prev, p1=current, p2=next, p3=after-next
            if closed:
                p0 = pts[(i - 1) % n]
                p1 = pts[i % n]
                p2 = pts[(i + 1) % n]
                p3 = pts[(i + 2) % n]
            else:
                p0 = pts[max(i - 1, 0)]
                p1 = pts[i]
                p2 = pts[i + 1]
                p3 = pts[min(i + 2, n - 1)]

            # Convert to cubic Bezier control points (tension=0.5)
            alpha = 0.5
            cp1x = p1[0] + (p2[0] - p0[0]) * alpha / 3
            cp1y = p1[1] + (p2[1] - p0[1]) * alpha / 3
            cp2x = p2[0] - (p3[0] - p1[0]) * alpha / 3
            cp2y = p2[1] - (p3[1] - p1[1]) * alpha / 3
            if closed and i == n - 1:
                ex, ey = pts[0]
            else:
                ex, ey = p2
            parts.append(f'C{cp1x},{cp1y} {cp2x},{cp2y} {ex},{ey}')
        if closed:
            parts.append('Z')
        return cls(' '.join(parts), **kwargs)

class Image(VObject):
    """SVG <image> element."""
    def __init__(self, href, x=0, y=0, width=1, height=1, creation: float = 0, z: float = 0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        self.href = href
        self.x = attributes.Real(creation, x)
        self.y = attributes.Real(creation, y)
        self.width = attributes.Real(creation, width)
        self.height = attributes.Real(creation, height)
        self.styling = style.Styling(styling_kwargs, creation=creation, stroke_width=0)

    def _extra_attrs(self):
        return [self.x, self.y, self.width, self.height]

    def _shift_reals(self):
        return [(self.x, self.y)]

    def path(self, time):
        """Return an SVG path tracing the image bounding rectangle."""
        x, y = self.x.at_time(time), self.y.at_time(time)
        w, h = self.width.at_time(time), self.height.at_time(time)
        return f'M{x},{y}L{x+w},{y}L{x+w},{y+h}L{x},{y+h}Z'

    def bbox(self, time: float = 0):
        """Return the bounding box of the image."""
        x, y = self.x.at_time(time), self.y.at_time(time)
        w, h = self.width.at_time(time), self.height.at_time(time)
        return self._bbox_from_points([(x,y),(x+w,y),(x+w,y+h),(x,y+h)], time) or super().bbox(time)

    def __repr__(self):
        return f'Image({self.width.at_time(0):.0f}x{self.height.at_time(0):.0f})'

    def to_svg(self, time):
        """Return the SVG <image> element string."""
        return (f"<image href='{self.href}' x='{self.x.at_time(time)}' y='{self.y.at_time(time)}'"
                f" width='{self.width.at_time(time)}' height='{self.height.at_time(time)}'"
                f"{self.styling.svg_style(time)} />")

class Arc(VObject):
    """SVG arc segment defined by center, radius, and start/end angles (degrees)."""
    def __init__(self, cx: float = ORIGIN[0], cy: float = ORIGIN[1], r: float = 120, start_angle: float = 0, end_angle: float = 90,
                 creation: float = 0, z: float = 0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        self.cx = attributes.Real(creation, cx)
        self.cy = attributes.Real(creation, cy)
        self.r = attributes.Real(creation, r)
        self.start_angle = attributes.Real(creation, start_angle)
        self.end_angle = attributes.Real(creation, end_angle)
        self.styling = style.Styling(styling_kwargs, creation=creation,
                                     stroke='#fff', stroke_width=DEFAULT_STROKE_WIDTH, fill_opacity=0)

    def _extra_attrs(self):
        return [self.cx, self.cy, self.r, self.start_angle, self.end_angle]

    def _shift_reals(self):
        return [(self.cx, self.cy)]

    def snap_points(self, time):
        """Return the arc center position as a snap point."""
        return [(float(self.cx.at_time(time)), float(self.cy.at_time(time)))]

    def bbox(self, time: float = 0):
        """Return the bounding box of the arc including cardinal extremes."""
        cx, cy, r = self.cx.at_time(time), self.cy.at_time(time), self.r.at_time(time)
        sa, ea = self.start_angle.at_time(time), self.end_angle.at_time(time)
        sa_rad, ea_rad = math.radians(sa), math.radians(ea)
        pts = [(cx + r * math.cos(sa_rad), cy - r * math.sin(sa_rad)),
               (cx + r * math.cos(ea_rad), cy - r * math.sin(ea_rad))]
        # Add cardinal extremes that fall within the arc sweep
        lo = sa % 360
        span = (ea - sa) % 360 or 360
        for card_deg, px, py in [(0, cx+r, cy), (90, cx, cy-r), (180, cx-r, cy), (270, cx, cy+r)]:
            if (card_deg - lo) % 360 < span:
                pts.append((px, py))
        return self._bbox_from_points(pts, time) or super().bbox(time)

    def path(self, time):
        """Return the SVG path data string for the arc."""
        cx, cy, r = self.cx.at_time(time), self.cy.at_time(time), self.r.at_time(time)
        sa, ea = self.start_angle.at_time(time), self.end_angle.at_time(time)
        sa_rad, ea_rad = math.radians(sa), math.radians(ea)
        x1, y1 = cx + r * math.cos(sa_rad), cy - r * math.sin(sa_rad)
        x2, y2 = cx + r * math.cos(ea_rad), cy - r * math.sin(ea_rad)
        large = 1 if abs(ea - sa) % 360 > 180 else 0
        sweep = 0 if ea > sa else 1
        return f'M{x1},{y1}A{r},{r} 0 {large},{sweep} {x2},{y2}'

    def get_start_point(self, time: float = 0):
        """Return the (x, y) position at the start of the arc."""
        return self.point_at_angle(self.start_angle.at_time(time), time)

    def get_end_point(self, time: float = 0):
        """Return the (x, y) position at the end of the arc."""
        return self.point_at_angle(self.end_angle.at_time(time), time)

    def get_sweep(self, time: float = 0):
        """Return the total sweep angle in degrees."""
        return abs(self.end_angle.at_time(time) - self.start_angle.at_time(time))

    def get_arc_length(self, time: float = 0):
        """Return the arc length (r * angle_in_radians)."""
        return self.r.at_time(time) * math.radians(self.get_sweep(time))

    def get_chord_length(self, time: float = 0):
        """Return the length of the chord from start point to end point."""
        p1 = self.get_start_point(time)
        p2 = self.get_end_point(time)
        return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

    def get_sagitta(self, time: float = 0):
        """Return the sagitta (height of the arc segment from chord to arc)."""
        r = self.r.at_time(time)
        half_angle = math.radians(self.get_sweep(time) / 2)
        return r * (1 - math.cos(half_angle))

    def tangent_at(self, degrees, length=100, time: float = 0, **kwargs):
        """Return a Line tangent to the arc at the given angle (degrees)."""
        px, py = self.point_at_angle(degrees, time)
        rad = math.radians(degrees)
        # Tangent is perpendicular to radius: (-sin, -cos) in SVG coords
        tx, ty = -math.sin(rad), -math.cos(rad)
        half = length / 2
        return Line(x1=px - tx * half, y1=py + ty * half,
                    x2=px + tx * half, y2=py - ty * half, **kwargs)

    def point_at_angle(self, degrees, time: float = 0):
        """Return (x, y) on the arc at the given angle (degrees, CCW from right)."""
        cx, cy = self.cx.at_time(time), self.cy.at_time(time)
        r = self.r.at_time(time)
        rad = math.radians(degrees)
        return (cx + r * math.cos(rad), cy - r * math.sin(rad))

    def set_radius(self, value, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Animate or set the arc radius."""
        _set_attr(self.r, start, end, value, easing)
        return self

    def set_angles(self, start_angle=None, end_angle=None, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Animate or set the arc start/end angles (degrees)."""
        if start_angle is not None:
            _set_attr(self.start_angle, start, end, start_angle, easing)
        if end_angle is not None:
            _set_attr(self.end_angle, start, end, end_angle, easing)
        return self

    def animate_sweep(self, target_angle, start: float = 0, end: float | None = None, easing=None):
        """Animate the end angle of this arc to *target_angle* (degrees)."""
        if easing is None:
            easing = easings.smooth
        _set_attr(self.end_angle, start, end, target_angle, easing)
        return self

    def get_midpoint(self, time: float = 0):
        """Return the point at the midpoint angle of the arc."""
        mid = (self.start_angle.at_time(time) + self.end_angle.at_time(time)) / 2
        return self.point_at_angle(mid, time)

    get_midpoint_on_arc = get_midpoint

    def complement(self, time: float = 0, **kwargs):
        """Return an Arc spanning the complementary angle (remaining portion of the circle)."""
        ea = self.end_angle.at_time(time)
        sa = self.start_angle.at_time(time)
        return Arc(cx=self.cx.at_time(time), cy=self.cy.at_time(time),
                   r=self.r.at_time(time), start_angle=ea, end_angle=sa + 360, **kwargs)

    def to_wedge(self, time: float = 0, **kwargs):
        """Return a :class:`Wedge` with the same geometry as this arc at *time*."""
        return Wedge(
            cx=self.cx.at_time(time),
            cy=self.cy.at_time(time),
            r=self.r.at_time(time),
            start_angle=self.start_angle.at_time(time),
            end_angle=self.end_angle.at_time(time),
            **kwargs,
        )

    def split_into(self, n=2, time: float = 0, **kwargs):
        """Split this arc into *n* equal sub-arcs."""
        if n < 1:
            n = 1
        cx = self.cx.at_time(time)
        cy = self.cy.at_time(time)
        r = self.r.at_time(time)
        sa = self.start_angle.at_time(time)
        ea = self.end_angle.at_time(time)
        step = (ea - sa) / n
        arcs = []
        for i in range(n):
            a1 = sa + i * step
            a2 = sa + (i + 1) * step
            arcs.append(Arc(cx=cx, cy=cy, r=r, start_angle=a1, end_angle=a2, **kwargs))
        return arcs

    def contains_point(self, px, py, time: float = 0, tol=2):
        """Return True if (px, py) lies on the arc within tolerance."""
        cx = self.cx.at_time(time)
        cy = self.cy.at_time(time)
        r = self.r.at_time(time)
        # Check distance to center equals radius (within tolerance)
        dist = math.hypot(px - cx, py - cy)
        if abs(dist - r) > tol:
            return False
        # Check angle is within arc sweep
        # Arc uses standard math angles (CCW from right) but SVG y-axis is
        # flipped, so point_at_angle uses cy - r*sin.  To recover the math
        # angle from an SVG point we negate the y-component.
        angle = math.degrees(math.atan2(-(py - cy), px - cx)) % 360
        start = self.start_angle.at_time(time) % 360
        end = self.end_angle.at_time(time) % 360
        if start <= end:
            return start <= angle <= end
        else:
            return angle >= start or angle <= end

    @classmethod
    def from_three_points(cls, p1, p2, p3, **kwargs):
        """Create an Arc through three points (x, y tuples)."""
        ux, uy, r = _circumcenter(p1, p2, p3)
        ax, ay = p1; bx, by = p2; cx, cy = p3
        # Compute angles (note: SVG y-axis is flipped, so use -(y - uy))
        a1 = math.degrees(math.atan2(-(ay - uy), ax - ux))
        a2_angle = math.degrees(math.atan2(-(by - uy), bx - ux))
        a3 = math.degrees(math.atan2(-(cy - uy), cx - ux))
        # Normalize angles to [0, 360)
        a1 = a1 % 360
        a2_angle = a2_angle % 360
        a3 = a3 % 360

        def _angle_between_ccw(start, end):
            return (end - start) % 360

        ccw_12 = _angle_between_ccw(a1, a2_angle)
        ccw_13 = _angle_between_ccw(a1, a3)
        if ccw_12 < ccw_13:
            # a2 is between a1 and a3 counterclockwise
            return cls(r=r, start_angle=a1, end_angle=a1 + ccw_13, cx=ux, cy=uy, **kwargs)
        else:
            # Go clockwise: a1 to a3 the other way
            cw_13 = 360 - ccw_13
            return cls(r=r, start_angle=a1, end_angle=a1 - cw_13, cx=ux, cy=uy, **kwargs)

    def get_chord(self, time: float = 0, **kwargs):
        """Return a Line connecting the start and end points of the arc."""
        x1, y1 = self.get_start_point(time)
        x2, y2 = self.get_end_point(time)
        return Line(x1=x1, y1=y1, x2=x2, y2=y2, **kwargs)

    def __repr__(self):
        return f'Arc(r={self.r.at_time(0):.0f}, {self.start_angle.at_time(0):.0f}°-{self.end_angle.at_time(0):.0f}°)'

    def to_svg(self, time):
        """Return the SVG <path> element string for the arc."""
        return f"<path d='{self.path(time)}'{self.styling.svg_style(time)} />"

class Wedge(Arc):
    """Arc that closes through the center (pie/wedge shape)."""
    def __init__(self, cx: float = ORIGIN[0], cy: float = ORIGIN[1], r: float = 120, start_angle: float = 0, end_angle: float = 90,
                 creation: float = 0, z: float = 0, **styling_kwargs):
        super().__init__(cx=cx, cy=cy, r=r, start_angle=start_angle, end_angle=end_angle,
                         creation=creation, z=z, **({'fill_opacity': 0.7, 'stroke': '#fff', 'stroke_width': DEFAULT_STROKE_WIDTH} | styling_kwargs))

    def get_area(self, time: float = 0):
        """Return the area of the wedge (0.5 * r^2 * sweep_in_radians)."""
        r = self.r.at_time(time)
        sweep = abs(self.end_angle.at_time(time) - self.start_angle.at_time(time))
        return 0.5 * r * r * math.radians(sweep)

    def to_arc(self, time: float = 0, **kwargs):
        """Return an :class:`Arc` with the same geometry as this wedge at *time*."""
        return Arc(
            cx=self.cx.at_time(time),
            cy=self.cy.at_time(time),
            r=self.r.at_time(time),
            start_angle=self.start_angle.at_time(time),
            end_angle=self.end_angle.at_time(time),
            **kwargs,
        )

    def __repr__(self):
        return f'Wedge(r={self.r.at_time(0):.0f}, {self.start_angle.at_time(0):.0f}\u00b0-{self.end_angle.at_time(0):.0f}\u00b0)'

    def path(self, time):
        """Return the SVG path data for the wedge (arc closed through center)."""
        return super().path(time) + f'L{self.cx.at_time(time)},{self.cy.at_time(time)}Z'

class Annulus(VObject):
    """Ring/donut shape defined by inner and outer radius."""
    def __init__(self, inner_radius: float = 60, outer_radius: float = 120, cx: float = ORIGIN[0], cy: float = ORIGIN[1],
                 creation: float = 0, z: float = 0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        self.c = attributes.Coor(creation, (cx, cy))
        self.inner_r = attributes.Real(creation, inner_radius)
        self.outer_r = attributes.Real(creation, outer_radius)
        self.styling = style.Styling(styling_kwargs, creation=creation,
                                     fill='#58C4DD', fill_opacity=0.7, stroke='#fff', stroke_width=DEFAULT_STROKE_WIDTH)

    def _extra_attrs(self):
        return [self.c, self.inner_r, self.outer_r]

    def _shift_coors(self):
        return [self.c]

    def snap_points(self, time):
        """Return the annulus center position as a snap point."""
        cx, cy = self.c.at_time(time)
        return [(float(cx), float(cy))]

    def bbox(self, time: float = 0):
        """Return the bounding box based on the outer radius."""
        cx, cy = self.c.at_time(time)
        r = self.outer_r.at_time(time)
        return self._bbox_from_points([(cx-r, cy-r), (cx+r, cy-r), (cx+r, cy+r), (cx-r, cy+r)], time) or super().bbox(time)

    def path(self, time):
        """Return the SVG path data for the annulus ring shape."""
        cx, cy = self.c.at_time(time)
        ri, ro = self.inner_r.at_time(time), self.outer_r.at_time(time)
        # Outer circle CW, then inner circle CCW (creates a ring with even-odd fill)
        return (f'M{cx-ro},{cy}a{ro},{ro} 0 1,0 {ro*2},0a{ro},{ro} 0 1,0 -{ro*2},0z'
                f'M{cx-ri},{cy}a{ri},{ri} 0 1,1 {ri*2},0a{ri},{ri} 0 1,1 -{ri*2},0z')

    def __repr__(self):
        return f'Annulus(inner={self.inner_r.at_time(0):.0f}, outer={self.outer_r.at_time(0):.0f})'

    def get_inner_radius(self, time: float = 0):
        """Return the inner radius at the given time."""
        return self.inner_r.at_time(time)

    def get_outer_radius(self, time: float = 0):
        """Return the outer radius at the given time."""
        return self.outer_r.at_time(time)

    def set_inner_radius(self, value, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Animate or set the inner radius."""
        _set_attr(self.inner_r, start, end, value, easing); return self

    def set_outer_radius(self, value, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Animate or set the outer radius."""
        _set_attr(self.outer_r, start, end, value, easing); return self

    def get_area(self, time: float = 0):
        """Return the area of the annulus (pi * (outer^2 - inner^2))."""
        ri, ro = self.inner_r.at_time(time), self.outer_r.at_time(time)
        return math.pi * (ro * ro - ri * ri)

    def set_radii(self, inner=None, outer=None, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Set inner and/or outer radius."""
        if inner is not None:
            self.set_inner_radius(inner, start, end, easing)
        if outer is not None:
            self.set_outer_radius(outer, start, end, easing)
        return self

    def to_svg(self, time):
        """Return the SVG <path> element string with even-odd fill rule."""
        return f"<path d='{self.path(time)}' fill-rule='evenodd'{self.styling.svg_style(time)} />"

class DashedLine(Line):
    """Line with a dashed stroke pattern."""
    def __init__(self, x1: float = 0, y1: float = 0, x2: float = 100, y2: float = 100, dash='10,5', creation: float = 0, z: float = 0, **styling_kwargs):
        super().__init__(x1=x1, y1=y1, x2=x2, y2=y2, creation=creation, z=z,
                         **({'stroke_dasharray': dash} | styling_kwargs))

    def __repr__(self):
        x1, y1, x2, y2 = self._ep(0)
        return f'DashedLine(({x1:.0f},{y1:.0f})->({x2:.0f},{y2:.0f}))'

    def set_dash_pattern(self, dash, gap=None, start: float = 0):
        """Set the dash pattern. If gap is None, gap = dash."""
        if gap is None:
            gap = dash
        self.styling.stroke_dasharray.set_onward(start, f'{dash},{gap}')
        return self

class BackgroundRectangle(Rectangle):
    """Semi-transparent rectangle behind a target object (useful for text backgrounds)."""
    def __init__(self, target, buff=SMALL_BUFF, creation: float = 0, z: float = -1, **styling_kwargs):
        bx, by, bw, bh = target.bbox(creation)
        style_kw = {'fill': '#000', 'fill_opacity': 0.75, 'stroke_width': 0} | styling_kwargs
        super().__init__(bw + 2*buff, bh + 2*buff, x=bx - buff, y=by - buff,
                         creation=creation, z=z, **style_kw)

    def __repr__(self):
        return 'BackgroundRectangle()'

class ScreenRectangle(Rectangle):
    """A rectangle with the canvas aspect ratio (16:9).
    height is derived from width automatically."""
    def __init__(self, width=480, creation: float = 0, z: float = 0, **kwargs):
        height = width * 9 / 16
        super().__init__(width=width, height=height, creation=creation, z=z, **kwargs)

    def __repr__(self):
        return 'ScreenRectangle()'

class ArcBetweenPoints(Arc):
    """Arc connecting two points, bulging by a given angle."""
    def __init__(self, start, end, angle=60, creation: float = 0, z: float = 0, **styling_kwargs):
        x1, y1 = start
        x2, y2 = end
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy) or 1
        # Compute radius from chord length and angle
        half_angle = math.radians(abs(angle) / 2)
        r = dist / (2 * math.sin(half_angle)) if half_angle > 1e-9 else dist * 1000
        # Perpendicular direction (pointing left of start→end)
        px, py = -dy / dist, dx / dist
        sign = 1 if angle > 0 else -1
        sagitta = r - r * math.cos(half_angle)
        cx = mx + sign * px * (r - sagitta)
        cy = my + sign * py * (r - sagitta)
        sa = math.degrees(math.atan2(-(y1 - cy), x1 - cx))
        ea = math.degrees(math.atan2(-(y2 - cy), x2 - cx))
        if angle > 0 and (ea - sa) % 360 > 180:
            sa, ea = ea, sa
        elif angle < 0 and (sa - ea) % 360 > 180:
            sa, ea = ea, sa
        super().__init__(cx=cx, cy=cy, r=r, start_angle=sa, end_angle=ea,
                         creation=creation, z=z, **styling_kwargs)

    def __repr__(self):
        return 'ArcBetweenPoints()'

class Elbow(Lines):
    """Right-angle connector (L-shape) between two directions."""
    def __init__(self, cx=ORIGIN[0], cy=ORIGIN[1], width=40, height=40,
                 creation: float = 0, z: float = 0, **styling_kwargs):
        style_kw = {'stroke': '#fff', 'stroke_width': DEFAULT_STROKE_WIDTH, 'fill_opacity': 0} | styling_kwargs
        super().__init__(
            (cx + width, cy), (cx, cy), (cx, cy + height),
            creation=creation, z=z, **style_kw)

    def __repr__(self):
        return 'Elbow()'

class AnnularSector(Arc):
    """Sector of an annulus (ring wedge)."""
    def __init__(self, inner_radius=60, outer_radius=120, cx=ORIGIN[0], cy=ORIGIN[1],
                 start_angle=0, end_angle=90, creation: float = 0, z: float = 0, **styling_kwargs):
        super().__init__(cx=cx, cy=cy, r=outer_radius, start_angle=start_angle,
                         end_angle=end_angle, creation=creation, z=z,
                         **({'fill_opacity': 0.7, 'stroke': '#fff', 'stroke_width': DEFAULT_STROKE_WIDTH} | styling_kwargs))
        self.inner_r = attributes.Real(creation, inner_radius)

    def __repr__(self):
        return 'AnnularSector()'

    def _extra_attrs(self):
        return super()._extra_attrs() + [self.inner_r]

    def path(self, time):
        """Return the SVG path data for the annular sector."""
        cx, cy, ro = self.cx.at_time(time), self.cy.at_time(time), self.r.at_time(time)
        ri = self.inner_r.at_time(time)
        sa, ea = self.start_angle.at_time(time), self.end_angle.at_time(time)
        sa_rad, ea_rad = math.radians(sa), math.radians(ea)
        cos_sa, sin_sa = math.cos(sa_rad), math.sin(sa_rad)
        cos_ea, sin_ea = math.cos(ea_rad), math.sin(ea_rad)
        # Outer arc
        ox1, oy1 = cx + ro * cos_sa, cy - ro * sin_sa
        ox2, oy2 = cx + ro * cos_ea, cy - ro * sin_ea
        # Inner arc (reversed)
        ix1, iy1 = cx + ri * cos_ea, cy - ri * sin_ea
        ix2, iy2 = cx + ri * cos_sa, cy - ri * sin_sa
        large = 1 if abs(ea - sa) % 360 > 180 else 0
        sweep_out = 0 if ea > sa else 1
        sweep_in = 1 - sweep_out
        return (f'M{ox1},{oy1}A{ro},{ro} 0 {large},{sweep_out} {ox2},{oy2}'
                f'L{ix1},{iy1}A{ri},{ri} 0 {large},{sweep_in} {ix2},{iy2}Z')

    def set_inner_radius(self, value, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Animate or set the inner radius of the annular sector."""
        _set_attr(self.inner_r, start, end, value, easing)
        return self

    def get_area(self, time: float = 0):
        """Return the area of the annular sector."""
        ri = self.inner_r.at_time(time)
        ro = self.r.at_time(time)
        return 0.5 * math.radians(self.get_sweep(time)) * (ro * ro - ri * ri)

    def to_svg(self, time):
        """Return the SVG <path> element string for the annular sector."""
        return f"<path d='{self.path(time)}'{self.styling.svg_style(time)} />"

class ArcPolygon(VObject):
    """Polygon whose edges are arcs instead of straight lines.

    *vertices*: list of (x, y) tuples.
    *arc_angles*: angle of each arc (scalar for all, or list per edge).
      Positive → bulge left of travel direction, negative → right.
      0 = straight line segment.
    """
    def __init__(self, *vertices, arc_angles=30, creation: float = 0, z: float = 0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        if len(vertices) < 3:
            raise ValueError("ArcPolygon requires at least 3 vertices")
        self._verts = list(vertices)
        self._angles = ([arc_angles] * len(vertices)
                        if isinstance(arc_angles, (int, float))
                        else list(arc_angles))
        defaults = dict(stroke='#fff', stroke_width=DEFAULT_STROKE_WIDTH, fill_opacity=0.3)
        self.styling = style.Styling(styling_kwargs, creation=creation, **defaults)

    def __repr__(self):
        return f'ArcPolygon({len(self._verts)} vertices)'

    def path(self, time):
        """Return the SVG path data for the arc polygon."""
        verts = self._verts
        n = len(verts)
        parts = [f'M{verts[0][0]:.1f},{verts[0][1]:.1f}']
        for i in range(n):
            x1, y1 = verts[i]
            x2, y2 = verts[(i + 1) % n]
            angle = self._angles[i % len(self._angles)]
            if abs(angle) < 0.1:
                parts.append(f'L{x2:.1f},{y2:.1f}')
            else:
                dist = math.hypot(x2 - x1, y2 - y1) or 1
                half = math.radians(abs(angle) / 2)
                r = dist / (2 * math.sin(half)) if half > 1e-9 else dist * 1000
                large = 1 if abs(angle) > 180 else 0
                sweep = 0 if angle > 0 else 1
                parts.append(f'A{r:.1f},{r:.1f} 0 {large},{sweep} {x2:.1f},{y2:.1f}')
        parts.append('Z')
        return ''.join(parts)

    def to_svg(self, time):
        """Return the SVG <path> element string for the arc polygon."""
        return f"<path d='{self.path(time)}'{self.styling.svg_style(time)} />"


class CubicBezier(VObject):
    """Cubic Bezier curve from four control points."""
    def __init__(self, p0=(860, 540), p1=(910, 440), p2=(1010, 440), p3=(1060, 540),
                 creation: float = 0, z: float = 0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        self.p0 = attributes.Coor(creation, p0)
        self.p1 = attributes.Coor(creation, p1)
        self.p2 = attributes.Coor(creation, p2)
        self.p3 = attributes.Coor(creation, p3)
        defaults = dict(stroke='#fff', stroke_width=DEFAULT_STROKE_WIDTH, fill_opacity=0)
        self.styling = style.Styling(styling_kwargs, creation=creation, **defaults)

    def _extra_attrs(self):
        return [self.p0, self.p1, self.p2, self.p3]

    def _shift_coors(self):
        return [self.p0, self.p1, self.p2, self.p3]

    def __repr__(self):
        p0 = self.p0.at_time(0)
        p3 = self.p3.at_time(0)
        return f'CubicBezier(({p0[0]:.0f},{p0[1]:.0f})->({p3[0]:.0f},{p3[1]:.0f}))'

    def snap_points(self, time):
        """Return the start and end control points as snap points."""
        return [self.p0.at_time(time), self.p3.at_time(time)]

    def bbox(self, time: float = 0):
        """Return the bounding box enclosing all four control points."""
        pts = [self.p0.at_time(time), self.p1.at_time(time),
               self.p2.at_time(time), self.p3.at_time(time)]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        x_min, x_max = min(xs), max(xs)
        y_min, y_max = min(ys), max(ys)
        return self._bbox_from_points([(x_min, y_min), (x_max, y_max)], time) or (x_min, y_min, x_max - x_min, y_max - y_min)

    def _cps(self, time):
        """Return all four control point coordinates at time."""
        return (*self.p0.at_time(time), *self.p1.at_time(time),
                *self.p2.at_time(time), *self.p3.at_time(time))

    def path(self, time):
        """Return the SVG path data string for the cubic Bezier curve."""
        x0, y0, x1, y1, x2, y2, x3, y3 = self._cps(time)
        return f'M{x0},{y0}C{x1},{y1} {x2},{y2} {x3},{y3}'

    def point_at(self, t, time: float = 0):
        """Evaluate point on curve at parameter t (0 to 1)."""
        x0, y0, x1, y1, x2, y2, x3, y3 = self._cps(time)
        u = 1 - t
        return (u**3*x0 + 3*u**2*t*x1 + 3*u*t**2*x2 + t**3*x3,
                u**3*y0 + 3*u**2*t*y1 + 3*u*t**2*y2 + t**3*y3)

    def tangent_at(self, t, time: float = 0):
        """Return the unit tangent direction (dx, dy) at parameter t."""
        x0, y0, x1, y1, x2, y2, x3, y3 = self._cps(time)
        u = 1 - t
        dx = 3*u*u*(x1-x0) + 6*u*t*(x2-x1) + 3*t*t*(x3-x2)
        dy = 3*u*u*(y1-y0) + 6*u*t*(y2-y1) + 3*t*t*(y3-y2)
        mag = math.hypot(dx, dy)
        return (dx / mag, dy / mag) if mag > 1e-9 else (1.0, 0.0)

    def to_svg(self, time):
        """Return the SVG <path> element string for the cubic Bezier curve."""
        return f"<path d='{self.path(time)}'{self.styling.svg_style(time)} />"

class _TextBlockMixin:
    """Shared position/path/init methods for Paragraph, BulletedList, NumberedList."""

    def _init_block(self, items, x, y, font_size, line_spacing, creation, z, styling_kwargs):
        super().__init__(creation=creation, z=z)
        self.items = list(items)
        self.x = attributes.Real(creation, x)
        self.y = attributes.Real(creation, y)
        self.font_size = font_size
        self.line_spacing = line_spacing
        self.styling = style.Styling(styling_kwargs, creation=creation, fill='#fff', stroke_width=0)

    def _extra_attrs(self):
        return [self.x, self.y]

    def _shift_reals(self):
        return [(self.x, self.y)]

    def snap_points(self, time):
        """Return the text block origin as a snap point."""
        return [(self.x.at_time(time), self.y.at_time(time))]

    def path(self, time):
        """Return an empty path (text blocks have no geometric path)."""
        return ''

    def _list_bbox(self, time, indent=0):
        x, y = self.x.at_time(time), self.y.at_time(time)
        max_chars = max((len(item) for item in self.items), default=0)
        w = indent + max_chars * self.font_size * CHAR_WIDTH_FACTOR
        h = len(self.items) * self.font_size * self.line_spacing
        return (x, y - self.font_size, w, h)

    def bbox(self, time: float = 0):
        """Return the bounding box of the text block."""
        return self._list_bbox(time, getattr(self, 'indent', 0))

    def _render_list_svg(self, time, label_func):
        """Render a labelled list: *label_func(i)* returns the label string for item *i*."""
        x, y = self.x.at_time(time), self.y.at_time(time)
        st = self.styling.svg_style(time)
        parts = []
        for i, item in enumerate(self.items):
            ly = y + i * self.font_size * self.line_spacing
            parts.append(f"<text x='{x}' y='{ly}' font-size='{self.font_size}'{st}>{label_func(i)}</text>")
            parts.append(f"<text x='{x + self.indent}' y='{ly}' font-size='{self.font_size}'{st}>{_xml_escape(item)}</text>")
        return '\n'.join(parts)

class Paragraph(_TextBlockMixin, VObject):
    """Multi-line text with alignment and line spacing."""
    def __init__(self, *lines, x=ORIGIN[0], y=ORIGIN[1], font_size=36, alignment='left',
                 line_spacing=1.4, creation: float = 0, z: float = 0, **styling_kwargs):
        self._init_block(lines, x, y, font_size, line_spacing, creation, z, styling_kwargs)
        self.alignment = alignment

    def __repr__(self):
        return f'Paragraph({len(self.items)} lines)'

    @property
    def lines(self):
        """Return the list of text lines."""
        return self.items

    @lines.setter
    def lines(self, val):
        """Set the list of text lines."""
        self.items = val

    def bbox(self, time: float = 0):
        """Return the bounding box adjusted for text alignment."""
        x, y, w, h = self._list_bbox(time)
        if self.alignment == 'center':
            return (x - w / 2, y, w, h)
        if self.alignment == 'right':
            return (x - w, y, w, h)
        return (x, y, w, h)

    def to_svg(self, time):
        """Return the SVG markup for the paragraph lines."""
        x, y = self.x.at_time(time), self.y.at_time(time)
        anchor = {'left': 'start', 'center': 'middle', 'right': 'end'}[self.alignment]
        st = self.styling.svg_style(time)
        parts = []
        for i, line in enumerate(self.items):
            ly = y + i * self.font_size * self.line_spacing
            parts.append(f"<text x='{x}' y='{ly}' text-anchor='{anchor}' "
                         f"font-size='{self.font_size}'{st}>{_xml_escape(line)}</text>")
        return '\n'.join(parts)

class BulletedList(_TextBlockMixin, VObject):
    """List of items with bullet points."""
    def __init__(self, *items, x=200, y=200, font_size=36, bullet='\u2022',
                 indent=40, line_spacing=1.6, creation: float = 0, z: float = 0, **styling_kwargs):
        self._init_block(items, x, y, font_size, line_spacing, creation, z, styling_kwargs)
        self.bullet = bullet
        self.indent = indent

    def __repr__(self):
        return f'BulletedList({len(self.items)} items)'

    def to_svg(self, time):
        """Return the SVG markup for the bulleted list."""
        esc = _xml_escape(self.bullet)
        return self._render_list_svg(time, lambda i: esc)

class NumberedList(_TextBlockMixin, VObject):
    """List of items with numeric labels (1. 2. 3. ...)."""
    def __init__(self, *items, x=200, y=200, font_size=36, indent=50,
                 line_spacing=1.6, start_number=1, creation: float = 0, z: float = 0, **styling_kwargs):
        self._init_block(items, x, y, font_size, line_spacing, creation, z, styling_kwargs)
        self.indent = indent
        self.start_number = start_number

    def __repr__(self):
        return f'NumberedList({len(self.items)} items)'

    def to_svg(self, time):
        """Return the SVG markup for the numbered list."""
        sn = self.start_number
        return self._render_list_svg(time, lambda i: f'{sn + i}.')

class FunctionGraph(Lines):
    """Plot a mathematical function as a polyline (no axes, ticks, or labels)."""
    def __init__(self, func, x_range=(-5, 5), y_range=None, num_points=200,
                 x=120, y=60, width=1440, height=840,
                 creation: float = 0, z: float = 0, **styling_kwargs):
        x_min, x_max = x_range
        y_lo, y_hi, _, clamped = _sample_function(
            func, x_min, x_max, y_range, num_points, x, y, width, height)
        style_kw = {'stroke': '#58C4DD', 'stroke_width': 5, 'fill_opacity': 0} | styling_kwargs
        super().__init__(*clamped, creation=creation, z=z, **style_kw)
        self._func = func
        self._x_min, self._x_max = x_min, x_max
        self._y_min, self._y_max = y_lo, y_hi
        self._px, self._py, self._pw, self._ph = x, y, width, height

    def __repr__(self):
        return f'FunctionGraph(x=[{self._x_min}, {self._x_max}])'

    def get_point_from_x(self, math_x):
        """Return (svg_x, svg_y) for a given math x coordinate."""
        yv = self._func(math_x)
        x_span = self._x_max - self._x_min or 1
        y_span = self._y_max - self._y_min or 1
        sx = self._px + (math_x - self._x_min) / x_span * self._pw
        sy = self._py + (1 - (yv - self._y_min) / y_span) * self._ph
        return (sx, sy)

    def get_slope_at(self, math_x, dx=1e-6):
        """Return the numerical derivative (in math coordinates) at math_x."""
        return (self._func(math_x + dx) - self._func(math_x - dx)) / (2 * dx)


# ---------------------------------------------------------------------------
# Fractals
# ---------------------------------------------------------------------------

def _koch_points(p1, p2, depth):
    """Recursively generate Koch curve points between p1 and p2."""
    if depth == 0:
        return [p1]
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    a = (p1[0] + dx / 3, p1[1] + dy / 3)
    b = (p1[0] + dx * 2 / 3, p1[1] + dy * 2 / 3)
    # Peak: rotate (a→b) by -60° around a
    cos60, sin60 = 0.5, math.sin(math.radians(60))
    peak = (a[0] + (b[0] - a[0]) * cos60 - (b[1] - a[1]) * sin60,
            a[1] + (b[0] - a[0]) * sin60 + (b[1] - a[1]) * cos60)
    return (_koch_points(p1, a, depth - 1) +
            _koch_points(a, peak, depth - 1) +
            _koch_points(peak, b, depth - 1) +
            _koch_points(b, p2, depth - 1))


class KochSnowflake(Polygon):
    """Koch snowflake fractal polygon.

    Parameters
    ----------
    cx, cy : float
        Center position.
    size : float
        Side length of the initial equilateral triangle.
    depth : int
        Recursion depth (0 = triangle, 3 is typical).
    """

    def __init__(self, cx=ORIGIN[0], cy=ORIGIN[1], size=400, depth=3,
                 creation: float = 0, z: float = 0, **styling_kwargs):
        h = size * math.sqrt(3) / 2
        # Equilateral triangle vertices (top, bottom-left, bottom-right)
        p1 = (cx, cy - h * 2 / 3)
        p2 = (cx - size / 2, cy + h / 3)
        p3 = (cx + size / 2, cy + h / 3)
        pts = (_koch_points(p1, p2, depth) +
               _koch_points(p2, p3, depth) +
               _koch_points(p3, p1, depth))
        style_kw = {'stroke': '#58C4DD', 'fill_opacity': 0.1, 'stroke_width': 2} | styling_kwargs
        super().__init__(*pts, creation=creation, z=z, **style_kw)

    def __repr__(self):
        return f'KochSnowflake({len(self.vertices)} pts)'


def _sierpinski_triangles(ax, ay, bx, by, cx, cy, depth):
    """Yield filled triangle vertex tuples for a Sierpinski triangle."""
    if depth == 0:
        yield ((ax, ay), (bx, by), (cx, cy))
        return
    mx_ab, my_ab = (ax + bx) / 2, (ay + by) / 2
    mx_bc, my_bc = (bx + cx) / 2, (by + cy) / 2
    mx_ca, my_ca = (cx + ax) / 2, (cy + ay) / 2
    yield from _sierpinski_triangles(ax, ay, mx_ab, my_ab, mx_ca, my_ca, depth - 1)
    yield from _sierpinski_triangles(mx_ab, my_ab, bx, by, mx_bc, my_bc, depth - 1)
    yield from _sierpinski_triangles(mx_ca, my_ca, mx_bc, my_bc, cx, cy, depth - 1)


class SierpinskiTriangle(VCollection):
    """Sierpinski triangle fractal.

    Parameters
    ----------
    cx, cy : float
        Center position.
    size : float
        Side length of the outer triangle.
    depth : int
        Recursion depth (0 = solid triangle, 5 is typical).
    """

    def __init__(self, cx=ORIGIN[0], cy=ORIGIN[1], size=500, depth=4,
                 creation: float = 0, z: float = 0, **styling_kwargs):
        h = size * math.sqrt(3) / 2
        ax, ay = cx, cy - h * 2 / 3
        bx, by = cx - size / 2, cy + h / 3
        cx_, cy_ = cx + size / 2, cy + h / 3
        style_kw = {'fill': '#58C4DD', 'fill_opacity': 0.8,
                     'stroke': '#58C4DD', 'stroke_width': 1} | styling_kwargs
        triangles = [Polygon(*tri, creation=creation, z=z, **style_kw)
                     for tri in _sierpinski_triangles(ax, ay, bx, by, cx_, cy_, depth)]
        super().__init__(*triangles, creation=creation, z=z)

    def __repr__(self):
        return f'SierpinskiTriangle({len(self.objects)} triangles)'


class Spiral(Lines):
    """Archimedean or logarithmic spiral.

    Parameters
    ----------
    cx, cy : float
        Center position.
    a : float
        Initial radius (distance from center at angle=0).
    b : float
        Growth rate per radian.
    turns : float
        Number of full turns.
    num_points : int
        Number of sample points.
    log_spiral : bool
        If True, use r = a * exp(b*theta) instead of r = a + b*theta.
    """

    def __init__(self, cx=ORIGIN[0], cy=ORIGIN[1], a=0, b=15, turns=5, num_points=500,
                 log_spiral=False, creation: float = 0, z: float = 0, **styling_kwargs):
        style_kw = {'stroke': '#58C4DD', 'fill_opacity': 0, 'stroke_width': 2} | styling_kwargs
        max_theta = turns * math.tau
        pts = []
        for i in range(num_points):
            theta = max_theta * i / (num_points - 1) if num_points > 1 else 0
            r = a * math.exp(b * theta) if log_spiral else a + b * theta
            pts.append((cx + r * math.cos(theta), cy + r * math.sin(theta)))
        super().__init__(*pts, creation=creation, z=z, **style_kw)
        self._cx, self._cy = cx, cy
        self._turns = turns

    def __repr__(self):
        return f'Spiral(turns={self._turns})'
