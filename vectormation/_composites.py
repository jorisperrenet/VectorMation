"""Composite classes: Arrow, Axes, Graph, NumberLine, Table, etc."""
import math
import re
import tempfile
from collections import defaultdict

import vectormation.easings as easings
import vectormation.attributes as attributes
import vectormation.style as style
import vectormation.morphing as morphing
from vectormation._constants import (
    CANVAS_WIDTH, CANVAS_HEIGHT, ORIGIN,
    UNIT, SMALL_BUFF, DEFAULT_FONT_SIZE,
    DEFAULT_ARROW_TIP_LENGTH, DEFAULT_ARROW_TIP_WIDTH,
    DEFAULT_OBJECT_TO_EDGE_BUFF, DEFAULT_CHART_COLORS, CHAR_WIDTH_FACTOR, TEXT_Y_OFFSET,
    _sample_function, _normalize,
)
from vectormation._base import VObject, VCollection, _norm_dir, _lerp, _ramp, _lerp_point
from vectormation._shapes import (
    Polygon, Circle, Ellipse, Dot, Rectangle, RoundedRectangle, Line, Lines,
    Text, Path, Arc, Wedge,
)
from vectormation._arrows import Arrow, DoubleArrow, CurvedArrow, Brace, _arrowhead, _transform_rel_svg_path
from vectormation._axes import (
    Axes, Graph, NumberPlane, ComplexPlane,
    _nice_ticks, _log_ticks, _format_tick, _build_axes_decoration,
    _MARCH_SEGS, _AREA_STYLE, _HIGHLIGHT_STYLE,
    _AXIS_STROKE_WIDTH, _TICK_FONT_SIZE, _TICK_GAP, _LABEL_GAP,
)


def _label_text(text, x, y, font_size, creation=0, z=0, **overrides):
    """Create a centered white text label (common pattern in composites)."""
    kw = {'fill': '#fff', 'stroke_width': 0} | overrides
    return Text(text=str(text), x=x, y=y + font_size * TEXT_Y_OFFSET,
                font_size=font_size, text_anchor='middle', creation=creation, z=z, **kw)


class MorphObject(VCollection):
    """Morphs one object/collection into another over a time range.
    Must be added to the canvas. The source becomes hidden at start, target appears at end."""
    def __init__(self, morph_from, morph_to, start: float = 0, end: float = 1, z: float = 0,
                 easing=easings.smooth, change_existence=True, rotation_degrees: float = 0):
        # Both morph_from and morph_to are converted to collections
        if isinstance(morph_from, VObject):
            morph_from = VCollection(morph_from)
        if isinstance(morph_to, VObject):
            morph_to = VCollection(morph_to)
        assert isinstance(morph_from, VCollection)
        assert isinstance(morph_to, VCollection)

        def _flatten(collection):
            for obj in collection:
                if isinstance(obj, VCollection):
                    yield from _flatten(obj)
                else:
                    yield obj

        def _flatten_for_paths(collection, time):
            """Like _flatten but snapshot DynamicObjects at *time*."""
            for obj in collection:
                if isinstance(obj, VCollection):
                    yield from _flatten_for_paths(obj, time)
                elif isinstance(obj, DynamicObject):
                    inner = obj._func(time)
                    if isinstance(inner, VCollection):
                        yield from _flatten_for_paths(inner, time)
                    elif hasattr(inner, 'path'):
                        yield inner
                else:
                    yield obj

        # Hide source during/after morph, show target only after morph
        if change_existence:
            for obj in _flatten(morph_from):
                obj.show.set_onward(start, False)
            for obj in _flatten(morph_to):
                obj.show.set_onward(0, False)
                obj.show.set_onward(end, True)

        # Get SVG paths and stylings from all objects
        paths_from = [(morphing.Path(obj.path(start)), obj.styling) for obj in _flatten_for_paths(morph_from, start)]
        paths_to = [(morphing.Path(obj.path(end)), obj.styling) for obj in _flatten_for_paths(morph_to, end)]
        obj_from = morphing.Paths(*paths_from)
        obj_to = morphing.Paths(*paths_to)

        mapping = obj_from.morph(obj_to, start=start, end=end, easing=easing)

        # Compute rotation centre from source/target bounding boxes
        if rotation_degrees != 0:
            bbox_from = morph_from.bbox(start)
            bbox_to = morph_to.bbox(end)
            # Average the centres of both bounding boxes
            cx = (bbox_from[0] + bbox_from[2] / 2 + bbox_to[0] + bbox_to[2] / 2) / 2
            cy = (bbox_from[1] + bbox_from[3] / 2 + bbox_to[1] + bbox_to[3] / 2) / 2
        else:
            cx, cy = 0, 0

        # Convert morphing data into displayable Path objects
        # Group by compound_id to recombine subpaths from compound paths (e.g. letters with holes)
        groups = defaultdict(list)
        for path_func, styling_from, styling_to, compound_id in mapping:
            groups[compound_id].append((path_func, styling_from, styling_to))

        objects = []
        for group_entries in groups.values():
            path_funcs = [e[0] for e in group_entries]
            styling_from = group_entries[0][1]
            styling_to = group_entries[0][2]
            compound = len(path_funcs) > 1

            new = Path('', x=0, y=0, creation=start, z=z)
            new.show.set_onward(end, False)
            def _make_d_func(pfs):
                dur = end - start
                if dur <= 0:
                    dur = 1
                if len(pfs) == 1:
                    pf = pfs[0]
                    return lambda t: pf((t - start) / dur)
                return lambda t: ' '.join(pf((t - start) / dur) for pf in pfs)
            new.d.set(start, end, _make_d_func(path_funcs))
            # Interpolate styling, optionally adding rotation during the morph
            new.styling = styling_from.interpolate(
                styling_to, start, end, easing=easing,
                rotation_degrees=rotation_degrees, rotation_center=(cx, cy)
            )
            if compound:
                new.styling.fill_rule = attributes.String(start, 'evenodd')
            objects.append(new)

        super().__init__(*objects, creation=start, z=z)
        self.show.set_onward(end, False)

class LabeledDot(VCollection):
    """Dot with a centered text label."""
    def __init__(self, label='', r=24, cx=960, cy=540, creation: float = 0, z: float = 0, font_size=None, **styling_kwargs):
        dot_kw = {k: v for k, v in styling_kwargs.items() if k != 'fill'}
        dot_fill = styling_kwargs.get('fill', '#83C167')
        dot = Dot(r=r, cx=cx, cy=cy, creation=creation, z=z, fill=dot_fill, **dot_kw)
        if font_size is None:
            font_size = r * 0.9
        text = _label_text(label, cx, cy, font_size, creation=creation, z=z)
        super().__init__(dot, text, creation=creation, z=z)
        self.dot = dot
        self.label = text


class TexObject(VCollection):
    """Renders LaTeX content as SVG paths via dvisvgm.

    font_size: target height in pixels (default 30, matching Text).
    scale_x/scale_y in styles act as multipliers on the font_size-derived scale.
    """
    def __init__(self, to_render, x=0, y=0, font_size=48, creation: float = 0, z: float = 0, **styles):
        from vectormation.tex_file_writing import get_characters
        import vectormation._canvas as _cm
        tex_dir = f'{_cm.save_directory}/tex' if hasattr(_cm, 'save_directory') else tempfile.mkdtemp()
        self.char_viewbox, chars = get_characters(tex_dir, to_render, 'latex', '')

        # Normalize: scale raw dvisvgm pt coordinates to pixel size
        vb_height = abs(self.char_viewbox[3]) if self.char_viewbox[3] else 1
        base_scale = font_size / vb_height
        user_sx = styles.pop('scale_x', 1)
        user_sy = styles.pop('scale_y', 1)

        st = {'stroke_width': 0, 'fill': '#fff',
              'scale_x': base_scale * user_sx, 'scale_y': base_scale * user_sy} | styles
        chars = [from_svg(char, **st) for char in chars]

        # Init the collection of VObjects
        super().__init__(*chars, creation=creation, z=z)

        # Initialize the position and scale/width of the group viewbox
        self.x = attributes.Real(creation, x)
        self.y = attributes.Real(creation, y)

        # Get the bounding box and reset the position
        xmin, ymin, _, _ = self.bbox(creation)
        for obj in self.objects:
            obj.styling.dx.add_onward(creation, lambda t, _xm=xmin: self.x.at_time(t) - _xm)
            obj.styling.dy.add_onward(creation, lambda t, _ym=ymin: self.y.at_time(t) - _ym)


class SplitTexObject:
    """Renders multiple lines of LaTeX, each as a separate TexObject.
    Supports indexing, iteration, and conversion to a single VCollection."""
    def __init__(self, *lines, x=0, y=0, line_spacing=60, creation: float = 0, **styles):
        self.lines = [TexObject(line, x=x, y=y + i * line_spacing, creation=creation, **styles)
                      for i, line in enumerate(lines)]

    def __iter__(self): return iter(self.lines)
    def __getitem__(self, idx): return self.lines[idx]
    def __len__(self): return len(self.lines)


class ClipPath:
    """SVG clip path definition containing one or more shape objects."""
    def __init__(self, *objects):
        self.id = f'clip{id(self)}'
        self.objects = list(objects)

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

    def to_svg_def(self, time=None):
        return (f"<filter id='{self.id}'>"
                f"<feDropShadow dx='{self.dx}' dy='{self.dy}' "
                f"stdDeviation='{self.std_deviation}' "
                f"flood-color='{self.color}' flood-opacity='{self.opacity}'/>"
                f"</filter>")

    def filter_ref(self):
        return f'url(#{self.id})'



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


class NumberLine(VCollection):
    """A number line with ticks and labels, with optional endpoint arrows.

    x_range: (start, end, step) or (start, end) with auto step.
    """
    def __init__(self, x_range=(-5, 5, 1), length=720, x=240, y=540,
                 include_arrows=True, include_numbers=True,
                 tick_size=2*SMALL_BUFF, font_size=_TICK_FONT_SIZE,
                 creation=0, z=0, **styling_kwargs):
        if len(x_range) == 2:
            x_range = (*x_range, 1)
        x_start, x_end, x_step = x_range
        if x_end <= x_start:
            raise ValueError(f'NumberLine requires x_end > x_start, got ({x_start}, {x_end})')
        if x_step <= 0:
            raise ValueError(f'NumberLine requires positive step, got {x_step}')
        self.x_start, self.x_end, self.x_step = x_start, x_end, x_step
        self.length = length
        self.origin_x, self.origin_y = x, y

        line_style = {'stroke': '#fff', 'stroke_width': 3} | styling_kwargs
        objects = []

        # Main axis line
        if include_arrows:
            objects.append(Arrow(x1=x, y1=y, x2=x+length, y2=y,
                                 creation=creation, z=z, **line_style))
        else:
            objects.append(Line(x1=x, y1=y, x2=x+length, y2=y,
                                creation=creation, z=z, **line_style))

        # Ticks and labels
        val = x_start
        while val <= x_end + x_step * 0.01:
            sx = x + (val - x_start) / (x_end - x_start) * length
            objects.append(Line(x1=sx, y1=y - tick_size/2, x2=sx, y2=y + tick_size/2,
                                creation=creation, z=z, stroke='#fff', stroke_width=3))
            if include_numbers:
                label = f'{val:g}'
                objects.append(Text(text=label, x=sx - len(label) * font_size * 0.15,
                                    y=y + tick_size/2 + font_size + 2,
                                    font_size=font_size, creation=creation, z=z,
                                    fill='#aaa', stroke_width=0))
            val += x_step

        super().__init__(*objects, creation=creation, z=z)

    def number_to_point(self, value, time=0):
        """Convert a number on the line to an SVG (x, y) coordinate.

        This is the inverse of :meth:`point_to_number`.  The *time* parameter
        is accepted for API consistency with other coordinate-mapping methods
        but is currently unused because NumberLine geometry is static.
        """
        span = self.x_end - self.x_start
        if span == 0:
            return (self.origin_x, self.origin_y)
        t = (value - self.x_start) / span
        return (self.origin_x + t * self.length, self.origin_y)

    def point_to_number(self, x, y=None):
        """Convert an SVG x coordinate (or (x,y) tuple) back to a value on the line."""
        if isinstance(x, (tuple, list)):
            x = x[0]
        span = self.x_end - self.x_start
        if self.length == 0:
            return self.x_start
        t = (x - self.origin_x) / self.length
        return self.x_start + t * span

    def get_range(self):
        """Return (min_val, max_val) tuple for the number line's value range."""
        return (self.x_start, self.x_end)

    def get_range_length(self):
        """Return ``x_end - x_start``."""
        return self.x_end - self.x_start

    def snap_to_tick(self, value):
        """Return the nearest tick mark value, clamped to ``[x_start, x_end]``."""
        if value <= self.x_start:
            return self.x_start
        if value >= self.x_end:
            return self.x_end
        # Number of steps from x_start
        k = round((value - self.x_start) / self.x_step)
        snapped = self.x_start + k * self.x_step
        # Clamp to range (rounding could overshoot)
        return max(self.x_start, min(self.x_end, snapped))

    def add_pointer(self, value, label=None, color='#FF6B6B', size=12,
                     creation=0, z=1):
        """Add an animated pointer (triangle) above the number line at *value*.

        *value* may be a number or an ``attributes.Real`` — if animatable the
        pointer tracks the value automatically.  Returns the pointer
        ``VCollection`` (already added to this NumberLine's objects).
        """
        # Triangle pointing down at the value
        px, py = self.number_to_point(
            value.at_time(creation) if hasattr(value, 'at_time') else value
        )
        ptr = Polygon(
            (px - size / 2, py - size - 2),
            (px + size / 2, py - size - 2),
            (px, py - 2),
            creation=creation, z=z,
            fill=color, stroke_width=0,
        )

        # Dynamic positioning: update vertices each frame
        _nl = self
        _val = value

        def _ptr_pos(time):
            v = _val.at_time(time) if hasattr(_val, 'at_time') else _val
            return _nl.number_to_point(v)

        ptr.vertices[0].set_onward(creation,
            lambda t: (_ptr_pos(t)[0] - size / 2, _ptr_pos(t)[1] - size - 2))
        ptr.vertices[1].set_onward(creation,
            lambda t: (_ptr_pos(t)[0] + size / 2, _ptr_pos(t)[1] - size - 2))
        ptr.vertices[2].set_onward(creation,
            lambda t: (_ptr_pos(t)[0], _ptr_pos(t)[1] - 2))

        objects = [ptr]
        if label is not None:
            lbl = Text(text=str(label), x=px, y=py - size - 18,
                        font_size=20, fill=color, stroke_width=0,
                        text_anchor='middle', creation=creation, z=z + 0.1)
            lbl.x.set_onward(creation, lambda t: _ptr_pos(t)[0])
            lbl.y.set_onward(creation, lambda t: _ptr_pos(t)[1] - size - 18)
            objects.append(lbl)

        from vectormation._base import VCollection as _VC
        group = _VC(*objects, creation=creation, z=z)
        self.objects.append(group)
        return group

    def animate_pointer(self, pointer_group, target_value, start=0, end=1, easing=easings.smooth):
        """Animate a pointer (from add_pointer) to a new value.

        pointer_group: the VCollection returned by add_pointer()
        target_value: the new value to point to
        """
        dur = end - start
        if dur <= 0:
            return self
        # Get the pointer's triangle (first object in group)
        tri = pointer_group.objects[0]
        # Current tip x at start time
        current_x = tri.vertices[2].at_time(start)[0]
        target_x = self.number_to_point(target_value)[0]
        dx = target_x - current_x
        # Animate all vertices of the triangle
        for vert in tri.vertices:
            base = vert.at_time(start)
            vert.move_to(start, end, (base[0] + dx, base[1]), easing=easing)
        # If there's a label (second object), animate it too
        if len(pointer_group.objects) > 1:
            lbl = pointer_group.objects[1]
            lbl_x = lbl.x.at_time(start)
            lbl_y = lbl.y.at_time(start)
            lbl.x.move_to(start, end, lbl_x + dx, easing=easing)
            lbl.y.move_to(start, end, lbl_y, easing=easing)
        return self

    def add_segment(self, start_val, end_val, color='#58C4DD', height=8, creation=0, z=1):
        """Highlight a range on the number line with a filled rectangle."""
        x1, y = self.number_to_point(start_val)
        x2, _ = self.number_to_point(end_val)
        w = abs(x2 - x1)
        rect = Rectangle(w, height, x=min(x1, x2), y=y - height / 2,
                         creation=creation, z=z,
                         fill=color, fill_opacity=0.7, stroke_width=0)
        self.objects.append(rect)
        return rect

    def add_dot_at(self, value, color='#FF6B6B', radius=8, creation=0, **kwargs):
        """Add a colored dot at a specific value on the number line.

        Uses :meth:`number_to_point` to convert the value to SVG coordinates.

        Parameters
        ----------
        value:
            Numeric position on the line.
        color:
            Fill color for the dot (default ``'#FF6B6B'``).
        radius:
            Radius of the dot in SVG pixels (default 8).
        creation:
            Creation time for the Dot.
        **kwargs:
            Extra keyword arguments forwarded to the Dot constructor.

        Returns
        -------
        Dot
            The created Dot (already appended to this NumberLine's objects).
        """
        px, py = self.number_to_point(value)
        kw = {'fill': color, 'stroke_width': 0} | kwargs
        dot = Dot(cx=px, cy=py, r=radius, creation=creation, **kw)
        self.objects.append(dot)
        return dot

    def highlight_range(self, start_val, end_val, color='#FFFF00',
                        height=16, opacity=0.4, creation=0, z=1, **kwargs):
        """Highlight a numeric range on the number line with a colored rectangle.

        Creates a semi-transparent filled rectangle that spans from *start_val*
        to *end_val* along the line.  Unlike :meth:`add_segment` (which uses a
        fixed 0.7 opacity and blue color), this method exposes *color*,
        *height*, and *opacity* as top-level parameters so common highlight
        colors (yellow, green, red…) can be applied directly.

        Parameters
        ----------
        start_val, end_val:
            Numeric values on the line.  They are clamped to the range
            [x_start, x_end] so the rectangle never extends beyond the axis.
        color:
            Fill color for the highlight rectangle.  Default ``'#FFFF00'``
            (yellow).
        height:
            Pixel height of the highlight rectangle (it is centred on the
            line).
        opacity:
            Fill opacity in [0, 1].  Default 0.4 gives a translucent overlay.
        creation:
            Creation time for the returned Rectangle.
        z:
            Z-layer for the rectangle.
        **kwargs:
            Extra styling keyword arguments forwarded to Rectangle (e.g.
            ``stroke_width``, ``stroke``).

        Returns
        -------
        Rectangle
            The highlight rectangle (already appended to this NumberLine's
            objects list).
        """
        # Clamp to valid axis range
        sv = max(self.x_start, min(self.x_end, start_val))
        ev = max(self.x_start, min(self.x_end, end_val))
        if sv > ev:
            sv, ev = ev, sv
        x1, y = self.number_to_point(sv)
        x2, _ = self.number_to_point(ev)
        w = abs(x2 - x1)
        rect = Rectangle(w, height, x=min(x1, x2), y=y - height / 2,
                          creation=creation, z=z,
                          fill=color, fill_opacity=opacity, stroke_width=0,
                          **kwargs)
        self.objects.append(rect)
        return rect

    def add_label(self, value, text, buff=10, font_size=24, side='below', creation=0, **kwargs):
        """Add a text label at the given value on the number line.

        value: the numeric position on the line.
        text: the string to display.
        buff: pixel distance above or below the line.
        side: 'below' (default) or 'above'.
        Returns self.
        """
        px, py = self.number_to_point(value)
        kw = {'fill': '#fff', 'stroke_width': 0, 'text_anchor': 'middle'} | kwargs
        if side == 'above':
            ty = py - buff - font_size
        else:
            ty = py + buff + font_size
        lbl = Text(text=str(text), x=px, y=ty,
                   font_size=font_size, creation=creation, **kw)
        self.objects.append(lbl)
        return self

    def add_tick_labels_range(self, start_val, end_val, step, format_func=None,
                              font_size=None, creation=0):
        """Batch-add tick labels for values from *start_val* to *end_val*.

        Adds Text objects positioned at each tick value along the number line.

        Parameters
        ----------
        start_val:
            First tick value (inclusive).
        end_val:
            Last tick value (inclusive, if reachable by *step*).
        step:
            Increment between tick values.  Must be positive.
        format_func:
            Callable that converts a numeric value to a label string.
            Defaults to ``str``.
        font_size:
            Font size for the labels.  Defaults to the number line's font
            size (the ``_TICK_FONT_SIZE`` used during construction).
        creation:
            Appearance time (seconds).

        Returns
        -------
        self
        """
        if format_func is None:
            format_func = str
        if font_size is None:
            font_size = _TICK_FONT_SIZE
        val = start_val
        while val <= end_val + step * 0.001:
            px, py = self.number_to_point(val)
            label_text = format_func(val)
            lbl = Text(text=label_text, x=px, y=py + SMALL_BUFF + font_size,
                       font_size=font_size, creation=creation,
                       fill='#fff', stroke_width=0, text_anchor='middle')
            self.objects.append(lbl)
            val += step
        return self

    def add_brace(self, x1, x2, label=None, direction='down', **kwargs):
        """Add a curly brace between two values on the number line.

        Uses the existing :class:`Brace` class positioned between the
        SVG coordinates of *x1* and *x2* on the line.

        Parameters
        ----------
        x1, x2:
            Numeric values on the number line defining the brace span.
        label:
            Optional text label placed near the brace midpoint.
        direction:
            Which side the brace sits on.  Accepts a string
            (``'down'``, ``'up'``, ``'left'``, ``'right'``) or a
            direction constant (``DOWN``, ``UP``, ``LEFT``, ``RIGHT``).
            Default ``'down'``.
        **kwargs:
            Extra keyword arguments forwarded to the :class:`Brace`
            constructor (e.g. ``fill``, ``depth``, ``buff``).

        Returns
        -------
        Brace
            The Brace object (already appended to this NumberLine's
            objects list).
        """
        direction = _norm_dir(direction, 'down')
        p1x, p1y = self.number_to_point(x1)
        p2x, _p2y = self.number_to_point(x2)
        lx, rx_ = min(p1x, p2x), max(p1x, p2x)
        w = rx_ - lx
        # Create a temporary rectangle as the brace target
        target = Rectangle(w, 1, x=lx, y=p1y - 0.5)
        brace = Brace(target, direction=direction, label=label, **kwargs)
        self.objects.append(brace)
        return brace

    def add_interval_bracket(self, x1, x2, closed_left=True, closed_right=True,
                              creation=0, **kwargs):
        """Show an interval on the number line with bracket notation.

        Draws a horizontal line between ``x1`` and ``x2`` with bracket or
        parenthesis characters at each end to indicate whether the endpoint
        is included (closed) or excluded (open).

        Parameters
        ----------
        x1, x2:
            Numeric values on the line defining the interval endpoints.
        closed_left:
            If True, use ``'['`` at the left endpoint; otherwise ``'('``.
        closed_right:
            If True, use ``']'`` at the right endpoint; otherwise ``')'``.
        creation:
            Appearance time.
        **kwargs:
            Extra styling keyword arguments for the connecting line.

        Returns
        -------
        VCollection
            A VCollection containing the connecting line and two bracket
            Text objects (already appended to this NumberLine's objects).
        """
        style_kw = {'stroke': '#58C4DD', 'stroke_width': 3} | kwargs
        p1x, p1y = self.number_to_point(x1)
        p2x, _p2y = self.number_to_point(x2)
        # Offset above the number line
        offset_y = -20
        ly = p1y + offset_y
        bar = Line(x1=p1x, y1=ly, x2=p2x, y2=ly, creation=creation, **style_kw)
        left_char = '[' if closed_left else '('
        right_char = ']' if closed_right else ')'
        font_size = 24
        left_text = Text(text=left_char, x=p1x - font_size * 0.3, y=ly + font_size * 0.35,
                         font_size=font_size, creation=creation,
                         fill=style_kw.get('stroke', '#58C4DD'), stroke_width=0)
        right_text = Text(text=right_char, x=p2x + font_size * 0.05, y=ly + font_size * 0.35,
                          font_size=font_size, creation=creation,
                          fill=style_kw.get('stroke', '#58C4DD'), stroke_width=0)
        group = VCollection(bar, left_text, right_text, creation=creation)
        self.objects.append(group)
        return group

    def animate_add_tick(self, value, start=0, end=1, label=None, easing=None):
        """Dynamically add a tick mark at *value* with a pop-in animation.

        Creates a small vertical Line at the position on the number line and
        optionally a Text label below it.  Both fade and scale in during
        ``[start, end]``.

        Parameters
        ----------
        value:
            Numeric value on the number line where the tick should appear.
        start:
            Time at which the animation begins.
        end:
            Time at which the animation ends.
        label:
            Optional label text below the tick.  If ``None``, no label is added.
        easing:
            Easing function for the animation.  Defaults to
            ``easings.smooth``.

        Returns
        -------
        self
        """
        if easing is None:
            easing = easings.smooth
        px, py = self.number_to_point(value)
        tick_size = 2 * SMALL_BUFF
        tick = Line(x1=px, y1=py - tick_size / 2, x2=px, y2=py + tick_size / 2,
                    creation=start, stroke='#fff', stroke_width=3)
        tick.fadein(start=start, end=end, easing=easing)
        self.objects.append(tick)

        if label is not None:
            font_size = _TICK_FONT_SIZE
            lbl = Text(text=str(label), x=px - len(str(label)) * font_size * 0.15,
                        y=py + tick_size / 2 + font_size + 2,
                        font_size=font_size, creation=start,
                        fill='#aaa', stroke_width=0)
            lbl.fadein(start=start, end=end, easing=easing)
            self.objects.append(lbl)

        return self

    def add_animated_pointer(self, value_func, start=0, end=None, color='#FFFF00',
                             label=True):
        """Add a pointer (triangle) that tracks a dynamic value function over time.

        Parameters
        ----------
        value_func:
            A callable ``f(time)`` returning the numeric value on the line.
        start:
            Time at which the pointer appears.
        end:
            Time at which the pointer disappears (``None`` = forever).
        color:
            Fill color for the pointer triangle.
        label:
            If True, add a Text showing the current value below the pointer.

        Returns
        -------
        self
        """
        size = 12
        _nl = self
        _vf = value_func
        _cache = [None, None]  # [last_t, last_result]

        def _ptr_pos(t):
            if _cache[0] != t:
                _cache[0] = t
                _cache[1] = _nl.number_to_point(_vf(t))
            return _cache[1]

        # Initial position
        px, py = _ptr_pos(start)
        ptr = Polygon(
            (px - size / 2, py - size - 2),
            (px + size / 2, py - size - 2),
            (px, py - 2),
            creation=start, z=1,
            fill=color, stroke_width=0,
        )
        ptr.vertices[0].set_onward(start,
            lambda t: (_ptr_pos(t)[0] - size / 2, _ptr_pos(t)[1] - size - 2))
        ptr.vertices[1].set_onward(start,
            lambda t: (_ptr_pos(t)[0] + size / 2, _ptr_pos(t)[1] - size - 2))
        ptr.vertices[2].set_onward(start,
            lambda t: (_ptr_pos(t)[0], _ptr_pos(t)[1] - 2))

        if end is not None:
            ptr._hide_from(end)

        self.objects.append(ptr)

        if label:
            lbl = Text(text=str(round(_vf(start), 2)), x=px, y=py - size - 18,
                        font_size=20, fill=color, stroke_width=0,
                        text_anchor='middle', creation=start, z=1.1)
            lbl.x.set_onward(start, lambda t: _ptr_pos(t)[0])
            lbl.y.set_onward(start, lambda t: _ptr_pos(t)[1] - size - 18)
            lbl.text.set_onward(start, lambda t: str(round(_vf(t), 2)))
            if end is not None:
                lbl._hide_from(end)
            self.objects.append(lbl)

        return self

    def animate_range(self, new_start, new_end, start=0, end=1, easing=None):
        """Animate the number line's visible range to ``[new_start, new_end]``.

        Tick marks and labels slide to their new positions under the updated
        range mapping.  Objects whose tick values fall outside the new range
        are faded out; objects now inside are faded in.

        After the animation completes, ``self.x_start`` and ``self.x_end``
        are updated so that :meth:`number_to_point` uses the new range.

        Parameters
        ----------
        new_start:
            New range start value.
        new_end:
            New range end value.
        start:
            Animation start time.
        end:
            Animation end time.
        easing:
            Easing function (default ``easings.smooth``).

        Returns
        -------
        self
        """
        _easing = easing or easings.smooth
        old_start, old_end = self.x_start, self.x_end
        length = self.length
        ox = self.origin_x
        dur = end - start

        def _old_val_to_x(val):
            span = old_end - old_start
            return ox + (val - old_start) / span * length if span else ox

        def _new_val_to_x(val):
            span = new_end - new_start
            return ox + (val - new_start) / span * length if span else ox

        # Skip object 0 (the main line/arrow) -- it spans the full length
        # and does not move.
        # Remaining objects are tick/label pairs.  Walk through them
        # and figure out which tick value each belongs to.
        i = 1
        while i < len(self.objects):
            obj = self.objects[i]
            # Tick lines: Line objects whose x1 roughly equals a tick position
            if hasattr(obj, 'p1'):
                # It's a Line (tick mark)
                cur_x = obj.p1.at_time(start)[0]
                # Determine what value this tick represents using old mapping
                val = old_start + (cur_x - ox) / length * (old_end - old_start)
                new_x = _new_val_to_x(val)
                if dur <= 0:
                    obj.p1.set_onward(start, (new_x, obj.p1.at_time(start)[1]))
                    obj.p2.set_onward(start, (new_x, obj.p2.at_time(start)[1]))
                else:
                    old_x = cur_x
                    p1_y = obj.p1.at_time(start)[1]
                    p2_y = obj.p2.at_time(start)[1]
                    _dx = new_x - old_x
                    obj.p1.set_onward(start,
                        lambda t, _ox=old_x, _dx=_dx, _y=p1_y, _s=start, _d=dur, _e=_easing, _end=end:
                            (_ox + _dx * _e(min(1, (t - _s) / _d)) if t < _end else _ox + _dx, _y))
                    obj.p2.set_onward(start,
                        lambda t, _ox=old_x, _dx=_dx, _y=p2_y, _s=start, _d=dur, _e=_easing, _end=end:
                            (_ox + _dx * _e(min(1, (t - _s) / _d)) if t < _end else _ox + _dx, _y))
            elif hasattr(obj, 'text') and hasattr(obj, 'x'):
                # It's a Text label
                cur_x = obj.x.at_time(start)
                # Approximate: label x is near the tick position
                # Read the label text to get the value
                txt = obj.text.at_time(start)
                try:
                    val = float(txt)
                except (ValueError, TypeError):
                    i += 1
                    continue
                new_x = _new_val_to_x(val)
                # Adjust for label offset (label x was offset from tick x)
                old_tick_x = _old_val_to_x(val)
                offset = cur_x - old_tick_x
                target_x = new_x + offset
                if dur <= 0:
                    obj.x.set_onward(start, target_x)
                else:
                    obj.x.move_to(start, end, target_x, easing=_easing)
            i += 1

        # Update range properties at the end of the animation
        if dur <= 0:
            self.x_start, self.x_end = new_start, new_end
        else:
            # Schedule the update -- since Python closures capture self,
            # we use a post-animation updater-style approach.
            # We set them immediately so number_to_point uses new values
            # for any subsequent calls.
            self.x_start, self.x_end = new_start, new_end

        return self

    def __repr__(self):
        return f'NumberLine([{self.x_start}, {self.x_end}], step={self.x_step})'


class PieChart(VCollection):
    """Pie chart visualization using Wedge sectors.

    values: list of numeric values (proportional sizes).
    labels: optional list of labels.
    colors: list of sector colors (cycles if shorter than values).
    """
    def __init__(self, values, labels=None, colors=None, cx=960, cy=540, r=240,
                 start_angle=90, creation: float = 0, z: float = 0):
        if colors is None:
            colors = list(DEFAULT_CHART_COLORS)
        total = sum(values)
        if total == 0:
            total = 1
        objects: list[VObject] = []
        angle = start_angle
        for i, val in enumerate(values):
            sweep = 360 * val / total
            color = colors[i % len(colors)]
            sector = Wedge(cx=cx, cy=cy, r=r, start_angle=angle, end_angle=angle + sweep,
                           creation=creation, z=z, fill=color, fill_opacity=0.85, stroke='#222', stroke_width=2)
            objects.append(sector)
            if labels and i < len(labels):
                mid_angle = math.radians(angle + sweep / 2)
                lx = cx + (r * 0.65) * math.cos(mid_angle)
                ly = cy - (r * 0.65) * math.sin(mid_angle)
                lbl = Text(text=str(labels[i]), x=lx, y=ly, font_size=17,
                           text_anchor='middle', creation=creation, z=z, fill='#fff', stroke_width=0)
                objects.append(lbl)
            angle += sweep
        self._sectors = [o for o in objects if isinstance(o, Wedge)]
        super().__init__(*objects, creation=creation, z=z)
        self.values = values
        self._cx, self._cy = cx, cy

    @classmethod
    def from_dict(cls, data, **kwargs):
        """Create a PieChart from a dictionary.

        Keys become labels and values become sector sizes.

        Parameters
        ----------
        data:
            A dictionary mapping label strings to numeric values.
        **kwargs:
            Extra keyword arguments forwarded to the PieChart constructor.

        Returns
        -------
        PieChart
        """
        values = list(data.values())
        labels = list(data.keys())
        return cls(values, labels=labels, **kwargs)

    def __repr__(self):
        return f'PieChart({len(self.values)} sectors)'

    def get_sector(self, index):
        if index < 0 or index >= len(self._sectors):
            raise IndexError(f"sector index {index} out of range (0..{len(self._sectors) - 1})")
        return self._sectors[index]

    def highlight_sector(self, index, start=0, end=1, pull_distance=30, easing=easings.there_and_back):
        """Pull out a sector from the pie to highlight it."""
        if index < 0 or index >= len(self._sectors):
            return self
        sector = self._sectors[index]
        # Calculate angle bisector direction
        sa = sector.start_angle.at_time(start) if hasattr(sector.start_angle, 'at_time') else 0
        ea = sector.end_angle.at_time(start) if hasattr(sector.end_angle, 'at_time') else 0
        mid_rad = math.radians((sa + ea) / 2)
        dx = pull_distance * math.cos(mid_rad)
        dy = -pull_distance * math.sin(mid_rad)
        dur = end - start
        if dur <= 0:
            return self
        sector.shift(dx=dx, dy=dy, start=start, end=start + dur / 2, easing=easing)
        return self

    def explode(self, indices, distance=20, start=0, end=None, easing=None):
        """Permanently shift specified sectors outward from the pie center.

        For each index in *indices*, the sector's bisect angle is computed
        and the sector is shifted along that direction by *distance* pixels.

        Parameters
        ----------
        indices:
            Sequence of sector indices to explode.
        distance:
            How many pixels to shift each sector outward.
        start:
            Time at which the shift begins.
        end:
            Time at which the shift ends.  ``None`` means instant.
        easing:
            Easing function for the animation.

        Returns
        -------
        self
        """
        for idx in indices:
            if idx < 0 or idx >= len(self._sectors):
                continue
            sector = self._sectors[idx]
            # Read angles from the actual Wedge attributes
            sa = sector.start_angle.at_time(start) if hasattr(sector.start_angle, 'at_time') else 0
            ea = sector.end_angle.at_time(start) if hasattr(sector.end_angle, 'at_time') else 0
            mid_rad = math.radians((sa + ea) / 2)
            dx = distance * math.cos(mid_rad)
            dy = -distance * math.sin(mid_rad)
            sector.shift(dx=dx, dy=dy, start=start, end=end, easing=easing or easings.smooth)
        return self

    def animate_values(self, new_values, start=0, end=1, easing=easings.smooth):
        """Animate pie chart to new values by morphing sector angles."""
        if len(new_values) != len(self.values):
            return self
        old_values = list(self.values)
        old_total = sum(old_values) or 1
        new_total = sum(new_values) or 1
        dur = end - start
        if dur <= 0:
            return self
        # Update stored values
        self.values = list(new_values)
        # Animate each sector's start/end angles
        cum_old, cum_new = 0, 0
        for i, sector in enumerate(self._sectors):
            old_start_angle = 360 * cum_old / old_total + 90
            old_end_angle = 360 * (cum_old + old_values[i]) / old_total + 90
            new_start_angle = 360 * cum_new / new_total + 90
            new_end_angle = 360 * (cum_new + new_values[i]) / new_total + 90
            _d = max(dur, 1e-9)
            sector.start_angle.set(start, end,
                _lerp(start, _d, old_start_angle, new_start_angle, easing), stay=True)
            sector.end_angle.set(start, end,
                _lerp(start, _d, old_end_angle, new_end_angle, easing), stay=True)
            cum_old += old_values[i]
            cum_new += new_values[i]
        return self

    def add_percentage_labels(self, fmt='{:.0f}%', font_size=16, color='#fff', creation=0):
        """Add percentage labels at the center of each sector."""
        total = sum(self.values) or 1
        angle = 90  # PieChart starts at 90 degrees
        for sector, val in zip(self._sectors, self.values):
            sweep = 360 * val / total
            mid_angle = math.radians(angle + sweep / 2)
            r = sector.r.at_time(creation) * 0.65
            cx = sector.cx.at_time(creation)
            cy = sector.cy.at_time(creation)
            lx = cx + r * math.cos(mid_angle)
            ly = cy - r * math.sin(mid_angle)
            label = Text(text=fmt.format(val / total * 100), font_size=font_size,
                         x=lx, y=ly, creation=creation, fill=color,
                         text_anchor='middle', stroke_width=0)
            self.objects.append(label)
            angle += sweep
        return self


class DonutChart(VCollection):
    """Donut (ring) chart — PieChart with a hollow center.

    values: list of numeric values (proportional sizes).
    labels: optional list of labels.
    inner_radius: radius of the hole (0 < inner_radius < r).
    """
    def __init__(self, values, labels=None, colors=None, cx=960, cy=540,
                 r=240, inner_radius=120, start_angle=90,
                 center_text=None, font_size=17, creation: float = 0, z: float = 0):
        if colors is None:
            colors = list(DEFAULT_CHART_COLORS)
        total = sum(values)
        if total == 0:
            total = 1
        objects: list[VObject] = []
        angle = start_angle
        sectors = []
        for i, val in enumerate(values):
            sweep = 360 * val / total
            color = colors[i % len(colors)]
            # Draw arc sector as a Path (outer arc CW, inner arc CCW)
            a1 = math.radians(angle)
            a2 = math.radians(angle + sweep)
            ox1, oy1 = cx + r * math.cos(a1), cy - r * math.sin(a1)
            ox2, oy2 = cx + r * math.cos(a2), cy - r * math.sin(a2)
            ix1, iy1 = cx + inner_radius * math.cos(a2), cy - inner_radius * math.sin(a2)
            ix2, iy2 = cx + inner_radius * math.cos(a1), cy - inner_radius * math.sin(a1)
            large = 1 if sweep > 180 else 0
            d = (f'M{ox1:.1f},{oy1:.1f} '
                 f'A{r},{r} 0 {large} 0 {ox2:.1f},{oy2:.1f} '
                 f'L{ix1:.1f},{iy1:.1f} '
                 f'A{inner_radius},{inner_radius} 0 {large} 1 {ix2:.1f},{iy2:.1f} Z')
            sector = Path(d, x=0, y=0, fill=color, fill_opacity=0.85,
                          stroke='#222', stroke_width=2, creation=creation, z=z)
            sectors.append(sector)
            objects.append(sector)
            if labels and i < len(labels):
                mid_r = (r + inner_radius) / 2
                mid_angle = math.radians(angle + sweep / 2)
                lx = cx + mid_r * math.cos(mid_angle)
                ly = cy - mid_r * math.sin(mid_angle)
                lbl = Text(text=str(labels[i]), x=lx, y=ly,
                           font_size=font_size, text_anchor='middle',
                           creation=creation, z=z + 0.1, fill='#fff', stroke_width=0)
                objects.append(lbl)
            angle += sweep
        self._sectors = sectors
        self._cx, self._cy = cx, cy
        self._r, self._inner_radius = r, inner_radius
        self._start_angle = start_angle
        if center_text is not None:
            ct = Text(text=str(center_text), x=cx, y=cy + font_size * TEXT_Y_OFFSET,
                      font_size=int(font_size * 1.5), text_anchor='middle',
                      fill='#fff', stroke_width=0, creation=creation, z=z + 0.1)
            objects.append(ct)
        super().__init__(*objects, creation=creation, z=z)
        self.values = values

    def __repr__(self):
        return f'DonutChart({len(self.values)} sectors)'

    def get_sector(self, index):
        """Return the Path object for the sector at index."""
        if index < 0 or index >= len(self._sectors):
            raise IndexError(f"sector index {index} out of range (0..{len(self._sectors) - 1})")
        return self._sectors[index]

    def highlight_sector(self, index, start=0, end=1, pull_distance=30, easing=easings.there_and_back):
        """Pull out a donut sector to highlight it by shifting it outward."""
        if index < 0 or index >= len(self._sectors):
            return self
        sector = self._sectors[index]
        # Determine mid-angle for this sector from cumulative values
        total = sum(self.values) or 1
        cum = sum(self.values[:index])
        start_a = self._start_angle + 360 * cum / total
        sweep = 360 * self.values[index] / total
        mid_rad = math.radians(start_a + sweep / 2)
        dx = pull_distance * math.cos(mid_rad)
        dy = -pull_distance * math.sin(mid_rad)
        dur = end - start
        if dur <= 0:
            return self
        sector.shift(dx=dx, dy=dy, start=start, end=start + dur / 2, easing=easing)
        return self

    def animate_values(self, new_values, start=0, end=1, easing=easings.smooth):
        """Animate donut chart to new values by morphing sector path shapes."""
        if len(new_values) != len(self.values):
            return self
        old_values = list(self.values)
        old_total = sum(old_values) or 1
        new_total = sum(new_values) or 1
        dur = end - start
        if dur <= 0:
            return self
        self.values = list(new_values)
        cx, cy = self._cx, self._cy
        r, ir = self._r, self._inner_radius
        sa0 = self._start_angle
        for i, sector in enumerate(self._sectors):
            old_cum = sum(old_values[:i])
            new_cum = sum(new_values[:i])
            old_a1 = sa0 + 360 * old_cum / old_total
            old_a2 = sa0 + 360 * (old_cum + old_values[i]) / old_total
            new_a1 = sa0 + 360 * new_cum / new_total
            new_a2 = sa0 + 360 * (new_cum + new_values[i]) / new_total
            _s, _d = start, max(dur, 1e-9)
            _oa1, _oa2 = old_a1, old_a2
            _na1, _na2 = new_a1, new_a2

            def _make_d(t, _s=_s, _d=_d, _oa1=_oa1, _oa2=_oa2,
                        _na1=_na1, _na2=_na2):
                prog = easing(max(0.0, min(1.0, (t - _s) / _d)))
                a1 = math.radians(_oa1 + (_na1 - _oa1) * prog)
                a2 = math.radians(_oa2 + (_na2 - _oa2) * prog)
                sweep_deg = math.degrees(a2 - a1)
                ox1, oy1 = cx + r * math.cos(a1), cy - r * math.sin(a1)
                ox2, oy2 = cx + r * math.cos(a2), cy - r * math.sin(a2)
                ix1, iy1 = cx + ir * math.cos(a2), cy - ir * math.sin(a2)
                ix2, iy2 = cx + ir * math.cos(a1), cy - ir * math.sin(a1)
                large = 1 if sweep_deg > 180 else 0
                return (f'M{ox1:.1f},{oy1:.1f} '
                        f'A{r},{r} 0 {large} 0 {ox2:.1f},{oy2:.1f} '
                        f'L{ix1:.1f},{iy1:.1f} '
                        f'A{ir},{ir} 0 {large} 1 {ix2:.1f},{iy2:.1f} Z')

            sector.d.set(start, end, _make_d, stay=True)
        return self


class BarChart(VCollection):
    """Simple bar chart visualization.

    values: list of numeric values.
    labels: optional list of labels (same length as values).
    colors: list of bar colors (cycles if shorter than values).
    """
    def __init__(self, values, labels=None, colors=None, x=120, y=60,
                 width=1440, height=840, bar_spacing=0.2,
                 creation: float = 0, z: float = 0):
        if colors is None:
            colors = list(DEFAULT_CHART_COLORS)
        n = len(values)
        if n == 0:
            super().__init__(creation=creation, z=z)
            self.values, self.bar_count, self._bars, self._labels = [], 0, [], []
            self._height, self._y = height, y
            self._x, self._width = x, width
            self._bar_spacing = bar_spacing
            self._colors = colors
            self._creation = creation
            self._z = z
            return
        max_val = max(abs(v) for v in values) if values else 1
        bar_width = width / n
        inner_width = bar_width * (1 - bar_spacing)
        objects: list[VObject] = []
        bars: list = []
        label_objs: list = []

        for i, val in enumerate(values):
            bar_h = abs(val) / max_val * height * 0.85
            bx = x + i * bar_width + (bar_width - inner_width) / 2
            by = y + height - bar_h if val >= 0 else y + height
            color = colors[i % len(colors)]
            bar = Rectangle(inner_width, bar_h, x=bx, y=by,
                            creation=creation, z=z,
                            fill=color, fill_opacity=0.8, stroke_width=0)
            objects.append(bar)
            bars.append(bar)

            if labels and i < len(labels):
                lbl = Text(text=str(labels[i]),
                           x=bx + inner_width / 2, y=y + height + 24,
                           font_size=14, text_anchor='middle',
                           creation=creation, z=z, fill='#aaa', stroke_width=0)
                objects.append(lbl)
                label_objs.append(lbl)
            else:
                label_objs.append(None)

        # Baseline
        baseline = Line(x1=x, y1=y + height, x2=x + width, y2=y + height,
                        creation=creation, z=z, stroke='#fff', stroke_width=3)
        objects.append(baseline)
        super().__init__(*objects, creation=creation, z=z)
        self.values = values
        self.bar_count = n
        self._bars = bars
        self._labels = label_objs
        self._height = height
        self._y = y
        self._x = x
        self._width = width
        self._bar_spacing = bar_spacing
        self._colors = colors
        self._creation = creation
        self._z = z

    @classmethod
    def from_dict(cls, data, **kwargs):
        """Create a BarChart from a dictionary.

        Keys become labels and values become bar heights.

        Parameters
        ----------
        data:
            A dictionary mapping label strings to numeric values.
        **kwargs:
            Extra keyword arguments forwarded to the BarChart constructor.

        Returns
        -------
        BarChart
        """
        values = list(data.values())
        labels = list(data.keys())
        return cls(values, labels=labels, **kwargs)

    def __repr__(self):
        return f'BarChart({self.bar_count} bars)'

    def animate_values(self, new_values, start=0, end=1, easing=easings.smooth):
        """Animate bars to new values over [start, end]."""
        max_val = max(abs(v) for v in new_values) if new_values else 1
        dur = end - start
        if dur <= 0:
            dur = 1
        for bar, new_val in zip(self._bars, new_values):
            old_h = bar.height.at_time(start)
            new_h = abs(new_val) / max_val * self._height * 0.85
            old_y = bar.y.at_time(start)
            new_y = self._y + self._height - new_h if new_val >= 0 else self._y + self._height
            bar.height.set(start, end, _lerp(start, dur, old_h, new_h, easing), stay=True)
            bar.y.set(start, end, _lerp(start, dur, old_y, new_y, easing), stay=True)
        self.values = new_values
        return self

    def set_bar_color(self, index, color, start=0, end=None, easing=easings.smooth):
        """Change the color of a specific bar."""
        if index < 0 or index >= len(self._bars):
            return self
        bar = self._bars[index]
        if end is None:
            bar.styling.fill = attributes.Color(start, color)
        else:
            bar.styling.fill.interpolate(attributes.Color(start, color), start, end, easing=easing)
        return self

    def set_bar_colors(self, colors, start=0):
        """Change all bar colors at once."""
        for i, color in enumerate(colors):
            if i < len(self._bars):
                self._bars[i].styling.fill = attributes.Color(start, color)
        return self

    def get_bar(self, index):
        """Return the bar VObject at the given index."""
        return self._bars[index]

    def get_bars(self, start=None, end=None):
        """Return a VCollection of bars, optionally sliced by index range."""
        bars = self._bars[start:end]
        return VCollection(*bars)

    def highlight_bar(self, index, color='#FFFF00', start=0, end=None, opacity=None):
        """Highlight a specific bar by changing its fill color.

        Parameters
        ----------
        index:
            Bar index (0-based).
        color:
            Target fill color for the bar.
        start:
            Time at which the highlight begins.
        end:
            Time at which the color transition ends.  ``None`` means
            the color is set instantly at *start*.
        opacity:
            If provided, also set the bar's fill opacity.

        Returns
        -------
        self
        """
        n = len(self._bars)
        if index < -n or index >= n:
            raise IndexError(f"bar index {index} out of range for chart with {n} bars")
        bar = self._bars[index]
        if end is None:
            bar.styling.fill = attributes.Color(start, color)
        else:
            bar.styling.fill.interpolate(attributes.Color(start, color), start, end)
        if opacity is not None:
            if end is None:
                bar.styling.fill_opacity.set_onward(start, opacity)
            else:
                bar.styling.fill_opacity.move_to(start, end, opacity)
        return self

    def get_bar_by_label(self, label):
        """Return the bar (Rectangle) matching the given label text, or None."""
        for i, lbl in enumerate(self._labels):
            if lbl is not None and lbl.text.at_time(0) == label:
                return self._bars[i]
        return None

    def add_value_labels(self, fmt='{:.0f}', offset=10, font_size=20, creation=0):
        """Add text labels showing each bar's value above (or below) the bar."""
        for bar, val in zip(self._bars, self.values):
            _, by, _, bh = bar.bbox(creation)
            lx = bar.center(creation)[0]
            ly = by - offset if val >= 0 else by + bh + offset + font_size
            label_text = fmt.format(val)
            label = Text(text=label_text, font_size=font_size, x=lx, y=ly,
                         creation=creation, fill='#fff', text_anchor='middle',
                         stroke_width=0)
            self.objects.append(label)
        return self

    def grow_from_zero(self, start=0, end=1, easing=easings.smooth, stagger=True, delay=0.1):
        """Animate bars growing up from zero height at the baseline."""
        n = len(self._bars)
        for i, bar in enumerate(self._bars):
            if stagger and n > 1:
                bar_start = start + i * delay
                bar_end = bar_start + (end - start - (n - 1) * delay)
                bar_end = max(bar_end, bar_start + 0.01)
            else:
                bar_start, bar_end = start, end
            bar.grow_from_edge('bottom', bar_start, bar_end, easing=easing)
        return self

    def get_max_bar(self) -> 'Rectangle | None':
        """Return the bar Rectangle with the maximum value, or None if no bars."""
        return self._bar_by_extreme(max)

    def get_min_bar(self) -> 'Rectangle | None':
        """Return the bar Rectangle with the minimum value, or None if no bars."""
        return self._bar_by_extreme(min)

    def _bar_by_extreme(self, func) -> 'Rectangle | None':
        if not self._bars:
            return None
        idx = func(range(len(self.values)), key=lambda i: self.values[i])
        return self._bars[idx]

    def sort_bars(self, key=None, reverse=False, start=0, end=1, easing=easings.smooth):
        """Animate reordering bars by value (or custom key function).

        Parameters
        ----------
        key:
            A function ``key(value) -> sort_key``.  If *None*, bars are sorted
            by their numeric value.
        reverse:
            If *True*, sort in descending order.
        start, end:
            Animation time range for the reordering animation.
        easing:
            Easing function for the slide animation.

        Returns
        -------
        self
        """
        if len(self._bars) <= 1:
            return self
        if key is None:
            key = lambda v: v
        # Build (sort_key, original_index) pairs and sort
        indexed = [(key(val), i) for i, val in enumerate(self.values)]
        indexed.sort(key=lambda x: x[0], reverse=reverse)
        # Get current x positions of each bar at start time
        old_xs = [bar.x.at_time(start) for bar in self._bars]
        # Compute new positions: bar at indexed[new_pos][1] should move to old_xs[new_pos]
        dur = end - start
        if dur <= 0:
            return self
        for new_pos, (_, old_idx) in enumerate(indexed):
            if new_pos == old_idx:
                continue
            bar = self._bars[old_idx]
            target_x = old_xs[new_pos]
            current_x = old_xs[old_idx]
            dx = target_x - current_x
            bar.shift(dx=dx, dy=0, start=start, end=end, easing=easing)
            # Also move the associated label if it exists
            lbl = self._labels[old_idx]
            if lbl is not None:
                lbl.shift(dx=dx, dy=0, start=start, end=end, easing=easing)
        # Reorder internal lists to match new order
        new_order = [orig_idx for _, orig_idx in indexed]
        self._bars = [self._bars[i] for i in new_order]
        self._labels = [self._labels[i] for i in new_order]
        self.values = [self.values[i] for i in new_order]
        return self

    def add_bar(self, value, label=None, start=0, end=None):
        """Add a new bar to the right side of the chart.

        Parameters
        ----------
        value:
            Numeric value for the new bar.
        label:
            Optional label string displayed below the bar.
        start:
            Time at which the bar appears (or animation begins).
        end:
            If provided, the bar animates growing from height 0 over
            ``[start, end]``.  If ``None``, the bar appears instantly.

        Returns
        -------
        self
        """
        n = len(self._bars)
        all_vals = list(self.values) + [value]
        max_val = max(abs(v) for v in all_vals) if all_vals else 1
        # Recompute bar layout for n+1 bars
        new_n = n + 1
        bar_width = self._width / new_n
        inner_width = bar_width * (1 - self._bar_spacing)
        bar_h = abs(value) / max_val * self._height * 0.85
        bx = self._x + n * bar_width + (bar_width - inner_width) / 2
        by = self._y + self._height - bar_h if value >= 0 else self._y + self._height
        color = self._colors[n % len(self._colors)]
        bar = Rectangle(inner_width, bar_h, x=bx, y=by,
                        creation=start, z=self._z,
                        fill=color, fill_opacity=0.8, stroke_width=0)
        if end is not None:
            # Animate: start at zero height at baseline, grow to full
            bar.height.set_onward(start, 0)
            bar.y.set_onward(start, self._y + self._height)
            dur = end - start
            if dur > 0:
                bar.height.set(start, end,
                    _lerp(start, dur, 0, bar_h, easings.smooth), stay=True)
                bar.y.set(start, end,
                    _lerp(start, dur, self._y + self._height, by, easings.smooth),
                    stay=True)
        self.objects.append(bar)
        self._bars.append(bar)
        self.values = all_vals
        self.bar_count = new_n
        # Label
        if label is not None:
            lbl = Text(text=str(label),
                       x=bx + inner_width / 2,
                       y=self._y + self._height + 24,
                       font_size=14, text_anchor='middle',
                       creation=start, z=self._z,
                       fill='#aaa', stroke_width=0)
            self.objects.append(lbl)
            self._labels.append(lbl)
        else:
            self._labels.append(None)
        return self

    def remove_bar(self, index, start=0, end=None):
        """Remove a bar by index.

        Parameters
        ----------
        index:
            Index of the bar to remove (0-based).
        start:
            Time at which the removal begins.
        end:
            If provided, the bar shrinks to zero height over
            ``[start, end]`` before being removed.  If ``None``, the
            bar is removed instantly.

        Returns
        -------
        self
        """
        n = len(self._bars)
        if index < -n or index >= n:
            raise IndexError(f"bar index {index} out of range for chart with {n} bars")
        if index < 0:
            index += n
        bar = self._bars[index]
        lbl = self._labels[index]
        if end is not None:
            dur = end - start
            if dur > 0:
                # Animate shrinking to zero height at baseline
                _oh = bar.height.at_time(start)
                _oy = bar.y.at_time(start)
                _by = self._y + self._height
                bar.height.set(start, end,
                    _lerp(start, dur, _oh, 0, easings.smooth), stay=True)
                bar.y.set(start, end,
                    _lerp(start, dur, _oy, _by, easings.smooth), stay=True)
            # Hide bar and label after animation
            bar._hide_from(end)
            if lbl is not None:
                lbl._hide_from(end)
        else:
            bar._hide_from(start)
            if lbl is not None:
                lbl._hide_from(start)
        # Remove from tracking lists
        self._bars.pop(index)
        self._labels.pop(index)
        self.values = list(self.values)
        self.values.pop(index)
        self.bar_count = len(self._bars)
        # Shift remaining bars left to fill gap
        if index < len(self._bars):
            new_n = len(self._bars)
            if new_n > 0:
                bar_width = self._width / new_n
                inner_width = bar_width * (1 - self._bar_spacing)
                shift_time = end if end is not None else start
                for i in range(index, len(self._bars)):
                    target_x = self._x + i * bar_width + (bar_width - inner_width) / 2
                    self._bars[i].x.set_onward(shift_time, target_x)
                    if self._labels[i] is not None:
                        self._labels[i].x.set_onward(shift_time, target_x + inner_width / 2)
        return self

    def animate_sort(self, key=None, reverse=False, start=0, end=1, easing=None):
        """Smoothly animate bars sliding into sorted order.

        Like :meth:`sort_bars`, but animates bar positions with ``move_to``
        for smooth interpolation.  Labels are moved alongside their bars.

        Parameters
        ----------
        key:
            A function ``key(value) -> sort_key``.  If *None*, bars are
            sorted by their numeric value.
        reverse:
            If *True*, sort in descending order.
        start, end:
            Animation time range.
        easing:
            Easing function for the animation.  Defaults to
            ``easings.smooth``.

        Returns
        -------
        self
        """
        if easing is None:
            easing = easings.smooth
        if len(self._bars) <= 1:
            return self
        if key is None:
            key = lambda v: v
        indexed = [(key(val), i) for i, val in enumerate(self.values)]
        indexed.sort(key=lambda x: x[0], reverse=reverse)
        # Record current x positions at start time
        old_xs = [bar.x.at_time(start) for bar in self._bars]
        dur = end - start
        if dur <= 0:
            return self
        for new_pos, (_, old_idx) in enumerate(indexed):
            if new_pos == old_idx:
                continue
            bar = self._bars[old_idx]
            target_x = old_xs[new_pos]
            current_x = old_xs[old_idx]
            # Animate bar x position smoothly
            bar.x.set(start, end,
                _lerp(start, dur, current_x, target_x, easing), stay=True)
            # Also animate label if present
            lbl = self._labels[old_idx]
            if lbl is not None:
                lbl_x = lbl.x.at_time(start)
                lbl.x.set(start, end,
                    _lerp(start, dur, lbl_x, lbl_x + target_x - current_x, easing),
                    stay=True)
        # Reorder internal lists to match new order
        new_order = [orig_idx for _, orig_idx in indexed]
        self._bars = [self._bars[i] for i in new_order]
        self._labels = [self._labels[i] for i in new_order]
        self.values = [self.values[i] for i in new_order]
        return self


class Table(VCollection):
    """Table for displaying tabular data with optional row/column labels.

    data: 2D list of values (data[row][col]).
    row_labels/col_labels: optional label lists.
    """
    def __init__(self, data, row_labels=None, col_labels=None,
                 x=120, y=60, cell_width=160, cell_height=60,
                 font_size=24, creation: float = 0, z: float = 0, **styling_kwargs):
        rows = len(data)
        cols = len(data[0]) if data else 0
        x_off = cell_width if row_labels else 0
        y_off = cell_height if col_labels else 0
        total_w = cols * cell_width + x_off
        total_h = rows * cell_height + y_off
        line_kw = {'stroke': '#fff', 'stroke_width': 2} | styling_kwargs
        objects: list = []

        for r in range(rows + 1):
            ly = y + y_off + r * cell_height
            objects.append(Line(x1=x, y1=ly, x2=x + total_w, y2=ly,
                                creation=creation, z=z, **line_kw))
        for c in range(cols + 1):
            lx = x + x_off + c * cell_width
            objects.append(Line(x1=lx, y1=y + (y_off if not col_labels else 0),
                                x2=lx, y2=y + total_h,
                                creation=creation, z=z, **line_kw))

        self.entries = []
        for r in range(rows):
            row_entries = []
            for c in range(cols):
                cx = x + x_off + c * cell_width + cell_width / 2
                cy = y + y_off + r * cell_height + cell_height / 2 + font_size * TEXT_Y_OFFSET
                t = Text(text=str(data[r][c]), x=cx, y=cy,
                         font_size=font_size, text_anchor='middle',
                         creation=creation, z=z, fill='#fff', stroke_width=0)
                objects.append(t)
                row_entries.append(t)
            self.entries.append(row_entries)

        if row_labels:
            for r, label in enumerate(row_labels):
                cx = x + cell_width / 2
                cy = y + y_off + r * cell_height + cell_height / 2 + font_size * TEXT_Y_OFFSET
                objects.append(Text(text=str(label), x=cx, y=cy,
                                   font_size=font_size, text_anchor='middle',
                                   creation=creation, z=z, fill='#FFFF00', stroke_width=0))
        if col_labels:
            for c, label in enumerate(col_labels):
                cx = x + x_off + c * cell_width + cell_width / 2
                cy = y + cell_height / 2 + font_size * TEXT_Y_OFFSET
                objects.append(Text(text=str(label), x=cx, y=cy,
                                   font_size=font_size, text_anchor='middle',
                                   creation=creation, z=z, fill='#FFFF00', stroke_width=0))

        super().__init__(*objects, creation=creation, z=z)
        self.rows, self.cols = rows, cols
        self._table_x = x
        self._table_y = y
        self._cell_width = cell_width
        self._cell_height = cell_height
        self._x_off = x_off
        self._y_off = y_off
        self._font_size = font_size
        self._line_kw = line_kw
        self._z = z

    def get_entry(self, row, col):
        """Return the Text object at (row, col) for animation."""
        return self.entries[row][col]

    def get_cell(self, row, col):
        """Alias for :meth:`get_entry`."""
        return self.get_entry(row, col)

    def get_cell_rect(self, row, col, padding=2, **kwargs):
        """Return a Rectangle covering the cell at (row, col).

        The Rectangle is not added to the table; callers can animate or add it
        to a canvas independently.  padding shrinks the rect inward on all sides.
        """
        rx = self._table_x + self._x_off + col * self._cell_width + padding
        ry = self._table_y + self._y_off + row * self._cell_height + padding
        w = self._cell_width - 2 * padding
        h = self._cell_height - 2 * padding
        kw = {'fill': '#FFFF00', 'fill_opacity': 0.15, 'stroke_width': 0} | kwargs
        return Rectangle(w, h, x=rx, y=ry, **kw)

    def get_row(self, row):
        """Return a VCollection of all Text objects in the given row."""
        return VCollection(*self.entries[row])

    def get_column(self, col):
        """Return a VCollection of all Text objects in the given column."""
        return VCollection(*(row[col] for row in self.entries if col < len(row)))

    def highlight_cell(self, row, col, start=0, end=1, color='#FFFF00', easing=easings.there_and_back):
        """Flash-highlight a single cell's text."""
        self.entries[row][col].flash(start, end, color=color, easing=easing)
        return self

    def highlight_row(self, row_idx, start=0, end=1, color='#FFFF00', opacity=0.3, easing=None):
        """Highlight all cells in a row by setting their fill color.

        The highlight fades in at *start* and fades out at *end* using the
        fill opacity.  If *easing* is ``None``, ``easings.there_and_back``
        is used so the highlight peaks at the midpoint and fades out by *end*.

        Parameters
        ----------
        row_idx:
            Row index (0-based).
        start:
            Time at which the highlight begins.
        end:
            Time at which the highlight ends.
        color:
            Fill color for the highlight.
        opacity:
            Peak fill opacity for the highlight.
        easing:
            Easing function.  If ``None``, ``easings.there_and_back`` is used.

        Returns
        -------
        self
        """
        if easing is None:
            easing = easings.there_and_back
        for entry in self.entries[row_idx]:
            entry.set_fill(color=color, start=start)
            dur = end - start
            if dur > 0:
                entry.styling.fill_opacity.set(start, end,
                    _ramp(start, dur, opacity, easing))
        return self

    def highlight_column(self, col, start=0, end=1, color='#FFFF00', easing=easings.there_and_back):
        """Flash-highlight all cells in a column."""
        for row in self.entries:
            if col < len(row):
                row[col].flash(start, end, color=color, easing=easing)
        return self

    def highlight_cells(self, cells, start=0, end=1, color='#FFFF00', easing=easings.there_and_back):
        """Flash-highlight multiple cells. cells: list of (row, col) tuples."""
        for r, c in cells:
            self.entries[r][c].flash(start, end, color=color, easing=easing)
        return self

    def set_cell_value(self, row, col, new_value, start: float = 0):
        """Change the text of a cell at the given time."""
        self.entries[row][col].text.set_onward(start, str(new_value))
        return self

    def highlight_range(self, start_row, start_col, end_row, end_col,
                        start=0, end=1, color='#FFD700', easing=easings.there_and_back):
        """Highlight a rectangular range of cells."""
        for r in range(start_row, end_row + 1):
            for c in range(start_col, end_col + 1):
                if r < self.rows and c < self.cols:
                    self.entries[r][c].flash(start, end, color=color, easing=easing)
        return self

    def set_cell_values(self, updates, start=0):
        """Batch update multiple cell values.

        updates: dict of {(row, col): value, ...}
        """
        for (r, c), value in updates.items():
            self.set_cell_value(r, c, str(value), start=start)
        return self

    def sort_by_column(self, col, start=0, end=1, reverse=False, easing=easings.smooth):
        """Animate rows sliding to sorted positions based on column values."""
        # Get text values from the column
        values = [(self.entries[r][col].text.at_time(start), r) for r in range(len(self.entries))]
        values.sort(key=lambda x: x[0], reverse=reverse)
        # Get current y positions of each row (using first cell as reference)
        ys = [self.entries[r][0].y.at_time(start) for r in range(len(self.entries))]
        # Animate each row to its new y position
        for new_pos, (_, old_row) in enumerate(values):
            if new_pos != old_row:
                dy = ys[new_pos] - ys[old_row]
                for entry in self.entries[old_row]:
                    entry.shift(dx=0, dy=dy, start=start, end=end, easing=easing)
        return self

    def transpose(self, start=0, end=None, easing=None):
        """Transpose the table so rows become columns and vice versa.

        Cell at ``(row, col)`` slides to position ``(col, row)``.  If
        *end* is ``None`` the rearrangement is instant; otherwise cells
        animate over ``[start, end]``.

        Only works when the current ``rows`` and ``cols`` fit within each
        other's dimensions (i.e. the table has enough rows and columns
        that transposed positions exist).

        Parameters
        ----------
        start:
            Animation start time.
        end:
            Animation end time.  ``None`` for instant rearrangement.
        easing:
            Easing function.  Defaults to ``easings.smooth`` if ``None``.

        Returns
        -------
        self
        """
        if easing is None:
            easing = easings.smooth
        x = self._table_x
        y = self._table_y
        x_off = self._x_off
        y_off = self._y_off
        cw = self._cell_width
        ch = self._cell_height
        fs = self._font_size

        # Animate each cell to its transposed position
        for r in range(self.rows):
            for c in range(self.cols):
                entry = self.entries[r][c]
                # Target position: swap row and col
                new_cx = x + x_off + r * cw + cw / 2
                new_cy = y + y_off + c * ch + ch / 2 + fs * TEXT_Y_OFFSET
                entry.center_to_pos(posx=new_cx, posy=new_cy,
                                    start=start, end=end, easing=easing)

        # Rebuild entries grid as transposed
        new_entries = []
        for c in range(self.cols):
            new_row = []
            for r in range(self.rows):
                new_row.append(self.entries[r][c])
            new_entries.append(new_row)
        self.entries = new_entries
        self.rows, self.cols = self.cols, self.rows
        return self

    def animate_cell_values(self, data, start=0, end=1, easing=None):
        """Animate table cells changing to new values.

        For each cell, the text transitions from its current value to the
        corresponding value in *data*.  Numeric values are interpolated
        smoothly (like CountAnimation); non-numeric text is swapped at the
        midpoint of the animation.

        Parameters
        ----------
        data:
            A 2D list matching the table dimensions.  ``data[row][col]``
            gives the target value for the cell at ``(row, col)``.
        start:
            Animation start time.
        end:
            Animation end time.
        easing:
            Easing function for the transition.  Defaults to
            ``easings.smooth`` if ``None``.

        Returns
        -------
        self
        """
        if easing is None:
            easing = easings.smooth
        dur = end - start
        for r, row in enumerate(data):
            for c, new_val in enumerate(row):
                if r >= self.rows or c >= self.cols:
                    continue
                entry = self.entries[r][c]
                old_text = entry.text.at_time(start)
                new_text = str(new_val)
                # Try numeric interpolation
                try:
                    old_num = float(old_text)
                    new_num = float(new_text)
                    # Detect if we should use integer formatting
                    is_int = ('.' not in old_text and '.' not in new_text
                              and old_num == int(old_num) and new_num == int(new_num))
                    if dur <= 0:
                        entry.text.set_onward(start, new_text)
                    else:
                        if is_int:
                            entry.text.set(start, end,
                                lambda t, _s=start, _d=dur, _ov=old_num, _nv=new_num, _e=easing:
                                    str(int(round(_ov + (_nv - _ov) * _e((t - _s) / _d)))),
                                stay=True)
                        else:
                            # Preserve decimal places from the new value
                            dot_pos = new_text.find('.')
                            decimals = len(new_text) - dot_pos - 1 if dot_pos >= 0 else 1
                            fmt = f'{{:.{decimals}f}}'
                            entry.text.set(start, end,
                                lambda t, _s=start, _d=dur, _ov=old_num, _nv=new_num,
                                       _e=easing, _fmt=fmt:
                                    _fmt.format(_ov + (_nv - _ov) * _e((t - _s) / _d)),
                                stay=True)
                except (ValueError, TypeError):
                    # Non-numeric: swap at midpoint
                    if dur <= 0:
                        entry.text.set_onward(start, new_text)
                    else:
                        mid = start + dur / 2
                        entry.text.set_onward(mid, new_text)
        return self

    def animate_cells(self, cells, method_name='flash', start=0, delay=0.15, **kwargs):
        """Apply an animation method to specific cells with a stagger delay.

        Parameters
        ----------
        cells:
            List of (row, col) tuples identifying the cells to animate.
        method_name:
            Name of the animation method to call on each cell's Text object
            (e.g. ``'flash'``, ``'indicate'``, ``'wiggle'``).
        start:
            Start time for the first cell's animation.
        delay:
            Time offset between successive cells.
        **kwargs:
            Extra keyword arguments forwarded to each animation method call.

        Returns
        -------
        self
        """
        for i, (r, c) in enumerate(cells):
            entry = self.entries[r][c]
            method = getattr(entry, method_name)
            t = start + i * delay
            method(start=t, **kwargs)
        return self

    @classmethod
    def from_dict(cls, data, **kwargs):
        """Create a Table from a Python dict.

        Keys become column headers and values become row data.  If the values
        are lists, each element becomes a separate row.  Scalar values are
        wrapped in a single-element list.

        Parameters
        ----------
        data:
            A dict mapping column header strings to values or lists of values.
        **kwargs:
            Extra keyword arguments forwarded to the Table constructor
            (e.g. ``x``, ``y``, ``cell_width``, ``font_size``).

        Returns
        -------
        Table

        Examples
        --------
        >>> t = Table.from_dict({'Name': ['Alice', 'Bob'], 'Age': [30, 25]})
        >>> t.rows  # 2
        >>> t.cols  # 2
        """
        headers = list(data.keys())
        # Normalize all values to lists
        columns = []
        for v in data.values():
            columns.append(v if isinstance(v, (list, tuple)) else [v])
        n_rows = max(len(col) for col in columns) if columns else 0
        # Build the 2D data grid (rows x cols)
        grid = []
        for r in range(n_rows):
            row = []
            for col in columns:
                row.append(col[r] if r < len(col) else '')
            grid.append(row)
        return cls(grid, col_labels=headers, **kwargs)

    def add_row(self, values, start=0, animate=True):
        """Append a new row to the bottom of the table.

        Creates Text objects for each cell value, adds a horizontal
        separator line, and extends the existing vertical lines downward.
        If *animate* is True the new elements fade in at *start*.

        Parameters
        ----------
        values:
            Sequence of cell values (one per column).  Extra values are
            silently ignored; missing columns get an empty string.
        start:
            Time at which the new row appears.
        animate:
            If True, new elements fade in over 0.5 seconds starting at
            *start*.

        Returns
        -------
        self
        """
        x = self._table_x
        y_off = self._y_off
        cw = self._cell_width
        ch = self._cell_height
        x_off = self._x_off
        fs = self._font_size
        z = self._z

        new_row_idx = self.rows
        row_y = self._table_y + y_off + new_row_idx * ch

        # Horizontal line at the bottom of the new row
        total_w = self.cols * cw + x_off
        new_line_y = row_y + ch
        h_line = Line(x1=x, y1=new_line_y, x2=x + total_w, y2=new_line_y,
                      creation=start, z=z, **self._line_kw)

        # Extend existing vertical lines downward by one cell height
        # Vertical lines were created with y2 = y + total_h, so we need to
        # extend them.  Instead, we just lengthen them.
        for obj in self.objects:
            if isinstance(obj, Line):
                p1 = obj.p1.at_time(start)
                p2 = obj.p2.at_time(start)
                # Vertical line: same x for p1 and p2, goes from top to bottom
                if abs(p1[0] - p2[0]) < 0.1 and p2[1] > p1[1]:
                    old_y2 = p2[1]
                    expected_bottom = self._table_y + y_off + self.rows * ch
                    if abs(old_y2 - expected_bottom) < 1:
                        obj.p2.add_onward(start, (p2[0], old_y2 + ch))

        # Create text entries for the new row
        new_entries = []
        new_objects = [h_line]
        for c in range(self.cols):
            val = values[c] if c < len(values) else ''
            cx = x + x_off + c * cw + cw / 2
            cy = row_y + ch / 2 + fs * TEXT_Y_OFFSET
            t = Text(text=str(val), x=cx, y=cy,
                     font_size=fs, text_anchor='middle',
                     creation=start, z=z, fill='#fff', stroke_width=0)
            new_entries.append(t)
            new_objects.append(t)

        if animate:
            for obj in new_objects:
                obj.fadein(start=start, end=start + 0.5)

        self.entries.append(new_entries)
        self.rows += 1
        for obj in new_objects:
            self.objects.append(obj)
        return self

    def add_column(self, values, start=0, animate=True):
        """Append a new column to the right of the table.

        Creates Text objects for each cell value, adds a vertical
        separator line, and extends the existing horizontal lines to the
        right.  If *animate* is True the new elements fade in at *start*.

        Parameters
        ----------
        values:
            Sequence of cell values (one per row).  Extra values are
            silently ignored; missing rows get an empty string.
        start:
            Time at which the new column appears.
        animate:
            If True, new elements fade in over 0.5 seconds starting at
            *start*.

        Returns
        -------
        self
        """
        x = self._table_x
        y_off = self._y_off
        cw = self._cell_width
        ch = self._cell_height
        x_off = self._x_off
        fs = self._font_size
        z = self._z

        new_col_idx = self.cols
        col_x = x + x_off + new_col_idx * cw

        # Vertical line at the right edge of the new column
        total_h = self.rows * ch + y_off
        v_line = Line(x1=col_x + cw, y1=self._table_y + y_off,
                      x2=col_x + cw, y2=self._table_y + total_h,
                      creation=start, z=z, **self._line_kw)

        # Extend existing horizontal lines to the right by one cell width
        for obj in self.objects:
            if isinstance(obj, Line):
                p1 = obj.p1.at_time(start)
                p2 = obj.p2.at_time(start)
                # Horizontal line: same y for p1 and p2
                if abs(p1[1] - p2[1]) < 0.1 and p2[0] > p1[0]:
                    old_x2 = p2[0]
                    expected_right = x + self.cols * cw + x_off
                    if abs(old_x2 - expected_right) < 1:
                        obj.p2.add_onward(start, (old_x2 + cw, p2[1]))

        # Create text entries for the new column
        new_objects = [v_line]
        for r in range(self.rows):
            val = values[r] if r < len(values) else ''
            cx = col_x + cw / 2
            cy = self._table_y + y_off + r * ch + ch / 2 + fs * TEXT_Y_OFFSET
            t = Text(text=str(val), x=cx, y=cy,
                     font_size=fs, text_anchor='middle',
                     creation=start, z=z, fill='#fff', stroke_width=0)
            # Extend the row's entry list
            if r < len(self.entries):
                self.entries[r].append(t)
            new_objects.append(t)

        if animate:
            for obj in new_objects:
                obj.fadein(start=start, end=start + 0.5)

        self.cols += 1
        for obj in new_objects:
            self.objects.append(obj)
        return self

    def __repr__(self):
        return f'Table({self.rows}x{self.cols})'


class DynamicObject(VObject):
    """VObject whose SVG is regenerated each frame by calling func(time).
    func should return a VObject. Useful for reactive/always-redraw patterns."""
    def __init__(self, func, creation: float = 0, z: float = 0):
        super().__init__(creation=creation, z=z)
        self._func = func
        self._cache = [None, None]  # [time, result]
        self.styling = style.Styling({}, creation=creation)

    def _eval(self, time):
        """Evaluate func(time) with per-frame caching."""
        if self._cache[0] == time:
            return self._cache[1]
        result = self._func(time)
        self._cache[0] = time
        self._cache[1] = result
        return result

    def to_svg(self, time):
        return self._eval(time).to_svg(time)

    def path(self, time):
        obj = self._eval(time)
        return obj.path(time) if hasattr(obj, 'path') else ''

    def bbox(self, time):
        return self._eval(time).bbox(time)


class Matrix(VCollection):
    """Display a mathematical matrix with square bracket delimiters.

    data: 2D list of values.
    x, y: position of the matrix center.
    """
    def __init__(self, data, x=960, y=540, font_size=36, h_spacing=80, v_spacing=50,
                 creation: float = 0, z: float = 0, **styling_kwargs):
        if not data or not data[0]:
            raise ValueError('Matrix requires a non-empty 2D list of data')
        rows = len(data)
        cols = len(data[0])
        total_w = (cols - 1) * h_spacing
        total_h = (rows - 1) * v_spacing
        bracket_pad = 20
        bracket_w = 8

        objects: list = []
        self.entries = []

        for r in range(rows):
            row_entries = []
            for c in range(cols):
                tx = x - total_w / 2 + c * h_spacing
                ty = y - total_h / 2 + r * v_spacing + font_size * TEXT_Y_OFFSET
                t = Text(text=str(data[r][c]), x=tx, y=ty, font_size=font_size,
                         text_anchor='middle', creation=creation, z=z,
                         fill='#fff', stroke_width=0)
                objects.append(t)
                row_entries.append(t)
            self.entries.append(row_entries)

        # Left bracket
        lx = x - total_w / 2 - bracket_pad
        bracket_kw = {'stroke': '#fff', 'stroke_width': 3, 'fill_opacity': 0} | styling_kwargs
        objects.append(Lines(
            (lx + bracket_w, y - total_h / 2 - bracket_pad),
            (lx, y - total_h / 2 - bracket_pad),
            (lx, y + total_h / 2 + bracket_pad),
            (lx + bracket_w, y + total_h / 2 + bracket_pad),
            creation=creation, z=z, **bracket_kw))

        # Right bracket
        rx = x + total_w / 2 + bracket_pad
        objects.append(Lines(
            (rx - bracket_w, y - total_h / 2 - bracket_pad),
            (rx, y - total_h / 2 - bracket_pad),
            (rx, y + total_h / 2 + bracket_pad),
            (rx - bracket_w, y + total_h / 2 + bracket_pad),
            creation=creation, z=z, **bracket_kw))

        super().__init__(*objects, creation=creation, z=z)
        self.rows, self.cols = rows, cols

    def get_entry(self, row, col):
        """Return the Text object at (row, col) for animation."""
        return self.entries[row][col]

    def get_row(self, row):
        """Return a VCollection of all Text objects in the given row."""
        return VCollection(*self.entries[row])

    def get_column(self, col):
        """Return a VCollection of all Text objects in the given column."""
        return VCollection(*(row[col] for row in self.entries if col < len(row)))

    def highlight_entry(self, row, col, start=0, end=1, color='#FFD700'):
        """Flash-highlight a single matrix entry."""
        entry = self.get_entry(row, col)
        entry.flash_color(color, start=start, duration=end - start)
        return self

    def highlight_row(self, row, start=0, end=1, color='#FFD700'):
        """Flash-highlight all entries in a row."""
        for entry in self.entries[row]:
            entry.flash_color(color, start=start, duration=end - start)
        return self

    def highlight_column(self, col, start=0, end=1, color='#FFD700'):
        """Flash-highlight all entries in a column."""
        for row in self.entries:
            if col < len(row):
                row[col].flash_color(color, start=start, duration=end - start)
        return self


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
        return Text(text=content, x=g('x', ORIGIN[0]) + tx, y=g('y', ORIGIN[1]) + ty,
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

from vectormation._ui import (  # noqa: E402 -- UI components
    Title, Variable, Underline, Code, Label, LabeledArrow,
    Callout, DimensionLine, Tooltip, TextBox, Bracket, IconGrid,
    SpeechBubble, Badge, Divider, Checklist, Stepper, TagCloud,
    StatusIndicator, Meter, Breadcrumb, Countdown, Filmstrip,
    RoundedCornerPolygon,
)



def brace_between_points(p1, p2, direction=None, label=None, buff=0, depth=18,
                         creation=0, z=0, **styling_kwargs):
    """Create a Brace between two arbitrary points.

    If direction is None, it is inferred perpendicular to the line p1→p2.
    Returns a Brace (VCollection).
    """
    from vectormation._shapes import Rectangle
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

    return Brace(dummy, direction=direction, label=label, buff=buff,
                 depth=depth, creation=creation, z=z, **styling_kwargs)


class ArrowVectorField(VCollection):
    """Vector field visualization using arrows.

    func: callable(x, y) -> (vx, vy) returning the vector at (x, y).
    x_range, y_range: (min, max, step) in pixel coordinates.
    """
    def __init__(self, func, x_range=(60, 1860, 120), y_range=(60, 1020, 120),
                 max_length=80, creation=0, z=0, **styling_kwargs):
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


class StreamLines(VCollection):
    """Animated flow lines for a vector field.

    func: callable(x, y) -> (vx, vy).
    Draws streamlines by integrating the field using Euler steps.
    """
    def __init__(self, func, x_range=(60, 1860, 200), y_range=(60, 1020, 200),
                 n_steps=40, step_size=5, creation=0, z=0, **styling_kwargs):
        from vectormation._shapes import Lines
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


class PolarAxes(VCollection):
    """Polar coordinate system with radial gridlines and angle markers.

    r_range: (min, max) radius in abstract units.
    n_rings: number of concentric rings.
    n_sectors: number of angular sectors (lines from center).
    """
    def __init__(self, cx=960, cy=540, max_radius=400, r_range=(0, 5),
                 n_rings=5, n_sectors=12, creation=0, z=0):
        from vectormation._shapes import Circle, Line, Text
        objects = []
        self._cx, self._cy = cx, cy
        self._max_radius = max_radius
        self._r_max = r_range[1]
        self._r_min = r_range[0]
        r_span = r_range[1] - r_range[0]
        px_per_unit = max_radius / r_span if r_span > 0 else 1

        # Concentric rings
        for i in range(1, max(n_rings, 1) + 1):
            r_val = r_range[0] + i * r_span / max(n_rings, 1)
            r_px = (r_val - r_range[0]) * px_per_unit
            ring = Circle(r=r_px, cx=cx, cy=cy, creation=creation, z=z,
                          stroke='#444', stroke_width=1, fill_opacity=0)
            objects.append(ring)
            label = Text(text=f'{r_val:g}', x=cx + r_px + 5, y=cy - 5,
                         font_size=14, creation=creation, z=z, fill='#666', stroke_width=0)
            objects.append(label)

        # Angular sector lines
        n_sectors = max(n_sectors, 1)
        for i in range(n_sectors):
            angle = math.tau * i / n_sectors
            ex = cx + max_radius * math.cos(angle)
            ey = cy - max_radius * math.sin(angle)
            line = Line(x1=cx, y1=cy, x2=ex, y2=ey,
                        creation=creation, z=z, stroke='#444', stroke_width=1)
            objects.append(line)
            # Angle label
            deg = round(360 * i / n_sectors)
            lx = cx + (max_radius + 20) * math.cos(angle)
            ly = cy - (max_radius + 20) * math.sin(angle)
            lbl = Text(text=f'{deg}\u00b0', x=lx, y=ly + 5,
                       font_size=14, text_anchor='middle',
                       creation=creation, z=z, fill='#888', stroke_width=0)
            objects.append(lbl)

        super().__init__(*objects, creation=creation, z=z)
        self._px_per_unit = px_per_unit

    def polar_to_point(self, r, theta_deg):
        """Convert (r, theta) to SVG pixel coordinates."""
        theta = math.radians(theta_deg)
        px = (r - self._r_min) * self._px_per_unit
        return (self._cx + px * math.cos(theta),
                self._cy - px * math.sin(theta))

    def plot_polar(self, func, theta_range=(0, 360), num_points=200,
                   creation=0, z=0, **styling_kwargs):
        """Plot r = func(theta_deg) on this polar axes."""
        from vectormation._shapes import Lines
        style_kw = {'stroke': '#58C4DD', 'stroke_width': 3, 'fill_opacity': 0} | styling_kwargs
        t0, t1 = theta_range
        num_points = max(1, num_points)
        pts = []
        for i in range(num_points + 1):
            theta = t0 + i * (t1 - t0) / num_points
            r = func(theta)
            pts.append(self.polar_to_point(r, theta))
        curve = Lines(*pts, creation=creation, z=z, **style_kw)
        self.objects.append(curve)
        return curve


from vectormation._diagrams import Tree as Tree  # noqa: E402,F811


def always_redraw(func, creation=0, z=0):
    """Convenience wrapper: create a DynamicObject from a callable.
    func(time) should return a VObject."""
    return DynamicObject(func, creation=creation, z=z)


from vectormation._diagrams import Stamp as Stamp  # noqa: E402,F811
from vectormation._diagrams import TimelineBar as TimelineBar  # noqa: E402,F811


class Legend(VCollection):
    """Chart legend with colored swatches and labels.

    items: list of (color, label) tuples.
    """
    def __init__(self, items, x=100, y=100, swatch_size=16, spacing=8,
                 font_size=16, direction='down', creation: float = 0, z: float = 0):
        from vectormation._shapes import Rectangle, Text
        objects = []
        horizontal = direction == 'right'
        cursor_x, cursor_y = x, y
        for color, label in items:
            swatch = Rectangle(swatch_size, swatch_size, x=cursor_x, y=cursor_y,
                               fill=color, fill_opacity=0.9, stroke_width=0,
                               creation=creation, z=z)
            txt = Text(text=label, x=cursor_x + swatch_size + spacing,
                       y=cursor_y + swatch_size * 0.75,
                       font_size=font_size, fill='#ccc', stroke_width=0,
                       creation=creation, z=z)
            objects.extend([swatch, txt])
            if horizontal:
                # estimate text width
                cursor_x += swatch_size + spacing + len(label) * font_size * CHAR_WIDTH_FACTOR + spacing * 2
            else:
                cursor_y += swatch_size + spacing
        super().__init__(*objects, creation=creation, z=z)


class RadarChart(VCollection):
    """Radar/spider chart visualization.

    values: list of numeric values (one per axis).
    labels: optional list of axis labels.
    max_val: maximum value for the chart (scales all values).
    """
    def __init__(self, values, labels=None, max_val=None, colors=None,
                 cx=960, cy=540, radius=250, font_size=16,
                 fill_opacity=0.3, creation: float = 0, z: float = 0):
        n = len(values)
        if n < 3:
            super().__init__(creation=creation, z=z)
            return
        if max_val is None:
            max_val = max(values) if values else 1
        if max_val == 0:
            max_val = 1
        if colors is None:
            colors = ['#58C4DD']
        objects = []
        # Draw concentric rings (grid)
        for level in range(1, 4):
            r = radius * level / 3
            ring = Circle(r=r, cx=cx, cy=cy, fill_opacity=0,
                          stroke='#444', stroke_width=1, creation=creation, z=z)
            objects.append(ring)
        # Draw axis lines
        angles = [i * math.tau / n - math.pi / 2 for i in range(n)]
        for angle in angles:
            lx = cx + radius * math.cos(angle)
            ly = cy + radius * math.sin(angle)
            line = Line(x1=cx, y1=cy, x2=lx, y2=ly,
                        stroke='#555', stroke_width=1, creation=creation, z=z)
            objects.append(line)
        # Draw data polygon
        points = []
        for i, val in enumerate(values):
            r = radius * min(val / max_val, 1)
            px = cx + r * math.cos(angles[i])
            py = cy + r * math.sin(angles[i])
            points.append((px, py))
        color = colors[0]
        data_poly = Polygon(*points, fill=color, fill_opacity=fill_opacity,
                            stroke=color, stroke_width=2, creation=creation, z=z + 0.1)
        objects.append(data_poly)
        # Draw data dots
        for px, py in points:
            dot = Dot(cx=px, cy=py, fill=color, creation=creation, z=z + 0.2)
            objects.append(dot)
        # Labels
        if labels:
            for i, label in enumerate(labels[:n]):
                lx = cx + (radius + 30) * math.cos(angles[i])
                ly = cy + (radius + 30) * math.sin(angles[i])
                anchor = 'middle'
                if math.cos(angles[i]) > 0.3:
                    anchor = 'start'
                elif math.cos(angles[i]) < -0.3:
                    anchor = 'end'
                txt = Text(text=label, x=lx, y=ly + font_size * TEXT_Y_OFFSET,
                           font_size=font_size, fill='#ccc', stroke_width=0,
                           text_anchor=anchor, creation=creation, z=z + 0.1)
                objects.append(txt)
        self._data_poly = data_poly
        super().__init__(*objects, creation=creation, z=z)


class ProgressBar(VCollection):
    """Animated progress bar that fills from left to right.

    width, height: dimensions of the bar.
    x, y: top-left corner position.
    bg_color: background track color.
    fill_color: fill bar color.
    """
    def __init__(self, width=400, height=30, x=760, y=520,
                 bg_color='#333', fill_color='#58C4DD',
                 corner_radius=6, creation: float = 0, z: float = 0):

        self._bar_width = width
        bg = RoundedRectangle(width, height, x=x, y=y, corner_radius=corner_radius,
                              fill=bg_color, fill_opacity=0.5, stroke_width=0, creation=creation, z=z)
        fill = RoundedRectangle(0.01, height, x=x, y=y, corner_radius=corner_radius,
                                fill=fill_color, fill_opacity=1, stroke_width=0, creation=creation, z=z + 0.1)
        self._fill = fill
        super().__init__(bg, fill, creation=creation, z=z)

    def set_progress(self, value, start=0, end=None, easing=easings.smooth):
        """Set progress (0 to 1). Animates if end is given."""
        target_w = max(0.01, self._bar_width * max(0, min(1, value)))
        if end is None:
            self._fill.width.set_onward(start, target_w)
        else:
            self._fill.width.move_to(start, end, target_w, easing=easing)
        return self

    def animate_to(self, value, start, end, easing=easings.smooth):
        """Animate progress to a target value (0-1)."""
        return self.set_progress(value, start, end, easing)

    def get_progress(self, time=0):
        """Return the current progress value (0-1) at the given time."""
        fill_w = self._fill.width.at_time(time)
        return fill_w / self._bar_width if self._bar_width else 0


from vectormation._diagrams import FlowChart as FlowChart  # noqa: E402,F811


class WaterfallChart(VCollection):
    """Waterfall chart showing cumulative effect of positive/negative values.

    values: list of numbers (positive = increase, negative = decrease).
    labels: optional list of labels for each bar.
    show_total: if True, adds a total bar at the end.
    """
    def __init__(self, values, labels=None, x=200, y=100,
                 width=800, height=400, bar_width=0.7,
                 pos_color='#83C167', neg_color='#FF6B6B', total_color='#58C4DD',
                 connector_color='#666', font_size=16,
                 show_total=True, creation: float = 0, z: float = 0):
        n = len(values)
        if n == 0:
            super().__init__(creation=creation, z=z)
            return
        # Compute cumulative running totals
        cumulative = [0.0]
        for v in values:
            cumulative.append(cumulative[-1] + v)
        all_vals = list(cumulative)
        if show_total:
            all_vals.append(cumulative[-1])
        n_bars = n + (1 if show_total else 0)
        vmin = min(all_vals + [0])
        vmax = max(all_vals + [0])
        vspan = vmax - vmin if vmax != vmin else 1
        # Axes geometry
        margin_left = 60
        margin_bottom = 50
        plot_w = width - margin_left
        plot_h = height - margin_bottom
        bar_step = plot_w / max(n_bars, 1)
        def _val_to_y(v):
            return y + plot_h - (v - vmin) / vspan * plot_h
        objects = []
        # Y-axis line
        y_axis = Line(x1=x + margin_left, y1=y, x2=x + margin_left, y2=y + plot_h,
                      stroke='#888', stroke_width=1, creation=creation, z=z)
        objects.append(y_axis)
        # Zero line
        zero_y = _val_to_y(0)
        zero_line = Line(x1=x + margin_left, y1=zero_y,
                         x2=x + width, y2=zero_y,
                         stroke='#555', stroke_width=1,
                         stroke_dasharray='4 3', creation=creation, z=z)
        objects.append(zero_line)
        def _bar_x(idx):
            return x + margin_left + idx * bar_step + bar_step * (1 - bar_width) / 2
        bw = bar_step * bar_width
        def _add_bar(idx, base_y, top_y, color, lbl_text, val_text):
            bx = _bar_x(idx)
            by_top = _val_to_y(max(base_y, top_y))
            bh = abs(_val_to_y(base_y) - _val_to_y(top_y))
            rect = Rectangle(width=bw, height=max(bh, 1), x=bx, y=by_top,
                              fill=color, fill_opacity=0.8, stroke=color, stroke_width=1,
                              creation=creation, z=z + 0.1)
            self._bars.append(rect)
            objects.append(rect)
            objects.append(Text(text=lbl_text, x=bx + bw / 2, y=y + plot_h + 20,
                                font_size=font_size, fill='#ccc', stroke_width=0,
                                text_anchor='middle', creation=creation, z=z + 0.2))
            objects.append(Text(text=val_text, x=bx + bw / 2, y=by_top - 5,
                                font_size=font_size - 2, fill=color, stroke_width=0,
                                text_anchor='middle', creation=creation, z=z + 0.2))
        # Bars
        self._bars = []
        for i in range(n):
            v = values[i]
            base, top = cumulative[i], cumulative[i + 1]
            color = pos_color if v >= 0 else neg_color
            lbl = labels[i] if labels and i < len(labels) else str(i)
            val_text = f'{v:+.1f}' if v != int(v) else f'{v:+.0f}'
            _add_bar(i, base, top, color, lbl, val_text)
            # Connector line to next bar
            if i < n - 1 or show_total:
                bx = _bar_x(i)
                conn = Line(x1=bx + bw, y1=_val_to_y(top),
                            x2=_bar_x(i + 1), y2=_val_to_y(top),
                            stroke=connector_color, stroke_width=1,
                            stroke_dasharray='3 2', creation=creation, z=z + 0.05)
                objects.append(conn)
        # Total bar
        if show_total:
            total = cumulative[-1]
            lbl = labels[n] if labels and n < len(labels) else 'Total'
            val_text = f'{total:.1f}' if total != int(total) else f'{int(total)}'
            _add_bar(n, 0, total, total_color, lbl, val_text)
        super().__init__(*objects, creation=creation, z=z)


class GanttChart(VCollection):
    """Gantt chart for project timelines.

    tasks: list of (label, start, end) tuples or (label, start, end, color).
    """
    def __init__(self, tasks, x=100, y=80, width=1200, height=None,
                 bar_height=30, bar_spacing=10, colors=None,
                 font_size=16, creation: float = 0, z: float = 0):
        n = len(tasks)
        if n == 0:
            super().__init__(creation=creation, z=z)
            return
        if colors is None:
            colors = list(DEFAULT_CHART_COLORS)
        # Compute time range
        all_starts = [t[1] for t in tasks]
        all_ends = [t[2] for t in tasks]
        t_min, t_max = min(all_starts), max(all_ends)
        t_span = t_max - t_min if t_max != t_min else 1
        label_w = 120
        chart_x = x + label_w
        chart_w = width - label_w
        objects = []
        # Header line
        header = Line(x1=chart_x, y1=y, x2=chart_x + chart_w, y2=y,
                      stroke='#555', stroke_width=1, creation=creation, z=z)
        objects.append(header)
        # Time axis ticks
        n_ticks = min(10, int(t_span) + 1) if t_span >= 1 else 2
        for i in range(n_ticks + 1):
            frac = i / max(n_ticks, 1)
            tx = chart_x + frac * chart_w
            tv = t_min + frac * t_span
            tick = Line(x1=tx, y1=y - 5, x2=tx, y2=y + 5,
                        stroke='#666', stroke_width=1, creation=creation, z=z)
            objects.append(tick)
            label = f'{tv:.0f}' if tv == int(tv) else f'{tv:.1f}'
            lbl = Text(text=label, x=tx, y=y - 10,
                       font_size=font_size - 2, fill='#aaa', stroke_width=0,
                       text_anchor='middle', creation=creation, z=z + 0.1)
            objects.append(lbl)
        # Task bars
        self._bars = []
        for i, task in enumerate(tasks):
            task_label = task[0]
            t_start, t_end = task[1], task[2]
            color = task[3] if len(task) > 3 else colors[i % len(colors)]
            by = y + 20 + i * (bar_height + bar_spacing)
            bx = chart_x + (t_start - t_min) / t_span * chart_w
            bw = max(2, (t_end - t_start) / t_span * chart_w)
            rect = Rectangle(width=bw, height=bar_height, x=bx, y=by,
                              fill=color, fill_opacity=0.8, stroke=color,
                              stroke_width=1, rx=4, ry=4,
                              creation=creation, z=z + 0.1)
            self._bars.append(rect)
            objects.append(rect)
            # Label
            lbl = Text(text=task_label, x=x + 5, y=by + bar_height / 2 + font_size * TEXT_Y_OFFSET,
                       font_size=font_size, fill='#ccc', stroke_width=0,
                       text_anchor='start', creation=creation, z=z + 0.1)
            objects.append(lbl)
            # Grid line
            grid = Line(x1=chart_x, y1=by + bar_height + bar_spacing / 2,
                        x2=chart_x + chart_w, y2=by + bar_height + bar_spacing / 2,
                        stroke='#333', stroke_width=0.5, creation=creation, z=z - 0.1)
            objects.append(grid)
        super().__init__(*objects, creation=creation, z=z)


class SankeyDiagram(VCollection):
    """Sankey flow diagram showing flows between nodes.

    flows: list of (source_label, target_label, value) tuples.
    """
    def __init__(self, flows, x=100, y=100, width=1200, height=600,
                 node_width=30, node_spacing=20, colors=None,
                 font_size=16, creation: float = 0, z: float = 0):
        if not flows:
            super().__init__(creation=creation, z=z)
            return
        if colors is None:
            colors = list(DEFAULT_CHART_COLORS)
        sources = list(dict.fromkeys(src for src, _, _ in flows))
        targets = list(dict.fromkeys(tgt for _, tgt, _ in flows))
        src_totals = {s: sum(v for ss, _, v in flows if ss == s) for s in sources}
        tgt_totals = {t: sum(v for _, tt, v in flows if tt == t) for t in targets}
        max_total = max(max(src_totals.values()), max(tgt_totals.values())) or 1

        def _layout(names, totals, left_x):
            sc = (height - (len(names) - 1) * node_spacing) / max_total
            rects, cy = {}, y
            for n in names:
                h = max(totals[n] * sc, 2)
                rects[n] = (left_x, cy, node_width, h)
                cy += h + node_spacing
            return rects, sc

        src_rects, scale = _layout(sources, src_totals, x)
        tgt_rects, tgt_scale = _layout(targets, tgt_totals, x + width - node_width)
        objects = []
        # Flow paths (cubic bezier)
        src_offsets = {s: 0.0 for s in sources}
        tgt_offsets = {t: 0.0 for t in targets}
        for i, (src, tgt, val) in enumerate(flows):
            color = colors[i % len(colors)]
            sx, sy, sw, _ = src_rects[src]
            tx, ty, _, _ = tgt_rects[tgt]
            fhs, fht = val * scale, val * tgt_scale
            y0, y1 = sy + src_offsets[src], ty + tgt_offsets[tgt]
            src_offsets[src] += fhs
            tgt_offsets[tgt] += fht
            x0, x3 = sx + sw, tx
            cx1, cx2 = x0 + (x3 - x0) * 0.4, x0 + (x3 - x0) * 0.6
            d = (f'M{x0:.1f},{y0:.1f} '
                 f'C{cx1:.1f},{y0:.1f} {cx2:.1f},{y1:.1f} {x3:.1f},{y1:.1f} '
                 f'L{x3:.1f},{y1 + fht:.1f} '
                 f'C{cx2:.1f},{y1 + fht:.1f} {cx1:.1f},{y0 + fhs:.1f} '
                 f'{x0:.1f},{y0 + fhs:.1f} Z')
            objects.append(Path(d, x=0, y=0, fill=color, fill_opacity=0.4,
                                stroke=color, stroke_width=0.5, stroke_opacity=0.6,
                                creation=creation, z=z + 0.1))
        # Node rectangles + labels
        def _draw_nodes(names, rects, color_offset, anchor, lbl_dx):
            for i, n in enumerate(names):
                bx, by, bw, bh = rects[n]
                c = colors[(color_offset + i) % len(colors)]
                objects.append(Rectangle(width=bw, height=bh, x=bx, y=by,
                                         fill=c, fill_opacity=0.9, stroke_width=0,
                                         creation=creation, z=z + 0.2))
                objects.append(Text(text=n, x=bx + lbl_dx,
                                    y=by + bh / 2 + font_size * TEXT_Y_OFFSET,
                                    font_size=font_size, fill='#ddd', stroke_width=0,
                                    text_anchor=anchor, creation=creation, z=z + 0.3))
        _draw_nodes(sources, src_rects, 0, 'end', -5)
        _draw_nodes(targets, tgt_rects, len(sources), 'start', node_width + 5)
        super().__init__(*objects, creation=creation, z=z)


class FunnelChart(VCollection):
    """Funnel chart showing progressive narrowing stages.

    stages: list of (label, value) tuples, ordered top-to-bottom.
    """
    def __init__(self, stages, x=100, y=100, width=600, height=500,
                 colors=None, font_size=18, gap=4, creation: float = 0, z: float = 0):
        if not stages:
            super().__init__(creation=creation, z=z)
            return
        if colors is None:
            colors = list(DEFAULT_CHART_COLORS)
        n = len(stages)
        max_val = max(v for _, v in stages) or 1
        row_h = (height - (n - 1) * gap) / n
        cx = x + width / 2
        objects = []
        for i, (label, val) in enumerate(stages):
            top_w = width if i == 0 else width * stages[i - 1][1] / max_val
            bot_w = width * val / max_val
            ty = y + i * (row_h + gap)
            by = ty + row_h
            pts = [(cx - top_w / 2, ty), (cx + top_w / 2, ty),
                   (cx + bot_w / 2, by), (cx - bot_w / 2, by)]
            color = colors[i % len(colors)]
            trap = Polygon(*pts, fill=color, fill_opacity=0.85, stroke=color,
                           stroke_width=1, creation=creation, z=z)
            objects.append(trap)
            lbl = Text(text=f'{label} ({val})', x=cx, y=ty + row_h / 2 + font_size * TEXT_Y_OFFSET,
                       font_size=font_size, fill='#fff', stroke_width=0,
                       text_anchor='middle', creation=creation, z=z + 0.1)
            objects.append(lbl)
        super().__init__(*objects, creation=creation, z=z)


class TreeMap(VCollection):
    """Treemap visualization using squarified layout.

    data: list of (label, value) tuples.
    """
    def __init__(self, data, x=100, y=100, width=800, height=600,
                 colors=None, font_size=14, padding=2, creation: float = 0, z: float = 0):
        if not data:
            super().__init__(creation=creation, z=z)
            return
        if colors is None:
            colors = list(DEFAULT_CHART_COLORS)
        total = sum(v for _, v in data) or 1
        # Sort descending by value for squarified layout
        sorted_data = sorted(enumerate(data), key=lambda iv: iv[1][1], reverse=True)
        rects = self._squarify(sorted_data, x, y, width, height, total)
        objects = []
        for orig_idx, (label, _val), (rx, ry, rw, rh) in rects:
            color = colors[orig_idx % len(colors)]
            rect = Rectangle(width=max(rw - padding, 1), height=max(rh - padding, 1),
                              x=rx + padding / 2, y=ry + padding / 2,
                              fill=color, fill_opacity=0.8, stroke='#222', stroke_width=1,
                              creation=creation, z=z)
            objects.append(rect)
            if rw > font_size * 2 and rh > font_size * 1.5:
                lbl = Text(text=str(label), x=rx + rw / 2, y=ry + rh / 2 + font_size * TEXT_Y_OFFSET,
                           font_size=min(font_size, rw / max(len(str(label)), 1) * 1.5),
                           fill='#fff', stroke_width=0, text_anchor='middle',
                           creation=creation, z=z + 0.1)
                objects.append(lbl)
        super().__init__(*objects, creation=creation, z=z)

    @staticmethod
    def _squarify(items, x, y, w, h, total):
        """Squarified treemap layout. Returns list of (orig_idx, (label, val), (rx, ry, rw, rh))."""
        if not items:
            return []
        if len(items) == 1:
            idx, (label, val) = items[0]
            return [(idx, (label, val), (x, y, w, h))]
        area = w * h
        result = []
        remaining = list(items)
        cx, cy, cw, ch = x, y, w, h
        while remaining:
            if len(remaining) == 1:
                idx, (label, val) = remaining[0]
                result.append((idx, (label, val), (cx, cy, cw, ch)))
                break
            # Lay out along shorter side
            short = min(cw, ch)
            row = [remaining.pop(0)]
            row_area = row[0][1][1] / total * area

            def _worst(row_items, side, r_area):
                if side <= 0 or r_area <= 0:
                    return float('inf')
                s2 = side * side
                return max(max(s2 * r_area / (itm[1][1] / total * area) ** 2,
                               (itm[1][1] / total * area) ** 2 / (s2 * r_area))
                           for itm in row_items)

            while remaining:
                candidate = remaining[0]
                new_area = row_area + candidate[1][1] / total * area
                if _worst(row + [candidate], short, new_area) <= _worst(row, short, row_area):
                    row.append(remaining.pop(0))
                    row_area = new_area
                else:
                    break
            # Place row
            if cw <= ch:  # horizontal strip at top
                strip_h = row_area / max(cw, 1)
                rx = cx
                for idx, (label, val) in row:
                    rw = (val / total * area) / max(strip_h, 1)
                    result.append((idx, (label, val), (rx, cy, rw, strip_h)))
                    rx += rw
                cy += strip_h
                ch -= strip_h
            else:  # vertical strip at left
                strip_w = row_area / max(ch, 1)
                ry = cy
                for idx, (label, val) in row:
                    rh = (val / total * area) / max(strip_w, 1)
                    result.append((idx, (label, val), (cx, ry, strip_w, rh)))
                    ry += rh
                cx += strip_w
                cw -= strip_w
        return result


class GaugeChart(VCollection):
    """Speedometer / gauge chart.

    value: current value.  min_val/max_val: gauge range.
    """
    def __init__(self, value, min_val=0, max_val=100, x=960, y=540,
                 radius=200, start_angle=225, end_angle=-45,
                 colors=None, label=None, font_size=36,
                 tick_count=5, creation: float = 0, z: float = 0):
        if colors is None:
            colors = [('#83C167', 0.0), ('#FFFF00', 0.5), ('#FF6B6B', 1.0)]
        objects = []
        # Background arc segments (colored bands)
        n_segments = 60
        sa_rad = math.radians(start_angle)
        ea_rad = math.radians(end_angle)
        if ea_rad > sa_rad:
            ea_rad -= math.tau
        total_sweep = ea_rad - sa_rad
        for i in range(n_segments):
            frac = i / n_segments
            a0 = sa_rad + total_sweep * frac
            a1 = sa_rad + total_sweep * (frac + 1 / n_segments)
            # Interpolate color
            seg_color = GaugeChart._interp_gauge_color(frac, colors)
            arc = Arc(cx=x, cy=y, r=radius, start_angle=math.degrees(a0),
                      end_angle=math.degrees(a1), stroke=seg_color,
                      stroke_width=20, creation=creation, z=z)
            objects.append(arc)
        # Tick marks + labels
        for i in range(tick_count + 1):
            frac = i / tick_count
            angle = sa_rad + total_sweep * frac
            tick_val = min_val + (max_val - min_val) * frac
            ix = x + (radius + 18) * math.cos(angle)
            iy = y - (radius + 18) * math.sin(angle)
            ox = x + (radius - 15) * math.cos(angle)
            oy = y - (radius - 15) * math.sin(angle)
            tick = Line(x1=ox, y1=oy, x2=ix, y2=iy, stroke='#888',
                        stroke_width=1.5, creation=creation, z=z + 0.1)
            objects.append(tick)
            lx = x + (radius + 35) * math.cos(angle)
            ly = y - (radius + 35) * math.sin(angle)
            tlbl = Text(text=f'{tick_val:.0f}', x=lx, y=ly + font_size * 0.2,
                        font_size=font_size * 0.4, fill='#aaa', stroke_width=0,
                        text_anchor='middle', creation=creation, z=z + 0.1)
            objects.append(tlbl)
        # Needle
        val_frac = max(0, min(1, (value - min_val) / max(max_val - min_val, 1)))
        needle_angle = sa_rad + total_sweep * val_frac
        nx = x + (radius - 30) * math.cos(needle_angle)
        ny = y - (radius - 30) * math.sin(needle_angle)
        needle = Line(x1=x, y1=y, x2=nx, y2=ny, stroke='#fff',
                      stroke_width=3, creation=creation, z=z + 0.2)
        objects.append(needle)
        # Center dot
        center = Dot(cx=x, cy=y, r=8, fill='#fff', stroke_width=0,
                     creation=creation, z=z + 0.3)
        objects.append(center)
        # Value label
        val_lbl = Text(text=f'{value:.0f}', x=x, y=y + radius * 0.4,
                       font_size=font_size, fill='#fff', stroke_width=0,
                       text_anchor='middle', creation=creation, z=z + 0.3)
        objects.append(val_lbl)
        if label:
            sub_lbl = Text(text=str(label), x=x, y=y + radius * 0.4 + font_size * 1.2,
                           font_size=font_size * 0.5, fill='#aaa', stroke_width=0,
                           text_anchor='middle', creation=creation, z=z + 0.3)
            objects.append(sub_lbl)
        super().__init__(*objects, creation=creation, z=z)

    @staticmethod
    def _interp_gauge_color(frac, colors):
        """Interpolate gauge color from color stops list [(color, position), ...]."""
        if frac <= colors[0][1]:
            return colors[0][0]
        if frac >= colors[-1][1]:
            return colors[-1][0]
        for i in range(len(colors) - 1):
            c0, p0 = colors[i]
            c1, p1 = colors[i + 1]
            if p0 <= frac <= p1:
                t = (frac - p0) / max(p1 - p0, 1e-9)
                r0, g0, b0 = int(c0[1:3], 16), int(c0[3:5], 16), int(c0[5:7], 16)
                r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
                r = int(r0 + (r1 - r0) * t)
                g = int(g0 + (g1 - g0) * t)
                b = int(b0 + (b1 - b0) * t)
                return f'#{r:02x}{g:02x}{b:02x}'
        return colors[-1][0]


class SparkLine(VObject):
    """Minimal inline chart (sparkline) rendered as a single SVG path.

    data: list of numeric values.
    """
    def __init__(self, data, x=100, y=100, width=120, height=30,
                 stroke='#58C4DD', stroke_width=1.5,
                 show_endpoint=False, creation: float = 0, z: float = 0, **styling_kwargs):
        kw = {'stroke': stroke, 'stroke_width': stroke_width,
              'fill_opacity': 0} | styling_kwargs
        super().__init__(creation=creation, z=z)
        self.styling = style.Styling(kw, creation=creation, stroke='#58C4DD')
        self._data = list(data)
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._show_endpoint = show_endpoint
        self._endpoint_r = 2.5

    def _extra_attrs(self):
        return []

    def path(self, time):
        data = self._data
        if len(data) < 2:
            return ''
        mn, mx = min(data), max(data)
        rng = mx - mn if mx != mn else 1
        n = len(data)
        dx = self._width / (n - 1)
        pts = []
        for i, v in enumerate(data):
            px = self._x + i * dx
            py = self._y + self._height - (v - mn) / rng * self._height
            pts.append(f'{px:.1f},{py:.1f}')
        return 'M' + 'L'.join(pts)

    def snap_points(self, time):
        return [(self._x, self._y), (self._x + self._width, self._y + self._height)]

    def to_svg(self, time):
        d = self.path(time)
        if not d:
            return ''
        s = self.styling.svg_style(time)
        svg = f'<path d="{d}"{s}/>'
        if self._show_endpoint and len(self._data) >= 2:
            mn, mx = min(self._data), max(self._data)
            rng = mx - mn if mx != mn else 1
            last = self._data[-1]
            ex = self._x + self._width
            ey = self._y + self._height - (last - mn) / rng * self._height
            sc = self.styling.stroke.time_func(time)
            color = f'rgb({int(sc[0])},{int(sc[1])},{int(sc[2])})' if isinstance(sc, tuple) else str(sc)
            svg += f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="{self._endpoint_r}" fill="{color}"/>'
        return svg


from vectormation._diagrams import VennDiagram as VennDiagram  # noqa: E402,F811
from vectormation._diagrams import OrgChart as OrgChart  # noqa: E402,F811


class KPICard(VCollection):
    """Metric card showing a title, large value, optional subtitle and trend sparkline.

    title: metric name.  value: displayed value string.
    """
    def __init__(self, title, value, subtitle=None, trend_data=None,
                 x=100, y=100, width=280, height=160,
                 bg_color='#1a1a2e', title_color='#aaa', value_color='#fff',
                 font_size=48, creation: float = 0, z: float = 0):
        objects = []
        # Background card

        bg = RoundedRectangle(width=width, height=height, x=x, y=y,
                               corner_radius=10, fill=bg_color, fill_opacity=0.9,
                               stroke='#333', stroke_width=1,
                               creation=creation, z=z)
        objects.append(bg)
        # Title
        t_lbl = Text(text=str(title), x=x + width / 2, y=y + 30,
                     font_size=font_size * TEXT_Y_OFFSET, fill=title_color, stroke_width=0,
                     text_anchor='middle', creation=creation, z=z + 0.1)
        objects.append(t_lbl)
        # Value
        v_lbl = Text(text=str(value), x=x + width / 2, y=y + height * 0.5 + font_size * 0.3,
                     font_size=font_size, fill=value_color, stroke_width=0,
                     text_anchor='middle', creation=creation, z=z + 0.1)
        objects.append(v_lbl)
        # Subtitle
        if subtitle:
            s_lbl = Text(text=str(subtitle), x=x + width / 2,
                         y=y + height * 0.5 + font_size * 0.3 + font_size * CHAR_WIDTH_FACTOR,
                         font_size=font_size * 0.3, fill=title_color, stroke_width=0,
                         text_anchor='middle', creation=creation, z=z + 0.1)
            objects.append(s_lbl)
        # Trend sparkline
        if trend_data and len(trend_data) >= 2:
            sl_w = width * 0.6
            sl_h = height * 0.15
            sl_x = x + (width - sl_w) / 2
            sl_y = y + height - sl_h - 15
            spark = SparkLine(trend_data, x=sl_x, y=sl_y, width=sl_w, height=sl_h,
                              stroke='#58C4DD', stroke_width=1, show_endpoint=True,
                              creation=creation, z=z + 0.1)
            objects.append(spark)
        super().__init__(*objects, creation=creation, z=z)


class BulletChart(VCollection):
    """Bullet chart: qualitative ranges + actual bar + target marker.

    actual: actual value.  target: target value.
    ranges: list of (value, color) tuples for qualitative ranges, sorted ascending.
    """
    def __init__(self, actual, target, ranges=None, label=None,
                 x=100, y=100, width=500, height=40,
                 bar_color='#333', target_color='#fff',
                 font_size=16, max_val=None, creation: float = 0, z: float = 0):
        if ranges is None:
            ranges = [(0.5, '#2a2a3a'), (0.75, '#3a3a4a'), (1.0, '#4a4a5a')]
        if max_val is None:
            max_val = max(actual, target, max(v for v, _ in ranges) if ranges else 1)
            if max_val <= 0:
                max_val = 1
        objects = []
        # Qualitative range backgrounds
        prev = 0
        for val, color in sorted(ranges, key=lambda vc: vc[0]):
            rw = (val - prev) / max_val * width
            rect = Rectangle(width=max(rw, 0), height=height,
                              x=x + prev / max_val * width, y=y,
                              fill=color, fill_opacity=1, stroke_width=0,
                              creation=creation, z=z)
            objects.append(rect)
            prev = val
        # Actual value bar
        bar_h = height * 0.5
        bar_w = max(actual / max_val * width, 0)
        bar = Rectangle(width=bar_w, height=bar_h,
                         x=x, y=y + (height - bar_h) / 2,
                         fill=bar_color, fill_opacity=1, stroke_width=0,
                         creation=creation, z=z + 0.1)
        objects.append(bar)
        # Target marker
        tx = x + target / max_val * width
        marker = Line(x1=tx, y1=y + height * 0.15, x2=tx, y2=y + height * 0.85,
                      stroke=target_color, stroke_width=2.5,
                      creation=creation, z=z + 0.2)
        objects.append(marker)
        # Label
        if label:
            lbl = Text(text=str(label), x=x - 10, y=y + height / 2 + font_size * TEXT_Y_OFFSET,
                       font_size=font_size, fill='#ddd', stroke_width=0,
                       text_anchor='end', creation=creation, z=z + 0.1)
            objects.append(lbl)
        super().__init__(*objects, creation=creation, z=z)


class CalendarHeatmap(VCollection):
    """Grid heatmap like a GitHub contribution graph.

    data: dict mapping (row, col) to a value, or a flat list (auto-arranged into rows).
    """
    def __init__(self, data, rows=7, cols=52, x=100, y=100,
                 cell_size=14, gap=2, colormap=None,
                 creation: float = 0, z: float = 0):
        if colormap is None:
            colormap = ['#161b22', '#0e4429', '#006d32', '#26a641', '#39d353']
        # Normalize data to dict
        if isinstance(data, dict):
            grid = data
        else:
            grid = {}
            flat = list(data)
            for idx, val in enumerate(flat):
                r = idx % rows
                c = idx // rows
                grid[(r, c)] = val
        if not grid:
            super().__init__(creation=creation, z=z)
            return
        vals = list(grid.values())
        mn, mx = min(vals), max(vals)
        rng = mx - mn if mx != mn else 1
        objects = []
        for (r, c), val in grid.items():
            frac = (val - mn) / rng
            ci = min(int(frac * (len(colormap) - 1) + 0.5), len(colormap) - 1)
            color = colormap[ci]
            rx = x + c * (cell_size + gap)
            ry = y + r * (cell_size + gap)
            rect = Rectangle(width=cell_size, height=cell_size, x=rx, y=ry,
                              fill=color, fill_opacity=1, stroke_width=0,
                              creation=creation, z=z)
            objects.append(rect)
        super().__init__(*objects, creation=creation, z=z)


class WaffleChart(VCollection):
    """Waffle chart: grid of colored squares showing category proportions.

    categories: list of (label, value, color) tuples.
    """
    def __init__(self, categories, x=100, y=100, grid_size=10,
                 cell_size=20, gap=3, font_size=14, creation: float = 0, z: float = 0):
        total = sum(v for _, v, _ in categories) or 1
        n_cells = grid_size * grid_size
        objects = []
        cell_idx = 0
        legend_objs = []
        for label, val, color in categories:
            count = round(val / total * n_cells)
            for _ in range(count):
                if cell_idx >= n_cells:
                    break
                r = cell_idx // grid_size
                c = cell_idx % grid_size
                rx = x + c * (cell_size + gap)
                ry = y + r * (cell_size + gap)
                rect = Rectangle(width=cell_size, height=cell_size, x=rx, y=ry,
                                  fill=color, fill_opacity=0.9, stroke_width=0,
                                  creation=creation, z=z)
                objects.append(rect)
                cell_idx += 1
            # Legend entry
            lx = x + grid_size * (cell_size + gap) + 15
            ly = y + len(legend_objs) * (font_size * 1.5)
            swatch = Rectangle(width=font_size, height=font_size,
                                x=lx, y=ly, fill=color, fill_opacity=0.9,
                                stroke_width=0, creation=creation, z=z + 0.1)
            lbl = Text(text=f'{label} ({val})', x=lx + font_size + 5,
                       y=ly + font_size * 0.8, font_size=font_size,
                       fill='#ddd', stroke_width=0, text_anchor='start',
                       creation=creation, z=z + 0.1)
            legend_objs += [swatch, lbl]
        # Fill remaining cells with empty color
        while cell_idx < n_cells:
            r = cell_idx // grid_size
            c = cell_idx % grid_size
            rx = x + c * (cell_size + gap)
            ry = y + r * (cell_size + gap)
            rect = Rectangle(width=cell_size, height=cell_size, x=rx, y=ry,
                              fill='#1a1a2e', fill_opacity=0.5, stroke_width=0,
                              creation=creation, z=z)
            objects.append(rect)
            cell_idx += 1
        super().__init__(*(objects + legend_objs), creation=creation, z=z)


from vectormation._diagrams import MindMap as MindMap  # noqa: E402,F811


class CircularProgressBar(VCollection):
    """Circular progress indicator with percentage text.

    value: 0-100 (percent complete).
    """
    def __init__(self, value, x=960, y=540, radius=80, stroke_width=12,
                 track_color='#2a2a3a', bar_color='#58C4DD',
                 font_size=36, show_text=True, creation: float = 0, z: float = 0):
        objects = []
        # Background track (full circle arc)
        track = Arc(cx=x, cy=y, r=radius, start_angle=90, end_angle=90 - 359.99,
                    stroke=track_color, stroke_width=stroke_width,
                    creation=creation, z=z)
        objects.append(track)
        # Progress arc
        pct = max(0, min(100, value))
        sweep = 360 * pct / 100
        if sweep > 0.1:
            prog = Arc(cx=x, cy=y, r=radius, start_angle=90,
                       end_angle=90 - sweep,
                       stroke=bar_color, stroke_width=stroke_width,
                       creation=creation, z=z + 0.1)
            objects.append(prog)
        # Text
        if show_text:
            lbl = Text(text=f'{pct:.0f}%', x=x, y=y + font_size * TEXT_Y_OFFSET,
                       font_size=font_size, fill=bar_color, stroke_width=0,
                       text_anchor='middle', creation=creation, z=z + 0.2)
            objects.append(lbl)
        super().__init__(*objects, creation=creation, z=z)


class Scoreboard(VCollection):
    """Score/metric display panel.

    entries: list of (label, value) tuples.
    """
    def __init__(self, entries, x=100, y=100, col_width=200, row_height=60,
                 bg_color='#1a1a2e', label_color='#aaa', value_color='#fff',
                 font_size=28, cols=None, creation: float = 0, z: float = 0):
        if not entries:
            super().__init__(creation=creation, z=z)
            return
        if cols is None:
            cols = min(len(entries), 4)
        rows_count = math.ceil(len(entries) / cols)
        total_w = cols * col_width
        total_h = rows_count * row_height

        objects = []
        # Background
        bg = RoundedRectangle(width=total_w + 20, height=total_h + 20,
                               x=x - 10, y=y - 10, corner_radius=10,
                               fill=bg_color, fill_opacity=0.9,
                               stroke='#333', stroke_width=1,
                               creation=creation, z=z)
        objects.append(bg)
        for i, (label, value) in enumerate(entries):
            r = i // cols
            c = i % cols
            cx = x + c * col_width + col_width / 2
            cy = y + r * row_height
            # Value
            v_lbl = Text(text=str(value), x=cx, y=cy + font_size * 0.9,
                         font_size=font_size, fill=value_color, stroke_width=0,
                         text_anchor='middle', creation=creation, z=z + 0.1)
            objects.append(v_lbl)
            # Label
            l_lbl = Text(text=str(label), x=cx,
                         y=cy + font_size * 0.9 + font_size * 0.7,
                         font_size=font_size * 0.4, fill=label_color, stroke_width=0,
                         text_anchor='middle', creation=creation, z=z + 0.1)
            objects.append(l_lbl)
            # Divider (between columns)
            if c < cols - 1 and i < len(entries) - 1:
                dx = x + (c + 1) * col_width
                div = Line(x1=dx, y1=cy + 5, x2=dx, y2=cy + row_height - 5,
                           stroke='#333', stroke_width=1,
                           creation=creation, z=z + 0.05)
                objects.append(div)
        super().__init__(*objects, creation=creation, z=z)


class MatrixHeatmap(VCollection):
    """Labeled matrix heatmap with colored cells.

    data: 2D list of values (rows x cols).
    row_labels / col_labels: optional label lists.
    """
    def __init__(self, data, row_labels=None, col_labels=None,
                 x=100, y=100, cell_size=50, gap=2,
                 colormap=None, font_size=14, show_values=True,
                 creation: float = 0, z: float = 0):
        if not data or not data[0]:
            super().__init__(creation=creation, z=z)
            return
        if colormap is None:
            colormap = ['#313695', '#4575b4', '#74add1', '#abd9e9',
                        '#fee090', '#fdae61', '#f46d43', '#d73027']
        n_rows = len(data)
        n_cols = len(data[0])
        # Flatten to find min/max
        flat = [v for row in data for v in row]
        mn, mx = min(flat), max(flat)
        rng = mx - mn if mx != mn else 1
        objects = []
        label_offset = 0
        if row_labels:
            label_offset = max(len(str(l)) for l in row_labels) * font_size * 0.5 + 10
        col_offset = font_size + 10 if col_labels else 0
        for r in range(n_rows):
            for c in range(n_cols):
                val = data[r][c]
                frac = (val - mn) / rng
                ci = min(int(frac * (len(colormap) - 1) + 0.5), len(colormap) - 1)
                color = colormap[ci]
                rx = x + label_offset + c * (cell_size + gap)
                ry = y + col_offset + r * (cell_size + gap)
                rect = Rectangle(width=cell_size, height=cell_size, x=rx, y=ry,
                                  fill=color, fill_opacity=0.9, stroke='#222',
                                  stroke_width=0.5, creation=creation, z=z)
                objects.append(rect)
                if show_values:
                    vlbl = Text(text=f'{val:.1f}' if isinstance(val, float) else str(val),
                                x=rx + cell_size / 2, y=ry + cell_size / 2 + font_size * TEXT_Y_OFFSET,
                                font_size=font_size * 0.8, fill='#fff', stroke_width=0,
                                text_anchor='middle', creation=creation, z=z + 0.1)
                    objects.append(vlbl)
        # Row labels
        if row_labels:
            for r, label in enumerate(row_labels[:n_rows]):
                ry = y + col_offset + r * (cell_size + gap)
                lbl = Text(text=str(label), x=x + label_offset - 8,
                           y=ry + cell_size / 2 + font_size * TEXT_Y_OFFSET,
                           font_size=font_size, fill='#aaa', stroke_width=0,
                           text_anchor='end', creation=creation, z=z + 0.1)
                objects.append(lbl)
        # Column labels
        if col_labels:
            for c, label in enumerate(col_labels[:n_cols]):
                cx = x + label_offset + c * (cell_size + gap) + cell_size / 2
                lbl = Text(text=str(label), x=cx, y=y + font_size * 0.8,
                           font_size=font_size, fill='#aaa', stroke_width=0,
                           text_anchor='middle', creation=creation, z=z + 0.1)
                objects.append(lbl)
        super().__init__(*objects, creation=creation, z=z)


class BoxPlot(VCollection):
    """Box-and-whisker plot for one or more data groups.

    data_groups: list of lists of numeric values.
    positions: x-positions for each box (defaults to 1, 2, 3, ...).
    """
    def __init__(self, data_groups, positions=None, x=100, y=100,
                 plot_width=400, plot_height=300, box_width=30,
                 box_color='#58C4DD', whisker_color='#aaa', median_color='#FF6B6B',
                 font_size=12, creation: float = 0, z: float = 0):
        if not data_groups:
            super().__init__(creation=creation, z=z)
            return
        if positions is None:
            positions = list(range(1, len(data_groups) + 1))
        # Compute stats for each group
        stats = []
        for grp in data_groups:
            s = sorted(grp)
            n = len(s)
            q1 = s[n // 4] if n >= 4 else s[0]
            med = s[n // 2]
            q3 = s[3 * n // 4] if n >= 4 else s[-1]
            iqr = q3 - q1
            lo = max(s[0], q1 - 1.5 * iqr)
            hi = min(s[-1], q3 + 1.5 * iqr)
            stats.append((lo, q1, med, q3, hi))
        # Determine data range
        all_vals = [v for grp in data_groups for v in grp]
        y_min, y_max = min(all_vals), max(all_vals)
        y_rng = y_max - y_min if y_max != y_min else 1
        x_min, x_max = min(positions) - 0.5, max(positions) + 0.5
        x_rng = x_max - x_min if x_max != x_min else 1
        def to_px(xv, yv):
            px = x + (xv - x_min) / x_rng * plot_width
            py = y + plot_height - (yv - y_min) / y_rng * plot_height
            return px, py
        objects = []
        half = box_width / 2
        for pos, (lo, q1, med, q3, hi) in zip(positions, stats):
            cx, _ = to_px(pos, 0)
            _, py_lo = to_px(0, lo)
            _, py_q1 = to_px(0, q1)
            _, py_med = to_px(0, med)
            _, py_q3 = to_px(0, q3)
            _, py_hi = to_px(0, hi)
            # Box (Q1 to Q3)
            bh = abs(py_q1 - py_q3)
            box = Rectangle(width=box_width, height=bh, x=cx - half, y=min(py_q1, py_q3),
                            fill=box_color, fill_opacity=0.3, stroke=box_color,
                            stroke_width=1.5, creation=creation, z=z)
            objects.append(box)
            # Median line
            ml = Line(x1=cx - half, y1=py_med, x2=cx + half, y2=py_med,
                      stroke=median_color, stroke_width=2, creation=creation, z=z + 0.1)
            objects.append(ml)
            # Whiskers
            for wy in [py_lo, py_hi]:
                cap = Line(x1=cx - half * 0.6, y1=wy, x2=cx + half * 0.6, y2=wy,
                           stroke=whisker_color, stroke_width=1.5, creation=creation, z=z)
                objects.append(cap)
            stem_lo = Line(x1=cx, y1=py_q1, x2=cx, y2=py_lo,
                           stroke=whisker_color, stroke_width=1, creation=creation, z=z)
            stem_hi = Line(x1=cx, y1=py_q3, x2=cx, y2=py_hi,
                           stroke=whisker_color, stroke_width=1, creation=creation, z=z)
            objects.extend([stem_lo, stem_hi])
        super().__init__(*objects, creation=creation, z=z)


class SampleSpace(VCollection):
    """Rectangle representing a probability sample space, divisible into regions.

    Useful for visualizing conditional probability, Bayes' theorem, etc.
    """
    def __init__(self, width=500, height=400, x=710, y=340, creation: float = 0, z: float = 0, **styling_kwargs):
        style_kw = {'fill': '#222', 'fill_opacity': 0.5,
                    'stroke': '#fff', 'stroke_width': 2} | styling_kwargs
        self._rect = Rectangle(width=width, height=height, x=x, y=y,
                               creation=creation, z=z, **style_kw)
        self._width, self._height = width, height
        self._x, self._y = x, y
        self._parts = []
        super().__init__(self._rect, creation=creation, z=z)

    def divide_horizontally(self, proportion, colors=('#58C4DD', '#FC6255'), labels=None,
                            creation=0, z=0):
        """Split the space horizontally by proportion (0-1). Left gets first color."""
        w1 = self._width * proportion
        w2 = self._width - w1
        r1 = Rectangle(width=w1, height=self._height,
                       x=self._x, y=self._y,
                       fill=colors[0], fill_opacity=0.4, stroke_width=0,
                       creation=creation, z=z + 0.1)
        r2 = Rectangle(width=w2, height=self._height,
                       x=self._x + w1, y=self._y,
                       fill=colors[1], fill_opacity=0.4, stroke_width=0,
                       creation=creation, z=z + 0.1)
        self.objects.extend([r1, r2])
        self._parts = [r1, r2]
        if labels:
            for rect, label in zip([r1, r2], labels):
                rcx, rcy = rect.center(creation)
                self.objects.append(
                    _label_text(label, rcx, rcy, 24,
                                creation=creation, z=z + 0.2))
        return self

    def divide_vertically(self, proportion, colors=('#58C4DD', '#FC6255'), labels=None,
                          creation=0, z=0):
        """Split the space vertically by proportion (0-1). Top gets first color."""
        h1 = self._height * proportion
        h2 = self._height - h1
        r1 = Rectangle(width=self._width, height=h1,
                       x=self._x, y=self._y,
                       fill=colors[0], fill_opacity=0.4, stroke_width=0,
                       creation=creation, z=z + 0.1)
        r2 = Rectangle(width=self._width, height=h2,
                       x=self._x, y=self._y + h1,
                       fill=colors[1], fill_opacity=0.4, stroke_width=0,
                       creation=creation, z=z + 0.1)
        self.objects.extend([r1, r2])
        self._parts = [r1, r2]
        if labels:
            for rect, label in zip([r1, r2], labels):
                rcx, rcy = rect.center(creation)
                self.objects.append(
                    _label_text(label, rcx, rcy, 24,
                                creation=creation, z=z + 0.2))
        return self


class Array(VCollection):
    """Visual array data structure with cells, indices, and animation methods.

    values: list of initial values to display in cells.
    """
    def __init__(self, values, x=360, y=440, cell_width=80, cell_height=60,
                 font_size=24, index_font_size=16,
                 fill='#1e1e2e', text_color='#fff', border_color='#58C4DD',
                 show_indices=True, creation: float = 0, z: float = 0):
        self._cell_width = cell_width
        self._cell_height = cell_height
        self._x, self._y = x, y
        self._cells = []
        self._labels = []
        objects = []
        for i, val in enumerate(values):
            cx = x + i * cell_width
            cell = Rectangle(width=cell_width, height=cell_height, x=cx, y=y,
                             fill=fill, stroke=border_color, stroke_width=2,
                             creation=creation, z=z)
            lbl = _label_text(str(val), cx + cell_width / 2, y + cell_height / 2,
                              font_size, creation=creation, z=z + 0.1, fill=text_color)
            self._cells.append(cell)
            self._labels.append(lbl)
            objects.extend([cell, lbl])
            if show_indices:
                idx = _label_text(str(i), cx + cell_width / 2, y + cell_height + index_font_size + 4,
                                  index_font_size, creation=creation, z=z + 0.1, fill='#888')
                objects.append(idx)
        super().__init__(*objects, creation=creation, z=z)

    def highlight_cell(self, index, start=0, end=1, color='#58C4DD', easing=easings.there_and_back):
        """Flash-highlight a cell by index."""
        if 0 <= index < len(self._cells):
            self._cells[index].flash(start, end, color=color, easing=easing)
        return self

    def swap_cells(self, i, j, start=0, end=1, easing=easings.smooth):
        """Animate swapping the values at indices i and j."""
        if 0 <= i < len(self._labels) and 0 <= j < len(self._labels):
            li, lj = self._labels[i], self._labels[j]
            bxi = li.bbox(start)[0] + li.bbox(start)[2] / 2
            bxj = lj.bbox(start)[0] + lj.bbox(start)[2] / 2
            dx = bxj - bxi
            li.shift(dx=dx, start=start, end=end, easing=easing)
            lj.shift(dx=-dx, start=start, end=end, easing=easing)
            self._labels[i], self._labels[j] = self._labels[j], self._labels[i]
        return self

    def add_pointer(self, index, label='', color='#FF6B6B', creation=0, z=1):
        """Add a pointer arrow above a cell."""
        if 0 <= index < len(self._cells):
            cx = self._x + index * self._cell_width + self._cell_width / 2
            arrow = Arrow(x1=cx, y1=self._y - 50, x2=cx, y2=self._y - 8,
                          creation=creation, z=z, stroke=color, fill=color)
            self.objects.append(arrow)
            if label:
                lbl = _label_text(label, cx, self._y - 58, 16,
                                  creation=creation, z=z, fill=color)
                self.objects.append(lbl)
            return arrow
        return None


class Stack(VCollection):
    """Visual stack data structure (LIFO) with push/pop animations.

    values: initial values (bottom to top).
    """
    def __init__(self, values=None, x=860, y=600, cell_width=100, cell_height=50,
                 font_size=22, fill='#1e1e2e', text_color='#fff', border_color='#58C4DD',
                 creation: float = 0, z: float = 0):
        self._cell_width = cell_width
        self._cell_height = cell_height
        self._x, self._y_base = x, y
        self._font_size = font_size
        self._fill = fill
        self._text_color = text_color
        self._border_color = border_color
        self._items = []
        objects = []
        if values:
            for i, val in enumerate(values):
                cy = y - i * cell_height
                cell = Rectangle(width=cell_width, height=cell_height, x=x, y=cy,
                                 fill=fill, stroke=border_color, stroke_width=2,
                                 creation=creation, z=z)
                lbl = _label_text(str(val), x + cell_width / 2, cy + cell_height / 2,
                                  font_size, creation=creation, z=z + 0.1, fill=text_color)
                self._items.append((cell, lbl))
                objects.extend([cell, lbl])
        super().__init__(*objects, creation=creation, z=z)

    def push(self, value, start=0, end=0.5):
        """Animate pushing a value onto the stack."""
        n = len(self._items)
        slot_y = self._y_base - n * self._cell_height
        start_y = slot_y - self._cell_height * 2
        cell = Rectangle(width=self._cell_width, height=self._cell_height,
                         x=self._x, y=start_y,
                         fill=self._fill, stroke=self._border_color, stroke_width=2,
                         creation=start, z=0)
        lbl = _label_text(str(value), self._x + self._cell_width / 2,
                          start_y + self._cell_height / 2,
                          self._font_size, creation=start, z=0.1, fill=self._text_color)
        dy = slot_y - start_y
        cell.shift(dy=dy, start=start, end=end, easing=easings.ease_out_back)
        lbl.shift(dy=dy, start=start, end=end, easing=easings.ease_out_back)
        self._items.append((cell, lbl))
        self.objects.extend([cell, lbl])
        return self

    def pop(self, start=0, end=0.5):
        """Animate popping the top value from the stack."""
        if not self._items:
            return self
        cell, lbl = self._items.pop()
        cell.fadeout(start=start, end=end, change_existence=True)
        lbl.fadeout(start=start, end=end, change_existence=True)
        return self


class Queue(VCollection):
    """Visual queue data structure (FIFO) with enqueue/dequeue animations.

    values: initial values (front to back).
    """
    def __init__(self, values=None, x=360, y=440, cell_width=80, cell_height=60,
                 font_size=22, fill='#1e1e2e', text_color='#fff', border_color='#83C167',
                 creation: float = 0, z: float = 0):
        self._cell_width = cell_width
        self._cell_height = cell_height
        self._x, self._y = x, y
        self._font_size = font_size
        self._fill = fill
        self._text_color = text_color
        self._border_color = border_color
        self._items = []
        objects = []
        if values:
            for i, val in enumerate(values):
                cx = x + i * cell_width
                cell = Rectangle(width=cell_width, height=cell_height, x=cx, y=y,
                                 fill=fill, stroke=border_color, stroke_width=2,
                                 creation=creation, z=z)
                lbl = _label_text(str(val), cx + cell_width / 2, y + cell_height / 2,
                                  font_size, creation=creation, z=z + 0.1, fill=text_color)
                self._items.append((cell, lbl))
                objects.extend([cell, lbl])
        super().__init__(*objects, creation=creation, z=z)

    def enqueue(self, value, start=0, end=0.5):
        """Animate adding a value to the back of the queue."""
        n = len(self._items)
        target_cx = self._x + n * self._cell_width
        start_cx = target_cx + self._cell_width
        cell = Rectangle(width=self._cell_width, height=self._cell_height,
                         x=start_cx, y=self._y,
                         fill=self._fill, stroke=self._border_color, stroke_width=2,
                         creation=start, z=0)
        lbl = _label_text(str(value), start_cx + self._cell_width / 2,
                          self._y + self._cell_height / 2,
                          self._font_size, creation=start, z=0.1, fill=self._text_color)
        cell.shift(dx=-self._cell_width, start=start, end=end,
                   easing=easings.ease_out_back)
        lbl.shift(dx=-self._cell_width, start=start, end=end,
                  easing=easings.ease_out_back)
        self._items.append((cell, lbl))
        self.objects.extend([cell, lbl])
        return self

    def dequeue(self, start=0, end=0.5):
        """Animate removing the front value from the queue."""
        if not self._items:
            return self
        cell, lbl = self._items.pop(0)
        cell.fadeout(start=start, end=end, change_existence=True)
        lbl.fadeout(start=start, end=end, change_existence=True)
        for c, l in self._items:
            c.shift(dx=-self._cell_width, start=start, end=end, easing=easings.smooth)
            l.shift(dx=-self._cell_width, start=start, end=end, easing=easings.smooth)
        return self


class LinkedList(VCollection):
    """Visual linked list with nodes and arrow pointers.

    values: list of node values.
    """
    def __init__(self, values, x=200, y=440, node_width=80, node_height=50,
                 gap=40, font_size=22,
                 fill='#1e1e2e', text_color='#fff', border_color='#58C4DD',
                 arrow_color='#fff', creation: float = 0, z: float = 0):
        self._nodes = []
        objects = []
        step = node_width + gap
        for i, val in enumerate(values):
            nx = x + i * step
            node = Rectangle(width=node_width, height=node_height, x=nx, y=y,
                             fill=fill, stroke=border_color, stroke_width=2,
                             creation=creation, z=z)
            lbl = _label_text(str(val), nx + node_width / 2, y + node_height / 2,
                              font_size, creation=creation, z=z + 0.1, fill=text_color)
            self._nodes.append((node, lbl))
            objects.extend([node, lbl])
            if i < len(values) - 1:
                ax1 = nx + node_width
                ax2 = nx + step
                ay = y + node_height / 2
                objects.append(Arrow(x1=ax1, y1=ay, x2=ax2, y2=ay,
                                     creation=creation, z=z, stroke=arrow_color, fill=arrow_color))
        if values:
            nx = x + (len(values) - 1) * step + node_width + 10
            ny = y + node_height / 2
            objects.append(Text(text='null', x=nx, y=ny + font_size * TEXT_Y_OFFSET,
                                font_size=font_size - 4, fill='#888', stroke_width=0,
                                creation=creation, z=z))
        super().__init__(*objects, creation=creation, z=z)

    def highlight_node(self, index, start=0, end=1, color='#FF6B6B',
                       easing=easings.there_and_back):
        """Flash-highlight a node by index."""
        if 0 <= index < len(self._nodes):
            self._nodes[index][0].flash(start, end, color=color, easing=easing)
        return self


class BinaryTree(VCollection):
    """Visual binary tree with automatic layout.

    tree: nested tuple (value, left_subtree, right_subtree).
    Leaves can be just a value or (value, None, None).
    """
    def __init__(self, tree, x=960, y=120, h_spacing=200, v_spacing=100,
                 node_radius=25, font_size=20,
                 fill='#1e1e2e', text_color='#fff', border_color='#58C4DD',
                 edge_color='#888', creation: float = 0, z: float = 0):
        objects = []
        self._node_objects = []

        def _draw(node, cx, cy, spread):
            if node is None:
                return
            if isinstance(node, (int, float, str)):
                val, left, right = node, None, None
            elif isinstance(node, (tuple, list)) and len(node) >= 1:
                val = node[0]
                left = node[1] if len(node) > 1 else None
                right = node[2] if len(node) > 2 else None
            else:
                return
            child_y = cy + v_spacing
            child_spread = spread / 2
            if left is not None:
                lx = cx - child_spread
                objects.append(Line(x1=cx, y1=cy, x2=lx, y2=child_y,
                                    stroke=edge_color, stroke_width=2,
                                    creation=creation, z=z))
                _draw(left, lx, child_y, child_spread)
            if right is not None:
                rx = cx + child_spread
                objects.append(Line(x1=cx, y1=cy, x2=rx, y2=child_y,
                                    stroke=edge_color, stroke_width=2,
                                    creation=creation, z=z))
                _draw(right, rx, child_y, child_spread)
            node_obj = Circle(r=node_radius, cx=cx, cy=cy,
                              fill=fill, stroke=border_color, stroke_width=2,
                              creation=creation, z=z + 0.1)
            lbl = _label_text(str(val), cx, cy, font_size,
                              creation=creation, z=z + 0.2, fill=text_color)
            self._node_objects.append(node_obj)
            objects.extend([node_obj, lbl])

        _draw(tree, x, y, h_spacing)
        super().__init__(*objects, creation=creation, z=z)

    def highlight_node(self, index, color='#E9C46A', start=0, end=0.5):
        """Temporarily highlight a node by index (depth-first order).

        Parameters
        ----------
        index : int
            Node index in depth-first (pre-order) order.
        color : str
            Highlight fill colour.
        start, end : float
            Time range for the highlight.
        """
        if 0 <= index < len(self._node_objects):
            _flash_fill(self._node_objects[index], color, start, end, '#1e1e2e')
        return self


class Resistor(VCollection):
    """Electrical resistor symbol (zigzag line)."""
    def __init__(self, x1=400, y1=540, x2=600, y2=540, label='R',
                 creation: float = 0, z: float = 0, **styling_kwargs):
        style_kw = {'stroke': '#fff', 'stroke_width': 2} | styling_kwargs
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy) or 1
        ux, uy = _normalize(dx, dy)
        px, py = -uy, ux
        lead, zag_end = 0.25, 0.75
        n_zags, zag_amp = 6, 12
        pts = [(x1, y1), (x1 + ux * length * lead, y1 + uy * length * lead)]
        for i in range(n_zags):
            t = lead + (zag_end - lead) * (i + 0.5) / n_zags
            sign = 1 if i % 2 == 0 else -1
            pts.append((x1 + ux * length * t + px * zag_amp * sign,
                        y1 + uy * length * t + py * zag_amp * sign))
        pts.extend([(x1 + ux * length * zag_end, y1 + uy * length * zag_end), (x2, y2)])
        zigzag = Lines(*pts, creation=creation, z=z, fill_opacity=0, **style_kw)
        objects = [zigzag]
        if label:
            mx = (x1 + x2) / 2 + px * (zag_amp + 16)
            my = (y1 + y2) / 2 + py * (zag_amp + 16)
            objects.append(Text(text=label, x=mx, y=my, font_size=18,
                                fill='#aaa', stroke_width=0, text_anchor='middle',
                                creation=creation, z=z + 0.1))
        super().__init__(*objects, creation=creation, z=z)


class Capacitor(VCollection):
    """Electrical capacitor symbol (two parallel plates)."""
    def __init__(self, x1=400, y1=540, x2=600, y2=540, label='C',
                 creation: float = 0, z: float = 0, **styling_kwargs):
        style_kw = {'stroke': '#fff', 'stroke_width': 2} | styling_kwargs
        dx, dy = x2 - x1, y2 - y1
        ux, uy = _normalize(dx, dy)
        px, py = -uy, ux
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        gap, plate_h = 8, 24
        objects = [
            Line(x1=x1, y1=y1, x2=mx - ux * gap, y2=my - uy * gap,
                 creation=creation, z=z, **style_kw),
            Line(x1=mx - ux * gap + px * plate_h, y1=my - uy * gap + py * plate_h,
                 x2=mx - ux * gap - px * plate_h, y2=my - uy * gap - py * plate_h,
                 creation=creation, z=z, **style_kw),
            Line(x1=mx + ux * gap + px * plate_h, y1=my + uy * gap + py * plate_h,
                 x2=mx + ux * gap - px * plate_h, y2=my + uy * gap - py * plate_h,
                 creation=creation, z=z, **style_kw),
            Line(x1=mx + ux * gap, y1=my + uy * gap, x2=x2, y2=y2,
                 creation=creation, z=z, **style_kw),
        ]
        if label:
            lx = mx + px * (plate_h + 16)
            ly = my + py * (plate_h + 16)
            objects.append(Text(text=label, x=lx, y=ly, font_size=18,
                                fill='#aaa', stroke_width=0, text_anchor='middle',
                                creation=creation, z=z + 0.1))
        super().__init__(*objects, creation=creation, z=z)


class Inductor(VCollection):
    """Electrical inductor symbol (coil/solenoid)."""
    def __init__(self, x1=400, y1=540, x2=600, y2=540, label='L',
                 n_loops=4, creation: float = 0, z: float = 0, **styling_kwargs):
        style_kw = {'stroke': '#fff', 'stroke_width': 2} | styling_kwargs
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy) or 1
        ux, uy = _normalize(dx, dy)
        px, py = -uy, ux
        lead = 0.2
        coil_start = lead
        coil_end = 1 - lead
        coil_len = coil_end - coil_start
        # Build semicircular arcs for coil
        arc_r = length * coil_len / (2 * n_loops)
        d_parts = [f'M{x1},{y1} L{x1 + ux * length * lead},{y1 + uy * length * lead}']
        for i in range(n_loops):
            end_t = coil_start + coil_len * (i + 1) / n_loops
            ex = x1 + ux * length * end_t
            ey = y1 + uy * length * end_t
            d_parts.append(f'A{arc_r},{arc_r} 0 0 1 {ex},{ey}')
        d_parts.append(f'L{x2},{y2}')
        d_str = ' '.join(d_parts)
        from vectormation._shapes import Path
        coil = Path(d_str, x=0, y=0, creation=creation, z=z, fill_opacity=0, **style_kw)
        objects = [coil]
        if label:
            mx = (x1 + x2) / 2 + px * (arc_r + 16)
            my = (y1 + y2) / 2 + py * (arc_r + 16)
            objects.append(Text(text=label, x=mx, y=my, font_size=18,
                                fill='#aaa', stroke_width=0, text_anchor='middle',
                                creation=creation, z=z + 0.1))
        super().__init__(*objects, creation=creation, z=z)


class Diode(VCollection):
    """Electrical diode symbol (triangle with bar)."""
    def __init__(self, x1=400, y1=540, x2=600, y2=540, label='D',
                 creation: float = 0, z: float = 0, **styling_kwargs):
        style_kw = {'stroke': '#fff', 'stroke_width': 2} | styling_kwargs
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy) or 1
        ux, uy = _normalize(dx, dy)
        px, py = -uy, ux
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        tri_h, tri_w = length * 0.2, 20
        # Triangle vertices: tip pointing in direction of current flow
        tip_x = mx + ux * tri_h
        tip_y = my + uy * tri_h
        base1_x = mx - ux * tri_h + px * tri_w
        base1_y = my - uy * tri_h + py * tri_w
        base2_x = mx - ux * tri_h - px * tri_w
        base2_y = my - uy * tri_h - py * tri_w
        triangle = Polygon((base1_x, base1_y), (base2_x, base2_y), (tip_x, tip_y),
                           creation=creation, z=z, fill_opacity=0, **style_kw)
        # Bar at the tip
        bar = Line(x1=tip_x + px * tri_w, y1=tip_y + py * tri_w,
                   x2=tip_x - px * tri_w, y2=tip_y - py * tri_w,
                   creation=creation, z=z, **style_kw)
        # Lead wires
        lead1 = Line(x1=x1, y1=y1, x2=mx - ux * tri_h, y2=my - uy * tri_h,
                     creation=creation, z=z, **style_kw)
        lead2 = Line(x1=tip_x, y1=tip_y, x2=x2, y2=y2,
                     creation=creation, z=z, **style_kw)
        objects = [lead1, triangle, bar, lead2]
        if label:
            lx = mx + px * (tri_w + 16)
            ly = my + py * (tri_w + 16)
            objects.append(Text(text=label, x=lx, y=ly, font_size=18,
                                fill='#aaa', stroke_width=0, text_anchor='middle',
                                creation=creation, z=z + 0.1))
        super().__init__(*objects, creation=creation, z=z)


class LED(VCollection):
    """Light-emitting diode symbol (diode with light rays)."""
    def __init__(self, x1=400, y1=540, x2=600, y2=540, label='LED',
                 color='#FF0000', creation: float = 0, z: float = 0, **styling_kwargs):
        # Base diode
        diode = Diode(x1=x1, y1=y1, x2=x2, y2=y2, label='',
                      creation=creation, z=z, **styling_kwargs)
        dx, dy = x2 - x1, y2 - y1
        ux, uy = _normalize(dx, dy)
        px, py = -uy, ux
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        # Two small arrows (rays) coming off the diode
        ray_len = 20
        ray_offset = 15
        style_kw = {'stroke': color, 'stroke_width': 1.5}
        ray1_start = (mx + px * ray_offset, my + py * ray_offset)
        ray1_end = (ray1_start[0] + px * ray_len + ux * 5,
                    ray1_start[1] + py * ray_len + uy * 5)
        ray2_start = (mx + px * (ray_offset + 8), my + py * (ray_offset + 8))
        ray2_end = (ray2_start[0] + px * ray_len + ux * 5,
                    ray2_start[1] + py * ray_len + uy * 5)
        ray1 = Line(x1=ray1_start[0], y1=ray1_start[1],
                     x2=ray1_end[0], y2=ray1_end[1],
                     creation=creation, z=z, **style_kw)
        ray2 = Line(x1=ray2_start[0], y1=ray2_start[1],
                     x2=ray2_end[0], y2=ray2_end[1],
                     creation=creation, z=z, **style_kw)
        objects = list(diode.objects) + [ray1, ray2]
        if label:
            lx = mx + px * (ray_offset + ray_len + 16)
            ly = my + py * (ray_offset + ray_len + 16)
            objects.append(Text(text=label, x=lx, y=ly, font_size=18,
                                fill='#aaa', stroke_width=0, text_anchor='middle',
                                creation=creation, z=z + 0.1))
        super().__init__(*objects, creation=creation, z=z)


class UnitInterval(NumberLine):
    """A NumberLine from 0 to 1 — commonly used for probabilities and parameters.
    Convenience subclass with sensible defaults for [0, 1] range."""
    def __init__(self, x=360, y=540, length=600, tick_step=0.1,
                 show_labels=True, label_step=0.2, font_size=18,
                 creation: float = 0, z: float = 0, **styling_kwargs):
        super().__init__(x_range=(0, 1, tick_step), length=length,
                         x=x, y=y, include_numbers=show_labels,
                         font_size=font_size,
                         creation=creation, z=z, **styling_kwargs)


class Molecule2D(VCollection):
    """Simple 2D molecule visualization from atom positions and bonds.

    atoms: list of (element_symbol, x, y) tuples.
    bonds: list of (i, j, order) tuples (order: 1=single, 2=double, 3=triple).
    """
    _ATOM_COLORS = {
        'C': '#555', 'H': '#fff', 'O': '#FF4444', 'N': '#4444FF',
        'S': '#FFFF00', 'P': '#FF8800', 'F': '#00FF00', 'Cl': '#00FF00',
        'Br': '#882200', 'I': '#8800FF',
    }

    def __init__(self, atoms, bonds=None, scale=80, cx=960, cy=540,
                 atom_radius=20, font_size=16, creation: float = 0, z: float = 0):
        objects = []
        self._atom_objects = []
        if bonds:
            for bond in bonds:
                i, j = bond[0], bond[1]
                if i >= len(atoms) or j >= len(atoms):
                    continue
                bond_order = bond[2] if len(bond) > 2 else 1
                ax, ay = cx + atoms[i][1] * scale, cy + atoms[i][2] * scale
                bx, by = cx + atoms[j][1] * scale, cy + atoms[j][2] * scale
                d = math.hypot(bx - ax, by - ay) or 1
                perpx, perpy = -(by - ay) / d * 4, (bx - ax) / d * 4
                for k in range(bond_order):
                    offset = (k - (bond_order - 1) / 2) * 1.5
                    objects.append(Line(
                        x1=ax + perpx * offset, y1=ay + perpy * offset,
                        x2=bx + perpx * offset, y2=by + perpy * offset,
                        stroke='#888', stroke_width=2, creation=creation, z=z))
        for elem, ax_pos, ay_pos in atoms:
            sx, sy = cx + ax_pos * scale, cy + ay_pos * scale
            color = self._ATOM_COLORS.get(elem, '#888')
            atom_c = Circle(r=atom_radius, cx=sx, cy=sy,
                            fill=color, fill_opacity=0.9, stroke='#444', stroke_width=1,
                            creation=creation, z=z + 0.1)
            lbl = _label_text(elem, sx, sy, font_size, creation=creation, z=z + 0.2, fill='#fff')
            self._atom_objects.append(atom_c)
            objects.extend([atom_c, lbl])
        super().__init__(*objects, creation=creation, z=z)


class NeuralNetwork(VCollection):
    """Neural network diagram with layers of neurons connected by edges.

    Parameters
    ----------
    layer_sizes : list[int]
        Number of neurons per layer (e.g. [3, 5, 2]).
    cx, cy : float
        Center position.
    width, height : float
        Total diagram dimensions.
    neuron_radius : float
        Radius of each neuron circle.
    neuron_fill : str
        Fill color for neurons.
    edge_color : str
        Stroke color for connecting lines.
    edge_width : float
        Stroke width for connecting lines.
    """

    def __init__(self, layer_sizes, cx=960, cy=540, width=800, height=500,
                 neuron_radius=16, neuron_fill='#58C4DD', edge_color='#888',
                 edge_width=1, creation: float = 0, z: float = 0, **kwargs):
        objects = []
        self._layers = []
        n_layers = len(layer_sizes)
        if n_layers < 2:
            super().__init__(creation=creation, z=z)
            return

        # Compute neuron positions
        x_left = cx - width / 2
        x_spacing = width / (n_layers - 1) if n_layers > 1 else 0
        layer_positions = []
        for li, n_neurons in enumerate(layer_sizes):
            lx = x_left + li * x_spacing
            y_top = cy - (n_neurons - 1) * (neuron_radius * 3) / 2
            positions = [(lx, y_top + ni * neuron_radius * 3)
                         for ni in range(n_neurons)]
            layer_positions.append(positions)

        # Draw edges first (behind neurons)
        self._edges = []
        for li in range(n_layers - 1):
            for (x1, y1) in layer_positions[li]:
                for (x2, y2) in layer_positions[li + 1]:
                    edge = Line(x1, y1, x2, y2, stroke=edge_color,
                                stroke_width=edge_width, creation=creation, z=z)
                    objects.append(edge)
                    self._edges.append(edge)

        # Draw neurons on top
        for li, positions in enumerate(layer_positions):
            layer_circles = []
            for (nx, ny) in positions:
                neuron = Circle(r=neuron_radius, cx=nx, cy=ny,
                                fill=neuron_fill, fill_opacity=1,
                                stroke='#fff', stroke_width=2,
                                creation=creation, z=z + 0.1)
                objects.append(neuron)
                layer_circles.append(neuron)
            self._layers.append(layer_circles)

        super().__init__(*objects, creation=creation, z=z)

    def label_input(self, labels, font_size=20, buff=30, **kwargs):
        """Add labels to the left of input neurons."""
        if not self._layers:
            return self
        for neuron, text in zip(self._layers[0], labels):
            cx, cy = neuron.center(0)
            lbl = Text(str(text), x=cx - neuron.rx.at_time(0) - buff,
                       y=cy, font_size=font_size,
                       text_anchor='end', fill='#fff',
                       creation=0, **kwargs)
            self.add(lbl)
        return self

    def label_output(self, labels, font_size=20, buff=30, **kwargs):
        """Add labels to the right of output neurons."""
        if not self._layers:
            return self
        for neuron, text in zip(self._layers[-1], labels):
            cx, cy = neuron.center(0)
            lbl = Text(str(text), x=cx + neuron.rx.at_time(0) + buff,
                       y=cy, font_size=font_size,
                       text_anchor='start', fill='#fff',
                       creation=0, **kwargs)
            self.add(lbl)
        return self

    def activate(self, layer_idx, neuron_idx, start=0, end=1, color='#FFFF00'):
        """Animate a neuron activation (flash color)."""
        if 0 <= layer_idx < len(self._layers):
            layer = self._layers[layer_idx]
            if 0 <= neuron_idx < len(layer):
                layer[neuron_idx].flash(start=start, end=end, color=color)
        return self

    def propagate(self, start=0, duration=2, delay=0.3, color='#FFFF00'):
        """Animate a forward-propagation signal through the network."""
        for li, layer in enumerate(self._layers):
            t = start + li * delay
            for neuron in layer:
                neuron.flash(start=t, end=t + duration / len(self._layers),
                             color=color)
        return self


class Pendulum(VCollection):
    """Animated pendulum with a pivot, rod, and bob.

    Uses the small-angle approximation or exact solution for animation.

    Parameters
    ----------
    pivot_x, pivot_y : float
        Pivot point position.
    length : float
        Rod length in pixels.
    angle : float
        Initial angle in degrees from vertical.
    bob_radius : float
        Radius of the bob circle.
    period : float
        Oscillation period in seconds.
    damping : float
        Damping factor (0 = no damping, 1 = fully damped).
    start, end : float
        Animation time range.
    """

    def __init__(self, pivot_x=960, pivot_y=200, length=300, angle=30,
                 bob_radius=20, period=2.0, damping=0.0,
                 start=0, end=5, creation: float = 0, z: float = 0, **kwargs):
        self._pivot_x = pivot_x
        self._pivot_y = pivot_y
        self._length = length
        self._init_angle = math.radians(angle)
        self._period = period
        self._damping = damping
        omega = math.tau / period

        # Pivot dot
        pivot = Dot(r=5, cx=pivot_x, cy=pivot_y, fill='#888',
                    creation=creation, z=z + 0.1)

        # Rod line
        rod = Line(pivot_x, pivot_y, pivot_x, pivot_y + length,
                   stroke='#aaa', stroke_width=3, creation=creation, z=z)

        # Bob
        bob = Circle(r=bob_radius, cx=pivot_x, cy=pivot_y + length,
                     fill='#58C4DD', fill_opacity=1, stroke='#fff',
                     stroke_width=2, creation=creation, z=z + 0.2)

        # Animate bob and rod end
        init_a = self._init_angle
        damp = damping
        px, py = pivot_x, pivot_y
        L = length

        _end = end

        def bob_pos(t):
            dt = max(0, min(t, _end) - start)
            a = init_a * math.exp(-damp * dt) * math.cos(omega * dt)
            bx = px + L * math.sin(a)
            by = py + L * math.cos(a)
            return (bx, by)

        bob.c.set_onward(start, bob_pos)
        rod.p2.set_onward(start, bob_pos)

        self.pivot = pivot
        self.rod = rod
        self.bob = bob
        super().__init__(rod, pivot, bob, creation=creation, z=z)


class StandingWave(VCollection):
    """Animated standing wave between two fixed points.

    Parameters
    ----------
    x1, y1, x2, y2 : float
        Endpoints of the wave.
    amplitude : float
        Maximum displacement in pixels.
    harmonics : int
        Number of half-wavelengths (harmonic number).
    frequency : float
        Oscillation frequency in Hz.
    num_points : int
        Number of sample points along the wave.
    start, end : float
        Animation time range.
    """

    def __init__(self, x1=300, y1=540, x2=1620, y2=540,
                 amplitude=100, harmonics=3, frequency=1.0, num_points=200,
                 start=0, end=5, creation: float = 0, z: float = 0, **kwargs):
        wave_length = math.hypot(x2 - x1, y2 - y1)
        dx_norm = (x2 - x1) / wave_length if wave_length else 1
        dy_norm = (y2 - y1) / wave_length if wave_length else 0
        perp_x, perp_y = -dy_norm, dx_norm
        omega = math.tau * frequency
        k = harmonics * math.pi / wave_length if wave_length else 0

        # Fixed endpoint dots
        dot1 = Dot(r=6, cx=x1, cy=y1, fill='#888', creation=creation, z=z + 0.1)
        dot2 = Dot(r=6, cx=x2, cy=y2, fill='#888', creation=creation, z=z + 0.1)

        # Wave path
        wave = Path('', creation=creation, z=z,
                    stroke=kwargs.get('stroke', '#58C4DD'),
                    stroke_width=kwargs.get('stroke_width', 3),
                    fill_opacity=0)

        _x1, _y1, _a = x1, y1, amplitude
        _px, _py = perp_x, perp_y
        _dx, _dy = dx_norm, dy_norm
        _wl, _np = wave_length, num_points
        _start, _end = start, end

        def wave_d(t):
            dt = max(0, min(t, _end) - _start)
            parts = [f'M {_x1:.1f} {_y1:.1f}']
            for i in range(1, _np):
                s = i / _np
                dist = s * _wl
                bx = _x1 + _dx * dist
                by = _y1 + _dy * dist
                disp = _a * math.sin(k * dist) * math.cos(omega * dt)
                px = bx + _px * disp
                py = by + _py * disp
                parts.append(f'L {px:.1f} {py:.1f}')
            parts.append(f'L {x2:.1f} {y2:.1f}')
            return ' '.join(parts)

        wave.d.set_onward(start, wave_d)

        self.dot1 = dot1
        self.dot2 = dot2
        self.wave = wave
        super().__init__(wave, dot1, dot2, creation=creation, z=z)


def _flash_fill(obj, color, start, end, default='#264653'):
    """Temporarily change an object's fill colour, reverting at *end*."""
    orig = obj.styling.fill.time_func(0)
    orig_hex = '#{:02x}{:02x}{:02x}'.format(*orig) if orig else default
    obj.set_fill(color=color, start=start)
    obj.set_fill(color=orig_hex, start=end)


class ArrayViz(VCollection):
    """Visualise an array as a row of labeled cells.

    Each element is rendered as a Rectangle with centred Text inside.
    Supports animated swaps, highlights, and value changes.

    Parameters
    ----------
    values : list
        Initial values to display in the array.
    cell_size : float
        Width and height of each cell.
    x, y : float
        Position of the top-left corner of the first cell.
    colors : list or None
        Per-cell fill colours.  If *None*, all cells use *default_fill*.
    default_fill : str
        Default cell fill colour.
    show_indices : bool
        If *True*, show 0-based indices below each cell.
    """

    def __init__(self, values, cell_size=80, x=None, y=None,
                 colors=None, default_fill='#264653', show_indices=True,
                 font_size=32, creation: float = 0, z: float = 0):
        from vectormation._shapes import Rectangle, Text
        n = len(values)
        if x is None:
            x = ORIGIN[0] - n * cell_size / 2
        if y is None:
            y = ORIGIN[1] - cell_size / 2
        self._cells = []
        self._labels = []
        self._index_labels = []
        self._cell_size = cell_size
        self.values = list(values)
        objects = []
        for i, val in enumerate(values):
            cx = x + i * cell_size
            fill = colors[i] if colors and i < len(colors) else default_fill
            cell = Rectangle(cell_size, cell_size, x=cx, y=y,
                             fill=fill, fill_opacity=0.9, stroke='#fff',
                             stroke_width=2, creation=creation, z=z)
            lbl = Text(text=str(val), x=cx + cell_size / 2,
                       y=y + cell_size * 0.65,
                       font_size=font_size, fill='#fff', stroke_width=0,
                       text_anchor='middle', creation=creation, z=z + 0.1)
            self._cells.append(cell)
            self._labels.append(lbl)
            objects.extend([cell, lbl])
            if show_indices:
                idx_lbl = Text(text=str(i), x=cx + cell_size / 2,
                               y=y + cell_size + 20,
                               font_size=font_size * 0.6, fill='#888',
                               stroke_width=0, text_anchor='middle',
                               creation=creation, z=z)
                self._index_labels.append(idx_lbl)
                objects.append(idx_lbl)
        super().__init__(*objects, creation=creation, z=z)

    def highlight(self, index, start=0, end=1, color='#FFFF00'):
        """Temporarily highlight a cell by changing its fill colour."""
        if 0 <= index < len(self._cells):
            _flash_fill(self._cells[index], color, start, end)
        return self

    def swap(self, i, j, start=0, end=1, easing=easings.smooth):
        """Animate swapping the values at indices *i* and *j*.

        Cell rectangles stay in place; labels animate to the other position
        using arc paths.
        """
        if i == j or not (0 <= i < len(self._labels)) or not (0 <= j < len(self._labels)):
            return self
        a, b = self._labels[i], self._labels[j]
        ax, ay = a.x.at_time(start), a.y.at_time(start)
        bx, by = b.x.at_time(start), b.y.at_time(start)
        a.path_arc(bx, by, start=start, end=end, angle=math.pi / 3, easing=easing)
        b.path_arc(ax, ay, start=start, end=end, angle=-math.pi / 3, easing=easing)
        self._labels[i], self._labels[j] = self._labels[j], self._labels[i]
        self.values[i], self.values[j] = self.values[j], self.values[i]
        return self

    def set_value(self, index, new_val, start=0, end=None):
        """Change the displayed value of a cell.

        If *end* is given, the old text fades out and the new text fades in
        over [start, end].  Otherwise the change is instant.
        """
        if 0 <= index < len(self._labels):
            lbl = self._labels[index]
            if end is not None:
                lbl.set_text(start, end, str(new_val))
            else:
                lbl.text.set_onward(start, str(new_val))
            self.values[index] = new_val
        return self

    def pointer(self, index, label='', start=0, end=None, color='#FC6255'):
        """Add an arrow pointer above a cell.

        Returns the Arrow object (also added to self).
        """
        if not (0 <= index < len(self._cells)):
            return self
        cell = self._cells[index]
        cx = cell.x.at_time(start) + self._cell_size / 2
        cy = cell.y.at_time(start)
        arr = Arrow(x1=cx, y1=cy - 50, x2=cx, y2=cy - 8,
                    stroke=color, fill=color, fill_opacity=1,
                    stroke_width=2, creation=start)
        arr.fadein(start, start + 0.3 if end is None else end)
        self.objects.append(arr)
        if label:
            from vectormation._shapes import Text
            lbl = Text(text=label, x=cx, y=cy - 60,
                       font_size=20, fill=color, stroke_width=0,
                       text_anchor='middle', creation=start)
            lbl.fadein(start, start + 0.3 if end is None else end)
            self.objects.append(lbl)
        return arr


class LinkedListViz(VCollection):
    """Visualise a singly linked list as nodes connected by arrows.

    Parameters
    ----------
    values : list
        Initial node values.
    node_radius : float
        Radius of each node circle.
    spacing : float
        Horizontal distance between node centres.
    x, y : float
        Position of the first node's centre.
    """

    def __init__(self, values, node_radius=35, spacing=140,
                 x=None, y=540, node_fill='#264653',
                 font_size=28, creation: float = 0, z: float = 0):
        from vectormation._shapes import Circle, Text
        n = len(values)
        if x is None:
            x = ORIGIN[0] - (n - 1) * spacing / 2
        self._nodes = []
        self._labels = []
        self._arrows = []
        self._node_radius = node_radius
        self._spacing = spacing
        self.values = list(values)
        objects = []
        for i, val in enumerate(values):
            cx = x + i * spacing
            node = Circle(r=node_radius, cx=cx, cy=y,
                          fill=node_fill, fill_opacity=0.9,
                          stroke='#fff', stroke_width=2,
                          creation=creation, z=z)
            lbl = Text(text=str(val), x=cx, y=y + font_size * 0.35,
                       font_size=font_size, fill='#fff', stroke_width=0,
                       text_anchor='middle', creation=creation, z=z + 0.1)
            self._nodes.append(node)
            self._labels.append(lbl)
            objects.extend([node, lbl])
            if i > 0:
                prev_cx = x + (i - 1) * spacing
                arr = Arrow(x1=prev_cx + node_radius + 4, y1=y,
                            x2=cx - node_radius - 4, y2=y,
                            stroke='#fff', fill='#fff', fill_opacity=1,
                            stroke_width=2, creation=creation, z=z)
                self._arrows.append(arr)
                objects.append(arr)
        # Null terminator
        last_cx = x + (n - 1) * spacing
        null_lbl = Text(text='∅', x=last_cx + spacing * 0.6,
                        y=y + font_size * 0.35,
                        font_size=font_size, fill='#888', stroke_width=0,
                        text_anchor='middle', creation=creation, z=z)
        null_arr = Arrow(x1=last_cx + node_radius + 4, y1=y,
                         x2=last_cx + spacing * 0.6 - 15, y2=y,
                         stroke='#888', fill='#888', fill_opacity=1,
                         stroke_width=2, creation=creation, z=z)
        objects.extend([null_arr, null_lbl])
        self._null_lbl = null_lbl
        self._null_arr = null_arr
        super().__init__(*objects, creation=creation, z=z)

    def highlight(self, index, start=0, end=1, color='#FFFF00'):
        """Temporarily highlight a node."""
        if 0 <= index < len(self._nodes):
            _flash_fill(self._nodes[index], color, start, end)
        return self

    def traverse(self, start=0, delay=0.5, color='#FFFF00'):
        """Animate traversing each node in sequence.

        Each node lights up for *delay* seconds in order.
        """
        for i in range(len(self._nodes)):
            t = start + i * delay
            self.highlight(i, t, t + delay, color)
        return self


class StackViz(VCollection):
    """Visualise a stack (LIFO) as vertically stacked cells.

    Parameters
    ----------
    values : list
        Initial values (bottom to top).
    cell_width, cell_height : float
        Dimensions of each cell.
    x, y : float
        Position of the bottom-left corner of the bottom cell.
    """

    def __init__(self, values, cell_width=120, cell_height=50,
                 x=None, y=None, fill='#264653',
                 font_size=28, creation: float = 0, z: float = 0):
        from vectormation._shapes import Rectangle, Text
        n = len(values)
        if x is None:
            x = ORIGIN[0] - cell_width / 2
        if y is None:
            y = ORIGIN[1] + n * cell_height / 2
        self._cell_width = cell_width
        self._cell_height = cell_height
        self._base_x = x
        self._base_y = y
        self._fill = fill
        self._font_size = font_size
        self._stack_cells = []
        self._stack_labels = []
        self._z = z
        self.values = list(values)
        objects = []
        for i, val in enumerate(values):
            cy = y - i * cell_height
            cell = Rectangle(cell_width, cell_height, x=x, y=cy,
                              fill=fill, fill_opacity=0.9, stroke='#fff',
                              stroke_width=2, creation=creation, z=z)
            lbl = Text(text=str(val), x=x + cell_width / 2,
                       y=cy + cell_height * 0.65,
                       font_size=font_size, fill='#fff', stroke_width=0,
                       text_anchor='middle', creation=creation, z=z + 0.1)
            self._stack_cells.append(cell)
            self._stack_labels.append(lbl)
            objects.extend([cell, lbl])
        # "TOP" label
        top_y = y - (n - 1) * cell_height if n > 0 else y
        self._top_arrow = Arrow(x1=x - 50, y1=top_y + cell_height / 2,
                                x2=x - 8, y2=top_y + cell_height / 2,
                                stroke='#FC6255', fill='#FC6255', fill_opacity=1,
                                stroke_width=2, creation=creation, z=z)
        top_lbl = Text(text='TOP', x=x - 58, y=top_y + cell_height * 0.65,
                       font_size=font_size * 0.7, fill='#FC6255', stroke_width=0,
                       text_anchor='end', creation=creation, z=z)
        self._top_label = top_lbl
        objects.extend([self._top_arrow, top_lbl])
        super().__init__(*objects, creation=creation, z=z)

    def push(self, value, start=0, end=0.5):
        """Animate pushing a value onto the stack."""
        from vectormation._shapes import Rectangle, Text
        n = len(self._stack_cells)
        cy = self._base_y - n * self._cell_height
        cell = Rectangle(self._cell_width, self._cell_height,
                         x=self._base_x, y=cy,
                         fill=self._fill, fill_opacity=0.9, stroke='#fff',
                         stroke_width=2, creation=start, z=self._z)
        lbl = Text(text=str(value), x=self._base_x + self._cell_width / 2,
                   y=cy + self._cell_height * 0.65,
                   font_size=self._font_size, fill='#fff', stroke_width=0,
                   text_anchor='middle', creation=start, z=self._z + 0.1)
        cell.fadein(start, end)
        lbl.fadein(start, end)
        self._stack_cells.append(cell)
        self._stack_labels.append(lbl)
        self.values.append(value)
        self.objects.extend([cell, lbl])
        # Move TOP arrow up
        self._top_arrow.shift(dy=-self._cell_height, start=start, end=end)
        self._top_label.shift(dy=-self._cell_height, start=start, end=end)
        return self

    def pop(self, start=0, end=0.5):
        """Animate popping the top value from the stack."""
        if not self._stack_cells:
            return self
        cell = self._stack_cells.pop()
        lbl = self._stack_labels.pop()
        self.values.pop()
        cell.fadeout(start, end)
        lbl.fadeout(start, end)
        # Move TOP arrow down
        if self._stack_cells:
            self._top_arrow.shift(dy=self._cell_height, start=start, end=end)
            self._top_label.shift(dy=self._cell_height, start=start, end=end)
        return self


class QueueViz(VCollection):
    """Visualise a queue (FIFO) as a horizontal row of cells.

    Parameters
    ----------
    values : list
        Initial values (front on the left, back on the right).
    cell_width, cell_height : float
        Dimensions of each cell.
    x, y : float
        Position of the top-left corner of the front cell.
    """

    def __init__(self, values, cell_width=80, cell_height=60,
                 x=None, y=None, fill='#264653',
                 font_size=28, creation: float = 0, z: float = 0):
        from vectormation._shapes import Rectangle, Text
        n = len(values)
        if x is None:
            x = ORIGIN[0] - n * cell_width / 2
        if y is None:
            y = ORIGIN[1] - cell_height / 2
        self._cell_width = cell_width
        self._cell_height = cell_height
        self._base_x = x
        self._base_y = y
        self._fill = fill
        self._font_size = font_size
        self._z = z
        self._queue_cells = []
        self._queue_labels = []
        self.values = list(values)
        objects = []
        for i, val in enumerate(values):
            cx = x + i * cell_width
            cell = Rectangle(cell_width, cell_height, x=cx, y=y,
                              fill=fill, fill_opacity=0.9, stroke='#fff',
                              stroke_width=2, creation=creation, z=z)
            lbl = _label_text(str(val), cx + cell_width / 2, y + cell_height / 2,
                              font_size, creation=creation, z=z + 0.1)
            self._queue_cells.append(cell)
            self._queue_labels.append(lbl)
            objects.extend([cell, lbl])
        # FRONT / BACK labels
        front_x = x - 8
        back_x = x + n * cell_width + 8
        mid_y = y + cell_height * 0.65
        self._front_label = Text(text='FRONT', x=front_x, y=mid_y,
                                  font_size=int(font_size * 0.7), fill='#50FA7B',
                                  stroke_width=0, text_anchor='end',
                                  creation=creation, z=z)
        self._back_label = Text(text='BACK', x=back_x, y=mid_y,
                                 font_size=int(font_size * 0.7), fill='#FC6255',
                                 stroke_width=0, text_anchor='start',
                                 creation=creation, z=z)
        objects.extend([self._front_label, self._back_label])
        super().__init__(*objects, creation=creation, z=z)

    def enqueue(self, value, start=0, end=0.5):
        """Animate adding a value to the back of the queue."""
        from vectormation._shapes import Rectangle, Text
        n = len(self._queue_cells)
        cx = self._base_x + n * self._cell_width
        cell = Rectangle(self._cell_width, self._cell_height,
                         x=cx, y=self._base_y,
                         fill=self._fill, fill_opacity=0.9, stroke='#fff',
                         stroke_width=2, creation=start, z=self._z)
        lbl = _label_text(str(value), cx + self._cell_width / 2,
                          self._base_y + self._cell_height / 2,
                          self._font_size, creation=start, z=self._z + 0.1)
        cell.fadein(start, end)
        lbl.fadein(start, end)
        self._queue_cells.append(cell)
        self._queue_labels.append(lbl)
        self.values.append(value)
        self.objects.extend([cell, lbl])
        self._back_label.shift(dx=self._cell_width, start=start, end=end)
        return self

    def dequeue(self, start=0, end=0.5):
        """Animate removing the front value from the queue."""
        if not self._queue_cells:
            return self
        cell = self._queue_cells.pop(0)
        lbl = self._queue_labels.pop(0)
        self.values.pop(0)
        cell.fadeout(start, end)
        lbl.fadeout(start, end)
        # Slide remaining cells left
        for c, l in zip(self._queue_cells, self._queue_labels):
            c.shift(dx=-self._cell_width, start=start, end=end)
            l.shift(dx=-self._cell_width, start=start, end=end)
        self._back_label.shift(dx=-self._cell_width, start=start, end=end)
        return self

    def highlight(self, index, color='#E9C46A', start=0, end=0.5):
        """Temporarily highlight a cell at *index*."""
        if 0 <= index < len(self._queue_cells):
            _flash_fill(self._queue_cells[index], color, start, end, self._fill)
        return self


def parse_args():
    """Parse common CLI arguments for VectorMation scripts."""
    import argparse
    parser = argparse.ArgumentParser(description='VectorMation animation script')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--port', type=int, default=8765, help='Browser viewer port')
    parser.add_argument('--fps', type=int, default=60, help='Frames per second')
    parser.add_argument('--no-display', action='store_true', help='Skip browser display')
    parser.add_argument('-o', '--output', type=str, default=None, help='Output file path (e.g. out.mp4)')
    parser.add_argument('-d', '--duration', type=float, default=None, help='Animation duration in seconds')
    parser.add_argument('--start', type=float, default=None, help='Start time in seconds')
    parser.add_argument('--end', type=float, default=None, help='End time in seconds')
    parser.add_argument('--hot-reload', action='store_true', help='Enable hot reload in browser')
    return parser.parse_args()

