"""Arrow classes: Arrow, DoubleArrow, CurvedArrow, Brace."""
import math
import re
from vectormation._constants import (
    DEFAULT_ARROW_TIP_LENGTH, DEFAULT_ARROW_TIP_WIDTH,
    SMALL_BUFF, _normalize,
)
from vectormation._base import VObject, VCollection, _norm_dir
from vectormation._shapes import Polygon, Line, Path, Rectangle


def _arrowhead(from_x, from_y, to_x, to_y, tip_length, tip_width, fill, creation, z):
    """Create a triangular arrowhead polygon pointing from (from_x,from_y) toward (to_x,to_y)."""
    dx, dy = to_x - from_x, to_y - from_y
    ux, uy = _normalize(dx, dy)
    px, py = -uy, ux
    bx, by = to_x - ux * tip_length, to_y - uy * tip_length
    hw = tip_width / 2
    return Polygon((to_x, to_y), (bx + px * hw, by + py * hw), (bx - px * hw, by - py * hw),
                   creation=creation, z=z, fill=fill, fill_opacity=1, stroke_width=0)


class Arrow(VCollection):
    """Arrow as a line (shaft) with a triangular arrowhead (and optional second head)."""
    def __init__(self, x1=0, y1=0, x2=100, y2=100, tip_length=DEFAULT_ARROW_TIP_LENGTH, tip_width=DEFAULT_ARROW_TIP_WIDTH,
                 double_ended=False, creation: float = 0, z: float = 0, **styling_kwargs):
        shaft_style = {'stroke': '#fff', 'stroke_width': 5} | styling_kwargs
        tip_fill = shaft_style.get('stroke', '#fff')
        self.shaft = Line(x1=x1, y1=y1, x2=x2, y2=y2, creation=creation, z=z, **shaft_style)
        self.tip = _arrowhead(x1, y1, x2, y2, tip_length, tip_width, tip_fill, creation, z)
        self._tip_length = tip_length
        self._tip_width = tip_width
        self.tail = None
        objects = [self.shaft, self.tip]
        if double_ended:
            self.tail = _arrowhead(x2, y2, x1, y1, tip_length, tip_width, tip_fill, creation, z)
            objects.append(self.tail)
        super().__init__(*objects, creation=creation, z=z)


    def _update_tip_dynamic(self, start):
        """Set up dynamic arrowhead vertices that follow the shaft endpoints."""
        tl = self._tip_length
        hw = self._tip_width / 2
        shaft = self.shaft

        def _tip_geom(t):
            p1 = shaft.p1.at_time(t)
            p2 = shaft.p2.at_time(t)
            dx, dy = p2[0] - p1[0], p2[1] - p1[1]
            ux, uy = _normalize(dx, dy)
            px, py = -uy, ux
            bx, by = p2[0] - ux * tl, p2[1] - uy * tl
            return (p2, (bx + px * hw, by + py * hw), (bx - px * hw, by - py * hw))

        _cache = [None, None]
        def _cached_geom(t):
            if _cache[0] == t:
                return _cache[1]
            result = _tip_geom(t)
            _cache[0], _cache[1] = t, result
            return result

        self.tip.vertices[0].set_onward(start, lambda t: _cached_geom(t)[0])
        self.tip.vertices[1].set_onward(start, lambda t: _cached_geom(t)[1])
        self.tip.vertices[2].set_onward(start, lambda t: _cached_geom(t)[2])

    def set_start(self, x, y, start=0, end=None):
        """Animate the arrow start point."""
        if end is None:
            self.shaft.p1.set_onward(start, lambda t: (x, y))
        else:
            self.shaft.p1.move_to(start, end, (x, y))
        self._update_tip_dynamic(start)
        return self

    def set_end(self, x, y, start=0, end=None):
        """Animate the arrow end point."""
        if end is None:
            self.shaft.p2.set_onward(start, lambda t: (x, y))
        else:
            self.shaft.p2.move_to(start, end, (x, y))
        self._update_tip_dynamic(start)
        return self

    def get_start(self, time: float = 0):
        """Return the start point (x1, y1) of the arrow shaft."""
        return self.shaft.p1.at_time(time)

    def get_end(self, time: float = 0):
        """Return the end point (x2, y2) of the arrow shaft."""
        return self.shaft.p2.at_time(time)


    def get_midpoint(self, time=0):
        """Return the midpoint of the arrow shaft."""
        return self.shaft.get_midpoint(time)

    def get_length(self, time=0):
        """Return the length of the arrow shaft."""
        return self.shaft.get_length(time)

    def set_color(self, color, start=0):
        """Set shaft stroke and tip fill to *color* from *start* onward."""
        self.shaft.styling.stroke.set_onward(start, color)
        self.tip.styling.fill.set_onward(start, color)
        if self.tail is not None:
            self.tail.styling.fill.set_onward(start, color)
        return self

    @classmethod
    def between(cls, obj_a, obj_b, buff=0, **kwargs):
        """Create an Arrow connecting two VObjects."""
        ca = obj_a.get_edge('center', time=0)
        cb = obj_b.get_edge('center', time=0)
        dx = cb[0] - ca[0]
        dy = cb[1] - ca[1]
        # Choose edges based on dominant direction
        if abs(dx) >= abs(dy):
            if dx >= 0:
                start = obj_a.get_edge('right', time=0)
                end = obj_b.get_edge('left', time=0)
            else:
                start = obj_a.get_edge('left', time=0)
                end = obj_b.get_edge('right', time=0)
        else:
            if dy >= 0:
                start = obj_a.get_edge('bottom', time=0)
                end = obj_b.get_edge('top', time=0)
            else:
                start = obj_a.get_edge('top', time=0)
                end = obj_b.get_edge('bottom', time=0)
        # Apply buff
        if buff > 0:
            length = math.hypot(end[0] - start[0], end[1] - start[1])
            if length > 2 * buff:
                ux, uy = _normalize(end[0] - start[0], end[1] - start[1])
                start = (start[0] + ux * buff, start[1] + uy * buff)
                end = (end[0] - ux * buff, end[1] - uy * buff)
        return cls(x1=start[0], y1=start[1], x2=end[0], y2=end[1], **kwargs)

    def __repr__(self):
        s, e = self.get_start(), self.get_end()
        return f'Arrow(({s[0]:.0f},{s[1]:.0f})->({e[0]:.0f},{e[1]:.0f}))'


class DoubleArrow(Arrow):
    """Double-ended arrow (shorthand for Arrow with double_ended=True)."""
    def __init__(self, x1=0, y1=0, x2=100, y2=100, tip_length=DEFAULT_ARROW_TIP_LENGTH, tip_width=DEFAULT_ARROW_TIP_WIDTH,
                 creation: float = 0, z: float = 0, **styling_kwargs):
        super().__init__(x1=x1, y1=y1, x2=x2, y2=y2, tip_length=tip_length,
                         tip_width=tip_width, double_ended=True,
                         creation=creation, z=z, **styling_kwargs)

    def __repr__(self):
        return f'DoubleArrow()'


class CurvedArrow(VCollection):
    """Arrow with a curved (quadratic bezier) shaft and a triangular tip."""
    def __init__(self, x1=0, y1=0, x2=100, y2=100, angle=0.4,
                 tip_length=DEFAULT_ARROW_TIP_LENGTH, tip_width=DEFAULT_ARROW_TIP_WIDTH, creation: float = 0, z: float = 0, **styling_kwargs):
        shaft_style = {'stroke': '#fff', 'stroke_width': 5, 'fill_opacity': 0} | styling_kwargs
        tip_fill = shaft_style.get('stroke', '#fff')
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = x2 - x1, y2 - y1
        cx, cy = mx - dy * angle, my + dx * angle
        shaft = Path(f'M{x1},{y1}Q{cx},{cy} {x2},{y2}',
                     creation=creation, z=z, **shaft_style)
        tip = _arrowhead(cx, cy, x2, y2, tip_length, tip_width, tip_fill, creation, z)
        super().__init__(shaft, tip, creation=creation, z=z)

    def __repr__(self):
        return f'CurvedArrow()'


def _transform_rel_svg_path(raw, m00, m01, m10, m11, tx, ty):
    """Parse a relative SVG path and convert to absolute coords with an affine transform."""
    tokens = re.findall(r'[mcvhsz]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?', raw)

    def xf(x, y):
        return m00 * x + m01 * y + tx, m10 * x + m11 * y + ty

    parts: list[str] = []
    cx = cy = 0.0
    prev_cp2: tuple[float, float] | None = None
    i = 0

    while i < len(tokens):
        cmd = tokens[i]; i += 1

        if cmd == 'm':
            cx += float(tokens[i]); cy += float(tokens[i + 1]); i += 2
            ax, ay = xf(cx, cy)
            parts.append(f'M{ax:.4f},{ay:.4f}')
            prev_cp2 = None

        elif cmd == 'c':
            while i < len(tokens) and tokens[i] not in 'mcvhsz':
                d1x, d1y = float(tokens[i]), float(tokens[i + 1])
                d2x, d2y = float(tokens[i + 2]), float(tokens[i + 3])
                dex, dey = float(tokens[i + 4]), float(tokens[i + 5])
                i += 6
                cp1 = (cx + d1x, cy + d1y)
                cp2 = (cx + d2x, cy + d2y)
                end = (cx + dex, cy + dey)
                a1x, a1y = xf(*cp1)
                a2x, a2y = xf(*cp2)
                aex, aey = xf(*end)
                parts.append(f'C{a1x:.4f},{a1y:.4f} {a2x:.4f},{a2y:.4f} {aex:.4f},{aey:.4f}')
                prev_cp2 = cp2
                cx, cy = end

        elif cmd == 'v':
            cy += float(tokens[i]); i += 1
            ax, ay = xf(cx, cy)
            parts.append(f'L{ax:.4f},{ay:.4f}')
            prev_cp2 = None

        elif cmd == 'h':
            cx += float(tokens[i]); i += 1
            ax, ay = xf(cx, cy)
            parts.append(f'L{ax:.4f},{ay:.4f}')
            prev_cp2 = None

        elif cmd == 's':
            while i < len(tokens) and tokens[i] not in 'mcvhsz':
                d2x, d2y = float(tokens[i]), float(tokens[i + 1])
                dex, dey = float(tokens[i + 2]), float(tokens[i + 3])
                i += 4
                cp1 = (2 * cx - prev_cp2[0], 2 * cy - prev_cp2[1]) if prev_cp2 else (cx, cy)
                cp2 = (cx + d2x, cy + d2y)
                end = (cx + dex, cy + dey)
                a1x, a1y = xf(*cp1)
                a2x, a2y = xf(*cp2)
                aex, aey = xf(*end)
                parts.append(f'C{a1x:.4f},{a1y:.4f} {a2x:.4f},{a2y:.4f} {aex:.4f},{aey:.4f}')
                prev_cp2 = cp2
                cx, cy = end

        elif cmd == 'z':
            parts.append('Z')
            prev_cp2 = None

    return ''.join(parts)


# Curly-brace SVG path template (derived from LaTeX).
# {0} = linear_section_length, {1} = -linear_section_length.
# At {0}=0 the brace is ~0.906 wide x ~0.167 tall, tip pointing +Y.
_BRACE_PATH_TEMPLATE = (
    "m0.01216 0c-0.01152 0-0.01216 6.103e-4 -0.01216 0.01311v0.007762"
    "c0.06776 0.122 0.1799 0.1455 0.2307 0.1455h{0}"
    "c0.03046 3.899e-4 0.07964 0.00449 0.1246 0.02636 "
    "0.0537 0.02695 0.07418 0.05816 0.08648 0.07769 "
    "0.001562 0.002538 0.004539 0.002563 0.01098 0.002563 "
    "0.006444-2e-8 0.009421-2.47e-5 0.01098-0.002563 "
    "0.0123-0.01953 0.03278-0.05074 0.08648-0.07769 "
    "0.04491-0.02187 0.09409-0.02597 0.1246-0.02636h{0}"
    "c0.05077 0 0.1629-0.02346 0.2307-0.1455v-0.007762"
    "c-1.78e-6 -0.0125-6.365e-4 -0.01311-0.01216-0.01311"
    "-0.006444-3.919e-8 -0.009348 2.448e-5 -0.01091 0.002563"
    "-0.0123 0.01953-0.03278 0.05074-0.08648 0.07769"
    "-0.04491 0.02187-0.09416 0.02597-0.1246 0.02636h{1}"
    "c-0.04786 0-0.1502 0.02094-0.2185 0.1256"
    "-0.06833-0.1046-0.1706-0.1256-0.2185-0.1256h{1}"
    "c-0.03046-3.899e-4 -0.07972-0.004491-0.1246-0.02636"
    "-0.0537-0.02695-0.07418-0.05816-0.08648-0.07769"
    "-0.001562-0.002538-0.004467-0.002563-0.01091-0.002563z"
)
_BRACE_MIN_WIDTH = 0.90552
_BRACE_HEIGHT = 0.167


class Brace(VCollection):
    """Curly brace annotation pointing at a target object."""
    def __init__(self, target, direction='down', label=None, buff=SMALL_BUFF,
                 depth=18, creation: float = 0, z: float = 0, **styling_kwargs):
        direction = _norm_dir(direction, 'down')
        bx, by, bw, bh = target.bbox(creation)

        if direction in ('down', 'up'):
            span = bw
        elif direction in ('left', 'right'):
            span = bh
        else:
            raise ValueError(f"direction must be 'down', 'up', 'left', or 'right', got '{direction}'")

        # Compute linear section length so curved parts have the right depth
        scale = depth / _BRACE_HEIGHT
        linear_section = max(0, (span / scale - _BRACE_MIN_WIDTH) / 2)
        raw = _BRACE_PATH_TEMPLATE.format(linear_section, -linear_section)

        # Affine transform: (x,y) in template -> pixel coords
        # Template: horizontal, tip pointing +Y (down in SVG)
        if direction == 'down':
            m00, m01, tx = scale, 0, bx
            m10, m11, ty = 0, scale, by + bh + buff
        elif direction == 'up':
            m00, m01, tx = -scale, 0, bx + bw
            m10, m11, ty = 0, -scale, by - buff
        elif direction == 'right':
            m00, m01, tx = 0, scale, bx + bw + buff
            m10, m11, ty = scale, 0, by
        else:  # left
            m00, m01, tx = 0, -scale, bx - buff
            m10, m11, ty = scale, 0, by

        d = _transform_rel_svg_path(raw, m00, m01, m10, m11, tx, ty)
        brace_style = {'fill': '#fff', 'fill_opacity': 1, 'stroke_width': 0} | styling_kwargs
        brace_path = Path(d, creation=creation, z=z, **brace_style)

        objects: list = [brace_path]

        # Optional label
        if label is not None:
            from vectormation._composites import TexObject
            label_gap = 30
            label_obj = TexObject(label, font_size=30, creation=creation, z=z,
                                  fill='#fff', stroke_width=0)
            _, _, lw, lh = label_obj.bbox(creation)
            tcx, tcy = bx + bw / 2, by + bh / 2
            arm = buff + depth + label_gap
            if direction == 'down':
                lx, ly = tcx, by + bh + arm + lh / 2
            elif direction == 'up':
                lx, ly = tcx, by - arm - lh / 2
            elif direction == 'right':
                lx, ly = bx + bw + arm + lw / 2, tcy
            else:  # left
                lx, ly = bx - arm - lw / 2, tcy
            label_obj.center_to_pos(posx=lx, posy=ly)
            objects.append(label_obj)

        super().__init__(*objects, creation=creation, z=z)
        self._direction = direction

    def __repr__(self):
        return f'Brace(direction={self._direction!r})'

    @classmethod
    def for_range(cls, axes, axis, start_val, end_val, direction=None,
                  label=None, **kwargs):
        """Create a Brace spanning a range on an Axes object."""
        creation = kwargs.pop('creation', 0)
        if axis == 'x':
            sx1 = axes._math_to_svg_x(start_val, creation)
            sx2 = axes._math_to_svg_x(end_val, creation)
            # y-position: use the x-axis line (y_min mapped to SVG)
            sy = axes._math_to_svg_y(axes.y_min.at_time(creation), creation)
            x_left = min(sx1, sx2)
            width = abs(sx2 - sx1)
            # Create a thin target rectangle along the x-axis
            target = Rectangle(width, 1, x=x_left, y=sy - 0.5,
                               creation=creation)
            if direction is None:
                direction = 'down'
        elif axis == 'y':
            sy1 = axes._math_to_svg_y(start_val, creation)
            sy2 = axes._math_to_svg_y(end_val, creation)
            # x-position: use the y-axis line (x_min mapped to SVG)
            sx = axes._math_to_svg_x(axes.x_min.at_time(creation), creation)
            y_top = min(sy1, sy2)
            height = abs(sy2 - sy1)
            # Create a thin target rectangle along the y-axis
            target = Rectangle(1, height, x=sx - 0.5, y=y_top,
                               creation=creation)
            if direction is None:
                direction = 'left'
        else:
            raise ValueError(f"axis must be 'x' or 'y', got {axis!r}")

        return cls(target, direction=direction, label=label,
                   creation=creation, **kwargs)


class Vector(Arrow):
    """Arrow originating from a point (default: origin), for use in coordinate systems."""
    def __init__(self, x=100, y=0, origin_x=960, origin_y=540, creation: float = 0, z: float = 0, **kwargs):
        super().__init__(x1=origin_x, y1=origin_y, x2=origin_x + x, y2=origin_y + y,
                         creation=creation, z=z, **kwargs)
        self._vx, self._vy = x, y

    def __repr__(self):
        return f'Vector({self._vx:.0f}, {self._vy:.0f})'

    def get_vector(self, time=0):
        """Return the vector components (dx, dy) from start to end."""
        s = self.get_start(time)
        e = self.get_end(time)
        return (e[0] - s[0], e[1] - s[1])

    def coordinate_label(self, integer_labels=True, creation=0, **kwargs):
        """Create a column-matrix label showing the vector's endpoint coordinates."""
        from vectormation._composites import Matrix
        vx, vy = self.get_vector(creation)
        if integer_labels:
            vx, vy = round(vx), round(vy)
        m = Matrix([[vx], [vy]], creation=creation, **kwargs)
        ex, ey = self.get_end(creation)
        m.center_to_pos(posx=ex + 40, posy=ey, start=creation)
        return m
