"""Shape classes: Polygon, Circle, Rectangle, Line, Text, Arc, etc."""
from __future__ import annotations
import math
from typing import Any

import vectormation.easings as easings
import vectormation.attributes as attributes
import vectormation.style as style
from vectormation._constants import SMALL_BUFF, DEFAULT_STROKE_WIDTH, DEFAULT_DOT_RADIUS, TEXT_Y_OFFSET, ORIGIN, _distance, _circumcenter, _normalize
from vectormation._base import VObject, _set_attr

def _cross2d(o, a, b):
    """Cross product of vectors OA and OB (positive = CCW)."""
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

def _make_time_cache(func):
    """Return a wrapper that caches func(t) per time value."""
    _cache: list[Any] = [None, None]
    def _cached(t) -> Any:
        if _cache[0] != t:
            _cache[0] = t
            _cache[1] = func(t)
        return _cache[1]
    return _cached


def _cached_bbox(target):
    """Return a function that caches target.bbox(t) per time value."""
    return _make_time_cache(target.bbox)

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
        return self.get_vertices(time)

    def bbox(self, time):
        if self._bbox_cache and self._bbox_cache[0] == time and self._bbox_cache[1] == self._bbox_version:
            return self._bbox_cache[2]
        points = [v.at_time(time) for v in self.vertices]
        result = self._bbox_from_points(points, time) or super().bbox(time)
        self._bbox_cache = (time, self._bbox_version, result)
        return result

    def path(self, time):
        vert = [v.at_time(time) for v in self.vertices]
        if not vert:
            return ''
        parts = [f'M {vert[0][0]},{vert[0][1]}'] + [f'L {x},{y}' for x, y in vert[1:]]
        if self.closed:
            parts.append('Z')
        return ' '.join(parts)

    def to_svg(self, time):
        tag = 'polygon' if self.closed else 'polyline'
        pts = ' '.join(f'{x},{y}' for x, y in (v.at_time(time) for v in self.vertices))
        return f"<{tag} points='{pts}'{self.styling.svg_style(time)} />"

    def get_vertices(self, time: float = 0):
        """Return a list of (x, y) tuples for each vertex."""
        return [(float(x), float(y)) for x, y in (v.at_time(time) for v in self.vertices)]

    def move_vertex(self, index, x, y, start=0, end=None, easing=easings.smooth):
        """Animate a single vertex to a new position."""
        n = len(self.vertices)
        if index < -n or index >= n:
            raise IndexError(f"vertex index {index} out of range for polygon with {n} vertices")
        _set_attr(self.vertices[index], start, end, (x, y), easing)
        return self

    def to_path_string(self, time=0):
        """Return an SVG path d-string representation of the polygon."""
        return self.path(time)

    def get_center(self, time=0):
        """Return the centroid (average of vertices)."""
        pts = self.get_vertices(time)
        if not pts:
            return (0.0, 0.0)
        n = len(pts)
        return (sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n)

    def centroid(self, time=0):
        """Return the geometric centroid (cx, cy) using the polygon centroid formula."""
        pts = self.get_vertices(time)
        n = len(pts)
        if n <= 2:
            return self.get_center(time)
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
            return self.get_center(time)
        cx /= (6 * signed_area)
        cy /= (6 * signed_area)
        return (cx, cy)

    def perimeter(self, time=0):
        """Return the perimeter (sum of edge lengths)."""
        pts = self.get_vertices(time)
        if len(pts) < 2:
            return 0.0
        total = sum(_distance(a[0], a[1], b[0], b[1])
                    for a, b in zip(pts, pts[1:]))
        if self.closed and len(pts) > 2:
            total += _distance(pts[0][0], pts[0][1], pts[-1][0], pts[-1][1])
        return total

    get_perimeter = perimeter

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
        """Convert the polygon to a :class:`Path` object."""
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
        """Return the signed area using the shoelace formula."""
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

    get_area = area

    def winding_number(self, px, py, time=0):
        """Return the winding number of point (px, py) relative to this polygon."""
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
        """Return True if all edges have the same length (within tolerance)."""
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
        """Return a new Polygon with vertices moved along averaged edge normals."""
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
        """Return a new Polygon inset by *distance* pixels."""
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
        """Return a new Polygon with all vertices rotated by angle_deg degrees."""
        pts = self.get_vertices(time)
        if cx is None or cy is None:
            c = self.get_center(time)
            cx, cy = cx if cx is not None else c[0], cy if cy is not None else c[1]
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
        """Create a Polygon that is the convex hull of the given points using gift-wrapping (Jarvis march)."""
        pts = [(float(p[0]), float(p[1])) for p in points]
        if len(pts) < 3:
            raise ValueError("convex_hull requires at least 3 points")

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
                cross = _cross2d(current, candidate, p)
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
        """Create a Polygon from a simple SVG path string (M/L/Z commands only)."""
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
        """Return a new Polygon that is the convex hull of this polygon's vertices."""
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
        """Return a list of Line objects for each edge of the polygon."""
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
        """Return a list of midpoint (x, y) tuples for each edge."""
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
        """Translate all vertices by (*dx*, *dy*)."""
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
        """Mirror vertices across an axis line."""
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
        """Return the interior angles of the polygon in degrees."""
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

    def get_diagonals(self, time=0, **kwargs):
        """Return all diagonals of a closed polygon as Line objects."""
        pts = self.get_vertices(time)
        n = len(pts)
        if n < 4 or not self.closed:
            return []
        diags = []
        for i in range(n):
            for j in range(i + 2, n):
                if i == 0 and j == n - 1:
                    continue  # skip edge connecting first and last vertex
                diags.append(Line(x1=pts[i][0], y1=pts[i][1],
                                  x2=pts[j][0], y2=pts[j][1], **kwargs))
        return diags

    def bounding_circle(self, time=0, **kwargs):
        """Return the smallest enclosing circle of the polygon's vertices."""
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
                if not boundary:
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
        """Decompose this polygon into triangles using ear-clipping."""
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

        def _point_in_triangle(p, a, b, c):
            d1 = _cross2d(p, a, b)
            d2 = _cross2d(p, b, c)
            d3 = _cross2d(p, c, a)
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
            if _cross2d(a, b, c) <= 0:
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
        """Return a VCollection of Line objects, one per edge, offset outward."""
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
            ux, uy = _normalize(dx, dy)
            nx, ny = ux * gap, uy * gap
            edges.append(Line(x1=ax + nx, y1=ay + ny,
                              x2=bx + nx, y2=by + ny, **kwargs))
        return VCollection(*edges)

    def subdivide_edges(self, iterations=1, time=0, **kwargs):
        """Split each edge at its midpoint, creating a polygon with 2x vertices per iteration."""
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
        """Return a Path with Bezier-smoothed corners."""
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
        """Apply an arbitrary function to all vertices."""
        for v in self.vertices:
            x, y = v.at_time(time)
            nx, ny = func(float(x), float(y))
            v.set_onward(time, (nx, ny))
        return self

    def label_vertices(self, labels=None, offset=20, font_size=24, time=0,
                       creation=0, z=None, **styling_kwargs):
        """Create labeled dots at each vertex.

        Returns a VCollection of (Dot, Text) pairs positioned at each vertex,
        offset outward from the polygon center. Labels default to A, B, C, ..."""
        from vectormation._base import VCollection
        pts = self.get_vertices(time)
        n = len(pts)
        if not n:
            return VCollection()
        if labels is None:
            labels = [chr(65 + i) for i in range(n)]  # A, B, C, ...
        if z is None:
            z = self.z.at_time(time) + 0.1
        cx, cy = self.get_center(time)
        style_kw = {'fill': '#fff', 'stroke_width': 0} | styling_kwargs
        from vectormation._shapes_ext import Text as _Text
        objects = []
        for i, (vx, vy) in enumerate(pts):
            dx, dy = vx - cx, vy - cy
            ux, uy = _normalize(dx, dy)
            lx = vx + ux * offset
            ly = vy + uy * offset
            lbl = labels[i] if i < len(labels) else ''
            objects.append(_Text(text=str(lbl), x=lx,
                                 y=ly + font_size * TEXT_Y_OFFSET,
                                 font_size=font_size, text_anchor='middle',
                                 creation=creation, z=z, **style_kw))
        return VCollection(*objects, creation=creation, z=z)

    def get_subcurve(self, a: float, b: float, time: float = 0, **kwargs):
        """Extract the portion of the polyline between parameters *a* and *b*.

        *a* and *b* are floats in [0, 1] representing fraction of the total
        path length. Returns a new Lines object.
        """
        pts = self.get_vertices(time)
        if len(pts) < 2 or a >= b:
            return Lines(*(pts[:1] or [(0, 0)]), **kwargs)
        # Compute cumulative edge lengths
        cum = [0.0]
        for p0, p1 in zip(pts, pts[1:]):
            cum.append(cum[-1] + math.hypot(p1[0] - p0[0], p1[1] - p0[1]))
        total = cum[-1] if cum[-1] > 0 else 1
        # Convert a, b to absolute lengths
        la, lb = a * total, b * total
        result = []
        for (x0, y0), (x1, y1), s0, s1 in zip(pts, pts[1:], cum, cum[1:]):
            seg_len = s1 - s0
            if s1 <= la or s0 >= lb or seg_len == 0:
                continue
            # Clip segment to [la, lb]
            ta = max(0, (la - s0) / seg_len)
            tb = min(1, (lb - s0) / seg_len)
            if not result:
                result.append((x0 + ta * (x1 - x0), y0 + ta * (y1 - y0)))
            result.append((x0 + tb * (x1 - x0), y0 + tb * (y1 - y0)))
        return Lines(*(result or pts[:1]), **kwargs)

    def __repr__(self):
        return f'Polygon({len(self.vertices)} vertices)'

class Ellipse(VObject):
    def __init__(self, rx: float = 120, ry: float = 60, cx: float = ORIGIN[0], cy: float = ORIGIN[1], z: float = 0, creation: float = 0, **styling_kwargs):
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

    def _ep(self, time: float = 0):
        """Return (cx, cy, rx, ry) evaluated at *time*."""
        cx, cy = self.c.at_time(time)
        return cx, cy, self.rx.at_time(time), self.ry.at_time(time)

    def snap_points(self, time):
        cx, cy, _, _ = self._ep(time)
        return [(float(cx), float(cy))]

    def bbox(self, time):
        cx, cy, rx, ry = self._ep(time)
        return self._bbox_from_points([(cx-rx, cy), (cx+rx, cy), (cx, cy-ry), (cx, cy+ry)], time) or super().bbox(time)

    def path(self, time):
        cx, cy, rx, ry = self._ep(time)
        return f'M{cx-rx},{cy}a{rx},{ry} 0 1,0 {rx*2},0a{rx},{ry} 0 1,0 -{rx*2},0z'

    def get_area(self, time=0):
        """Return the area (pi * rx * ry)."""
        _, _, rx, ry = self._ep(time)
        return math.pi * rx * ry

    def get_perimeter(self, time=0):
        """Approximate perimeter using Ramanujan's second formula (more accurate)."""
        _, _, a, b = self._ep(time)
        h = ((a - b) / (a + b)) ** 2
        return math.pi * (a + b) * (1 + 3 * h / (10 + math.sqrt(4 - 3 * h)))

    get_circumference = get_perimeter

    def eccentricity(self, time=0):
        """Return the eccentricity of the ellipse."""
        _, _, rx, ry = self._ep(time)
        a, b = max(rx, ry), min(rx, ry)
        return 0.0 if a == 0 else math.sqrt(1 - (b / a) ** 2)

    def get_foci(self, time=0):
        """Return the two foci as ((x1,y1), (x2,y2))."""
        cx, cy, rx, ry = self._ep(time)
        a, b = max(rx, ry), min(rx, ry)
        c = math.sqrt(a * a - b * b)
        if rx >= ry:
            return ((cx - c, cy), (cx + c, cy))
        return ((cx, cy - c), (cx, cy + c))

    def point_at_angle(self, degrees, time=0):
        """Return (x, y) on the ellipse at the given angle (degrees, CCW from right)."""
        cx, cy, rx, ry = self._ep(time)
        rad = math.radians(degrees)
        return (cx + rx * math.cos(rad), cy - ry * math.sin(rad))

    def get_point_at_parameter(self, t, time=0):
        """Return (x, y) on the ellipse at parameter t in [0, 1]."""
        cx, cy, rx, ry = self._ep(time)
        angle = math.tau * t
        return (cx + rx * math.cos(angle), cy + ry * math.sin(angle))

    def contains_point(self, px, py, time=0):
        """Return True if point (px, py) is inside the ellipse."""
        cx, cy, rx, ry = self._ep(time)
        if rx == 0 or ry == 0:
            return False
        return ((px - cx) / rx) ** 2 + ((py - cy) / ry) ** 2 <= 1

    def get_rx(self, time=0): return self.rx.at_time(time)
    def get_ry(self, time=0): return self.ry.at_time(time)

    def set_center(self, cx, cy, start=0, end=None, easing=easings.smooth):
        _set_attr(self.c, start, end, (cx, cy), easing); return self

    def set_rx(self, value, start=0, end=None, easing=easings.smooth):
        """Animate the x-radius."""
        _set_attr(self.rx, start, end, value, easing); return self

    def set_ry(self, value, start=0, end=None, easing=easings.smooth):
        """Animate the y-radius."""
        _set_attr(self.ry, start, end, value, easing); return self

    def tangent_at_angle(self, angle_deg, length=200, time=0, **kwargs):
        """Return a tangent Line at the given angle, centered on the ellipse point."""
        px, py, tx, ty = self._tangent_at(angle_deg, time)
        dx, dy = tx * length / 2, ty * length / 2
        return Line(x1=px - dx, y1=py - dy, x2=px + dx, y2=py + dy, **kwargs)

    def _tangent_at(self, angle_deg, time=0):
        """Return (px, py, tx, ty): point on ellipse and unit tangent direction."""
        cx, cy, rx, ry = self._ep(time)
        angle = math.radians(angle_deg)
        px = cx + rx * math.cos(angle)
        py = cy - ry * math.sin(angle)  # SVG y-down
        tx = -rx * math.sin(angle)
        ty = -ry * math.cos(angle)  # SVG y-down
        tx, ty = _normalize(tx, ty)
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
        cx, cy, rx, ry = self._ep(time)
        return f"<ellipse cx='{cx}' cy='{cy}' rx='{rx}' ry='{ry}'{self.styling.svg_style(time)} />"

class Circle(Ellipse):
    """Circle: Ellipse with rx == ry."""
    def __init__(self, r: float = 120, cx: float = ORIGIN[0], cy: float = ORIGIN[1], z: float = 0, creation: float = 0, **styling_kwargs):
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

    get_circumference = get_perimeter
    circumference = get_perimeter
    point_on_circle = point_at_angle

    @classmethod
    def from_diameter(cls, p1, p2, **kwargs):
        """Create a Circle from two diameter endpoints."""
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
        """Create a Circle that circumscribes another object's bounding box."""
        _, _, bw, bh = vobject.bbox(time)
        cx, cy = vobject.center(time)
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
        """Return a Line tangent to the circle at the point closest to (px, py)."""
        cx, cy = self.c.at_time(time)
        # Angle from circle center to the given point
        angle_rad = math.atan2(-(py - cy), px - cx)  # negate dy for SVG coords
        angle_deg = math.degrees(angle_rad)
        return self.tangent_line(angle_deg, length=length, time=time,
                                 creation=creation, **line_kwargs)

    def get_tangent_lines(self, px, py, time=0, length=200, **kwargs):
        """Return the two tangent lines from external point (px, py) to the circle."""
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
        """Return the tangent touch-points from an external point to the circle."""
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
        """Return a Line connecting two points on the circle at the given angles."""
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
        """Create a Circle (circumscribed circle) passing through three points."""
        ux, uy, r = _circumcenter(p1, p2, p3)
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
        """Return intersection points with another Circle as list of (x, y) tuples."""
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

    def circumscribed_polygon(self, n, angle=0, time=0, **kwargs):
        """Return a regular *n*-gon circumscribed around this circle."""
        if n < 3:
            raise ValueError(f"circumscribed_polygon requires n >= 3, got {n}")
        cx, cy = self.c.at_time(time)
        r = self.rx.at_time(time)
        # The inradius of a regular n-gon with circumradius R is R*cos(pi/n).
        # We want the inradius to equal r, so R = r / cos(pi/n).
        circum_r = r / math.cos(math.pi / n)
        return RegularPolygon(n, radius=circum_r, cx=cx, cy=cy, angle=angle, **kwargs)

    def arc_between(self, start_angle, end_angle, time=0, **kwargs):
        """Return an Arc with the same center and radius as this circle."""
        cx, cy = self.c.at_time(time)
        r = self.rx.at_time(time)
        return Arc(cx=cx, cy=cy, r=r,
                   start_angle=start_angle, end_angle=end_angle, **kwargs)

    def get_arc(self, start_angle=0, end_angle=180, time=0, **kwargs):
        """Create an Arc from this circle's center and radius."""
        return self.arc_between(start_angle, end_angle, time=time, **kwargs)

    def diameter_line(self, angle_deg: float = 0, time: float = 0, **kwargs):
        """Return a Line representing the diameter at the given angle."""
        cx, cy = self.c.at_time(time)
        r = self.rx.at_time(time)
        rad = math.radians(angle_deg)
        dx = r * math.cos(rad)
        dy = -r * math.sin(rad)   # negate: SVG y-axis points down
        return Line(x1=cx - dx, y1=cy - dy, x2=cx + dx, y2=cy + dy, **kwargs)

    def segment_area(self, start_angle, end_angle, time=0):
        """Return the area of a circular segment between two angles."""
        r = self.get_radius(time)
        sweep_deg = abs(end_angle - start_angle) % 360
        if sweep_deg == 0:
            return 0.0
        theta = math.radians(sweep_deg)
        # Sector area = 0.5 * r^2 * theta
        # Triangle area = 0.5 * r^2 * sin(theta)
        return abs(0.5 * r * r * (theta - math.sin(theta)))

    def power_of_point(self, px, py, time=0):
        """Return the power of point (px, py) with respect to this circle."""
        cx, cy = self.c.at_time(time)
        r = self.get_radius(time)
        d_sq = (px - cx) ** 2 + (py - cy) ** 2
        return d_sq - r * r

    def chord_length(self, distance, time=0):
        """Return the length of a chord at the given distance from the center."""
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
        """Return the arc length between two angles on the circle."""
        r = self.get_radius(time)
        sweep_deg = abs(end_angle - start_angle) % 360
        if abs(end_angle - start_angle) != 0 and sweep_deg == 0:
            sweep_deg = 360  # full circle
        return r * math.radians(sweep_deg)

    def get_sectors(self, n, **kwargs):
        """Divide the circle into *n* equal sectors (Wedge objects)."""
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
        """Create an annular sector (donut slice) as a Path."""
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
        """Return a regular *n*-sided polygon inscribed in this circle."""
        if angle is not None:
            start_angle = angle
        cx, cy = self.c.at_time(time)
        r = self.rx.at_time(time)
        return RegularPolygon(n, radius=r, cx=cx, cy=cy, angle=start_angle, **kwargs)

    def get_annulus(self, inner_ratio=0.5, time=0, **kwargs):
        """Create an Annulus (ring) using this circle's center and radius."""
        cx, cy = self.c.at_time(time)
        r = self.rx.at_time(time)
        return Annulus(inner_radius=r * inner_ratio, outer_radius=r,
                       cx=cx, cy=cy, **kwargs)

    tangent_line_from_point = get_tangent_lines

    def to_svg(self, time):
        cx, cy = self.c.at_time(time)
        return f"<circle cx='{cx}' cy='{cy}' r='{self.rx.at_time(time)}'{self.styling.svg_style(time)} />"

class Dot(Circle):
    """Small filled circle, no stroke."""
    def __init__(self, r: float = DEFAULT_DOT_RADIUS, cx: float = ORIGIN[0], cy: float = ORIGIN[1], z: float = 0, creation: float = 0, **styling_kwargs):
        super().__init__(r=r, cx=cx, cy=cy, z=z, creation=creation,
                         **({'fill': '#fff', 'fill_opacity': 1, 'stroke_width': 0} | styling_kwargs))

    def __repr__(self):
        cx, cy = self.c.at_time(0)
        return f'Dot(cx={cx:.0f}, cy={cy:.0f})'

class AnnotationDot(Dot):
    """Larger dot with bold stroke for annotation purposes."""
    def __init__(self, r: float = DEFAULT_DOT_RADIUS * 1.3, cx: float = ORIGIN[0], cy: float = ORIGIN[1],
                 z: float = 0, creation: float = 0, **styling_kwargs):
        super().__init__(r=r, cx=cx, cy=cy, z=z, creation=creation,
                         **({'stroke_width': 5, 'stroke': '#fff'} | styling_kwargs))

    def __repr__(self):
        cx, cy = self.c.at_time(0)
        return f'AnnotationDot(cx={cx:.0f}, cy={cy:.0f})'

class Rectangle(VObject):
    def __init__(self, width, height, x: float = ORIGIN[0], y: float = ORIGIN[1], rx: float = 0, ry: float = 0, creation: float = 0, z: float = 0, **styling_kwargs):
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

    def _dims(self, time: float = 0):
        """Return (x, y, w, h) as floats at *time*."""
        return (float(self.x.at_time(time)), float(self.y.at_time(time)),
                float(self.width.at_time(time)), float(self.height.at_time(time)))

    def snap_points(self, time):
        x, y, w, h = self._dims(time)
        return [(x, y), (x+w, y), (x+w, y+h), (x, y+h)]

    def bbox(self, time):
        x, y, w, h = self._dims(time)
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

    def get_vertices(self, time: float = 0):
        """Return the four corners: top-left, top-right, bottom-right, bottom-left."""
        return self.snap_points(time)

    get_corners = get_vertices

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

    diagonal_length = get_diagonal_length

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
        """Return a point (x, y) on the rectangle border at parameter *t*."""
        x, y, w, h = self._dims(time)
        perim = 2 * (w + h)
        if perim < 1e-12:
            return (x, y)
        t = t % 1.0
        dist = t * perim
        # Top edge: left to right
        if dist <= w:
            return (x + dist, y)
        dist -= w
        # Right edge: top to bottom
        if dist <= h:
            return (x + w, y + dist)
        dist -= h
        # Bottom edge: right to left
        if dist <= w:
            return (x + w - dist, y + h)
        dist -= w
        # Left edge: bottom to top
        return (x, y + h - dist)

    def get_grid_lines(self, rows, cols, time=0, **kwargs):
        """Return a VCollection of Lines forming a grid inside this rectangle."""
        from vectormation._base import VCollection
        x, y, w, h = self._dims(time)
        lines = []
        # Horizontal lines
        for i in range(1, rows + 1):
            y_pos = y + h * i / (rows + 1)
            lines.append(Line(x1=x, y1=y_pos, x2=x + w, y2=y_pos, **kwargs))
        # Vertical lines
        for j in range(1, cols + 1):
            x_pos = x + w * j / (cols + 1)
            lines.append(Line(x1=x_pos, y1=y, x2=x_pos, y2=y + h, **kwargs))
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
        """Create a Rectangle from two opposite corner points."""
        lx, rx_ = min(x1, x2), max(x1, x2)
        ty, by = min(y1, y2), max(y1, y2)
        return cls(rx_ - lx, by - ty, x=lx, y=ty, **kwargs)

    @classmethod
    def from_bounding_box(cls, vobject, padding=0, time=0, **kwargs):
        """Create a Rectangle that encloses another object's bounding box."""
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
        """Create a Rectangle that encloses two objects' bounding boxes."""
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

    def _grow_dim(self, attr, amount, start, end, easing):
        attr.move_to(start, end, attr.at_time(start) + amount, easing=easing); return self

    def grow_width(self, amount, start=0, end=1, easing=easings.smooth):
        """Animate increasing width by *amount*."""
        return self._grow_dim(self.width, amount, start, end, easing)

    def grow_height(self, amount, start=0, end=1, easing=easings.smooth):
        """Animate increasing height by *amount*."""
        return self._grow_dim(self.height, amount, start, end, easing)

    def contains_point(self, px, py, time=0):
        """Point-in-rect test."""
        x, y, w, h = self._dims(time)
        return x <= px <= x + w and y <= py <= y + h

    def round_corners(self, radius=10, time=0, **kwargs):
        """Return a RoundedRectangle with the same size/position and the given corner radius."""
        from vectormation.style import _STYLES
        x, y, w, h = self._dims(time)
        style_kw = {}
        for name in _STYLES:
            attr = getattr(self.styling, name)
            # Color.time_func returns a raw tuple; for other attrs use at_time
            val = attr.time_func(time) if isinstance(attr, attributes.Color) else attr.at_time(time)
            style_kw[name] = val
        style_kw.update(kwargs)
        return RoundedRectangle(w, h, x=x, y=y, corner_radius=radius, **style_kw)

    def split(self, direction='horizontal', count=2, time=0, **kwargs):
        """Split this rectangle into *count* equal sub-rectangles."""
        from vectormation._base import VCollection
        if count < 1:
            raise ValueError("split: count must be >= 1")
        rx, ry, rw, rh = self._dims(time)
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
        """Split into *n* equal horizontal strips."""
        return self.split('horizontal', n, time, **kwargs)

    def split_vertical(self, n=2, time=0, **kwargs):
        """Split into *n* equal vertical strips. Alias for ``split('vertical', ...)``."""
        return self.split('vertical', n, time, **kwargs)

    def quadrants(self, time=0, **kwargs):
        """Split this rectangle into 4 equal quadrants (2x2 grid)."""
        return self.subdivide(2, 2, time, **kwargs)

    def inset(self, amount: float, time: float = 0, **kwargs):
        """Return a new Rectangle inset by *amount* pixels on every side."""
        rx, ry, rw, rh = self._dims(time)
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
        """Subdivide this rectangle into a grid of *rows* x *cols* sub-rectangles."""
        from vectormation._base import VCollection
        if rows < 1 or cols < 1:
            raise ValueError(f"subdivide: rows and cols must be >= 1, got rows={rows}, cols={cols}")
        rx, ry, rw, rh = self._dims(time)
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
        """Return a :class:`Path` where each corner is cut at 45 degrees."""
        x, y, w, h = self._dims(time)
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

class Lines(Polygon):
    """Open polyline — a Polygon with closed=False."""
    def __init__(self, *vertices, creation: float = 0, z: float = 0, **styling_kwargs):
        super().__init__(*vertices, closed=False, creation=creation, z=z, **styling_kwargs)

    def __repr__(self):
        return f'Lines({len(self.vertices)} vertices)'

class RegularPolygon(Polygon):
    """Regular n-sided polygon inscribed in a circle of given radius."""
    def __init__(self, n, radius: float = 120, cx: float = ORIGIN[0], cy: float = ORIGIN[1], angle: float = 0, creation: float = 0, z: float = 0, **styling_kwargs):
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
    def __init__(self, n=5, outer_radius=120, inner_radius=None, cx=ORIGIN[0], cy=ORIGIN[1],
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
    def __init__(self, side_length, angle=0, cx=ORIGIN[0], cy=ORIGIN[1], creation: float = 0, z: float = 0, **styling_kwargs):
        self._side_length = side_length
        radius = side_length / math.sqrt(3)
        super().__init__(3, radius=radius, cx=cx, cy=cy, angle=angle + 90,
                         creation=creation, z=z, **styling_kwargs)

    def __repr__(self):
        return f'EquilateralTriangle(side={self._side_length:.0f})'

class RoundedRectangle(Rectangle):
    """Rectangle with rounded corners (default corner_radius=10)."""
    def __init__(self, width, height, x: float = ORIGIN[0], y: float = ORIGIN[1], corner_radius: float = 12, creation: float = 0, z: float = 0, **styling_kwargs):
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

class Square(Rectangle):
    """Square — a Rectangle with equal side length."""
    def __init__(self, side: float = 200, x: float = ORIGIN[0], y: float = ORIGIN[1], creation: float = 0, z: float = 0, **styling_kwargs):
        super().__init__(side, side, x=x - side / 2, y=y - side / 2,
                         creation=creation, z=z, **styling_kwargs)

    def __repr__(self):
        return f'Square({self.width.at_time(0):.0f})'

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
            _bb = _cached_bbox(target)
            self.x.set_onward(creation, lambda t: _bb(t)[0] - buff)
            self.y.set_onward(creation, lambda t: _bb(t)[1] - buff)
            self.width.set_onward(creation, lambda t: _bb(t)[2] + 2*buff)
            self.height.set_onward(creation, lambda t: _bb(t)[3] + 2*buff)

    def __repr__(self):
        return 'SurroundingRectangle()'

class SurroundingCircle(Circle):
    """Circle that surrounds a target object with padding.
    If follow=True (default), tracks the target as it moves."""
    def __init__(self, target, buff=SMALL_BUFF, follow=True,
                 creation: float = 0, z: float = 0, **styling_kwargs):
        _bb = _cached_bbox(target)
        bw, bh = _bb(creation)[2], _bb(creation)[3]
        r = math.hypot(bw, bh) / 2 + buff
        cx, cy = target.center(creation)
        style_kw = {'fill_opacity': 0, 'stroke': '#FFFF00'} | styling_kwargs
        super().__init__(r=r, cx=cx, cy=cy, creation=creation, z=z, **style_kw)
        if follow:
            self.c.set_onward(creation, lambda t: target.center(t))
            _r_func = lambda t: math.hypot(_bb(t)[2], _bb(t)[3]) / 2 + buff
            self.rx.set_onward(creation, _r_func)
            self.ry.set_onward(creation, _r_func)

    def __repr__(self):
        return 'SurroundingCircle()'

# Re-export extended shapes so `from vectormation._shapes import X` still works
from vectormation._shapes_ext import (  # noqa: E402
    Line, DashedLine, Text, CountAnimation, ValueTracker, ComplexValueTracker, DecimalNumber, Integer,
    Trace, Path, Image,
    Arc, Wedge, Annulus, ArcBetweenPoints, AnnularSector,
    CubicBezier, ArcPolygon, ScreenRectangle, BackgroundRectangle, Elbow,
    _TextBlockMixin, Paragraph, BulletedList, NumberedList, FunctionGraph,
    KochSnowflake, SierpinskiTriangle, Spiral,
)
