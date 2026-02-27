"""SVG utilities, boolean operations, and geometric annotations."""
import math
import re

import vectormation.easings as easings
import vectormation.attributes as attributes
import vectormation.style as style
from vectormation._constants import (
    CANVAS_WIDTH, CANVAS_HEIGHT, SMALL_BUFF,
    TEXT_Y_OFFSET, _normalize, _get_arrow,
)
from vectormation._base import VObject, VCollection, _norm_dir
from vectormation._shapes import (
    Polygon, Circle, Rectangle, Line, Lines, Text, Path, Arc, Ellipse,
)


def _get_brace():
    from vectormation._arrows import Brace
    return Brace


# ---------------------------------------------------------------------------
# SVG filter / clip definitions
# ---------------------------------------------------------------------------

class ClipPath:
    """SVG clip path definition containing one or more shape objects."""
    def __init__(self, *objects):
        self.id = f'clip{id(self)}'
        self.objects = list(objects)

    def __repr__(self):
        return 'ClipPath()'

    def to_svg_def(self, time):
        paths = ''.join(obj.to_svg(time) for obj in self.objects)
        return f"<clipPath id='{self.id}'>{paths}</clipPath>"

    def clip_ref(self):
        return f'url(#{self.id})'


class BlurFilter:
    """SVG Gaussian blur filter definition. Register with canvas.add_def().
    Apply to objects via styling: obj.styling.filter = 'url(#filter_id)'."""
    def __init__(self, std_deviation=4):
        self.id = f'blur{id(self)}'
        self.std_deviation = std_deviation

    def __repr__(self):
        return 'BlurFilter()'

    def to_svg_def(self, time=None):
        return (f"<filter id='{self.id}'>"
                f"<feGaussianBlur stdDeviation='{self.std_deviation}'/>"
                f"</filter>")

    def filter_ref(self):
        return f'url(#{self.id})'


class DropShadowFilter:
    """SVG drop shadow filter definition. Register with canvas.add_def()."""
    def __init__(self, dx=4, dy=4, std_deviation=4, color='#000', opacity=0.5):
        self.id = f'shadow{id(self)}'
        self.dx, self.dy = dx, dy
        self.std_deviation = std_deviation
        self.color, self.opacity = color, opacity

    def __repr__(self):
        return 'DropShadowFilter()'

    def to_svg_def(self, time=None):
        return (f"<filter id='{self.id}'>"
                f"<feDropShadow dx='{self.dx}' dy='{self.dy}' "
                f"stdDeviation='{self.std_deviation}' "
                f"flood-color='{self.color}' flood-opacity='{self.opacity}'/>"
                f"</filter>")

    def filter_ref(self):
        return f'url(#{self.id})'


# ---------------------------------------------------------------------------
# Geometric annotations
# ---------------------------------------------------------------------------

class Angle(VCollection):
    """Draw an angle arc between two lines meeting at a vertex, with optional label.

    vertex, p1, p2: (x, y) tuples or Coor objects (for time-varying angles).
    radius: arc radius in pixels.
    label: TeX string (e.g. r'$\\theta$'), True for degree value, or None for no label.
    label_radius: distance from vertex to label center (default: radius * 1.75).
    """
    def __init__(self, vertex, p1, p2, radius=36, label=None, label_radius=None,
                 label_font_size=36, creation: float = 0, z: float = 0, **styling_kwargs):
        self.vertex = vertex if isinstance(vertex, attributes.Coor) else attributes.Coor(creation, vertex)
        self.p1 = p1 if isinstance(p1, attributes.Coor) else attributes.Coor(creation, p1)
        self.p2 = p2 if isinstance(p2, attributes.Coor) else attributes.Coor(creation, p2)

        vx, vy = self.vertex.at_time(creation)
        p1x, p1y = self.p1.at_time(creation)
        p2x, p2y = self.p2.at_time(creation)
        a1, a2 = self._angles_from_points(vx, vy, p1x, p1y, p2x, p2y)

        arc_kw = {'stroke': '#FFFF00', 'fill_opacity': 0} | styling_kwargs
        self.arc = Arc(cx=vx, cy=vy, r=radius, start_angle=a1, end_angle=a2,
                       creation=creation, z=z, **arc_kw)
        self.arc.cx.set_onward(creation, lambda t: self.vertex.at_time(t)[0])
        self.arc.cy.set_onward(creation, lambda t: self.vertex.at_time(t)[1])
        self.arc.start_angle.set_onward(creation, lambda t: self._compute_angles(t)[0])
        self.arc.end_angle.set_onward(creation, lambda t: self._compute_angles(t)[1])

        objects: list = [self.arc]

        if label is not None:
            lr = label_radius if label_radius is not None else radius * 1.75
            label_color = arc_kw.get('stroke', '#FFFF00')

            if label is True:
                # Dynamic degree label using Text (updates every frame)
                angle_deg = (a2 - a1) % 360
                if angle_deg > 180:
                    angle_deg = 360 - angle_deg
                mid_a = math.radians((a1 + a2) / 2)
                init_lx = vx + lr * math.cos(mid_a)
                init_ly = vy - lr * math.sin(mid_a)
                self._label_obj = Text(
                    text=f'{round(angle_deg)}\u00b0', font_size=label_font_size,
                    x=init_lx, y=init_ly, text_anchor='middle',
                    creation=creation, z=z, fill=label_color, stroke_width=0)

                def _deg_text(t):
                    a1t, a2t = self._compute_angles(t)
                    deg = (a2t - a1t) % 360
                    if deg > 180:
                        deg = 360 - deg
                    return f'{round(deg)}\u00b0'

                self._label_obj.text.set_onward(creation, _deg_text)
                self._label_obj.x.set_onward(creation, lambda t, _lr=lr: (
                    self.vertex.at_time(t)[0] + _lr * math.cos(
                        math.radians(sum(self._compute_angles(t)) / 2))))
                self._label_obj.y.set_onward(creation, lambda t, _lr=lr: (
                    self.vertex.at_time(t)[1] - _lr * math.sin(
                        math.radians(sum(self._compute_angles(t)) / 2))
                    + label_font_size * TEXT_Y_OFFSET))
            else:
                # Static TeX label (e.g. theta symbol)
                from vectormation._composites import TexObject
                label_text = label if '$' in label else f'${label}$'
                mid_a = math.radians((a1 + a2) / 2)
                init_lx = vx + lr * math.cos(mid_a)
                init_ly = vy - lr * math.sin(mid_a)
                self._label_obj = TexObject(
                    label_text, font_size=label_font_size,
                    creation=creation, z=z, fill=label_color, stroke_width=0)
                self._label_obj.center_to_pos(posx=init_lx, posy=init_ly)

                base_x = self._label_obj.x.at_time(creation)
                base_y = self._label_obj.y.at_time(creation)

                def _label_x(t, _lr=lr, _bx=base_x, _ilx=init_lx):
                    a1t, a2t = self._compute_angles(t)
                    mid = math.radians((a1t + a2t) / 2)
                    return _bx + (self.vertex.at_time(t)[0] + _lr * math.cos(mid)) - _ilx

                def _label_y(t, _lr=lr, _by=base_y, _ily=init_ly):
                    a1t, a2t = self._compute_angles(t)
                    mid = math.radians((a1t + a2t) / 2)
                    return _by + (self.vertex.at_time(t)[1] - _lr * math.sin(mid)) - _ily

                self._label_obj.x.set_onward(creation, _label_x)
                self._label_obj.y.set_onward(creation, _label_y)

            objects.append(self._label_obj)

        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return 'Angle()'

    @property
    def start_angle(self):
        return self.arc.start_angle

    @property
    def end_angle(self):
        return self.arc.end_angle

    @property
    def r(self):
        return self.arc.r

    def path(self, time):
        return self.arc.path(time)

    @staticmethod
    def _angles_from_points(vx, vy, p1x, p1y, p2x, p2y):
        a1 = math.degrees(math.atan2(-(p1y - vy), p1x - vx))
        a2 = math.degrees(math.atan2(-(p2y - vy), p2x - vx))
        if (a2 - a1) % 360 > 180:
            a1, a2 = a2, a1
        return a1, a2

    def _compute_angles(self, t):
        vx, vy = self.vertex.at_time(t)
        p1x, p1y = self.p1.at_time(t)
        p2x, p2y = self.p2.at_time(t)
        return self._angles_from_points(vx, vy, p1x, p1y, p2x, p2y)

    def set_radius(self, new_radius, start=0, end=None, easing=easings.smooth):
        """Animate the angle arc radius to new_radius."""
        if end is None:
            self.arc.r.set_onward(start, new_radius)
        else:
            self.arc.r.move_to(start, end, new_radius, easing=easing)
        return self

    def shift(self, dx=0, dy=0, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Shift the angle by moving vertex, p1, p2 (label follows automatically)."""
        for c in [self.vertex, self.p1, self.p2]:
            if end is None:
                c.add_onward(start, (dx, dy))
            else:
                s, e = start, end
                d = max(e - s, 1e-9)
                c.add_onward(s, lambda t, _s=s, _d=d: (dx * easing((t-_s)/_d), dy * easing((t-_s)/_d)), last_change=e)
        return self


class RightAngle(VCollection):
    """Right angle indicator (small square) at a vertex between two perpendicular lines."""
    def __init__(self, vertex, p1, p2, size=18, creation: float = 0, z: float = 0, **styling_kwargs):
        vx, vy = vertex
        d1x, d1y = p1[0] - vx, p1[1] - vy
        d2x, d2y = p2[0] - vx, p2[1] - vy
        len1 = math.hypot(d1x, d1y) or 1
        len2 = math.hypot(d2x, d2y) or 1
        u1x, u1y = d1x / len1 * size, d1y / len1 * size
        u2x, u2y = d2x / len2 * size, d2y / len2 * size
        style_kw = {'stroke': '#FFFF00', 'stroke_width': 4, 'fill_opacity': 0} | styling_kwargs
        corner = Lines(
            (vx + u1x, vy + u1y),
            (vx + u1x + u2x, vy + u1y + u2y),
            (vx + u2x, vy + u2y),
            creation=creation, z=z, **style_kw
        )
        super().__init__(corner, creation=creation, z=z)

    def __repr__(self):
        return 'RightAngle()'


class Cross(VCollection):
    """X mark shape, useful for indicating errors or crossing out."""
    def __init__(self, size=36, cx=960, cy=540, creation: float = 0, z: float = 0, **styling_kwargs):
        style_kw = {'stroke': '#FC6255', 'stroke_width': 4} | styling_kwargs
        half = size / 2
        l1 = Line(x1=cx - half, y1=cy - half, x2=cx + half, y2=cy + half,
                  creation=creation, z=z, **style_kw)
        l2 = Line(x1=cx - half, y1=cy + half, x2=cx + half, y2=cy - half,
                  creation=creation, z=z, **style_kw)
        super().__init__(l1, l2, creation=creation, z=z)

    def __repr__(self):
        return 'Cross()'


# ---------------------------------------------------------------------------
# SVG parsing
# ---------------------------------------------------------------------------

def _parse_svg_points(points_str):
    """Parse an SVG points attribute into a list of (x, y) tuples."""
    coords = [float(t) for t in re.split(r'[\s,]+', points_str.strip()) if t]
    return [(coords[i], coords[i+1]) for i in range(0, len(coords) - 1, 2)]


def _parse_inline_style(style_str):
    """Parse CSS inline style string into a dict of presentation attributes."""
    return {k.strip(): v.strip() for part in style_str.split(';')
            if ':' in part for k, v in [part.split(':', 1)]}


def from_svg(element, **styles):
    """Convert a bs4 SVG element to a VObject.
    Handles both presentation attributes and inline CSS style attributes."""
    tag = element.name
    inline = _parse_inline_style(element.get('style', ''))
    g = lambda k, d=0: float(element.get(k, inline.get(k, d)))

    def _merged_attrs(*exclude):
        """Merge inline styles with element attrs, excluding given keys and 'style'."""
        skip = set(exclude) | {'style'}
        attrs = {k: v for k, v in (inline | dict(element.attrs)).items() if k not in skip}
        for k in ('x', 'y'):
            if k in attrs: attrs[k] = float(attrs[k])
        return styles | attrs

    # Parse SVG transform attribute (translate only for now)
    transform_str = element.get('transform', '')
    tx, ty = 0.0, 0.0
    if transform_str:
        m = re.search(r'translate\(\s*([-\d.]+)[\s,]+([-\d.]+)\s*\)', transform_str)
        if m:
            tx, ty = float(m.group(1)), float(m.group(2))

    if tag == 'path':
        obj = Path(element['d'], **_merged_attrs('d', 'transform'))
        if tx or ty:
            obj.shift(dx=tx, dy=ty, start=0)
        return obj
    elif tag == 'rect':
        rect_x, rect_y = g('x', 0) + tx, g('y', 0) + ty
        return Rectangle(width=g('width'), height=g('height'), x=rect_x, y=rect_y,
                         **_merged_attrs('width', 'height', 'x', 'y', 'transform'))
    elif tag == 'circle':
        return Circle(r=g('r', 100), cx=g('cx') + tx, cy=g('cy') + ty,
                      **_merged_attrs('r', 'cx', 'cy', 'transform'))
    elif tag == 'ellipse':
        return Ellipse(rx=g('rx', 100), ry=g('ry', 50), cx=g('cx') + tx, cy=g('cy') + ty,
                       **_merged_attrs('rx', 'ry', 'cx', 'cy', 'transform'))
    elif tag == 'line':
        return Line(x1=g('x1') + tx, y1=g('y1') + ty, x2=g('x2') + tx, y2=g('y2') + ty,
                    **_merged_attrs('x1', 'y1', 'x2', 'y2', 'transform'))
    elif tag == 'polygon':
        pts = [(x + tx, y + ty) for x, y in _parse_svg_points(element.get('points', ''))]
        return Polygon(*pts, **_merged_attrs('points', 'transform'))
    elif tag == 'polyline':
        pts = [(x + tx, y + ty) for x, y in _parse_svg_points(element.get('points', ''))]
        return Lines(*pts, **_merged_attrs('points', 'transform'))
    elif tag == 'text':
        content = element.get_text(strip=True)
        kw = _merged_attrs('x', 'y', 'font-size', 'text-anchor', 'transform')
        fs = float(element.get('font-size', inline.get('font-size', 48)))
        anchor = element.get('text-anchor', inline.get('text-anchor', None))
        return Text(text=content, x=g('x', CANVAS_WIDTH // 2) + tx,
                    y=g('y', CANVAS_HEIGHT // 2) + ty,
                    font_size=fs, text_anchor=anchor, **kw)
    elif tag == 'g':
        children = []
        group_styles = _merged_attrs()
        for child in element.children:
            if getattr(child, 'name', None) in _SVG_SHAPE_TAGS:
                try:
                    children.append(from_svg(child, **group_styles))
                except (KeyError, NotImplementedError, ValueError):
                    continue
        return VCollection(*children)
    else:
        raise NotImplementedError(f'Type "{tag}" has no from_svg implemented')


_SVG_SHAPE_TAGS = frozenset({'path', 'rect', 'circle', 'ellipse', 'line', 'polygon', 'polyline', 'text', 'g'})

def from_svg_file(filepath, creation=0, z=0, **styles):
    """Load an SVG file and return a VCollection of all parseable elements."""
    from bs4 import BeautifulSoup
    with open(filepath, 'r') as f:
        soup = BeautifulSoup(f.read(), features='xml')
    svg = soup.find('svg')
    if svg is None:
        raise ValueError(f'No <svg> element found in {filepath}')
    objects = []
    for elem in svg.descendants:
        tag = getattr(elem, 'name', None)
        if tag not in _SVG_SHAPE_TAGS:
            continue
        # Skip elements inside a <g> — they are handled by the <g> recursion
        if getattr(elem.parent, 'name', None) == 'g':
            continue
        try:
            obj = from_svg(elem, **styles)
            obj.show.set_onward(creation, True)
            obj.z = attributes.Real(creation, z)
            objects.append(obj)
        except (KeyError, NotImplementedError, ValueError):
            continue
    return VCollection(*objects, creation=creation, z=z)


# ---------------------------------------------------------------------------
# ZoomedInset
# ---------------------------------------------------------------------------

class ZoomedInset(VObject):
    """Magnified inset view of a region on the canvas.

    Shows a source rectangle (frame) on the canvas and a magnified display
    rectangle elsewhere. Objects within the source region appear enlarged in
    the display. The frame and display can be animated independently.

    source: (x, y, w, h) — the region to zoom into (canvas coordinates).
    display: (x, y, w, h) — where to draw the magnified view.
    """
    def __init__(self, canvas, source, display, creation: float = 0, z=999,
                 frame_color='#FFFF00', display_color='#FFFF00', frame_width=2):
        super().__init__(creation=creation, z=z)
        self.canvas = canvas
        self.src_x = attributes.Real(creation, source[0])
        self.src_y = attributes.Real(creation, source[1])
        self.src_w = attributes.Real(creation, source[2])
        self.src_h = attributes.Real(creation, source[3])
        self.dst_x = attributes.Real(creation, display[0])
        self.dst_y = attributes.Real(creation, display[1])
        self.dst_w = attributes.Real(creation, display[2])
        self.dst_h = attributes.Real(creation, display[3])
        self.frame_color = frame_color
        self.display_color = display_color
        self.frame_width = frame_width
        self.styling = style.Styling({}, creation=creation)

    def __repr__(self):
        return 'ZoomedInset()'

    def _extra_attrs(self):
        return [self.src_x, self.src_y, self.src_w, self.src_h,
                self.dst_x, self.dst_y, self.dst_w, self.dst_h]

    def _shift_reals(self):
        return [(self.src_x, self.src_y), (self.dst_x, self.dst_y)]

    def to_svg(self, time):
        sx, sy = self.src_x.at_time(time), self.src_y.at_time(time)
        sw, sh = self.src_w.at_time(time), self.src_h.at_time(time)
        dx, dy = self.dst_x.at_time(time), self.dst_y.at_time(time)
        dw, dh = self.dst_w.at_time(time), self.dst_h.at_time(time)
        fc, dc = self.frame_color, self.display_color
        fw = self.frame_width

        # Collect SVG of all visible canvas objects (except self)
        inner = []
        visible = [(obj.z.at_time(time), obj)
                    for obj in self.canvas.objects.values()
                    if obj.show.at_time(time) and obj is not self]
        for _, obj in sorted(visible, key=lambda x: x[0]):
            inner.append(obj.to_svg(time))
        content = '\n'.join(inner)

        # Source frame rectangle
        frame = (f"<rect x='{sx}' y='{sy}' width='{sw}' height='{sh}' "
                 f"fill='none' stroke='{fc}' stroke-width='{fw}'/>")
        # Nested SVG with clipped viewBox showing magnified content
        inset = (f"<svg x='{dx}' y='{dy}' width='{dw}' height='{dh}' "
                 f"viewBox='{sx} {sy} {sw} {sh}'>\n{content}\n</svg>")
        # Display border
        border = (f"<rect x='{dx}' y='{dy}' width='{dw}' height='{dh}' "
                  f"fill='none' stroke='{dc}' stroke-width='{fw}'/>")
        body = f"{frame}\n{inset}\n{border}"
        st = self.styling.svg_style(time)
        if st:
            return f"<g{st}>{body}</g>"
        return body

    def path(self, time):
        return ''

    def bbox(self, time):
        dx, dy = self.dst_x.at_time(time), self.dst_y.at_time(time)
        dw, dh = self.dst_w.at_time(time), self.dst_h.at_time(time)
        return (dx, dy, dw, dh)

    def move_source(self, x, y, start, end=None, easing=easings.smooth):
        """Animate the source region position."""
        if end is None:
            self.src_x.set_onward(start, x)
            self.src_y.set_onward(start, y)
        else:
            self.src_x.move_to(start, end, x, easing=easing)
            self.src_y.move_to(start, end, y, easing=easing)
        return self


# ---------------------------------------------------------------------------
# Boolean shape operations
# ---------------------------------------------------------------------------

class _BooleanOp(VObject):
    """Base for boolean shape operations.

    Rendering uses SVG clip-paths so that each operation shows the correct
    filled region *and* strokes only along the true boundary.  All styling
    transforms (scale, rotate, …) are applied on a wrapping ``<g>`` so that
    clip regions transform together with the geometry.
    """
    _fill_rule = None  # override in subclass

    def __init__(self, shape_a, shape_b, creation: float = 0, z: float = 0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        self._a, self._b = shape_a, shape_b
        self.styling = style.Styling(styling_kwargs, creation=creation,
                                     fill_opacity=0.7, stroke='#fff')
        self._off_x = attributes.Real(creation, 0)
        self._off_y = attributes.Real(creation, 0)
        self._uid = id(self)

    def __repr__(self):
        return f'{type(self).__name__}()'

    def _extra_attrs(self):
        return [self._off_x, self._off_y]

    def _shift_reals(self):
        return [(self._off_x, self._off_y)]

    def path(self, time):
        return self._a.path(time) + self._b.path(time)

    # -- SVG helpers --------------------------------------------------

    def _wrap_group(self, inner, time):
        """Wrap *inner* in ``<g>`` with offset + styling transforms."""
        parts = ''
        tx, ty = self._off_x.at_time(time), self._off_y.at_time(time)
        if tx != 0 or ty != 0:
            parts += f'translate({tx},{ty})'
        st = self.styling.transform_style(time)
        if st:
            if parts:
                parts += ' '
            parts += st.lstrip()
        if parts:
            return f"<g transform='{parts}'>{inner}</g>"
        return inner

    def _fill_attrs(self, time):
        """Fill/opacity presentation attributes (no stroke, no transform)."""
        result = ''
        for name, svgname in style._STYLE_PAIRS:
            if name.startswith('stroke') or name == 'clip_path':
                continue
            val = getattr(self.styling, name).at_time(time)
            rd = style._RENDERED_DEFAULTS[name]
            if rd is None or val != rd:
                result += f" {svgname}='{val}'"
        return result

    def _stroke_attrs(self, time):
        """Stroke presentation attributes with ``fill='none'``."""
        result = " fill='none'"
        for name, svgname in style._STYLE_PAIRS:
            if not name.startswith('stroke'):
                continue
            val = getattr(self.styling, name).at_time(time)
            rd = style._RENDERED_DEFAULTS[name]
            if rd is None or val != rd:
                result += f" {svgname}='{val}'"
        return result

    def _all_attrs(self, time):
        """All presentation attributes (no transform)."""
        result = ''
        for name, svgname in style._STYLE_PAIRS:
            val = getattr(self.styling, name).at_time(time)
            rd = style._RENDERED_DEFAULTS[name]
            if rd is None or val != rd:
                result += f" {svgname}='{val}'"
        return result

    @staticmethod
    def _clip_def(path_d, cid):
        """``<clipPath>`` that clips *to* a shape."""
        return f"<clipPath id='{cid}'><path d='{path_d}'/></clipPath>"

    @staticmethod
    def _clip_inv(path_d, cid):
        """``<clipPath>`` that clips *outside* a shape (inverse clip)."""
        return (f"<clipPath id='{cid}'>"
                f"<path d='M-9999,-9999 H99999 V99999 H-9999Z{path_d}'"
                f" clip-rule='evenodd'/></clipPath>")

    # -- default to_svg / bbox (used by Exclusion) --------------------

    def to_svg(self, time):
        fr = f" fill-rule='{self._fill_rule}'" if self._fill_rule else ''
        inner = f"<path d='{self.path(time)}'{fr}{self._all_attrs(time)}/>"
        return self._wrap_group(inner, time)

    def bbox(self, time):
        ax, ay, aw, ah = self._a.bbox(time)
        bx, by, bw, bh = self._b.bbox(time)
        x, y = min(ax, bx), min(ay, by)
        tx, ty = self._off_x.at_time(time), self._off_y.at_time(time)
        return (x + tx, y + ty, max(ax+aw, bx+bw) - x, max(ay+ah, by+bh) - y)


class Union(_BooleanOp):
    """Boolean union — combined area of both shapes.

    Fill uses nonzero fill-rule on combined paths.  Strokes are drawn per
    shape, each clipped to exclude the other's interior so that only the
    outer boundary is stroked.
    """
    def to_svg(self, time):
        pa, pb = self._a.path(time), self._b.path(time)
        u = self._uid
        defs = (f"<defs>{self._clip_inv(pb, f'nb{u}')}"
                f"{self._clip_inv(pa, f'na{u}')}</defs>")
        fill = f"<path d='{pa}{pb}'{self._fill_attrs(time)}/>"
        sa = f"<path d='{pa}'{self._stroke_attrs(time)} clip-path='url(#nb{u})'/>"
        sb = f"<path d='{pb}'{self._stroke_attrs(time)} clip-path='url(#na{u})'/>"
        return self._wrap_group(defs + fill + sa + sb, time)


class Difference(_BooleanOp):
    """Boolean difference: shape_a minus shape_b.

    Fill uses evenodd on combined paths clipped to shape_a.  Strokes:
    shape_a outside shape_b + shape_b inside shape_a.
    """
    def to_svg(self, time):
        pa, pb = self._a.path(time), self._b.path(time)
        u = self._uid
        defs = (f"<defs>{self._clip_def(pa, f'ca{u}')}"
                f"{self._clip_inv(pb, f'nb{u}')}</defs>")
        fill = (f"<path d='{pa}{pb}' fill-rule='evenodd'"
                f"{self._fill_attrs(time)} clip-path='url(#ca{u})'/>"  )
        sa = f"<path d='{pa}'{self._stroke_attrs(time)} clip-path='url(#nb{u})'/>"
        sb = f"<path d='{pb}'{self._stroke_attrs(time)} clip-path='url(#ca{u})'/>"
        return self._wrap_group(defs + fill + sa + sb, time)

    def bbox(self, time):
        ax, ay, aw, ah = self._a.bbox(time)
        tx, ty = self._off_x.at_time(time), self._off_y.at_time(time)
        return (ax + tx, ay + ty, aw, ah)


class Exclusion(_BooleanOp):
    """Boolean exclusion (XOR) — non-overlapping areas."""
    _fill_rule = 'evenodd'


class Intersection(_BooleanOp):
    """Boolean intersection — only where both shapes overlap.

    Fill: shape_a clipped to shape_b.  Strokes: each shape's outline
    clipped to the other so only the intersection boundary is drawn.
    """
    def path(self, time):
        return self._a.path(time)

    def to_svg(self, time):
        pa, pb = self._a.path(time), self._b.path(time)
        u = self._uid
        defs = (f"<defs>{self._clip_def(pa, f'ca{u}')}"
                f"{self._clip_def(pb, f'cb{u}')}</defs>")
        fill = f"<path d='{pa}'{self._fill_attrs(time)} clip-path='url(#cb{u})'/>"
        sa = f"<path d='{pa}'{self._stroke_attrs(time)} clip-path='url(#cb{u})'/>"
        sb = f"<path d='{pb}'{self._stroke_attrs(time)} clip-path='url(#ca{u})'/>"
        return self._wrap_group(defs + fill + sa + sb, time)

    def bbox(self, time):
        ax, ay, aw, ah = self._a.bbox(time)
        bx, by, bw, bh = self._b.bbox(time)
        x, y = max(ax, bx), max(ay, by)
        x2 = min(ax + aw, bx + bw)
        y2 = min(ay + ah, by + bh)
        tx, ty = self._off_x.at_time(time), self._off_y.at_time(time)
        return (x + tx, y + ty, max(0, x2 - x), max(0, y2 - y))


# ---------------------------------------------------------------------------
# Standalone helper functions
# ---------------------------------------------------------------------------

def brace_between_points(p1, p2, direction=None, label=None, buff=0, depth=18,
                         creation=0, z=0, **styling_kwargs):
    """Create a Brace between two arbitrary points.

    If direction is None, it is inferred perpendicular to the line p1→p2.
    Returns a Brace (VCollection).
    """
    x1, y1 = p1
    x2, y2 = p2
    # Build a thin invisible rect along the line
    dx, dy = x2 - x1, y2 - y1
    dist = math.hypot(dx, dy) or 1
    ux, uy = _normalize(dx, dy)
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    # Determine direction
    if direction is None:
        # Perpendicular (pointing to the left of p1→p2)
        nx, ny = -uy, ux
        if ny > 0:
            direction = 'down'
        elif ny < 0:
            direction = 'up'
        elif nx > 0:
            direction = 'right'
        else:
            direction = 'left'
    else:
        direction = _norm_dir(direction, 'down')
    # Create a dummy rectangle matching the span
    if direction in ('down', 'up'):
        dummy = Rectangle(dist, 1, x=cx - dist / 2, y=cy - 0.5, creation=creation)
    else:
        dummy = Rectangle(1, dist, x=cx - 0.5, y=cy - dist / 2, creation=creation)

    Brace = _get_brace()
    return Brace(dummy, direction=direction, label=label, buff=buff,
                 depth=depth, creation=creation, z=z, **styling_kwargs)


# ---------------------------------------------------------------------------
# Vector field visualizations
# ---------------------------------------------------------------------------

class ArrowVectorField(VCollection):
    """Vector field visualization using arrows.

    func: callable(x, y) -> (vx, vy) returning the vector at (x, y).
    x_range, y_range: (min, max, step) in pixel coordinates.
    """
    def __init__(self, func, x_range=(60, 1860, 120), y_range=(60, 1020, 120),
                 max_length=80, creation=0, z=0, **styling_kwargs):
        Arrow = _get_arrow()
        style_kw = {'stroke': '#58C4DD', 'stroke_width': 2} | styling_kwargs
        x_min, x_max, x_step = x_range
        y_min, y_max, y_step = y_range
        objects = []
        # Sample all vectors to find max magnitude for normalization
        samples = []
        x = x_min
        while x <= x_max:
            y = y_min
            while y <= y_max:
                vx, vy = func(x, y)
                mag = math.hypot(vx, vy)
                samples.append((x, y, vx, vy, mag))
                y += y_step
            x += x_step
        max_mag = max((s[4] for s in samples), default=1) or 1
        for sx, sy, vx, vy, mag in samples:
            if mag < 1e-9:
                continue
            scale = (mag / max_mag) * max_length
            nvx, nvy = vx / mag * scale, vy / mag * scale
            arrow = Arrow(x1=sx, y1=sy, x2=sx + nvx, y2=sy + nvy,
                          tip_length=12, tip_width=10, creation=creation, z=z, **style_kw)
            objects.append(arrow)
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return 'ArrowVectorField()'


class StreamLines(VCollection):
    """Animated flow lines for a vector field.

    func: callable(x, y) -> (vx, vy).
    Draws streamlines by integrating the field using Euler steps.
    """
    def __init__(self, func, x_range=(60, 1860, 200), y_range=(60, 1020, 200),
                 n_steps=40, step_size=5, creation=0, z=0, **styling_kwargs):
        style_kw = {'stroke': '#58C4DD', 'stroke_width': 2, 'fill_opacity': 0} | styling_kwargs
        x_min, x_max, x_step = x_range
        y_min, y_max, y_step = y_range
        objects = []
        x = x_min
        while x <= x_max:
            y = y_min
            while y <= y_max:
                pts = [(x, y)]
                cx, cy = x, y
                for _ in range(n_steps):
                    vx, vy = func(cx, cy)
                    mag = math.hypot(vx, vy)
                    if mag < 1e-9:
                        break
                    cx += vx / mag * step_size
                    cy += vy / mag * step_size
                    if cx < 0 or cx > CANVAS_WIDTH or cy < 0 or cy > CANVAS_HEIGHT:
                        break
                    pts.append((cx, cy))
                if len(pts) > 1:
                    line = Lines(*pts, creation=creation, z=z, **style_kw)
                    objects.append(line)
                y += y_step
            x += x_step
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return 'StreamLines()'


class Cutout(VObject):
    """Full-screen overlay with a rectangular cutout (spotlight effect).

    The overlay fills the canvas with a semi-transparent color and cuts out
    a rectangular hole at the specified position, drawing focus to the content
    underneath. The hole position and size can be animated.
    """
    def __init__(self, hole_x=660, hole_y=340, hole_w=600, hole_h=400,
                 color='#000', opacity=0.7, rx=0, ry=0,
                 creation: float = 0, z: float = 99, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        self.hole_x = attributes.Real(creation, hole_x)
        self.hole_y = attributes.Real(creation, hole_y)
        self.hole_w = attributes.Real(creation, hole_w)
        self.hole_h = attributes.Real(creation, hole_h)
        self.rx = rx
        self.ry = ry
        self.styling = style.Styling(
            styling_kwargs, creation=creation,
            fill=color, fill_opacity=opacity, stroke_width=0,
        )

    def _extra_attrs(self):
        return [self.hole_x, self.hole_y, self.hole_w, self.hole_h]

    def _shift_reals(self):
        return [(self.hole_x, self.hole_y)]

    def snap_points(self, time):
        hx = self.hole_x.at_time(time)
        hy = self.hole_y.at_time(time)
        return [(hx, hy)]

    def bbox(self, time=0):
        return (0, 0, CANVAS_WIDTH, CANVAS_HEIGHT)

    def path(self, time):
        return ''

    def set_hole(self, x=None, y=None, w=None, h=None,
                 start=0, end=None, easing=easings.smooth):
        """Animate hole position/size."""
        from vectormation._base_helpers import _set_attr
        if x is not None: _set_attr(self.hole_x, start, end, x, easing)
        if y is not None: _set_attr(self.hole_y, start, end, y, easing)
        if w is not None: _set_attr(self.hole_w, start, end, w, easing)
        if h is not None: _set_attr(self.hole_h, start, end, h, easing)
        return self

    def surround(self, obj, buff=20, start=0, end=None, easing=easings.smooth):
        """Move the cutout hole to surround a VObject's bounding box."""
        bx, by, bw, bh = obj.bbox(start)
        return self.set_hole(bx - buff, by - buff, bw + 2*buff, bh + 2*buff,
                             start=start, end=end, easing=easing)

    def to_svg(self, time):
        hx = self.hole_x.at_time(time)
        hy = self.hole_y.at_time(time)
        hw = self.hole_w.at_time(time)
        hh = self.hole_h.at_time(time)
        # Outer rect (full canvas) + inner rect (hole), even-odd fill rule
        d = (f'M0,0 H{CANVAS_WIDTH} V{CANVAS_HEIGHT} H0 Z '
             f'M{hx},{hy} h{hw} v{hh} h{-hw} Z')
        if self.rx or self.ry:
            rx, ry = self.rx, self.ry
            d = (f'M0,0 H{CANVAS_WIDTH} V{CANVAS_HEIGHT} H0 Z '
                 f'M{hx+rx},{hy} h{hw-2*rx} '
                 f'a{rx},{ry} 0 0 1 {rx},{ry} v{hh-2*ry} '
                 f'a{rx},{ry} 0 0 1 {-rx},{ry} h{-(hw-2*rx)} '
                 f'a{rx},{ry} 0 0 1 {-rx},{-ry} v{-(hh-2*ry)} '
                 f'a{rx},{ry} 0 0 1 {rx},{-ry} Z')
        return f"<path d='{d}' fill-rule='evenodd'{self.styling.svg_style(time)} />"

    def __repr__(self):
        return f'Cutout(hole=({self.hole_x.at_time(0)}, {self.hole_y.at_time(0)}))'
