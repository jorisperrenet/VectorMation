"""Composite classes: MorphObject, TexObject, NumberLine, Table, Matrix, etc."""
from collections import defaultdict

import vectormation.easings as easings
import vectormation.attributes as attributes
import vectormation.style as style
import vectormation.morphing as morphing
from vectormation._constants import SMALL_BUFF, TEXT_Y_OFFSET, ORIGIN, _label_text
from vectormation._base import VObject, VCollection, _norm_dir
from vectormation._base_helpers import _norm_above_below
from vectormation._shapes import Polygon, Dot, Rectangle, Line, Lines, Text, Path
from vectormation._arrows import Arrow, Brace
from vectormation._svg_utils import from_svg
from vectormation._axes_helpers import _TICK_FONT_SIZE, _HIGHLIGHT_STYLE

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
        if not isinstance(morph_from, VCollection):
            raise TypeError(f'morph_from must be a VObject or VCollection, got {type(morph_from).__name__}')
        if not isinstance(morph_to, VCollection):
            raise TypeError(f'morph_to must be a VObject or VCollection, got {type(morph_to).__name__}')

        def _flatten(collection, time=None):
            """Flatten nested VCollections. When *time* is set, snapshot DynamicObjects."""
            for obj in collection:
                if isinstance(obj, VCollection):
                    yield from _flatten(obj, time)
                elif time is not None and isinstance(obj, DynamicObject):
                    inner = obj._func(time)
                    if isinstance(inner, VCollection):
                        yield from _flatten(inner, time)
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
        paths_from = [(morphing.Path(obj.path(start)), obj.styling) for obj in _flatten(morph_from, start)]
        paths_to = [(morphing.Path(obj.path(end)), obj.styling) for obj in _flatten(morph_to, end)]
        obj_from = morphing.Paths(*paths_from)
        obj_to = morphing.Paths(*paths_to)

        mapping = obj_from.morph(obj_to, start=start, end=end, easing=easing)

        # Compute rotation center from source/target bounding boxes
        if rotation_degrees != 0:
            bbox_from = morph_from.bbox(start)
            bbox_to = morph_to.bbox(end)
            # Average the centers of both bounding boxes
            cx = ((bbox_from[0] + bbox_from[2] / 2) + (bbox_to[0] + bbox_to[2] / 2)) / 2
            cy = ((bbox_from[1] + bbox_from[3] / 2) + (bbox_to[1] + bbox_to[3] / 2)) / 2
        else:
            cx, cy = 0, 0

        # Convert morphing data into displayable Path objects
        # Group by compound_id to recombine subpaths from compound paths (e.g. letters with holes)
        groups = defaultdict(list)
        for path_func, styling_from, styling_to, compound_id in mapping:
            groups[compound_id].append((path_func, styling_from, styling_to))

        def _make_d_func(pfs):
            dur = max(end - start, 1e-9)
            if len(pfs) == 1:
                pf = pfs[0]
                return lambda t: pf((t - start) / dur)
            return lambda t: ' '.join(pf((t - start) / dur) for pf in pfs)

        objects = []
        for group_entries in groups.values():
            path_funcs = [e[0] for e in group_entries]
            new = Path('', x=0, y=0, creation=start, z=z)
            new.show.set_onward(end, False)
            new.d.set(start, end, _make_d_func(path_funcs))
            new.styling = group_entries[0][1].interpolate(
                group_entries[0][2], start, end, easing=easing,
                rotation_degrees=rotation_degrees, rotation_center=(cx, cy)
            )
            if len(path_funcs) > 1:
                new.styling.fill_rule = attributes.String(start, 'evenodd')
            objects.append(new)

        super().__init__(*objects, creation=start, z=z)
        self.show.set_onward(end, False)

    def __repr__(self):
        return 'MorphObject()'

def counterclockwise_morph(source, target, start: float = 0, end: float = 1, z: float = 0, easing=easings.smooth):
    """Convenience: morph with a 180-degree counterclockwise rotation."""
    return MorphObject(source, target, start=start, end=end, z=z,
                       easing=easing, rotation_degrees=-180)


class LabeledDot(VCollection):
    """Dot with a centered text label."""
    def __init__(self, label='', r: float = 24, cx=ORIGIN[0], cy=ORIGIN[1], creation: float = 0, z: float = 0, font_size=None, **styling_kwargs):
        dot_kw = {k: v for k, v in styling_kwargs.items() if k != 'fill'}
        dot_fill = styling_kwargs.get('fill', '#83C167')
        dot = Dot(r=r, cx=cx, cy=cy, creation=creation, z=z, fill=dot_fill, **dot_kw)
        if font_size is None:
            font_size = r * 0.9
        text = _label_text(label, cx, cy, font_size, creation=creation, z=z)
        super().__init__(dot, text, creation=creation, z=z)
        self.dot = dot
        self.label = text

    def __repr__(self):
        return 'LabeledDot()'

def _strip_tex_commands(tex: str) -> str:
    """Strip LaTeX commands and braces to get approximate visible characters.

    Removes backslash-commands (e.g. \\frac, \\alpha), curly braces, dollar signs,
    and whitespace, leaving only the characters that dvisvgm renders as glyphs.
    """
    import re
    # Remove LaTeX commands like \frac, \alpha, \text, etc.
    result = re.sub(r'\\[a-zA-Z]+\*?', '', tex)
    # Remove remaining braces, dollar signs, carets, underscores, spaces
    result = re.sub(r'[{}$^_\s]', '', result)
    return result


class TexObject(VCollection):
    """Renders LaTeX content as SVG paths.

    Uses built-in Computer Modern glyphs when possible (no LaTeX needed).
    Falls back to full LaTeX compilation via dvisvgm for complex expressions.
    """
    def __init__(self, to_render, x: float = 0, y: float = 0, font_size: float = 48, creation: float = 0, z: float = 0, **styles):
        self._tex = to_render
        t2c = styles.pop('t2c', None)

        chars = self._try_glyph_assembly(to_render, font_size, creation, styles)
        if chars is None:
            chars = self._compile_latex(to_render, font_size, creation, styles)

        self._visible_tex = _strip_tex_commands(to_render)

        super().__init__(*chars, creation=creation, z=z)

        self.x = attributes.Real(creation, x)
        self.y = attributes.Real(creation, y)

        xmin, ymin, _, _ = self.bbox(creation)
        for obj in self.objects:
            obj.styling.dx.add_onward(creation, lambda t, _xm=xmin: self.x.at_time(t) - _xm)
            obj.styling.dy.add_onward(creation, lambda t, _ym=ymin: self.y.at_time(t) - _ym)

        if t2c is not None:
            self.set_color_by_tex(t2c, creation)

    @staticmethod
    def _try_glyph_assembly(to_render, font_size, creation, styles):
        """Try to assemble from built-in/cached glyphs. Returns list of VObjects or None."""
        from vectormation._tex_glyphs import _tokenize_tex, _assemble, _resolve_tex_dir

        inner = to_render
        if inner.startswith('$') and inner.endswith('$'):
            inner = inner[1:-1]

        tokens = _tokenize_tex(inner)
        if tokens is None:
            return None

        tex_dir = _resolve_tex_dir()
        result = _assemble(tokens, 0, 0, font_size, creation, tex_dir, 'left', styles)
        if result is None:
            return None
        return list(result.objects)

    @staticmethod
    def _compile_latex(to_render, font_size, creation, styles):
        """Full LaTeX compilation fallback. Returns list of VObjects."""
        from vectormation.tex_file_writing import get_characters
        from vectormation._tex_glyphs import _resolve_tex_dir

        tex_dir = _resolve_tex_dir()
        char_viewbox, raw_chars = get_characters(tex_dir, to_render, 'latex', '')

        vb_height = abs(char_viewbox[3]) if char_viewbox[3] else 1
        base_scale = font_size / vb_height
        user_sx = styles.pop('scale_x', 1)
        user_sy = styles.pop('scale_y', 1)

        st = {'stroke_width': 0, 'fill': '#fff',
              'scale_x': base_scale * user_sx, 'scale_y': base_scale * user_sy} | styles
        return [from_svg(char, **st) for char in raw_chars]

    def get_part_by_tex(self, substring: str) -> 'VCollection':
        """Return a VCollection of character objects whose source LaTeX matches *substring*.

        The mapping is approximate: LaTeX commands are stripped from both the full
        TeX string and the query, and the resulting visible characters are matched
        positionally against the rendered glyph objects.

        Returns an empty VCollection when no match is found or the number of glyphs
        does not align with the visible-character count.
        """
        visible = self._visible_tex
        query = _strip_tex_commands(substring) if substring else substring
        if not query:
            return VCollection()

        matched: list = []
        start = 0
        while True:
            idx = visible.find(query, start)
            if idx == -1:
                break
            end = idx + len(query)
            # Collect glyph objects corresponding to this span
            span_objs = self.objects[idx:end]
            matched.extend(span_objs)
            start = end

        return VCollection(*matched) if matched else VCollection()

    def set_color_by_tex(self, tex_to_color_map: dict, start: float = 0) -> 'TexObject':
        """Color character objects by matching TeX substrings.

        For each key in *tex_to_color_map*, calls ``get_part_by_tex(key)`` and
        sets the fill color of the returned characters to the corresponding value.
        Returns *self* for chaining.
        """
        for substring, color in tex_to_color_map.items():
            part = self.get_part_by_tex(substring)
            for obj in part.objects:
                obj.set_fill(color, start=start)
        return self

    # Manim compatibility alias
    set_color_by_tex_to_color_map = set_color_by_tex

    def __repr__(self):
        return f'TexObject({self._tex!r})'

class SplitTexObject:
    """Renders multiple lines of LaTeX, each as a separate TexObject.
    Supports indexing, iteration, and conversion to a single VCollection."""
    def __init__(self, *lines, x: float = 0, y: float = 0, line_spacing: float = 60, creation: float = 0, **styles):
        self.lines = [TexObject(line, x=x, y=y + i * line_spacing, creation=creation, **styles)
                      for i, line in enumerate(lines)]

    def __repr__(self):
        return f'SplitTexObject({len(self.lines)} lines)'
    def __iter__(self): return iter(self.lines)
    def __getitem__(self, idx): return self.lines[idx]
    def __len__(self): return len(self.lines)

class NumberLine(VCollection):
    """A number line with ticks and labels, with optional endpoint arrows."""
    def __init__(self, x_range=(-5, 5, 1), length: float = 720, x: float = 240, y=ORIGIN[1],
                 include_arrows=True, include_numbers=True,
                 tick_size=2*SMALL_BUFF, font_size=_TICK_FONT_SIZE,
                 creation: float = 0, z: float = 0, **styling_kwargs):
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
        n_ticks = min(round((x_end - x_start) / x_step), 1000)
        for i in range(n_ticks + 1):
            val = round(x_start + i * x_step, 10)
            sx = x + (val - x_start) / (x_end - x_start) * length
            objects.append(Line(x1=sx, y1=y - tick_size/2, x2=sx, y2=y + tick_size/2,
                                creation=creation, z=z, stroke='#fff', stroke_width=3))
            if include_numbers:
                label = f'{val:g}'
                from vectormation._tex_glyphs import assemble_tex_glyphs
                lbl = assemble_tex_glyphs(label, sx, y + tick_size/2 + font_size * 0.5 + 2,
                                          font_size, creation=creation, anchor='center',
                                          fill='#aaa')
                if lbl is not None:
                    objects.append(lbl)
                else:
                    objects.append(Text(text=label, x=sx - len(label) * font_size * 0.15,
                                        y=y + tick_size/2 + font_size + 2,
                                        font_size=font_size, creation=creation, z=z,
                                        fill='#aaa', stroke_width=0))

        super().__init__(*objects, creation=creation, z=z)

    def number_to_point(self, value, time: float = 0):
        """Convert a number on the line to an SVG (x, y) coordinate."""
        span = self.x_end - self.x_start
        if span == 0:
            return (self.origin_x, self.origin_y)
        t = (value - self.x_start) / span
        return (self.origin_x + t * self.length, self.origin_y)

    def point_to_number(self, x, y=None):  # noqa: ARG002 (y for API compat)
        """Convert an SVG x coordinate (or (x,y) tuple) back to a value on the line."""
        if isinstance(x, (tuple, list)): x = x[0]
        span = self.x_end - self.x_start
        if self.length == 0:
            return self.x_start
        t = (x - self.origin_x) / self.length
        return self.x_start + t * span

    def get_range(self):
        """Return ``(x_start, x_end)`` tuple."""
        return (self.x_start, self.x_end)

    def get_range_length(self):
        """Return the span of the number line (``x_end - x_start``)."""
        return self.x_end - self.x_start

    def snap_to_tick(self, value):
        """Return the nearest tick mark value, clamped to ``[x_start, x_end]``."""
        if value <= self.x_start: return self.x_start
        if value >= self.x_end: return self.x_end
        k = round((value - self.x_start) / self.x_step)
        return max(self.x_start, min(self.x_end, self.x_start + k * self.x_step))

    @staticmethod
    def _set_pointer_verts(ptr, pos_func, size, start):
        """Bind pointer triangle vertices to track *pos_func*."""
        hs = size / 2
        ptr.vertices[0].set_onward(start, lambda t: (p := pos_func(t), (p[0] - hs, p[1] - size - 2))[1])
        ptr.vertices[1].set_onward(start, lambda t: (p := pos_func(t), (p[0] + hs, p[1] - size - 2))[1])
        ptr.vertices[2].set_onward(start, lambda t: (p := pos_func(t), (p[0], p[1] - 2))[1])

    def add_pointer(self, value, label=None, color='#FF6B6B', size: float = 12,
                     creation: float = 0, z: float = 1):
        """Add an animated pointer (triangle) above the number line at *value*."""
        px, py = self.number_to_point(
            value.at_time(creation) if hasattr(value, 'at_time') else value
        )
        ptr = Polygon(
            (px - size / 2, py - size - 2),
            (px + size / 2, py - size - 2),
            (px, py - 2),
            creation=creation, z=z, fill=color, stroke_width=0,
        )

        def _ptr_pos(time):
            v = value.at_time(time) if hasattr(value, 'at_time') else value
            return self.number_to_point(v)

        self._set_pointer_verts(ptr, _ptr_pos, size, creation)

        objects = [ptr]
        if label is not None:
            lbl = Text(text=str(label), x=px, y=py - size - 18,
                        font_size=20, fill=color, stroke_width=0,
                        text_anchor='middle', creation=creation, z=z + 0.1)
            lbl.x.set_onward(creation, lambda t: _ptr_pos(t)[0])
            lbl.y.set_onward(creation, lambda t: _ptr_pos(t)[1] - size - 18)
            objects.append(lbl)

        group = VCollection(*objects, creation=creation, z=z)
        self.objects.append(group)
        return group

    def animate_pointer(self, pointer_group, target_value, start: float = 0, end: float = 1, easing=easings.smooth):
        """Animate a pointer (from add_pointer) to a new value."""
        dur = end - start
        if dur <= 0 or not pointer_group.objects:
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

    def _make_range_rect(self, sv, ev, color, height, opacity, creation, z, **kwargs):
        """Create a range highlight rectangle between two values."""
        x1, y = self.number_to_point(sv)
        x2, _ = self.number_to_point(ev)
        rect = Rectangle(abs(x2 - x1), height, x=min(x1, x2), y=y - height / 2,
                         creation=creation, z=z,
                         fill=color, fill_opacity=opacity, stroke_width=0, **kwargs)
        self.objects.append(rect)
        return rect

    def add_segment(self, start_val, end_val, color='#58C4DD', height: float = 8, creation: float = 0, z: float = 1):
        """Highlight a range on the number line with a filled rectangle."""
        return self._make_range_rect(start_val, end_val, color, height, 0.7, creation, z)

    def add_dot_at(self, value, color='#FF6B6B', radius: float = 8, creation: float = 0, **kwargs):
        """Add a colored dot at a specific value on the number line."""
        px, py = self.number_to_point(value)
        kw = {'fill': color, 'stroke_width': 0} | kwargs
        dot = Dot(cx=px, cy=py, r=radius, creation=creation, **kw)
        self.objects.append(dot)
        return dot

    def highlight_range(self, start_val, end_val, color='#FFFF00',
                        height: float = 16, opacity: float = 0.4, creation: float = 0, z: float = 1, **kwargs):
        """Highlight a numeric range on the number line with a colored rectangle."""
        sv = max(self.x_start, min(self.x_end, start_val))
        ev = max(self.x_start, min(self.x_end, end_val))
        if sv > ev:
            sv, ev = ev, sv
        return self._make_range_rect(sv, ev, color, height, opacity, creation, z, **kwargs)

    def add_label(self, value, text, buff: float = 10, font_size: float = 24, side='below', creation: float = 0, **kwargs):
        """Add a text label at the given value on the number line."""
        side = _norm_above_below(side, 'below')
        px, py = self.number_to_point(value)
        kw = {'fill': '#fff', 'stroke_width': 0, 'text_anchor': 'middle'} | kwargs
        ty = py + (-1 if side == 'above' else 1) * (buff + font_size)
        lbl = Text(text=str(text), x=px, y=ty,
                   font_size=font_size, creation=creation, **kw)
        self.objects.append(lbl)
        return self

    def add_tick_labels_range(self, start_val, end_val, step, format_func=None,
                              font_size=None, creation: float = 0):
        """Batch-add tick labels for values from *start_val* to *end_val*."""
        if step == 0:
            raise ValueError('step cannot be zero')
        if format_func is None:
            format_func = str
        if font_size is None:
            font_size = _TICK_FONT_SIZE
        n_ticks = round((end_val - start_val) / step)
        for i in range(n_ticks + 1):
            val = start_val + i * step
            px, py = self.number_to_point(val)
            label_text = format_func(val)
            lbl = Text(text=label_text, x=px, y=py + SMALL_BUFF + font_size,
                       font_size=font_size, creation=creation,
                       fill='#fff', stroke_width=0, text_anchor='middle')
            self.objects.append(lbl)
        return self

    def add_brace(self, x1, x2, label=None, direction='down', **kwargs):
        """Add a curly brace between two values on the number line."""
        direction = _norm_dir(direction, 'down')
        p1x, p1y = self.number_to_point(x1)
        p2x, _ = self.number_to_point(x2)
        lx, rx_ = min(p1x, p2x), max(p1x, p2x)
        w = rx_ - lx
        # Create a temporary rectangle as the brace target
        target = Rectangle(w, 1, x=lx, y=p1y - 0.5)
        brace = Brace(target, direction=direction, label=label, **kwargs)
        self.objects.append(brace)
        return brace

    def add_interval_bracket(self, x1, x2, closed_left=True, closed_right=True,
                              creation: float = 0, **kwargs):
        """Show an interval on the number line with bracket notation."""
        style_kw = {'stroke': '#58C4DD', 'stroke_width': 3} | kwargs
        p1x, p1y = self.number_to_point(x1)
        p2x, _ = self.number_to_point(x2)
        # Offset above the number line
        offset_y = -20
        ly = p1y + offset_y
        bar = Line(x1=p1x, y1=ly, x2=p2x, y2=ly, creation=creation, **style_kw)
        left_char = '[' if closed_left else '('
        right_char = ']' if closed_right else ')'
        font_size = 24
        left_text = Text(text=left_char, x=p1x - font_size * 0.3, y=ly + font_size * TEXT_Y_OFFSET,
                         font_size=font_size, creation=creation,
                         fill=style_kw.get('stroke', '#58C4DD'), stroke_width=0)
        right_text = Text(text=right_char, x=p2x + font_size * 0.05, y=ly + font_size * TEXT_Y_OFFSET,
                          font_size=font_size, creation=creation,
                          fill=style_kw.get('stroke', '#58C4DD'), stroke_width=0)
        group = VCollection(bar, left_text, right_text, creation=creation)
        self.objects.append(group)
        return group

    def animate_add_tick(self, value, start: float = 0, end: float = 1, label=None, easing=None):
        """Dynamically add a tick mark at *value* with a pop-in animation."""
        easing = easing or easings.smooth
        px, py = self.number_to_point(value)
        tick_size = 2 * SMALL_BUFF
        tick = Line(x1=px, y1=py - tick_size / 2, x2=px, y2=py + tick_size / 2,
                    creation=start, stroke='#fff', stroke_width=3)
        tick.fadein(start=start, end=end, easing=easing)
        self.objects.append(tick)

        if label is not None:
            font_size = _TICK_FONT_SIZE
            label_str = str(label)
            lbl = Text(text=label_str, x=px - len(label_str) * font_size * 0.15,
                        y=py + tick_size / 2 + font_size + 2,
                        font_size=font_size, creation=start,
                        fill='#aaa', stroke_width=0)
            lbl.fadein(start=start, end=end, easing=easing)
            self.objects.append(lbl)

        return self

    def add_animated_pointer(self, value_func, start: float = 0, end: float | None = None, color='#FFFF00',
                             label=True):
        """Add a pointer (triangle) that tracks a dynamic value function over time."""
        size = 12
        _cache = [None, None]  # [last_t, last_result]

        def _ptr_pos(t):
            if _cache[0] != t:
                _cache[0] = t
                _cache[1] = self.number_to_point(value_func(t))
            return _cache[1]

        px, py = _ptr_pos(start)
        ptr = Polygon(
            (px - size / 2, py - size - 2),
            (px + size / 2, py - size - 2),
            (px, py - 2),
            creation=start, z=1, fill=color, stroke_width=0,
        )
        self._set_pointer_verts(ptr, _ptr_pos, size, start)
        if end is not None:
            ptr._hide_from(end)
        self.objects.append(ptr)

        if label:
            lbl = Text(text=str(round(value_func(start), 2)), x=px, y=py - size - 18,
                        font_size=20, fill=color, stroke_width=0,
                        text_anchor='middle', creation=start, z=1.1)
            lbl.x.set_onward(start, lambda t: _ptr_pos(t)[0])
            lbl.y.set_onward(start, lambda t: _ptr_pos(t)[1] - size - 18)
            lbl.text.set_onward(start, lambda t: str(round(value_func(t), 2)))
            if end is not None:
                lbl._hide_from(end)
            self.objects.append(lbl)

        return self

    def animate_range(self, new_start, new_end, start: float = 0, end: float = 1, easing=None):
        """Animate the number line's visible range to ``[new_start, new_end]``."""
        _easing = easing or easings.smooth
        old_start, old_end = self.x_start, self.x_end
        length = self.length
        ox = self.origin_x
        dur = end - start
        old_span = old_end - old_start
        new_span = new_end - new_start

        def _old_val_to_x(val):
            return ox + (val - old_start) / old_span * length if old_span else ox

        def _new_val_to_x(val):
            return ox + (val - new_start) / new_span * length if new_span else ox

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
                val = old_start + (cur_x - ox) / (length or 1) * (old_end - old_start)
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

        # Update range properties so number_to_point uses new values
        self.x_start, self.x_end = new_start, new_end

        return self

    def __repr__(self):
        return f'NumberLine([{self.x_start}, {self.x_end}], step={self.x_step})'

class _GridAccessMixin:
    """Shared accessor and highlight helpers for Table and Matrix."""
    entries: list

    def get_entry(self, row, col):
        """Return the VObject at *row*, *col*."""
        if not (0 <= row < len(self.entries)):
            raise IndexError(f"row index {row} out of range (0..{len(self.entries) - 1})")
        if not (0 <= col < len(self.entries[row])):
            raise IndexError(f"column index {col} out of range (0..{len(self.entries[row]) - 1})")
        return self.entries[row][col]

    def get_row(self, row):
        """Return a VCollection of all entries in *row*."""
        return VCollection(*self.entries[row])

    def get_column(self, col):
        """Return a VCollection of all entries in column *col*."""
        return VCollection(*(row[col] for row in self.entries if col < len(row)))

    def _flash(self, entries, start, end, color, easing=easings.there_and_back):
        for e in entries: e.flash(start, end, color=color, easing=easing)
        return self

    def highlight_entry(self, row, col, start: float = 0, end: float = 1, color='#FFD700', easing=easings.there_and_back):
        """Flash-highlight a single entry."""
        return self._flash([self.entries[row][col]], start, end, color, easing)

    def highlight_row(self, row, start: float = 0, end: float = 1, color='#FFD700', easing=easings.there_and_back):
        """Flash-highlight all entries in a row."""
        return self._flash(self.entries[row], start, end, color, easing)

    def highlight_column(self, col, start: float = 0, end: float = 1, color='#FFD700', easing=easings.there_and_back):
        """Flash-highlight all entries in a column."""
        return self._flash([row[col] for row in self.entries if col < len(row)], start, end, color, easing)

    def set_entry_value(self, row, col, new_value, start: float = 0):
        """Change the text of an entry at the given time."""
        self.entries[row][col].text.set_onward(start, str(new_value))
        return self


class Table(_GridAccessMixin, VCollection):
    """Table for displaying tabular data with optional row/column labels."""
    def __init__(self, data, row_labels=None, col_labels=None,
                 x: float = 120, y: float = 60, cell_width: float = 160, cell_height: float = 60,
                 font_size: float = 24, creation: float = 0, z: float = 0, **styling_kwargs):
        if not data:
            raise ValueError("Table requires non-empty data")
        rows = len(data)
        cols = len(data[0])
        if any(len(row) != cols for row in data):
            raise ValueError("Table: all rows must have the same number of columns")
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

        def _label(lx, ly):
            return Text(text=str(label), x=lx, y=ly, font_size=font_size,
                        text_anchor='middle', creation=creation, z=z,
                        fill='#FFFF00', stroke_width=0)
        if row_labels:
            for r, label in enumerate(row_labels):
                objects.append(_label(x + cell_width / 2,
                    y + y_off + r * cell_height + cell_height / 2 + font_size * TEXT_Y_OFFSET))
        if col_labels:
            for c, label in enumerate(col_labels):
                objects.append(_label(x + x_off + c * cell_width + cell_width / 2,
                    y + cell_height / 2 + font_size * TEXT_Y_OFFSET))

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

    get_cell = _GridAccessMixin.get_entry

    def get_cell_rect(self, row, col, padding: float = 2, **kwargs):
        """Return a Rectangle covering the cell at (row, col)."""
        rx = self._table_x + self._x_off + col * self._cell_width + padding
        ry = self._table_y + self._y_off + row * self._cell_height + padding
        w = self._cell_width - 2 * padding
        h = self._cell_height - 2 * padding
        kw = _HIGHLIGHT_STYLE | kwargs
        return Rectangle(w, h, x=rx, y=ry, **kw)

    highlight_cell = _GridAccessMixin.highlight_entry  # Table alias
    set_cell_value = _GridAccessMixin.set_entry_value  # Table alias

    def highlight_cells(self, cells, start: float = 0, end: float = 1, color='#FFD700', easing=easings.there_and_back):
        """Flash-highlight multiple cells. cells: list of (row, col) tuples."""
        return self._flash([self.entries[r][c] for r, c in cells], start, end, color, easing)

    def highlight_range(self, start_row, start_col, end_row, end_col,
                        start=0, end=1, color='#FFD700', easing=easings.there_and_back):
        """Highlight a rectangular range of cells."""
        entries = [self.entries[r][c]
                   for r in range(start_row, end_row + 1)
                   for c in range(start_col, end_col + 1)
                   if r < self.rows and c < self.cols]
        return self._flash(entries, start, end, color, easing)

    def set_cell_values(self, updates, start: float = 0):
        """Batch update multiple cell values."""
        for (r, c), value in updates.items():
            self.set_cell_value(r, c, str(value), start=start)
        return self

    def sort_by_column(self, col, start: float = 0, end: float = 1, reverse=False, easing=easings.smooth):
        """Animate rows sliding to sorted positions based on column values."""
        if not self.entries or col >= len(self.entries[0]):
            return self
        values = sorted([(entry[col].text.at_time(start), r)
                         for r, entry in enumerate(self.entries)], reverse=reverse)
        ys = [entry[0].y.at_time(start) for entry in self.entries]
        for new_pos, (_, old_row) in enumerate(values):
            if new_pos != old_row:
                dy = ys[new_pos] - ys[old_row]
                for entry in self.entries[old_row]:
                    entry.shift(dx=0, dy=dy, start=start, end=end, easing=easing)
        return self

    def transpose(self, start: float = 0, end: float | None = None, easing=None):
        """Transpose the table so rows become columns and vice versa."""
        easing = easing or easings.smooth
        x, y_off, cw, ch, x_off, fs, _ = self._tp()
        y = self._table_y
        for r in range(self.rows):
            for c in range(self.cols):
                self.entries[r][c].center_to_pos(
                    posx=x + x_off + r * cw + cw / 2,
                    posy=y + y_off + c * ch + ch / 2 + fs * TEXT_Y_OFFSET,
                    start=start, end=end, easing=easing)
        self.entries = [[self.entries[r][c] for r in range(self.rows)] for c in range(self.cols)]
        self.rows, self.cols = self.cols, self.rows
        return self

    def animate_cell_values(self, data, start: float = 0, end: float = 1, easing=None):
        """Animate table cells changing to new values with numeric interpolation."""
        easing = easing or easings.smooth
        dur = end - start
        for r, row in enumerate(data):
            for c, new_val in enumerate(row):
                if r >= self.rows or c >= self.cols:
                    continue
                entry = self.entries[r][c]
                new_text = str(new_val)
                old_text = entry.text.at_time(start)
                try:
                    old_num, new_num = float(old_text), float(new_text)
                    is_int = ('.' not in old_text and '.' not in new_text
                              and old_num == int(old_num) and new_num == int(new_num))
                    if dur <= 0:
                        entry.text.set_onward(start, new_text)
                    elif is_int:
                        entry.text.set(start, end,
                            lambda t, _s=start, _d=dur, _ov=old_num, _nv=new_num, _e=easing:
                                str(int(round(_ov + (_nv - _ov) * _e((t - _s) / _d)))),
                            stay=True)
                    else:
                        dot_pos = new_text.find('.')
                        decimals = len(new_text) - dot_pos - 1 if dot_pos >= 0 else 1
                        fmt = f'{{:.{decimals}f}}'
                        entry.text.set(start, end,
                            lambda t, _s=start, _d=dur, _ov=old_num, _nv=new_num,
                                   _e=easing, _fmt=fmt:
                                _fmt.format(_ov + (_nv - _ov) * _e((t - _s) / _d)),
                            stay=True)
                except (ValueError, TypeError):
                    if dur <= 0:
                        entry.text.set_onward(start, new_text)
                    else:
                        entry.text.set_onward(start + dur / 2, new_text)
        return self

    def animate_cells(self, cells, method_name='flash', start: float = 0, delay: float = 0.15, **kwargs):
        """Apply an animation method to specific cells with a stagger delay."""
        for i, (r, c) in enumerate(cells):
            getattr(self.entries[r][c], method_name)(start=start + i * delay, **kwargs)
        return self

    @classmethod
    def from_dict(cls, data, **kwargs):
        """Create a Table from a dict (keys become column headers, values become rows)."""
        columns = [v if isinstance(v, (list, tuple)) else [v] for v in data.values()]
        n_rows = max((len(col) for col in columns), default=0)
        grid = [[col[r] if r < len(col) else '' for col in columns] for r in range(n_rows)]
        return cls(grid, col_labels=list(data.keys()), **kwargs)

    def _tp(self):
        """Return unpacked table layout parameters."""
        return (self._table_x, self._y_off, self._cell_width, self._cell_height,
                self._x_off, self._font_size, self._z)

    def _make_cell_text(self, val, cx, cy, start):
        _, _, _, _, _, fs, z = self._tp()
        return Text(text=str(val), x=cx, y=cy, font_size=fs, text_anchor='middle',
                    creation=start, z=z, fill='#fff', stroke_width=0)

    def add_row(self, values, start: float = 0, animate=True):
        """Append a new row to the bottom of the table."""
        x, y_off, cw, ch, x_off, fs, z = self._tp()
        row_y = self._table_y + y_off + self.rows * ch
        total_w = self.cols * cw + x_off
        h_line = Line(x1=x, y1=row_y + ch, x2=x + total_w, y2=row_y + ch,
                      creation=start, z=z, **self._line_kw)

        # Extend existing vertical lines downward by one cell height
        for obj in self.objects:
            if isinstance(obj, Line):
                p1, p2 = obj.p1.at_time(start), obj.p2.at_time(start)
                if abs(p1[0] - p2[0]) < 0.1 and p2[1] > p1[1]:
                    old_y2 = p2[1]
                    if abs(old_y2 - (self._table_y + y_off + self.rows * ch)) < 1:
                        obj.p2.add_onward(start, (p2[0], old_y2 + ch))

        new_entries = []
        new_objects = [h_line]
        for c in range(self.cols):
            val = values[c] if c < len(values) else ''
            t = self._make_cell_text(val, x + x_off + c * cw + cw / 2,
                                     row_y + ch / 2 + fs * TEXT_Y_OFFSET, start)
            new_entries.append(t)
            new_objects.append(t)

        if animate:
            for obj in new_objects: obj.fadein(start=start, end=start + 0.5)
        self.entries.append(new_entries)
        self.rows += 1
        self.objects.extend(new_objects)
        return self

    def add_column(self, values, start: float = 0, animate=True):
        """Append a new column to the right of the table."""
        x, y_off, cw, ch, x_off, fs, z = self._tp()
        col_x = x + x_off + self.cols * cw
        total_h = self.rows * ch + y_off
        v_line = Line(x1=col_x + cw, y1=self._table_y + y_off,
                      x2=col_x + cw, y2=self._table_y + total_h,
                      creation=start, z=z, **self._line_kw)

        # Extend existing horizontal lines to the right by one cell width
        for obj in self.objects:
            if isinstance(obj, Line):
                p1, p2 = obj.p1.at_time(start), obj.p2.at_time(start)
                if abs(p1[1] - p2[1]) < 0.1 and p2[0] > p1[0]:
                    old_x2 = p2[0]
                    if abs(old_x2 - (x + self.cols * cw + x_off)) < 1:
                        obj.p2.add_onward(start, (old_x2 + cw, p2[1]))

        new_objects = [v_line]
        for r in range(self.rows):
            val = values[r] if r < len(values) else ''
            t = self._make_cell_text(val, col_x + cw / 2,
                                     self._table_y + y_off + r * ch + ch / 2 + fs * TEXT_Y_OFFSET, start)
            if r < len(self.entries):
                self.entries[r].append(t)
            new_objects.append(t)

        if animate:
            for obj in new_objects: obj.fadein(start=start, end=start + 0.5)
        self.cols += 1
        self.objects.extend(new_objects)
        return self

    def _swap_dim(self, i, j, is_row, start: float = 0, end: float = 1, easing=easings.smooth):
        dim = self.rows if is_row else self.cols
        if i == j or not (0 <= i < dim) or not (0 <= j < dim):
            return self
        attr = 'y' if is_row else 'x'
        shift_kw = 'dy' if is_row else 'dx'
        for idx in range(self.cols if is_row else self.rows):
            a = self.entries[i][idx] if is_row else self.entries[idx][i]
            b = self.entries[j][idx] if is_row else self.entries[idx][j]
            av, bv = getattr(a, attr).at_time(start), getattr(b, attr).at_time(start)
            a.shift(**{shift_kw: bv - av}, start=start, end=end, easing=easing)
            b.shift(**{shift_kw: av - bv}, start=start, end=end, easing=easing)
        if is_row:
            self.entries[i], self.entries[j] = self.entries[j], self.entries[i]
        else:
            for r in range(self.rows):
                self.entries[r][i], self.entries[r][j] = self.entries[r][j], self.entries[r][i]
        return self

    def swap_rows(self, i, j, start: float = 0, end: float = 1, easing=easings.smooth):
        """Animate swapping two table rows."""
        return self._swap_dim(i, j, True, start, end, easing)

    def swap_columns(self, i, j, start: float = 0, end: float = 1, easing=easings.smooth):
        """Animate swapping two table columns."""
        return self._swap_dim(i, j, False, start, end, easing)

    def highlight_where(self, predicate, start: float = 0, end: float = 1, color='#FFFF00',
                        easing=easings.there_and_back):
        """Highlight cells whose text satisfies *predicate(text) -> bool*."""
        for r in range(self.rows):
            for c in range(self.cols):
                txt = self.entries[r][c].text.at_time(start)
                if predicate(str(txt)):
                    self.entries[r][c].flash(start, end, color=color, easing=easing)
        return self

    def _fade_or_remove(self, cell, start, animate):
        if animate: cell.fadeout(start=start, end=start + 0.3)
        else: self.objects.remove(cell)

    def remove_row(self, index, start: float = 0, animate=True):
        """Remove a row by index, fading out its cells."""
        if index < 0 or index >= self.rows:
            raise IndexError(f"row index {index} out of range (0..{self.rows - 1})")
        for cell in self.entries.pop(index):
            self._fade_or_remove(cell, start, animate)
        end_t = start + 0.3 if animate else start
        for r in range(index, len(self.entries)):
            for cell in self.entries[r]:
                cell.shift(dy=-self._cell_height, start=start, end=end_t)
        self.rows -= 1
        return self

    def remove_column(self, index, start: float = 0, animate=True):
        """Remove a column by index, fading out its cells."""
        if index < 0 or index >= self.cols:
            raise IndexError(f"column index {index} out of range (0..{self.cols - 1})")
        end_t = start + 0.3 if animate else start
        for r in range(self.rows):
            self._fade_or_remove(self.entries[r].pop(index), start, animate)
        for r in range(self.rows):
            for c in range(index, len(self.entries[r])):
                self.entries[r][c].shift(dx=-self._cell_width, start=start, end=end_t)
        self.cols -= 1
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
        if self._cache[0] != time:
            self._cache[0] = time
            self._cache[1] = self._func(time)
        return self._cache[1]

    def to_svg(self, time):
        """Render the dynamically-generated object at *time*."""
        obj = self._eval(time)
        return obj.to_svg(time) if obj is not None else ''

    def path(self, time):
        """Return the path of the dynamically-generated object at *time*."""
        obj = self._eval(time)
        return obj.path(time) if obj is not None and hasattr(obj, 'path') else ''

    def bbox(self, time: float = 0):
        """Return the bounding box of the dynamically-generated object at *time*."""
        obj = self._eval(time)
        return obj.bbox(time) if obj is not None else (0, 0, 0, 0)

    def __repr__(self) -> str:
        return 'DynamicObject()'

def _det(m):
    """Recursive determinant of a numeric 2D list."""
    n = len(m)
    if n == 1:
        return m[0][0]
    if n == 2:
        return m[0][0] * m[1][1] - m[0][1] * m[1][0]
    d = 0.0
    for c in range(n):
        minor = [[m[r][j] for j in range(n) if j != c] for r in range(1, n)]
        d += ((-1) ** c) * m[0][c] * _det(minor)
    return d

class Matrix(_GridAccessMixin, VCollection):
    """Display a mathematical matrix with square bracket delimiters."""
    def __init__(self, data, x=ORIGIN[0], y=ORIGIN[1], font_size: float = 36, h_spacing: float = 80, v_spacing: float = 50,
                 creation: float = 0, z: float = 0, **styling_kwargs):
        if not data or not data[0]:
            raise ValueError('Matrix requires a non-empty 2D list of data')
        rows = len(data)
        cols = len(data[0])
        total_w = (cols - 1) * h_spacing
        total_h = (rows - 1) * v_spacing
        bracket_pad = 20
        bracket_w = 8

        bracket_kw = {'stroke': '#fff', 'stroke_width': 3, 'fill_opacity': 0} | styling_kwargs
        yt, yb = y - total_h / 2 - bracket_pad, y + total_h / 2 + bracket_pad

        self.entries = []
        objects = []
        for r in range(rows):
            row_entries = []
            for c in range(cols):
                t = Text(text=str(data[r][c]),
                         x=x - total_w / 2 + c * h_spacing,
                         y=y - total_h / 2 + r * v_spacing + font_size * TEXT_Y_OFFSET,
                         font_size=font_size, text_anchor='middle',
                         creation=creation, z=z, fill='#fff', stroke_width=0)
                objects.append(t)
                row_entries.append(t)
            self.entries.append(row_entries)

        lx = x - total_w / 2 - bracket_pad
        objects.append(Lines((lx + bracket_w, yt), (lx, yt), (lx, yb), (lx + bracket_w, yb),
                             creation=creation, z=z, **bracket_kw))
        rx = x + total_w / 2 + bracket_pad
        objects.append(Lines((rx - bracket_w, yt), (rx, yt), (rx, yb), (rx - bracket_w, yb),
                             creation=creation, z=z, **bracket_kw))

        super().__init__(*objects, creation=creation, z=z)
        self.rows, self.cols = rows, cols

    def __repr__(self):
        return f'Matrix({self.rows}x{self.cols})'

    def swap_rows(self, i, j, start: float = 0, end: float = 1, easing=easings.smooth):
        """Animate swapping two rows via arc paths."""
        if i == j or not (0 <= i < self.rows) or not (0 <= j < self.rows):
            return self
        import math
        for c in range(self.cols):
            a, b = self.entries[i][c], self.entries[j][c]
            ax, ay = a.x.at_time(start), a.y.at_time(start)
            bx, by = b.x.at_time(start), b.y.at_time(start)
            a.path_arc(bx, by, start=start, end=end, angle=math.pi / 4, easing=easing)
            b.path_arc(ax, ay, start=start, end=end, angle=-math.pi / 4, easing=easing)
        self.entries[i], self.entries[j] = self.entries[j], self.entries[i]
        return self

    def row_operation(self, target_row, source_row, scalar: float = 1, start: float = 0, end: float = 1,
                      easing=easings.smooth):
        """Animate an elementary row operation: R_target += scalar * R_source.

        Each target entry is animated to its new numeric value."""
        dur = end - start
        for c in range(self.cols):
            tgt = self.entries[target_row][c]
            src_text = self.entries[source_row][c].text.at_time(start)
            tgt_text = tgt.text.at_time(start)
            try:
                src_val = float(src_text)
                tgt_val = float(tgt_text)
            except (ValueError, TypeError):
                continue
            new_val = tgt_val + scalar * src_val
            is_int = (tgt_val == int(tgt_val) and src_val == int(src_val)
                      and new_val == int(new_val))
            if dur <= 0:
                tgt.text.set_onward(start, str(int(new_val)) if is_int else f'{new_val:g}')
            else:
                tgt.text.set(start, end,
                    lambda t, _s=start, _d=dur, _ov=tgt_val, _nv=new_val, _e=easing, _ii=is_int:
                        str(int(round(_ov + (_nv - _ov) * _e((t - _s) / _d)))) if _ii
                        else f'{_ov + (_nv - _ov) * _e((t - _s) / _d):g}',
                    stay=True)
        return self

    def get_values(self, time: float = 0):
        """Return a 2D list of numeric values from the matrix entries at *time*."""
        return [[float(self.entries[r][c].text.at_time(time))
                 for c in range(self.cols)] for r in range(self.rows)]

    def trace(self, time: float = 0):
        """Return the trace (sum of diagonal elements) of a square matrix."""
        if self.rows != self.cols:
            raise ValueError(f'trace requires a square matrix, got {self.rows}x{self.cols}')
        return sum(float(self.entries[i][i].text.at_time(time)) for i in range(self.rows))

    def determinant(self, time: float = 0):
        """Compute the determinant of a square matrix (up to ~10x10)."""
        if self.rows != self.cols:
            raise ValueError(f'determinant requires a square matrix, got {self.rows}x{self.cols}')
        return _det(self.get_values(time))

    def set_row_colors(self, *colors, start: float = 0):
        """Set colors for each row. Cycles if fewer colors than rows."""
        for r in range(self.rows):
            for entry in self.entries[r]:
                entry.styling.fill.set_onward(start, colors[r % len(colors)])
        return self

    def set_column_colors(self, *colors, start: float = 0):
        """Set colors for each column. Cycles if fewer colors than columns."""
        for ci in range(self.cols):
            for row in self.entries:
                if ci < len(row):
                    row[ci].styling.fill.set_onward(start, colors[ci % len(colors)])
        return self

    @classmethod
    def augmented(cls, left_data, right_data, **kwargs):
        """Create an augmented matrix [left | right] with a vertical divider."""
        rows_l, rows_r = len(left_data), len(right_data)
        rows = max(rows_l, rows_r)
        cols_l = len(left_data[0]) if left_data else 0
        cols_r = len(right_data[0]) if right_data else 0
        merged = [(list(left_data[r]) if r < rows_l else [''] * cols_l) +
                  (list(right_data[r]) if r < rows_r else [''] * cols_r)
                  for r in range(rows)]
        m = cls(merged, **kwargs)
        m._augment_col = cols_l
        h_sp = kwargs.get('h_spacing', 80)
        v_sp = kwargs.get('v_spacing', 50)
        x0 = m.entries[0][0].x.at_time(0)
        div_x = x0 + (cols_l - 0.5) * h_sp
        y_top = m.entries[0][0].y.at_time(0) - v_sp * 0.6
        y_bot = m.entries[-1][0].y.at_time(0) + v_sp * 0.6
        m.objects.append(Line(x1=div_x, y1=y_top, x2=div_x, y2=y_bot,
                              stroke='#888', stroke_width=2,
                              creation=kwargs.get('creation', 0), z=kwargs.get('z', 0) + 0.05))
        return m

class DecimalMatrix(Matrix):
    """Matrix that formats entries as decimals with a fixed number of places."""
    def __init__(self, data, decimals: int = 1, **kwargs):
        formatted = [[f'{float(v):.{decimals}f}' for v in row] for row in data]
        super().__init__(formatted, **kwargs)

    def __repr__(self):
        return f'DecimalMatrix({self.rows}x{self.cols})'

class IntegerMatrix(Matrix):
    """Matrix that formats entries as integers."""
    def __init__(self, data, **kwargs):
        formatted = [[str(int(round(float(v)))) for v in row] for row in data]
        super().__init__(formatted, **kwargs)

    def __repr__(self):
        return f'IntegerMatrix({self.rows}x{self.cols})'

class TexCountAnimation(DynamicObject):
    """Animated number display using pre-rendered LaTeX digit glyphs."""

    def __init__(self, start_val: float = 0, end_val: float = 100, start: float = 0, end: float = 1,
                 fmt='{:.0f}', easing=easings.smooth,
                 x: float = ORIGIN[0], y: float = ORIGIN[1], font_size: float = 48,
                 text_anchor=None, creation: float = 0, z: float = 0, **styles):
        from vectormation._tex_glyphs import _resolve_tex_dir

        self._tex_dir = _resolve_tex_dir()
        self._x, self._y, self._font_size = x, y, font_size
        self._text_anchor = text_anchor
        self._styles = {'stroke_width': 0, 'fill': '#fff'} | styles
        self._fmt, self._start_val, self._end_val = fmt, start_val, end_val
        self._anim_start, self._anim_dur = start, max(end - start, 1e-9)
        self._easing, self._last_val = easing, end_val
        self._extra_segments = []  # [(from_val, to_val, start, dur, easing)]
        super().__init__(lambda t: self._build_number(self._compute_value(t), creation=t),
                         creation=creation, z=z)

    def __repr__(self):
        return f'TexCountAnimation({self._last_val})'

    def _compute_value(self, t):
        """Compute the displayed number at time t."""
        # Check extra segments in reverse order (latest wins)
        for from_val, to_val, seg_start, seg_dur, seg_easing in reversed(self._extra_segments):
            if t >= seg_start:
                if t >= seg_start + seg_dur:
                    return to_val
                alpha = seg_easing((t - seg_start) / seg_dur)
                return from_val + (to_val - from_val) * alpha

        # Base animation
        if t >= self._anim_start + self._anim_dur:
            return self._end_val
        if t < self._anim_start:
            return self._start_val
        alpha = self._easing((t - self._anim_start) / self._anim_dur)
        return self._start_val + (self._end_val - self._start_val) * alpha

    def _build_number(self, val, creation: float = 0):
        """Assemble digit glyphs into a VCollection for the given numeric value."""
        from vectormation._tex_glyphs import assemble_tex_glyphs

        text = self._fmt.format(val)
        # Map text_anchor to assemble_tex_glyphs anchor names
        anchor = 'left'
        if self._text_anchor == 'middle':
            anchor = 'center'
        elif self._text_anchor == 'end':
            anchor = 'right'
        result = assemble_tex_glyphs(text, self._x, self._y, self._font_size,
                                     creation=creation, tex_dir=self._tex_dir,
                                     anchor=anchor, **self._styles)
        if result is None:
            return VCollection(creation=creation)
        return result

    def count_to(self, target: float, start: float = 0, end: float = 1, easing=easings.smooth):
        """Animate counting from the current value to a new target."""
        dur = max(end - start, 1e-9)
        self._extra_segments.append((self._last_val, target, start, dur, easing))
        self._last_val = target
        return self

def always_redraw(func, creation: float = 0, z: float = 0):
    """Convenience wrapper: create a DynamicObject from a callable.
    func(time) should return a VObject."""
    return DynamicObject(func, creation=creation, z=z)


def succession(*animation_steps, start: float = 0, lag_ratio: float = 0.0):
    """Chain multiple animation steps in sequence.

    Each step is a tuple ``(obj, method_name, kwargs)`` or ``(obj, method_name)``.
    Steps are run in order; each step gets an equal portion of the total time.
    ``lag_ratio`` controls overlap: 0 = no overlap, 0.5 = 50% overlap.

    Example::

        succession(
            (circle, 'fadein'),
            (square, 'write'),
            (text, 'fadein', {'shift_dir': 'up'}),
            start=0, lag_ratio=0.2,
        )
    """
    n = len(animation_steps)
    if n == 0:
        return
    # Determine total end time: each step nominally takes 1 second
    total_dur = n  # 1s per step by default
    if n == 1:
        step_dur = total_dur
        step_offset = 0
    else:
        step_dur = total_dur / (1 + (1 - lag_ratio) * (n - 1))
        step_offset = step_dur * (1 - lag_ratio)
    for i, step in enumerate(animation_steps):
        obj = step[0]
        method_name = step[1]
        kwargs = step[2] if len(step) > 2 else {}
        s = start + i * step_offset
        e = s + step_dur
        getattr(obj, method_name)(start=s, end=e, **kwargs)

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

class ParametricFunction(Lines):
    """A curve defined by a parametric function f(t) -> (x, y)."""
    def __init__(self, func, t_range=(0, 1), num_points: int = 200,
                 creation: float = 0, z: float = 0, **styling_kwargs):
        t_min, t_max = t_range
        style_kw = {'stroke': '#58C4DD', 'stroke_width': 4, 'fill_opacity': 0} | styling_kwargs
        pts = [func(t_min + (t_max - t_min) * i / max(num_points - 1, 1))
               for i in range(num_points)]
        super().__init__(*pts, creation=creation, z=z, **style_kw)
        self._func = func
        self._t_min, self._t_max = t_min, t_max

    def __repr__(self):
        return f'ParametricFunction(t=[{self._t_min}, {self._t_max}])'

    def get_point(self, t):
        """Return (x, y) at parameter value t."""
        return self._func(t)


def _match_and_morph(src_objs, tgt_objs, src_keys, tgt_keys, start, end):
    """Match source/target objects by key, morph matched pairs, fade unmatched."""
    src_by_key: dict = {}
    for obj, k in zip(src_objs, src_keys):
        src_by_key.setdefault(k, []).append(obj)
    tgt_by_key: dict = {}
    for obj, k in zip(tgt_objs, tgt_keys):
        tgt_by_key.setdefault(k, []).append(obj)

    matched_src, matched_tgt, animations = set(), set(), []
    for k in set(src_by_key) | set(tgt_by_key):
        for s, t in zip(src_by_key.get(k, []), tgt_by_key.get(k, [])):
            animations.append(MorphObject(s, t, start=start, end=end))
            matched_src.add(id(s))
            matched_tgt.add(id(t))

    for obj in src_objs:
        if id(obj) not in matched_src:
            obj.fadeout(start=start, end=end)
    for obj in tgt_objs:
        if id(obj) not in matched_tgt:
            obj.fadein(start=start, end=end)
    return VCollection(*animations, creation=start)

def transform_matching_shapes(source, target, start: float = 0, end: float = 1, key=None):
    """Morph between VCollections by matching sub-objects via *key* (default: bbox area)."""
    src_objs = list(source.objects) if isinstance(source, VCollection) else list(source)
    tgt_objs = list(target.objects) if isinstance(target, VCollection) else list(target)

    def _area_key(obj, time):
        try:
            _, _, w, h = obj.bbox(time)
            return round(w * h, -1)
        except (TypeError, ValueError, AttributeError):
            return None

    key_fn = (lambda obj, _t: key(obj)) if key else _area_key
    return _match_and_morph(src_objs, tgt_objs,
                            [key_fn(o, start) for o in src_objs],
                            [key_fn(o, end) for o in tgt_objs], start, end)

def transform_matching_tex(source, target, start: float = 0, end: float = 1):
    """Morph between TexObjects by matching visible characters."""
    src_vis = getattr(source, '_visible_tex', None)
    tgt_vis = getattr(target, '_visible_tex', None)
    if src_vis is not None and tgt_vis is not None:
        src_objs, tgt_objs = list(source.objects), list(target.objects)
        src_keys = list(src_vis[:len(src_objs)]) + [None] * max(0, len(src_objs) - len(src_vis))
        tgt_keys = list(tgt_vis[:len(tgt_objs)]) + [None] * max(0, len(tgt_objs) - len(tgt_vis))
        return _match_and_morph(src_objs, tgt_objs, src_keys, tgt_keys, start, end)
    return transform_matching_shapes(source, target, start=start, end=end)

