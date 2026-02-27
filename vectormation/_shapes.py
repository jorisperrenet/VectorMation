"""Shape classes: Polygon, Circle, Rectangle, Line, Text, Arc, etc."""
import math
from xml.sax.saxutils import escape as _xml_escape

import vectormation.easings as easings
import vectormation.attributes as attributes
import vectormation.style as style
from vectormation.pathbbox import path_bbox
from vectormation._constants import (
    SMALL_BUFF, DEFAULT_STROKE_WIDTH, DEFAULT_DOT_RADIUS, CHAR_WIDTH_FACTOR,
    DEFAULT_ARROW_TIP_LENGTH, DEFAULT_ARROW_TIP_WIDTH,
    _rotate_point, _sample_function, _distance, _normalize,
)
from vectormation._base import VObject, _ramp, _ramp_down, _set_attr


def _cached_bbox(target):
    """Return a function that caches target.bbox(t) per time value."""
    _cache = [None, None]
    def _bbox(t):
        if _cache[0] != t:
            _cache[0] = t
            _cache[1] = target.bbox(t)
        return _cache[1]
    return _bbox


class Polygon(VObject):
    def __init__(self, *vertices, closed=True, z: float = 0, creation: float = 0, **styling_kwargs):
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

    def move_vertex(self, index, x, y, start=0, end=None, easing=easings.smooth):
        """Animate a single vertex to a new position.

        Parameters
        ----------
        index:
            Vertex index (0-based). Negative indices are supported.
        x, y:
            Target position for the vertex.
        start:
            Time at which the change begins.
        end:
            Time at which the change ends.  ``None`` means instant.
        easing:
            Easing function for the animation.

        Returns
        -------
        self

        Raises
        ------
        IndexError
            If *index* is out of range.
        """
        n = len(self.vertices)
        if index < -n or index >= n:
            raise IndexError(f"vertex index {index} out of range for polygon with {n} vertices")
        _set_attr(self.vertices[index], start, end, (x, y), easing)
        return self

    def to_path_string(self, time=0):
        """Return an SVG path d-string representation of the polygon.

        For a closed polygon with vertices [(x1,y1), (x2,y2), ...],
        returns "M x1,y1 L x2,y2 L ... Z".  For open polylines the
        trailing Z is omitted.

        Unlike :meth:`path`, vertex coordinates are formatted as floats
        and an empty polygon returns ``''`` instead of raising.

        Parameters
        ----------
        time:
            Animation time at which to read vertex positions.

        Returns
        -------
        str
            SVG path d-string.
        """
        verts = self.get_vertices(time)
        if not verts:
            return ''
        parts = [f'M {verts[0][0]},{verts[0][1]}']
        for x, y in verts[1:]:
            parts.append(f'L {x},{y}')
        if self.closed:
            parts.append('Z')
        return ' '.join(parts)

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
        """Alias for :meth:`perimeter`."""
        return self.perimeter(time)

    def edge_lengths(self, time=0):
        """Return list of edge lengths."""
        pts = self.get_vertices(time)
        n = len(pts)
        if n < 2:
            return []
        pairs = list(zip(pts, pts[1:]))
        if self.closed and n > 2:
            pairs.append((pts[-1], pts[0]))
        return [math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in pairs]

    def to_path(self, time=0):
        """Convert the polygon to a :class:`Path` object.

        Returns a new Path whose ``d`` attribute is the SVG path string
        of this polygon at *time*.  Styling (stroke, fill, opacity, etc.)
        is copied from the polygon's current values at *time*.

        Parameters
        ----------
        time:
            Animation time at which to read vertex positions and styling.

        Returns
        -------
        Path
        """
        d = self.path(time)
        # Snapshot styling values at the given time.
        # Color attributes return rgb(...) strings from at_time(), but the
        # constructor expects hex or tuples.  Use the raw time_func to get
        # the (r, g, b) tuple for color attrs.
        style_kwargs = {}
        for name in ('fill_opacity', 'stroke_width',
                      'stroke_opacity', 'opacity', 'stroke_dasharray',
                      'stroke_dashoffset', 'stroke_linecap', 'stroke_linejoin',
                      'fill_rule'):
            style_kwargs[name] = getattr(self.styling, name).at_time(time)
        for name in ('fill', 'stroke'):
            attr = getattr(self.styling, name)
            style_kwargs[name] = attr.time_func(time)
        return Path(d, **style_kwargs)

    def get_longest_edge(self, time=0):
        """Return the length of the longest edge."""
        lengths = self.edge_lengths(time)
        return max(lengths) if lengths else 0

    def get_shortest_edge(self, time=0):
        """Return the length of the shortest edge."""
        lengths = self.edge_lengths(time)
        return min(lengths) if lengths else 0

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
        return sum(pts[i][0] * pts[(i+1) % n][1] - pts[(i+1) % n][0] * pts[i][1]
                   for i in range(n)) / 2

    def area(self, time=0):
        """Return the area using the shoelace formula (0 for open polylines)."""
        if not self.closed:
            return 0.0
        return abs(self.signed_area(time))

    def get_area(self, time=0):
        """Return the polygon's area (alias for area())."""
        return self.area(time)

    def winding_number(self, px, py, time=0):
        """Return the winding number of point (px, py) relative to this polygon.

        The winding number counts how many times the polygon winds around the
        point.  A return value of 0 means the point is outside.

        Parameters
        ----------
        px:
            X coordinate of the query point.
        py:
            Y coordinate of the query point.
        time:
            Animation time at which to read vertex positions.
        """
        pts = self.get_vertices(time)
        n = len(pts)
        if n < 3:
            return 0
        wn = 0
        for i in range(n):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % n]
            if y1 <= py:
                if y2 > py:
                    if ((x2 - x1) * (py - y1) - (px - x1) * (y2 - y1)) > 0:
                        wn += 1
            else:
                if y2 <= py:
                    if ((x2 - x1) * (py - y1) - (px - x1) * (y2 - y1)) < 0:
                        wn -= 1
        return wn

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
            len1 = math.hypot(dx1, dy1)
            # Edge from current to next
            dx2 = float(pts[next_idx][0] - pts[i][0])
            dy2 = float(pts[next_idx][1] - pts[i][1])
            len2 = math.hypot(dx2, dy2)
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
            avg_len = math.hypot(avg_nx, avg_ny)
            if avg_len > 0:
                avg_nx /= avg_len
                avg_ny /= avg_len
            new_x = float(pts[i][0]) + avg_nx * distance
            new_y = float(pts[i][1]) + avg_ny * distance
            new_pts.append((new_x, new_y))
        return Polygon(*new_pts, closed=self.closed)

    def buffer(self, distance, time=0):
        """Alias for :meth:`offset`."""
        return self.offset(distance, time=time)

    def inset(self, distance, time=0, **kwargs):
        """Return a new Polygon inset by *distance* pixels.

        Each edge of the polygon is moved inward along its inward normal by
        *distance* pixels.  The new vertices are computed as the intersections
        of the offset edges.  This works correctly for convex polygons; for
        concave polygons the result is a best-effort approximation.

        Parameters
        ----------
        distance:
            Number of pixels to inset.  Must be positive.
        time:
            Animation time at which to read current vertex positions.
        **kwargs:
            Extra styling keyword arguments forwarded to the new Polygon.

        Returns
        -------
        Polygon
            A new Polygon with inset vertices.

        Raises
        ------
        ValueError
            If *distance* would cause the polygon to collapse (i.e. any pair
            of adjacent offset edges fails to intersect properly).
        """
        pts = self.get_vertices(time)
        n = len(pts)
        if n < 3:
            raise ValueError("Cannot inset a polygon with fewer than 3 vertices")

        # Determine winding direction to figure out which side is "inward".
        # signed_area > 0 means CW in SVG (y-down), < 0 means CCW.
        sa = self.signed_area(time)
        # For CW (sa > 0): outward normal is (dy, -dx), inward = (-dy, dx).
        # For CCW (sa < 0): outward normal is (-dy, dx), inward = (dy, -dx).
        # sign = -1 for CW, +1 for CCW flips outward->inward.
        sign = -1.0 if sa >= 0 else 1.0

        # Compute offset edges: each edge moved inward by distance.
        offset_edges = []
        for i in range(n):
            j = (i + 1) % n
            dx = pts[j][0] - pts[i][0]
            dy = pts[j][1] - pts[i][1]
            edge_len = math.hypot(dx, dy)
            if edge_len < 1e-12:
                raise ValueError("Degenerate edge with zero length")
            # Inward normal direction depends on winding
            nx = sign * dy / edge_len
            ny = sign * (-dx) / edge_len
            # Offset edge points
            ox = nx * distance
            oy = ny * distance
            p1 = (pts[i][0] + ox, pts[i][1] + oy)
            p2 = (pts[j][0] + ox, pts[j][1] + oy)
            offset_edges.append((p1, p2))

        # Find intersections of consecutive offset edges
        new_pts = []
        for i in range(n):
            j = (i + 1) % n
            p1, p2 = offset_edges[i]
            p3, p4 = offset_edges[j]
            # Line-line intersection
            x1, y1 = p1
            x2, y2 = p2
            x3, y3 = p3
            x4, y4 = p4
            denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            if abs(denom) < 1e-12:
                raise ValueError(
                    f"Inset distance {distance} causes polygon to collapse "
                    f"(parallel edges at vertex {j})"
                )
            t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
            ix = x1 + t * (x2 - x1)
            iy = y1 + t * (y2 - y1)
            new_pts.append((ix, iy))

        result = Polygon(*new_pts, closed=self.closed, **kwargs)
        # Validate: check that the inset polygon has the same winding direction
        if sa != 0 and (sa * result.signed_area()) < 0:
            raise ValueError(
                f"Inset distance {distance} causes polygon to collapse "
                f"(area sign flipped)"
            )
        return result

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

    def get_convex_hull(self, time=0, **kwargs):
        """Return a new Polygon that is the convex hull of this polygon's vertices.

        Unlike the classmethod :meth:`convex_hull` which takes explicit points,
        this instance method computes the hull from the polygon's own vertices
        at the given *time*.

        Uses the gift-wrapping (Jarvis march) algorithm.  Collinear intermediate
        points are skipped so only the extreme hull vertices are kept.

        Parameters
        ----------
        time:
            Animation time at which to read vertex positions.
        **kwargs:
            Extra keyword arguments forwarded to the Polygon constructor
            (e.g. ``fill``, ``stroke``).

        Returns
        -------
        Polygon
            A new convex Polygon whose vertices are a subset of this
            polygon's vertices.

        Raises
        ------
        ValueError
            If the polygon has fewer than 3 vertices or all vertices
            are collinear.
        """
        pts = self.get_vertices(time)
        return Polygon.convex_hull(*pts, **kwargs)

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

    def get_edge_midpoints(self, time=0):
        """Return a list of midpoint (x, y) tuples for each edge.

        For a closed polygon this includes the midpoint of the closing edge
        from the last vertex back to the first.  For an open polyline only
        the interior segments are included.

        Parameters
        ----------
        time:
            Animation time at which to evaluate vertex positions.

        Returns
        -------
        list[tuple[float, float]]
            One midpoint per edge.
        """
        pts = self.get_vertices(time)
        n = len(pts)
        if n < 2:
            return []
        midpoints = []
        for i in range(n - 1):
            mx = (pts[i][0] + pts[i + 1][0]) / 2
            my = (pts[i][1] + pts[i + 1][1]) / 2
            midpoints.append((mx, my))
        if self.closed and n > 2:
            mx = (pts[-1][0] + pts[0][0]) / 2
            my = (pts[-1][1] + pts[0][1]) / 2
            midpoints.append((mx, my))
        return midpoints

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

    def _mirror(self, axis, center=None, time=0):
        """Mirror vertices across an axis line.

        *axis* is 0 for x (vertical mirror line) or 1 for y (horizontal).
        """
        pts = self.get_vertices(time)
        if center is None:
            center = sum(p[axis] for p in pts) / len(pts) if pts else 0
        for v in self.vertices:
            pt = list(v.at_time(time))
            pt[axis] = 2 * center - pt[axis]
            v.set_onward(time, tuple(pt))
        self._bbox_version += 1
        return self

    def mirror_x(self, cx=None, time=0):
        """Mirror vertices across vertical line x=cx."""
        return self._mirror(0, cx, time)

    def mirror_y(self, cy=None, time=0):
        """Mirror vertices across horizontal line y=cy."""
        return self._mirror(1, cy, time)

    def interior_angles(self, time=0):
        """Return the interior angles of the polygon in degrees.

        For a closed polygon with *n* vertices, returns a list of *n* angles
        (one per vertex) measured on the interior side.  For convex polygons
        all angles are less than 180; for concave polygons some may exceed 180.

        For an open polyline or a polygon with fewer than 3 vertices, returns
        an empty list.

        Parameters
        ----------
        time:
            Animation time at which to read vertex positions.

        Returns
        -------
        list[float]
            Interior angles in degrees, one per vertex.
        """
        if not self.closed:
            return []
        pts = self.get_vertices(time)
        n = len(pts)
        if n < 3:
            return []
        angles = []
        crosses = []
        for i in range(n):
            ax, ay = pts[(i - 1) % n]
            bx, by = pts[i]
            cx, cy = pts[(i + 1) % n]
            v1x, v1y = ax - bx, ay - by
            v2x, v2y = cx - bx, cy - by
            dot = v1x * v2x + v1y * v2y
            cross = v1x * v2y - v1y * v2x
            angles.append(math.degrees(math.atan2(abs(cross), dot)))
            crosses.append(cross)
        # Use winding direction to identify reflex angles (> 180 degrees).
        sa = self.signed_area(time)
        for i in range(n):
            if (sa > 0 and crosses[i] > 0) or (sa < 0 and crosses[i] < 0):
                angles[i] = 360 - angles[i]
        return angles

    def is_clockwise(self, time=0):
        """Return True if vertices are in clockwise order (positive signed area in SVG coords)."""
        return self.signed_area(time) > 0

    def bounding_circle(self, time=0, **kwargs):
        """Return the smallest enclosing circle of the polygon's vertices.

        Uses Welzl's algorithm (randomised, expected linear time) to compute
        the minimum bounding circle.  The returned :class:`Circle` is a static
        snapshot at the given *time*.

        Parameters
        ----------
        time:
            Animation time at which to read vertex positions.
        **kwargs:
            Extra keyword arguments forwarded to :class:`Circle` (e.g.
            ``stroke``, ``fill``).

        Returns
        -------
        Circle
            The smallest circle that contains all vertices of this polygon.

        Raises
        ------
        ValueError
            If the polygon has no vertices.
        """
        pts = self.get_vertices(time)
        if not pts:
            raise ValueError("bounding_circle requires at least one vertex")

        import random as _random
        rng = _random.Random(0)  # deterministic seed for reproducibility

        def _circle_from_1(p):
            return (p[0], p[1], 0.0)

        def _circle_from_2(p1, p2):
            cx = (p1[0] + p2[0]) / 2
            cy = (p1[1] + p2[1]) / 2
            r = math.hypot(p2[0] - p1[0], p2[1] - p1[1]) / 2
            return (cx, cy, r)

        def _circle_from_3(p1, p2, p3):
            ax, ay = p1
            bx, by = p2
            cx, cy = p3
            d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
            if abs(d) < 1e-14:
                # Collinear: return circle from the two farthest points
                pairs = [(p1, p2), (p1, p3), (p2, p3)]
                best = max(pairs, key=lambda ab: math.hypot(ab[1][0] - ab[0][0], ab[1][1] - ab[0][1]))
                return _circle_from_2(*best)
            a2 = ax * ax + ay * ay
            b2 = bx * bx + by * by
            c2 = cx * cx + cy * cy
            ux = (a2 * (by - cy) + b2 * (cy - ay) + c2 * (ay - by)) / d
            uy = (a2 * (cx - bx) + b2 * (ax - cx) + c2 * (bx - ax)) / d
            r = math.hypot(ax - ux, ay - uy)
            return (ux, uy, r)

        def _in_circle(circ, p):
            return math.hypot(p[0] - circ[0], p[1] - circ[1]) <= circ[2] + 1e-10

        def _welzl(points, boundary, n):
            if n == 0 or len(boundary) == 3:
                if len(boundary) == 0:
                    return (0, 0, 0)
                elif len(boundary) == 1:
                    return _circle_from_1(boundary[0])
                elif len(boundary) == 2:
                    return _circle_from_2(boundary[0], boundary[1])
                else:
                    return _circle_from_3(boundary[0], boundary[1], boundary[2])
            p = points[n - 1]
            circ = _welzl(points, boundary, n - 1)
            if _in_circle(circ, p):
                return circ
            return _welzl(points, boundary + [p], n - 1)

        shuffled = list(pts)
        rng.shuffle(shuffled)
        cx, cy, r = _welzl(shuffled, [], len(shuffled))
        return Circle(r=r, cx=cx, cy=cy, **kwargs)

    def triangulate(self, time=0, **kwargs):
        """Decompose this polygon into triangles using ear-clipping.

        Only works for simple (non-self-intersecting) polygons.  The polygon
        must be closed and have at least 3 vertices.

        Parameters
        ----------
        time:
            Animation time at which to read vertex positions.
        **kwargs:
            Extra styling keyword arguments forwarded to each triangle
            :class:`Polygon` (e.g. ``fill``, ``stroke``).

        Returns
        -------
        list[Polygon]
            A list of triangular Polygon objects whose union covers the
            original polygon.  For an *n*-vertex polygon this returns
            *n - 2* triangles.

        Raises
        ------
        ValueError
            If the polygon has fewer than 3 vertices or is not closed.
        """
        pts = self.get_vertices(time)
        n = len(pts)
        if n < 3:
            raise ValueError("triangulate requires at least 3 vertices")
        if not self.closed:
            raise ValueError("triangulate requires a closed polygon")

        # Ensure counter-clockwise winding (positive signed area).
        sa = 0
        for i in range(n):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % n]
            sa += (x1 - x0) * (y1 + y0)
        indices = list(range(n))
        if sa > 0:
            indices.reverse()

        def _cross(o, a, b):
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

        def _point_in_triangle(p, a, b, c):
            d1 = _cross(p, a, b)
            d2 = _cross(p, b, c)
            d3 = _cross(p, c, a)
            has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
            has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)
            return not (has_neg and has_pos)

        def _is_ear(idx_list, i):
            n_idx = len(idx_list)
            prev_i = idx_list[(i - 1) % n_idx]
            curr_i = idx_list[i]
            next_i = idx_list[(i + 1) % n_idx]
            a, b, c = pts[prev_i], pts[curr_i], pts[next_i]
            # Must be convex (positive cross product for CCW winding)
            if _cross(a, b, c) <= 0:
                return False
            # No other vertex inside this triangle
            for j in range(n_idx):
                if j in ((i - 1) % n_idx, i, (i + 1) % n_idx):
                    continue
                if _point_in_triangle(pts[idx_list[j]], a, b, c):
                    return False
            return True

        triangles = []
        remaining = list(indices)
        safety = 0
        max_iter = n * n
        while len(remaining) > 3 and safety < max_iter:
            safety += 1
            found = False
            for i in range(len(remaining)):
                if _is_ear(remaining, i):
                    prev_i = remaining[(i - 1) % len(remaining)]
                    curr_i = remaining[i]
                    next_i = remaining[(i + 1) % len(remaining)]
                    triangles.append(Polygon(
                        pts[prev_i], pts[curr_i], pts[next_i], **kwargs))
                    remaining.pop(i)
                    found = True
                    break
            if not found:
                break
        # Last remaining triangle
        if len(remaining) == 3:
            triangles.append(Polygon(
                pts[remaining[0]], pts[remaining[1]], pts[remaining[2]], **kwargs))
        return triangles

    def explode_edges(self, gap=10, **kwargs):
        """Return a VCollection of Line objects, one per edge, offset outward.

        Each edge is converted to a Line and pushed outward from the polygon
        centre by *gap* pixels along the edge's outward normal.  Useful for
        showing polygon decomposition.

        Parameters
        ----------
        gap:
            Pixel distance to offset each edge outward from the centroid.
        **kwargs:
            Extra keyword arguments forwarded to each :class:`Line`
            constructor (e.g. ``stroke``, ``stroke_width``).

        Returns
        -------
        VCollection
            A VCollection of Line objects.
        """
        from vectormation._base import VCollection
        pts = self.get_vertices(0)
        n = len(pts)
        if n < 2:
            return VCollection()
        cx, cy = self.get_center(0)
        edges = []
        pairs = list(zip(pts, pts[1:]))
        if self.closed and n > 2:
            pairs.append((pts[-1], pts[0]))
        for (ax, ay), (bx, by) in pairs:
            # Edge midpoint
            mx, my = (ax + bx) / 2, (ay + by) / 2
            # Direction from center to edge midpoint
            dx, dy = mx - cx, my - cy
            dist = math.hypot(dx, dy)
            if dist > 0:
                nx, ny = dx / dist * gap, dy / dist * gap
            else:
                nx, ny = 0, 0
            edges.append(Line(x1=ax + nx, y1=ay + ny,
                              x2=bx + nx, y2=by + ny, **kwargs))
        return VCollection(*edges)

    def subdivide_edges(self, iterations=1, time=0, **kwargs):
        """Split each edge at its midpoint, creating a polygon with 2x vertices per iteration.

        For a triangle with 3 edges, one iteration gives 6 vertices (original +
        midpoints).  Multiple iterations subdivide recursively.

        Parameters
        ----------
        iterations:
            Number of subdivision passes.  Each pass doubles the vertex count.
        time:
            Animation time at which to read vertex positions.
        **kwargs:
            Extra styling keyword arguments forwarded to the new Polygon.

        Returns
        -------
        Polygon
            A new Polygon with subdivided edges.
        """
        pts = self.get_vertices(time)
        for _ in range(iterations):
            new_pts = []
            n = len(pts)
            edges = list(zip(pts, pts[1:]))
            if self.closed and n > 1:
                edges.append((pts[-1], pts[0]))
            for (ax, ay), (bx, by) in edges:
                new_pts.append((ax, ay))
                new_pts.append(((ax + bx) / 2, (ay + by) / 2))
            if not self.closed and pts:
                new_pts.append(pts[-1])
            pts = new_pts
        return Polygon(*pts, closed=self.closed, **kwargs)

    def smooth_corners(self, radius=10, time=0, **kwargs):
        """Return a Path with Bezier-smoothed corners.

        For each corner vertex, replace the sharp angle with a quadratic
        Bezier curve that starts ``radius`` pixels before the vertex along
        the incoming edge and ends ``radius`` pixels after along the
        outgoing edge.

        Parameters
        ----------
        radius:
            How far (in pixels) from each corner the smoothing begins/ends.
        time:
            Animation time at which to read vertex positions.
        **kwargs:
            Extra styling keyword arguments forwarded to :class:`Path`.

        Returns
        -------
        Path
            A new Path with rounded corners.
        """
        pts = self.get_vertices(time)
        n = len(pts)
        if n < 3:
            # Not enough vertices to smooth — return a straight-line path.
            d = ' '.join(f'{"M" if i == 0 else "L"} {x},{y}' for i, (x, y) in enumerate(pts))
            if self.closed and n > 1:
                d += ' Z'
            return Path(d, **kwargs)

        parts = []
        for i in range(n):
            curr = pts[i]

            # For open polylines, first and last vertices are endpoints (no smoothing)
            if not self.closed and (i == 0 or i == n - 1):
                if i == 0:
                    parts.append(f'M {curr[0]},{curr[1]}')
                else:
                    parts.append(f'L {curr[0]},{curr[1]}')
                continue

            prev = pts[(i - 1) % n]
            nxt = pts[(i + 1) % n]

            # Vector from curr to prev / next
            dx_in = prev[0] - curr[0]
            dy_in = prev[1] - curr[1]
            len_in = math.hypot(dx_in, dy_in)
            dx_out = nxt[0] - curr[0]
            dy_out = nxt[1] - curr[1]
            len_out = math.hypot(dx_out, dy_out)

            # Clamp radius so it doesn't exceed half the edge length
            r = min(radius, len_in / 2 if len_in > 0 else radius,
                    len_out / 2 if len_out > 0 else radius)

            if len_in == 0 or len_out == 0:
                # Degenerate edge — just use the vertex
                parts.append(f'L {curr[0]},{curr[1]}')
                continue

            # Start point: r pixels before the vertex along incoming edge
            sx = curr[0] + (dx_in / len_in) * r
            sy = curr[1] + (dy_in / len_in) * r
            # End point: r pixels after the vertex along outgoing edge
            ex = curr[0] + (dx_out / len_out) * r
            ey = curr[1] + (dy_out / len_out) * r

            if i == 0:
                parts.append(f'M {sx},{sy}')
            else:
                parts.append(f'L {sx},{sy}')
            # Quadratic Bezier through the original vertex as control point
            parts.append(f'Q {curr[0]},{curr[1]} {ex},{ey}')

        if self.closed:
            parts.append('Z')
        d = ' '.join(parts)
        return Path(d, **kwargs)

    def apply_pointwise(self, func, time=0):
        """Apply an arbitrary function to all vertices.

        *func* is called as ``func(x, y)`` for each vertex and must return
        an ``(x', y')`` tuple.  The vertex position is read at *time* via
        ``at_time`` and the result is written back with ``set_onward``.

        Parameters
        ----------
        func:
            A callable ``(x, y) -> (x', y')``.
        time:
            Animation time at which to read current positions and write
            the transformed positions.

        Returns
        -------
        self
        """
        for v in self.vertices:
            x, y = v.at_time(time)
            nx, ny = func(float(x), float(y))
            v.set_onward(time, (nx, ny))
        return self

    def __repr__(self):
        return f'Polygon({len(self.vertices)} vertices)'


class Ellipse(VObject):
    def __init__(self, rx: float = 120, ry: float = 60, cx: float = 960, cy: float = 540, z: float = 0, creation: float = 0, **styling_kwargs):
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

    def get_foci(self, time=0):
        """Return the two foci as ((x1,y1), (x2,y2))."""
        cx, cy = self.c.at_time(time)
        rx, ry = self.rx.at_time(time), self.ry.at_time(time)
        a, b = max(rx, ry), min(rx, ry)
        c = math.sqrt(a * a - b * b)
        if rx >= ry:
            return ((cx - c, cy), (cx + c, cy))
        return ((cx, cy - c), (cx, cy + c))

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
        angle = math.tau * t
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
        _set_attr(self.c, start, end, (cx, cy), easing)
        return self

    def set_rx(self, value, start=0, end=None, easing=easings.smooth):
        """Animate the x-radius to value."""
        _set_attr(self.rx, start, end, value, easing)
        return self

    def set_ry(self, value, start=0, end=None, easing=easings.smooth):
        """Animate the y-radius to value."""
        _set_attr(self.ry, start, end, value, easing)
        return self

    def tangent_at_angle(self, angle_deg, length=200, time=0, **kwargs):
        """Return a tangent Line at the given angle, centred on the ellipse point."""
        px, py, tx, ty = self._tangent_at(angle_deg, time)
        dx, dy = tx * length / 2, ty * length / 2
        return Line(x1=px - dx, y1=py - dy, x2=px + dx, y2=py + dy, **kwargs)

    def _tangent_at(self, angle_deg, time=0):
        """Return (px, py, tx, ty): point on ellipse and unit tangent direction."""
        cx, cy = self.c.at_time(time)
        rx = self.rx.at_time(time)
        ry = self.ry.at_time(time)
        angle = math.radians(angle_deg)
        px = cx + rx * math.cos(angle)
        py = cy - ry * math.sin(angle)  # SVG y-down
        tx = -rx * math.sin(angle)
        ty = -ry * math.cos(angle)  # SVG y-down
        mag = math.hypot(tx, ty)
        if mag > 0:
            tx, ty = tx / mag, ty / mag
        return px, py, tx, ty

    def normal_at_angle(self, angle_deg, length=200, time=0, **kwargs):
        """Return a normal (perpendicular) Line at the given angle on the ellipse."""
        px, py, tx, ty = self._tangent_at(angle_deg, time)
        # Normal is perpendicular to tangent: rotate 90 degrees
        nx, ny = -ty * length / 2, tx * length / 2
        return Line(x1=px - nx, y1=py - ny, x2=px + nx, y2=py + ny, **kwargs)

    def get_tangent_line(self, angle_deg, length=100, time=0, **kwargs):
        """Alias for :meth:`tangent_at_angle` with default length=100."""
        return self.tangent_at_angle(angle_deg, length=length, time=time, **kwargs)

    def __repr__(self):
        cx, cy = self.c.at_time(0)
        return f'Ellipse(rx={self.rx.at_time(0):.0f}, ry={self.ry.at_time(0):.0f}, cx={cx:.0f}, cy={cy:.0f})'

    def to_svg(self, time):
        cx, cy = self.c.at_time(time)
        return f"<ellipse cx='{cx}' cy='{cy}' rx='{self.rx.at_time(time)}' ry='{self.ry.at_time(time)}'{self.styling.svg_style(time)} />"


class Circle(Ellipse):
    """Circle: Ellipse with rx == ry."""
    def __init__(self, r: float = 120, cx: float = 960, cy: float = 540, z: float = 0, creation: float = 0, **styling_kwargs):
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
        return math.tau * self.rx.at_time(time)

    def get_circumference(self, time=0):
        """Alias for get_perimeter. Returns the exact circumference (2 * pi * r)."""
        return self.get_perimeter(time)

    def circumference(self, time=0):
        """Return the circumference (2 * pi * r). Alias for get_perimeter."""
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

    @classmethod
    def from_center_and_point(cls, center, point, **kwargs):
        """Create a Circle from center and a point on the circumference."""
        r = math.hypot(point[0] - center[0], point[1] - center[1])
        return cls(r=r, cx=center[0], cy=center[1], **kwargs)

    @classmethod
    def from_bounding_box(cls, vobject, padding=0, time=0, **kwargs):
        """Create a Circle that circumscribes another object's bounding box.

        The circle is centered at the bbox center with radius equal to half
        the diagonal of the bounding box plus *padding*.

        Parameters
        ----------
        vobject:
            A VObject whose bounding box will be circumscribed.
        padding:
            Extra radius in pixels beyond the bbox half-diagonal.
        time:
            Time at which to read the bounding box.
        **kwargs:
            Extra keyword arguments forwarded to the Circle constructor.

        Returns
        -------
        Circle
        """
        bx, by, bw, bh = vobject.bbox(time)
        cx = bx + bw / 2
        cy = by + bh / 2
        r = math.hypot(bw / 2, bh / 2) + padding
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

    def tangent_points(self, px, py, time=0):
        """Return the tangent touch-points from an external point to the circle.

        Computes the points on the circle where tangent lines from the external
        point (px, py) would touch the circle.  This is the pure-geometry
        counterpart of :meth:`get_tangent_lines` — it returns coordinate tuples
        instead of Line objects.

        Parameters
        ----------
        px, py:
            Coordinates of the external point.
        time:
            Animation time at which to read the circle's position/radius.

        Returns
        -------
        list[tuple[float, float]]
            0, 1, or 2 touch-point (x, y) tuples:

            * Empty list if the point is strictly inside the circle.
            * One point if the point lies on the circle (within tolerance).
            * Two points if the point is outside the circle.
        """
        cx, cy = self.c.at_time(time)
        r = self.rx.at_time(time)
        d = _distance(cx, cy, px, py)
        if d < r - 1e-9:
            return []
        if abs(d) < 1e-12:
            return []
        if d <= r + 1e-9:
            # Point is on the circle — it is itself the single tangent point.
            ux, uy = (px - cx) / d, (py - cy) / d
            return [(cx + r * ux, cy + r * uy)]
        # Point is outside — two tangent points.
        half_angle = math.acos(max(-1.0, min(1.0, r / d)))
        base_angle = math.atan2(py - cy, px - cx)
        return [(cx + r * math.cos(base_angle + s * half_angle),
                 cy + r * math.sin(base_angle + s * half_angle))
                for s in (1, -1)]

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

    def sector_area(self, start_angle, end_angle, time=0):
        """Return the area of a circular sector between two angles (degrees)."""
        r = self.get_radius(time)
        sweep = abs(end_angle - start_angle)
        return 0.5 * r * r * math.radians(sweep)

    def set_radius(self, value, start=0, end=None, easing=easings.smooth):
        """Animate the radius to value."""
        _set_attr(self.rx, start, end, value, easing)
        _set_attr(self.ry, start, end, value, easing)
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
        r = math.hypot(ax - ux, ay - uy)
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

    def circumscribed_polygon(self, n, angle=0, time=0, **kwargs):
        """Return a regular *n*-gon circumscribed around this circle.

        The polygon's edges are tangent to the circle.  Each vertex lies at
        distance ``r / cos(pi / n)`` from the centre — the circumradius of a
        regular n-gon whose inradius equals this circle's radius.

        Parameters
        ----------
        n:
            Number of sides / vertices (>= 3).
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
        if n < 3:
            raise ValueError(f"circumscribed_polygon requires n >= 3, got {n}")
        cx, cy = self.c.at_time(time)
        r = self.rx.at_time(time)
        # The inradius of a regular n-gon with circumradius R is R*cos(pi/n).
        # We want the inradius to equal r, so R = r / cos(pi/n).
        circum_r = r / math.cos(math.pi / n)
        return RegularPolygon(n, radius=circum_r, cx=cx, cy=cy, angle=angle, **kwargs)

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

    def get_arc(self, start_angle=0, end_angle=180, time=0, **kwargs):
        """Create an Arc from this circle's center and radius.

        Convenience wrapper around :meth:`arc_between` with default angles
        of 0 and 180 degrees.

        Parameters
        ----------
        start_angle:
            Start angle in degrees (default 0).
        end_angle:
            End angle in degrees (default 180).
        time:
            Animation time at which to read the circle's position and radius.
        **kwargs:
            Extra styling keyword arguments forwarded to :class:`Arc`.

        Returns
        -------
        Arc
        """
        return self.arc_between(start_angle, end_angle, time=time, **kwargs)

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

    def segment_area(self, start_angle, end_angle, time=0):
        """Return the area of a circular segment between two angles.

        A circular segment is the region between a chord and the arc it
        subtends.  The segment area is computed as::

            segment_area = sector_area - triangle_area

        where the sector is the pie-slice from *start_angle* to *end_angle*
        and the triangle is formed by the two radii and the chord.

        Parameters
        ----------
        start_angle, end_angle:
            Angles in degrees defining the arc.
        time:
            Animation time at which to read the circle's radius.

        Returns
        -------
        float
            The area of the circular segment (always non-negative).

        Example
        -------
        >>> c = Circle(r=100)
        >>> c.segment_area(0, 180)   # semicircle area = pi*r^2/2
        """
        r = self.get_radius(time)
        sweep_deg = abs(end_angle - start_angle) % 360
        if sweep_deg == 0:
            return 0.0
        theta = math.radians(sweep_deg)
        # Sector area = 0.5 * r^2 * theta
        # Triangle area = 0.5 * r^2 * sin(theta)
        return abs(0.5 * r * r * (theta - math.sin(theta)))

    def power_of_point(self, px, py, time=0):
        """Return the power of point (px, py) with respect to this circle.

        The power of a point is defined as::

            power = d^2 - r^2

        where *d* is the distance from the point to the circle center and
        *r* is the radius.

        * Negative: the point is inside the circle.
        * Zero: the point is on the circle.
        * Positive: the point is outside the circle.

        This value is useful in computational geometry for determining
        point-circle relationships and for constructing radical axes.

        Parameters
        ----------
        px, py:
            Coordinates of the query point.
        time:
            Animation time at which to read the circle's position and radius.

        Returns
        -------
        float
        """
        cx, cy = self.c.at_time(time)
        r = self.get_radius(time)
        d_sq = (px - cx) ** 2 + (py - cy) ** 2
        return d_sq - r * r

    def chord_length(self, distance, time=0):
        """Return the length of a chord at the given distance from the center.

        A chord is a straight line segment whose endpoints lie on the circle.
        Given the perpendicular distance *d* from the center to the chord, the
        chord length is::

            chord = 2 * sqrt(r^2 - d^2)

        Parameters
        ----------
        distance:
            Perpendicular distance from the circle's center to the chord.
            Must be between 0 and the radius (inclusive).  A distance of 0
            gives the diameter (longest chord), while a distance equal to
            the radius gives 0 (the chord degenerates to a single point).
        time:
            Animation time at which to read the circle's radius.

        Returns
        -------
        float
            Length of the chord.

        Raises
        ------
        ValueError
            If *distance* is negative or greater than the radius.

        Examples
        --------
        >>> c = Circle(r=100)
        >>> c.chord_length(0)     # diameter = 200.0
        >>> c.chord_length(100)   # 0.0
        >>> c.chord_length(60)    # 2 * sqrt(100^2 - 60^2) = 160.0
        """
        r = self.get_radius(time)
        d = float(distance)
        if d < 0:
            raise ValueError(f"distance must be non-negative, got {d}")
        if d > r + 1e-9:
            raise ValueError(f"distance ({d}) exceeds radius ({r})")
        if d >= r:
            return 0.0
        return 2 * math.sqrt(r * r - d * d)

    def arc_length(self, start_angle, end_angle, time=0):
        """Return the arc length between two angles on the circle.

        The arc length is the distance along the circle's circumference
        from *start_angle* to *end_angle*.  The sweep is always taken as
        the absolute difference, so ``arc_length(0, 90)`` and
        ``arc_length(90, 0)`` return the same value.

        Parameters
        ----------
        start_angle:
            Start angle in degrees (CCW from the right).
        end_angle:
            End angle in degrees (CCW from the right).
        time:
            Animation time at which to read the circle's radius.

        Returns
        -------
        float
            The arc length in SVG pixels.

        Examples
        --------
        >>> c = Circle(r=100)
        >>> c.arc_length(0, 360)       # full circumference = 2*pi*100
        >>> c.arc_length(0, 90)        # quarter arc = pi*100/2
        >>> c.arc_length(0, 180)       # semicircle = pi*100
        """
        r = self.get_radius(time)
        sweep_deg = abs(end_angle - start_angle) % 360
        if abs(end_angle - start_angle) != 0 and sweep_deg == 0:
            sweep_deg = 360  # full circle
        return r * math.radians(sweep_deg)

    def get_sectors(self, n, **kwargs):
        """Divide the circle into *n* equal sectors (Wedge objects).

        Each sector spans ``360/n`` degrees.  The sectors share the circle's
        centre and radius at time 0.

        Parameters
        ----------
        n:
            Number of sectors (must be >= 1).
        **kwargs:
            Extra keyword arguments forwarded to each :class:`Wedge`
            constructor (e.g. ``fill``, ``stroke``).

        Returns
        -------
        VCollection
            A VCollection containing *n* Wedge objects.
        """
        from vectormation._base import VCollection
        if n < 1:
            n = 1
        cx, cy = self.c.at_time(0)
        r = self.rx.at_time(0)
        step = 360 / n
        sectors = []
        for i in range(n):
            sa = i * step
            ea = (i + 1) * step
            sectors.append(Wedge(cx=cx, cy=cy, r=r,
                                 start_angle=sa, end_angle=ea, **kwargs))
        return VCollection(*sectors)

    def annular_sector(self, inner_ratio=0.5, start_angle=0, end_angle=360, **kwargs):
        """Create an annular sector (donut slice) as a Path.

        Uses this circle's center and radius as the outer boundary.
        The inner boundary is at ``inner_ratio * radius``.

        Parameters
        ----------
        inner_ratio:
            Fraction of the outer radius for the inner boundary (0 < ratio < 1).
        start_angle:
            Start angle in degrees (0 = right, counter-clockwise in math coords).
        end_angle:
            End angle in degrees.
        **kwargs:
            Styling keyword arguments forwarded to the Path constructor.

        Returns
        -------
        Path
            A Path object with the annular sector shape.
        """
        cx, cy = self.c.at_time(0)
        ro = self.rx.at_time(0)
        ri = ro * inner_ratio
        sa_rad = math.radians(start_angle)
        ea_rad = math.radians(end_angle)
        # Outer arc start/end points
        ox1 = cx + ro * math.cos(sa_rad)
        oy1 = cy - ro * math.sin(sa_rad)
        ox2 = cx + ro * math.cos(ea_rad)
        oy2 = cy - ro * math.sin(ea_rad)
        # Inner arc start/end points (reversed direction)
        ix1 = cx + ri * math.cos(ea_rad)
        iy1 = cy - ri * math.sin(ea_rad)
        ix2 = cx + ri * math.cos(sa_rad)
        iy2 = cy - ri * math.sin(sa_rad)
        # Determine large-arc flag
        angle_span = abs(end_angle - start_angle) % 360
        if angle_span == 0 and abs(end_angle - start_angle) >= 360:
            angle_span = 360
        large = 1 if angle_span > 180 else 0
        # Sweep: for SVG with y-inverted, CCW math angles map to CW SVG sweep=0
        sweep_out = 0 if end_angle > start_angle else 1
        sweep_in = 1 - sweep_out
        if angle_span >= 360:
            # Full annulus: two half-arcs to avoid degenerate zero-length arc
            mid_rad = sa_rad + math.pi
            omx = cx + ro * math.cos(mid_rad)
            omy = cy - ro * math.sin(mid_rad)
            imx = cx + ri * math.cos(mid_rad)
            imy = cy - ri * math.sin(mid_rad)
            d = (f'M{ox1},{oy1}'
                 f'A{ro},{ro} 0 1,0 {omx},{omy}'
                 f'A{ro},{ro} 0 1,0 {ox1},{oy1}'
                 f'M{ix2},{iy2}'
                 f'A{ri},{ri} 0 1,1 {imx},{imy}'
                 f'A{ri},{ri} 0 1,1 {ix2},{iy2}Z')
        else:
            d = (f'M{ox1},{oy1}'
                 f'A{ro},{ro} 0 {large},{sweep_out} {ox2},{oy2}'
                 f'L{ix1},{iy1}'
                 f'A{ri},{ri} 0 {large},{sweep_in} {ix2},{iy2}Z')
        style_kw = {'fill': '#fff', 'fill_opacity': 0.7, 'stroke': '#fff',
                     'stroke_width': DEFAULT_STROKE_WIDTH} | kwargs
        return Path(d, **style_kw)

    def inscribed_polygon(self, n, start_angle=0, angle=None, time=0, **kwargs):
        """Return a regular *n*-sided polygon inscribed in this circle.

        Vertices are placed at equal angular intervals starting from
        *start_angle* (degrees, counter-clockwise from the positive
        x-axis in math convention; y is inverted for SVG).

        Parameters
        ----------
        n:
            Number of sides (must be >= 3).
        start_angle:
            Starting angle in degrees (CCW from right).
        angle:
            Alias for *start_angle*.  If both are given, *angle* takes
            precedence.
        time:
            Animation time at which to read the circle's center and radius.
        **kwargs:
            Extra styling keyword arguments forwarded to :class:`RegularPolygon`.

        Returns
        -------
        RegularPolygon
            A new RegularPolygon inscribed in the circle.
        """
        if angle is not None:
            start_angle = angle
        cx, cy = self.c.at_time(time)
        r = self.rx.at_time(time)
        return RegularPolygon(n, radius=r, cx=cx, cy=cy, angle=start_angle, **kwargs)

    def get_annulus(self, inner_ratio=0.5, time=0, **kwargs):
        """Create an Annulus (ring) using this circle's center and radius.

        The outer radius of the annulus equals this circle's radius; the inner
        radius is ``inner_ratio * radius``.

        Parameters
        ----------
        inner_ratio:
            Fraction of the outer radius used as the inner radius.
            Must be in (0, 1).  Default 0.5.
        time:
            Animation time at which to read the circle's center and radius.
        **kwargs:
            Extra keyword arguments forwarded to the :class:`Annulus`
            constructor (e.g. ``fill``, ``stroke``).

        Returns
        -------
        Annulus
            A new Annulus centered on this circle.
        """
        cx, cy = self.c.at_time(time)
        r = self.rx.at_time(time)
        return Annulus(inner_radius=r * inner_ratio, outer_radius=r,
                       cx=cx, cy=cy, **kwargs)

    def tangent_line_from_point(self, px, py, time=0, length=200, **kwargs):
        """Return tangent line(s) from an external point to this circle.

        Uses the standard geometric construction: compute the distance from
        the point to the circle center, then find the tangent touch points.

        Parameters
        ----------
        px, py:
            Coordinates of the external point.
        time:
            Animation time at which to read the circle's position/radius.
        length:
            Total length of each returned tangent Line segment.
        **kwargs:
            Extra styling keyword arguments forwarded to :class:`Line`.

        Returns
        -------
        list of Line
            0 lines if the point is inside the circle, 1 if on the
            boundary, or 2 if outside.
        """
        cx, cy = self.c.at_time(time)
        r = self.rx.at_time(time)
        d = _distance(cx, cy, px, py)
        if d < r - 1e-9:
            return []
        if abs(d) < 1e-12:
            return []
        ux, uy = (px - cx) / d, (py - cy) / d
        if d <= r + 1e-9:
            tx, ty = -uy, ux
            half = length / 2
            return [Line(x1=px - tx * half, y1=py - ty * half,
                         x2=px + tx * half, y2=py + ty * half, **kwargs)]
        half_angle = math.acos(max(-1.0, min(1.0, r / d)))
        base_angle = math.atan2(py - cy, px - cx)
        lines = []
        for sign in (1, -1):
            touch_angle = base_angle + sign * half_angle
            tx_touch = cx + r * math.cos(touch_angle)
            ty_touch = cy + r * math.sin(touch_angle)
            td_x = -math.sin(touch_angle)
            td_y = math.cos(touch_angle)
            half = length / 2
            lines.append(Line(x1=tx_touch - td_x * half, y1=ty_touch - td_y * half,
                               x2=tx_touch + td_x * half, y2=ty_touch + td_y * half,
                               **kwargs))
        return lines

    def to_svg(self, time):
        cx, cy = self.c.at_time(time)
        return f"<circle cx='{cx}' cy='{cy}' r='{self.rx.at_time(time)}'{self.styling.svg_style(time)} />"


class Dot(Circle):
    """Small filled circle, no stroke."""
    def __init__(self, r: float = DEFAULT_DOT_RADIUS, cx: float = 960, cy: float = 540, z: float = 0, creation: float = 0, **styling_kwargs):
        super().__init__(r=r, cx=cx, cy=cy, z=z, creation=creation,
                         **({'fill': '#fff', 'fill_opacity': 1, 'stroke_width': 0} | styling_kwargs))

    def __repr__(self):
        cx, cy = self.c.at_time(0)
        return f'Dot(cx={cx:.0f}, cy={cy:.0f})'


class Rectangle(VObject):
    def __init__(self, width, height, x=960, y=540, rx=0, ry=0, creation: float = 0, z: float = 0, **styling_kwargs):
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
        """Return ``[tl, tr, br, bl]`` as (x, y) tuples. Alias for get_vertices."""
        return self.get_vertices(time)

    def get_area(self, time=0):
        """Return the area (width * height)."""
        return self.width.at_time(time) * self.height.at_time(time)

    def get_perimeter(self, time=0):
        """Return the perimeter (2 * (width + height))."""
        return 2 * (self.width.at_time(time) + self.height.at_time(time))

    def get_diagonal_length(self, time=0):
        """Return the diagonal length: ``sqrt(width^2 + height^2)``."""
        w = self.width.at_time(time)
        h = self.height.at_time(time)
        return math.hypot(w, h)

    def diagonal_length(self, time=0):
        """Return the length of the diagonal (alias for get_diagonal_length)."""
        return self.get_diagonal_length(time)

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

    def sample_border(self, t, time=0):
        """Return a point (x, y) on the rectangle border at parameter *t*.

        The parameter *t* is in ``[0, 1)`` and maps to a position along the
        perimeter, starting from the top-left corner and proceeding clockwise:

        * ``t = 0``   : top-left corner
        * ``t = 0.25``: approximately the top-right corner (exact when square)
        * ``t = 0.5`` : approximately the bottom-right corner
        * ``t = 0.75``: approximately the bottom-left corner

        More precisely, the perimeter is parameterised proportionally to
        arc length: the top edge occupies ``width / perimeter`` of the
        parameter range, and so on.

        Parameters
        ----------
        t:
            Parameter in ``[0, 1)``.  Values outside this range are
            wrapped via modulo.
        time:
            Animation time at which to read the rectangle geometry.

        Returns
        -------
        tuple[float, float]
            ``(x, y)`` on the border.
        """
        rx = float(self.x.at_time(time))
        ry = float(self.y.at_time(time))
        w = float(self.width.at_time(time))
        h = float(self.height.at_time(time))
        perim = 2 * (w + h)
        if perim < 1e-12:
            return (rx, ry)
        t = t % 1.0
        dist = t * perim
        # Top edge: left to right
        if dist <= w:
            return (rx + dist, ry)
        dist -= w
        # Right edge: top to bottom
        if dist <= h:
            return (rx + w, ry + dist)
        dist -= h
        # Bottom edge: right to left
        if dist <= w:
            return (rx + w - dist, ry + h)
        dist -= w
        # Left edge: bottom to top
        return (rx, ry + h - dist)

    def get_grid_lines(self, rows, cols, time=0, **kwargs):
        """Return a VCollection of Lines forming a grid inside this rectangle.

        *rows* horizontal lines and *cols* vertical lines divide the
        interior into ``(rows + 1)`` horizontal bands and ``(cols + 1)``
        vertical bands.

        Parameters
        ----------
        rows:
            Number of horizontal dividing lines.
        cols:
            Number of vertical dividing lines.
        time:
            Animation time at which to read the rectangle geometry.
        **kwargs:
            Extra keyword arguments forwarded to each :class:`Line`
            constructor (e.g. ``stroke``, ``stroke_width``).

        Returns
        -------
        VCollection
            A VCollection of Line objects.
        """
        from vectormation._base import VCollection
        rx = float(self.x.at_time(time))
        ry = float(self.y.at_time(time))
        w = float(self.width.at_time(time))
        h = float(self.height.at_time(time))
        lines = []
        # Horizontal lines
        for i in range(1, rows + 1):
            y_pos = ry + h * i / (rows + 1)
            lines.append(Line(x1=rx, y1=y_pos, x2=rx + w, y2=y_pos, **kwargs))
        # Vertical lines
        for j in range(1, cols + 1):
            x_pos = rx + w * j / (cols + 1)
            lines.append(Line(x1=x_pos, y1=ry, x2=x_pos, y2=ry + h, **kwargs))
        return VCollection(*lines)

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

    @classmethod
    def from_bounding_box(cls, vobject, padding=0, time=0, **kwargs):
        """Create a Rectangle that encloses another object's bounding box.

        Parameters
        ----------
        vobject:
            Any object with a ``bbox(time)`` method that returns
            ``(x, y, width, height)``.
        padding:
            Extra space in pixels added to each side of the bounding box
            (default ``0``).
        time:
            Animation time at which to read the target's bounding box.
        **kwargs:
            Extra keyword arguments forwarded to the Rectangle constructor
            (e.g. ``stroke``, ``fill``).

        Returns
        -------
        Rectangle
        """
        bx, by, bw, bh = vobject.bbox(time)
        return cls(
            bw + 2 * padding,
            bh + 2 * padding,
            x=bx - padding,
            y=by - padding,
            **kwargs,
        )

    @classmethod
    def from_two_objects(cls, obj_a, obj_b, padding=0, **kwargs):
        """Create a Rectangle that encloses two objects' bounding boxes.

        Computes the union of ``obj_a.bbox(0)`` and ``obj_b.bbox(0)``,
        adds *padding* on every side, and returns a new Rectangle.

        Parameters
        ----------
        obj_a, obj_b:
            Any objects with a ``bbox(time)`` method returning
            ``(x, y, width, height)``.
        padding:
            Extra space in pixels added to each side (default ``0``).
        **kwargs:
            Extra keyword arguments forwarded to the Rectangle constructor.

        Returns
        -------
        Rectangle
        """
        ax, ay, aw, ah = obj_a.bbox(0)
        bx, by, bw, bh = obj_b.bbox(0)
        x1 = min(ax, bx)
        y1 = min(ay, by)
        x2 = max(ax + aw, bx + bw)
        y2 = max(ay + ah, by + bh)
        return cls(
            x2 - x1 + 2 * padding,
            y2 - y1 + 2 * padding,
            x=x1 - padding,
            y=y1 - padding,
            **kwargs,
        )

    def set_size(self, width, height, start=0, end=None, easing=easings.smooth):
        """Set both dimensions."""
        _set_attr(self.width, start, end, width, easing)
        _set_attr(self.height, start, end, height, easing)
        return self

    def grow_width(self, amount, start=0, end=1, easing=easings.smooth):
        """Animate increasing width by amount."""
        self.width.move_to(start, end, self.width.at_time(start) + amount, easing=easing)
        return self

    def grow_height(self, amount, start=0, end=1, easing=easings.smooth):
        """Animate increasing height by amount."""
        self.height.move_to(start, end, self.height.at_time(start) + amount, easing=easing)
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

    def split_horizontal(self, n=2, time=0, **kwargs):
        """Split into *n* equal horizontal strips. Alias for ``split('horizontal', ...)``."""
        return self.split('horizontal', n, time, **kwargs)

    def split_vertical(self, n=2, time=0, **kwargs):
        """Split into *n* equal vertical strips. Alias for ``split('vertical', ...)``."""
        return self.split('vertical', n, time, **kwargs)

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
        """Animate expanding by *amount* pixels on each side (center stays in place)."""
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
        """Convert to a Polygon snapshot with 4 vertices at *time*."""
        corners = self.get_corners(time)
        return Polygon(*corners, **kwargs)

    def to_lines(self, time=0, **kwargs):
        """Return ``[top, right, bottom, left]`` as 4 Line objects."""
        tl, tr, br, bl = self.get_corners(time)
        return [
            Line(x1=tl[0], y1=tl[1], x2=tr[0], y2=tr[1], **kwargs),  # top
            Line(x1=tr[0], y1=tr[1], x2=br[0], y2=br[1], **kwargs),  # right
            Line(x1=br[0], y1=br[1], x2=bl[0], y2=bl[1], **kwargs),  # bottom
            Line(x1=bl[0], y1=bl[1], x2=tl[0], y2=tl[1], **kwargs),  # left
        ]

    def diagonal_lines(self, time=0, **kwargs):
        """Return ``(tl-to-br, tr-to-bl)`` as two Line objects."""
        tl, tr, br, bl = self.get_corners(time)
        d1 = Line(x1=tl[0], y1=tl[1], x2=br[0], y2=br[1], **kwargs)
        d2 = Line(x1=tr[0], y1=tr[1], x2=bl[0], y2=bl[1], **kwargs)
        return (d1, d2)

    def subdivide(self, rows=2, cols=2, time=0, **kwargs):
        """Subdivide this rectangle into a grid of *rows* x *cols* sub-rectangles.

        Unlike :meth:`split` which only divides along one axis, this method
        creates a full 2-D grid tiling the original rectangle.

        Parameters
        ----------
        rows:
            Number of rows (vertical divisions).  Must be >= 1.
        cols:
            Number of columns (horizontal divisions).  Must be >= 1.
        time:
            Animation time at which to read the current rectangle geometry.
        **kwargs:
            Extra styling keyword arguments forwarded to each sub-Rectangle
            (e.g. ``fill``, ``stroke``).

        Returns
        -------
        VCollection
            A collection of ``rows * cols`` Rectangle objects arranged in
            row-major order (row 0 col 0, row 0 col 1, ..., row 1 col 0, ...).

        Raises
        ------
        ValueError
            If *rows* or *cols* is less than 1.
        """
        from vectormation._base import VCollection
        if rows < 1 or cols < 1:
            raise ValueError(f"subdivide: rows and cols must be >= 1, got rows={rows}, cols={cols}")
        rx = float(self.x.at_time(time))
        ry = float(self.y.at_time(time))
        rw = float(self.width.at_time(time))
        rh = float(self.height.at_time(time))
        cell_w = rw / cols
        cell_h = rh / rows
        parts = []
        for r in range(rows):
            for c in range(cols):
                parts.append(Rectangle(cell_w, cell_h,
                                       x=rx + c * cell_w,
                                       y=ry + r * cell_h, **kwargs))
        return VCollection(*parts)

    def chamfer(self, size=10, time=0, **kwargs):
        """Return a :class:`Path` where each corner is cut at 45 degrees.

        Creates an octagonal shape by cutting each corner of the rectangle
        by *size* pixels.

        Parameters
        ----------
        size:
            The distance along each edge from the corner where the cut
            starts (default 10 px).
        time:
            Animation time at which to read the rectangle geometry.
        **kwargs:
            Extra keyword arguments forwarded to the :class:`Path`
            constructor (e.g. ``stroke``, ``fill``).

        Returns
        -------
        Path
            A closed Path with 8 vertices (an octagon).
        """
        x = float(self.x.at_time(time))
        y = float(self.y.at_time(time))
        w = float(self.width.at_time(time))
        h = float(self.height.at_time(time))
        s = min(size, w / 2, h / 2)
        # 8 points clockwise from top-left chamfer:
        # top edge
        d = (f'M{x + s},{y} L{x + w - s},{y} '
             # top-right corner
             f'L{x + w},{y + s} '
             # right edge
             f'L{x + w},{y + h - s} '
             # bottom-right corner
             f'L{x + w - s},{y + h} '
             # bottom edge
             f'L{x + s},{y + h} '
             # bottom-left corner
             f'L{x},{y + h - s} '
             # left edge
             f'L{x},{y + s} Z')
        return Path(d, **kwargs)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.width.at_time(0):.0f}x{self.height.at_time(0):.0f})'


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

    def length(self, time=0):
        """Return the Euclidean length of the line (alias for get_length)."""
        return self.get_length(time)

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
        """Return the normalized unit vector ``(dx, dy)`` from p1 to p2."""
        x1, y1 = self.p1.at_time(time)
        x2, y2 = self.p2.at_time(time)
        return _normalize(x2 - x1, y2 - y1)

    def get_vector(self, time=0):
        """Return the unnormalized direction vector ``(dx, dy)`` from p1 to p2."""
        x1, y1 = self.get_start(time)
        x2, y2 = self.get_end(time)
        return (x2 - x1, y2 - y1)

    def get_normal(self, time=0):
        """Return the unit normal ``(-dy, dx)`` perpendicular to the line."""
        dx, dy = self.get_direction(time)
        return (-dy, dx)

    def angle_to(self, other, time=0):
        """Return the angle in degrees [0, 180] between this line and *other*."""
        d1 = self.get_direction(time)
        d2 = other.get_direction(time)
        dot = d1[0] * d2[0] + d1[1] * d2[1]
        dot = max(-1.0, min(1.0, dot))  # clamp for numerical safety
        return math.degrees(math.acos(dot))

    def angle_with(self, other, time=0):
        """Alias for :meth:`angle_to`."""
        return self.angle_to(other, time)

    def is_parallel(self, other, time=0, tol=1e-6):
        """Return True if cross product of directions is within *tol* of zero."""
        d1 = self.get_direction(time)
        d2 = other.get_direction(time)
        cross = d1[0] * d2[1] - d1[1] * d2[0]
        return abs(cross) < tol

    def is_perpendicular(self, other, time=0, tol=1e-6):
        """Return True if dot product of directions is within *tol* of zero."""
        d1 = self.get_direction(time)
        d2 = other.get_direction(time)
        dot_val = d1[0] * d2[0] + d1[1] * d2[1]
        return abs(dot_val) < tol

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

    def _is_aligned(self, axis, time, tol):
        """Return True if start and end differ by less than *tol* on *axis* (0=x, 1=y)."""
        return abs(self.get_end(time)[axis] - self.get_start(time)[axis]) < tol

    def is_horizontal(self, time=0, tol=1e-3):
        """Return True if this line is approximately horizontal."""
        return self._is_aligned(1, time, tol)

    def is_vertical(self, time=0, tol=1e-3):
        """Return True if this line is approximately vertical."""
        return self._is_aligned(0, time, tol)

    def set_start(self, point, start=0, end=None, easing=easings.smooth):
        _set_attr(self.p1, start, end, point, easing)
        return self

    def set_end(self, point, start=0, end=None, easing=easings.smooth):
        _set_attr(self.p2, start, end, point, easing)
        return self

    def set_points(self, p1, p2, start=0):
        """Set both endpoints at once."""
        self.p1.set_onward(start, p1)
        self.p2.set_onward(start, p2)
        return self

    def set_length(self, length, start=0, end=None, easing=easings.smooth):
        """Set absolute length while keeping the midpoint fixed.

        Parameters
        ----------
        length:
            Target length in SVG pixels.
        start:
            Time at which the change begins.
        end:
            Time at which the change ends.  ``None`` means instant.
        easing:
            Easing function for the animation.

        Returns
        -------
        self
        """
        x1, y1 = self.p1.at_time(start)
        x2, y2 = self.p2.at_time(start)
        cur = _distance(x1, y1, x2, y2)
        if cur < 1e-9:
            return self
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = _normalize(x2 - x1, y2 - y1)
        half = length / 2
        _set_attr(self.p1, start, end, (mx - dx * half, my - dy * half), easing)
        _set_attr(self.p2, start, end, (mx + dx * half, my + dy * half), easing)
        return self

    def extend_to(self, length, anchor='start', start=0, end=None, easing=easings.smooth):
        """Extend or shrink the line to *length*, keeping one endpoint fixed.

        Unlike :meth:`set_length` (which keeps the midpoint fixed), this method
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
        start:
            Time at which the change begins.
        end:
            Time at which the change ends.  ``None`` means instant.
        easing:
            Easing function for the animation.
        """
        x1, y1 = self.p1.at_time(start)
        x2, y2 = self.p2.at_time(start)
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
    def from_points(cls, p1, p2, **kwargs):
        """Create a Line from two (x, y) tuples. Alias for :meth:`between`."""
        return cls.between(p1, p2, **kwargs)

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
        mag = math.hypot(dx, dy)
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

    @classmethod
    def from_slope_point(cls, slope, point, length=200, **kwargs):
        """Create a Line passing through *point* with the given *slope*.

        The line is centered at *point* and extends *length/2* pixels in
        each direction along the slope.

        Parameters
        ----------
        slope:
            The slope (dy/dx) of the line.  Use ``float('inf')`` or
            ``float('-inf')`` for vertical lines.
        point:
            ``(px, py)`` — a point the line passes through.
        length:
            Total length of the resulting line in pixels.
        **kwargs:
            Forwarded to the :class:`Line` constructor.

        Returns
        -------
        Line

        Examples
        --------
        >>> Line.from_slope_point(1, (960, 540))       # 45-degree line
        >>> Line.from_slope_point(0, (960, 540))        # horizontal line
        >>> Line.from_slope_point(float('inf'), (960, 540))  # vertical line
        """
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
    def from_objects(cls, obj_a, obj_b, buff=0, **kwargs):
        """Create a Line connecting the nearest edges of two objects.

        The direction from *obj_a*'s center to *obj_b*'s center determines
        which edges to use: if the horizontal distance is greater than the
        vertical distance, the right edge of the closer object and the left
        edge of the farther object are used (or vice-versa); otherwise the
        bottom/top edges are used.

        Parameters
        ----------
        obj_a, obj_b:
            Any objects with ``bbox(time)`` and ``get_edge(name, time)``
            methods.
        buff:
            Distance in pixels to shorten each endpoint inward along the
            line direction (default ``0``).
        **kwargs:
            Extra keyword arguments forwarded to the Line constructor.

        Returns
        -------
        Line
        """
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

    def lerp(self, t, time=0):
        """Return point (x, y) at parameter t (0=start, 1=end) along the line."""
        x1, y1 = self.get_start(time)
        x2, y2 = self.get_end(time)
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))

    def subdivide_into(self, n=2, time=0, **kwargs):
        """Divide this line into *n* equal segments.

        Returns a list of *n* :class:`Line` objects, each spanning one
        segment of the original line.  The first segment starts at p1 and
        the last ends at p2.

        Parameters
        ----------
        n:
            Number of equal segments (must be >= 1).  Default is 2.
        time:
            Animation time at which to read the line endpoints.
        **kwargs:
            Extra keyword arguments forwarded to each :class:`Line`
            constructor (e.g. ``stroke``, ``stroke_width``).

        Returns
        -------
        list[Line]
            A list of *n* Line objects.
        """
        if n < 1:
            n = 1
        x1, y1 = self.get_start(time)
        x2, y2 = self.get_end(time)
        dx = (x2 - x1) / n
        dy = (y2 - y1) / n
        segments = []
        for i in range(n):
            sx = x1 + i * dx
            sy = y1 + i * dy
            ex = x1 + (i + 1) * dx
            ey = y1 + (i + 1) * dy
            segments.append(Line(x1=sx, y1=sy, x2=ex, y2=ey, **kwargs))
        return segments

    def divide(self, n=2, time=0):
        """Return *n* + 1 points that divide the line into *n* equal segments.

        Unlike :meth:`subdivide_into` which returns new :class:`Line` objects,
        this method returns the division points themselves as a list of
        ``(x, y)`` tuples.  The first point is always p1 and the last is
        always p2.

        Parameters
        ----------
        n:
            Number of equal segments (must be >= 1).  Default is 2.
        time:
            Animation time at which to read the line endpoints.

        Returns
        -------
        list[tuple[float, float]]
            A list of *n* + 1 ``(x, y)`` points.

        Example
        -------
        >>> line = Line(0, 0, 200, 0)
        >>> line.divide(4)
        [(0.0, 0.0), (50.0, 0.0), (100.0, 0.0), (150.0, 0.0), (200.0, 0.0)]
        """
        if n < 1:
            n = 1
        x1, y1 = self.get_start(time)
        x2, y2 = self.get_end(time)
        return [(x1 + i * (x2 - x1) / n, y1 + i * (y2 - y1) / n)
                for i in range(n + 1)]

    def distance_to_point(self, px, py, time=0):
        """Return the shortest distance from point ``(px, py)`` to this line segment.

        The distance is measured to the closest point on the segment (clamped),
        not to the infinite line extension.

        Parameters
        ----------
        px, py:
            Coordinates of the external point.
        time:
            Animation time at which to evaluate the line endpoints.

        Returns
        -------
        float
            Euclidean distance from the point to the nearest point on the segment.
        """
        cp = self.get_perpendicular_point(px, py, time)
        return math.hypot(px - cp[0], py - cp[1])

    def contains_point(self, px, py, time=0, tol=2):
        """Return True if ``(px, py)`` is within *tol* pixels of this segment."""
        return self.distance_to_point(px, py, time) <= tol

    def add_tip(self, end=True, start=False, tip_length=None, tip_width=None, creation=0):
        """Create arrowhead tip polygon(s) at line endpoints.

        Parameters
        ----------
        end:
            If True, add a tip at the end (p2) of the line.
        start:
            If True, add a tip at the start (p1) of the line.
        tip_length:
            Length of the tip along the line direction.  Defaults to
            ``DEFAULT_ARROW_TIP_LENGTH``.
        tip_width:
            Width of the tip perpendicular to the line.  Defaults to
            ``DEFAULT_ARROW_TIP_WIDTH``.
        creation:
            Creation time for the tip polygons.

        Returns
        -------
        VCollection
            A VCollection containing the line and tip polygon(s).
        """
        from vectormation._base import VCollection
        tl = tip_length if tip_length is not None else DEFAULT_ARROW_TIP_LENGTH
        tw = tip_width if tip_width is not None else DEFAULT_ARROW_TIP_WIDTH
        hw = tw / 2
        x1, y1 = self.p1.at_time(creation)
        x2, y2 = self.p2.at_time(creation)
        stroke_color = self.styling.stroke.time_func(creation)
        objects = [self]

        # Build tip at each requested endpoint: (tip_point, direction toward tip)
        tips = []
        if end:
            tips.append(((x2, y2), (x2 - x1, y2 - y1)))
        if start:
            tips.append(((x1, y1), (x1 - x2, y1 - y2)))
        for (tx, ty), (dx, dy) in tips:
            length = math.hypot(dx, dy) or 1
            ux, uy = dx / length, dy / length
            px, py = -uy, ux
            bx, by = tx - ux * tl, ty - uy * tl
            objects.append(Polygon(
                (tx, ty), (bx + px * hw, by + py * hw), (bx - px * hw, by - py * hw),
                creation=creation, z=self.z,
                fill=stroke_color, fill_opacity=1, stroke_width=0,
            ))

        return VCollection(*objects, creation=creation, z=self.z)

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

    def perpendicular_at(self, t=0.5, length=None, time=0, **kwargs):
        """Return a Line perpendicular to this line at parameter t (0=start, 1=end).

        Parameters
        ----------
        t:
            Position along the line as a fraction (0 = start, 1 = end, default 0.5 = midpoint).
        length:
            Total length of the perpendicular line.  Defaults to the
            original line's length when ``None``.
        time:
            Animation time at which to evaluate the line endpoints.
        **kwargs:
            Extra keyword arguments forwarded to the new Line constructor.
        """
        x1, y1 = self.p1.at_time(time)
        x2, y2 = self.p2.at_time(time)
        dx, dy = -(y2 - y1), x2 - x1  # perpendicular direction
        mag = math.hypot(dx, dy)
        if length is None:
            length = mag
        px = x1 + t * (x2 - x1)
        py = y1 + t * (y2 - y1)
        if mag > 0:
            dx, dy = dx / mag * length / 2, dy / mag * length / 2
        return Line(x1=px - dx, y1=py - dy, x2=px + dx, y2=py + dy, **kwargs)

    def bisector(self, time=0, length=200, **kwargs):
        """Return the perpendicular bisector (at midpoint). Alias for ``perpendicular_at(t=0.5)``."""
        return self.perpendicular_at(t=0.5, length=length, time=time, **kwargs)

    def extend(self, factor=1.5, start=0, end=None, easing=easings.smooth):
        """Scale the line length by *factor* while keeping the midpoint fixed.

        ``factor=2`` doubles the length.  ``factor=0.5`` halves it.

        Parameters
        ----------
        factor:
            Multiplicative factor for the line length.
        start:
            Time at which the change begins.
        end:
            Time at which the change ends.  ``None`` means instant.
        easing:
            Easing function for the animation.

        Returns
        -------
        self
        """
        x1, y1 = self.p1.at_time(start)
        x2, y2 = self.p2.at_time(start)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = (x2 - x1) / 2 * factor, (y2 - y1) / 2 * factor
        _set_attr(self.p1, start, end, (mx - dx, my - dy), easing)
        _set_attr(self.p2, start, end, (mx + dx, my + dy), easing)
        return self

    def scale_length(self, factor=2.0, time=0):
        """Scale line length by *factor* in place, keeping the midpoint fixed.

        ``factor=2`` doubles the length while the midpoint stays the same.

        Parameters
        ----------
        factor:
            Multiplicative factor for the line length.
        time:
            Time at which to read/set the endpoints.
        """
        return self.extend(factor=factor, start=time)

    def parallel(self, offset=50, time=0, **kwargs):
        """Return a new Line parallel to this one, offset perpendicular by offset pixels.
        Extra kwargs are forwarded to the new Line constructor."""
        x1, y1 = self.p1.at_time(time)
        x2, y2 = self.p2.at_time(time)
        dx, dy = x2 - x1, y2 - y1
        line_len = math.hypot(dx, dy)
        if line_len == 0:
            return Line(x1, y1, x2, y2, **kwargs)
        nx, ny = -dy / line_len, dx / line_len
        return Line(x1 + nx * offset, y1 + ny * offset,
                    x2 + nx * offset, y2 + ny * offset, **kwargs)

    def parallel_through(self, point, time=0, **kwargs):
        """Return a new Line parallel to this one, passing through the given point.

        The returned line has the same direction and length as this line, but
        its midpoint is placed at *point*.

        Parameters
        ----------
        point:
            An ``(x, y)`` tuple through which the new line should pass.
            The new line's midpoint is placed at this location.
        time:
            Animation time at which to read this line's direction and length.
        **kwargs:
            Extra keyword arguments forwarded to the :class:`Line` constructor
            (e.g. ``stroke``, ``stroke_width``).

        Returns
        -------
        Line
            A new Line with the same direction and length as this line,
            centered on *point*.

        Example
        -------
        >>> l = Line(0, 0, 200, 0)
        >>> l2 = l.parallel_through((100, 50))
        >>> l2.get_start()   # (0.0, 50.0)
        >>> l2.get_end()     # (200.0, 50.0)
        """
        x1, y1 = self.p1.at_time(time)
        x2, y2 = self.p2.at_time(time)
        dx, dy = x2 - x1, y2 - y1
        px, py = point
        # Center the parallel line on the given point
        return Line(x1=px - dx / 2, y1=py - dy / 2,
                    x2=px + dx / 2, y2=py + dy / 2, **kwargs)

    def rotate_around_midpoint(self, angle_deg, time=0):
        """Rotate line endpoints around the midpoint by angle_deg degrees."""
        mx, my = self.get_midpoint(time)
        angle = math.radians(angle_deg)
        for p in [self.p1, self.p2]:
            px, py = p.at_time(time)
            dx, dy = px - mx, py - my
            new_dx = dx * math.cos(angle) - dy * math.sin(angle)
            new_dy = dx * math.sin(angle) + dy * math.cos(angle)
            p.set_onward(time, (mx + new_dx, my + new_dy))
        return self

    def _intersect_params(self, other, time=0):
        """Return (t, u) line-line intersection parameters, or None if parallel.

        t is the parameter along self, u along other.  The intersection
        point is ``p1 + t * (p2 - p1)`` on self.
        """
        x1, y1 = self.p1.at_time(time)
        x2, y2 = self.p2.at_time(time)
        x3, y3 = other.p1.at_time(time)
        x4, y4 = other.p2.at_time(time)
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if abs(denom) < 1e-10:
            return None
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
        return (t, u)

    def intersect_line(self, other, time=0):
        """Return intersection point (x, y) of this line with another, or None if parallel."""
        params = self._intersect_params(other, time)
        if params is None:
            return None
        t = params[0]
        x1, y1 = self.p1.at_time(time)
        x2, y2 = self.p2.at_time(time)
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))

    def intersect_segment(self, other, time=0):
        """Return the intersection point only if it lies within both segments.

        Unlike :meth:`intersect_line`, which treats each line as extending
        infinitely, this method returns ``None`` unless the intersection point
        lies between p1 and p2 of **both** line segments.

        Parameters
        ----------
        other : Line
            Another Line segment to test against.
        time:
            Animation time at which to read endpoint coordinates.

        Returns
        -------
        tuple[float, float] | None
            ``(x, y)`` of the intersection if it lies within both segments,
            otherwise ``None``.
        """
        params = self._intersect_params(other, time)
        if params is None:
            return None
        t, u = params
        if t < -1e-10 or t > 1 + 1e-10 or u < -1e-10 or u > 1 + 1e-10:
            return None
        x1, y1 = self.p1.at_time(time)
        x2, y2 = self.p2.at_time(time)
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))

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

    def closest_point_on_segment(self, px, py, time=0):
        """Return the closest point on this line **segment** to point (px, py).

        Unlike :meth:`project_point`, which projects onto the infinite line,
        this method clamps the parameter *t* to ``[0, 1]`` so the result
        always lies between p1 and p2.

        Parameters
        ----------
        px, py:
            Coordinates of the external point.
        time:
            Animation time at which to read the endpoint coordinates.

        Returns
        -------
        tuple[float, float]
            ``(x, y)`` of the closest point on the segment.
        """
        t = max(0.0, min(1.0, self.parameter_at(px, py, time)))
        x1, y1 = self.p1.at_time(time)
        x2, y2 = self.p2.at_time(time)
        return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))

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

    def project_onto(self, other, time=0, **kwargs):
        """Project this line segment onto another line and return the projection.

        The projection is the "shadow" of this line segment cast onto the
        infinite line defined by *other*.  Each endpoint of ``self`` is
        orthogonally projected onto *other*, and the resulting segment is
        returned as a new :class:`Line`.

        Parameters
        ----------
        other:
            The :class:`Line` onto which to project.
        time:
            Animation time at which to evaluate both lines.
        **kwargs:
            Extra styling keyword arguments forwarded to the new Line.

        Returns
        -------
        Line
            A new Line whose endpoints are the projections of self's
            endpoints onto *other*.
        """
        p1 = other.project_point(*self.get_start(time), time=time)
        p2 = other.project_point(*self.get_end(time), time=time)
        return Line(x1=p1[0], y1=p1[1], x2=p2[0], y2=p2[1], **kwargs)

    def get_normal_line(self, t=0.5, length=100, time=0, **kwargs):
        """Alias for :meth:`perpendicular_at` with default length=100."""
        return self.perpendicular_at(t=t, length=length, time=time, **kwargs)

    def intersection(self, other, time=0):
        """Return the intersection of this line with *other*.

        Dispatches based on the type of *other*:

        - If *other* is a :class:`Line`, delegates to
          :meth:`intersect_segment` and returns a single ``(x, y)``
          tuple or ``None``.
        - If *other* is a :class:`Circle` (or :class:`Ellipse`),
          delegates to ``other.intersect_line(self, time)`` and returns
          a list of ``(x, y)`` tuples (may be empty).

        Parameters
        ----------
        other:
            A Line or Circle instance.
        time:
            Animation time at which to evaluate geometry.

        Returns
        -------
        tuple | list | None
            Single point for Line-Line (or None), list of points for
            Line-Circle.

        Raises
        ------
        TypeError
            If *other* is not a Line or Circle.
        """
        if isinstance(other, Line):
            return self.intersect_segment(other, time)
        # Circle (subclass of Ellipse) or any object with intersect_line
        if hasattr(other, 'intersect_line'):
            return other.intersect_line(self, time)
        raise TypeError(f"intersection not supported between Line and {type(other).__name__}")

    def reflect_over(self, other, time=0, **kwargs):
        """Reflect this line's endpoints over another line and return the result.

        Each endpoint is reflected across the infinite line defined by
        *other* using the standard reflection formula::

            reflected = 2 * projection - original

        Parameters
        ----------
        other:
            The :class:`Line` to reflect over.
        time:
            Animation time at which to evaluate both lines.
        **kwargs:
            Extra styling keyword arguments forwarded to the new Line.

        Returns
        -------
        Line
            A new Line whose endpoints are the reflections of self's
            endpoints over *other*.
        """
        s1 = self.get_start(time)
        s2 = self.get_end(time)
        proj1 = other.project_point(s1[0], s1[1], time=time)
        proj2 = other.project_point(s2[0], s2[1], time=time)
        r1 = (2 * proj1[0] - s1[0], 2 * proj1[1] - s1[1])
        r2 = (2 * proj2[0] - s2[0], 2 * proj2[1] - s2[1])
        return Line(x1=r1[0], y1=r1[1], x2=r2[0], y2=r2[1], **kwargs)

    def bisector(self, time=0, length=None, **kwargs):
        """Return the perpendicular bisector of this line.

        The bisector passes through the midpoint and is perpendicular to
        the direction from p1 to p2.  Its total length defaults to the
        length of this line if *length* is not specified.

        Parameters
        ----------
        time:
            Animation time at which to read the line's endpoints.
        length:
            Total length of the returned bisector line.  ``None`` means
            use this line's own length.
        **kwargs:
            Extra keyword arguments forwarded to the :class:`Line`
            constructor (e.g. ``stroke``, ``stroke_width``).

        Returns
        -------
        Line
            A new Line centred at the midpoint, perpendicular to this line.
        """
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

    def __init__(self, text='', x: float = 960, y: float = 540, font_size: float = 48, text_anchor=None, font_family=None, creation: float = 0, z: float = 0, **styling_kwargs):
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

    def starts_with(self, prefix, time=0):
        """Return True if the text starts with *prefix* at the given time."""
        return self.text.at_time(time).startswith(prefix)

    def ends_with(self, suffix, time=0):
        """Return True if the text ends with *suffix* at the given time."""
        return self.text.at_time(time).endswith(suffix)

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
            _ramp(start, dur, opacity, easing), stay=True)
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
                _ramp(start, dur, opacity, easing), stay=True)
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
        _set_attr(self.font_size, start, end, size, easing)
        return self

    def bold(self, weight='bold'):
        """Set the font weight to bold.

        Modifies the SVG ``font-weight`` attribute.  Call with no arguments
        to make the text bold; pass ``weight='normal'`` to remove boldness.

        Parameters
        ----------
        weight:
            CSS font-weight value (e.g. ``'bold'``, ``'normal'``, ``'700'``).

        Returns
        -------
        self
            For method chaining.
        """
        self._font_weight = weight if weight != 'normal' else None
        return self

    def italic(self, style='italic'):
        """Set the font style to italic.

        Modifies the SVG ``font-style`` attribute.  Call with no arguments
        to make the text italic; pass ``style='normal'`` to remove italics.

        Parameters
        ----------
        style:
            CSS font-style value (e.g. ``'italic'``, ``'oblique'``, ``'normal'``).

        Returns
        -------
        self
            For method chaining.
        """
        self._font_style = style if style != 'normal' else None
        return self

    def set_font_family(self, family, start=0):
        """Set the font family for this text element.

        Modifies the SVG ``font-family`` attribute.  Pass ``None`` to
        remove a previously set font family.

        Parameters
        ----------
        family:
            CSS font-family value (e.g. ``'monospace'``, ``'Arial'``,
            ``'serif'``).  Pass ``None`` to clear.
        start:
            Time at which the change takes effect (unused for this
            discrete property, kept for API consistency).

        Returns
        -------
        self
            For method chaining.
        """
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

    def update_text(self, new_text, start=0):
        """Instantly change the displayed text from *start* onward.

        This is a convenience wrapper around
        ``self.text.set_onward(start, new_text)`` for simple text
        replacements that don't need an animated transition.

        Parameters
        ----------
        new_text:
            The new text string to display.
        start:
            Time from which the new text is shown.

        Returns
        -------
        self
        """
        self.text.set_onward(start, new_text)
        return self

    def reverse_text(self, time=0):
        """Reverse the text at the given time."""
        text = self.text.at_time(time)
        if isinstance(text, str):
            self.text.set_onward(time, text[::-1])
        return self

    def reverse(self, time=0):
        """Return the text content reversed (does not modify the object)."""
        return self.text.at_time(time)[::-1]

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

    def char_count(self, time=0):
        """Return the number of characters in the text content at the given time."""
        return len(self.text.at_time(time))

    def word_count(self, time=0):
        """Return the number of whitespace-separated words.
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

    def split_lines(self, time=0, line_spacing=1.4):
        """Split multi-line text (containing newlines) into separate Text objects.

        Each line of text becomes a separate :class:`Text` positioned
        vertically below the previous one.  Lines are spaced by
        ``font_size * line_spacing`` pixels.

        Parameters
        ----------
        time:
            Animation time at which to read the current text content,
            position, and font size.
        line_spacing:
            Vertical spacing as a multiple of the font size (default 1.4).
            A value of 1.0 means lines are packed tightly; 1.4 adds 40%
            extra space for readability.

        Returns
        -------
        VCollection
            A collection of Text objects, one per line.  If the text has
            no newlines, the collection contains a single Text object
            with the full text.

        Example
        -------
        >>> t = Text(text='Hello\\nWorld\\nFoo', x=100, y=200)
        >>> parts = t.split_lines()
        >>> len(parts.objects)  # 3
        """
        from vectormation._base import VCollection
        full = str(self.text.at_time(time))
        lines = full.split('\n')
        x = self.x.at_time(time)
        y = self.y.at_time(time)
        fs = self.font_size.at_time(time)
        step = fs * line_spacing
        fill_val = self.styling.fill.time_func(time)
        parts = []
        for i, line_text in enumerate(lines):
            t = Text(text=line_text, x=x, y=y + i * step, font_size=fs,
                     text_anchor=self._text_anchor, creation=time,
                     stroke_width=0, fill=fill_val)
            parts.append(t)
        return VCollection(*parts)

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

    def truncate(self, n, ellipsis='...', time=0):
        """Truncate the text to at most *n* characters, appending *ellipsis* if trimmed.

        If the text is already *n* characters or shorter, nothing changes.
        Otherwise the text is shortened to ``n - len(ellipsis)`` characters
        plus the ellipsis string, so the total length is exactly *n*.

        Parameters
        ----------
        n:
            Maximum number of characters in the resulting text (including
            the ellipsis).  Must be >= ``len(ellipsis)``.
        ellipsis:
            The string to append when truncation occurs (default ``'...'``).
            Set to ``''`` to simply chop the text without any suffix.
        time:
            Animation time at which to read and modify the text.

        Returns
        -------
        self
            For method chaining.

        Raises
        ------
        ValueError
            If *n* is less than the length of the ellipsis string.

        Examples
        --------
        >>> t = Text('Hello, World!')
        >>> t.truncate(8)
        >>> t.get_text()   # 'Hello...'
        >>> t2 = Text('Hi')
        >>> t2.truncate(10)   # no change (already short enough)
        >>> t2.get_text()     # 'Hi'
        """
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

    def split_into_words(self, time=0, **kwargs):
        """Split text into a VCollection of individual word Text objects.

        Each word becomes a separate Text object positioned approximately
        where it would appear in the original text.  Uses
        :meth:`_estimate_width` for more accurate per-character width
        estimation than the fixed ``CHAR_WIDTH_FACTOR`` used by
        :meth:`split_words`.

        Parameters
        ----------
        time:
            Animation time at which to read text content, position and
            font size.
        **kwargs:
            Extra keyword arguments forwarded to each :class:`Text`
            constructor (e.g. ``fill``, ``stroke_width``).

        Returns
        -------
        VCollection
            A collection of Text objects, one per whitespace-delimited word.
        """
        from vectormation._base import VCollection
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

    def add_background_rectangle(self, color='#000000', opacity=0.5, padding=10, time=0):
        """Create a Rectangle behind the text, sized from bbox + padding.

        Parameters
        ----------
        color:
            Fill color for the background rectangle.
        opacity:
            Fill opacity for the background rectangle.
        padding:
            Extra padding in pixels around the text bbox.
        time:
            Time at which to read the text bbox.

        Returns
        -------
        VCollection
            A VCollection containing the background rectangle and this text.
        """
        from vectormation._base import VCollection
        bx, by, bw, bh = self.bbox(time)
        rect = Rectangle(
            bw + 2 * padding, bh + 2 * padding,
            x=bx - padding, y=by - padding,
            creation=time, z=self.z.at_time(time) - 1,
            fill=color, fill_opacity=opacity, stroke_width=0,
        )
        return VCollection(rect, self, creation=time)

    def wrap(self, max_width, time=0):
        """Word-wrap text to fit within *max_width* pixels.

        Splits the text into words and accumulates them into lines, starting
        a new line whenever the next word would exceed *max_width*.  Returns
        a ``VCollection`` of :class:`Text` objects (one per line), positioned
        vertically with ``font_size * 1.2`` line spacing.

        Parameters
        ----------
        max_width:
            Maximum width in pixels for each line.
        time:
            Animation time at which to read the text and font size.

        Returns
        -------
        VCollection
            A VCollection of Text objects, one per wrapped line.
        """
        from vectormation._base import VCollection
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
            if self._text_anchor:
                t._text_anchor = self._text_anchor
            if self._font_family:
                t._font_family = self._font_family
            if self._font_weight:
                t._font_weight = self._font_weight
            if self._font_style:
                t._font_style = self._font_style
            parts.append(t)
        return VCollection(*parts)

    def to_svg(self, time):
        anchor = f" text-anchor='{self._text_anchor}'" if self._text_anchor else ''
        weight = f" font-weight='{self._font_weight}'" if self._font_weight else ''
        fstyle = f" font-style='{self._font_style}'" if self._font_style else ''
        ffamily = f" font-family='{self._font_family}'" if self._font_family else ''
        txt = _xml_escape(str(self.text.at_time(time)))
        return (f"<text x='{self.x.at_time(time)}' y='{self.y.at_time(time)}'"
                f" font-size='{self.font_size.at_time(time)}'{anchor}{weight}{fstyle}{ffamily}{self.styling.svg_style(time)}"
                f">{txt}</text>")


class CountAnimation(Text):
    """Text that animates a number counting from start_val to end_val."""
    def __init__(self, start_val=0, end_val=100, start: float = 0, end: float = 1,
                 fmt='{:.0f}', easing=easings.smooth,
                 x: float = 960, y: float = 540, font_size: float = 60, text_anchor=None, creation: float = 0, z: float = 0, **styling_kwargs):
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
    def __init__(self, value=0, creation: float = 0):
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
        return self._tracker

    def set_value(self, val, start=0):
        self._tracker.set_onward(start, val)
        return self

    def animate_value(self, target, start, end, easing=easings.smooth):
        self._tracker.move_to(start, end, target, easing=easing)
        return self


class Lines(Polygon):
    """Open polyline — a Polygon with closed=False."""
    def __init__(self, *vertices, creation: float = 0, z: float = 0, **styling_kwargs):
        super().__init__(*vertices, closed=False, creation=creation, z=z, **styling_kwargs)

    def __repr__(self):
        return f'Lines({len(self.vertices)} vertices)'


class Trace(VObject):
    """Follows a point every dt and renders as a polyline."""
    def __init__(self, point, start=0, end=None, dt=1/60, z: float = 0, **styling_kwargs):
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

    def shift(self, dx=0, dy=0, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Shift via styling transform (Trace points are immutable)."""
        if end is None:
            self.styling.dx.add_onward(start, dx)
            self.styling.dy.add_onward(start, dy)
        else:
            s, e = start, end
            d = max(e - s, 1e-9)
            self.styling.dx.add_onward(s, _ramp(s, d, dx, easing), last_change=e)
            self.styling.dy.add_onward(s, _ramp(s, d, dy, easing), last_change=e)
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
    def __init__(self, path, x=0, y=0, creation: float = 0, z: float = 0, **styling_kwargs):
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

    def shift(self, dx=0, dy=0, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Shift via transform styling, accounting for current rotation."""
        rot = self.styling.rotation.at_time(0)
        if rot[0] != 0:
            dx, dy = _rotate_point(dx, dy, rot[1], rot[2], -rot[0] * math.pi / 180)
        if end is None:
            self.styling.dx.add_onward(start, dx)
            self.styling.dy.add_onward(start, dy)
        else:
            s, e = start, end
            d = max(e - s, 1e-9)
            self.styling.dx.add_onward(s, _ramp(s, d, dx, easing), last_change=e)
            self.styling.dy.add_onward(s, _ramp(s, d, dy, easing), last_change=e)
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

    def tangent_at(self, proportion, time=0):
        """Return the unit tangent direction (dx, dy) at a proportional distance along the path.

        Parameters
        ----------
        proportion:
            A value in [0, 1] specifying the position along the arc length.
        time:
            Animation time at which to read the path data.

        Returns
        -------
        (dx, dy)
            A unit vector tuple representing the tangent direction at the
            given proportion.  Returns ``(0.0, 0.0)`` for empty or
            zero-length paths.
        """
        d = self.d.at_time(time)
        if not d:
            return (0.0, 0.0)
        from svgpathtools import parse_path
        parsed = parse_path(d)
        total = parsed.length()
        if total == 0:
            return (0.0, 0.0)
        t_param = parsed.ilength(total * max(0, min(1, proportion)))
        # derivative() returns a complex number (dx + dy*j)
        deriv = parsed.derivative(t_param)
        dx, dy = deriv.real, deriv.imag
        mag = math.hypot(dx, dy)
        if mag < 1e-12:
            return (0.0, 0.0)
        return (dx / mag, dy / mag)

    def trim(self, t_start=0.0, t_end=1.0, time=0):
        """Return a new Path representing the sub-path between proportions
        *t_start* and *t_end* along the arc length.

        Both parameters are clamped to ``[0, 1]`` and represent fractions of
        the total arc length.  The styling of the returned Path is copied
        from this Path at *time*.

        Parameters
        ----------
        t_start:
            Start proportion along the arc length (0 = path start).
        t_end:
            End proportion along the arc length (1 = path end).
        time:
            Animation time at which to read the path data.

        Returns
        -------
        Path
            A new Path covering the requested sub-range.
        """
        d = self.d.at_time(time)
        if not d:
            return Path('')
        from svgpathtools import parse_path
        parsed = parse_path(d)
        total = parsed.length()
        if total == 0:
            return Path(d)
        t_start = max(0.0, min(1.0, t_start))
        t_end = max(0.0, min(1.0, t_end))
        if t_start >= t_end:
            return Path('')
        T0 = parsed.ilength(total * t_start)
        T1 = parsed.ilength(total * t_end)
        sub = parsed.cropped(T0, T1)
        # Copy styling.  Color attrs need raw tuples, not rendered strings.
        style_kwargs = {}
        for name in ('fill_opacity', 'stroke_width',
                      'stroke_opacity', 'opacity', 'stroke_dasharray',
                      'stroke_dashoffset', 'stroke_linecap', 'stroke_linejoin',
                      'fill_rule'):
            style_kwargs[name] = getattr(self.styling, name).at_time(time)
        for name in ('fill', 'stroke'):
            attr = getattr(self.styling, name)
            style_kwargs[name] = attr.time_func(time)
        return Path(sub.d(), **style_kwargs)

    def reverse(self, time=0):
        """Return a new Path with the segments reversed.

        Uses ``svgpathtools`` to parse the ``d`` attribute at *time*,
        reverses the parsed path, and converts it back to a ``d``-string.
        Styling is copied from this Path at *time*.

        Parameters
        ----------
        time:
            Animation time at which to read the path data and styling.

        Returns
        -------
        Path
            A new Path with the reversed segment order.
        """
        d = self.d.at_time(time)
        if not d:
            return Path('')
        from svgpathtools import parse_path
        parsed = parse_path(d)
        reversed_d = parsed.reversed().d()
        # Copy styling (same pattern as trim / Polygon.to_path)
        style_kwargs = {}
        for name in ('fill_opacity', 'stroke_width',
                      'stroke_opacity', 'opacity', 'stroke_dasharray',
                      'stroke_dashoffset', 'stroke_linecap', 'stroke_linejoin',
                      'fill_rule'):
            style_kwargs[name] = getattr(self.styling, name).at_time(time)
        for name in ('fill', 'stroke'):
            attr = getattr(self.styling, name)
            style_kwargs[name] = attr.time_func(time)
        return Path(reversed_d, **style_kwargs)

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
    def __init__(self, n, radius=120, cx=960, cy=540, angle=0, creation: float = 0, z: float = 0, **styling_kwargs):
        n = max(n, 1)
        self._n = n
        self._radius = radius
        angle_rad = angle * math.pi / 180
        vertices = [
            (cx + radius * math.cos(math.tau * k / n + angle_rad),
             cy - radius * math.sin(math.tau * k / n + angle_rad))
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
                 angle=90, creation: float = 0, z: float = 0, **styling_kwargs):
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
    def __init__(self, side_length, angle=0, cx=960, cy=540, creation: float = 0, z: float = 0, **styling_kwargs):
        self._side_length = side_length
        radius = side_length / math.sqrt(3)
        super().__init__(3, radius=radius, cx=cx, cy=cy, angle=angle + 90,
                         creation=creation, z=z, **styling_kwargs)

    def __repr__(self):
        return f'EquilateralTriangle(side={self._side_length:.0f})'


class RoundedRectangle(Rectangle):
    """Rectangle with rounded corners (default corner_radius=10)."""
    def __init__(self, width, height, x=960, y=540, corner_radius=12, creation: float = 0, z: float = 0, **styling_kwargs):
        super().__init__(width, height, x=x, y=y, rx=corner_radius, ry=corner_radius,
                         creation=creation, z=z, **styling_kwargs)

    def __repr__(self):
        return f'RoundedRectangle({self.width.at_time(0):.0f}x{self.height.at_time(0):.0f}, r={self.rx.at_time(0):.0f})'

    def get_corner_radius(self, time=0):
        return self.rx.at_time(time)

    def set_corner_radius(self, value, start=0, end=None, easing=easings.smooth):
        """Animate corner radius to value."""
        _set_attr(self.rx, start, end, value, easing)
        _set_attr(self.ry, start, end, value, easing)
        return self


class SurroundingRectangle(RoundedRectangle):
    """Rectangle that surrounds a target object with padding.
    If follow=True (default), tracks the target as it moves."""
    def __init__(self, target, buff=SMALL_BUFF, corner_radius=6, follow=True,
                 creation: float = 0, z: float = 0, **styling_kwargs):
        bx, by, bw, bh = target.bbox(creation)
        style_kw = {'fill_opacity': 0, 'stroke': '#FFFF00'} | styling_kwargs
        super().__init__(bw + 2*buff, bh + 2*buff, x=bx - buff, y=by - buff,
                         corner_radius=corner_radius, creation=creation, z=z, **style_kw)
        if follow:
            _bbox = _cached_bbox(target)
            self.x.set_onward(creation, lambda t: _bbox(t)[0] - buff)
            self.y.set_onward(creation, lambda t: _bbox(t)[1] - buff)
            self.width.set_onward(creation, lambda t: _bbox(t)[2] + 2*buff)
            self.height.set_onward(creation, lambda t: _bbox(t)[3] + 2*buff)


class SurroundingCircle(Circle):
    """Circle that surrounds a target object with padding.
    If follow=True (default), tracks the target as it moves."""
    def __init__(self, target, buff=SMALL_BUFF, follow=True,
                 creation: float = 0, z: float = 0, **styling_kwargs):
        bx, by, bw, bh = target.bbox(creation)
        r = math.hypot(bw, bh) / 2 + buff
        cx, cy = bx + bw / 2, by + bh / 2
        style_kw = {'fill_opacity': 0, 'stroke': '#FFFF00'} | styling_kwargs
        super().__init__(r=r, cx=cx, cy=cy, creation=creation, z=z, **style_kw)
        if follow:
            _bbox = _cached_bbox(target)
            self.c.set_onward(creation, lambda t: (_bbox(t)[0] + _bbox(t)[2] / 2,
                                                    _bbox(t)[1] + _bbox(t)[3] / 2))
            _r_func = lambda t: math.hypot(_bbox(t)[2], _bbox(t)[3]) / 2 + buff
            self.rx.set_onward(creation, _r_func)
            self.ry.set_onward(creation, _r_func)


class BackgroundRectangle(Rectangle):
    """Semi-transparent rectangle behind a target object (useful for text backgrounds)."""
    def __init__(self, target, buff=SMALL_BUFF, creation: float = 0, z=-1, **styling_kwargs):
        bx, by, bw, bh = target.bbox(creation)
        style_kw = {'fill': '#000', 'fill_opacity': 0.75, 'stroke_width': 0} | styling_kwargs
        super().__init__(bw + 2*buff, bh + 2*buff, x=bx - buff, y=by - buff,
                         creation=creation, z=z, **style_kw)


class Arc(VObject):
    """SVG arc segment defined by centre, radius, and start/end angles (degrees)."""
    def __init__(self, cx: float = 960, cy: float = 540, r: float = 120, start_angle: float = 0, end_angle: float = 90,
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
        _set_attr(self.r, start, end, value, easing)
        return self

    def set_angles(self, start_angle=None, end_angle=None, start=0, end=None, easing=easings.smooth):
        """Animate or set the arc start/end angles (degrees)."""
        if start_angle is not None:
            _set_attr(self.start_angle, start, end, start_angle, easing)
        if end_angle is not None:
            _set_attr(self.end_angle, start, end, end_angle, easing)
        return self

    def animate_sweep(self, target_angle, start=0, end=None, easing=None):
        """Animate the end angle of this arc to *target_angle* (degrees).

        This effectively animates the "sweep" of the arc by moving the
        end angle while keeping the start angle fixed.

        Parameters
        ----------
        target_angle:
            The target end angle in degrees.
        start:
            Time at which the animation begins (or the instant change
            occurs if *end* is ``None``).
        end:
            Time at which the animation ends.  ``None`` means an
            instant change at *start*.
        easing:
            Easing function for the animation.  Defaults to
            ``easings.smooth``.

        Returns
        -------
        self
        """
        if easing is None:
            easing = easings.smooth
        _set_attr(self.end_angle, start, end, target_angle, easing)
        return self

    def get_midpoint(self, time=0):
        """Return the point at the midpoint angle of the arc."""
        mid = (self.start_angle.at_time(time) + self.end_angle.at_time(time)) / 2
        return self.point_at_angle(mid, time)

    def get_midpoint_on_arc(self, time=0):
        """Alias for :meth:`get_midpoint` (point on the arc, not the chord)."""
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

    def split_into(self, n=2, time=0, **kwargs):
        """Split this arc into *n* equal sub-arcs.

        Each sub-arc shares the same centre and radius but spans an equal
        fraction of the total sweep angle.

        Parameters
        ----------
        n:
            Number of sub-arcs to create (must be >= 1).  Default is 2.
        time:
            Animation time at which to read the arc geometry.
        **kwargs:
            Extra keyword arguments forwarded to each :class:`Arc`
            constructor (e.g. ``stroke``, ``stroke_width``).

        Returns
        -------
        list[Arc]
            A list of *n* Arc objects.
        """
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

    def contains_point(self, px, py, time=0, tol=2):
        """Return True if (px, py) lies on the arc within tolerance.

        The point must be within *tol* pixels of the arc radius **and** its
        angle (relative to the arc centre) must fall within the arc's angular
        sweep.

        Parameters
        ----------
        px, py:
            Point coordinates to test.
        time:
            Animation time at which to evaluate the arc geometry.
        tol:
            Distance tolerance in pixels (default 2).
        """
        cx = self.cx.at_time(time)
        cy = self.cy.at_time(time)
        r = self.r.at_time(time)
        # Check distance to centre equals radius (within tolerance)
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

    def get_chord(self, time=0, **kwargs):
        """Return a Line connecting the start and end points of the arc.

        The chord is the straight line segment from the arc's start point
        to its end point — useful for geometry visualizations.

        Parameters
        ----------
        time:
            Animation time at which to evaluate the arc geometry.
        **kwargs:
            Extra keyword arguments forwarded to the :class:`Line`
            constructor (e.g. ``stroke``, ``stroke_width``).

        Returns
        -------
        Line
            A Line from the arc's start point to its end point.
        """
        x1, y1 = self.get_start_point(time)
        x2, y2 = self.get_end_point(time)
        return Line(x1=x1, y1=y1, x2=x2, y2=y2, **kwargs)

    def __repr__(self):
        return f'Arc(r={self.r.at_time(0):.0f}, {self.start_angle.at_time(0):.0f}°-{self.end_angle.at_time(0):.0f}°)'

    def to_svg(self, time):
        return f"<path d='{self.path(time)}'{self.styling.svg_style(time)} />"


class Wedge(Arc):
    """Arc that closes through the centre (pie/wedge shape)."""
    def __init__(self, cx: float = 960, cy: float = 540, r: float = 120, start_angle: float = 0, end_angle: float = 90,
                 creation: float = 0, z: float = 0, **styling_kwargs):
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
        _set_attr(self.inner_r, start, end, value, easing)
        return self

    def set_outer_radius(self, value, start=0, end=None, easing=easings.smooth):
        """Animate or set the outer radius."""
        _set_attr(self.outer_r, start, end, value, easing)
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
    def __init__(self, x1: float = 0, y1: float = 0, x2: float = 100, y2: float = 100, dash='10,5', creation: float = 0, z: float = 0, **styling_kwargs):
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
    def __init__(self, width=480, creation: float = 0, z: float = 0, **kwargs):
        height = width * 9 / 16
        super().__init__(width=width, height=height, creation=creation, z=z, **kwargs)


class ArcBetweenPoints(Arc):
    """Arc connecting two points, bulging by a given angle.

    angle: how much the arc bulges (degrees). Positive = left of start→end.
    """
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


class Elbow(Lines):
    """Right-angle connector (L-shape) between two directions.

    width/height: pixel size of each arm.
    """
    def __init__(self, cx=960, cy=540, width=40, height=40,
                 creation: float = 0, z: float = 0, **styling_kwargs):
        style_kw = {'stroke': '#fff', 'stroke_width': DEFAULT_STROKE_WIDTH, 'fill_opacity': 0} | styling_kwargs
        super().__init__(
            (cx + width, cy), (cx, cy), (cx, cy + height),
            creation=creation, z=z, **style_kw)


class AnnularSector(Arc):
    """Sector of an annulus (ring wedge).

    Like a Wedge but with an inner radius cut out.
    """
    def __init__(self, inner_radius=60, outer_radius=120, cx=960, cy=540,
                 start_angle=0, end_angle=90, creation: float = 0, z: float = 0, **styling_kwargs):
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
        _set_attr(self.inner_r, start, end, value, easing)
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


class _TextBlockMixin:
    """Shared position/path methods for Paragraph, BulletedList, NumberedList."""

    def _extra_attrs(self):
        return [self.x, self.y]

    def _shift_reals(self):
        return [(self.x, self.y)]

    def snap_points(self, time):
        return [(self.x.at_time(time), self.y.at_time(time))]

    def path(self, time):
        return ''


class Paragraph(_TextBlockMixin, VObject):
    """Multi-line text with alignment and line spacing."""
    def __init__(self, *lines, x=960, y=540, font_size=36, alignment='left',
                 line_spacing=1.4, creation: float = 0, z: float = 0, **styling_kwargs):
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


class BulletedList(_TextBlockMixin, VObject):
    """List of items with bullet points."""
    def __init__(self, *items, x=200, y=200, font_size=36, bullet='\u2022',
                 indent=40, line_spacing=1.6, creation: float = 0, z: float = 0, **styling_kwargs):
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


class NumberedList(_TextBlockMixin, VObject):
    """List of items with numeric labels (1. 2. 3. ...)."""
    def __init__(self, *items, x=200, y=200, font_size=36, indent=50,
                 line_spacing=1.6, start_number=1, creation: float = 0, z: float = 0, **styling_kwargs):
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
