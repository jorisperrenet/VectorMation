"""Composite classes: MorphObject, TexObject, NumberLine, Table, Matrix, etc."""
import tempfile
from collections import defaultdict

import vectormation.easings as easings
import vectormation.attributes as attributes
import vectormation.style as style
import vectormation.morphing as morphing
from vectormation._constants import SMALL_BUFF, TEXT_Y_OFFSET, _label_text
from vectormation._base import VObject, VCollection, _norm_dir, _ramp
from vectormation._shapes import Polygon, Dot, Rectangle, Line, Lines, Text, Path
from vectormation._arrows import Arrow, Brace
from vectormation._svg_utils import from_svg
from vectormation._axes_helpers import _TICK_FONT_SIZE

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

    def __repr__(self):
        return 'MorphObject()'

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

    def __repr__(self):
        return 'LabeledDot()'

class TexObject(VCollection):
    """Renders LaTeX content as SVG paths via dvisvgm."""
    def __init__(self, to_render, x=0, y=0, font_size=48, creation: float = 0, z: float = 0, **styles):
        from vectormation.tex_file_writing import get_characters
        import vectormation._canvas as _cm
        tex_dir = f'{_cm.save_directory}/tex' if hasattr(_cm, 'save_directory') else tempfile.mkdtemp()
        self._tex = to_render
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

    def __repr__(self):
        return f'TexObject({self._tex!r})'

class SplitTexObject:
    """Renders multiple lines of LaTeX, each as a separate TexObject.
    Supports indexing, iteration, and conversion to a single VCollection."""
    def __init__(self, *lines, x=0, y=0, line_spacing=60, creation: float = 0, **styles):
        self.lines = [TexObject(line, x=x, y=y + i * line_spacing, creation=creation, **styles)
                      for i, line in enumerate(lines)]

    def __repr__(self):
        return f'SplitTexObject({len(self.lines)} lines)'
    def __iter__(self): return iter(self.lines)
    def __getitem__(self, idx): return self.lines[idx]
    def __len__(self): return len(self.lines)

class NumberLine(VCollection):
    """A number line with ticks and labels, with optional endpoint arrows."""
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
        """Convert a number on the line to an SVG (x, y) coordinate."""
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
        """Add an animated pointer (triangle) above the number line at *value*."""
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
        """Animate a pointer (from add_pointer) to a new value."""
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
        """Add a colored dot at a specific value on the number line."""
        px, py = self.number_to_point(value)
        kw = {'fill': color, 'stroke_width': 0} | kwargs
        dot = Dot(cx=px, cy=py, r=radius, creation=creation, **kw)
        self.objects.append(dot)
        return dot

    def highlight_range(self, start_val, end_val, color='#FFFF00',
                        height=16, opacity=0.4, creation=0, z=1, **kwargs):
        """Highlight a numeric range on the number line with a colored rectangle."""
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
        """Add a text label at the given value on the number line."""
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
        """Batch-add tick labels for values from *start_val* to *end_val*."""
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
        """Add a curly brace between two values on the number line."""
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
        """Show an interval on the number line with bracket notation."""
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
        """Dynamically add a tick mark at *value* with a pop-in animation."""
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
        """Add a pointer (triangle) that tracks a dynamic value function over time."""
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
        """Animate the number line's visible range to ``[new_start, new_end]``."""
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

class Table(VCollection):
    """Table for displaying tabular data with optional row/column labels."""
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
        """Return a Rectangle covering the cell at (row, col)."""
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
        """Highlight all cells in a row by setting their fill color."""
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
        """Batch update multiple cell values."""
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
        """Transpose the table so rows become columns and vice versa."""
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
        """Animate table cells changing to new values with numeric interpolation."""
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
        """Apply an animation method to specific cells with a stagger delay."""
        for i, (r, c) in enumerate(cells):
            entry = self.entries[r][c]
            method = getattr(entry, method_name)
            t = start + i * delay
            method(start=t, **kwargs)
        return self

    @classmethod
    def from_dict(cls, data, **kwargs):
        """Create a Table from a dict (keys become column headers, values become rows)."""
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
        """Append a new row to the bottom of the table."""
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
        """Append a new column to the right of the table."""
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

    def __repr__(self):
        return f'DynamicObject()'

class Matrix(VCollection):
    """Display a mathematical matrix with square bracket delimiters."""
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

    def __repr__(self):
        return f'Matrix({self.rows}x{self.cols})'

    def get_entry(self, row, col):
        """Return the Text object at (row, col)."""
        return self.entries[row][col]

    def get_row(self, row):
        """Return a VCollection of all Text objects in the given row."""
        return VCollection(*self.entries[row])

    def get_column(self, col):
        """Return a VCollection of all Text objects in the given column."""
        return VCollection(*(row[col] for row in self.entries if col < len(row)))

    def highlight_entry(self, row, col, start=0, end=1, color='#FFD700'):
        """Flash-highlight a single matrix entry."""
        self.entries[row][col].flash_color(color, start=start, duration=end - start)
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

class TexCountAnimation(DynamicObject):
    """Animated number display using pre-rendered LaTeX digit glyphs."""

    _glyph_cache = {}  # class-level: {(tex_dir, font_size): {char: (vb, chars)}}

    def __init__(self, start_val=0, end_val=100, start: float = 0, end: float = 1,
                 fmt='{:.0f}', easing=easings.smooth,
                 x: float = 960, y: float = 540, font_size=48,
                 creation: float = 0, z: float = 0, **styles):
        from vectormation.tex_file_writing import get_characters
        import vectormation._canvas as _cm
        import tempfile as _tmpmod
        tex_dir = f'{_cm.save_directory}/tex' if hasattr(_cm, 'save_directory') else _tmpmod.mkdtemp()

        cache_key = (tex_dir, font_size)
        if cache_key not in TexCountAnimation._glyph_cache:
            glyphs = {}
            for ch in '0123456789.-':
                tex_str = f'${ch}$' if ch != '.' else '$.$'
                vb, chars = get_characters(tex_dir, tex_str, 'latex', '')
                glyphs[ch] = (vb, chars)
            TexCountAnimation._glyph_cache[cache_key] = glyphs

        self._glyphs = TexCountAnimation._glyph_cache[cache_key]
        self._x = x
        self._y = y
        self._font_size = font_size
        self._styles = {'stroke_width': 0, 'fill': '#fff'} | styles
        self._fmt = fmt
        self._start_val = start_val
        self._end_val = end_val
        self._anim_start = start
        self._anim_dur = max(end - start, 1e-9)
        self._easing = easing
        self._last_val = end_val
        self._extra_segments = []  # [(from_val, to_val, start, dur, easing)]

        def build_fn(t):
            val = self._compute_value(t)
            return self._build_number(val, creation=t)

        super().__init__(build_fn, creation=creation, z=z)

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

    def _build_number(self, val, creation=0):
        """Assemble digit glyphs into a VCollection for the given numeric value."""
        text = self._fmt.format(val)
        objects = []
        cursor_x = self._x
        for ch in text:
            glyph_data = self._glyphs.get(ch)
            if glyph_data is None:
                # Space or unrecognized char — advance cursor
                cursor_x += self._font_size * 0.3
                continue
            vb, chars = glyph_data
            vb_height = abs(vb[3]) if vb[3] else 1
            vb_width = abs(vb[2]) if vb[2] else 1
            base_scale = self._font_size / vb_height
            char_width = vb_width * base_scale

            st = dict(self._styles)
            st['scale_x'] = base_scale * st.pop('scale_x', 1)
            st['scale_y'] = base_scale * st.pop('scale_y', 1)
            for char_svg in chars:
                obj = from_svg(char_svg, **st)
                # Position: shift glyph so it starts at cursor_x
                obj.styling.dx.set_onward(creation, cursor_x)
                obj.styling.dy.set_onward(creation, self._y)
                objects.append(obj)
            cursor_x += char_width + self._font_size * 0.05

        return VCollection(*objects, creation=creation)

    def count_to(self, target, start, end, easing=easings.smooth):
        """Animate counting from the current value to a new target."""
        dur = max(end - start, 1e-9)
        self._extra_segments.append((self._last_val, target, start, dur, easing))
        self._last_val = target
        return self

def always_redraw(func, creation=0, z=0):
    """Convenience wrapper: create a DynamicObject from a callable.
    func(time) should return a VObject."""
    return DynamicObject(func, creation=creation, z=z)

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
    def __init__(self, func, t_range=(0, 1), num_points=200,
                 creation=0, z=0, **styling_kwargs):
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

