"""Composite classes: Arrow, Axes, Graph, NumberLine, Table, etc."""
import math
import os
import re
import tempfile
from collections import defaultdict

import vectormation.easings as easings
import vectormation.attributes as attributes
import vectormation.style as style
import vectormation.morphing as morphing
from vectormation._constants import (
    UNIT, SMALL_BUFF, DEFAULT_FONT_SIZE,
    DEFAULT_ARROW_TIP_LENGTH, DEFAULT_ARROW_TIP_WIDTH,
    DEFAULT_OBJECT_TO_EDGE_BUFF, _sample_function,
)
from vectormation._base import VObject, VCollection
from vectormation._shapes import (
    Polygon, Circle, Ellipse, Dot, Rectangle, Line, Lines,
    Text, Path, Arc, Wedge,
)

class MorphObject(VCollection):
    """Morphs one object/collection into another over a time range.
    Must be added to the canvas. The source becomes hidden at start, target appears at end."""
    def __init__(self, morph_from, morph_to, start: float = 0, end: float = 1, z=0,
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

        mapping = obj_from.morph(obj_to, start_time=start, end_time=end, easing=easing)

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
                if len(pfs) == 1:
                    pf = pfs[0]
                    return lambda t: pf((t - start) / (end - start))
                return lambda t: ' '.join(pf((t - start) / (end - start)) for pf in pfs)
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
    def __init__(self, label='', r=24, cx=960, cy=540, creation=0, z=0, font_size=None, **styling_kwargs):
        dot_kw = {k: v for k, v in styling_kwargs.items() if k != 'fill'}
        dot_fill = styling_kwargs.get('fill', '#83C167')
        dot = Dot(r=r, cx=cx, cy=cy, creation=creation, z=z, fill=dot_fill, **dot_kw)
        if font_size is None:
            font_size = r * 0.9
        text = Text(text=str(label), x=cx, y=cy + font_size * 0.35,
                    font_size=font_size, text_anchor='middle',
                    creation=creation, z=z, fill='#fff', stroke_width=0)
        super().__init__(dot, text, creation=creation, z=z)
        self.dot = dot
        self.label = text


class TexObject(VCollection):
    """Renders LaTeX content as SVG paths via dvisvgm.

    font_size: target height in pixels (default 30, matching Text).
    scale_x/scale_y in styles act as multipliers on the font_size-derived scale.
    """
    def __init__(self, to_render, x=0, y=0, font_size=48, creation=0, **styles):
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
        super().__init__(*chars, creation=creation)

        # Initialize the position and scale/width of the group viewbox
        self.x = attributes.Real(creation, x)
        self.y = attributes.Real(creation, y)

        # Get the bounding box and reset the position
        xmin, ymin, _, _ = self.bbox(creation)
        for obj in self.objects:
            obj.styling.dx.add_onward(creation, lambda t: self.x.at_time(t) - xmin)
            obj.styling.dy.add_onward(creation, lambda t: self.y.at_time(t) - ymin)



class SplitTexObject:
    """Renders multiple lines of LaTeX, each as a separate TexObject.
    Supports indexing, iteration, and conversion to a single VCollection."""
    def __init__(self, *lines, x=0, y=0, line_spacing=60, creation=0, **styles):
        self.lines = [TexObject(line, x=x, y=y + i * line_spacing, creation=creation, **styles)
                      for i, line in enumerate(lines)]

    def __iter__(self): return iter(self.lines)
    def __getitem__(self, idx): return self.lines[idx]
    def __len__(self): return len(self.lines)



def _nice_ticks(vmin, vmax, target_count=7):
    """Generate nicely spaced tick values between vmin and vmax."""
    span = vmax - vmin
    if span <= 0:
        return []
    rough_step = span / target_count
    mag = 10 ** math.floor(math.log10(rough_step))
    step = rough_step
    for nice in [1, 2, 2.5, 5, 10]:
        step = nice * mag
        if span / step <= target_count * 1.5:
            break
    start = math.ceil(vmin / step) * step
    ticks = []
    val = start
    while val <= vmax + step * 0.01:
        if abs(val) < step * 0.01:
            val = 0.0
        ticks.append(val)
        val += step
    return ticks


_AXIS_STROKE_WIDTH = 3
_TICK_FONT_SIZE = DEFAULT_FONT_SIZE // 2  # 24
_TICK_GAP = SMALL_BUFF // 2               # 7 (gap between tick and label)
_LABEL_GAP = SMALL_BUFF + 2              # 16 (gap between axis end and label)

def _build_axes_decoration(x_min, x_max, y_min, y_max, plot_x, plot_y, plot_width, plot_height,
                            show_grid, time):
    """Build axis lines, ticks, tick labels, and grid as VObjects for a single frame."""
    objects = []
    y_zero = plot_y + (1 - (0 - y_min) / (y_max - y_min)) * plot_height if y_min <= 0 <= y_max else plot_y + plot_height
    x_zero = plot_x + (0 - x_min) / (x_max - x_min) * plot_width if x_min <= 0 <= x_max else plot_x
    tick_len = SMALL_BUFF

    def _to_svg_x(val):
        return plot_x + (val - x_min) / (x_max - x_min) * plot_width

    def _to_svg_y(val):
        return plot_y + (1 - (val - y_min) / (y_max - y_min)) * plot_height

    # Grid lines (behind axes)
    if show_grid:
        for tx in _nice_ticks(x_min, x_max):
            sx = _to_svg_x(tx)
            objects.append(Line(x1=sx, y1=plot_y, x2=sx, y2=plot_y + plot_height,
                                creation=time, stroke='#333', stroke_width=1))
        for ty in _nice_ticks(y_min, y_max):
            sy = _to_svg_y(ty)
            objects.append(Line(x1=plot_x, y1=sy, x2=plot_x + plot_width, y2=sy,
                                creation=time, stroke='#333', stroke_width=1))

    # Axis lines
    objects.append(Line(x1=plot_x, y1=y_zero, x2=plot_x + plot_width, y2=y_zero,
                        creation=time, stroke='#fff', stroke_width=_AXIS_STROKE_WIDTH))
    objects.append(Line(x1=x_zero, y1=plot_y, x2=x_zero, y2=plot_y + plot_height,
                        creation=time, stroke='#fff', stroke_width=_AXIS_STROKE_WIDTH))

    # X-axis ticks and labels
    for tx in _nice_ticks(x_min, x_max):
        sx = _to_svg_x(tx)
        objects.append(Line(x1=sx, y1=y_zero - tick_len, x2=sx, y2=y_zero + tick_len,
                            creation=time, stroke='#fff', stroke_width=_AXIS_STROKE_WIDTH))
        if abs(tx) > 1e-9:
            objects.append(Text(text=f'{tx:g}', x=sx, y=y_zero + tick_len + _TICK_GAP + _TICK_FONT_SIZE * 0.35,
                                font_size=_TICK_FONT_SIZE, text_anchor='middle',
                                creation=time, fill='#aaa', stroke_width=0))

    # Y-axis ticks and labels
    for ty in _nice_ticks(y_min, y_max):
        sy = _to_svg_y(ty)
        objects.append(Line(x1=x_zero - tick_len, y1=sy, x2=x_zero + tick_len, y2=sy,
                            creation=time, stroke='#fff', stroke_width=_AXIS_STROKE_WIDTH))
        if abs(ty) > 1e-9:
            objects.append(Text(text=f'{ty:g}', x=x_zero - tick_len - _TICK_GAP, y=sy + _TICK_FONT_SIZE * 0.35,
                                font_size=_TICK_FONT_SIZE, text_anchor='end',
                                creation=time, fill='#aaa', stroke_width=0))

    return VCollection(*objects, creation=time)


class Axes(VCollection):
    """Coordinate axes with ticks and labels.

    x_range/y_range: (min, max) in math coordinates (animated via Real attributes).
    x/y/plot_width/plot_height: SVG pixel area for the axes.
    """
    def __init__(self, x_range=(-5, 5), y_range=None,
                 x=260, y=100, plot_width=1400, plot_height=880,
                 x_label=None, y_label=None,
                 show_grid=False, equal_aspect=False, creation=0, z=0):
        self.x_min = attributes.Real(creation, x_range[0])
        self.x_max = attributes.Real(creation, x_range[1])
        if equal_aspect and y_range is not None:
            plot_height = int(plot_width * (y_range[1] - y_range[0])
                              / (x_range[1] - x_range[0]))
            y = (1080 - plot_height) // 2
        self.plot_x, self.plot_y = x, y
        self.plot_width, self.plot_height = plot_width, plot_height
        self.num_points = 200
        self._show_grid = show_grid

        self._axis_labels = []

        if y_range is not None:
            self.y_min = attributes.Real(creation, y_range[0])
            self.y_max = attributes.Real(creation, y_range[1])
            self._axis_labels = self._build_label_objects(x_label, y_label, creation, z)
            super().__init__(creation=creation, z=z)
        else:
            # Defer axis construction until the first add_function call.
            self.y_min = self.y_max = None
            self._deferred_axes = (x_label, y_label, creation, z)
            super().__init__(creation=creation, z=z)

        self.axes = DynamicObject(self._build_axes_at, creation=creation, z=z)

    def _build_label_objects(self, x_label, y_label, creation, z):
        """Build axis title TexObjects (x_label, y_label) with dynamic position."""
        objects = []
        for label_text, is_x in [(x_label, True), (y_label, False)]:
            if not label_text:
                continue
            tex = label_text if '$' in label_text else f'${label_text}$'
            lbl = TexObject(tex, font_size=DEFAULT_FONT_SIZE, creation=creation, z=z,
                            fill='#fff', stroke_width=0)
            _, _, lw, lh = lbl.bbox(creation)
            if is_x:
                def _cx(t, _lw=lw):
                    ymin = self.y_min.at_time(t)
                    ymax = self.y_max.at_time(t)
                    y_zero = self.plot_y + (1 - (0 - ymin) / (ymax - ymin)) * self.plot_height if ymin <= 0 <= ymax else self.plot_y + self.plot_height
                    return self.plot_x + self.plot_width + _LABEL_GAP + _lw / 2
                def _cy(t):
                    ymin = self.y_min.at_time(t)
                    ymax = self.y_max.at_time(t)
                    return self.plot_y + (1 - (0 - ymin) / (ymax - ymin)) * self.plot_height if ymin <= 0 <= ymax else self.plot_y + self.plot_height
                lbl.x.set_onward(creation, lambda t, _lw=lw: _cx(t) - _lw / 2)
                lbl.y.set_onward(creation, lambda t, _lh=lh: _cy(t) - _lh / 2)
            else:
                def _cx_y(t):
                    xmin = self.x_min.at_time(t)
                    xmax = self.x_max.at_time(t)
                    return self.plot_x + (0 - xmin) / (xmax - xmin) * self.plot_width if xmin <= 0 <= xmax else self.plot_x
                def _cy_y(t, _lh=lh):
                    return self.plot_y - _LABEL_GAP - _lh / 2
                lbl.x.set_onward(creation, lambda t, _lw=lw: _cx_y(t) - _lw / 2)
                lbl.y.set_onward(creation, lambda t, _lh=lh: _cy_y(t) - _lh / 2)
            objects.append(lbl)
        return objects

    def _build_axes_at(self, time):
        """Build axis decoration VObjects for the given time, including axis labels."""
        if self.y_min is None:
            y_min, y_max = -5, 5
        else:
            y_min = self.y_min.at_time(time)
            y_max = self.y_max.at_time(time)
        coll = _build_axes_decoration(
            self.x_min.at_time(time), self.x_max.at_time(time), y_min, y_max,
            self.plot_x, self.plot_y, self.plot_width, self.plot_height,
            self._show_grid, time)
        # Include the persistent axis title labels (TexObjects created once)
        for lbl in self._axis_labels:
            coll.objects.append(lbl)
        return coll

    def _math_to_svg_x(self, val, time=0):
        xmin = self.x_min.at_time(time)
        xmax = self.x_max.at_time(time)
        return self.plot_x + (val - xmin) / (xmax - xmin) * self.plot_width

    def _math_to_svg_y(self, val, time=0):
        ymin = self.y_min.at_time(time)
        ymax = self.y_max.at_time(time)
        return self.plot_y + (1 - (val - ymin) / (ymax - ymin)) * self.plot_height

    def _make_curve(self, func, creation, z, num_points=None, x_range=None,
                    lincl=True, rincl=True, **style_kwargs):
        """Create a Path whose 'd' attribute resamples func each frame.

        x_range: optional (min, max) to limit the curve domain.  Both bounds
        are stored as Real attributes on the returned Path (``._domain_min``,
        ``._domain_max``) so they can be animated.
        lincl/rincl: whether the left/right bounds are inclusive (default True).
        """
        if num_points is None:
            num_points = self.num_points
        curve = Path('', x=0, y=0, creation=creation, z=z, **style_kwargs)
        if x_range is not None:
            curve._domain_min = attributes.Real(creation, x_range[0])
            curve._domain_max = attributes.Real(creation, x_range[1])
        else:
            curve._domain_min = None
            curve._domain_max = None
        def _compute_d(time, _func=func, _np=num_points):
            xmin = self.x_min.at_time(time)
            xmax = self.x_max.at_time(time)
            ymin = self.y_min.at_time(time)
            ymax = self.y_max.at_time(time)
            # Wrap function to return NaN outside domain bounds
            f = _func
            extra_xs = None
            if curve._domain_min is not None or curve._domain_max is not None:
                lo = curve._domain_min.at_time(time) if curve._domain_min else xmin
                hi = curve._domain_max.at_time(time) if curve._domain_max else xmax
                _li, _ri = lincl, rincl
                def _in_domain(x, _lo=lo, _hi=hi):
                    return (_lo <= x if _li else _lo < x) and (x <= _hi if _ri else x < _hi)
                f = lambda x, _f=_func: _f(x) if _in_domain(x) else float('nan')
                # Inject domain boundaries so the curve starts/ends exactly there
                extra_xs = [v for v in (lo, hi) if xmin <= v <= xmax]
            _, _, segments, _ = _sample_function(
                f, xmin, xmax, (ymin, ymax), _np,
                self.plot_x, self.plot_y, self.plot_width, self.plot_height,
                extra_xs=extra_xs)
            parts = []
            for seg in segments:
                if seg:
                    parts.append('M' + 'L'.join(f'{x},{y}' for x, y in seg))
            return ''.join(parts)
        curve.d.set_onward(creation, _compute_d)
        curve._func = func
        curve._num_points = num_points
        return curve

    def _add_plot_obj(self, obj):
        """Append *obj* to the axes."""
        self.objects.append(obj)
        return obj

    def to_svg(self, time):
        parts = []
        # Render axis decorations
        if self.axes.show.at_time(time):
            parts.append(self.axes.to_svg(time))

        # Render child objects (curves, areas, labels, etc.)
        visible = [(getattr(o, 'z', attributes.Real(0, 0)).at_time(time), o)
                    for o in self.objects if o.show.at_time(time)]
        for _, obj in sorted(visible, key=lambda x: x[0]):
            parts.append(obj.to_svg(time))

        inner = '\n'.join(parts)
        sx, sy = self._scale_x.at_time(time), self._scale_y.at_time(time)
        transform = ''
        if sx != 1 or sy != 1:
            if self._scale_origin:
                cx, cy = self._scale_origin
                transform = f' transform="translate({cx},{cy}) scale({sx},{sy}) translate({-cx},{-cy})"'
            else:
                transform = f' transform="scale({sx},{sy})"'
        return f'<g{transform}>\n{inner}\n</g>'

    def _build_deferred_axes(self, func, num_points):
        """Auto-detect y_range from *func* and build the axis label objects."""
        xmin = self.x_min.at_time(0)
        xmax = self.x_max.at_time(0)
        y_min, y_max, _, _ = _sample_function(
            func, xmin, xmax, None, num_points,
            self.plot_x, self.plot_y, self.plot_width, self.plot_height)
        x_label, y_label, creation, z = self._deferred_axes
        self.y_min = attributes.Real(creation, y_min)
        self.y_max = attributes.Real(creation, y_max)
        self._axis_labels = self._build_label_objects(x_label, y_label, creation, z)
        del self._deferred_axes

    def add_function(self, func, label=None, label_direction='up', label_x_val=None,
                     num_points=200, x_range=None, lincl=True, rincl=True,
                     creation=0, z=0, **styling_kwargs):
        """Add a function curve to these axes.  Returns the Path object.

        If *label* is provided, a TeX label is created and positioned on the
        curve.  The label fill colour defaults to the curve's stroke colour.
        If *y_range* was not set on the Axes, it is auto-detected from the
        first function added.
        x_range: optional (min, max) to limit the curve domain.  Both bounds
        are stored as Real attributes (``._domain_min``, ``._domain_max``)
        so they can be animated.
        lincl/rincl: whether the left/right bounds are inclusive (default True).
        """
        if hasattr(self, '_deferred_axes'):
            self._build_deferred_axes(func, num_points)
        style_kw = {'stroke': '#58C4DD', 'stroke_width': 5, 'fill_opacity': 0} | styling_kwargs
        curve = self._make_curve(func, creation, z, num_points=num_points,
                                 x_range=x_range, lincl=lincl, rincl=rincl, **style_kw)
        self._add_plot_obj(curve)
        if label is not None:
            label_obj = self.get_graph_label(func, label, x_val=label_x_val,
                                direction=label_direction,
                                fill=style_kw['stroke'], creation=creation, z=z)
            # Wrap create() so the label fades in alongside the curve drawing
            _original_create = curve.create
            def _create_with_label(*args, _lbl=label_obj, _orig=_original_create, **kw):
                result = _orig(*args, **kw)
                start = kw.get('start', args[0] if args else 0)
                end = kw.get('end', args[1] if len(args) > 1 else 1)
                _lbl.show.set_onward(0, False)
                _lbl.show.set_onward(start, True)
                _lbl.fadein(start, end)
                return result
            curve.create = _create_with_label
        return curve

    plot = add_function

    def set_x_range(self, start_time, end_time, x_range, **kwargs):
        """Animate the x-axis range to new bounds."""
        self.x_min.move_to(start_time, end_time, x_range[0], **kwargs)
        self.x_max.move_to(start_time, end_time, x_range[1], **kwargs)

    def set_y_range(self, start_time, end_time, y_range, **kwargs):
        """Animate the y-axis range to new bounds."""
        self.y_min.move_to(start_time, end_time, y_range[0], **kwargs)
        self.y_max.move_to(start_time, end_time, y_range[1], **kwargs)

    def set_ranges(self, start_time, end_time, x_range, y_range, **kwargs):
        """Animate both axis ranges to new bounds."""
        self.set_x_range(start_time, end_time, x_range, **kwargs)
        self.set_y_range(start_time, end_time, y_range, **kwargs)

    def coords_to_point(self, x, y, time=0):
        """Convert math coordinates to SVG pixel coordinates."""
        return (self._math_to_svg_x(x, time), self._math_to_svg_y(y, time))

    def input_to_graph_point(self, x, func, time=0):
        """Convert a math x-value and function to SVG pixel coordinates: (x, f(x))."""
        return self.coords_to_point(x, func(x), time)

    def graph_position(self, func, x_attr):
        """Return a callable(time) -> (svg_x, svg_y) that tracks a point on func.
        x_attr: a Real attribute or any object with .at_time(t), or a plain callable(t).
        """
        get_x = x_attr.at_time if hasattr(x_attr, 'at_time') else x_attr
        def _pos(time):
            xv = get_x(time)
            return self.coords_to_point(xv, func(xv), time)
        return _pos

    def get_graph_label(self, func, label, x_val=None, direction='up', buff=SMALL_BUFF,
                         font_size=48, creation=0, z=0, **styling_kwargs):
        """Create a TeX label positioned near the end of a plotted function.

        The label dynamically tracks the current x_max (or a fixed *x_val*)
        so it follows the curve as axis ranges animate.
        """
        style_kw = {'fill': '#fff', 'stroke_width': 0} | styling_kwargs
        label_obj = TexObject(label, font_size=font_size, creation=creation, z=z, **style_kw)
        _, _, lw, lh = label_obj.bbox(creation)
        offsets = {'up': (0, -buff - lh/2), 'down': (0, buff + lh/2),
                   'left': (-buff - lw/2, 0), 'right': (buff + lw/2, 0)}
        off_dx, off_dy = offsets.get(direction, offsets['up'])
        if x_val is not None:
            def _get_xv(t, _xv=x_val):
                return _xv
        else:
            def _get_xv(t):
                return self.x_max.at_time(t)
        def _label_x(t):
            xv = _get_xv(t)
            sx = self._math_to_svg_x(xv, t)
            return sx + off_dx - lw / 2
        def _label_y(t):
            xv = _get_xv(t)
            sy = self._math_to_svg_y(func(xv), t)
            return sy + off_dy - lh / 2
        label_obj.x.set_onward(creation, _label_x)
        label_obj.y.set_onward(creation, _label_y)
        self.objects.append(label_obj)
        return label_obj

    def plot_line_graph(self, x_values, y_values, creation=0, z=0, **styling_kwargs):
        """Plot a line graph from discrete data points. Returns a VCollection."""
        style_kw = {'stroke': '#58C4DD', 'stroke_width': 5, 'fill_opacity': 0} | styling_kwargs
        # Build a Path with dynamic d that re-maps data points each frame
        data = list(zip(x_values, y_values))
        curve = Path('', x=0, y=0, creation=creation, z=z, **style_kw)
        def _compute_d(time, _data=data):
            pts = [(self._math_to_svg_x(x, time), self._math_to_svg_y(y, time))
                   for x, y in _data]
            if not pts:
                return ''
            return 'M' + 'L'.join(f'{x},{y}' for x, y in pts)
        curve.d.set_onward(creation, _compute_d)
        # Static dots at initial positions
        dots = [Dot(cx=self._math_to_svg_x(x, creation), cy=self._math_to_svg_y(y, creation),
                    r=3, creation=creation, z=z,
                    fill=style_kw.get('stroke', '#58C4DD')) for x, y in data]
        group = VCollection(curve, *dots, creation=creation, z=z)
        self._add_plot_obj(group)
        return group

    def get_area(self, curve_or_func, x_range=None, bounded_graph=None, creation=0, z=0, **styling_kwargs):
        """Create a shaded area under a curve/function (or between two curves).

        *curve_or_func* can be a function, or a Path returned by plot() (which has ._func).
        """
        style_kw = {'fill': '#58C4DD', 'fill_opacity': 0.3, 'stroke_width': 0} | styling_kwargs
        # Resolve the function
        if callable(curve_or_func) and not hasattr(curve_or_func, '_func'):
            func = curve_or_func
        elif hasattr(curve_or_func, '_func'):
            func = curve_or_func._func
        else:
            raise TypeError('get_area requires a function or a curve returned by plot()')

        bound_func = None
        if bounded_graph is not None:
            if callable(bounded_graph) and not hasattr(bounded_graph, '_func'):
                bound_func = bounded_graph
            elif hasattr(bounded_graph, '_func'):
                bound_func = bounded_graph._func
            else:
                raise TypeError('bounded_graph must be a function or a curve returned by plot()')

        area = Path('', x=0, y=0, creation=creation, z=z, **style_kw)
        def _compute_area_d(time, _func=func, _bfunc=bound_func, _xr=x_range):
            xmin = self.x_min.at_time(time)
            xmax = self.x_max.at_time(time)
            ymin = self.y_min.at_time(time)
            ymax = self.y_max.at_time(time)
            lo = _xr[0] if _xr else xmin
            hi = _xr[1] if _xr else xmax
            n = 200
            step = (hi - lo) / n
            verts = []
            for i in range(n + 1):
                xv = lo + i * step
                yv = _func(xv)
                sx = self.plot_x + (xv - xmin) / (xmax - xmin) * self.plot_width
                sy = self.plot_y + (1 - (yv - ymin) / (ymax - ymin)) * self.plot_height
                sy = max(self.plot_y, min(self.plot_y + self.plot_height, sy))
                verts.append((sx, sy))
            if _bfunc is not None:
                bound_verts = []
                for i in range(n + 1):
                    xv = lo + i * step
                    yv = _bfunc(xv)
                    sx = self.plot_x + (xv - xmin) / (xmax - xmin) * self.plot_width
                    sy = self.plot_y + (1 - (yv - ymin) / (ymax - ymin)) * self.plot_height
                    sy = max(self.plot_y, min(self.plot_y + self.plot_height, sy))
                    bound_verts.append((sx, sy))
                all_verts = verts + list(reversed(bound_verts))
            else:
                baseline_y = self.plot_y + (1 - (0 - ymin) / (ymax - ymin)) * self.plot_height if ymin <= 0 <= ymax else self.plot_y + self.plot_height
                all_verts = verts + [(verts[-1][0], baseline_y), (verts[0][0], baseline_y)]
            if not all_verts:
                return ''
            return 'M' + 'L'.join(f'{x},{y}' for x, y in all_verts) + 'Z'
        area.d.set_onward(creation, _compute_area_d)
        self._add_plot_obj(area)
        return area

    def get_rect(self, x1, y1, x2, y2, creation=0, z=0, **styling_kwargs):
        """Create a Rectangle from two corners in math coordinates.

        Each coordinate can be a static number or an animated attribute (has ``.at_time()``).
        """
        style_kw = {'fill': '#58C4DD', 'fill_opacity': 0.3, 'stroke': '#fff', 'stroke_width': 1} | styling_kwargs
        rect = Rectangle(width=0, height=0, creation=creation, z=z, **style_kw)
        def _val(c, t):
            return c.at_time(t) if hasattr(c, 'at_time') else c
        def _x(t):
            sx1 = self._math_to_svg_x(_val(x1, t), t)
            sx2 = self._math_to_svg_x(_val(x2, t), t)
            return min(sx1, sx2)
        def _y(t):
            sy1 = self._math_to_svg_y(_val(y1, t), t)
            sy2 = self._math_to_svg_y(_val(y2, t), t)
            return min(sy1, sy2)
        def _w(t):
            sx1 = self._math_to_svg_x(_val(x1, t), t)
            sx2 = self._math_to_svg_x(_val(x2, t), t)
            return abs(sx2 - sx1)
        def _h(t):
            sy1 = self._math_to_svg_y(_val(y1, t), t)
            sy2 = self._math_to_svg_y(_val(y2, t), t)
            return abs(sy2 - sy1)
        rect.x.set_onward(creation, _x)
        rect.y.set_onward(creation, _y)
        rect.width.set_onward(creation, _w)
        rect.height.set_onward(creation, _h)
        self._add_plot_obj(rect)
        return rect

    def get_vertical_line(self, x, y_val=None, creation=0, z=0, **styling_kwargs):
        """Draw a vertical line at math x-coordinate."""
        style_kw = {'stroke': '#FFFF00', 'stroke_width': 2} | styling_kwargs
        line = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z, **style_kw)
        def _p1(t):
            sx = self._math_to_svg_x(x, t)
            ymin = self.y_min.at_time(t)
            ymax = self.y_max.at_time(t)
            baseline_y = self._math_to_svg_y(0, t) if ymin <= 0 <= ymax else self.plot_y + self.plot_height
            return (sx, baseline_y)
        def _p2(t):
            sx = self._math_to_svg_x(x, t)
            top_y = self._math_to_svg_y(y_val, t) if y_val is not None else self.plot_y
            return (sx, top_y)
        line.p1.set_onward(creation, _p1)
        line.p2.set_onward(creation, _p2)
        self._add_plot_obj(line)
        return line

    def get_riemann_rectangles(self, func, x_range, dx=0.1, creation=0, z=0, **styling_kwargs):
        """Create rectangles approximating the area under func.

        Returns a DynamicObject that rebuilds each frame."""
        style_kw = {'fill': '#58C4DD', 'fill_opacity': 0.5, 'stroke': '#fff', 'stroke_width': 1} | styling_kwargs
        def _build(time):
            xmin = self.x_min.at_time(time)
            xmax = self.x_max.at_time(time)
            ymin = self.y_min.at_time(time)
            ymax = self.y_max.at_time(time)
            x_lo, x_hi = x_range
            baseline_y = self.plot_y + (1 - (0 - ymin) / (ymax - ymin)) * self.plot_height if ymin <= 0 <= ymax else self.plot_y + self.plot_height
            rects = []
            xv = x_lo
            while xv < x_hi - 1e-9:
                x_next = min(xv + dx, x_hi)
                yv = func(xv)
                sx1 = self.plot_x + (xv - xmin) / (xmax - xmin) * self.plot_width
                sx2 = self.plot_x + (x_next - xmin) / (xmax - xmin) * self.plot_width
                sy = self.plot_y + (1 - (yv - ymin) / (ymax - ymin)) * self.plot_height
                rects.append(Rectangle(width=sx2 - sx1, height=abs(baseline_y - sy),
                                       x=sx1, y=min(sy, baseline_y),
                                       creation=time, z=z, **style_kw))
                xv = x_next
            return VCollection(*rects, creation=time, z=z)
        dyn = DynamicObject(_build, creation=creation, z=z)
        self._add_plot_obj(dyn)
        return dyn


class Graph(Axes):
    """Axes with an initial function curve plotted.

    Inherits all Axes methods (add_function, get_area, get_riemann_rectangles, etc.).
    """
    def __init__(self, func, x_range=(-5, 5), y_range=None, num_points=200,
                 x=260, y=100, plot_width=1400, plot_height=880,
                 x_label='x', y_label='y', label=None, label_direction='up',
                 label_x_val=None, show_grid=False,
                 creation=0, z=0, **styling_kwargs):
        # Determine y_range from function if not given
        x_min, x_max = x_range
        y_min, y_max, _, _ = _sample_function(
            func, x_min, x_max, y_range, num_points, x, y, plot_width, plot_height)
        super().__init__(x_range=x_range, y_range=(y_min, y_max),
                         x=x, y=y, plot_width=plot_width, plot_height=plot_height,
                         x_label=x_label, y_label=y_label,
                         show_grid=show_grid, creation=creation, z=z)
        self.func = func
        self.num_points = num_points
        curve_style = {'stroke': '#58C4DD', 'stroke_width': 5, 'fill_opacity': 0} | styling_kwargs
        self.curve = self._make_curve(func, creation, z, num_points=num_points, **curve_style)
        self._add_plot_obj(self.curve)
        if label is not None:
            self.get_graph_label(func, label, x_val=label_x_val,
                                direction=label_direction,
                                fill=curve_style['stroke'], creation=creation, z=z)


class NumberPlane(VCollection):
    """Cartesian coordinate plane with background grid lines.

    x_range/y_range: (min, max, step) in logical units (default: 1 unit = 135px).
    cx, cy: pixel position of the origin (default: screen center).
    width, height: pixel extent of the plane (default: full 1920x1080).
    faded_line_ratio: number of minor subdivisions per step (default: 4).

    Uses a single Path per grid layer for efficiency (~3 objects instead of ~100).
    """
    def __init__(self, x_range=None, y_range=None,
                 cx=960, cy=540, width=1920, height=1080,
                 faded_line_ratio=4,
                 background_line_style=None, faded_line_style=None,
                 axis_style=None, creation=0, z=0):
        unit = UNIT
        if x_range is None:
            half_x = width / (2 * unit)
            x_range = (-half_x, half_x, 1)
        if y_range is None:
            half_y = height / (2 * unit)
            y_range = (-half_y, half_y, 1)

        x_min, x_max = x_range[0], x_range[1]
        x_step = x_range[2] if len(x_range) > 2 else 1
        y_min, y_max = y_range[0], y_range[1]
        y_step = y_range[2] if len(y_range) > 2 else 1

        self._cx, self._cy = cx, cy
        self._unit = unit
        self._x_range = (x_min, x_max, x_step)
        self._y_range = (y_min, y_max, y_step)

        major_kw = {'stroke': '#4488AA', 'stroke_width': 3, 'stroke_opacity': 0.6}
        if background_line_style:
            major_kw |= background_line_style
        faded_kw = {'stroke': '#225566', 'stroke_width': 1, 'stroke_opacity': 0.4}
        if faded_line_style:
            faded_kw |= faded_line_style
        axis_kw = {'stroke': '#fff', 'stroke_width': 3}
        if axis_style:
            axis_kw |= axis_style

        # Pixel bounds of the plane
        px_left = round(cx + x_min * unit)
        px_right = round(cx + x_max * unit)
        px_top = round(cy - y_max * unit)
        px_bottom = round(cy - y_min * unit)

        def _build_path(vmin_x, vmax_x, step_x, vmin_y, vmax_y, step_y, skip_zero=False):
            """Build an SVG path string for a grid (vertical + horizontal lines)."""
            segs = []
            # Vertical lines
            v = math.ceil(vmin_x / step_x - 1e-9) * step_x
            while v <= vmax_x + 1e-9:
                if skip_zero and abs(v) < 1e-9:
                    v += step_x
                    continue
                px = round(cx + v * unit)
                segs.append(f'M{px} {px_top}V{px_bottom}')
                v += step_x
            # Horizontal lines
            v = math.ceil(vmin_y / step_y - 1e-9) * step_y
            while v <= vmax_y + 1e-9:
                if skip_zero and abs(v) < 1e-9:
                    v += step_y
                    continue
                py = round(cy - v * unit)
                segs.append(f'M{px_left} {py}H{px_right}')
                v += step_y
            return ''.join(segs)

        objects: list[VObject] = []

        # Layer 1: Minor (faded) grid lines
        if faded_line_ratio > 1:
            minor_x = x_step / faded_line_ratio
            minor_y = y_step / faded_line_ratio
            faded_d = _build_path(x_min, x_max, minor_x, y_min, y_max, minor_y)
            if faded_d:
                objects.append(Path(faded_d, creation=creation, z=z,
                                    fill_opacity=0, **faded_kw))

        # Layer 2: Major grid lines (skip origin to avoid overlap with axes)
        major_d = _build_path(x_min, x_max, x_step, y_min, y_max, y_step, skip_zero=True)
        if major_d:
            objects.append(Path(major_d, creation=creation, z=z,
                                fill_opacity=0, **major_kw))

        # Layer 3: Axis lines (on top)
        axis_d = []
        if x_min <= 0 <= x_max:
            axis_d.append(f'M{cx} {px_top}V{px_bottom}')
        if y_min <= 0 <= y_max:
            axis_d.append(f'M{px_left} {cy}H{px_right}')
        if axis_d:
            objects.append(Path(''.join(axis_d), creation=creation, z=z,
                                fill_opacity=0, **axis_kw))

        super().__init__(*objects, creation=creation, z=z)

    def coords_to_point(self, x, y):
        """Convert logical coordinates to SVG pixel coordinates."""
        return (self._cx + x * self._unit, self._cy - y * self._unit)



def _arrowhead(from_x, from_y, to_x, to_y, tip_length, tip_width, fill, creation, z):
    """Create a triangular arrowhead polygon pointing from (from_x,from_y) toward (to_x,to_y)."""
    dx, dy = to_x - from_x, to_y - from_y
    length = math.sqrt(dx * dx + dy * dy) or 1
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    bx, by = to_x - ux * tip_length, to_y - uy * tip_length
    hw = tip_width / 2
    return Polygon((to_x, to_y), (bx + px * hw, by + py * hw), (bx - px * hw, by - py * hw),
                   creation=creation, z=z, fill=fill, fill_opacity=1, stroke_width=0)


class Arrow(VCollection):
    """Arrow as a line (shaft) with a triangular arrowhead (and optional second head)."""
    def __init__(self, x1=0, y1=0, x2=100, y2=100, tip_length=DEFAULT_ARROW_TIP_LENGTH, tip_width=DEFAULT_ARROW_TIP_WIDTH,
                 double_ended=False, creation=0, z=0, **styling_kwargs):
        shaft_style = {'stroke': '#fff', 'stroke_width': 5} | styling_kwargs
        tip_fill = shaft_style.get('stroke', '#fff')
        self.shaft = Line(x1=x1, y1=y1, x2=x2, y2=y2, creation=creation, z=z, **shaft_style)
        self.tip = _arrowhead(x1, y1, x2, y2, tip_length, tip_width, tip_fill, creation, z)
        objects = [self.shaft, self.tip]
        if double_ended:
            self.tail = _arrowhead(x2, y2, x1, y1, tip_length, tip_width, tip_fill, creation, z)
            objects.append(self.tail)
        super().__init__(*objects, creation=creation, z=z)


class DoubleArrow(Arrow):
    """Double-ended arrow (shorthand for Arrow with double_ended=True)."""
    def __init__(self, x1=0, y1=0, x2=100, y2=100, tip_length=DEFAULT_ARROW_TIP_LENGTH, tip_width=DEFAULT_ARROW_TIP_WIDTH,
                 creation=0, z=0, **styling_kwargs):
        super().__init__(x1=x1, y1=y1, x2=x2, y2=y2, tip_length=tip_length,
                         tip_width=tip_width, double_ended=True,
                         creation=creation, z=z, **styling_kwargs)


class CurvedArrow(VCollection):
    """Arrow with a curved (quadratic bezier) shaft and a triangular tip."""
    def __init__(self, x1=0, y1=0, x2=100, y2=100, angle=0.4,
                 tip_length=DEFAULT_ARROW_TIP_LENGTH, tip_width=DEFAULT_ARROW_TIP_WIDTH, creation=0, z=0, **styling_kwargs):
        shaft_style = {'stroke': '#fff', 'stroke_width': 5, 'fill_opacity': 0} | styling_kwargs
        tip_fill = shaft_style.get('stroke', '#fff')
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = x2 - x1, y2 - y1
        cx, cy = mx - dy * angle, my + dx * angle
        shaft = Path(f'M{x1},{y1}Q{cx},{cy} {x2},{y2}',
                     creation=creation, z=z, **shaft_style)
        tip = _arrowhead(cx, cy, x2, y2, tip_length, tip_width, tip_fill, creation, z)
        super().__init__(shaft, tip, creation=creation, z=z)



def _transform_rel_svg_path(raw, m00, m01, m10, m11, tx, ty):
    """Parse a relative SVG path and convert to absolute coords with an affine transform.

    Transform: (x, y) → (m00*x + m01*y + tx, m10*x + m11*y + ty)
    Only handles the lowercase commands used in the brace template: m c v h s z.
    """
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
# At {0}=0 the brace is ~0.906 wide × ~0.167 tall, tip pointing +Y.
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
    """Curly brace annotation pointing at a target object.

    Uses a LaTeX-style curly-brace shape, rendered as a filled path.

    direction: 'down', 'up', 'left', or 'right' — which side the brace sits on.
    label: optional text placed near the brace midpoint.
    buff: spacing between the target and the brace in pixels.
    depth: peak height of the brace tip in pixels.
    """
    def __init__(self, target, direction='down', label=None, buff=SMALL_BUFF,
                 depth=18, creation=0, z=0, **styling_kwargs):
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

        # Affine transform: (x,y) in template → pixel coords
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
            label_gap = 30
            label_obj = TexObject(label, font_size=30, creation=creation, z=z,
                                  fill='#fff', stroke_width=0)
            _, _, lw, lh = label_obj.bbox(creation)
            if direction == 'down':
                lx = bx + bw / 2
                ly = by + bh + buff + depth + label_gap + lh / 2
            elif direction == 'up':
                lx = bx + bw / 2
                ly = by - buff - depth - label_gap - lh / 2
            elif direction == 'right':
                lx = bx + bw + buff + depth + label_gap + lw / 2
                ly = by + bh / 2
            else:  # left
                lx = bx - buff - depth - label_gap - lw / 2
                ly = by + bh / 2
            label_obj.center_to_pos(posx=lx, posy=ly)
            objects.append(label_obj)

        super().__init__(*objects, creation=creation, z=z)



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
                 label_font_size=36, creation=0, z=0, **styling_kwargs):
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
                    + label_font_size * 0.35))
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

    def shift(self, dx=0, dy=0, start_time: float = 0, end_time: float | None = None, easing=easings.smooth):
        """Shift the angle by moving vertex, p1, p2 (label follows automatically)."""
        for c in [self.vertex, self.p1, self.p2]:
            if end_time is None:
                c.add_onward(start_time, (dx, dy))
            else:
                s, e = start_time, end_time
                c.add_onward(s, lambda t, _s=s, _e=e: (dx * easing((t-_s)/(_e-_s)), dy * easing((t-_s)/(_e-_s))), last_change=e)
        return self


class RightAngle(VCollection):
    """Right angle indicator (small square) at a vertex between two perpendicular lines."""
    def __init__(self, vertex, p1, p2, size=18, creation=0, z=0, **styling_kwargs):
        vx, vy = vertex
        d1x, d1y = p1[0] - vx, p1[1] - vy
        d2x, d2y = p2[0] - vx, p2[1] - vy
        len1 = math.sqrt(d1x*d1x + d1y*d1y) or 1
        len2 = math.sqrt(d2x*d2x + d2y*d2y) or 1
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
    def __init__(self, size=36, cx=960, cy=540, creation=0, z=0, **styling_kwargs):
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

    def number_to_point(self, value):
        """Convert a number on the line to an SVG (x, y) coordinate."""
        t = (value - self.x_start) / (self.x_end - self.x_start)
        return (self.origin_x + t * self.length, self.origin_y)



class PieChart(VCollection):
    """Pie chart visualization using Wedge sectors.

    values: list of numeric values (proportional sizes).
    labels: optional list of labels.
    colors: list of sector colors (cycles if shorter than values).
    """
    def __init__(self, values, labels=None, colors=None, cx=960, cy=540, r=240,
                 start_angle=90, creation=0, z=0):
        if colors is None:
            colors = ['#58C4DD', '#83C167', '#FC6255', '#FFFF00', '#9A72AC',
                      '#F0AC5F', '#C55F73', '#5CD0B3']
        total = sum(values)
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
        super().__init__(*objects, creation=creation, z=z)
        self.values = values


class BarChart(VCollection):
    """Simple bar chart visualization.

    values: list of numeric values.
    labels: optional list of labels (same length as values).
    colors: list of bar colors (cycles if shorter than values).
    """
    def __init__(self, values, labels=None, colors=None, x=120, y=60,
                 width=1440, height=840, bar_spacing=0.2,
                 creation=0, z=0):
        if colors is None:
            colors = ['#58C4DD', '#83C167', '#FC6255', '#FFFF00', '#9A72AC',
                      '#F0AC5F', '#C55F73', '#5CD0B3']
        n = len(values)
        max_val = max(abs(v) for v in values) if values else 1
        bar_width = width / n
        inner_width = bar_width * (1 - bar_spacing)
        objects: list[VObject] = []

        for i, val in enumerate(values):
            bar_h = abs(val) / max_val * height * 0.85
            bx = x + i * bar_width + (bar_width - inner_width) / 2
            by = y + height - bar_h if val >= 0 else y + height
            color = colors[i % len(colors)]
            bar = Rectangle(inner_width, bar_h, x=bx, y=by,
                            creation=creation, z=z,
                            fill=color, fill_opacity=0.8, stroke_width=0)
            objects.append(bar)

            if labels and i < len(labels):
                lbl = Text(text=str(labels[i]),
                           x=bx + inner_width / 2, y=y + height + 24,
                           font_size=14, text_anchor='middle',
                           creation=creation, z=z, fill='#aaa', stroke_width=0)
                objects.append(lbl)

        # Baseline
        baseline = Line(x1=x, y1=y + height, x2=x + width, y2=y + height,
                        creation=creation, z=z, stroke='#fff', stroke_width=3)
        objects.append(baseline)
        super().__init__(*objects, creation=creation, z=z)
        self.values = values
        self.bar_count = n



class Table(VCollection):
    """Table for displaying tabular data with optional row/column labels.

    data: 2D list of values (data[row][col]).
    row_labels/col_labels: optional label lists.
    """
    def __init__(self, data, row_labels=None, col_labels=None,
                 x=120, y=60, cell_width=160, cell_height=60,
                 font_size=24, creation=0, z=0, **styling_kwargs):
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
                cy = y + y_off + r * cell_height + cell_height / 2 + font_size * 0.35
                t = Text(text=str(data[r][c]), x=cx, y=cy,
                         font_size=font_size, text_anchor='middle',
                         creation=creation, z=z, fill='#fff', stroke_width=0)
                objects.append(t)
                row_entries.append(t)
            self.entries.append(row_entries)

        if row_labels:
            for r, label in enumerate(row_labels):
                cx = x + cell_width / 2
                cy = y + y_off + r * cell_height + cell_height / 2 + font_size * 0.35
                objects.append(Text(text=str(label), x=cx, y=cy,
                                   font_size=font_size, text_anchor='middle',
                                   creation=creation, z=z, fill='#FFFF00', stroke_width=0))
        if col_labels:
            for c, label in enumerate(col_labels):
                cx = x + x_off + c * cell_width + cell_width / 2
                cy = y + cell_height / 2 + font_size * 0.35
                objects.append(Text(text=str(label), x=cx, y=cy,
                                   font_size=font_size, text_anchor='middle',
                                   creation=creation, z=z, fill='#FFFF00', stroke_width=0))

        super().__init__(*objects, creation=creation, z=z)
        self.rows, self.cols = rows, cols

    def get_entry(self, row, col):
        """Return the Text object at (row, col) for animation."""
        return self.entries[row][col]



class DynamicObject(VObject):
    """VObject whose SVG is regenerated each frame by calling func(time).
    func should return a VObject. Useful for reactive/always-redraw patterns."""
    def __init__(self, func, creation=0, z=0):
        super().__init__(creation=creation, z=z)
        self._func = func
        self.styling = style.Styling({}, creation=creation)

    def to_svg(self, time):
        return self._func(time).to_svg(time)

    def path(self, time):
        obj = self._func(time)
        return obj.path(time) if hasattr(obj, 'path') else ''

    def bbox(self, time):
        return self._func(time).bbox(time)



class Matrix(VCollection):
    """Display a mathematical matrix with square bracket delimiters.

    data: 2D list of values.
    x, y: position of the matrix center.
    """
    def __init__(self, data, x=960, y=540, font_size=36, h_spacing=80, v_spacing=50,
                 creation=0, z=0, **styling_kwargs):
        rows = len(data)
        cols = len(data[0]) if data else 0
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
                ty = y - total_h / 2 + r * v_spacing + font_size * 0.35
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

    if tag == 'path':
        return Path(element['d'], **_merged_attrs('d'))
    elif tag == 'rect':
        return Path(f'M0,0l{g("width")},0l0,{g("height")}l-{g("width")},0z',
                    **_merged_attrs('width', 'height'))
    elif tag == 'circle':
        return Circle(r=g('r', 100), cx=g('cx'), cy=g('cy'), **_merged_attrs('r', 'cx', 'cy'))
    elif tag == 'ellipse':
        return Ellipse(rx=g('rx', 100), ry=g('ry', 50), cx=g('cx'), cy=g('cy'), **_merged_attrs('rx', 'ry', 'cx', 'cy'))
    elif tag == 'line':
        return Line(x1=g('x1'), y1=g('y1'), x2=g('x2'), y2=g('y2'), **_merged_attrs('x1', 'y1', 'x2', 'y2'))
    elif tag == 'polygon':
        return Polygon(*_parse_svg_points(element.get('points', '')), **_merged_attrs('points'))
    elif tag == 'polyline':
        return Lines(*_parse_svg_points(element.get('points', '')), **_merged_attrs('points'))
    else:
        raise NotImplementedError(f'Type "{tag}" has no from_svg implemented')


_SVG_SHAPE_TAGS = frozenset({'path', 'rect', 'circle', 'ellipse', 'line', 'polygon', 'polyline'})

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
        if getattr(elem, 'name', None) in _SVG_SHAPE_TAGS:
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
    def __init__(self, canvas, source, display, creation=0, z=999,
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

    def __init__(self, shape_a, shape_b, creation=0, z=0, **styling_kwargs):
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



class Title(VCollection):
    """Centered title text at the top of the canvas.
    Accepts the same keyword args as Text (font_size, fill, etc.)."""
    def __init__(self, text, creation=0, z=0, **kwargs):
        defaults = {'font_size': 60, 'text_anchor': 'middle', 'fill': '#fff',
                    'stroke_width': 0}
        defaults.update(kwargs)
        txt = Text(text, x=960, y=DEFAULT_OBJECT_TO_EDGE_BUFF + 60,
                   creation=creation, z=z, **defaults)
        underline = Line(x1=960 - 200, y1=DEFAULT_OBJECT_TO_EDGE_BUFF + 80,
                         x2=960 + 200, y2=DEFAULT_OBJECT_TO_EDGE_BUFF + 80,
                         stroke='#888', stroke_width=2, creation=creation, z=z)
        super().__init__(txt, underline, creation=creation, z=z)



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
    return parser.parse_args()

