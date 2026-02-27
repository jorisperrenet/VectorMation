"""Shape classes: Polygon, Circle, Rectangle, Line, Text, Arc, etc."""
import math
from xml.sax.saxutils import escape as _xml_escape

import vectormation.easings as easings
import vectormation.attributes as attributes
import vectormation.style as style
from vectormation.pathbbox import path_bbox
from vectormation._constants import (
    SMALL_BUFF, DEFAULT_STROKE_WIDTH, DEFAULT_DOT_RADIUS, CHAR_WIDTH_FACTOR,
    _rotate_point, _sample_function, _distance, _normalize,
)
from vectormation._base import VObject


def _anim(attr, start, end, value, easing):
    """Set attr to value instantly at start, or animate to it by end."""
    if end is None:
        attr.set_onward(start, value)
    else:
        attr.move_to(start, end, value, easing=easing)


class Polygon(VObject):
    def __init__(self, *vertices, closed=True, z=0, creation=0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        self.closed = closed
        self.vertices = [attributes.Coor(creation, v) for v in vertices]
        defaults = dict(fill_opacity=0.7, stroke='#fff', stroke_width=DEFAULT_STROKE_WIDTH)
        if not closed:
            defaults = dict(stroke='#fff', stroke_width=DEFAULT_STROKE_WIDTH, fill_opacity=0)
        self.styling = style.Styling(styling_kwargs, creation=creation, **defaults)
        self._bbox_cache = None
        self._bbox_version = 0

    def _extra_attrs(self):
        return self.vertices

    def _shift_coors(self):
        return self.vertices

    def shift(self, *args, **kwargs):
        self._bbox_version += 1
        return super().shift(*args, **kwargs)

    def snap_points(self, time):
        return [(float(x), float(y)) for x, y in (v.at_time(time) for v in self.vertices)]

    def bbox(self, time):
        if self._bbox_cache and self._bbox_cache[0] == time and self._bbox_cache[1] == self._bbox_version:
            return self._bbox_cache[2]
        points = [v.at_time(time) for v in self.vertices]
        result = self._bbox_from_points(points, time) or super().bbox(time)
        self._bbox_cache = (time, self._bbox_version, result)
        return result

    def path(self, time):
        vert = [v.at_time(time) for v in self.vertices]
        parts = [f'M {vert[0][0]},{vert[0][1]}'] + [f'L {x},{y}' for x, y in vert[1:]]
        if self.closed:
            parts.append('Z')
        return ' '.join(parts)

    def to_svg(self, time):
        tag = 'polygon' if self.closed else 'polyline'
        pts = ' '.join(f'{x},{y}' for x, y in (v.at_time(time) for v in self.vertices))
        return f"<{tag} points='{pts}'{self.styling.svg_style(time)} />"


    def get_vertices(self, time=0):
        """Return a list of (x, y) tuples for each vertex."""
        return [(float(x), float(y)) for x, y in (v.at_time(time) for v in self.vertices)]

    def get_center(self, time=0):
        """Return the centroid (average of vertices)."""
        pts = self.get_vertices(time)
        if not pts:
            return (0.0, 0.0)
        n = len(pts)
        return (sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n)

    def centroid(self, time=0):
        """Return the geometric centroid (cx, cy) using the polygon centroid formula.

        For polygons with 3+ vertices this uses the area-weighted centroid
        formula which accounts for vertex distribution, unlike ``get_center``
        which simply averages the vertices.  For degenerate cases (0-2 vertices
        or near-zero area) the plain average is returned.

        Parameters
        ----------
        time:
            Animation time at which to read vertex positions.
        """
        pts = self.get_vertices(time)
        n = len(pts)
        if n == 0:
            return (0, 0)
        if n <= 2:
            return (sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n)
        cx = cy = signed_area = 0
        for i in range(n):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % n]
            cross = x0 * y1 - x1 * y0
            signed_area += cross
            cx += (x0 + x1) * cross
            cy += (y0 + y1) * cross
        signed_area *= 0.5
        if abs(signed_area) < 1e-10:
            return (sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n)
        cx /= (6 * signed_area)
        cy /= (6 * signed_area)
        return (cx, cy)

    def perimeter(self, time=0):
        """Return the perimeter (sum of edge lengths)."""
        pts = self.get_vertices(time)
        if len(pts) < 2:
            return 0.0
        total = sum(_distance(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1])
                    for i in range(len(pts) - 1))
        if self.closed and len(pts) > 2:
            total += _distance(pts[0][0], pts[0][1], pts[-1][0], pts[-1][1])
        return total

    def get_perimeter(self, time=0):
        """Return the perimeter (sum of all edge lengths).

        For a closed polygon this includes the closing edge from the last
        vertex back to the first.  For an open polyline only the segments
        between consecutive vertices are summed.

        Uses :func:`_distance` from :mod:`_constants`.

        Parameters
        ----------
        time:
            Animation time at which to read vertex positions.
        """
        return self.perimeter(time)

    def edge_lengths(self, time=0):
        """Return list of edge lengths."""
        pts = self.get_vertices(time)
        n = len(pts)
        if n < 2:
            return []
        lengths = []
        for i in range(n - 1):
            lengths.append(math.hypot(pts[i+1][0] - pts[i][0], pts[i+1][1] - pts[i][1]))
        if self.closed and n > 2:
            lengths.append(math.hypot(pts[0][0] - pts[-1][0], pts[0][1] - pts[-1][1]))
        return lengths

    def area(self, time=0):
        """Return the area using the shoelace formula (0 for open polylines)."""
        if not self.closed:
            return 0.0
        pts = self.get_vertices(time)
        n = len(pts)
        if n < 3:
            return 0.0
        return abs(sum(pts[i][0] * pts[(i+1) % n][1] - pts[(i+1) % n][0] * pts[i][1]
                       for i in range(n))) / 2

    def get_area(self, time=0):
        """Return the polygon's area (alias for area())."""
        return self.area(time)

    def signed_area(self, time=0):
        """Return the signed area using the shoelace formula.

        Positive for counter-clockwise winding, negative for clockwise
        (in standard math coordinates).  In SVG coordinates (y-down) the
        sign is flipped.
        """
        pts = self.get_vertices(time)
        n = len(pts)
        if n < 3:
            return 0
        total = 0
        for i in range(n):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % n]
            total += x0 * y1 - x1 * y0
        return total / 2

    def is_regular(self, tol=1e-3, time=0):
        """Return True if all edges have the same length (within tolerance).

        An open polyline is never considered regular.  A polygon with fewer
        than 3 vertices always returns False.

        Parameters
        ----------
        tol:
            Maximum allowed relative deviation from the mean edge length.
            Default is ``1e-3`` (0.1%).
        time:
            Animation time at which to evaluate vertex positions.

        Returns
        -------
        bool
        """
        if not self.closed:
            return False
        pts = self.get_vertices(time)
        n = len(pts)
        if n < 3:
            return False
        lengths = [_distance(pts[i][0], pts[i][1], pts[(i + 1) % n][0], pts[(i + 1) % n][1])
                   for i in range(n)]
        mean = sum(lengths) / n
        if mean < 1e-10:
            return False
        return all(abs(l - mean) <= tol * mean for l in lengths)

    def offset(self, distance, time=0):
        """Return a new Polygon with vertices moved along averaged edge normals.

        Positive distance moves outward, negative moves inward.
        For each vertex, compute the average of the two adjacent edge normals,
        then move the vertex along that average normal by distance.
        """
        pts = [v.at_time(time) for v in self.vertices]
        n = len(pts)
        if n < 2:
            return Polygon(*[(float(p[0]), float(p[1])) for p in pts], closed=self.closed)
        new_pts = []
        for i in range(n):
            if self.closed:
                prev_idx = (i - 1) % n
                next_idx = (i + 1) % n
            else:
                prev_idx = max(0, i - 1)
                next_idx = min(n - 1, i + 1)
            # Edge from prev to current
            dx1 = float(pts[i][0] - pts[prev_idx][0])
            dy1 = float(pts[i][1] - pts[prev_idx][1])
            len1 = math.sqrt(dx1 * dx1 + dy1 * dy1)
            # Edge from current to next
            dx2 = float(pts[next_idx][0] - pts[i][0])
            dy2 = float(pts[next_idx][1] - pts[i][1])
            len2 = math.sqrt(dx2 * dx2 + dy2 * dy2)
            # Outward normals (rotate edge direction 90 degrees CCW: (-dy, dx))
            # In SVG coords (y-down), "outward" for a CW polygon is (-dy, dx)
            if len1 > 0:
                n1x, n1y = -dy1 / len1, dx1 / len1
            else:
                n1x, n1y = 0.0, 0.0
            if len2 > 0:
                n2x, n2y = -dy2 / len2, dx2 / len2
            else:
                n2x, n2y = 0.0, 0.0
            # Average normal
            avg_nx = n1x + n2x
            avg_ny = n1y + n2y
            avg_len = math.sqrt(avg_nx * avg_nx + avg_ny * avg_ny)
            if avg_len > 0:
                avg_nx /= avg_len
                avg_ny /= avg_len
            new_x = float(pts[i][0]) + avg_nx * distance
            new_y = float(pts[i][1]) + avg_ny * distance
            new_pts.append((new_x, new_y))
        return Polygon(*new_pts, closed=self.closed)

    def rotate_vertices(self, angle_deg, cx=None, cy=None, time=0):
        """Return a new Polygon with all vertices rotated by angle_deg degrees.

        The rotation is applied around the point ``(cx, cy)``.  If *cx* and
        *cy* are not given the centroid of the polygon (at *time*) is used as
        the rotation centre.

        The returned polygon is a plain (non-animated) copy — its vertices are
        set to the rotated positions at creation time 0.

        Parameters
        ----------
        angle_deg:
            Rotation angle in degrees (positive = clockwise in SVG coordinates,
            which use a y-down system).
        cx, cy:
            Centre of rotation in SVG pixel coordinates.  Defaults to the
            polygon's centroid.
        time:
            Animation time at which to read the current vertex positions.

        Returns
        -------
        Polygon
            A new Polygon with rotated vertices and the same ``closed`` flag.
        """
        pts = self.get_vertices(time)
        if cx is None or cy is None:
            centroid = self.get_center(time)
            if cx is None:
                cx = centroid[0]
            if cy is None:
                cy = centroid[1]
        rad = math.radians(angle_deg)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        new_pts = []
        for x, y in pts:
            rx, ry = x - cx, y - cy
            new_pts.append((cx + rx * cos_a - ry * sin_a, cy + rx * sin_a + ry * cos_a))
        return Polygon(*new_pts, closed=self.closed)

    @classmethod
    def from_points(cls, points, **kwargs):
        """Create a Polygon from a list of (x, y) tuples."""
        return cls(*points, **kwargs)

    @classmethod
    def convex_hull(cls, *points, **kwargs):
        """Create a Polygon that is the convex hull of the given points using gift-wrapping (Jarvis march).

        Raises ValueError if fewer than 3 points are given or all points are collinear.
        Collinear intermediate points are skipped so only the extreme hull vertices are kept.
        """
        pts = [(float(p[0]), float(p[1])) for p in points]
        if len(pts) < 3:
            raise ValueError("convex_hull requires at least 3 points")

        def _cross(o, a, b):
            """Cross product of vectors OA and OB (positive = CCW, negative = CW, zero = collinear)."""
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

        # Find the leftmost (then bottommost in SVG coords) point as start
        start = min(pts, key=lambda p: (p[0], p[1]))
        hull = []
        current = start
        while True:
            hull.append(current)
            # Find next point that is most CCW from current (skip collinear midpoints)
            candidate = pts[0] if pts[0] != current else pts[1]
            for p in pts:
                if p == current:
                    continue
                cross = _cross(current, candidate, p)
                if cross < 0:
                    # p is more CCW — choose p as new candidate
                    candidate = p
                elif cross == 0:
                    # collinear: keep the farther one (skip intermediate points)
                    d_cand = (candidate[0] - current[0]) ** 2 + (candidate[1] - current[1]) ** 2
                    d_p = (p[0] - current[0]) ** 2 + (p[1] - current[1]) ** 2
                    if d_p > d_cand:
                        candidate = p
            if candidate == start:
                break
            current = candidate
            if len(hull) > len(pts):
                # Safety: degenerate case, all collinear
                break

        if len(hull) < 3:
            raise ValueError("convex_hull: all points are collinear")
        return cls(*hull, **kwargs)

    @classmethod
    def from_svg_path(cls, path_d, **kwargs):
        """Create a Polygon from a simple SVG path string (M/L/Z commands only).

        Parses MoveTo (M/m), LineTo (L/l), and ClosePath (Z/z) commands.
        """
        import re
        points = []
        cx, cy = 0.0, 0.0
        for cmd, coords_str in re.findall(r'([MmLlZz])\s*([^MmLlZz]*)', path_d):
            nums = [float(n) for n in re.findall(r'-?[\d.]+', coords_str)]
            pairs = [(nums[i], nums[i+1]) for i in range(0, len(nums) - 1, 2)]
            if cmd == 'M':
                for x, y in pairs:
                    cx, cy = x, y
                    points.append((cx, cy))
            elif cmd == 'm':
                for x, y in pairs:
                    cx += x; cy += y
                    points.append((cx, cy))
            elif cmd == 'L':
                for x, y in pairs:
                    cx, cy = x, y
                    points.append((cx, cy))
            elif cmd == 'l':
                for x, y in pairs:
                    cx += x; cy += y
                    points.append((cx, cy))
            # Z/z: just close, don't add point
        if not points:
            return cls((0, 0), **kwargs)
        return cls(*points, **kwargs)

    def contains_point(self, px, py, time=0):
        """Point-in-polygon test using ray-casting algorithm."""
        pts = self.get_vertices(time)
        n = len(pts)
        inside = False
        j = n - 1
        for i in range(n):
            xi, yi = pts[i]
            xj, yj = pts[j]
            if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi + 1e-20) + xi):
                inside = not inside
            j = i
        return inside

    def is_convex(self, time=0):
        """Return True if this polygon is convex."""
        pts = self.get_vertices(time)
        n = len(pts)
        if n < 3:
            return True
        sign = None
        for i in range(n):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % n]
            x3, y3 = pts[(i + 2) % n]
            cross = (x2 - x1) * (y3 - y2) - (y2 - y1) * (x3 - x2)
            if abs(cross) < 1e-10:
                continue
            if sign is None:
                sign = cross > 0
            elif (cross > 0) != sign:
                return False
        return True

    def get_edges(self, time=0):
        """Return a list of Line objects for each edge of the polygon.

        For a closed polygon the last edge connects the final vertex back to
        the first.  For an open polyline the last-to-first closing edge is
        omitted.

        Parameters
        ----------
        time:
            Animation time at which to evaluate vertex positions.

        Returns
        -------
        list[Line]
            Each Line corresponds to one edge of the polygon.
        """
        pts = self.get_vertices(time)
        n = len(pts)
        if n < 2:
            return []
        edges = []
        for i in range(n - 1):
            x1, y1 = pts[i]
            x2, y2 = pts[i + 1]
            edges.append(Line(x1=x1, y1=y1, x2=x2, y2=y2))
        if self.closed and n > 2:
            x1, y1 = pts[-1]
            x2, y2 = pts[0]
            edges.append(Line(x1=x1, y1=y1, x2=x2, y2=y2))
        return edges

    def translate(self, dx, dy):
        """Translate all vertices by (*dx*, *dy*).

        This is a geometric operation on the polygon's vertices (applied
        immediately at time 0), not an SVG transform.

        Parameters
        ----------
        dx, dy:
            Horizontal and vertical offset to apply to every vertex.
        """
        for v in self.vertices:
            v.add_onward(0, (dx, dy))
        self._bbox_version += 1
        return self

    def scale_vertices(self, factor, time=0):
        """Scale all vertices relative to the centroid by factor."""
        cx, cy = self.centroid(time)
        for v in self.vertices:
            vx, vy = v.at_time(time)
            v.set_onward(time, (cx + (vx - cx) * factor, cy + (vy - cy) * factor))
        self._bbox_version += 1
        return self

    def __repr__(self):
        return f'Polygon({len(self.vertices)} vertices)'


class Ellipse(VObject):
    def __init__(self, rx: float = 120, ry: float = 60, cx: float = 960, cy: float = 540, z=0, creation=0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        self.c = attributes.Coor(creation, (cx, cy))
        self.rx = attributes.Real(creation, rx)
        self.ry = attributes.Real(creation, ry)
        self.styling = style.Styling(styling_kwargs, creation=creation,
                                     fill_opacity=0.7, stroke='#fff', stroke_width=DEFAULT_STROKE_WIDTH)

    def _extra_attrs(self):
        return [self.c, self.rx, self.ry]

    def _shift_coors(self):
        return [self.c]

    def snap_points(self, time):
        cx, cy = self.c.at_time(time)
        return [(float(cx), float(cy))]

    def bbox(self, time):
        cx, cy = self.c.at_time(time)
        rx, ry = self.rx.at_time(time), self.ry.at_time(time)
        return self._bbox_from_points([(cx-rx, cy), (cx+rx, cy), (cx, cy-ry), (cx, cy+ry)], time) or super().bbox(time)

    def path(self, time):
        rx, ry = self.rx.at_time(time), self.ry.at_time(time)
        cx, cy = self.c.at_time(time)
        return f'M{cx-rx},{cy}a{rx},{ry} 0 1,0 {rx*2},0a{rx},{ry} 0 1,0 -{rx*2},0z'

    def get_area(self, time=0):
        """Return the area (pi * rx * ry)."""
        return math.pi * self.rx.at_time(time) * self.ry.at_time(time)

    def get_perimeter(self, time=0):
        """Approximate perimeter using Ramanujan's second formula (more accurate)."""
        a = self.rx.at_time(time)
        b = self.ry.at_time(time)
        h = ((a - b) / (a + b)) ** 2
        return math.pi * (a + b) * (1 + 3 * h / (10 + math.sqrt(4 - 3 * h)))

    def get_circumference(self, time=0):
        """Alias for get_perimeter. Returns approximate perimeter using Ramanujan's formula."""
        return self.get_perimeter(time)

    def eccentricity(self, time=0):
        """Return the eccentricity of the ellipse.

        Eccentricity e = sqrt(1 - (b/a)^2) where a = max(rx, ry) and b = min(rx, ry).
        Returns 0 for a circle (rx == ry) and approaches 1 as the ellipse becomes more elongated.
        """
        a = max(self.rx.at_time(time), self.ry.at_time(time))
        b = min(self.rx.at_time(time), self.ry.at_time(time))
        if a == 0:
            return 0.0
        return math.sqrt(1 - (b / a) ** 2)

    def point_at_angle(self, degrees, time=0):
        """Return (x, y) on the ellipse at the given angle (degrees, CCW from right)."""
        cx, cy = self.c.at_time(time)
        rx, ry = self.rx.at_time(time), self.ry.at_time(time)
        rad = math.radians(degrees)
        return (cx + rx * math.cos(rad), cy - ry * math.sin(rad))

    def get_point_at_parameter(self, t, time=0):
        """Return (x, y) on the ellipse at parameter t in [0, 1].

        t=0 corresponds to the rightmost point (angle 0), t=0.25 to the bottom
        (SVG convention, y increases downward), t=0.5 to the leftmost point, and
        t=0.75 to the top.  Uses the standard parametric form::

            x = cx + rx * cos(2 * pi * t)
            y = cy + ry * sin(2 * pi * t)

        Parameters
        ----------
        t:
            Parameter in [0, 1].  Values outside this range are allowed and
            wrap naturally via trigonometry.
        time:
            Animation time at which to read cx, cy, rx, ry.

        Returns
        -------
        (x, y) tuple of floats.

        Example
        -------
        >>> e = Ellipse(rx=100, ry=50, cx=500, cy=400)
        >>> e.get_point_at_parameter(0)    # rightmost: (600.0, 400.0)
        >>> e.get_point_at_parameter(0.25) # bottom:    (500.0, 450.0)
        """
        cx, cy = self.c.at_time(time)
        rx, ry = self.rx.at_time(time), self.ry.at_time(time)
        angle = 2 * math.pi * t
        return (cx + rx * math.cos(angle), cy + ry * math.sin(angle))

    def contains_point(self, px, py, time=0):
        """Return True if point (px, py) is inside the ellipse.

        Uses the standard ellipse equation:
        ``((px - cx) / rx)^2 + ((py - cy) / ry)^2 <= 1``.

        Parameters
        ----------
        px, py:
            Point coordinates to test.
        time:
            Animation time at which to evaluate ellipse parameters.
        """
        cx = self.c.at_time(time)[0]
        cy = self.c.at_time(time)[1]
        rx = self.rx.at_time(time)
        ry = self.ry.at_time(time)
        if rx == 0 or ry == 0:
            return False
        return ((px - cx) / rx) ** 2 + ((py - cy) / ry) ** 2 <= 1

    def get_rx(self, time=0):
        return self.rx.at_time(time)

    def get_ry(self, time=0):
        return self.ry.at_time(time)

    def set_center(self, cx, cy, start=0, end=None, easing=easings.smooth):
        _anim(self.c, start, end, (cx, cy), easing)
        return self

    def set_rx(self, value, start=0, end=None, easing=easings.smooth):
        """Animate the x-radius to value."""
        _anim(self.rx, start, end, value, easing)
        return self

    def set_ry(self, value, start=0, end=None, easing=easings.smooth):
        """Animate the y-radius to value."""
        _anim(self.ry, start, end, value, easing)
        return self

    def __repr__(self):
        cx, cy = self.c.at_time(0)
        return f'Ellipse(rx={self.rx.at_time(0):.0f}, ry={self.ry.at_time(0):.0f}, cx={cx:.0f}, cy={cy:.0f})'

    def to_svg(self, time):
        cx, cy = self.c.at_time(time)
        return f"<ellipse cx='{cx}' cy='{cy}' rx='{self.rx.at_time(time)}' ry='{self.ry.at_time(time)}'{self.styling.svg_style(time)} />"


class Circle(Ellipse):
    """Circle: Ellipse with rx == ry."""
    def __init__(self, r: float = 120, cx: float = 960, cy: float = 540, z=0, creation=0, **styling_kwargs):
        super().__init__(rx=r, ry=r, cx=cx, cy=cy, z=z, creation=creation, **styling_kwargs)

    def __repr__(self):
        cx, cy = self.c.at_time(0)
        return f'{self.__class__.__name__}(r={self.rx.at_time(0):.0f}, cx={cx:.0f}, cy={cy:.0f})'

    @property
    def r(self):
        return self.rx

    @r.setter
    def r(self, value):
        self.rx = value
        self.ry = value

    def point_at_angle(self, degrees, time=0):
        """Return (x, y) on the circle at the given angle (degrees, CCW from right)."""
        cx, cy = self.c.at_time(time)
        r = self.rx.at_time(time)
        rad = math.radians(degrees)
        return (cx + r * math.cos(rad), cy - r * math.sin(rad))

    def get_area(self, time=0):
        """Return the area (pi * r^2)."""
        r = self.rx.at_time(time)
        return math.pi * r * r

    def get_perimeter(self, time=0):
        """Return the exact perimeter (2 * pi * r)."""
        return 2 * math.pi * self.rx.at_time(time)

    def get_circumference(self, time=0):
        """Alias for get_perimeter. Returns the exact circumference (2 * pi * r)."""
        return self.get_perimeter(time)

    def point_on_circle(self, angle_degrees, time=0):
        """Return (x, y) on the circle at the given angle (degrees, CCW from right).
        Alias for point_at_angle."""
        return self.point_at_angle(angle_degrees, time)

    @classmethod
    def from_diameter(cls, p1, p2, **kwargs):
        """Create a Circle from two diameter endpoints.

        Parameters
        ----------
        p1, p2:
            Two (x, y) points defining the diameter.
        **kwargs:
            Extra keyword arguments forwarded to the Circle constructor.

        Returns
        -------
        Circle
            A new Circle centered at the midpoint with radius = half the distance.
        """
        cx = (p1[0] + p2[0]) / 2
        cy = (p1[1] + p2[1]) / 2
        r = math.hypot(p2[0] - p1[0], p2[1] - p1[1]) / 2
        return cls(r=r, cx=cx, cy=cy, **kwargs)

    def tangent_line(self, angle_degrees, length=100, time=0, creation=0, **line_kwargs):
        """Return a Line tangent to the circle at the given angle.
        Angle 0 = right, 90 = down (SVG coordinates)."""
        px, py = self.point_on_circle(angle_degrees, time)
        rad = math.radians(angle_degrees)
        # Tangent is perpendicular to radius
        tx, ty = -math.sin(rad), math.cos(rad)
        half = length / 2
        return Line(x1=px - tx * half, y1=py - ty * half,
                    x2=px + tx * half, y2=py + ty * half,
                    creation=creation, **line_kwargs)

    def tangent_at_point(self, px, py, length=200, time=0, creation=0, **line_kwargs):
        """Return a Line tangent to the circle at the point closest to (px, py).

        Finds the nearest point on the circle surface to the given external
        (or internal) point, then constructs the tangent at that point.
        The tangent is perpendicular to the radius at the contact point.

        Parameters
        ----------
        px, py:
            Reference point. The tangent is drawn at whichever point on the
            circle lies closest to this location.
        length:
            Total length of the returned tangent line segment.
        time:
            Animation time at which to read the circle's position and radius.
        creation:
            Creation time for the returned Line object.
        **line_kwargs:
            Additional styling keyword arguments forwarded to Line.
        """
        cx, cy = self.c.at_time(time)
        # Angle from circle center to the given point
        angle_rad = math.atan2(-(py - cy), px - cx)  # negate dy for SVG coords
        angle_deg = math.degrees(angle_rad)
        return self.tangent_line(angle_deg, length=length, time=time,
                                 creation=creation, **line_kwargs)

    def get_tangent_lines(self, px, py, time=0, length=200, **kwargs):
        """Return the two tangent lines from external point (px, py) to the circle.

        Uses the standard geometric construction:

        * Compute distance *d* from the point to the circle center.
        * If the point is strictly inside the circle (*d* < *r*), return ``[]``.
        * If the point lies on the circle (*d* ≈ *r*), return a single-element
          list containing the one tangent line.
        * Otherwise return two Line objects, one for each tangent.

        Each Line runs through the tangent touch-point and is oriented along
        the tangent direction (perpendicular to the radius at the touch point),
        centred on the touch point with total length *length*.

        Parameters
        ----------
        px, py:
            Coordinates of the external (or boundary) point.
        time:
            Animation time at which to read the circle's position/radius.
        length:
            Total length of each returned tangent Line segment.
        **kwargs:
            Extra styling keyword arguments forwarded to Line (e.g. stroke,
            stroke_width).

        Returns
        -------
        list of Line
            0, 1, or 2 Line objects.
        """
        cx, cy = self.c.at_time(time)
        r = self.rx.at_time(time)
        d = _distance(cx, cy, px, py)
        if d < r - 1e-9:
            # Point is inside the circle — no tangent lines exist.
            return []
        if abs(d) < 1e-12:
            # Point coincides with center — degenerate case.
            return []
        # Vector from center to external point (normalised)
        ux, uy = (px - cx) / d, (py - cy) / d
        if d <= r + 1e-9:
            # Point is on the circle — exactly one tangent.
            # Tangent is perpendicular to the radius at the point.
            tx, ty = -uy, ux  # 90-degree rotation
            half = length / 2
            return [Line(x1=px - tx * half, y1=py - ty * half,
                         x2=px + tx * half, y2=py + ty * half, **kwargs)]
        # Point is outside the circle — two tangent lines.
        # Half-angle of the tangent from the line joining point to center.
        half_angle = math.acos(max(-1.0, min(1.0, r / d)))
        # Angle from center to the external point (in SVG coords, y-down)
        base_angle = math.atan2(py - cy, px - cx)
        lines = []
        for sign in (1, -1):
            touch_angle = base_angle + sign * half_angle
            # Touch point on the circle
            tx_touch = cx + r * math.cos(touch_angle)
            ty_touch = cy + r * math.sin(touch_angle)
            # Tangent direction: perpendicular to the radius at the touch point
            # radius direction: (cos(touch_angle), sin(touch_angle))
            # tangent direction: (-sin(touch_angle), cos(touch_angle))
            td_x = -math.sin(touch_angle)
            td_y = math.cos(touch_angle)
            half = length / 2
            lines.append(Line(x1=tx_touch - td_x * half, y1=ty_touch - td_y * half,
                               x2=tx_touch + td_x * half, y2=ty_touch + td_y * half,
                               **kwargs))
        return lines

    def chord(self, angle1, angle2, time=0, **kwargs):
        """Return a Line connecting two points on the circle at the given angles.

        Both angles are measured in degrees, counter-clockwise from the
        rightmost point (the standard mathematical convention, which maps to
        SVG coordinates where y increases downward).

        Parameters
        ----------
        angle1, angle2:
            Angles in degrees for the two endpoints of the chord.
        time:
            Animation time at which to read the circle's center and radius.
        **kwargs:
            Extra styling keyword arguments forwarded to :class:`Line`
            (e.g. ``stroke``, ``stroke_width``).

        Returns
        -------
        Line
            A Line segment connecting ``point_at_angle(angle1)`` to
            ``point_at_angle(angle2)``.

        Example
        -------
        >>> c = Circle(r=100, cx=200, cy=200)
        >>> ch = c.chord(0, 90)   # connects (300,200) to (200,100)
        """
        x1, y1 = self.point_at_angle(angle1, time)
        x2, y2 = self.point_at_angle(angle2, time)
        return Line(x1=x1, y1=y1, x2=x2, y2=y2, **kwargs)

    def get_radius(self, time=0):
        return self.rx.at_time(time)

    def set_radius(self, value, start=0, end=None, easing=easings.smooth):
        """Animate the radius to value."""
        _anim(self.rx, start, end, value, easing)
        _anim(self.ry, start, end, value, easing)
        return self

    @classmethod
    def from_three_points(cls, p1, p2, p3, **kwargs):
        """Create a Circle (circumscribed circle) passing through three points.

        Each point is an (x, y) tuple. Raises ValueError if points are collinear.
        """
        ax, ay = p1
        bx, by = p2
        cx, cy = p3
        d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
        if abs(d) < 1e-10:
            raise ValueError("The three points are collinear; no unique circle exists.")
        a2 = ax * ax + ay * ay
        b2 = bx * bx + by * by
        c2 = cx * cx + cy * cy
        ux = (a2 * (by - cy) + b2 * (cy - ay) + c2 * (ay - by)) / d
        uy = (a2 * (cx - bx) + b2 * (ax - cx) + c2 * (bx - ax)) / d
        r = math.sqrt((ax - ux) ** 2 + (ay - uy) ** 2)
        return cls(r=r, cx=ux, cy=uy, **kwargs)

    def intersect_line(self, line, time=0):
        """Return list of intersection points [(x,y), ...] with a Line (0, 1, or 2 points)."""
        cx, cy = self.c.at_time(time)
        r = self.r.at_time(time)
        x1, y1 = line.p1.at_time(time)
        x2, y2 = line.p2.at_time(time)
        dx, dy = x2 - x1, y2 - y1
        fx, fy = x1 - cx, y1 - cy
        a = dx * dx + dy * dy
        b = 2 * (fx * dx + fy * dy)
        c = fx * fx + fy * fy - r * r
        disc = b * b - 4 * a * c
        if a < 1e-20 or disc < 0:
            return []
        sq = math.sqrt(disc)
        points = []
        for t_val in [(-b - sq) / (2 * a), (-b + sq) / (2 * a)]:
            points.append((x1 + t_val * dx, y1 + t_val * dy))
        if abs(disc) < 1e-10:
            return [points[0]]  # tangent: single point
        return points

    def intersect_circle(self, other, time=0):
        """Return intersection points with another Circle as list of (x, y) tuples.

        Returns 0 points if circles are too far apart or one contains the
        other, 1 point if they are tangent, 2 points otherwise.
        """
        cx1, cy1 = self.c.at_time(time)
        cx2, cy2 = other.c.at_time(time)
        r1 = self.rx.at_time(time)
        r2 = other.rx.at_time(time)
        d = math.hypot(cx2 - cx1, cy2 - cy1)
        if d > r1 + r2 or d < abs(r1 - r2) or d == 0:
            return []
        a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
        h_sq = r1 * r1 - a * a
        if h_sq < 0:
            return []
        h = math.sqrt(h_sq)
        mx = cx1 + a * (cx2 - cx1) / d
        my = cy1 + a * (cy2 - cy1) / d
        if h < 1e-9:
            return [(mx, my)]
        dx = h * (cy2 - cy1) / d
        dy = h * (cx2 - cx1) / d
        return [(mx + dx, my - dy), (mx - dx, my + dy)]

    def contains_point(self, px, py, time=0):
        """Point-in-circle test."""
        cx, cy = self.c.at_time(time)
        r = self.rx.at_time(time)
        return _distance(cx, cy, px, py) <= r

    def inscribed_polygon(self, n, angle=0, time=0, **kwargs):
        """Return a regular *n*-gon whose vertices lie on this circle.

        The polygon is constructed from the circle's current position and radius
        at *time*, so the result is a static snapshot (not dynamically linked).

        Parameters
        ----------
        n:
            Number of sides / vertices (≥ 3).
        angle:
            Rotation of the first vertex in degrees, measured counter-clockwise
            from the right (standard math convention).  Default 0 places the
            first vertex at the rightmost point.
        time:
            The time at which to read the circle's position and radius.
        **kwargs:
            Forwarded to :class:`RegularPolygon`.

        Returns
        -------
        RegularPolygon
        """
        cx, cy = self.c.at_time(time)
        r = self.rx.at_time(time)
        return RegularPolygon(n, radius=r, cx=cx, cy=cy, angle=angle, **kwargs)

    def arc_between(self, start_angle, end_angle, time=0, **kwargs):
        """Return an Arc with the same centre and radius as this circle.

        The arc spans from *start_angle* to *end_angle* (degrees, CCW from
        right, standard math convention matching :meth:`point_at_angle`).

        Parameters
        ----------
        start_angle, end_angle:
            Start and end angles in degrees.
        time:
            Time at which to read the circle's position and radius.
        **kwargs:
            Extra styling keyword arguments forwarded to :class:`Arc`
            (e.g. ``stroke``, ``stroke_width``).

        Returns
        -------
        Arc
            A new :class:`Arc` centred on this circle.

        Example
        -------
        >>> c = Circle(r=100, cx=500, cy=300)
        >>> arc = c.arc_between(0, 90)   # top-right quarter arc
        """
        cx, cy = self.c.at_time(time)
        r = self.rx.at_time(time)
        return Arc(cx=cx, cy=cy, r=r,
                   start_angle=start_angle, end_angle=end_angle, **kwargs)

    def diameter_line(self, angle_deg: float = 0, time: float = 0, **kwargs):
        """Return a Line representing the diameter at the given angle.

        The line passes through the circle's centre and extends one radius in
        each direction, so its total length equals the diameter (2 * r).

        Parameters
        ----------
        angle_deg:
            Angle of the diameter in degrees, measured counter-clockwise from
            the right (standard math convention, matching
            :meth:`point_at_angle`).  0° gives a horizontal diameter;
            90° gives a vertical one.
        time:
            Animation time at which to read the circle's position and radius.
        **kwargs:
            Extra styling keyword arguments forwarded to :class:`Line`
            (e.g. ``stroke``, ``stroke_width``).

        Returns
        -------
        Line
            A line segment whose endpoints lie on opposite sides of the circle.

        Example
        -------
        >>> c = Circle(r=100, cx=200, cy=200)
        >>> d = c.diameter_line(0)    # horizontal diameter
        >>> d = c.diameter_line(90)   # vertical diameter
        """
        cx, cy = self.c.at_time(time)
        r = self.rx.at_time(time)
        rad = math.radians(angle_deg)
        dx = r * math.cos(rad)
        dy = -r * math.sin(rad)   # negate: SVG y-axis points down
        return Line(x1=cx - dx, y1=cy - dy, x2=cx + dx, y2=cy + dy, **kwargs)

    def to_svg(self, time):
        cx, cy = self.c.at_time(time)
        return f"<circle cx='{cx}' cy='{cy}' r='{self.rx.at_time(time)}'{self.styling.svg_style(time)} />"


class Dot(Circle):
    """Small filled circle, no stroke."""
    def __init__(self, r: float = DEFAULT_DOT_RADIUS, cx: float = 960, cy: float = 540, z=0, creation=0, **styling_kwargs):
        super().__init__(r=r, cx=cx, cy=cy, z=z, creation=creation,
                         **({'fill': '#fff', 'fill_opacity': 1, 'stroke_width': 0} | styling_kwargs))

    def __repr__(self):
        cx, cy = self.c.at_time(0)
        return f'Dot(cx={cx:.0f}, cy={cy:.0f})'


class Rectangle(VObject):
    def __init__(self, width, height, x=960, y=540, rx=0, ry=0, creation=0, z=0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        self.x = attributes.Real(creation, x)
        self.y = attributes.Real(creation, y)
        self.width = attributes.Real(creation, width)
        self.height = attributes.Real(creation, height)
        self.rx = attributes.Real(creation, rx)
        self.ry = attributes.Real(creation, ry)
        self.styling = style.Styling(styling_kwargs, creation=creation, fill_opacity=0.7, stroke='#fff', stroke_width=DEFAULT_STROKE_WIDTH)

    def _extra_attrs(self):
        return [self.x, self.y, self.width, self.height, self.rx, self.ry]

    def _shift_reals(self):
        return [(self.x, self.y)]

    def snap_points(self, time):
        x, y = self.x.at_time(time), self.y.at_time(time)
        w, h = self.width.at_time(time), self.height.at_time(time)
        return [(float(x), float(y)), (float(x+w), float(y)),
                (float(x+w), float(y+h)), (float(x), float(y+h))]

    def bbox(self, time):
        x, y = self.x.at_time(time), self.y.at_time(time)
        w, h = self.width.at_time(time), self.height.at_time(time)
        return self._bbox_from_points([(x,y),(x+w,y),(x+w,y+h),(x,y+h)], time) or super().bbox(time)

    def path(self, time):
        x, y = self.x.at_time(time), self.y.at_time(time)
        w, h = self.width.at_time(time), self.height.at_time(time)
        rx, ry = self.rx.at_time(time), self.ry.at_time(time)
        if rx == 0 and ry == 0:
            return f'M{x},{y}l{w},0l0,{h}l-{w},0z'
        return (f'M{x+rx},{y} l {w-rx*2},0 '
                f'a {rx},{ry} 0 0,1 {rx},{ry} l 0,{h-ry*2} '
                f'a {rx},{ry} 0 0,1 -{rx},{ry} l {rx*2-w},0 '
                f'a {rx},{ry} 0 0,1 -{rx},-{ry} l 0,{ry*2-h} '
                f'a {rx},{ry} 0 0,1 {rx},-{ry} z')

    def to_svg(self, time):
        return (f"<rect x='{self.x.at_time(time)}' y='{self.y.at_time(time)}'"
                f" width='{self.width.at_time(time)}' height='{self.height.at_time(time)}'"
                f" rx='{self.rx.at_time(time)}' ry='{self.ry.at_time(time)}'"
                f"{self.styling.svg_style(time)} />")

    def get_vertices(self, time=0):
        """Return the four corners: top-left, top-right, bottom-right, bottom-left."""
        return self.snap_points(time)

    def get_corners(self, time=0):
        """Return the four corners as a list of (x, y) tuples.

        Order: top-left, top-right, bottom-right, bottom-left, matching SVG
        convention where y increases downward.  Equivalent to
        ``get_vertices(time)``.

        Example
        -------
        >>> r = Rectangle(width=100, height=50, x=10, y=20)
        >>> r.get_corners()
        [(10.0, 20.0), (110.0, 20.0), (110.0, 70.0), (10.0, 70.0)]
        """
        return self.get_vertices(time)

    def get_area(self, time=0):
        """Return the area (width * height)."""
        return self.width.at_time(time) * self.height.at_time(time)

    def get_perimeter(self, time=0):
        """Return the perimeter (2 * (width + height))."""
        return 2 * (self.width.at_time(time) + self.height.at_time(time))

    def get_diagonal_length(self, time=0):
        """Return the length of the diagonal: sqrt(width^2 + height^2).

        Parameters
        ----------
        time:
            Animation time at which to read the rectangle dimensions.

        Example
        -------
        >>> r = Rectangle(width=3, height=4)
        >>> r.get_diagonal_length()   # 5.0
        """
        w = self.width.at_time(time)
        h = self.height.at_time(time)
        return math.sqrt(w * w + h * h)

    def get_size(self, time=0):
        return (self.width.at_time(time), self.height.at_time(time))

    def is_square(self, time=0, tol=1e-3):
        """Return True if width equals height (within tolerance)."""
        w = self.width.at_time(time)
        h = self.height.at_time(time)
        return abs(w - h) < tol

    def aspect_ratio(self, time=0):
        """Return width / height ratio."""
        w = self.width.at_time(time)
        h = self.height.at_time(time)
        return w / h if h != 0 else float('inf')

    @classmethod
    def square(cls, side, **kwargs):
        """Create a square with equal width and height."""
        return cls(side, side, **kwargs)

    @classmethod
    def from_center(cls, cx, cy, width, height, **kwargs):
        """Create a Rectangle centered at (cx, cy) with the given width and height."""
        return cls(width, height, x=cx - width / 2, y=cy - height / 2, **kwargs)

    @classmethod
    def from_corners(cls, x1, y1, x2, y2, **kwargs):
        """Create a Rectangle from two opposite corner points.

        The two points do not need to be in any particular order — the
        method normalises them so that ``(x, y)`` is always the top-left
        corner and ``width``/``height`` are always positive.

        Parameters
        ----------
        x1, y1:
            First corner coordinates (e.g. top-left in SVG space).
        x2, y2:
            Opposite corner coordinates (e.g. bottom-right in SVG space).
        **kwargs:
            Extra keyword arguments forwarded to the Rectangle constructor
            (e.g. ``stroke``, ``fill``, ``rx`` for rounded corners).

        Returns
        -------
        Rectangle
            A new Rectangle whose top-left corner is at
            ``(min(x1,x2), min(y1,y2))`` with positive width and height.

        Example
        -------
        >>> r = Rectangle.from_corners(50, 100, 250, 300)
        >>> r.x.at_time(0), r.y.at_time(0)   # (50.0, 100.0)
        >>> r.width.at_time(0), r.height.at_time(0)  # (200.0, 200.0)
        """
        lx, rx_ = min(x1, x2), max(x1, x2)
        ty, by = min(y1, y2), max(y1, y2)
        return cls(rx_ - lx, by - ty, x=lx, y=ty, **kwargs)

    def set_size(self, width, height, start=0, end=None, easing=easings.smooth):
        """Set both dimensions."""
        _anim(self.width, start, end, width, easing)
        _anim(self.height, start, end, height, easing)
        return self

    def contains_point(self, px, py, time=0):
        """Point-in-rect test."""
        x, y = self.x.at_time(time), self.y.at_time(time)
        w, h = self.width.at_time(time), self.height.at_time(time)
        return x <= px <= x + w and y <= py <= y + h

    def round_corners(self, radius=10, time=0, **kwargs):
        """Return a RoundedRectangle with the same size/position and the given corner radius."""
        from vectormation.style import _STYLES
        x = self.x.at_time(time)
        y = self.y.at_time(time)
        w = self.width.at_time(time)
        h = self.height.at_time(time)
        style_kw = {}
        for name in _STYLES:
            attr = getattr(self.styling, name)
            # Color.time_func returns a raw tuple; for other attrs use at_time
            val = attr.time_func(time) if isinstance(attr, attributes.Color) else attr.at_time(time)
            style_kw[name] = val
        style_kw.update(kwargs)
        return RoundedRectangle(w, h, x=x, y=y, corner_radius=radius, **style_kw)

    def split(self, direction='horizontal', count=2, time=0, **kwargs):
        """Split this rectangle into *count* equal sub-rectangles.

        Parameters
        ----------
        direction:
            ``'horizontal'`` splits into *count* rows stacked top-to-bottom.
            ``'vertical'`` splits into *count* columns arranged left-to-right.
        count:
            Number of equal pieces (must be >= 1).
        time:
            Animation time at which to read the current rectangle geometry.
        **kwargs:
            Extra styling keyword arguments forwarded to each sub-Rectangle.

        Returns
        -------
        VCollection
            A collection of *count* Rectangle objects that together tile the
            original rectangle exactly.
        """
        from vectormation._base import VCollection
        if count < 1:
            raise ValueError("split: count must be >= 1")
        rx = float(self.x.at_time(time))
        ry = float(self.y.at_time(time))
        rw = float(self.width.at_time(time))
        rh = float(self.height.at_time(time))
        parts = []
        if direction == 'horizontal':
            piece_h = rh / count
            for i in range(count):
                parts.append(Rectangle(rw, piece_h, x=rx, y=ry + i * piece_h, **kwargs))
        else:
            piece_w = rw / count
            for i in range(count):
                parts.append(Rectangle(piece_w, rh, x=rx + i * piece_w, y=ry, **kwargs))
        return VCollection(*parts)

    def inset(self, amount: float, time: float = 0, **kwargs):
        """Return a new Rectangle inset by *amount* pixels on every side.

        The returned rectangle is centred on the same position as the original
        but is smaller by ``2 * amount`` in both width and height.  This is
        useful for creating inner borders or nested frames.

        Parameters
        ----------
        amount:
            Number of pixels to inset on each side.  Positive values shrink
            the rectangle; negative values expand it.
        time:
            Animation time at which to read the current rectangle geometry.
        **kwargs:
            Extra styling keyword arguments forwarded to the new Rectangle
            (e.g. ``stroke``, ``fill``).  Any attribute not specified here
            will **not** be automatically copied from the parent rectangle —
            use :meth:`round_corners` if you need a full style copy.

        Returns
        -------
        Rectangle
            A new Rectangle with reduced dimensions.

        Raises
        ------
        ValueError
            If *amount* is so large that the inset width or height would
            become non-positive.

        Example
        -------
        >>> outer = Rectangle(200, 100, x=100, y=50)
        >>> inner = outer.inset(10)   # 180x80 at (110, 60)
        """
        rx = float(self.x.at_time(time))
        ry = float(self.y.at_time(time))
        rw = float(self.width.at_time(time))
        rh = float(self.height.at_time(time))
        new_w = rw - 2 * amount
        new_h = rh - 2 * amount
        if new_w <= 0 or new_h <= 0:
            raise ValueError(
                f"inset amount {amount} is too large for a {rw}x{rh} rectangle "
                f"(result would be {new_w}x{new_h})"
            )
        return Rectangle(new_w, new_h, x=rx + amount, y=ry + amount, **kwargs)

    def expand(self, amount=20, start=0, end=1, easing=easings.smooth):
        """Animate expanding the rectangle by *amount* pixels on each side.

        The rectangle grows by ``2 * amount`` in both width and height,
        while the position shifts inward by *amount* so the expansion is
        centered (the center of the rectangle stays in place).

        Parameters
        ----------
        amount:
            Number of pixels to expand on each side.
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
        w0 = self.width.at_time(start)
        h0 = self.height.at_time(start)
        x0 = self.x.at_time(start)
        y0 = self.y.at_time(start)
        self.width.move_to(start, end, w0 + 2 * amount, easing=easing)
        self.height.move_to(start, end, h0 + 2 * amount, easing=easing)
        self.x.move_to(start, end, x0 - amount, easing=easing)
        self.y.move_to(start, end, y0 - amount, easing=easing)
        return self

    def to_polygon(self, time=0, **kwargs):
        """Convert this rectangle to a Polygon with 4 vertices.

        Returns a static snapshot at *time* -- the resulting Polygon is not
        dynamically linked to this rectangle.  Styling from the rectangle is
        not copied; pass ``**kwargs`` to set fill, stroke, etc.

        Parameters
        ----------
        time:
            Animation time at which to read the rectangle geometry.
        **kwargs:
            Forwarded to :class:`Polygon`.

        Returns
        -------
        Polygon
        """
        corners = self.get_corners(time)
        return Polygon(*corners, **kwargs)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.width.at_time(0):.0f}x{self.height.at_time(0):.0f})'


class Line(VObject):
    def __init__(self, x1: float = 0, y1: float = 0, x2: float = 100, y2: float = 100, creation=0, z=0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        self.p1 = attributes.Coor(creation, (x1, y1))
        self.p2 = attributes.Coor(creation, (x2, y2))
        self.styling = style.Styling(styling_kwargs, creation=creation, stroke='#fff', stroke_width=DEFAULT_STROKE_WIDTH)

    def _extra_attrs(self):
        return [self.p1, self.p2]

    def _shift_coors(self):
        return [self.p1, self.p2]

    def snap_points(self, time):
        p1, p2 = self.p1.at_time(time), self.p2.at_time(time)
        return [(float(p1[0]), float(p1[1])), (float(p2[0]), float(p2[1]))]

    def bbox(self, time):
        return self._bbox_from_points([self.p1.at_time(time), self.p2.at_time(time)], time) or super().bbox(time)

    def path(self, time):
        x1, y1 = self.p1.at_time(time)
        x2, y2 = self.p2.at_time(time)
        return f'M{x1},{y1}L{x2},{y2}'

    def to_svg(self, time):
        p1, p2 = self.p1.at_time(time), self.p2.at_time(time)
        return f"<line x1='{p1[0]}' y1='{p1[1]}' x2='{p2[0]}' y2='{p2[1]}'{self.styling.svg_style(time)} />"


    def get_start(self, time=0):
        """Return the start point (x, y)."""
        p = self.p1.at_time(time)
        return (float(p[0]), float(p[1]))

    def get_end(self, time=0):
        """Return the end point (x, y)."""
        p = self.p2.at_time(time)
        return (float(p[0]), float(p[1]))

    def get_length(self, time=0):
        """Return the Euclidean length of the line."""
        x1, y1 = self.p1.at_time(time)
        x2, y2 = self.p2.at_time(time)
        return _distance(x1, y1, x2, y2)

    def get_angle(self, time=0):
        """Return the angle (in degrees) from p1 to p2. 0 = right, 90 = down.

        SVG convention (y-down): positive angles go clockwise.
        """
        # SVG convention (y-down): atan2(dy, dx) where dy increases downward
        x1, y1 = self.p1.at_time(time)
        x2, y2 = self.p2.at_time(time)
        return math.degrees(math.atan2(y2 - y1, x2 - x1))

    def get_midpoint(self, time=0):
        """Return the midpoint (x, y) of the line."""
        x1, y1 = self.p1.at_time(time)
        x2, y2 = self.p2.at_time(time)
        return ((x1 + x2) / 2, (y1 + y2) / 2)

    def split_at(self, t: float = 0.5, time: float = 0):
        """Split the line at parameter *t* and return two new Line objects.

        The parameter *t* is in ``[0, 1]`` where 0 = start and 1 = end.
        Values outside this range are clamped automatically.

        The split point is::

            P = p1 + t * (p2 - p1)

        Both returned lines inherit no styling — pass ``**kwargs`` to
        :class:`Line` after the call if styling is required.

        Parameters
        ----------
        t:
            Split parameter in [0, 1].  Default 0.5 = midpoint split.
        time:
            Animation time at which to read the endpoint coordinates.

        Returns
        -------
        (Line, Line)
            ``(first_segment, second_segment)`` where the first segment runs
            from p1 to the split point and the second from the split point
            to p2.

        Examples
        --------
        >>> line = Line(0, 0, 200, 0)
        >>> a, b = line.split_at(0.5)
        >>> a.get_end()    # (100.0, 0.0)
        >>> b.get_start()  # (100.0, 0.0)
        >>> a, b = line.split_at(0.25)
        """
        t = max(0.0, min(1.0, t))
        x1, y1 = self.p1.at_time(time)
        x2, y2 = self.p2.at_time(time)
        mx = x1 + t * (x2 - x1)
        my = y1 + t * (y2 - y1)
        first = Line(float(x1), float(y1), float(mx), float(my))
        second = Line(float(mx), float(my), float(x2), float(y2))
        return first, second

    def get_unit_vector(self, time=0):
        """Return the normalized direction vector (dx, dy) from p1 to p2.

        Alias for :meth:`get_direction`.
        """
        return self.get_direction(time)

    def get_direction(self, time=0):
        """Return the normalized direction vector (dx, dy) from p1 to p2.

        Uses :func:`_normalize` from ``_constants``.  Returns ``(0.0, 0.0)``
        when p1 == p2 (zero-length line).

        Parameters
        ----------
        time:
            Animation time at which to read p1 and p2.

        Returns
        -------
        (dx, dy) unit vector tuple of floats.

        Example
        -------
        >>> l = Line(x1=0, y1=0, x2=3, y2=4)
        >>> l.get_direction()   # (0.6, 0.8)
        """
        x1, y1 = self.p1.at_time(time)
        x2, y2 = self.p2.at_time(time)
        return _normalize(x2 - x1, y2 - y1)

    def get_vector(self, time=0):
        """Return the direction vector (dx, dy) from start to end.

        Unlike :meth:`get_direction` which returns a normalized unit vector,
        this returns the raw (unnormalized) vector from p1 to p2.

        Parameters
        ----------
        time:
            Animation time at which to read p1 and p2.

        Returns
        -------
        (dx, dy) tuple of floats.
        """
        x1, y1 = self.get_start(time)
        x2, y2 = self.get_end(time)
        return (x2 - x1, y2 - y1)

    def get_normal(self, time=0):
        """Return the normal vector perpendicular to the line direction.

        Rotates the direction vector 90 degrees counter-clockwise:
        if direction is (dx, dy), the normal is (-dy, dx).

        Returns ``(0.0, 0.0)`` when the line has zero length (p1 == p2).

        Parameters
        ----------
        time:
            Animation time at which to read p1 and p2.

        Returns
        -------
        (nx, ny) unit normal vector tuple of floats.

        Example
        -------
        >>> l = Line(x1=0, y1=0, x2=1, y2=0)
        >>> l.get_normal()   # (0.0, -1.0) — perpendicular, pointing up in math coords
        """
        dx, dy = self.get_direction(time)
        return (-dy, dx)

    def angle_to(self, other, time=0):
        """Return the angle in degrees between this line and another.

        Computes the angle between the two direction vectors using the
        dot-product formula.  The result is always in [0, 180].

        Parameters
        ----------
        other:
            Another :class:`Line` instance.
        time:
            Animation time at which to read both lines.

        Returns
        -------
        float
            Angle in degrees.
        """
        d1 = self.get_direction(time)
        d2 = other.get_direction(time)
        dot = d1[0] * d2[0] + d1[1] * d2[1]
        dot = max(-1.0, min(1.0, dot))  # clamp for numerical safety
        return math.degrees(math.acos(dot))

    def get_slope(self, time=0):
        """Return the slope (dy/dx) of the line, or float('inf') for vertical lines.
        Uses SVG coordinates (y increases downward)."""
        x1, y1 = self.p1.at_time(time)
        x2, y2 = self.p2.at_time(time)
        dx = x2 - x1
        if abs(dx) < 1e-10:
            return float('inf')
        return (y2 - y1) / dx

    def angle(self, time=0):
        """Return the angle of this line in degrees (0 = right, CCW positive).

        Math convention (y-up): positive angles go counter-clockwise.
        """
        # Math convention (CCW, y-up): negate dy to flip from SVG y-down to math y-up
        x1, y1 = self.p1.at_time(time)
        x2, y2 = self.p2.at_time(time)
        return math.degrees(math.atan2(-(y2 - y1), x2 - x1))

    def is_horizontal(self, time=0, tol=1e-3):
        """Return True if this line is approximately horizontal."""
        _, y1 = self.get_start(time)
        _, y2 = self.get_end(time)
        return abs(y2 - y1) < tol

    def is_vertical(self, time=0, tol=1e-3):
        """Return True if this line is approximately vertical."""
        x1, _ = self.get_start(time)
        x2, _ = self.get_end(time)
        return abs(x2 - x1) < tol

    def set_start(self, point, start=0, end=None, easing=easings.smooth):
        _anim(self.p1, start, end, point, easing)
        return self

    def set_end(self, point, start=0, end=None, easing=easings.smooth):
        _anim(self.p2, start, end, point, easing)
        return self

    def set_points(self, p1, p2, start=0):
        """Set both endpoints at once."""
        self.p1.set_onward(start, p1)
        self.p2.set_onward(start, p2)
        return self

    def set_length(self, length, start=0, end=None, easing=easings.smooth):
        """Scale line to new length keeping p1 fixed."""
        x1, y1 = self.p1.at_time(start)
        x2, y2 = self.p2.at_time(start)
        cur = _distance(x1, y1, x2, y2)
        if cur < 1e-9:
            return self
        factor = length / cur
        _anim(self.p2, start, end, (x1 + (x2 - x1) * factor, y1 + (y2 - y1) * factor), easing)
        return self

    def extend_to(self, length, anchor='start', start_time=0, end_time=None, easing=easings.smooth):
        """Extend or shrink the line to *length*, keeping one endpoint fixed.

        Unlike :meth:`set_length` (which always keeps p1 fixed), this method
        lets you choose which endpoint acts as the anchor:

        * ``anchor='start'`` — p1 is fixed; p2 moves to achieve the new length.
        * ``anchor='end'``   — p2 is fixed; p1 moves to achieve the new length.

        The direction of the line is preserved in both cases.

        Parameters
        ----------
        length:
            Target length in SVG pixels.
        anchor:
            Which endpoint to keep fixed: ``'start'`` (p1) or ``'end'`` (p2).
        start_time:
            Time at which the change begins.
        end_time:
            Time at which the change ends.  ``None`` means instant.
        easing:
            Easing function for the animation.
        """
        x1, y1 = self.p1.at_time(start_time)
        x2, y2 = self.p2.at_time(start_time)
        cur = _distance(x1, y1, x2, y2)
        if cur < 1e-9:
            return self
        factor = length / cur
        if anchor == 'start':
            # Keep p1 fixed, move p2
            new_p2 = (x1 + (x2 - x1) * factor, y1 + (y2 - y1) * factor)
            _anim(self.p2, start_time, end_time, new_p2, easing)
        else:
            # Keep p2 fixed, move p1
            new_p1 = (x2 - (x2 - x1) * factor, y2 - (y2 - y1) * factor)
            _anim(self.p1, start_time, end_time, new_p1, easing)
        return self

    def get_perpendicular_point(self, px, py, time=0):
        """Find the point on the line closest to ``(px, py)``.

        Uses orthogonal projection of the external point onto the infinite line
        through p1 and p2, then clamps to the segment.

        Parameters
        ----------
        px, py:
            Coordinates of the external point.
        time:
            Animation time at which to evaluate the line endpoints.

        Returns
        -------
        (x, y): the closest point on the line segment.
        """
        x1, y1 = self.p1.at_time(time)
        x2, y2 = self.p2.at_time(time)
        dx, dy = x2 - x1, y2 - y1
        seg_len_sq = dx * dx + dy * dy
        if seg_len_sq < 1e-18:
            return (float(x1), float(y1))
        # Parameter t in [0, 1] for the projection onto the segment
        t = ((px - x1) * dx + (py - y1) * dy) / seg_len_sq
        t = max(0.0, min(1.0, t))
        return (float(x1 + t * dx), float(y1 + t * dy))

    @classmethod
    def between(cls, p1, p2, **kwargs):
        """Create a Line from two (x, y) tuples."""
        return cls(p1[0], p1[1], p2[0], p2[1], **kwargs)

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
        """Create a Line from *origin* along *direction* for *length* pixels.

        Parameters
        ----------
        origin:
            Start point ``(x, y)``.
        direction:
            Direction vector ``(dx, dy)``.  Does **not** need to be a unit
            vector — it is normalised internally.  If the zero vector is given
            the end-point equals the origin.
        length:
            Length of the resulting line in pixels.
        **kwargs:
            Forwarded to the :class:`Line` constructor.

        Examples
        --------
        >>> import math
        >>> Line.from_direction((960, 540), (1, 0), 200)   # horizontal right
        >>> Line.from_direction((960, 540), (0, 1), 100)   # downward
        >>> Line.from_direction((0, 0), (1, 1), 100)       # diagonal
        """
        ox, oy = origin
        dx, dy = direction
        mag = math.sqrt(dx * dx + dy * dy)
        if mag < 1e-10:
            return cls(ox, oy, ox, oy, **kwargs)
        nx, ny = dx / mag, dy / mag
        return cls(ox, oy, ox + nx * length, oy + ny * length, **kwargs)

    @classmethod
    def from_angle(cls, origin, angle_deg, length=100, **kwargs):
        """Create a Line from *origin* at *angle_deg* degrees for *length* pixels.

        The angle follows the standard mathematical convention measured
        **counter-clockwise from the positive x-axis**.  Because SVG uses a
        y-down coordinate system, an angle of 0° points right, 90° points
        **up** (negative y direction in SVG), and 180° points left.

        Parameters
        ----------
        origin:
            Start point ``(x, y)``.
        angle_deg:
            Angle in degrees, measured counter-clockwise from the positive
            x-axis.
        length:
            Length of the resulting line in pixels (default 100).
        **kwargs:
            Forwarded to the :class:`Line` constructor.

        Returns
        -------
        Line

        Examples
        --------
        >>> Line.from_angle((960, 540), 0, 200)    # horizontal right
        >>> Line.from_angle((960, 540), 90, 100)   # upward (SVG y-down)
        >>> Line.from_angle((960, 540), 45, 100)   # 45° upper-right
        """
        ox, oy = origin
        rad = math.radians(angle_deg)
        dx = math.cos(rad)
        dy = -math.sin(rad)  # negate because SVG y-axis points downward
        return cls(ox, oy, ox + dx * length, oy + dy * length, **kwargs)

    def lerp(self, t, time=0):
        """Return point (x, y) at parameter t (0=start, 1=end) along the line."""
        x1, y1 = self.get_start(time)
        x2, y2 = self.get_end(time)
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))

    def __repr__(self):
        p1, p2 = self.p1.at_time(0), self.p2.at_time(0)
        return f'Line(({p1[0]:.0f},{p1[1]:.0f})->({p2[0]:.0f},{p2[1]:.0f}))'

    def perpendicular(self, at_proportion=0.5, length=None, time=0, **kwargs):
        """Return a new Line perpendicular to this line at the given proportion.

        at_proportion: 0 = start, 1 = end (default 0.5 = midpoint).
        length: length of the new line (defaults to same as this line).
        Extra kwargs are forwarded to the new Line constructor.
        """
        x1, y1 = self.p1.at_time(time)
        x2, y2 = self.p2.at_time(time)
        dx, dy = x2 - x1, y2 - y1
        line_len = math.sqrt(dx * dx + dy * dy)
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

    def perpendicular_at(self, t=0.5, length=100, time=0, **kwargs):
        """Return a Line perpendicular to this line at parameter t (0=start, 1=end).

        Parameters
        ----------
        t:
            Position along the line as a fraction (0 = start, 1 = end, default 0.5 = midpoint).
        length:
            Total length of the perpendicular line (default 100).
        time:
            Animation time at which to evaluate the line endpoints.
        **kwargs:
            Extra keyword arguments forwarded to the new Line constructor.
        """
        x1, y1 = self.p1.at_time(time)
        x2, y2 = self.p2.at_time(time)
        px = x1 + t * (x2 - x1)
        py = y1 + t * (y2 - y1)
        dx, dy = -(y2 - y1), x2 - x1  # perpendicular direction
        mag = math.hypot(dx, dy)
        if mag > 0:
            dx, dy = dx / mag * length / 2, dy / mag * length / 2
        return Line(x1=px - dx, y1=py - dy, x2=px + dx, y2=py + dy, **kwargs)

    def bisector(self, time=0, length=200, **kwargs):
        """Return the perpendicular bisector of this line.

        The bisector passes through the midpoint and is perpendicular to
        the line.  This is a convenience wrapper around
        ``perpendicular_at(t=0.5, ...)``.

        Parameters
        ----------
        time:
            Animation time at which to evaluate the line endpoints.
        length:
            Total length of the bisector line (default 200).
        **kwargs:
            Extra keyword arguments forwarded to the new Line constructor.
        """
        return self.perpendicular_at(t=0.5, length=length, time=time, **kwargs)

    def extend(self, factor=1.5, time=0, **kwargs):
        """Return a new Line extended in both directions by factor.

        factor=1.5 means 50% longer on each side.
        Extra kwargs are forwarded to the new Line constructor.
        """
        x1, y1 = self.p1.at_time(time)
        x2, y2 = self.p2.at_time(time)
        dx, dy = x2 - x1, y2 - y1
        extra = factor - 1
        return Line(x1 - dx * extra, y1 - dy * extra,
                    x2 + dx * extra, y2 + dy * extra, **kwargs)

    def parallel(self, offset=50, time=0, **kwargs):
        """Return a new Line parallel to this one, offset perpendicular by offset pixels.
        Extra kwargs are forwarded to the new Line constructor."""
        x1, y1 = self.p1.at_time(time)
        x2, y2 = self.p2.at_time(time)
        dx, dy = x2 - x1, y2 - y1
        line_len = math.sqrt(dx * dx + dy * dy)
        if line_len == 0:
            return Line(x1, y1, x2, y2, **kwargs)
        nx, ny = -dy / line_len, dx / line_len
        return Line(x1 + nx * offset, y1 + ny * offset,
                    x2 + nx * offset, y2 + ny * offset, **kwargs)

    def intersect_line(self, other, time=0):
        """Return intersection point (x, y) of this line with another, or None if parallel."""
        x1, y1 = self.p1.at_time(time)
        x2, y2 = self.p2.at_time(time)
        x3, y3 = other.p1.at_time(time)
        x4, y4 = other.p2.at_time(time)
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(denom) < 1e-10:
            return None
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        ix = x1 + t * (x2 - x1)
        iy = y1 + t * (y2 - y1)
        return (ix, iy)

    def project_point(self, px, py, time=0):
        """Return the closest point on this line (extended) to point (px, py)."""
        x1, y1 = self.p1.at_time(time)
        x2, y2 = self.p2.at_time(time)
        dx, dy = x2 - x1, y2 - y1
        len_sq = dx * dx + dy * dy
        if len_sq < 1e-20:
            return (x1, y1)
        t = ((px - x1) * dx + (py - y1) * dy) / len_sq
        return (x1 + t * dx, y1 + t * dy)

    def parameter_at(self, px, py, time=0):
        """Return the parameter t for the projection of (px, py) onto the line.

        The parameter t is defined such that the projection point equals
        ``p1 + t * (p2 - p1)``.  A value of 0 corresponds to p1, 1 to p2.
        The result is unclamped, so t < 0 or t > 1 means the projection
        falls outside the segment.

        Parameters
        ----------
        px, py:
            Coordinates of the external point.
        time:
            Animation time at which to evaluate the line endpoints.

        Returns
        -------
        float
            The unclamped parameter t for the closest point on the infinite
            line through p1 and p2.
        """
        x1, y1 = self.p1.at_time(time)
        x2, y2 = self.p2.at_time(time)
        dx, dy = x2 - x1, y2 - y1
        len_sq = dx * dx + dy * dy
        if len_sq < 1e-20:
            return 0.0
        return float(((px - x1) * dx + (py - y1) * dy) / len_sq)


class Text(VObject):
    """Plain SVG text element."""
    _NARROW = set('iIlj1|!.,;:\'"()[]{}')
    _WIDE = set('mMwWOQD@')

    def __init__(self, text='', x: float = 960, y: float = 540, font_size: float = 48, text_anchor=None, creation: float = 0, z=0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        self.text = attributes.String(creation, text)
        self.x = attributes.Real(creation, x)
        self.y = attributes.Real(creation, y)
        self.font_size = attributes.Real(creation, font_size)
        self._text_anchor = text_anchor
        self.styling = style.Styling(styling_kwargs, creation=creation,
                                     fill='#fff', fill_opacity=1, stroke_width=0)

    def _extra_attrs(self):
        return [self.text, self.x, self.y, self.font_size]

    def _shift_reals(self):
        return [(self.x, self.y)]

    def snap_points(self, time):
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
        x, y, fs = self.x.at_time(time), self.y.at_time(time), self.font_size.at_time(time)
        w = self._estimate_width(self.text.at_time(time), fs)
        xl = self._text_left(x, w)
        return f'M{xl},{y-fs}L{xl+w},{y-fs}L{xl+w},{y}L{xl},{y}Z'

    def bbox(self, time):
        x, y, fs = self.x.at_time(time), self.y.at_time(time), self.font_size.at_time(time)
        w = self._estimate_width(self.text.at_time(time), fs)
        return (self._text_left(x, w), y - fs, w, fs)

    def get_text(self, time=0):
        """Return the text string at the given time."""
        return self.text.at_time(time)

    def get_font_size(self, time=0):
        return self.font_size.at_time(time)

    def __repr__(self):
        t = self.text.at_time(0)
        return f'Text({t!r})' if len(t) <= 20 else f'Text({t[:17]!r}...)'

    def typing(self, start: float = 0, end: float = 1, change_existence=True):
        """Typewriter effect: reveal text character by character over [start, end]."""
        full_text = self.text.at_time(start)
        n = len(full_text)
        if n == 0:
            return self
        if change_existence:
            self._show_from(start)
        s, e = start, end
        dur = e - s
        if dur <= 0:
            self.text.set_onward(s, full_text)
            return self
        self.text.set(s, e, lambda t, _s=s, _d=dur, _n=n: full_text[:max(1, int(_n * (t - _s) / _d))], stay=True)
        return self

    def reveal_by_word(self, start=0, end=1, change_existence=True, easing=None):
        """Reveal text word by word over [start, end].

        Similar to :meth:`typing` but reveals full words at a time instead of
        individual characters.  Words are split by whitespace.
        """
        easing = easing or easings.linear
        full_text = self.text.at_time(start)
        words = full_text.split()
        if not words:
            return self
        if change_existence:
            self._show_from(start)
        n = len(words)
        dur = end - start
        if dur <= 0:
            self.text.set_onward(start, full_text)
            return self

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

    def highlight(self, start=0, end=1, color='#FFFF00', opacity=0.3, padding=4, easing=easings.there_and_back):
        """Highlight the text with a colored background rectangle that fades in/out.
        Returns the highlight Rectangle (must be added to canvas separately)."""
        bx, by, bw, bh = self.bbox(start)
        rect = Rectangle(bw + 2 * padding, bh + 2 * padding,
                         x=bx - padding, y=by - padding,
                         creation=start, fill=color, fill_opacity=0, stroke_width=0)
        dur = end - start
        if dur <= 0:
            return rect
        rect.styling.fill_opacity.set(start, end,
            lambda t, _s=start, _d=dur: opacity * easing((t - _s) / _d), stay=True)
        return rect

    def highlight_substring(self, substring, color='#FFFF00', start=0, end=1,
                            opacity=0.3, easing=easings.there_and_back):
        """Highlight a substring with a colored background rectangle.
        Returns the highlight Rectangle (must be added to canvas)."""
        text_val = str(self.text.at_time(start))
        idx = text_val.find(substring)
        if idx < 0:
            return Rectangle(0, 0, x=0, y=0)  # empty rect
        fs = self.font_size.at_time(start)
        x = self.x.at_time(start)
        y = self.y.at_time(start)
        # Adjust for text anchor
        total_w = self._estimate_width(text_val, fs)
        xl = self._text_left(x, total_w)
        # Approximate x offset to the substring
        prefix_w = self._estimate_width(text_val[:idx], fs)
        sub_w = self._estimate_width(substring, fs)
        rx = xl + prefix_w
        ry = y - fs * 0.8
        rh = fs * 1.2
        rect = Rectangle(sub_w, rh, x=rx, y=ry, creation=start,
                         fill=color, fill_opacity=0, stroke_width=0)
        dur = end - start
        if dur > 0:
            rect.styling.fill_opacity.set(start, end,
                lambda t, _s=start, _d=dur: opacity * easing((t - _s) / _d), stay=True)
        return rect

    def typewrite(self, start=0, end=1, cursor='|', change_existence=True):
        """Reveal text character by character like a typewriter.
        The text attribute is updated progressively with an optional cursor character."""
        if change_existence:
            self._show_from(start)
        full_text = self.text.at_time(start)
        n = len(full_text)
        if n == 0:
            return self
        dur = end - start
        if dur <= 0:
            return self
        s = start
        def _typed(t):
            progress = min(1, (t - s) / dur)
            chars = int(progress * n)
            shown = full_text[:chars]
            if chars < n:
                return shown + cursor
            return shown
        self.text.set(s, end, _typed, stay=True)
        self.text.set_onward(end, full_text)
        return self

    def untype(self, start=0, end=1, change_existence=True):
        """Reverse typewriter: remove characters right-to-left."""
        full_text = self.text.at_time(start)
        n = len(full_text)
        if n == 0:
            return self
        dur = end - start
        if dur <= 0:
            return self
        s = start
        def _untyped(t, _s=s, _d=dur, _n=n, _ft=full_text):
            progress = min(1, (t - _s) / _d)
            remaining = _n - int(progress * _n)
            return _ft[:max(0, remaining)]
        self.text.set(s, end, _untyped, stay=True)
        self.text.set_onward(end, '')
        if change_existence:
            self._hide_from(end)
        return self

    def scramble(self, start=0, end=1, charset=None, change_existence=True):
        """Decode/reveal text from random characters. Characters settle left-to-right."""
        if change_existence:
            self._show_from(start)
        full_text = self.text.at_time(start)
        n = len(full_text)
        if n == 0:
            return self
        dur = end - start
        if dur <= 0:
            return self
        if charset is None:
            charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%&*'
        import random
        rng = random.Random(42)  # deterministic for reproducibility
        _randoms = [[rng.choice(charset) for _ in range(20)] for _ in range(n)]
        s = start
        def _scrambled(t):
            progress = min(1, (t - s) / dur)
            settled = int(progress * n)
            result = list(full_text[:settled])
            frame = int((t - s) * 15) % 20  # cycle through pre-generated randoms
            for i in range(settled, n):
                if full_text[i] == ' ':
                    result.append(' ')
                else:
                    result.append(_randoms[i][frame])
            return ''.join(result)
        self.text.set(s, end, _scrambled, stay=True)
        self.text.set_onward(end, full_text)
        return self

    def set_font_size(self, size, start=0, end=None, easing=easings.smooth):
        """Animate font size to new value."""
        _anim(self.font_size, start, end, size, easing)
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
            lambda t, _s=start, _d=dur1: 1 - easing((t - _s) / _d), stay=True)
        self.text.set_onward(mid, new_text)
        self.styling.opacity.set(mid, end,
            lambda t, _m=mid, _d=dur2: easing((t - _m) / _d), stay=True)
        return self

    def underline_anim(self, start: float = 0, end: float = 1, color=None,
                        stroke_width=2, offset_y=5):
        """Create an animated underline under this text. Returns a Line object."""
        bx, by, bw, bh = self.bbox(start)
        line_y = by + bh + offset_y
        line_color = color or self.styling.fill.at_time(start)
        line = Line(x1=bx, y1=line_y, x2=bx, y2=line_y, creation=start,
                    stroke=line_color, stroke_width=stroke_width)
        dur = end - start
        if dur > 0:
            s, x1, x2 = start, bx, bx + bw
            line.p2.set(s, end,
                lambda t, _s=s, _d=dur, _x1=x1, _x2=x2, _y=line_y: (
                    _x1 + (_x2 - _x1) * easings.smooth((t - _s) / _d), _y),
                stay=True)
        return line

    def split_words(self, time=0):
        """Split text into a VCollection of individual word Text objects.
        Words are positioned horizontally at approximate character offsets."""
        from vectormation._base import VCollection
        full = str(self.text.at_time(time))
        words = full.split()
        if not words:
            return VCollection()
        x = self.x.at_time(time)
        y = self.y.at_time(time)
        fs = self.font_size.at_time(time)
        char_width = fs * CHAR_WIDTH_FACTOR
        parts = []
        cursor = 0
        for word in words:
            idx = full.index(word, cursor)
            wx = x + idx * char_width
            t = Text(text=word, x=wx, y=y, font_size=fs,
                     creation=time, stroke_width=0,
                     fill=self.styling.fill.time_func(time))
            parts.append(t)
            cursor = idx + len(word)
        return VCollection(*parts)

    def split_chars(self, time=0):
        """Split text into a VCollection of individual character Text objects.
        Characters are positioned horizontally at approximate character offsets."""
        from vectormation._base import VCollection
        full = str(self.text.at_time(time))
        if not full:
            return VCollection()
        x = self.x.at_time(time)
        y = self.y.at_time(time)
        fs = self.font_size.at_time(time)
        char_width = fs * CHAR_WIDTH_FACTOR
        chars = []
        for i, ch in enumerate(full):
            if ch == ' ':
                continue
            cx = x + i * char_width
            t = Text(text=ch, x=cx, y=y, font_size=fs,
                     creation=time, stroke_width=0,
                     fill=self.styling.fill.time_func(time))
            chars.append(t)
        return VCollection(*chars)

    def char_count(self):
        """Return the number of characters in the text string at time 0."""
        return len(self.text.at_time(0))

    def word_count(self, time=0):
        """Return the number of words in the text at the given time.

        Words are defined by Python's :meth:`str.split` (splits on any
        whitespace, ignoring leading/trailing spaces).

        Parameters
        ----------
        time:
            Animation time at which to read the text (default 0).

        Returns
        -------
        int

        Example
        -------
        >>> t = Text('hello world foo')
        >>> t.word_count()
        3
        >>> Text('  ').word_count()
        0
        """
        return len(self.text.at_time(time).split())

    def word_at(self, index, time=0):
        """Return the word at the given index."""
        text = self.text.at_time(time)
        if isinstance(text, str):
            words = text.split()
            if 0 <= index < len(words):
                return words[index]
        return ''

    def fit_to_box(self, max_width, max_height=None, time=0):
        """Adjust font_size so the text fits within the given box dimensions.

        Uses width estimation to find appropriate font size.
        Returns self for chaining.
        """
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

    def to_upper(self, time=0):
        """Change text to uppercase at given time."""
        full = self.text.at_time(time)
        if isinstance(full, str):
            self.text.set_onward(time, full.upper())
        return self

    def to_lower(self, time=0):
        """Change text to lowercase at given time."""
        full = self.text.at_time(time)
        if isinstance(full, str):
            self.text.set_onward(time, full.lower())
        return self

    def char_at(self, index, time=0):
        """Return the character at the given index."""
        text = self.text.at_time(time)
        if isinstance(text, str) and 0 <= index < len(text):
            return text[index]
        return ''

    def to_svg(self, time):
        anchor = f" text-anchor='{self._text_anchor}'" if self._text_anchor else ''
        txt = _xml_escape(str(self.text.at_time(time)))
        return (f"<text x='{self.x.at_time(time)}' y='{self.y.at_time(time)}'"
                f" font-size='{self.font_size.at_time(time)}'{anchor}{self.styling.svg_style(time)}"
                f">{txt}</text>")


class CountAnimation(Text):
    """Text that animates a number counting from start_val to end_val."""
    def __init__(self, start_val=0, end_val=100, start: float = 0, end: float = 1,
                 fmt='{:.0f}', easing=easings.smooth,
                 x: float = 960, y: float = 540, font_size: float = 60, text_anchor=None, creation: float = 0, z=0, **styling_kwargs):
        super().__init__(text=fmt.format(start_val), x=x, y=y,
                         font_size=font_size, text_anchor=text_anchor,
                         creation=creation, z=z, **styling_kwargs)
        s, e = start, end
        dur = e - s
        if dur <= 0:
            self.text.set_onward(s, fmt.format(end_val))
        else:
            self.text.set(s, e,
                lambda t, _s=s, _d=dur, _sv=start_val, _ev=end_val, _fmt=fmt: _fmt.format(_sv + (_ev - _sv) * easing((t - _s) / _d)),
                stay=True)
        self._fmt = fmt
        self._last_val = end_val

    def count_to(self, target, start, end, easing=easings.smooth):
        """Animate counting from the current value to a new target."""
        from_val = self._last_val
        fmt = self._fmt
        dur = end - start
        if dur <= 0:
            self.text.set_onward(start, fmt.format(target))
        else:
            s = start
            self.text.set(s, end,
                lambda t, _f=from_val, _t=target, _s=s, _d=dur, _fmt=fmt:
                    _fmt.format(_f + (_t - _f) * easing((t - _s) / _d)),
                stay=True)
        self._last_val = target
        return self


class ValueTracker:
    """Convenience wrapper around a time-varying Real attribute.

    Use to drive reactive animations (e.g. link a label's position to a value).
    """
    def __init__(self, value=0, creation=0):
        self.value = attributes.Real(creation, value)
        self.show = attributes.Real(creation, True)

    @property
    def last_change(self):
        return self.value.last_change

    def get_value(self, time=0):
        return self.value.at_time(time)

    def set_value(self, val, start=0):
        self.value.set_onward(start, val)
        return self

    def animate_value(self, target, start, end, easing=easings.smooth):
        self.value.move_to(start, end, target, easing=easing)
        return self

    def at_time(self, time):
        return self.value.at_time(time)


class DecimalNumber(Text):
    """Text that dynamically displays a numeric value, updating each frame.

    value: initial numeric value, or an attributes.Real / ValueTracker to track.
    fmt: format string for display.
    """
    def __init__(self, value: 'float | ValueTracker | attributes.Real' = 0, fmt='{:.2f}', x=960, y=540, font_size=48,
                 text_anchor=None, creation=0, z=0, **styling_kwargs):
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
        return self._tracker

    def set_value(self, val, start=0):
        self._tracker.set_onward(start, val)
        return self

    def animate_value(self, target, start, end, easing=easings.smooth):
        self._tracker.move_to(start, end, target, easing=easing)
        return self


class Lines(Polygon):
    """Open polyline — a Polygon with closed=False."""
    def __init__(self, *vertices, creation=0, z=0, **styling_kwargs):
        super().__init__(*vertices, closed=False, creation=creation, z=z, **styling_kwargs)

    def __repr__(self):
        return f'Lines({len(self.vertices)} vertices)'


class Trace(VObject):
    """Follows a point every dt and renders as a polyline."""
    def __init__(self, point, start=0, end=None, dt=1/60, z=0, **styling_kwargs):
        super().__init__(creation=start, z=z)
        self.start = start
        self.end = end
        self.dt = dt
        self.p = point
        self.styling = style.Styling(styling_kwargs, creation=start, stroke='#fff', stroke_width=DEFAULT_STROKE_WIDTH)
        self._vert_cache = []
        self._str_parts = []  # List of "x,y" strings

    def _extra_attrs(self):
        return [self.p]

    def snap_points(self, time):
        pos = self.p.at_time(time)
        return [(float(pos[0]), float(pos[1]))]

    def shift(self, dx=0, dy=0, start_time: float = 0, end_time: float | None = None, easing=easings.smooth):
        """Shift via styling transform (Trace points are immutable)."""
        if end_time is None:
            self.styling.dx.add_onward(start_time, dx)
            self.styling.dy.add_onward(start_time, dy)
        else:
            s, e = start_time, end_time
            d = max(e - s, 1e-9)
            self.styling.dx.add_onward(s, lambda t, _s=s, _d=d: dx * easing((t-_s)/_d), last_change=e)
            self.styling.dy.add_onward(s, lambda t, _s=s, _d=d: dy * easing((t-_s)/_d), last_change=e)
        return self

    def path(self, time):
        verts = self.vertices(time)
        if not verts:
            return ''
        parts = [f'M {verts[0][0]},{verts[0][1]}']
        parts.extend(f'L {x},{y}' for x, y in verts[1:])
        return ' '.join(parts)

    def vertices(self, time):
        end = min(self.end, time) if self.end is not None else time
        steps = int((end - self.start) / self.dt)
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

    def to_svg(self, time):
        self.vertices(time)
        end = min(self.end, time) if self.end is not None else time
        steps = int((end - self.start) / self.dt)
        if steps == 0:
            return ''
        pts = ' '.join(self._str_parts[:steps])
        cur = self.p.at_time(time)
        return f"<polyline points='{pts} {cur[0]},{cur[1]}'{self.styling.svg_style(time)} />"

    def to_polygon(self, time):
        return Polygon(*self.vertices(time), creation=time, z=self.z.at_time(time), **self.styling.kwargs())

    def __repr__(self):
        return f'Trace({len(self._vert_cache)} points)'

class Path(VObject):
    """SVG path element with a 'd' attribute."""
    def __init__(self, path, x=0, y=0, creation: float = 0, z=0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        self.d = attributes.String(creation, path)
        self.styling = style.Styling(styling_kwargs, creation=creation, stroke='#fff')
        self.styling.dx.add_onward(creation, lambda t: x * self.styling.scale_x.at_time(t))
        self.styling.dy.add_onward(creation, lambda t: y * self.styling.scale_y.at_time(t))

    def _extra_attrs(self):
        return [self.d]

    def snap_points(self, time):
        d = self.d.at_time(time)
        if d:
            xmin, xmax, ymin, ymax = path_bbox(d)
            return [(float(xmin), float(ymin)), (float(xmax), float(ymin)),
                    (float(xmax), float(ymax)), (float(xmin), float(ymax))]
        return []

    def shift(self, dx=0, dy=0, start_time: float = 0, end_time: float | None = None, easing=easings.smooth):
        """Shift via transform styling, accounting for current rotation."""
        rot = self.styling.rotation.at_time(0)
        if rot[0] != 0:
            dx, dy = _rotate_point(dx, dy, rot[1], rot[2], -rot[0] * math.pi / 180)
        if end_time is None:
            self.styling.dx.add_onward(start_time, dx)
            self.styling.dy.add_onward(start_time, dy)
        else:
            s, e = start_time, end_time
            d = max(e - s, 1e-9)
            self.styling.dx.add_onward(s, lambda t, _s=s, _d=d: dx * easing((t-_s)/_d), last_change=e)
            self.styling.dy.add_onward(s, lambda t, _s=s, _d=d: dy * easing((t-_s)/_d), last_change=e)
        return self

    def __repr__(self):
        d = self.d.at_time(0)
        short = d[:30] + '...' if len(d) > 30 else d
        return f"Path(d='{short}')"

    @staticmethod
    def _parse_path_lazy(d):
        try:
            from svgpathtools import parse_path
        except ImportError:
            raise ImportError("svgpathtools is required for path operations")
        return parse_path(d)

    def get_length(self, time=0):
        """Return the total length of the path."""
        d = self.d.at_time(time)
        return self._parse_path_lazy(d).length() if d else 0.0

    def point_from_proportion(self, proportion, time=0):
        """Return (x, y) at a proportional distance along the path (0-1)."""
        d = self.d.at_time(time)
        if not d:
            return (0, 0)
        parsed = self._parse_path_lazy(d)
        total = parsed.length()
        if total == 0:
            pt = parsed.point(0)
            return (pt.real, pt.imag)
        pt = parsed.point(parsed.ilength(total * max(0, min(1, proportion))))
        return (pt.real, pt.imag)

    def path(self, time):
        return self.d.at_time(time)

    def to_svg(self, time):
        return f"<path d='{self.d.at_time(time)}'{self.styling.svg_style(time)} />"

    @classmethod
    def from_points(cls, points, closed=False, smooth=False, **kwargs):
        """Create a Path from a list of (x, y) points.

        If smooth=False, straight line segments are used (M x,y L x,y ...).
        If smooth=True, Catmull-Rom splines are used for smooth interpolation,
        converted to cubic Bezier curves.
        If closed=True, the path ends with a Z command.
        """
        pts = list(points)
        if not pts:
            return cls('', **kwargs)
        if len(pts) == 1:
            x, y = pts[0]
            return cls(f'M{x},{y}', **kwargs)

        if not smooth:
            parts = [f'M{pts[0][0]},{pts[0][1]}']
            for x, y in pts[1:]:
                parts.append(f'L{x},{y}')
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
    def __init__(self, href, x=0, y=0, width=1, height=1, creation=0, z=0, **styling_kwargs):
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
        x, y = self.x.at_time(time), self.y.at_time(time)
        w, h = self.width.at_time(time), self.height.at_time(time)
        return f'M{x},{y}L{x+w},{y}L{x+w},{y+h}L{x},{y+h}Z'

    def bbox(self, time):
        x, y = self.x.at_time(time), self.y.at_time(time)
        w, h = self.width.at_time(time), self.height.at_time(time)
        return self._bbox_from_points([(x,y),(x+w,y),(x+w,y+h),(x,y+h)], time) or super().bbox(time)

    def __repr__(self):
        return f'Image({self.width.at_time(0):.0f}x{self.height.at_time(0):.0f})'

    def to_svg(self, time):
        return (f"<image href='{self.href}' x='{self.x.at_time(time)}' y='{self.y.at_time(time)}'"
                f" width='{self.width.at_time(time)}' height='{self.height.at_time(time)}'"
                f"{self.styling.svg_style(time)} />")


class RegularPolygon(Polygon):
    """Regular n-sided polygon inscribed in a circle of given radius."""
    def __init__(self, n, radius=120, cx=960, cy=540, angle=0, creation=0, z=0, **styling_kwargs):
        n = max(n, 1)
        self._n = n
        self._radius = radius
        angle_rad = angle * math.pi / 180
        vertices = [
            (cx + radius * math.cos(2 * math.pi * k / n + angle_rad),
             cy - radius * math.sin(2 * math.pi * k / n + angle_rad))
            for k in range(n)
        ]
        super().__init__(*vertices, creation=creation, z=z, **styling_kwargs)

    def get_side_length(self, time=0):
        """Return the side length of the regular polygon.
        Computed from the circumradius: side = 2 * r * sin(pi / n)."""
        return 2 * self._radius * math.sin(math.pi / self._n)

    def get_inradius(self, time=0):
        """Return the inradius (apothem) of the regular polygon.
        Computed from the circumradius: inradius = r * cos(pi / n)."""
        return self._radius * math.cos(math.pi / self._n)

    def get_apothem(self, time=0):
        """Return the apothem of the regular polygon (alias for :meth:`get_inradius`)."""
        return self.get_inradius(time)

    def get_circumradius(self, time=0):
        """Return the circumscribed circle radius."""
        return self._radius

    def __repr__(self):
        return f'RegularPolygon(n={self._n}, r={self._radius:.0f})'


class Star(Polygon):
    """Star polygon with n outer points. outer_radius and inner_radius control the shape."""
    def __init__(self, n=5, outer_radius=120, inner_radius=None, cx=960, cy=540,
                 angle=90, creation=0, z=0, **styling_kwargs):
        n = max(n, 1)
        if inner_radius is None:
            inner_radius = outer_radius * 0.4
        self._n = n
        self._outer_radius = outer_radius
        self._inner_radius = inner_radius
        angle_rad = angle * math.pi / 180
        vertices = []
        for k in range(2 * n):
            r = outer_radius if k % 2 == 0 else inner_radius
            a = math.pi * k / n + angle_rad
            vertices.append((cx + r * math.cos(a), cy - r * math.sin(a)))
        super().__init__(*vertices, creation=creation, z=z, **styling_kwargs)

    def get_outer_radius(self):
        """Return the outer (tip) radius of the star."""
        return self._outer_radius

    def get_inner_radius(self):
        """Return the inner (valley) radius of the star."""
        return self._inner_radius

    def __repr__(self):
        return f'Star(n={self._n}, outer={self._outer_radius:.0f}, inner={self._inner_radius:.0f})'


class EquilateralTriangle(RegularPolygon):
    """Equilateral triangle: RegularPolygon with n=3.
    side_length is converted to the circumscribed radius."""
    def __init__(self, side_length, angle=0, cx=960, cy=540, creation=0, z=0, **styling_kwargs):
        self._side_length = side_length
        radius = side_length / math.sqrt(3)
        super().__init__(3, radius=radius, cx=cx, cy=cy, angle=angle + 90,
                         creation=creation, z=z, **styling_kwargs)

    def __repr__(self):
        return f'EquilateralTriangle(side={self._side_length:.0f})'


class RoundedRectangle(Rectangle):
    """Rectangle with rounded corners (default corner_radius=10)."""
    def __init__(self, width, height, x=960, y=540, corner_radius=12, creation=0, z=0, **styling_kwargs):
        super().__init__(width, height, x=x, y=y, rx=corner_radius, ry=corner_radius,
                         creation=creation, z=z, **styling_kwargs)

    def __repr__(self):
        return f'RoundedRectangle({self.width.at_time(0):.0f}x{self.height.at_time(0):.0f}, r={self.rx.at_time(0):.0f})'

    def get_corner_radius(self, time=0):
        return self.rx.at_time(time)

    def set_corner_radius(self, value, start=0, end=None, easing=easings.smooth):
        """Animate corner radius to value."""
        _anim(self.rx, start, end, value, easing)
        _anim(self.ry, start, end, value, easing)
        return self


class SurroundingRectangle(RoundedRectangle):
    """Rectangle that surrounds a target object with padding.
    If follow=True (default), tracks the target as it moves."""
    def __init__(self, target, buff=SMALL_BUFF, corner_radius=6, follow=True,
                 creation=0, z=0, **styling_kwargs):
        bx, by, bw, bh = target.bbox(creation)
        style_kw = {'fill_opacity': 0, 'stroke': '#FFFF00'} | styling_kwargs
        super().__init__(bw + 2*buff, bh + 2*buff, x=bx - buff, y=by - buff,
                         corner_radius=corner_radius, creation=creation, z=z, **style_kw)
        if follow:
            _cache = [None, None]
            def _bbox(t):
                if _cache[0] != t:
                    _cache[0] = t
                    _cache[1] = target.bbox(t)
                return _cache[1]
            self.x.set_onward(creation, lambda t: _bbox(t)[0] - buff)
            self.y.set_onward(creation, lambda t: _bbox(t)[1] - buff)
            self.width.set_onward(creation, lambda t: _bbox(t)[2] + 2*buff)
            self.height.set_onward(creation, lambda t: _bbox(t)[3] + 2*buff)


class SurroundingCircle(Circle):
    """Circle that surrounds a target object with padding.
    If follow=True (default), tracks the target as it moves."""
    def __init__(self, target, buff=SMALL_BUFF, follow=True,
                 creation=0, z=0, **styling_kwargs):
        bx, by, bw, bh = target.bbox(creation)
        r = math.hypot(bw, bh) / 2 + buff
        cx, cy = bx + bw / 2, by + bh / 2
        style_kw = {'fill_opacity': 0, 'stroke': '#FFFF00'} | styling_kwargs
        super().__init__(r=r, cx=cx, cy=cy, creation=creation, z=z, **style_kw)
        if follow:
            _cache = [None, None]
            def _bbox(t):
                if _cache[0] != t:
                    _cache[0] = t
                    _cache[1] = target.bbox(t)
                return _cache[1]
            self.c.set_onward(creation, lambda t: (_bbox(t)[0] + _bbox(t)[2] / 2,
                                                    _bbox(t)[1] + _bbox(t)[3] / 2))
            _r_func = lambda t: math.hypot(_bbox(t)[2], _bbox(t)[3]) / 2 + buff
            self.rx.set_onward(creation, _r_func)
            self.ry.set_onward(creation, _r_func)


class BackgroundRectangle(Rectangle):
    """Semi-transparent rectangle behind a target object (useful for text backgrounds)."""
    def __init__(self, target, buff=SMALL_BUFF, creation=0, z=-1, **styling_kwargs):
        bx, by, bw, bh = target.bbox(creation)
        style_kw = {'fill': '#000', 'fill_opacity': 0.75, 'stroke_width': 0} | styling_kwargs
        super().__init__(bw + 2*buff, bh + 2*buff, x=bx - buff, y=by - buff,
                         creation=creation, z=z, **style_kw)


class Arc(VObject):
    """SVG arc segment defined by centre, radius, and start/end angles (degrees)."""
    def __init__(self, cx: float = 960, cy: float = 540, r: float = 120, start_angle: float = 0, end_angle: float = 90,
                 creation=0, z=0, **styling_kwargs):
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
        return [(float(self.cx.at_time(time)), float(self.cy.at_time(time)))]

    def bbox(self, time):
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
        cx, cy, r = self.cx.at_time(time), self.cy.at_time(time), self.r.at_time(time)
        sa, ea = self.start_angle.at_time(time), self.end_angle.at_time(time)
        sa_rad, ea_rad = math.radians(sa), math.radians(ea)
        x1, y1 = cx + r * math.cos(sa_rad), cy - r * math.sin(sa_rad)
        x2, y2 = cx + r * math.cos(ea_rad), cy - r * math.sin(ea_rad)
        large = 1 if abs(ea - sa) % 360 > 180 else 0
        sweep = 0 if ea > sa else 1
        return f'M{x1},{y1}A{r},{r} 0 {large},{sweep} {x2},{y2}'

    def get_start_point(self, time=0):
        """Return the (x, y) position at the start of the arc."""
        return self.point_at_angle(self.start_angle.at_time(time), time)

    def get_end_point(self, time=0):
        """Return the (x, y) position at the end of the arc."""
        return self.point_at_angle(self.end_angle.at_time(time), time)

    def get_arc_length(self, time=0):
        """Return the arc length (r * angle_in_radians)."""
        r = self.r.at_time(time)
        sweep = abs(self.end_angle.at_time(time) - self.start_angle.at_time(time))
        return r * math.radians(sweep)

    def get_chord_length(self, time=0):
        """Return the length of the chord from start point to end point."""
        p1 = self.get_start_point(time)
        p2 = self.get_end_point(time)
        return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

    def get_sweep(self, time=0):
        """Return the total sweep angle in degrees."""
        return abs(self.end_angle.at_time(time) - self.start_angle.at_time(time))

    def point_at_angle(self, degrees, time=0):
        """Return (x, y) on the arc at the given angle (degrees, CCW from right)."""
        cx, cy = self.cx.at_time(time), self.cy.at_time(time)
        r = self.r.at_time(time)
        rad = math.radians(degrees)
        return (cx + r * math.cos(rad), cy - r * math.sin(rad))

    def set_radius(self, value, start=0, end=None, easing=easings.smooth):
        """Animate or set the arc radius."""
        _anim(self.r, start, end, value, easing)
        return self

    def set_angles(self, start_angle=None, end_angle=None, start=0, end=None, easing=easings.smooth):
        """Animate or set the arc start/end angles (degrees)."""
        if start_angle is not None:
            _anim(self.start_angle, start, end, start_angle, easing)
        if end_angle is not None:
            _anim(self.end_angle, start, end, end_angle, easing)
        return self

    def get_midpoint(self, time=0):
        """Return the point at the midpoint angle of the arc."""
        mid = (self.start_angle.at_time(time) + self.end_angle.at_time(time)) / 2
        return self.point_at_angle(mid, time)

    def get_midpoint_on_arc(self, time=0):
        """Return the point at the middle of the arc curve.

        This computes the angle midway between ``start_angle`` and
        ``end_angle`` and returns the corresponding (x, y) point on the arc.
        Equivalent to :meth:`get_midpoint` — provided for API clarity when the
        caller wants to emphasise that the result lies *on the arc* rather
        than at the midpoint of the chord.

        Parameters
        ----------
        time:
            Animation time at which to evaluate the arc geometry.
        """
        return self.get_midpoint(time)

    def to_wedge(self, time=0, **kwargs):
        """Return a :class:`Wedge` with the same geometry as this arc at *time*.

        The result is a static snapshot — it is not dynamically linked to the
        original arc.  Styling from the arc is not copied; pass ``**kwargs`` to
        set fill, stroke, etc. on the resulting wedge.

        Parameters
        ----------
        time:
            Time at which to read the arc's center, radius and angles.
        **kwargs:
            Forwarded to :class:`Wedge`.

        Returns
        -------
        Wedge

        Example
        -------
        >>> arc = Arc(cx=500, cy=400, r=100, start_angle=30, end_angle=120)
        >>> wedge = arc.to_wedge(fill='#44aaff', fill_opacity=0.6)
        """
        return Wedge(
            cx=self.cx.at_time(time),
            cy=self.cy.at_time(time),
            r=self.r.at_time(time),
            start_angle=self.start_angle.at_time(time),
            end_angle=self.end_angle.at_time(time),
            **kwargs,
        )

    @classmethod
    def from_three_points(cls, p1, p2, p3, **kwargs):
        """Create an Arc through three points (x, y tuples).

        Computes the circumscribed circle of the three points and returns an
        Arc that passes through all three in order (p1 -> p2 -> p3).

        Raises ValueError if the points are collinear.
        """
        ax, ay = p1
        bx, by = p2
        cx, cy = p3
        D = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
        if abs(D) < 1e-10:
            raise ValueError("Points are collinear; cannot define an arc")
        a2 = ax * ax + ay * ay
        b2 = bx * bx + by * by
        c2 = cx * cx + cy * cy
        ux = (a2 * (by - cy) + b2 * (cy - ay) + c2 * (ay - by)) / D
        uy = (a2 * (cx - bx) + b2 * (ax - cx) + c2 * (bx - ax)) / D
        r = math.hypot(ax - ux, ay - uy)
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

    def __repr__(self):
        return f'Arc(r={self.r.at_time(0):.0f}, {self.start_angle.at_time(0):.0f}°-{self.end_angle.at_time(0):.0f}°)'

    def to_svg(self, time):
        return f"<path d='{self.path(time)}'{self.styling.svg_style(time)} />"


class Wedge(Arc):
    """Arc that closes through the centre (pie/wedge shape)."""
    def __init__(self, cx: float = 960, cy: float = 540, r: float = 120, start_angle: float = 0, end_angle: float = 90,
                 creation=0, z=0, **styling_kwargs):
        super().__init__(cx=cx, cy=cy, r=r, start_angle=start_angle, end_angle=end_angle,
                         creation=creation, z=z, **({'fill_opacity': 0.7, 'stroke': '#fff', 'stroke_width': 5} | styling_kwargs))

    def get_area(self, time=0):
        """Return the area of the wedge (0.5 * r^2 * sweep_in_radians)."""
        r = self.r.at_time(time)
        sweep = abs(self.end_angle.at_time(time) - self.start_angle.at_time(time))
        return 0.5 * r * r * math.radians(sweep)

    def to_arc(self, time=0, **kwargs):
        """Return an :class:`Arc` with the same geometry as this wedge at *time*.

        The result is a static snapshot — it is not dynamically linked to the
        original wedge.  Styling from the wedge is not copied; pass ``**kwargs``
        to set stroke, fill, etc. on the resulting arc.

        Parameters
        ----------
        time:
            Time at which to read the wedge's center, radius, and angles.
        **kwargs:
            Forwarded to :class:`Arc`.

        Returns
        -------
        Arc

        Example
        -------
        >>> wedge = Wedge(cx=500, cy=400, r=100, start_angle=30, end_angle=120)
        >>> arc = wedge.to_arc(stroke='#44aaff', stroke_width=3)
        """
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
        return super().path(time) + f'L{self.cx.at_time(time)},{self.cy.at_time(time)}Z'


class Annulus(VObject):
    """Ring/donut shape defined by inner and outer radius."""
    def __init__(self, inner_radius=60, outer_radius=120, cx=960, cy=540,
                 creation=0, z=0, **styling_kwargs):
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
        cx, cy = self.c.at_time(time)
        return [(float(cx), float(cy))]

    def bbox(self, time):
        cx, cy = self.c.at_time(time)
        r = self.outer_r.at_time(time)
        return self._bbox_from_points([(cx-r, cy-r), (cx+r, cy-r), (cx+r, cy+r), (cx-r, cy+r)], time) or super().bbox(time)

    def path(self, time):
        cx, cy = self.c.at_time(time)
        ri, ro = self.inner_r.at_time(time), self.outer_r.at_time(time)
        # Outer circle CW, then inner circle CCW (creates a ring with even-odd fill)
        return (f'M{cx-ro},{cy}a{ro},{ro} 0 1,0 {ro*2},0a{ro},{ro} 0 1,0 -{ro*2},0z'
                f'M{cx-ri},{cy}a{ri},{ri} 0 1,1 {ri*2},0a{ri},{ri} 0 1,1 -{ri*2},0z')

    def __repr__(self):
        return f'Annulus(inner={self.inner_r.at_time(0):.0f}, outer={self.outer_r.at_time(0):.0f})'

    def get_inner_radius(self, time=0):
        return self.inner_r.at_time(time)

    def get_outer_radius(self, time=0):
        return self.outer_r.at_time(time)

    def set_inner_radius(self, value, start=0, end=None, easing=easings.smooth):
        """Animate or set the inner radius."""
        _anim(self.inner_r, start, end, value, easing)
        return self

    def set_outer_radius(self, value, start=0, end=None, easing=easings.smooth):
        """Animate or set the outer radius."""
        _anim(self.outer_r, start, end, value, easing)
        return self

    def get_area(self, time=0):
        """Return the area of the annulus (pi * (outer^2 - inner^2))."""
        ri, ro = self.inner_r.at_time(time), self.outer_r.at_time(time)
        return math.pi * (ro * ro - ri * ri)

    def set_radii(self, inner=None, outer=None, start=0, end=None, easing=easings.smooth):
        """Set inner and/or outer radius."""
        if inner is not None:
            self.set_inner_radius(inner, start, end, easing)
        if outer is not None:
            self.set_outer_radius(outer, start, end, easing)
        return self

    def to_svg(self, time):
        return f"<path d='{self.path(time)}' fill-rule='evenodd'{self.styling.svg_style(time)} />"


class DashedLine(Line):
    """Line with a dashed stroke pattern."""
    def __init__(self, x1: float = 0, y1: float = 0, x2: float = 100, y2: float = 100, dash='10,5', creation=0, z=0, **styling_kwargs):
        super().__init__(x1=x1, y1=y1, x2=x2, y2=y2, creation=creation, z=z,
                         **({'stroke_dasharray': dash} | styling_kwargs))

    def __repr__(self):
        p1, p2 = self.p1.at_time(0), self.p2.at_time(0)
        return f'DashedLine(({p1[0]:.0f},{p1[1]:.0f})->({p2[0]:.0f},{p2[1]:.0f}))'

    def set_dash_pattern(self, dash, gap=None, start=0, end=None, easing=easings.smooth):
        """Set the dash pattern. If gap is None, gap = dash."""
        if gap is None:
            gap = dash
        pattern = f'{dash},{gap}'
        self.styling.stroke_dasharray.set_onward(start, pattern)
        return self


class ScreenRectangle(Rectangle):
    """A rectangle with the canvas aspect ratio (16:9).
    height is derived from width automatically."""
    def __init__(self, width=480, creation=0, z=0, **kwargs):
        height = width * 9 / 16
        super().__init__(width=width, height=height, creation=creation, z=z, **kwargs)


class ArcBetweenPoints(Arc):
    """Arc connecting two points, bulging by a given angle.

    angle: how much the arc bulges (degrees). Positive = left of start→end.
    """
    def __init__(self, start, end, angle=60, creation=0, z=0, **styling_kwargs):
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


class Elbow(Lines):
    """Right-angle connector (L-shape) between two directions.

    width/height: pixel size of each arm.
    """
    def __init__(self, cx=960, cy=540, width=40, height=40,
                 creation=0, z=0, **styling_kwargs):
        style_kw = {'stroke': '#fff', 'stroke_width': DEFAULT_STROKE_WIDTH, 'fill_opacity': 0} | styling_kwargs
        super().__init__(
            (cx + width, cy), (cx, cy), (cx, cy + height),
            creation=creation, z=z, **style_kw)


class AnnularSector(Arc):
    """Sector of an annulus (ring wedge).

    Like a Wedge but with an inner radius cut out.
    """
    def __init__(self, inner_radius=60, outer_radius=120, cx=960, cy=540,
                 start_angle=0, end_angle=90, creation=0, z=0, **styling_kwargs):
        super().__init__(cx=cx, cy=cy, r=outer_radius, start_angle=start_angle,
                         end_angle=end_angle, creation=creation, z=z,
                         **({'fill_opacity': 0.7, 'stroke': '#fff', 'stroke_width': DEFAULT_STROKE_WIDTH} | styling_kwargs))
        self.inner_r = attributes.Real(creation, inner_radius)

    def _extra_attrs(self):
        return super()._extra_attrs() + [self.inner_r]

    def path(self, time):
        cx, cy, ro = self.cx.at_time(time), self.cy.at_time(time), self.r.at_time(time)
        ri = self.inner_r.at_time(time)
        sa, ea = self.start_angle.at_time(time), self.end_angle.at_time(time)
        sa_rad, ea_rad = math.radians(sa), math.radians(ea)
        # Outer arc
        ox1, oy1 = cx + ro * math.cos(sa_rad), cy - ro * math.sin(sa_rad)
        ox2, oy2 = cx + ro * math.cos(ea_rad), cy - ro * math.sin(ea_rad)
        # Inner arc (reversed)
        ix1, iy1 = cx + ri * math.cos(ea_rad), cy - ri * math.sin(ea_rad)
        ix2, iy2 = cx + ri * math.cos(sa_rad), cy - ri * math.sin(sa_rad)
        large = 1 if abs(ea - sa) % 360 > 180 else 0
        sweep_out = 0 if ea > sa else 1
        sweep_in = 1 - sweep_out
        return (f'M{ox1},{oy1}A{ro},{ro} 0 {large},{sweep_out} {ox2},{oy2}'
                f'L{ix1},{iy1}A{ri},{ri} 0 {large},{sweep_in} {ix2},{iy2}Z')

    def set_inner_radius(self, value, start=0, end=None, easing=easings.smooth):
        _anim(self.inner_r, start, end, value, easing)
        return self

    def get_area(self, time=0):
        ri = self.inner_r.at_time(time)
        ro = self.r.at_time(time)
        angle1 = self.start_angle.at_time(time)
        angle2 = self.end_angle.at_time(time)
        return 0.5 * abs(angle2 - angle1) * math.pi / 180 * (ro * ro - ri * ri)

    def to_svg(self, time):
        return f"<path d='{self.path(time)}'{self.styling.svg_style(time)} />"


class CubicBezier(VObject):
    """Cubic Bezier curve from four control points."""
    def __init__(self, p0=(860, 540), p1=(910, 440), p2=(1010, 440), p3=(1060, 540),
                 creation=0, z=0, **styling_kwargs):
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
        return [self.p0.at_time(time), self.p3.at_time(time)]

    def bbox(self, time):
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
        x0, y0, x1, y1, x2, y2, x3, y3 = self._cps(time)
        return f'M{x0},{y0}C{x1},{y1} {x2},{y2} {x3},{y3}'

    def point_at(self, t, time=0):
        """Evaluate point on curve at parameter t (0 to 1)."""
        x0, y0, x1, y1, x2, y2, x3, y3 = self._cps(time)
        u = 1 - t
        return (u**3*x0 + 3*u**2*t*x1 + 3*u*t**2*x2 + t**3*x3,
                u**3*y0 + 3*u**2*t*y1 + 3*u*t**2*y2 + t**3*y3)

    def tangent_at(self, t, time=0):
        """Return the unit tangent direction (dx, dy) at parameter t."""
        x0, y0, x1, y1, x2, y2, x3, y3 = self._cps(time)
        u = 1 - t
        dx = 3*u*u*(x1-x0) + 6*u*t*(x2-x1) + 3*t*t*(x3-x2)
        dy = 3*u*u*(y1-y0) + 6*u*t*(y2-y1) + 3*t*t*(y3-y2)
        mag = math.hypot(dx, dy)
        return (dx / mag, dy / mag) if mag > 1e-9 else (1.0, 0.0)

    def to_svg(self, time):
        return f"<path d='{self.path(time)}'{self.styling.svg_style(time)} />"


class Paragraph(VObject):
    """Multi-line text with alignment and line spacing.

    alignment: 'left', 'center', or 'right'.
    line_spacing: multiplier for vertical spacing between lines.
    """
    def __init__(self, *lines, x=960, y=540, font_size=36, alignment='left',
                 line_spacing=1.4, creation=0, z=0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        self.lines = list(lines)
        self.x = attributes.Real(creation, x)
        self.y = attributes.Real(creation, y)
        self.font_size = font_size
        self.alignment = alignment
        self.line_spacing = line_spacing
        defaults = dict(fill='#fff', stroke_width=0)
        self.styling = style.Styling(styling_kwargs, creation=creation, **defaults)

    def __repr__(self):
        return f'Paragraph({len(self.lines)} lines)'

    def _extra_attrs(self):
        return [self.x, self.y]

    def _shift_reals(self):
        return [(self.x, self.y)]

    def snap_points(self, time):
        return [(self.x.at_time(time), self.y.at_time(time))]

    def path(self, time):
        return ''

    def bbox(self, time=0):
        x, y = self.x.at_time(time), self.y.at_time(time)
        max_chars = max((len(line) for line in self.lines), default=0)
        w = max_chars * self.font_size * CHAR_WIDTH_FACTOR
        h = len(self.lines) * self.font_size * self.line_spacing
        if self.alignment == 'center':
            return (x - w / 2, y - self.font_size, w, h)
        elif self.alignment == 'right':
            return (x - w, y - self.font_size, w, h)
        return (x, y - self.font_size, w, h)

    def to_svg(self, time):
        x, y = self.x.at_time(time), self.y.at_time(time)
        anchor = {'left': 'start', 'center': 'middle', 'right': 'end'}[self.alignment]
        parts = []
        for i, line in enumerate(self.lines):
            ly = y + i * self.font_size * self.line_spacing
            parts.append(f"<text x='{x}' y='{ly}' text-anchor='{anchor}' "
                         f"font-size='{self.font_size}'{self.styling.svg_style(time)}>{_xml_escape(line)}</text>")
        return '\n'.join(parts)


class BulletedList(VObject):
    """List of items with bullet points.

    bullet: character to use as bullet marker.
    indent: pixel indentation for each item.
    """
    def __init__(self, *items, x=200, y=200, font_size=36, bullet='\u2022',
                 indent=40, line_spacing=1.6, creation=0, z=0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        self.items = list(items)
        self.x = attributes.Real(creation, x)
        self.y = attributes.Real(creation, y)
        self.font_size = font_size
        self.bullet = bullet
        self.indent = indent
        self.line_spacing = line_spacing
        defaults = dict(fill='#fff', stroke_width=0)
        self.styling = style.Styling(styling_kwargs, creation=creation, **defaults)

    def __repr__(self):
        return f'BulletedList({len(self.items)} items)'

    def _extra_attrs(self):
        return [self.x, self.y]

    def _shift_reals(self):
        return [(self.x, self.y)]

    def snap_points(self, time):
        return [(self.x.at_time(time), self.y.at_time(time))]

    def path(self, time):
        return ''

    def bbox(self, time=0):
        x, y = self.x.at_time(time), self.y.at_time(time)
        max_chars = max((len(item) for item in self.items), default=0)
        w = self.indent + max_chars * self.font_size * CHAR_WIDTH_FACTOR
        h = len(self.items) * self.font_size * self.line_spacing
        return (x, y - self.font_size, w, h)

    def to_svg(self, time):
        x, y = self.x.at_time(time), self.y.at_time(time)
        parts = []
        for i, item in enumerate(self.items):
            ly = y + i * self.font_size * self.line_spacing
            parts.append(f"<text x='{x}' y='{ly}' font-size='{self.font_size}'"
                         f"{self.styling.svg_style(time)}>{_xml_escape(self.bullet)}</text>")
            parts.append(f"<text x='{x + self.indent}' y='{ly}' font-size='{self.font_size}'"
                         f"{self.styling.svg_style(time)}>{_xml_escape(item)}</text>")
        return '\n'.join(parts)


class NumberedList(VObject):
    """List of items with numeric labels (1. 2. 3. ...).

    indent: pixel indentation for item text after the number.
    start_number: first number in the sequence.
    """
    def __init__(self, *items, x=200, y=200, font_size=36, indent=50,
                 line_spacing=1.6, start_number=1, creation=0, z=0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        self.items = list(items)
        self.x = attributes.Real(creation, x)
        self.y = attributes.Real(creation, y)
        self.font_size = font_size
        self.indent = indent
        self.line_spacing = line_spacing
        self.start_number = start_number
        defaults = dict(fill='#fff', stroke_width=0)
        self.styling = style.Styling(styling_kwargs, creation=creation, **defaults)

    def __repr__(self):
        return f'NumberedList({len(self.items)} items)'

    def _extra_attrs(self):
        return [self.x, self.y]

    def _shift_reals(self):
        return [(self.x, self.y)]

    def snap_points(self, time):
        return [(self.x.at_time(time), self.y.at_time(time))]

    def path(self, time):
        return ''

    def bbox(self, time=0):
        x, y = self.x.at_time(time), self.y.at_time(time)
        max_chars = max((len(item) for item in self.items), default=0)
        w = self.indent + max_chars * self.font_size * CHAR_WIDTH_FACTOR
        h = len(self.items) * self.font_size * self.line_spacing
        return (x, y - self.font_size, w, h)

    def to_svg(self, time):
        x, y = self.x.at_time(time), self.y.at_time(time)
        parts = []
        for i, item in enumerate(self.items):
            ly = y + i * self.font_size * self.line_spacing
            num = f'{self.start_number + i}.'
            parts.append(f"<text x='{x}' y='{ly}' font-size='{self.font_size}'"
                         f"{self.styling.svg_style(time)}>{num}</text>")
            parts.append(f"<text x='{x + self.indent}' y='{ly}' font-size='{self.font_size}'"
                         f"{self.styling.svg_style(time)}>{_xml_escape(item)}</text>")
        return '\n'.join(parts)


class FunctionGraph(Lines):
    """Plot a mathematical function as a polyline (no axes, ticks, or labels).

    x_range: (start, end) in math coordinates.
    y_range: (min, max) or None for auto.
    x, y, width, height: SVG pixel area for the plot.
    """
    def __init__(self, func, x_range=(-5, 5), y_range=None, num_points=200,
                 x=120, y=60, width=1440, height=840,
                 creation=0, z=0, **styling_kwargs):
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
        sx = self._px + (math_x - self._x_min) / (self._x_max - self._x_min) * self._pw
        sy = self._py + (1 - (yv - self._y_min) / (self._y_max - self._y_min)) * self._ph
        return (sx, sy)

    def get_slope_at(self, math_x, dx=1e-6):
        """Return the numerical derivative (in math coordinates) at math_x."""
        return (self._func(math_x + dx) - self._func(math_x - dx)) / (2 * dx)
