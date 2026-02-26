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
    UNIT, SMALL_BUFF, DEFAULT_FONT_SIZE,
    DEFAULT_ARROW_TIP_LENGTH, DEFAULT_ARROW_TIP_WIDTH,
    DEFAULT_OBJECT_TO_EDGE_BUFF, _sample_function,
)
from vectormation._base import VObject, VCollection
from vectormation._shapes import (
    Polygon, Circle, Ellipse, Dot, Rectangle, Line, Lines,
    Text, Path, Arc, Wedge,
)

# Marching squares segment table: maps 4-bit case to list of (edge1, edge2) pairs.
_MARCH_SEGS = {
    1: [('left', 'top')], 2: [('top', 'right')],
    3: [('left', 'right')], 4: [('right', 'bottom')],
    5: [('left', 'bottom'), ('top', 'right')],
    6: [('top', 'bottom')], 7: [('left', 'bottom')],
    8: [('bottom', 'left')], 9: [('bottom', 'top')],
    10: [('left', 'top'), ('right', 'bottom')],
    11: [('right', 'bottom')], 12: [('right', 'left')],
    13: [('top', 'right')], 14: [('top', 'left')],
}


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
    def __init__(self, to_render, x=0, y=0, font_size=48, creation=0, z=0, **styles):
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
    x_span = x_max - x_min if x_max != x_min else 1
    y_span = y_max - y_min if y_max != y_min else 1
    y_zero = plot_y + (1 - (0 - y_min) / y_span) * plot_height if y_min <= 0 <= y_max else plot_y + plot_height
    x_zero = plot_x + (0 - x_min) / x_span * plot_width if x_min <= 0 <= x_max else plot_x
    tick_len = SMALL_BUFF

    def _to_svg_x(val):
        return plot_x + (val - x_min) / x_span * plot_width

    def _to_svg_y(val):
        return plot_y + (1 - (val - y_min) / y_span) * plot_height

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
        if equal_aspect and y_range is not None and x_range[1] != x_range[0]:
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
                lbl.x.set_onward(creation, self.plot_x + self.plot_width + _LABEL_GAP)
                lbl.y.set_onward(creation, lambda t, _lh=lh: self._baseline_y(t) - _lh / 2)
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

    def _get_bounds(self, time=0):
        """Return (xmin, xmax, ymin, ymax) at the given time."""
        return (self.x_min.at_time(time), self.x_max.at_time(time),
                self.y_min.at_time(time), self.y_max.at_time(time))

    def _math_to_svg_x(self, val, time=0):
        xmin, xmax = self.x_min.at_time(time), self.x_max.at_time(time)
        span = xmax - xmin
        if span == 0:
            span = 1
        return self.plot_x + (val - xmin) / span * self.plot_width

    def _math_to_svg_y(self, val, time=0):
        ymin, ymax = self.y_min.at_time(time), self.y_max.at_time(time)
        span = ymax - ymin
        if span == 0:
            span = 1
        return self.plot_y + (1 - (val - ymin) / span) * self.plot_height

    def _baseline_y(self, time=0):
        """SVG y-coordinate of y=0 (or bottom edge if 0 is out of range)."""
        ymin, ymax = self.y_min.at_time(time), self.y_max.at_time(time)
        if ymin <= 0 <= ymax:
            span = ymax - ymin
            if span == 0:
                return self.plot_y + self.plot_height
            return self.plot_y + (1 - (0 - ymin) / span) * self.plot_height
        return self.plot_y + self.plot_height

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

    def add_coordinates(self, creation=0, font_size=None, color='#aaa'):
        """Add coordinate labels at each tick mark on both axes."""
        if font_size is None:
            font_size = _TICK_FONT_SIZE
        xmin, xmax = self.x_min.at_time(creation), self.x_max.at_time(creation)
        ymin = self.y_min.at_time(creation) if self.y_min is not None else -5
        ymax = self.y_max.at_time(creation) if self.y_max is not None else 5
        for val in _nice_ticks(xmin, xmax):
            sx = self._math_to_svg_x(val, creation)
            sy = self.plot_y + self.plot_height + font_size + 4
            lbl = Text(text=f'{val:g}', x=sx, y=sy, font_size=font_size,
                       text_anchor='middle', fill=color, stroke_width=0, creation=creation)
            self._add_plot_obj(lbl)
        for val in _nice_ticks(ymin, ymax):
            sx = self.plot_x - 8
            sy = self._math_to_svg_y(val, creation) + font_size * 0.35
            lbl = Text(text=f'{val:g}', x=sx, y=sy, font_size=font_size,
                       text_anchor='end', fill=color, stroke_width=0, creation=creation)
            self._add_plot_obj(lbl)
        return self

    def add_grid(self):
        """Enable background grid lines on the axes."""
        self._show_grid = True
        return self

    def add_zero_line(self, axis='x', creation=0, z=-1, **styling_kwargs):
        """Add a prominent zero line (y=0 for axis='x', x=0 for axis='y').
        Useful to visually separate positive/negative regions."""
        styling_kwargs.setdefault('stroke', '#888')
        styling_kwargs.setdefault('stroke_width', 2)
        styling_kwargs.setdefault('stroke_dasharray', '6 3')
        # Use placeholder coords; set_onward overrides them dynamically
        line = Line(x1=0, y1=0, x2=0, y2=0,
                    creation=creation, z=z, **styling_kwargs)
        if axis == 'x':
            line.p1.set_onward(creation,
                lambda t: self.coords_to_point(self.x_min.at_time(t), 0, t))
            line.p2.set_onward(creation,
                lambda t: self.coords_to_point(self.x_max.at_time(t), 0, t))
        else:
            line.p1.set_onward(creation,
                lambda t: self.coords_to_point(0, self.y_min.at_time(t), t))
            line.p2.set_onward(creation,
                lambda t: self.coords_to_point(0, self.y_max.at_time(t), t))
        self._add_plot_obj(line)
        return line

    def set_x_range(self, start_time, end_time, x_range, **kwargs):
        """Animate the x-axis range to new bounds."""
        self.x_min.move_to(start_time, end_time, x_range[0], **kwargs)
        self.x_max.move_to(start_time, end_time, x_range[1], **kwargs)
        return self

    def set_y_range(self, start_time, end_time, y_range, **kwargs):
        """Animate the y-axis range to new bounds."""
        self.y_min.move_to(start_time, end_time, y_range[0], **kwargs)
        self.y_max.move_to(start_time, end_time, y_range[1], **kwargs)
        return self

    def set_ranges(self, start_time, end_time, x_range, y_range, **kwargs):
        """Animate both axis ranges to new bounds."""
        self.set_x_range(start_time, end_time, x_range, **kwargs)
        self.set_y_range(start_time, end_time, y_range, **kwargs)
        return self

    def coords_to_point(self, x, y, time=0):
        """Convert math coordinates to SVG pixel coordinates."""
        return (self._math_to_svg_x(x, time), self._math_to_svg_y(y, time))

    def annotate_point(self, x, y, label='', direction='up', buff=15,
                       creation=0, z=0, **styling_kwargs):
        """Add a dot and label at a math coordinate.

        Returns a VCollection containing the dot and optional label.
        """
        sx, sy = self.coords_to_point(x, y, creation)
        style_kw = {'fill': '#FFFF00', 'stroke_width': 0} | styling_kwargs
        dot = Dot(cx=sx, cy=sy, r=6, creation=creation, z=z + 1, **style_kw)
        dot.c.set_onward(creation,
            lambda t, _x=x, _y=y: self.coords_to_point(_x, _y, t))
        objs = [dot]
        if label:
            offsets = {'up': (0, -buff - 10), 'down': (0, buff + 15),
                       'left': (-buff - 10, 5), 'right': (buff + 10, 5)}
            dx, dy = offsets.get(direction, offsets['up'])
            lbl = Text(text=label, x=sx + dx, y=sy + dy,
                       font_size=20, text_anchor='middle',
                       creation=creation, z=z + 2,
                       fill=style_kw.get('fill', '#FFFF00'), stroke_width=0)
            _dx, _dy = dx, dy
            lbl.x.set_onward(creation,
                lambda t, _x=x, _y=y, _dx=_dx: self.coords_to_point(_x, _y, t)[0] + _dx)
            lbl.y.set_onward(creation,
                lambda t, _x=x, _y=y, _dy=_dy: self.coords_to_point(_x, _y, t)[1] + _dy)
            objs.append(lbl)
        group = VCollection(*objs, creation=creation, z=z)
        self._add_plot_obj(group)
        return group

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
        _get_xv = (lambda t, _xv=x_val: _xv) if x_val is not None else (lambda t: self.x_max.at_time(t))
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

    def plot_parametric(self, func, t_range=(0, 1), num_points=200,
                        creation=0, z=0, **styling_kwargs):
        """Plot a parametric curve func(t) -> (x, y) in math coordinates.

        t_range: (t_min, t_max) parameter range.
        Returns a Path object.
        """
        style_kw = {'stroke': '#58C4DD', 'stroke_width': 5, 'fill_opacity': 0} | styling_kwargs
        curve = Path('', x=0, y=0, creation=creation, z=z, **style_kw)
        def _compute_d(time, _func=func, _np=num_points, _tr=t_range):
            t0, t1 = _tr
            pts = []
            for i in range(_np + 1):
                t = t0 + i * (t1 - t0) / _np
                mx, my = _func(t)
                sx, sy = self._math_to_svg_x(mx, time), self._math_to_svg_y(my, time)
                pts.append(f'{sx},{sy}')
            return 'M' + 'L'.join(pts) if pts else ''
        curve.d.set_onward(creation, _compute_d)
        curve._func = func
        self._add_plot_obj(curve)
        return curve

    def plot_polar(self, func, theta_range=(0, 2 * math.pi), num_points=200,
                    creation=0, z=0, **styling_kwargs):
        """Plot a polar curve r=func(theta) on these axes.
        theta_range: (min, max) in radians.
        Returns a Path object."""
        def _parametric(theta):
            r = func(theta)
            return (r * math.cos(theta), r * math.sin(theta))
        return self.plot_parametric(_parametric, t_range=theta_range,
                                    num_points=num_points, creation=creation,
                                    z=z, **styling_kwargs)

    def plot_implicit(self, func, num_points=100, creation=0, z=0, **styling_kwargs):
        """Plot an implicit curve f(x, y) = 0 using marching squares.

        func: callable(x, y) -> float; the zero contour is drawn.
        Returns a Path object.
        """
        style_kw = {'stroke': '#58C4DD', 'stroke_width': 3, 'fill_opacity': 0} | styling_kwargs
        curve = Path('', x=0, y=0, creation=creation, z=z, **style_kw)
        def _compute_d(time, _func=func, _n=num_points):
            xmin, xmax, ymin, ymax = self._get_bounds(time)
            dx = (xmax - xmin) / _n
            dy = (ymax - ymin) / _n
            segments = []
            for i in range(_n):
                for j in range(_n):
                    x0 = xmin + i * dx
                    y0 = ymin + j * dy
                    x1, y1 = x0 + dx, y0 + dy
                    vals = [_func(x0, y0), _func(x1, y0), _func(x1, y1), _func(x0, y1)]
                    case = sum(1 << k for k, v in enumerate(vals) if v > 0)
                    if case == 0 or case == 15:
                        continue
                    # Linear interpolation along edges
                    def _lerp(v0, v1, p0, p1):
                        if abs(v1 - v0) < 1e-12:
                            return ((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2)
                        t = -v0 / (v1 - v0)
                        return (p0[0] + t * (p1[0] - p0[0]), p0[1] + t * (p1[1] - p0[1]))
                    corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
                    edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
                    pts = []
                    for a, b in edges:
                        if (vals[a] > 0) != (vals[b] > 0):
                            mx, my = _lerp(vals[a], vals[b], corners[a], corners[b])
                            sx = self._math_to_svg_x(mx, time)
                            sy = self._math_to_svg_y(my, time)
                            pts.append((sx, sy))
                    if len(pts) == 2:
                        segments.append(f'M{pts[0][0]},{pts[0][1]}L{pts[1][0]},{pts[1][1]}')
                    elif len(pts) == 4:
                        segments.append(f'M{pts[0][0]},{pts[0][1]}L{pts[1][0]},{pts[1][1]}')
                        segments.append(f'M{pts[2][0]},{pts[2][1]}L{pts[3][0]},{pts[3][1]}')
            return ''.join(segments)
        curve.d.set_onward(creation, _compute_d)
        self._add_plot_obj(curve)
        return curve

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
        # Dynamic dots that track animated axis ranges
        dots = []
        for x, y in data:
            dot = Dot(cx=self._math_to_svg_x(x, creation), cy=self._math_to_svg_y(y, creation),
                      r=3, creation=creation, z=z,
                      fill=style_kw.get('stroke', '#58C4DD'))
            dot.c.set_onward(creation,
                lambda t, _x=x, _y=y: self.coords_to_point(_x, _y, t))
            dots.append(dot)
        group = VCollection(curve, *dots, creation=creation, z=z)
        self._add_plot_obj(group)
        return group

    def plot_scatter(self, x_values, y_values, r=5, creation=0, z=0, **styling_kwargs):
        """Plot a scatter plot (dots only, no connecting lines).
        Returns a VCollection of Dot objects."""
        style_kw = {'fill': '#58C4DD', 'stroke_width': 0} | styling_kwargs
        data = list(zip(x_values, y_values))
        dots = []
        for x, y in data:
            dot = Dot(cx=0, cy=0, r=r, creation=creation, z=z, **style_kw)
            _x, _y = x, y
            dot.c.set_onward(creation, lambda t, _xv=_x, _yv=_y: self.coords_to_point(_xv, _yv, t))
            dots.append(dot)
        group = VCollection(*dots, creation=creation, z=z)
        self._add_plot_obj(group)
        return group

    def plot_step(self, x_values, y_values, creation=0, z=0, **styling_kwargs):
        """Plot a step function (horizontal then vertical segments).
        Returns a Path object."""
        style_kw = {'stroke': '#58C4DD', 'stroke_width': 3, 'fill_opacity': 0} | styling_kwargs
        data = list(zip(x_values, y_values))
        curve = Path('', x=0, y=0, creation=creation, z=z, **style_kw)
        def _compute_d(time, _data=data):
            if not _data:
                return ''
            parts = []
            sx, sy = self._math_to_svg_x(_data[0][0], time), self._math_to_svg_y(_data[0][1], time)
            parts.append(f'M{sx},{sy}')
            for i in range(1, len(_data)):
                # Horizontal step to new x
                nx = self._math_to_svg_x(_data[i][0], time)
                parts.append(f'L{nx},{sy}')
                # Vertical step to new y
                sy = self._math_to_svg_y(_data[i][1], time)
                parts.append(f'L{nx},{sy}')
            return ''.join(parts)
        curve.d.set_onward(creation, _compute_d)
        self._add_plot_obj(curve)
        return curve

    def plot_filled_step(self, x_values, y_values, baseline=0, creation=0, z=0, **styling_kwargs):
        """Plot a step function with shaded area down to baseline.
        Returns a Path object."""
        style_kw = {'fill': '#58C4DD', 'fill_opacity': 0.3,
                    'stroke': '#58C4DD', 'stroke_width': 2} | styling_kwargs
        data = list(zip(x_values, y_values))
        curve = Path('', x=0, y=0, creation=creation, z=z, **style_kw)
        def _compute_d(time, _data=data, _bl=baseline):
            if not _data:
                return ''
            parts = []
            base_y = self._math_to_svg_y(_bl, time)
            sx = self._math_to_svg_x(_data[0][0], time)
            sy = self._math_to_svg_y(_data[0][1], time)
            last_x = sx
            parts.append(f'M{sx},{base_y}L{sx},{sy}')
            for i in range(1, len(_data)):
                last_x = self._math_to_svg_x(_data[i][0], time)
                parts.append(f'L{last_x},{sy}')
                sy = self._math_to_svg_y(_data[i][1], time)
                parts.append(f'L{last_x},{sy}')
            parts.append(f'L{last_x},{base_y}Z')
            return ''.join(parts)
        curve.d.set_onward(creation, _compute_d)
        self._add_plot_obj(curve)
        return curve

    def plot_histogram(self, data, bins=10, creation=0, z=0, **styling_kwargs):
        """Plot a histogram from raw data values.
        bins: int (number of bins) or list of bin edges.
        Returns a VCollection of Rectangle objects."""
        style_kw = {'fill': '#58C4DD', 'fill_opacity': 0.5,
                    'stroke': '#58C4DD', 'stroke_width': 1} | styling_kwargs
        if isinstance(bins, int):
            lo, hi = min(data), max(data)
            if lo == hi:
                lo, hi = lo - 1, hi + 1
            step = (hi - lo) / bins
            edges = [lo + i * step for i in range(bins + 1)]
        else:
            edges = list(bins)
        counts = [0] * (len(edges) - 1)
        for v in data:
            for i in range(len(edges) - 1):
                if edges[i] <= v < edges[i + 1] or (i == len(edges) - 2 and v == edges[i + 1]):
                    counts[i] += 1
                    break
        rects = []
        for i, count in enumerate(counts):
            if count == 0:
                continue
            x_lo, x_hi = edges[i], edges[i + 1]
            rect = Rectangle(width=0, height=0, x=0, y=0, creation=creation, z=z, **style_kw)
            _xl, _xh, _c = x_lo, x_hi, count
            rect.x.set_onward(creation, lambda t, _xl=_xl: self._math_to_svg_x(_xl, t))
            rect.width.set_onward(creation, lambda t, _xl=_xl, _xh=_xh: abs(
                self._math_to_svg_x(_xh, t) - self._math_to_svg_x(_xl, t)))
            rect.y.set_onward(creation, lambda t, _c=_c: self._math_to_svg_y(_c, t))
            rect.height.set_onward(creation, lambda t, _c=_c: abs(
                self._math_to_svg_y(0, t) - self._math_to_svg_y(_c, t)))
            rects.append(rect)
        group = VCollection(*rects, creation=creation, z=z)
        self._add_plot_obj(group)
        return group

    def plot_bar(self, x_values, y_values, width=0.8, creation=0, z=0,
                  align='center', **styling_kwargs):
        """Plot bars at x_values with heights y_values.
        width: bar width in math units.  align: 'center', 'left', or 'right'.
        Returns a VCollection of Rectangle objects."""
        style_kw = {'fill': '#58C4DD', 'fill_opacity': 0.7,
                    'stroke': '#58C4DD', 'stroke_width': 1} | styling_kwargs
        rects = []
        for xv, yv in zip(x_values, y_values):
            if align == 'left':
                xl = xv
            elif align == 'right':
                xl = xv - width
            else:
                xl = xv - width / 2
            xr = xl + width
            rect = Rectangle(width=0, height=0, x=0, y=0,
                              creation=creation, z=z, **style_kw)
            _xl, _xr, _yv = xl, xr, yv
            rect.x.set_onward(creation, lambda t, _xl=_xl: self._math_to_svg_x(_xl, t))
            rect.width.set_onward(creation, lambda t, _xl=_xl, _xr=_xr: abs(
                self._math_to_svg_x(_xr, t) - self._math_to_svg_x(_xl, t)))
            if yv >= 0:
                rect.y.set_onward(creation, lambda t, _yv=_yv: self._math_to_svg_y(_yv, t))
                rect.height.set_onward(creation, lambda t, _yv=_yv: abs(
                    self._math_to_svg_y(0, t) - self._math_to_svg_y(_yv, t)))
            else:
                rect.y.set_onward(creation, lambda t: self._math_to_svg_y(0, t))
                rect.height.set_onward(creation, lambda t, _yv=_yv: abs(
                    self._math_to_svg_y(_yv, t) - self._math_to_svg_y(0, t)))
            rects.append(rect)
        group = VCollection(*rects, creation=creation, z=z)
        self._add_plot_obj(group)
        return group

    def plot_stem(self, x_values, y_values, baseline=0, r=4, creation=0, z=0,
                   **styling_kwargs):
        """Plot a stem chart: vertical lines from baseline to each data point with a dot marker.
        Returns a VCollection of lines and dots."""
        line_kw = {'stroke': '#58C4DD', 'stroke_width': 1.5}
        dot_kw = {'fill': '#58C4DD', 'stroke_width': 0}
        for k, v in styling_kwargs.items():
            if k.startswith('dot_'):
                dot_kw[k[4:]] = v
            else:
                line_kw[k] = v
        objs = []
        for xv, yv in zip(x_values, y_values):
            # Stem line
            stem = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z, **line_kw)
            _xv, _yv, _bl = xv, yv, baseline
            stem.p1.set_onward(creation,
                lambda t, _x=_xv, _bl=_bl: self.coords_to_point(_x, _bl, t))
            stem.p2.set_onward(creation,
                lambda t, _x=_xv, _y=_yv: self.coords_to_point(_x, _y, t))
            self._add_plot_obj(stem)
            objs.append(stem)
            # Dot marker
            dot = Dot(cx=0, cy=0, r=r, creation=creation, z=z + 1, **dot_kw)
            dot.c.set_onward(creation,
                lambda t, _x=_xv, _y=_yv: self.coords_to_point(_x, _y, t))
            self._add_plot_obj(dot)
            objs.append(dot)
        return VCollection(*objs, creation=creation, z=z)

    def plot_grouped_bar(self, data, group_labels=None, bar_width=0.25,
                          group_spacing=1.0, colors=None, creation=0, z=0,
                          **styling_kwargs):
        """Plot grouped bar chart. data: list of lists (each inner list is one series).
        Returns a VCollection of all bars."""
        n_series = len(data)
        if n_series == 0:
            return VCollection(creation=creation, z=z)
        n_groups = max(len(s) for s in data)
        if colors is None:
            colors = ['#FF6B6B', '#58C4DD', '#83C167', '#FFFF00',
                      '#FF79C6', '#B8BB26', '#BD93F9', '#FFB86C']
        style_kw = {'stroke_width': 1} | styling_kwargs
        rects = []
        for si, series in enumerate(data):
            color = colors[si % len(colors)]
            for gi, yv in enumerate(series):
                x_center = (gi + 1) * group_spacing
                x_offset = (si - n_series / 2 + 0.5) * bar_width
                xl = x_center + x_offset - bar_width / 2
                xr = xl + bar_width
                rect = Rectangle(width=0, height=0, x=0, y=0,
                                  fill=color, fill_opacity=0.7, stroke=color,
                                  creation=creation, z=z, **style_kw)
                _xl, _xr, _yv = xl, xr, yv
                rect.x.set_onward(creation, lambda t, _xl=_xl: self._math_to_svg_x(_xl, t))
                rect.width.set_onward(creation, lambda t, _xl=_xl, _xr=_xr: abs(
                    self._math_to_svg_x(_xr, t) - self._math_to_svg_x(_xl, t)))
                if yv >= 0:
                    rect.y.set_onward(creation, lambda t, _yv=_yv: self._math_to_svg_y(_yv, t))
                    rect.height.set_onward(creation, lambda t, _yv=_yv: abs(
                        self._math_to_svg_y(0, t) - self._math_to_svg_y(_yv, t)))
                else:
                    rect.y.set_onward(creation, lambda t: self._math_to_svg_y(0, t))
                    rect.height.set_onward(creation, lambda t, _yv=_yv: abs(
                        self._math_to_svg_y(_yv, t) - self._math_to_svg_y(0, t)))
                rects.append(rect)
        group = VCollection(*rects, creation=creation, z=z)
        self._add_plot_obj(group)
        return group

    @staticmethod
    def _lerp_colormap(frac, colormap):
        """Interpolate a color from a colormap: list of (frac, '#rrggbb') stops."""
        frac = max(0, min(1, frac))
        for i in range(len(colormap) - 1):
            f0, c0 = colormap[i]
            f1, c1 = colormap[i + 1]
            if f0 <= frac <= f1:
                t = (frac - f0) / max(f1 - f0, 1e-9)
                a = int(c0[1:3], 16), int(c0[3:5], 16), int(c0[5:7], 16)
                b = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
                return '#{:02x}{:02x}{:02x}'.format(
                    *(int(a[j] + (b[j] - a[j]) * t) for j in range(3)))
        return colormap[-1][1]

    @staticmethod
    def _resolve_func(obj, label='argument'):
        """Extract a callable from a function or a curve with ._func."""
        if hasattr(obj, '_func'):
            return obj._func
        if callable(obj):
            return obj
        raise TypeError(f'{label} must be a function or a curve returned by plot()')

    def get_area(self, curve_or_func, x_range=None, bounded_graph=None, creation=0, z=0, **styling_kwargs):
        """Create a shaded area under a curve/function (or between two curves).

        *curve_or_func* can be a function, or a Path returned by plot() (which has ._func).
        """
        style_kw = {'fill': '#58C4DD', 'fill_opacity': 0.3, 'stroke_width': 0} | styling_kwargs
        func = self._resolve_func(curve_or_func, 'curve_or_func')
        bound_func = self._resolve_func(bounded_graph, 'bounded_graph') if bounded_graph is not None else None

        area = Path('', x=0, y=0, creation=creation, z=z, **style_kw)
        def _compute_area_d(time, _func=func, _bfunc=bound_func, _xr=x_range):
            xmin, xmax = self.x_min.at_time(time), self.x_max.at_time(time)
            lo = _xr[0] if _xr else xmin
            hi = _xr[1] if _xr else xmax
            n = 200
            step = (hi - lo) / n
            def _sample(f):
                pts = []
                for i in range(n + 1):
                    xv = lo + i * step
                    sx = self._math_to_svg_x(xv, time)
                    sy = self._math_to_svg_y(f(xv), time)
                    sy = max(self.plot_y, min(self.plot_y + self.plot_height, sy))
                    pts.append((sx, sy))
                return pts
            verts = _sample(_func)
            if _bfunc is not None:
                all_verts = verts + list(reversed(_sample(_bfunc)))
            else:
                by = self._baseline_y(time)
                all_verts = verts + [(verts[-1][0], by), (verts[0][0], by)]
            if not all_verts:
                return ''
            return 'M' + 'L'.join(f'{x},{y}' for x, y in all_verts) + 'Z'
        area.d.set_onward(creation, _compute_area_d)
        self._add_plot_obj(area)
        return area

    def add_legend(self, entries, position='upper right', font_size=18,
                    bg_color='#1a1a2e', bg_opacity=0.8, creation=0, z=10):
        """Add a legend box.
        entries: list of (label_str, color_str) pairs.
        position: 'upper right', 'upper left', 'lower right', 'lower left'.
        Returns a VCollection."""
        if not entries:
            return VCollection(creation=creation, z=z)
        row_h = font_size + 8
        swatch_w = 16
        max_label_w = max(len(e[0]) for e in entries) * font_size * 0.55
        box_w = swatch_w + max_label_w + 30
        box_h = len(entries) * row_h + 12
        # Position relative to the axes plot area
        margin = 10
        if 'right' in position:
            bx = self.plot_x + self.plot_width - box_w - margin
        else:
            bx = self.plot_x + margin
        if 'upper' in position or 'top' in position:
            by = self.plot_y + margin
        else:
            by = self.plot_y + self.plot_height - box_h - margin
        objs = []
        bg = Rectangle(width=box_w, height=box_h, x=bx, y=by,
                        fill=bg_color, fill_opacity=bg_opacity,
                        stroke='#555', stroke_width=1, rx=4, ry=4,
                        creation=creation, z=z)
        objs.append(bg)
        for i, (label, color) in enumerate(entries):
            ry = by + 8 + i * row_h
            swatch = Rectangle(width=swatch_w, height=swatch_w,
                                x=bx + 8, y=ry, fill=color, stroke_width=0,
                                creation=creation, z=z + 1)
            lbl = Text(text=label, x=bx + 8 + swatch_w + 8, y=ry + font_size - 2,
                        font_size=font_size, fill='#ddd', stroke_width=0,
                        creation=creation, z=z + 1)
            objs.extend([swatch, lbl])
        group = VCollection(*objs, creation=creation, z=z)
        self._add_plot_obj(group)
        return group

    def get_area_between(self, func1, func2, x_range=None, creation=0, z=0, **styling_kwargs):
        """Shade the area between two functions.
        func1, func2: callables. The area between them is shaded.
        x_range: optional (min, max) to limit domain.
        Returns a Path object."""
        style_kw = {'fill': '#58C4DD', 'fill_opacity': 0.3, 'stroke_width': 0} | styling_kwargs
        return self.get_area(func1, bounded_graph=func2, x_range=x_range,
                             creation=creation, z=z, **style_kw)

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

    def add_dot_label(self, x, y, label=None, dot_color='#FF6B6B', dot_radius=6,
                       label_offset=(10, -10), font_size=20, creation=0, z=0):
        """Add a labeled dot at math coordinates (x, y). Returns (dot, text) or dot."""
        from vectormation._shapes import Dot as _Dot, Text as _Text
        sx, sy = self.coords_to_point(x, y, time=creation)
        dot = _Dot(cx=sx, cy=sy, r=dot_radius, fill=dot_color,
                   creation=creation, z=z)
        dot.c.set_onward(creation,
            lambda t, _x=x, _y=y: self.coords_to_point(_x, _y, t))
        self._add_plot_obj(dot)
        if label is not None:
            lx, ly = sx + label_offset[0], sy + label_offset[1]
            lbl = _Text(text=str(label), x=lx, y=ly, font_size=font_size,
                        fill=dot_color, stroke_width=0, creation=creation, z=z)
            _ox, _oy = label_offset
            lbl.x.set_onward(creation,
                lambda t, _x=x, _y=y, _ox=_ox: self.coords_to_point(_x, _y, t)[0] + _ox)
            lbl.y.set_onward(creation,
                lambda t, _x=x, _y=y, _oy=_oy: self.coords_to_point(_x, _y, t)[1] + _oy)
            self._add_plot_obj(lbl)
            return dot, lbl
        return dot

    def add_arrow_annotation(self, x, y, text, direction='up', length=80, buff=10,
                              font_size=20, creation=0, z=5, **styling_kwargs):
        """Add a labeled arrow pointing to a math coordinate.
        Returns a VCollection with arrow and label."""
        style_kw = {'stroke': '#FFFF00', 'fill': '#FFFF00'} | styling_kwargs
        sx, sy = self.coords_to_point(x, y, creation)
        offsets = {
            'up': (0, -1), 'down': (0, 1), 'left': (-1, 0), 'right': (1, 0),
        }
        dx, dy = offsets.get(direction, (0, -1))
        ax1 = sx + dx * (length + buff)
        ay1 = sy + dy * (length + buff)
        ax2 = sx + dx * buff
        ay2 = sy + dy * buff
        _tl, _tw = 12, 10
        arrow = Arrow(x1=ax1, y1=ay1, x2=ax2, y2=ay2,
                       tip_length=_tl, tip_width=_tw,
                       creation=creation, z=z, **style_kw)
        # Dynamic arrow endpoints
        _dx, _dy, _lb = dx, dy, length + buff
        _bb = buff
        def _base(t, _x=x, _y=y):
            return self.coords_to_point(_x, _y, t)
        arrow.shaft.p1.set_onward(creation,
            lambda t, _dx=_dx, _dy=_dy, _lb=_lb: (
                (_b := _base(t))[0] + _dx * _lb, _b[1] + _dy * _lb))
        arrow.shaft.p2.set_onward(creation,
            lambda t, _dx=_dx, _dy=_dy, _bb=_bb: (
                (_b := _base(t))[0] + _dx * _bb, _b[1] + _dy * _bb))
        # Dynamic arrowhead tip (3 vertices) — precompute constants
        _hw = _tw / 2
        _ln = math.hypot(_dx, _dy) or 1
        _ux, _uy = _dx / _ln, _dy / _ln
        _px, _py = -_uy, _ux
        # Precompute fixed offsets from the tip base point
        _back_x, _back_y = -_ux * _tl, -_uy * _tl
        _perp_x, _perp_y = _px * _hw, _py * _hw
        _tb_cache = [None, None]  # [time, (bx, by)]
        def _tip_base(t, _dx=_dx, _dy=_dy, _bb=_bb):
            if _tb_cache[0] == t:
                return _tb_cache[1]
            b = _base(t)
            result = b[0] + _dx * _bb, b[1] + _dy * _bb
            _tb_cache[0], _tb_cache[1] = t, result
            return result
        arrow.tip.vertices[0].set_onward(creation,
            lambda t: _tip_base(t))
        arrow.tip.vertices[1].set_onward(creation,
            lambda t, _bx=_back_x, _by=_back_y, _px=_perp_x, _py=_perp_y: (
                (_tb := _tip_base(t))[0] + _bx + _px, _tb[1] + _by + _py))
        arrow.tip.vertices[2].set_onward(creation,
            lambda t, _bx=_back_x, _by=_back_y, _px=_perp_x, _py=_perp_y: (
                (_tb := _tip_base(t))[0] + _bx - _px, _tb[1] + _by - _py))
        # Label at the far end of the arrow
        lx = ax1 + dx * 15
        ly = ay1 + dy * 15
        lbl = Text(text=text, x=lx, y=ly, font_size=font_size,
                    text_anchor='middle', fill=style_kw.get('fill', '#FFFF00'),
                    stroke_width=0, creation=creation, z=z + 1)
        _lxo, _lyo = dx * (length + buff + 15), dy * (length + buff + 15)
        lbl.x.set_onward(creation,
            lambda t, _lxo=_lxo: _base(t)[0] + _lxo)
        lbl.y.set_onward(creation,
            lambda t, _lyo=_lyo: _base(t)[1] + _lyo)
        group = VCollection(arrow, lbl, creation=creation, z=z)
        self._add_plot_obj(group)
        return group

    def add_cursor(self, func, x_start, x_end, start: float = 0, end: float = 1,
                    r=6, creation=0, z=5, easing=easings.smooth, **styling_kwargs):
        """Add an animated dot that travels along func from x_start to x_end.
        Returns the Dot object."""
        style_kw = {'fill': '#FFFF00', 'stroke_width': 0} | styling_kwargs
        dot = Dot(cx=0, cy=0, r=r, creation=creation, z=z, **style_kw)
        dur = end - start
        if dur <= 0:
            sx, sy = self.coords_to_point(x_start, func(x_start), creation)
            dot.c.set_onward(creation, (sx, sy))
        else:
            s, d = start, dur
            xs, xe = x_start, x_end
            def _pos(t, _s=s, _d=d, _xs=xs, _xe=xe, _easing=easing):
                progress = _easing((t - _s) / _d)
                xv = _xs + (_xe - _xs) * progress
                return self.coords_to_point(xv, func(xv), t)
            dot.c.set(s, end, _pos, stay=True)
        dot._show_from(start)
        self._add_plot_obj(dot)
        return dot

    def add_trace(self, func, x_start, x_end, start: float = 0, end: float = 1,
                   r=5, trail_width=2, creation=0, z=5, easing=easings.smooth,
                   **styling_kwargs):
        """Animated dot that traces along func, leaving a trail behind it.
        Returns a VCollection with (dot, trail_path).
        The trail grows progressively as the dot moves."""
        style_kw = {'fill': '#FFFF00', 'stroke': '#FFFF00', 'stroke_width': 0} | styling_kwargs
        dot = self.add_cursor(func, x_start, x_end, start=start, end=end,
                               r=r, creation=creation, z=z + 1, easing=easing,
                               **{k: v for k, v in style_kw.items()
                                  if k in ('fill', 'stroke_width')})
        # Trail path that grows as the dot moves
        trail = Path('', x=0, y=0, creation=creation, z=z,
                     stroke=style_kw.get('stroke', '#FFFF00'),
                     stroke_width=trail_width, fill_opacity=0)
        _xs, _xe = x_start, x_end
        _s, _d = start, max(end - start, 1e-9)
        n_pts = 80
        def _compute_trail(t, _s=_s, _d=_d, _xs=_xs, _xe=_xe, _n=n_pts, _easing=easing):
            progress = max(0, min(1, _easing((t - _s) / _d)))
            x_cur = _xs + (_xe - _xs) * progress
            steps = max(2, int(_n * progress))
            pts = []
            for i in range(steps):
                frac = i / max(steps - 1, 1)
                xv = _xs + (x_cur - _xs) * frac
                pts.append(self.coords_to_point(xv, func(xv), t))
            if not pts:
                return ''
            return 'M' + 'L'.join(f'{px},{py}' for px, py in pts)
        trail.d.set(start, end, _compute_trail, stay=True)
        self._add_plot_obj(trail)
        group = VCollection(dot, trail, creation=creation, z=z)
        return group

    def get_line_from_to(self, x1, y1, x2, y2, creation=0, z=0, **styling_kwargs):
        """Draw a solid line between two math coordinate points.
        Returns a Line object."""
        style_kw = {'stroke': '#fff', 'stroke_width': 2} | styling_kwargs
        line = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z, **style_kw)
        _x1, _y1, _x2, _y2 = x1, y1, x2, y2
        line.p1.set_onward(creation, lambda t, _a=_x1, _b=_y1: self.coords_to_point(_a, _b, t))
        line.p2.set_onward(creation, lambda t, _a=_x2, _b=_y2: self.coords_to_point(_a, _b, t))
        self._add_plot_obj(line)
        return line

    def highlight_x_range(self, x_lo, x_hi, creation=0, z=-1, **styling_kwargs):
        """Shade a vertical strip between x_lo and x_hi math coordinates.
        Returns a Rectangle object."""
        style_kw = {'fill': '#FFFF00', 'fill_opacity': 0.15, 'stroke_width': 0} | styling_kwargs
        rect = Rectangle(width=0, height=0, x=0, y=0,
                          creation=creation, z=z, **style_kw)
        _lo, _hi = x_lo, x_hi
        rect.y.set_onward(creation, lambda t: self.plot_y)
        rect.height.set_onward(creation, lambda t: self.plot_height)
        rect.x.set_onward(creation, lambda t, _l=_lo, _h=_hi: min(
            self._math_to_svg_x(_l, t), self._math_to_svg_x(_h, t)))
        rect.width.set_onward(creation, lambda t, _l=_lo, _h=_hi: abs(
            self._math_to_svg_x(_h, t) - self._math_to_svg_x(_l, t)))
        self._add_plot_obj(rect)
        return rect

    def highlight_y_range(self, y_lo, y_hi, creation=0, z=-1, **styling_kwargs):
        """Shade a horizontal strip between y_lo and y_hi math coordinates.
        Returns a Rectangle object."""
        style_kw = {'fill': '#FFFF00', 'fill_opacity': 0.15, 'stroke_width': 0} | styling_kwargs
        rect = Rectangle(width=0, height=0, x=0, y=0,
                          creation=creation, z=z, **style_kw)
        _lo, _hi = y_lo, y_hi
        rect.x.set_onward(creation, lambda t: self.plot_x)
        rect.width.set_onward(creation, lambda t: self.plot_width)
        rect.y.set_onward(creation, lambda t, _l=_lo, _h=_hi: min(
            self._math_to_svg_y(_l, t), self._math_to_svg_y(_h, t)))
        rect.height.set_onward(creation, lambda t, _l=_lo, _h=_hi: abs(
            self._math_to_svg_y(_h, t) - self._math_to_svg_y(_l, t)))
        self._add_plot_obj(rect)
        return rect

    def add_shaded_inequality(self, func, direction='below', x_range=None,
                               samples=100, creation=0, z=-1, **styling_kwargs):
        """Shade the region above or below a curve (inequality visualization).
        direction: 'below' (y < f(x)) or 'above' (y > f(x)).
        Returns a dynamic Path object."""
        style_kw = {'fill': '#FFFF00', 'fill_opacity': 0.1, 'stroke_width': 0} | styling_kwargs
        fn = self._resolve_func(func, 'func')
        region = Path('', x=0, y=0, creation=creation, z=z, **style_kw)
        _xr, _dir = x_range, direction
        def _region_d(time, _fn=fn, _xr=_xr, _dir=_dir, _n=samples):
            xmin, xmax = self.x_min.at_time(time), self.x_max.at_time(time)
            x0 = _xr[0] if _xr else xmin
            x1 = _xr[1] if _xr else xmax
            step = (x1 - x0) / max(_n, 1)
            pts = []
            for i in range(_n + 1):
                xv = x0 + i * step
                sx, sy = self.coords_to_point(xv, _fn(xv), time)
                pts.append((sx, sy))
            if not pts:
                return ''
            # Build path: curve points, then boundary edge
            if _dir == 'below':
                # Curve left-to-right, then bottom-right to bottom-left
                bottom_y = self.plot_y + self.plot_height
                parts = [f'M{pts[0][0]:.1f},{pts[0][1]:.1f}']
                for sx, sy in pts[1:]:
                    parts.append(f'L{sx:.1f},{sy:.1f}')
                parts.append(f'L{pts[-1][0]:.1f},{bottom_y:.1f}')
                parts.append(f'L{pts[0][0]:.1f},{bottom_y:.1f}')
            else:
                # Curve left-to-right, then top-right to top-left
                top_y = self.plot_y
                parts = [f'M{pts[0][0]:.1f},{pts[0][1]:.1f}']
                for sx, sy in pts[1:]:
                    parts.append(f'L{sx:.1f},{sy:.1f}')
                parts.append(f'L{pts[-1][0]:.1f},{top_y:.1f}')
                parts.append(f'L{pts[0][0]:.1f},{top_y:.1f}')
            parts.append('Z')
            return ''.join(parts)
        region.d.set_onward(creation, _region_d)
        self._add_plot_obj(region)
        return region

    def add_area_label(self, func, x_range=None, text=None, font_size=20,
                        creation=0, z=3, samples=100, **styling_kwargs):
        """Add a text label positioned at the centroid of the area under func.
        If text is None, computes and displays the numerical area value.
        Returns the Text label object."""
        style_kw = {'fill': '#ddd', 'stroke_width': 0} | styling_kwargs
        fn = self._resolve_func(func, 'func')
        xlo = x_range[0] if x_range else self.x_min.at_time(creation)
        xhi = x_range[1] if x_range else self.x_max.at_time(creation)
        # Compute area and centroid
        step = (xhi - xlo) / max(samples, 1)
        total_area = 0
        cx_sum = 0
        cy_sum = 0
        for i in range(samples):
            x = xlo + (i + 0.5) * step
            y = fn(x)
            total_area += y * step
            cx_sum += x * abs(y) * step
            cy_sum += (y / 2) * abs(y) * step
        abs_area = sum(abs(fn(xlo + (i + 0.5) * step)) * step for i in range(samples))
        if abs_area < 1e-9:
            cx_math = (xlo + xhi) / 2
            cy_math = 0
        else:
            cx_math = cx_sum / abs_area
            cy_math = cy_sum / abs_area
        label_text = text if text is not None else f'A = {total_area:.2f}'
        sx, sy = self.coords_to_point(cx_math, cy_math, creation)
        lbl = Text(text=label_text, x=sx, y=sy, font_size=font_size,
                    text_anchor='middle', creation=creation, z=z, **style_kw)
        _cx, _cy = cx_math, cy_math
        lbl.x.set_onward(creation,
            lambda t, _cx=_cx, _cy=_cy: self.coords_to_point(_cx, _cy, t)[0])
        lbl.y.set_onward(creation,
            lambda t, _cx=_cx, _cy=_cy: self.coords_to_point(_cx, _cy, t)[1])
        self._add_plot_obj(lbl)
        return lbl

    def add_moving_tangent(self, func, x_start, x_end, start: float = 0, end: float = 1,
                            length=200, creation=0, z=2, easing=easings.smooth,
                            **styling_kwargs):
        """Draw a tangent line that slides along func from x_start to x_end.
        Returns a Line object with dynamic endpoints."""
        style_kw = {'stroke': '#FFFF00', 'stroke_width': 2} | styling_kwargs
        fn = self._resolve_func(func, 'func')
        line = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z, **style_kw)
        _xs, _xe, _s, _d = x_start, x_end, start, max(end - start, 1e-9)
        _hl = length / 2
        _h = 1e-6  # numerical derivative step
        def _tangent_pts(t, _xs=_xs, _xe=_xe, _s=_s, _d=_d, _hl=_hl, _h=_h,
                          _fn=fn, _easing=easing):
            p = _easing((t - _s) / _d) if t >= _s else 0
            xv = _xs + (_xe - _xs) * p
            yv = _fn(xv)
            # Numerical derivative
            slope = (_fn(xv + _h) - _fn(xv - _h)) / (2 * _h)
            # Direction vector along tangent
            dx = 1 / math.sqrt(1 + slope * slope) * _hl
            dy = slope * dx
            return xv, yv, dx, dy
        _tc = [None, None]  # per-frame cache
        def _cached(t):
            if _tc[0] == t:
                return _tc[1]
            _tc[1] = _tangent_pts(t)
            _tc[0] = t
            return _tc[1]
        line.p1.set_onward(creation,
            lambda t: (lambda xv, yv, dx, dy: self.coords_to_point(xv - dx, yv - dy, t))(*_cached(t)))
        line.p2.set_onward(creation,
            lambda t: (lambda xv, yv, dx, dy: self.coords_to_point(xv + dx, yv + dy, t))(*_cached(t)))
        self._add_plot_obj(line)
        return line

    def get_dashed_line(self, x1, y1, x2, y2, creation=0, z=0, **styling_kwargs):
        """Draw a dashed line between two math coordinate points.
        Returns a Line object."""
        style_kw = {'stroke': '#aaa', 'stroke_width': 2, 'stroke_dasharray': '6 4'} | styling_kwargs
        line = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z, **style_kw)
        _x1, _y1, _x2, _y2 = x1, y1, x2, y2
        line.p1.set_onward(creation, lambda t, _a=_x1, _b=_y1: self.coords_to_point(_a, _b, t))
        line.p2.set_onward(creation, lambda t, _a=_x2, _b=_y2: self.coords_to_point(_a, _b, t))
        self._add_plot_obj(line)
        return line

    def add_title(self, text, font_size=32, buff=20, creation=0, z=5, **styling_kwargs):
        """Add a title above the axes. Returns the Text object."""
        style_kw = {'fill': '#ddd', 'stroke_width': 0} | styling_kwargs
        cx = self.plot_x + self.plot_width / 2
        ty = self.plot_y - buff
        lbl = Text(text=text, x=cx, y=ty, font_size=font_size,
                    text_anchor='middle', creation=creation, z=z, **style_kw)
        self._add_plot_obj(lbl)
        return lbl

    def add_text_annotation(self, x, y, text, font_size=18, creation=0, z=3,
                             text_anchor='middle', **styling_kwargs):
        """Add a text label at math coordinates (x, y). Returns the Text object."""
        style_kw = {'fill': '#ddd', 'stroke_width': 0} | styling_kwargs
        sx, sy = self.coords_to_point(x, y, creation)
        lbl = Text(text=str(text), x=sx, y=sy, font_size=font_size,
                    text_anchor=text_anchor, creation=creation, z=z, **style_kw)
        _x, _y = x, y
        lbl.x.set_onward(creation,
            lambda t, _x=_x, _y=_y: self.coords_to_point(_x, _y, t)[0])
        lbl.y.set_onward(creation,
            lambda t, _x=_x, _y=_y: self.coords_to_point(_x, _y, t)[1])
        self._add_plot_obj(lbl)
        return lbl

    def add_horizontal_label(self, y, text, side='right', buff=10, font_size=18,
                              creation=0, z=5, **styling_kwargs):
        """Add a text label at y-coordinate on the specified side of the plot.
        side: 'left' or 'right'. Returns the Text object."""
        style_kw = {'fill': '#ddd', 'stroke_width': 0} | styling_kwargs
        if side == 'left':
            lx = self.plot_x - buff
            anchor = 'end'
        else:
            lx = self.plot_x + self.plot_width + buff
            anchor = 'start'
        lbl = Text(text=str(text), x=lx, y=0, font_size=font_size,
                    text_anchor=anchor, creation=creation, z=z, **style_kw)
        _yv = y
        lbl.y.set_onward(creation, lambda t, _y=_yv: self._math_to_svg_y(_y, t))
        self._add_plot_obj(lbl)
        return lbl

    def add_vertical_label(self, x, text, side='bottom', buff=10, font_size=18,
                            creation=0, z=5, **styling_kwargs):
        """Add a text label at x-coordinate above or below the plot.
        side: 'top' or 'bottom'. Returns the Text object."""
        style_kw = {'fill': '#ddd', 'stroke_width': 0} | styling_kwargs
        if side == 'top':
            ly = self.plot_y - buff
        else:
            ly = self.plot_y + self.plot_height + buff + font_size
        lbl = Text(text=str(text), x=0, y=ly, font_size=font_size,
                    text_anchor='middle', creation=creation, z=z, **style_kw)
        _xv = x
        lbl.x.set_onward(creation, lambda t, _x=_xv: self._math_to_svg_x(_x, t))
        self._add_plot_obj(lbl)
        return lbl

    def get_horizontal_line(self, x, y_val, creation=0, z=0, **styling_kwargs):
        """Draw a horizontal line at math y-coordinate from the y-axis to x."""
        style_kw = {'stroke': '#FFFF00', 'stroke_width': 2, 'stroke_dasharray': '5 5'} | styling_kwargs
        line = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z, **style_kw)
        def _p1(t):
            sy = self._math_to_svg_y(y_val, t)
            sx = self.plot_x
            return (sx, sy)
        def _p2(t):
            sy = self._math_to_svg_y(y_val, t)
            sx = self._math_to_svg_x(x, t)
            return (sx, sy)
        line.p1.set_onward(creation, _p1)
        line.p2.set_onward(creation, _p2)
        self._add_plot_obj(line)
        return line

    def add_asymptote(self, value, direction='vertical', creation=0, z=0, **styling_kwargs):
        """Draw a dashed asymptote line spanning the full plot range.
        direction: 'vertical' (x=value) or 'horizontal' (y=value).
        Returns a Line object."""
        style_kw = {'stroke': '#aaa', 'stroke_width': 1.5,
                    'stroke_dasharray': '8 4'} | styling_kwargs
        line = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z, **style_kw)
        _v = value
        if direction == 'vertical':
            def _p1(t, _v=_v):
                return (self._math_to_svg_x(_v, t), self.plot_y)
            def _p2(t, _v=_v):
                return (self._math_to_svg_x(_v, t), self.plot_y + self.plot_height)
        else:
            def _p1(t, _v=_v):
                return (self.plot_x, self._math_to_svg_y(_v, t))
            def _p2(t, _v=_v):
                return (self.plot_x + self.plot_width, self._math_to_svg_y(_v, t))
        line.p1.set_onward(creation, _p1)
        line.p2.set_onward(creation, _p2)
        self._add_plot_obj(line)
        return line

    def add_min_max_labels(self, func, x_range=None, samples=200, creation=0, z=3,
                            dot_radius=5, font_size=18, **styling_kwargs):
        """Find and label local min/max of func within x_range.
        Returns a VCollection of (dot, label) pairs."""
        from vectormation._shapes import Dot as _Dot, Text as _Text
        xlo = x_range[0] if x_range else self.x_min.at_time(creation)
        xhi = x_range[1] if x_range else self.x_max.at_time(creation)
        step = (xhi - xlo) / samples
        # Sample function values
        xs = [xlo + i * step for i in range(samples + 1)]
        ys = [func(x) for x in xs]
        extrema = []
        for i in range(1, len(ys) - 1):
            if ys[i] > ys[i - 1] and ys[i] > ys[i + 1]:
                extrema.append((xs[i], ys[i], 'max'))
            elif ys[i] < ys[i - 1] and ys[i] < ys[i + 1]:
                extrema.append((xs[i], ys[i], 'min'))
        objs = []
        colors = {'max': '#FF6B6B', 'min': '#58C4DD'}
        for mx, my, kind in extrema:
            color = styling_kwargs.get('fill', colors[kind])
            sx, sy = self.coords_to_point(mx, my, creation)
            dot = _Dot(cx=sx, cy=sy, r=dot_radius, fill=color,
                       creation=creation, z=z + 1)
            dot.c.set_onward(creation,
                lambda t, _mx=mx, _my=my: self.coords_to_point(_mx, _my, t))
            lbl_text = f'{kind}({mx:.1f}, {my:.1f})'
            offset_y = -15 if kind == 'max' else 20
            lbl = _Text(text=lbl_text, x=sx, y=sy + offset_y,
                        font_size=font_size, fill=color, stroke_width=0,
                        text_anchor='middle', creation=creation, z=z + 2)
            _mx, _my, _oy = mx, my, offset_y
            lbl.x.set_onward(creation,
                lambda t, _mx=_mx, _my=_my: self.coords_to_point(_mx, _my, t)[0])
            lbl.y.set_onward(creation,
                lambda t, _mx=_mx, _my=_my, _oy=_oy: self.coords_to_point(_mx, _my, t)[1] + _oy)
            self._add_plot_obj(dot)
            self._add_plot_obj(lbl)
            objs.extend([dot, lbl])
        return VCollection(*objs, creation=creation, z=z)

    def add_error_bars(self, x_data, y_data, y_err, creation=0, z=1,
                        cap_width=6, **styling_kwargs):
        """Add error bars at data points. y_err can be a single value or a list.
        Returns a VCollection of the error bar lines."""
        style_kw = {'stroke': '#aaa', 'stroke_width': 1.5} | styling_kwargs
        if isinstance(y_err, (int, float)):
            y_err = [y_err] * len(x_data)
        lines = []
        for xv, yv, err in zip(x_data, y_data, y_err):
            # Vertical bar
            bar = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z, **style_kw)
            bar.p1.set_onward(creation,
                lambda t, _x=xv, _y=yv, _e=err: self.coords_to_point(_x, _y - _e, t))
            bar.p2.set_onward(creation,
                lambda t, _x=xv, _y=yv, _e=err: self.coords_to_point(_x, _y + _e, t))
            self._add_plot_obj(bar)
            lines.append(bar)
            # Top cap
            top = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z, **style_kw)
            top.p1.set_onward(creation,
                lambda t, _x=xv, _y=yv, _e=err, _cw=cap_width: (
                    (_p := self.coords_to_point(_x, _y + _e, t))[0] - _cw, _p[1]))
            top.p2.set_onward(creation,
                lambda t, _x=xv, _y=yv, _e=err, _cw=cap_width: (
                    (_p := self.coords_to_point(_x, _y + _e, t))[0] + _cw, _p[1]))
            self._add_plot_obj(top)
            lines.append(top)
            # Bottom cap
            bot = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z, **style_kw)
            bot.p1.set_onward(creation,
                lambda t, _x=xv, _y=yv, _e=err, _cw=cap_width: (
                    (_p := self.coords_to_point(_x, _y - _e, t))[0] - _cw, _p[1]))
            bot.p2.set_onward(creation,
                lambda t, _x=xv, _y=yv, _e=err, _cw=cap_width: (
                    (_p := self.coords_to_point(_x, _y - _e, t))[0] + _cw, _p[1]))
            self._add_plot_obj(bot)
            lines.append(bot)
        return VCollection(*lines, creation=creation, z=z)

    def add_regression_line(self, x_data, y_data, creation=0, z=1, extend=0.5,
                             **styling_kwargs):
        """Add a least-squares regression line through data points.
        extend: how far to extend beyond data range (in math units).
        Returns the Line object."""
        style_kw = {'stroke': '#FFFF00', 'stroke_width': 2} | styling_kwargs
        n = len(x_data)
        if n < 2:
            return None
        sx = sum(x_data)
        sy = sum(y_data)
        sxy = sum(x * y for x, y in zip(x_data, y_data))
        sxx = sum(x * x for x in x_data)
        denom = n * sxx - sx * sx
        if abs(denom) < 1e-12:
            return None
        slope = (n * sxy - sx * sy) / denom
        intercept = (sy - slope * sx) / n
        xlo = min(x_data) - extend
        xhi = max(x_data) + extend
        _m, _b, _xlo, _xhi = slope, intercept, xlo, xhi
        line = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z, **style_kw)
        line.p1.set_onward(creation,
            lambda t, _m=_m, _b=_b, _xlo=_xlo: self.coords_to_point(_xlo, _m * _xlo + _b, t))
        line.p2.set_onward(creation,
            lambda t, _m=_m, _b=_b, _xhi=_xhi: self.coords_to_point(_xhi, _m * _xhi + _b, t))
        self._add_plot_obj(line)
        return line

    def add_confidence_band(self, func_lo, func_hi, x_range=None, samples=100,
                             creation=0, z=-1, **styling_kwargs):
        """Shade a band between two functions (e.g. confidence interval).
        func_lo/func_hi: callables (or curves with ._func).
        Returns a dynamic Path object."""
        style_kw = {'fill': '#58C4DD', 'fill_opacity': 0.2, 'stroke_width': 0} | styling_kwargs
        lo_fn = self._resolve_func(func_lo, 'func_lo')
        hi_fn = self._resolve_func(func_hi, 'func_hi')
        band = Path('', x=0, y=0, creation=creation, z=z, **style_kw)
        _xr = x_range
        def _band_d(time, _lo=lo_fn, _hi=hi_fn, _xr=_xr, _n=samples):
            xmin, xmax = self.x_min.at_time(time), self.x_max.at_time(time)
            x0 = _xr[0] if _xr else xmin
            x1 = _xr[1] if _xr else xmax
            step = (x1 - x0) / max(_n, 1)
            pts_hi, pts_lo = [], []
            for i in range(_n + 1):
                xv = x0 + i * step
                sx, sy_hi = self.coords_to_point(xv, _hi(xv), time)
                _, sy_lo = self.coords_to_point(xv, _lo(xv), time)
                pts_hi.append((sx, sy_hi))
                pts_lo.append((sx, sy_lo))
            if not pts_hi:
                return ''
            parts = [f'M{pts_hi[0][0]:.1f},{pts_hi[0][1]:.1f}']
            for sx, sy in pts_hi[1:]:
                parts.append(f'L{sx:.1f},{sy:.1f}')
            for sx, sy in reversed(pts_lo):
                parts.append(f'L{sx:.1f},{sy:.1f}')
            parts.append('Z')
            return ''.join(parts)
        band.d.set_onward(creation, _band_d)
        self._add_plot_obj(band)
        return band

    def add_boxplot(self, data_groups, x_positions=None, width=0.6,
                     creation=0, z=1, **styling_kwargs):
        """Draw box-and-whisker plots for one or more data groups.
        data_groups: list of lists of numbers.
        x_positions: x-coordinates for each box (defaults to 1, 2, ...).
        Returns a VCollection of all box elements."""
        style_kw = {'stroke': '#58C4DD', 'stroke_width': 2} | styling_kwargs
        fill_kw = style_kw.get('fill', '#58C4DD')
        line_kw = {k: v for k, v in style_kw.items() if k != 'fill'}
        if x_positions is None:
            x_positions = list(range(1, len(data_groups) + 1))
        def _percentile(sd, p):
            """Linear interpolation percentile (matches numpy default)."""
            k = (len(sd) - 1) * p
            f = int(k)
            c = f + 1 if f + 1 < len(sd) else f
            return sd[f] + (k - f) * (sd[c] - sd[f])
        objs = []
        hw = width / 2
        for xp, data in zip(x_positions, data_groups):
            if len(data) < 5:
                continue
            sd = sorted(data)
            q1 = _percentile(sd, 0.25)
            q2 = _percentile(sd, 0.5)
            q3 = _percentile(sd, 0.75)
            whisker_lo = sd[0]
            whisker_hi = sd[-1]
            # Box (rectangle from q1 to q3)
            box = Rectangle(width=0, height=0, x=0, y=0,
                             fill=fill_kw, fill_opacity=0.15,
                             creation=creation, z=z, **line_kw)
            box.x.set_onward(creation, lambda t, _xp=xp, _hw=hw: self._math_to_svg_x(_xp - _hw, t))
            box.width.set_onward(creation, lambda t, _xp=xp, _hw=hw: abs(
                self._math_to_svg_x(_xp + _hw, t) - self._math_to_svg_x(_xp - _hw, t)))
            box.y.set_onward(creation, lambda t, _q3=q3: self._math_to_svg_y(_q3, t))
            box.height.set_onward(creation, lambda t, _q1=q1, _q3=q3: abs(
                self._math_to_svg_y(_q1, t) - self._math_to_svg_y(_q3, t)))
            objs.append(box)
            # Median line
            med = Line(x1=0, y1=0, x2=0, y2=0, stroke=style_kw.get('stroke', '#58C4DD'),
                        stroke_width=style_kw.get('stroke_width', 2) + 1, creation=creation, z=z + 1)
            med.p1.set_onward(creation,
                lambda t, _xp=xp, _hw=hw, _q2=q2: (self._math_to_svg_x(_xp - _hw, t),
                                                      self._math_to_svg_y(_q2, t)))
            med.p2.set_onward(creation,
                lambda t, _xp=xp, _hw=hw, _q2=q2: (self._math_to_svg_x(_xp + _hw, t),
                                                      self._math_to_svg_y(_q2, t)))
            objs.append(med)
            # Whiskers (vertical lines from whisker_lo to q1 and q3 to whisker_hi)
            lo_whisk = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z,
                             **line_kw)
            lo_whisk.p1.set_onward(creation,
                lambda t, _xp=xp, _wlo=whisker_lo: (self._math_to_svg_x(_xp, t), self._math_to_svg_y(_wlo, t)))
            lo_whisk.p2.set_onward(creation,
                lambda t, _xp=xp, _q1=q1: (self._math_to_svg_x(_xp, t), self._math_to_svg_y(_q1, t)))
            objs.append(lo_whisk)
            hi_whisk = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z,
                             **line_kw)
            hi_whisk.p1.set_onward(creation,
                lambda t, _xp=xp, _q3=q3: (self._math_to_svg_x(_xp, t), self._math_to_svg_y(_q3, t)))
            hi_whisk.p2.set_onward(creation,
                lambda t, _xp=xp, _whi=whisker_hi: (self._math_to_svg_x(_xp, t), self._math_to_svg_y(_whi, t)))
            objs.append(hi_whisk)
            # Whisker caps
            cap_w = hw * 0.5
            for wval in (whisker_lo, whisker_hi):
                cap = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z,
                            **line_kw)
                cap.p1.set_onward(creation,
                    lambda t, _xp=xp, _cw=cap_w, _wv=wval: (
                        self._math_to_svg_x(_xp - _cw, t), self._math_to_svg_y(_wv, t)))
                cap.p2.set_onward(creation,
                    lambda t, _xp=xp, _cw=cap_w, _wv=wval: (
                        self._math_to_svg_x(_xp + _cw, t), self._math_to_svg_y(_wv, t)))
                objs.append(cap)
        for obj in objs:
            self._add_plot_obj(obj)
        return VCollection(*objs, creation=creation, z=z)

    def plot_heatmap(self, data, x_range=None, y_range=None, colormap=None,
                     creation=0, z=-1, **styling_kwargs):
        """Plot a heatmap grid on the axes.
        data: 2D list (rows × cols) of numeric values.
        x_range/y_range: optional (lo, hi) for axis mapping; defaults to (0, cols)/(0, rows).
        colormap: list of (value_fraction, '#hex') stops, default blue-red.
        Returns a VCollection of Rectangle cells."""
        if not data or not data[0]:
            return VCollection(creation=creation, z=z)
        nrows = len(data)
        ncols = len(data[0])
        xlo = x_range[0] if x_range else 0
        xhi = x_range[1] if x_range else ncols
        ylo = y_range[0] if y_range else 0
        yhi = y_range[1] if y_range else nrows
        flat = [v for row in data for v in row]
        vmin, vmax = min(flat), max(flat)
        if vmax == vmin:
            vmax = vmin + 1
        if colormap is None:
            colormap = [(0, '#0000FF'), (0.5, '#FFFF00'), (1, '#FF0000')]
        cell_w = (xhi - xlo) / ncols
        cell_h = (yhi - ylo) / nrows
        rects = []
        for ri in range(nrows):
            for ci in range(ncols):
                val = data[ri][ci]
                frac = (val - vmin) / (vmax - vmin)
                color = self._lerp_colormap(frac, colormap)
                x_math = xlo + ci * cell_w
                y_math = yhi - ri * cell_h  # top row = highest y
                _xl, _xr = x_math, x_math + cell_w
                _yt, _yb = y_math, y_math - cell_h
                rect = Rectangle(width=0, height=0, x=0, y=0,
                                  fill=color, fill_opacity=0.85, stroke=color,
                                  stroke_width=0.5, creation=creation, z=z)
                rect.x.set_onward(creation, lambda t, _xl=_xl: self._math_to_svg_x(_xl, t))
                rect.width.set_onward(creation, lambda t, _xl=_xl, _xr=_xr: abs(
                    self._math_to_svg_x(_xr, t) - self._math_to_svg_x(_xl, t)))
                rect.y.set_onward(creation, lambda t, _yt=_yt, _yb=_yb: min(
                    self._math_to_svg_y(_yt, t), self._math_to_svg_y(_yb, t)))
                rect.height.set_onward(creation, lambda t, _yt=_yt, _yb=_yb: abs(
                    self._math_to_svg_y(_yt, t) - self._math_to_svg_y(_yb, t)))
                rects.append(rect)
        group = VCollection(*rects, creation=creation, z=z)
        self._add_plot_obj(group)
        return group

    def add_crosshair(self, func, x_start, x_end, start: float = 0, end: float = 1,
                       creation=0, z=3, easing=easings.smooth, **styling_kwargs):
        """Add animated crosshair lines (horizontal + vertical) that follow func.
        Returns a VCollection with (h_line, v_line, dot)."""
        style_kw = {'stroke': '#FFFF00', 'stroke_width': 1,
                    'stroke_dasharray': '4 3'} | styling_kwargs
        dot_color = style_kw.get('fill', '#FFFF00')
        fn = self._resolve_func(func, 'func')
        _xs, _xe, _s, _d = x_start, x_end, start, max(end - start, 1e-9)
        _easing = easing
        def _cur_point(t, _fn=fn, _xs=_xs, _xe=_xe, _s=_s, _d=_d, _easing=_easing):
            p = max(0, min(1, _easing((t - _s) / _d)))
            xv = _xs + (_xe - _xs) * p
            return xv, _fn(xv)
        _cache = [None, None, None]  # [time, (xv, yv), (sx, sy)]
        def _cached(t):
            if _cache[0] == t:
                return _cache[1], _cache[2]
            mp = _cur_point(t)
            sp = self.coords_to_point(mp[0], mp[1], t)
            _cache[0], _cache[1], _cache[2] = t, mp, sp
            return mp, sp
        # Vertical line from x-axis to curve point
        v_line = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z, **style_kw)
        v_line.p1.set_onward(creation,
            lambda t: (_cached(t)[1][0], self.plot_y + self.plot_height))
        v_line.p2.set_onward(creation, lambda t: _cached(t)[1])
        # Horizontal line from y-axis to curve point
        h_line = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z, **style_kw)
        h_line.p1.set_onward(creation,
            lambda t: (self.plot_x, _cached(t)[1][1]))
        h_line.p2.set_onward(creation, lambda t: _cached(t)[1])
        # Dot at intersection
        dot = Dot(cx=0, cy=0, r=5, fill=dot_color, stroke_width=0,
                  creation=creation, z=z + 1)
        dot.c.set_onward(creation, lambda t: _cached(t)[1])
        for obj in (v_line, h_line, dot):
            obj._show_from(start)
            self._add_plot_obj(obj)
        return VCollection(v_line, h_line, dot, creation=creation, z=z)

    def add_violin_plot(self, data_groups, x_positions=None, width=0.8,
                         samples=50, creation=0, z=1, **styling_kwargs):
        """Draw violin plots for one or more data groups.
        data_groups: list of lists of numbers.
        x_positions: x-coordinates for each violin (defaults to 1, 2, ...).
        width: max width of each violin in math units.
        Returns a VCollection of all violin elements."""
        style_kw = {'fill': '#58C4DD', 'fill_opacity': 0.3,
                    'stroke': '#58C4DD', 'stroke_width': 2} | styling_kwargs
        if x_positions is None:
            x_positions = list(range(1, len(data_groups) + 1))
        objs = []
        hw = width / 2
        for xp, data in zip(x_positions, data_groups):
            if len(data) < 2:
                continue
            sd = sorted(data)
            lo, hi = sd[0], sd[-1]
            span = hi - lo
            if span < 1e-9:
                continue
            n = len(sd)
            # Kernel density estimation (Silverman's rule bandwidth)
            mean = sum(sd) / n
            bw = 1.06 * (sum((v - mean) ** 2 for v in sd) / n) ** 0.5 * n ** (-0.2)
            bw = max(bw, span * 0.05)
            ys = [lo + i * span / max(samples, 1) for i in range(samples + 1)]
            densities = []
            for yv in ys:
                d = sum(math.exp(-0.5 * ((yv - v) / bw) ** 2) for v in sd) / (n * bw * 2.5066)
                densities.append(d)
            max_d = max(densities) if densities else 1
            if max_d < 1e-12:
                max_d = 1
            # Build violin shape as a Path: right side top-to-bottom, left side bottom-to-top
            violin = Path('', x=0, y=0, creation=creation, z=z, **style_kw)
            _xp, _hw, _ys, _dens, _maxd = xp, hw, ys, densities, max_d
            def _violin_d(time, _xp=_xp, _hw=_hw, _ys=_ys, _dens=_dens, _maxd=_maxd):
                right_pts = []
                left_pts = []
                for yv, d in zip(_ys, _dens):
                    w = (d / _maxd) * _hw
                    sx_r, sy = self.coords_to_point(_xp + w, yv, time)
                    sx_l, _ = self.coords_to_point(_xp - w, yv, time)
                    right_pts.append((sx_r, sy))
                    left_pts.append((sx_l, sy))
                if not right_pts:
                    return ''
                parts = [f'M{right_pts[0][0]:.1f},{right_pts[0][1]:.1f}']
                for sx, sy in right_pts[1:]:
                    parts.append(f'L{sx:.1f},{sy:.1f}')
                for sx, sy in reversed(left_pts):
                    parts.append(f'L{sx:.1f},{sy:.1f}')
                parts.append('Z')
                return ''.join(parts)
            violin.d.set_onward(creation, _violin_d)
            objs.append(violin)
            # Median line
            median = sd[n // 2] if n % 2 else (sd[n // 2 - 1] + sd[n // 2]) / 2
            med_line = Line(x1=0, y1=0, x2=0, y2=0,
                            stroke=style_kw.get('stroke', '#58C4DD'),
                            stroke_width=style_kw.get('stroke_width', 2) + 1,
                            creation=creation, z=z + 1)
            _med, _xp2, _hw2 = median, xp, hw * 0.6
            med_line.p1.set_onward(creation,
                lambda t, _xp=_xp2, _hw=_hw2, _m=_med: (
                    self._math_to_svg_x(_xp - _hw, t), self._math_to_svg_y(_m, t)))
            med_line.p2.set_onward(creation,
                lambda t, _xp=_xp2, _hw=_hw2, _m=_med: (
                    self._math_to_svg_x(_xp + _hw, t), self._math_to_svg_y(_m, t)))
            objs.append(med_line)
        for obj in objs:
            self._add_plot_obj(obj)
        return VCollection(*objs, creation=creation, z=z)

    def plot_bubble(self, x_data, y_data, sizes, max_radius=20, creation=0, z=1,
                     **styling_kwargs):
        """Plot a bubble chart: scatter plot where dot size encodes a third variable.
        x_data, y_data: coordinates.  sizes: list of numeric values controlling bubble radius.
        max_radius: maximum bubble radius in SVG px.
        Returns a VCollection of Dot objects."""
        style_kw = {'fill': '#58C4DD', 'fill_opacity': 0.6, 'stroke_width': 0} | styling_kwargs
        if not sizes:
            return VCollection(creation=creation, z=z)
        smin, smax = min(sizes), max(sizes)
        srange = smax - smin if smax != smin else 1
        dots = []
        for xv, yv, sv in zip(x_data, y_data, sizes):
            r = max(3, max_radius * ((sv - smin) / srange) ** 0.5)
            dot = Dot(cx=0, cy=0, r=r, creation=creation, z=z, **style_kw)
            _xv, _yv = xv, yv
            dot.c.set_onward(creation,
                lambda t, _x=_xv, _y=_yv: self.coords_to_point(_x, _y, t))
            self._add_plot_obj(dot)
            dots.append(dot)
        return VCollection(*dots, creation=creation, z=z)

    def add_color_bar(self, colormap=None, vmin=0, vmax=1, label='', n_stops=50,
                       width=20, height=None, side='right', buff=20,
                       font_size=14, creation=0, z=5, **styling_kwargs):
        """Add a vertical color bar legend (e.g. for heatmaps).
        colormap: list of (frac, '#hex') stops.
        Returns a VCollection with the gradient bar and labels."""
        if colormap is None:
            colormap = [(0, '#0000FF'), (0.5, '#FFFF00'), (1, '#FF0000')]
        bar_h = height if height else self.plot_height
        if side == 'left':
            bx = self.plot_x - buff - width
        else:
            bx = self.plot_x + self.plot_width + buff
        by = self.plot_y
        objs = []
        strip_h = bar_h / n_stops
        for i in range(n_stops):
            frac = 1 - i / max(n_stops - 1, 1)  # top = high, bottom = low
            color = self._lerp_colormap(frac, colormap)
            rect = Rectangle(width=width, height=strip_h + 0.5, x=bx,
                              y=by + i * strip_h, fill=color, stroke_width=0,
                              creation=creation, z=z)
            objs.append(rect)
        # Border
        border = Rectangle(width=width, height=bar_h, x=bx, y=by,
                            fill_opacity=0, stroke='#888', stroke_width=1,
                            creation=creation, z=z + 0.1)
        objs.append(border)
        # Tick labels
        n_ticks = 5
        for i in range(n_ticks):
            frac = i / (n_ticks - 1)
            val = vmin + (vmax - vmin) * frac
            ly = by + bar_h - frac * bar_h
            lx = bx + width + 5 if side == 'right' else bx - 5
            anchor = 'start' if side == 'right' else 'end'
            lbl = Text(text=f'{val:.1f}', x=lx, y=ly + font_size * 0.35,
                        font_size=font_size, fill='#ccc', stroke_width=0,
                        text_anchor=anchor, creation=creation, z=z + 0.1)
            objs.append(lbl)
        # Title label
        if label:
            tx = bx + width / 2
            ty = by - 10
            title = Text(text=label, x=tx, y=ty, font_size=font_size,
                          fill='#ccc', stroke_width=0, text_anchor='middle',
                          creation=creation, z=z + 0.1)
            objs.append(title)
        group = VCollection(*objs, creation=creation, z=z)
        self._add_plot_obj(group)
        return group

    def plot_stacked_area(self, data, labels=None, colors=None, x_values=None,
                           creation=0, z=-1, **styling_kwargs):
        """Plot a stacked area chart.
        data: list of lists (each inner list is one series, same length).
        x_values: optional x coords (defaults to 0, 1, 2, ...).
        Returns a VCollection of Path objects (one per series)."""
        if not data or not data[0]:
            return VCollection(creation=creation, z=z)
        n_series = len(data)
        n_points = len(data[0])
        if x_values is None:
            x_values = list(range(n_points))
        if colors is None:
            colors = ['#58C4DD', '#83C167', '#FF6B6B', '#FFFF00',
                      '#FF79C6', '#B8BB26', '#BD93F9', '#FFB86C']
        # Compute cumulative sums
        cumulative = [[0] * n_points]
        for series in data:
            prev = cumulative[-1]
            cumulative.append([prev[j] + series[j] for j in range(n_points)])
        areas = []
        for si in range(n_series):
            color = colors[si % len(colors)]
            style_kw = {'fill': color, 'fill_opacity': 0.6, 'stroke': color,
                        'stroke_width': 1} | styling_kwargs
            area = Path('', x=0, y=0, creation=creation, z=z + si * 0.01, **style_kw)
            _lower = cumulative[si]
            _upper = cumulative[si + 1]
            _xv = x_values
            def _area_d(time, _lo=_lower, _hi=_upper, _xs=_xv):
                pts_hi = [self.coords_to_point(_xs[j], _hi[j], time)
                          for j in range(len(_xs))]
                pts_lo = [self.coords_to_point(_xs[j], _lo[j], time)
                          for j in range(len(_xs))]
                if not pts_hi:
                    return ''
                parts = [f'M{pts_hi[0][0]:.1f},{pts_hi[0][1]:.1f}']
                for sx, sy in pts_hi[1:]:
                    parts.append(f'L{sx:.1f},{sy:.1f}')
                for sx, sy in reversed(pts_lo):
                    parts.append(f'L{sx:.1f},{sy:.1f}')
                parts.append('Z')
                return ''.join(parts)
            area.d.set_onward(creation, _area_d)
            self._add_plot_obj(area)
            areas.append(area)
        return VCollection(*areas, creation=creation, z=z)

    def plot_candlestick(self, data, bar_width=0.6, creation=0, z=1,
                          up_color='#83C167', down_color='#FF6B6B', **styling_kwargs):
        """Plot an OHLC candlestick chart.
        data: list of (x, open, high, low, close) tuples.
        Returns a VCollection of all candlestick elements."""
        objs = []
        hw = bar_width / 2
        for x, o, h, l, c in data:
            is_up = c >= o
            color = up_color if is_up else down_color
            body_lo, body_hi = (o, c) if is_up else (c, o)
            # Wick (high-low line)
            wick = Line(x1=0, y1=0, x2=0, y2=0,
                        stroke=color, stroke_width=1.5, creation=creation, z=z)
            _x, _h, _l = x, h, l
            wick.p1.set_onward(creation,
                lambda t, _x=_x, _h=_h: (self._math_to_svg_x(_x, t), self._math_to_svg_y(_h, t)))
            wick.p2.set_onward(creation,
                lambda t, _x=_x, _l=_l: (self._math_to_svg_x(_x, t), self._math_to_svg_y(_l, t)))
            objs.append(wick)
            # Body (open-close rectangle)
            rect = Rectangle(width=0, height=0, x=0, y=0,
                              fill=color, fill_opacity=0.8, stroke=color, stroke_width=1,
                              creation=creation, z=z + 0.1)
            _xl, _xr = x - hw, x + hw
            _blo, _bhi = body_lo, body_hi
            rect.x.set_onward(creation, lambda t, _xl=_xl: self._math_to_svg_x(_xl, t))
            rect.width.set_onward(creation, lambda t, _xl=_xl, _xr=_xr: abs(
                self._math_to_svg_x(_xr, t) - self._math_to_svg_x(_xl, t)))
            rect.y.set_onward(creation, lambda t, _bhi=_bhi: self._math_to_svg_y(_bhi, t))
            rect.height.set_onward(creation, lambda t, _blo=_blo, _bhi=_bhi: max(1, abs(
                self._math_to_svg_y(_blo, t) - self._math_to_svg_y(_bhi, t))))
            objs.append(rect)
        for obj in objs:
            self._add_plot_obj(obj)
        return VCollection(*objs, creation=creation, z=z)

    def plot_dumbbell(self, y_positions, start_values, end_values,
                       creation=0, z=1, **styling_kwargs):
        """Plot a dumbbell chart: pairs of dots connected by a line at each y position.
        y_positions: list of y-coordinates (categories).
        start_values, end_values: x-coordinate pairs.
        Returns a VCollection."""
        start_color = styling_kwargs.pop('start_color', '#FF6B6B')
        end_color = styling_kwargs.pop('end_color', '#58C4DD')
        line_kw = {'stroke': '#888', 'stroke_width': 2} | styling_kwargs
        objs = []
        for yp, sv, ev in zip(y_positions, start_values, end_values):
            # Connecting line
            line = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z, **line_kw)
            _yp, _sv, _ev = yp, sv, ev
            line.p1.set_onward(creation,
                lambda t, _y=_yp, _x=_sv: self.coords_to_point(_x, _y, t))
            line.p2.set_onward(creation,
                lambda t, _y=_yp, _x=_ev: self.coords_to_point(_x, _y, t))
            objs.append(line)
            # Start dot
            d1 = Dot(cx=0, cy=0, r=6, fill=start_color, stroke_width=0,
                     creation=creation, z=z + 1)
            d1.c.set_onward(creation,
                lambda t, _y=_yp, _x=_sv: self.coords_to_point(_x, _y, t))
            objs.append(d1)
            # End dot
            d2 = Dot(cx=0, cy=0, r=6, fill=end_color, stroke_width=0,
                     creation=creation, z=z + 1)
            d2.c.set_onward(creation,
                lambda t, _y=_yp, _x=_ev: self.coords_to_point(_x, _y, t))
            objs.append(d2)
        for obj in objs:
            self._add_plot_obj(obj)
        return VCollection(*objs, creation=creation, z=z)

    def add_parametric_area(self, func_x, func_y, t_range=(0, 1),
                             samples=200, creation=0, z=-1, **styling_kwargs):
        """Fill the area enclosed by a parametric curve (func_x(t), func_y(t)).
        Returns a dynamic Path object."""
        style_kw = {'fill': '#58C4DD', 'fill_opacity': 0.3, 'stroke_width': 0} | styling_kwargs
        area = Path('', x=0, y=0, creation=creation, z=z, **style_kw)
        _t0, _t1 = t_range
        _fx, _fy, _n = func_x, func_y, samples
        def _param_d(time, _fx=_fx, _fy=_fy, _t0=_t0, _t1=_t1, _n=_n):
            step = (_t1 - _t0) / max(_n, 1)
            pts = []
            for i in range(_n + 1):
                tv = _t0 + i * step
                sx, sy = self.coords_to_point(_fx(tv), _fy(tv), time)
                pts.append((sx, sy))
            if not pts:
                return ''
            parts = [f'M{pts[0][0]:.1f},{pts[0][1]:.1f}']
            for sx, sy in pts[1:]:
                parts.append(f'L{sx:.1f},{sy:.1f}')
            parts.append('Z')
            return ''.join(parts)
        area.d.set_onward(creation, _param_d)
        self._add_plot_obj(area)
        return area

    def add_threshold_line(self, y, label=None, direction='horizontal',
                            font_size=14, creation=0, z=2, **styling_kwargs):
        """Add a threshold/reference line with optional label.
        direction: 'horizontal' (y=value) or 'vertical' (x=value).
        Returns a VCollection with line and optional label."""
        style_kw = {'stroke': '#FF6B6B', 'stroke_width': 1.5,
                    'stroke_dasharray': '6 3'} | styling_kwargs
        line = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z, **style_kw)
        _v = y
        if direction == 'horizontal':
            line.p1.set_onward(creation,
                lambda t, _v=_v: (self.plot_x, self._math_to_svg_y(_v, t)))
            line.p2.set_onward(creation,
                lambda t, _v=_v: (self.plot_x + self.plot_width, self._math_to_svg_y(_v, t)))
        else:
            line.p1.set_onward(creation,
                lambda t, _v=_v: (self._math_to_svg_x(_v, t), self.plot_y))
            line.p2.set_onward(creation,
                lambda t, _v=_v: (self._math_to_svg_x(_v, t), self.plot_y + self.plot_height))
        self._add_plot_obj(line)
        objs = [line]
        if label is not None:
            lbl_color = style_kw.get('stroke', '#FF6B6B')
            if direction == 'horizontal':
                lbl = Text(text=str(label),
                           x=self.plot_x + self.plot_width + 5, y=0,
                           font_size=font_size, fill=lbl_color, stroke_width=0,
                           text_anchor='start', creation=creation, z=z + 0.1)
                lbl.y.set_onward(creation,
                    lambda t, _v=_v: self._math_to_svg_y(_v, t) + font_size * 0.35)
            else:
                lbl = Text(text=str(label),
                           x=0, y=self.plot_y - 5,
                           font_size=font_size, fill=lbl_color, stroke_width=0,
                           text_anchor='middle', creation=creation, z=z + 0.1)
                lbl.x.set_onward(creation,
                    lambda t, _v=_v: self._math_to_svg_x(_v, t))
            self._add_plot_obj(lbl)
            objs.append(lbl)
        return VCollection(*objs, creation=creation, z=z)

    def add_data_labels(self, x_data, y_data, fmt='{:.1f}', offset_y=-12,
                         font_size=14, creation=0, z=3, **styling_kwargs):
        """Add value labels above/below data points.
        Returns a VCollection of Text objects."""
        style_kw = {'fill': '#ddd', 'stroke_width': 0} | styling_kwargs
        objs = []
        for xv, yv in zip(x_data, y_data):
            lbl = Text(text=fmt.format(yv), x=0, y=0, font_size=font_size,
                        text_anchor='middle', creation=creation, z=z, **style_kw)
            lbl.x.set_onward(creation,
                lambda t, _x=xv, _y=yv: self.coords_to_point(_x, _y, t)[0])
            lbl.y.set_onward(creation,
                lambda t, _x=xv, _y=yv, _oy=offset_y: self.coords_to_point(_x, _y, t)[1] + _oy)
            self._add_plot_obj(lbl)
            objs.append(lbl)
        return VCollection(*objs, creation=creation, z=z)

    def plot_lollipop(self, y_positions, values, baseline=0, r=6,
                       creation=0, z=1, **styling_kwargs):
        """Plot a horizontal lollipop chart: horizontal lines from baseline to value with dot.
        y_positions: category y-coordinates.  values: x-values.
        Returns a VCollection."""
        line_kw = {'stroke': '#58C4DD', 'stroke_width': 2}
        dot_kw = {'fill': '#58C4DD', 'stroke_width': 0}
        for k, v in styling_kwargs.items():
            if k.startswith('dot_'):
                dot_kw[k[4:]] = v
            else:
                line_kw[k] = v
        objs = []
        for yp, xv in zip(y_positions, values):
            line = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z, **line_kw)
            line.p1.set_onward(creation,
                lambda t, _y=yp, _x=baseline: self.coords_to_point(_x, _y, t))
            line.p2.set_onward(creation,
                lambda t, _y=yp, _x=xv: self.coords_to_point(_x, _y, t))
            dot = Dot(cx=0, cy=0, r=r, creation=creation, z=z + 1, **dot_kw)
            dot.c.set_onward(creation,
                lambda t, _y=yp, _x=xv: self.coords_to_point(_x, _y, t))
            self._add_plot_obj(line)
            self._add_plot_obj(dot)
            objs += [line, dot]
        return VCollection(*objs, creation=creation, z=z)

    def add_moving_label(self, func, text, x_start, x_end, start=0, end=2,
                          font_size=16, offset_y=-15, creation=0, z=3, **styling_kwargs):
        """A text label that follows a curve point from x_start to x_end over [start, end].
        Returns a VCollection with the dot and the label."""
        style_kw = {'fill': '#ddd', 'stroke_width': 0} | styling_kwargs
        f = self._resolve_func(func)
        dot = Dot(cx=0, cy=0, r=4, fill='#fff', stroke_width=0,
                  creation=creation, z=z + 0.1)
        lbl = Text(text=str(text), x=0, y=0, font_size=font_size,
                    text_anchor='middle', creation=creation, z=z + 0.2, **style_kw)
        dur = max(end - start, 1e-9)
        _xs, _xe, _s = x_start, x_end, start
        _cache = [None, None]  # [time, (sx, sy)]
        def _pos(t):
            if _cache[0] == t:
                return _cache[1]
            frac = max(0, min(1, (t - _s) / dur))
            xv = _xs + (_xe - _xs) * frac
            pt = self.coords_to_point(xv, f(xv), t)
            _cache[0], _cache[1] = t, pt
            return pt
        dot.c.set_onward(creation, lambda t: _pos(t))
        lbl.x.set_onward(creation, lambda t: _pos(t)[0])
        lbl.y.set_onward(creation, lambda t, _oy=offset_y: _pos(t)[1] + _oy)
        dot._show_from(start)
        lbl._show_from(start)
        self._add_plot_obj(dot)
        self._add_plot_obj(lbl)
        return VCollection(dot, lbl, creation=creation, z=z)

    def add_vertical_span(self, x0, x1, creation=0, z=-1, **styling_kwargs):
        """Shade a vertical band between x0 and x1 (math coords).
        Returns a Rectangle with dynamic position."""
        style_kw = {'fill': '#FFFF00', 'fill_opacity': 0.15, 'stroke_width': 0} | styling_kwargs
        rect = Rectangle(width=0, height=0, x=0, y=0, creation=creation, z=z, **style_kw)
        rect.x.set_onward(creation, lambda t, _a=x0: self._math_to_svg_x(_a, t))
        rect.y.set_onward(creation, lambda t: self.plot_y)
        rect.width.set_onward(creation,
            lambda t, _a=x0, _b=x1: self._math_to_svg_x(_b, t) - self._math_to_svg_x(_a, t))
        rect.height.set_onward(creation, lambda t: self.plot_height)
        self._add_plot_obj(rect)
        return rect

    def add_horizontal_span(self, y0, y1, creation=0, z=-1, **styling_kwargs):
        """Shade a horizontal band between y0 and y1 (math coords).
        Returns a Rectangle with dynamic position."""
        style_kw = {'fill': '#FFFF00', 'fill_opacity': 0.15, 'stroke_width': 0} | styling_kwargs
        rect = Rectangle(width=0, height=0, x=0, y=0, creation=creation, z=z, **style_kw)
        rect.x.set_onward(creation, lambda t: self.plot_x)
        rect.y.set_onward(creation, lambda t, _a=y1: self._math_to_svg_y(_a, t))
        rect.width.set_onward(creation, lambda t: self.plot_width)
        rect.height.set_onward(creation,
            lambda t, _a=y0, _b=y1: self._math_to_svg_y(_a, t) - self._math_to_svg_y(_b, t))
        self._add_plot_obj(rect)
        return rect

    def plot_density(self, data, bandwidth=None, samples=200, creation=0, z=0, **styling_kwargs):
        """Plot a kernel density estimate (KDE) curve from raw data.
        Uses Gaussian kernel. Returns a Path object."""
        style_kw = {'stroke': '#FF79C6', 'stroke_width': 2, 'fill_opacity': 0} | styling_kwargs
        data = sorted(data)
        n = len(data)
        if n == 0:
            p = Path('', creation=creation, z=z, **style_kw)
            self._add_plot_obj(p)
            return p
        if bandwidth is None:
            std = (sum((x - sum(data) / n) ** 2 for x in data) / n) ** 0.5
            bandwidth = 1.06 * std * n ** (-0.2) if std > 0 else 1
        h = bandwidth
        xmin, xmax = min(data), max(data)
        margin = 3 * h
        xs = [xmin - margin + i * (xmax - xmin + 2 * margin) / (samples - 1) for i in range(samples)]
        def _kde(xv):
            return sum(math.exp(-0.5 * ((xv - d) / h) ** 2) for d in data) / (n * h * math.sqrt(2 * math.pi))
        ys = [_kde(xv) for xv in xs]
        curve_data = list(zip(xs, ys))
        curve = Path('', x=0, y=0, creation=creation, z=z, **style_kw)
        def _compute_d(time, _cd=curve_data):
            parts = []
            for i, (xv, yv) in enumerate(_cd):
                sx, sy = self.coords_to_point(xv, yv, time)
                parts.append(f'{"M" if i == 0 else "L"}{sx:.1f},{sy:.1f}')
            return ''.join(parts)
        curve.d.set_onward(creation, _compute_d)
        self._add_plot_obj(curve)
        return curve

    def add_annotation_box(self, x_coord, y_coord, text, box_width=120, box_height=40,
                            offset=(60, -60), font_size=14, creation=0, z=5, **styling_kwargs):
        """Add a text box with an arrow pointing to (x_coord, y_coord).
        offset: (dx, dy) from the point to the box center.
        Returns a VCollection with arrow, box, and label."""
        from vectormation._shapes import RoundedRectangle
        style_kw = {'fill': '#ddd', 'stroke_width': 0} | styling_kwargs
        ox, oy = offset
        # Point SVG coordinates
        _xc, _yc = x_coord, y_coord
        def _pt(t):
            return self.coords_to_point(_xc, _yc, t)
        # Arrow from point to box edge
        arr = Arrow(x1=0, y1=0, x2=0, y2=0, stroke='#aaa', stroke_width=1.5,
                    creation=creation, z=z)
        arr.shaft.p1.set_onward(creation, lambda t: _pt(t))
        arr.shaft.p2.set_onward(creation, lambda t, _ox=ox, _oy=oy: (_pt(t)[0] + _ox, _pt(t)[1] + _oy))
        # Box
        box = RoundedRectangle(width=box_width, height=box_height,
                                x=0, y=0, corner_radius=5,
                                fill='#1a1a2e', fill_opacity=0.9,
                                stroke='#aaa', stroke_width=1,
                                creation=creation, z=z + 0.1)
        box.x.set_onward(creation, lambda t, _ox=ox: _pt(t)[0] + _ox - box_width / 2)
        box.y.set_onward(creation, lambda t, _oy=oy: _pt(t)[1] + _oy - box_height / 2)
        # Label
        lbl = Text(text=str(text), x=0, y=0, font_size=font_size,
                    text_anchor='middle', creation=creation, z=z + 0.2, **style_kw)
        lbl.x.set_onward(creation, lambda t, _ox=ox: _pt(t)[0] + _ox)
        lbl.y.set_onward(creation, lambda t, _oy=oy: _pt(t)[1] + _oy + font_size * 0.35)
        self._add_plot_obj(arr)
        self._add_plot_obj(box)
        self._add_plot_obj(lbl)
        return VCollection(arr, box, lbl, creation=creation, z=z)

    def plot_population_pyramid(self, categories, left_values, right_values,
                                 bar_height=0.6, creation=0, z=0,
                                 left_color='#58C4DD', right_color='#FF79C6'):
        """Plot a back-to-back horizontal bar chart (population pyramid).
        categories: y-positions (e.g. [1,2,3,...]).
        left_values: values extending left (shown as negative).
        right_values: values extending right.
        Returns a VCollection."""
        objs = []
        for yp, lv, rv in zip(categories, left_values, right_values):
            # Shared lambdas for y position and height
            y_fn = lambda t, _y=yp, _h=bar_height: self.coords_to_point(0, _y + _h / 2, t)[1]
            h_fn = lambda t, _y=yp, _h=bar_height: abs(
                self.coords_to_point(0, _y - _h / 2, t)[1] - self.coords_to_point(0, _y + _h / 2, t)[1])
            for val, color, x_fn in [
                (lv, left_color,
                 lambda t, _v=lv: self.coords_to_point(-_v, 0, t)[0]),
                (rv, right_color,
                 lambda t: self.coords_to_point(0, 0, t)[0]),
            ]:
                bar = Rectangle(width=0, height=0, x=0, y=0,
                                 fill=color, fill_opacity=0.8, stroke_width=0,
                                 creation=creation, z=z)
                bar.x.set_onward(creation, x_fn)
                bar.y.set_onward(creation, y_fn)
                bar.width.set_onward(creation,
                    lambda t, _v=val: self.coords_to_point(_v, 0, t)[0] - self.coords_to_point(0, 0, t)[0])
                bar.height.set_onward(creation, h_fn)
                self._add_plot_obj(bar)
                objs.append(bar)
        return VCollection(*objs, creation=creation, z=z)

    def add_data_table(self, headers, rows, x_offset=0, y_offset=30,
                        font_size=12, cell_width=80, cell_height=22,
                        creation=0, z=5):
        """Add a simple data table below the axes.
        headers: list of column header strings.
        rows: list of lists (each row is a list of cell values).
        Returns a VCollection."""
        objs = []
        base_x = self.plot_x + x_offset
        base_y = self.plot_y + self.plot_height + y_offset
        # Header row
        for j, h in enumerate(headers):
            hx = base_x + j * cell_width + cell_width / 2
            hy = base_y + font_size * 0.8
            lbl = Text(text=str(h), x=hx, y=hy, font_size=font_size,
                        fill='#aaa', stroke_width=0, text_anchor='middle',
                        creation=creation, z=z)
            objs.append(lbl)
        # Separator line
        sep = Line(x1=base_x, y1=base_y + cell_height * 0.8,
                   x2=base_x + len(headers) * cell_width,
                   y2=base_y + cell_height * 0.8,
                   stroke='#555', stroke_width=0.5, creation=creation, z=z)
        objs.append(sep)
        # Data rows
        for i, row in enumerate(rows):
            ry = base_y + (i + 1) * cell_height + font_size * 0.8
            for j, val in enumerate(row):
                cx = base_x + j * cell_width + cell_width / 2
                lbl = Text(text=str(val), x=cx, y=ry, font_size=font_size,
                            fill='#ddd', stroke_width=0, text_anchor='middle',
                            creation=creation, z=z)
                objs.append(lbl)
        return VCollection(*objs, creation=creation, z=z)

    def plot_ribbon(self, x_values, y_lower, y_upper, creation=0, z=0, **styling_kwargs):
        """Plot a ribbon (band) between y_lower and y_upper data arrays.
        Returns a filled Path."""
        style_kw = {'fill': '#58C4DD', 'fill_opacity': 0.3,
                    'stroke': '#58C4DD', 'stroke_width': 1} | styling_kwargs
        data = list(zip(x_values, y_lower, y_upper))
        curve = Path('', x=0, y=0, creation=creation, z=z, **style_kw)
        def _compute_d(time, _data=data):
            if not _data:
                return ''
            upper = [f'{"M" if i == 0 else "L"}{self._math_to_svg_x(x, time):.1f},{self._math_to_svg_y(yu, time):.1f}'
                     for i, (x, _, yu) in enumerate(_data)]
            lower = [f'L{self._math_to_svg_x(x, time):.1f},{self._math_to_svg_y(yl, time):.1f}'
                     for x, yl, _ in reversed(_data)]
            return ''.join(upper) + ''.join(lower) + 'Z'
        curve.d.set_onward(creation, _compute_d)
        self._add_plot_obj(curve)
        return curve

    def plot_swarm(self, x_positions, data_groups, r=4, jitter_width=0.3,
                    creation=0, z=1, **styling_kwargs):
        """Plot a beeswarm (jittered dot plot).
        x_positions: list of x values for each group.
        data_groups: list of lists, each containing y-values.
        Returns a VCollection of Dots."""
        style_kw = {'fill': '#58C4DD', 'stroke_width': 0} | styling_kwargs
        import random as _rng
        rng = _rng.Random(42)
        objs = []
        for xp, values in zip(x_positions, data_groups):
            for yv in sorted(values):
                jitter = (rng.random() - 0.5) * 2 * jitter_width
                dot = Dot(cx=0, cy=0, r=r, creation=creation, z=z, **style_kw)
                dot.c.set_onward(creation,
                    lambda t, _x=xp, _y=yv, _jj=jitter: self.coords_to_point(_x + _jj, _y, t))
                self._add_plot_obj(dot)
                objs.append(dot)
        return VCollection(*objs, creation=creation, z=z)

    def add_axis_break(self, value, axis='y', size=15, creation=0, z=3):
        """Add a zigzag break indicator on an axis.
        value: position in math coords where the break appears.
        axis: 'x' or 'y'."""
        n_zigs = 4
        if axis == 'y':
            anchor = self.plot_x
            def _d(t, _v=value):
                sv = self._math_to_svg_y(_v, t)
                pts = [f'M{anchor - 5},{sv - size}']
                for i in range(n_zigs):
                    frac = (i + 0.5) / n_zigs
                    off = 8 if i % 2 == 0 else -8
                    pts.append(f'L{anchor + off},{sv - size + frac * 2 * size}')
                pts.append(f'L{anchor - 5},{sv + size}')
                return ''.join(pts)
        else:
            anchor = self.plot_y + self.plot_height
            def _d(t, _v=value):
                sv = self._math_to_svg_x(_v, t)
                pts = [f'M{sv - size},{anchor + 5}']
                for i in range(n_zigs):
                    frac = (i + 0.5) / n_zigs
                    off = -8 if i % 2 == 0 else 8
                    pts.append(f'L{sv - size + frac * 2 * size},{anchor + off}')
                pts.append(f'L{sv + size},{anchor + 5}')
                return ''.join(pts)
        brk = Path('', x=0, y=0, stroke='#fff', stroke_width=2,
                   fill_opacity=0, creation=creation, z=z)
        brk.d.set_onward(creation, _d)
        self._add_plot_obj(brk)
        return brk

    def plot_error_bar(self, x_values, y_values, y_errors, r=4,
                        creation=0, z=1, **styling_kwargs):
        """Scatter plot with vertical error bars.
        y_errors: list of (err_low, err_high) tuples, or list of symmetric errors."""
        style_kw = {'fill': '#58C4DD', 'stroke': '#58C4DD', 'stroke_width': 1.5} | styling_kwargs
        objs = []
        for i, (xv, yv) in enumerate(zip(x_values, y_values)):
            e = y_errors[i]
            el, eh = (e, e) if not isinstance(e, (list, tuple)) else (e[0], e[1])
            # Dot
            dot = Dot(cx=0, cy=0, r=r, creation=creation, z=z + 0.1,
                      fill=style_kw['fill'], stroke_width=0)
            dot.c.set_onward(creation,
                lambda t, _x=xv, _y=yv: self.coords_to_point(_x, _y, t))
            self._add_plot_obj(dot)
            objs.append(dot)
            # Error bar (vertical line from y-el to y+eh with caps)
            bar = Path('', x=0, y=0, stroke=style_kw['stroke'],
                       stroke_width=style_kw['stroke_width'],
                       fill_opacity=0, creation=creation, z=z)
            cap = 4
            def _bar_d(t, _x=xv, _y=yv, _el=el, _eh=eh):
                sx, sy_lo = self.coords_to_point(_x, _y - _el, t)
                sx2, sy_hi = self.coords_to_point(_x, _y + _eh, t)
                return (f'M{sx - cap},{sy_lo}L{sx + cap},{sy_lo}'
                        f'M{sx},{sy_lo}L{sx2},{sy_hi}'
                        f'M{sx2 - cap},{sy_hi}L{sx2 + cap},{sy_hi}')
            bar.d.set_onward(creation, _bar_d)
            self._add_plot_obj(bar)
            objs.append(bar)
        return VCollection(*objs, creation=creation, z=z)

    def plot_contour(self, func, levels=8, x_samples=40, y_samples=40,
                      creation=0, z=0, **styling_kwargs):
        """Plot contour (level) curves for z = func(x, y).
        levels: int (auto) or list of explicit z-values.
        Returns a VCollection of Path objects (one per level)."""
        style_kw = {'stroke_width': 1.5, 'fill_opacity': 0} | styling_kwargs
        x_lo = self.x_min.at_time(creation)
        x_hi = self.x_max.at_time(creation)
        y_lo = self.y_min.at_time(creation)
        y_hi = self.y_max.at_time(creation)
        dx = (x_hi - x_lo) / max(x_samples - 1, 1)
        dy = (y_hi - y_lo) / max(y_samples - 1, 1)
        # Evaluate grid
        grid = [[func(x_lo + c * dx, y_lo + r * dy) for c in range(x_samples)]
                for r in range(y_samples)]
        flat = [v for row in grid for v in row]
        zmin, zmax = min(flat), max(flat)
        if isinstance(levels, int):
            n = levels
            levels = [zmin + (i + 1) * (zmax - zmin) / (n + 1) for i in range(n)]
        # Use _lerp_colormap if available, else generate colors
        colors = ['#313695', '#4575b4', '#74add1', '#abd9e9',
                  '#fee090', '#fdae61', '#f46d43', '#d73027']
        objs = []
        for li, lv in enumerate(levels):
            ci = min(int(li / max(len(levels) - 1, 1) * (len(colors) - 1) + 0.5), len(colors) - 1)
            color = style_kw.get('stroke', colors[ci])
            # Marching squares: find segments for this level
            segments = []
            for r in range(y_samples - 1):
                for c in range(x_samples - 1):
                    v = [grid[r][c], grid[r][c + 1], grid[r + 1][c + 1], grid[r + 1][c]]
                    case = sum(1 << i for i, val in enumerate(v) if val >= lv)
                    if case == 0 or case == 15:
                        continue
                    # Corner positions in math coords
                    cx0, cy0 = x_lo + c * dx, y_lo + r * dy
                    cx1, cy1 = cx0 + dx, cy0 + dy
                    def _interp(va, vb, pa, pb):
                        t = (lv - va) / (vb - va) if abs(vb - va) > 1e-12 else 0.5
                        return pa + t * (pb - pa)
                    edges = {
                        'top': (_interp(v[0], v[1], cx0, cx1), cy0),
                        'right': (cx1, _interp(v[1], v[2], cy0, cy1)),
                        'bottom': (_interp(v[3], v[2], cx0, cx1), cy1),
                        'left': (cx0, _interp(v[0], v[3], cy0, cy1)),
                    }
                    for e1, e2 in _MARCH_SEGS.get(case, []):
                        segments.append((edges[e1], edges[e2]))
            if not segments:
                continue
            contour = Path('', x=0, y=0, stroke=color, creation=creation, z=z, **style_kw)
            def _cd(t, _segs=segments):
                parts = []
                for (ax, ay), (bx, by) in _segs:
                    sa, sb = self.coords_to_point(ax, ay, t), self.coords_to_point(bx, by, t)
                    parts.append(f'M{sa[0]:.1f},{sa[1]:.1f}L{sb[0]:.1f},{sb[1]:.1f}')
                return ''.join(parts)
            contour.d.set_onward(creation, _cd)
            self._add_plot_obj(contour)
            objs.append(contour)
        return VCollection(*objs, creation=creation, z=z)

    def plot_quiver(self, func, x_step=1, y_step=1, scale=0.3,
                     tip_length=8, tip_width=6,
                     creation=0, z=0, **styling_kwargs):
        """2D vector/arrow field: func(x, y) -> (dx, dy).
        Returns a VCollection of small Arrow objects."""
        style_kw = {'stroke': '#58C4DD', 'stroke_width': 1.5} | styling_kwargs
        x_lo = self.x_min.at_time(creation)
        x_hi = self.x_max.at_time(creation)
        y_lo = self.y_min.at_time(creation)
        y_hi = self.y_max.at_time(creation)
        objs = []
        x = x_lo
        while x <= x_hi + 1e-9:
            y = y_lo
            while y <= y_hi + 1e-9:
                dx, dy = func(x, y)
                if abs(dx) < 1e-12 and abs(dy) < 1e-12:
                    y += y_step
                    continue
                arr = Arrow(x1=0, y1=0, x2=1, y2=0,
                            tip_length=tip_length, tip_width=tip_width,
                            creation=creation, z=z, **style_kw)
                arr.shaft.p1.set_onward(creation,
                    lambda t, _x=x, _y=y: self.coords_to_point(_x, _y, t))
                arr.shaft.p2.set_onward(creation,
                    lambda t, _x=x, _y=y, _dx=dx, _dy=dy, _s=scale:
                        self.coords_to_point(_x + _dx * _s, _y + _dy * _s, t))
                self._add_plot_obj(arr)
                objs.append(arr)
                y += y_step
            x += x_step
        return VCollection(*objs, creation=creation, z=z)

    def plot_area(self, func, x_range=None, baseline=0, num_points=100,
                   creation=0, z=0, **styling_kwargs):
        """Filled area chart between func(x) and a baseline value.
        Returns a dynamic Path."""
        style_kw = {'fill': '#58C4DD', 'fill_opacity': 0.3,
                    'stroke': '#58C4DD', 'stroke_width': 1.5} | styling_kwargs
        func = self._resolve_func(func)
        x_lo = x_range[0] if x_range else self.x_min.at_time(creation)
        x_hi = x_range[1] if x_range else self.x_max.at_time(creation)
        xs = [x_lo + i * (x_hi - x_lo) / max(num_points - 1, 1) for i in range(num_points)]
        data = [(x, func(x)) for x in xs]
        area = Path('', x=0, y=0, creation=creation, z=z, **style_kw)
        def _d(time, _data=data, _bl=baseline):
            if not _data:
                return ''
            pts = [f'{"M" if i == 0 else "L"}{self.coords_to_point(x, y, time)[0]:.1f},'
                   f'{self.coords_to_point(x, y, time)[1]:.1f}'
                   for i, (x, y) in enumerate(_data)]
            # Close to baseline
            last_x = _data[-1][0]
            first_x = _data[0][0]
            sx_last, sy_bl = self.coords_to_point(last_x, _bl, time)
            sx_first, _ = self.coords_to_point(first_x, _bl, time)
            pts.append(f'L{sx_last:.1f},{sy_bl:.1f}')
            pts.append(f'L{sx_first:.1f},{sy_bl:.1f}Z')
            return ''.join(pts)
        area.d.set_onward(creation, _d)
        self._add_plot_obj(area)
        return area

    def plot_dot_plot(self, values, stack_spacing=0.3, r=4,
                       creation=0, z=0, **styling_kwargs):
        """Dot plot: stack of dots at each value along the x-axis.
        values: list of x-values (can have duplicates).
        Returns a VCollection of Dots."""
        style_kw = {'fill': '#58C4DD', 'stroke_width': 0} | styling_kwargs
        from collections import Counter
        counts = Counter(values)
        objs = []
        for xv, cnt in sorted(counts.items()):
            for i in range(cnt):
                dot = Dot(cx=0, cy=0, r=r, creation=creation, z=z, **style_kw)
                yv = stack_spacing * (i + 0.5)
                dot.c.set_onward(creation,
                    lambda t, _x=xv, _y=yv: self.coords_to_point(_x, _y, t))
                self._add_plot_obj(dot)
                objs.append(dot)
        return VCollection(*objs, creation=creation, z=z)

    def add_reference_band(self, lo, hi, axis='y', creation=0, z=-1, **styling_kwargs):
        """Shaded horizontal or vertical reference band.
        axis='y': band between y=lo and y=hi. axis='x': between x=lo and x=hi.
        Returns a Rectangle."""
        style_kw = {'fill': '#58C4DD', 'fill_opacity': 0.1,
                    'stroke_width': 0} | styling_kwargs
        rect = Rectangle(width=0, height=0, x=0, y=0, creation=creation, z=z, **style_kw)
        px, py = self.plot_x, self.plot_y
        pw, ph = self.plot_width, self.plot_height
        if axis == 'y':
            rect.x.set_onward(creation, lambda t: px)
            rect.width.set_onward(creation, lambda t: pw)
            rect.y.set_onward(creation, lambda t, _hi=hi: self._math_to_svg_y(_hi, t))
            rect.height.set_onward(creation, lambda t, _lo=lo, _hi=hi:
                abs(self._math_to_svg_y(_lo, t) - self._math_to_svg_y(_hi, t)))
        else:
            rect.y.set_onward(creation, lambda t: py)
            rect.height.set_onward(creation, lambda t: ph)
            rect.x.set_onward(creation, lambda t, _lo=lo: self._math_to_svg_x(_lo, t))
            rect.width.set_onward(creation, lambda t, _lo=lo, _hi=hi:
                abs(self._math_to_svg_x(_hi, t) - self._math_to_svg_x(_lo, t)))
        self._add_plot_obj(rect)
        return rect

    def add_slope_field(self, func, x_step=1, y_step=1, seg_length=0.4,
                         creation=0, z=-1, **styling_kwargs):
        """Draw a direction/slope field for dy/dx = func(x, y).
        func: callable(x, y) -> slope (dy/dx).
        x_step, y_step: spacing between sample points in math units.
        seg_length: half-length of each line segment in math units.
        Returns a VCollection of the line segments."""
        style_kw = {'stroke': '#888', 'stroke_width': 1.5} | styling_kwargs
        x_step, y_step = max(abs(x_step), 1e-6), max(abs(y_step), 1e-6)
        xlo, xhi = self.x_min.at_time(creation), self.x_max.at_time(creation)
        ylo, yhi = self.y_min.at_time(creation), self.y_max.at_time(creation)
        lines = []
        x = xlo
        while x <= xhi:
            y = ylo
            while y <= yhi:
                try:
                    slope = func(x, y)
                except (ZeroDivisionError, ValueError):
                    y += y_step
                    continue
                # Compute direction from slope
                angle = math.atan(slope) if abs(slope) < 1e9 else math.copysign(math.pi / 2, slope)
                dx = seg_length * math.cos(angle)
                dy = seg_length * math.sin(angle)
                line = Line(x1=0, y1=0, x2=0, y2=0,
                            creation=creation, z=z, **style_kw)
                line.p1.set_onward(creation,
                    lambda t, _x=x, _y=y, _dx=dx, _dy=dy:
                        self.coords_to_point(_x - _dx, _y - _dy, t))
                line.p2.set_onward(creation,
                    lambda t, _x=x, _y=y, _dx=dx, _dy=dy:
                        self.coords_to_point(_x + _dx, _y + _dy, t))
                self._add_plot_obj(line)
                lines.append(line)
                y += y_step
            x += x_step
        group = VCollection(*lines, creation=creation, z=z)
        return group

    def add_vector(self, x, y, origin_x=0, origin_y=0, creation=0, z=2,
                    tip_length=20, tip_width=14, **styling_kwargs):
        """Draw a vector arrow from (origin_x, origin_y) to (x, y) in math coordinates.
        Returns the Arrow object."""
        style_kw = {'stroke': '#FFFF00', 'fill': '#FFFF00', 'stroke_width': 3} | styling_kwargs
        sx1, sy1 = self.coords_to_point(origin_x, origin_y, creation)
        sx2, sy2 = self.coords_to_point(x, y, creation)
        arrow = Arrow(x1=sx1, y1=sy1, x2=sx2, y2=sy2,
                      tip_length=tip_length, tip_width=tip_width,
                      creation=creation, z=z, **style_kw)
        # Dynamic endpoints
        arrow.shaft.p1.set_onward(creation,
            lambda t, _ox=origin_x, _oy=origin_y: self.coords_to_point(_ox, _oy, t))
        arrow.shaft.p2.set_onward(creation,
            lambda t, _tx=x, _ty=y: self.coords_to_point(_tx, _ty, t))
        # Dynamic arrowhead
        def _tip_base(t, _ox=origin_x, _oy=origin_y, _tx=x, _ty=y):
            p1 = self.coords_to_point(_ox, _oy, t)
            p2 = self.coords_to_point(_tx, _ty, t)
            return p1, p2
        _tl, _tw2 = tip_length, tip_width / 2
        _tip_cache = [None, None]  # [time, result]
        def _tip_geom(t):
            if _tip_cache[0] == t:
                return _tip_cache[1]
            p1, p2 = _tip_base(t)
            ddx, ddy = p2[0] - p1[0], p2[1] - p1[1]
            ln = math.hypot(ddx, ddy) or 1
            ux, uy = ddx / ln, ddy / ln
            px, py = -uy, ux
            bx, by = p2[0] - ux * _tl, p2[1] - uy * _tl
            result = (p2[0], p2[1]), (bx + px * _tw2, by + py * _tw2), (bx - px * _tw2, by - py * _tw2)
            _tip_cache[0], _tip_cache[1] = t, result
            return result
        arrow.tip.vertices[0].set_onward(creation, lambda t: _tip_geom(t)[0])
        arrow.tip.vertices[1].set_onward(creation, lambda t: _tip_geom(t)[1])
        arrow.tip.vertices[2].set_onward(creation, lambda t: _tip_geom(t)[2])
        self._add_plot_obj(arrow)
        return arrow

    def get_vertical_lines(self, func, x_values, creation=0, z=0, **styling_kwargs):
        """Draw vertical lines from x-axis to func(x) at each x in x_values.
        Returns a VCollection of the lines."""
        style_kw = {'stroke': '#aaa', 'stroke_width': 1,
                    'stroke_dasharray': '4 3'} | styling_kwargs
        lines = []
        for xv in x_values:
            yv = func(xv)
            line = self.get_vertical_line(xv, y_val=yv, creation=creation, z=z, **style_kw)
            lines.append(line)
        return VCollection(*lines, creation=creation, z=z)

    def add_interval(self, x_lo, x_hi, y=None, creation=0, z=2, bracket_height=10,
                      **styling_kwargs):
        """Draw an interval bracket [x_lo, x_hi] on the x-axis (or at y).
        Returns a VCollection with the bracket shape and optional label."""
        style_kw = {'stroke': '#FFFF00', 'stroke_width': 2} | styling_kwargs
        _y = y if y is not None else self.y_min.at_time(creation)
        # Three segments: left cap, horizontal bar, right cap
        left_cap = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z, **style_kw)
        bar = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z, **style_kw)
        right_cap = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z, **style_kw)
        _xlo, _xhi, _yv, _bh = x_lo, x_hi, _y, bracket_height
        def _lo_pt(t, _xlo=_xlo, _yv=_yv):
            return self.coords_to_point(_xlo, _yv, t)
        def _hi_pt(t, _xhi=_xhi, _yv=_yv):
            return self.coords_to_point(_xhi, _yv, t)
        left_cap.p1.set_onward(creation,
            lambda t, _bh=_bh: (_lo_pt(t)[0], _lo_pt(t)[1] - _bh))
        left_cap.p2.set_onward(creation,
            lambda t, _bh=_bh: (_lo_pt(t)[0], _lo_pt(t)[1] + _bh))
        bar.p1.set_onward(creation, _lo_pt)
        bar.p2.set_onward(creation, _hi_pt)
        right_cap.p1.set_onward(creation,
            lambda t, _bh=_bh: (_hi_pt(t)[0], _hi_pt(t)[1] - _bh))
        right_cap.p2.set_onward(creation,
            lambda t, _bh=_bh: (_hi_pt(t)[0], _hi_pt(t)[1] + _bh))
        for ln in (left_cap, bar, right_cap):
            self._add_plot_obj(ln)
        return VCollection(left_cap, bar, right_cap, creation=creation, z=z)

    def coords_label(self, x, y, text=None, creation=0, z=0, **styling_kwargs):
        """Add a labeled point with dashed guide lines to both axes.
        Returns a VCollection with (dot, h_line, v_line, label)."""
        style_kw = {'stroke': '#FFFF00', 'fill': '#FFFF00'} | styling_kwargs
        # Shared base point (cached per-frame to avoid 5 coords_to_point calls)
        _pt_cache = [None, None]
        def _pt(t, _xv=x, _yv=y):
            if _pt_cache[0] == t:
                return _pt_cache[1]
            _pt_cache[0] = t
            _pt_cache[1] = self.coords_to_point(_xv, _yv, t)
            return _pt_cache[1]
        # Dot at the point
        dot = Dot(cx=0, cy=0, r=5, creation=creation, z=z + 1,
                  fill=style_kw.get('fill', '#FFFF00'), stroke_width=0)
        dot.c.set_onward(creation, _pt)
        # Dashed line to x-axis
        v_line = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z,
                      stroke=style_kw.get('stroke', '#FFFF00'),
                      stroke_width=1, stroke_dasharray='4 3')
        v_line.p1.set_onward(creation, _pt)
        v_line.p2.set_onward(creation, lambda t: (_pt(t)[0], self.plot_y + self.plot_height))
        # Dashed line to y-axis
        h_line = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z,
                      stroke=style_kw.get('stroke', '#FFFF00'),
                      stroke_width=1, stroke_dasharray='4 3')
        h_line.p1.set_onward(creation, _pt)
        h_line.p2.set_onward(creation, lambda t: (self.plot_x, _pt(t)[1]))
        # Label
        label_text = text if text is not None else f'({x}, {y})'
        lbl = Text(text=label_text, x=0, y=0, font_size=16,
                   text_anchor='start', creation=creation, z=z + 1,
                   fill=style_kw.get('fill', '#FFFF00'), stroke_width=0)
        lbl.x.set_onward(creation, lambda t: _pt(t)[0] + 10)
        lbl.y.set_onward(creation, lambda t: _pt(t)[1] - 10)
        group = VCollection(dot, h_line, v_line, lbl, creation=creation, z=z)
        self._add_plot_obj(group)
        return group

    def plot_vector_field(self, func, x_step=1, y_step=1, max_length=80,
                           creation=0, z=0, **styling_kwargs):
        """Draw a vector field F(x,y) = (u,v) on the axes using arrows.
        func: callable(x, y) -> (u, v).
        Returns a VCollection of Arrow objects."""
        style_kw = {'stroke': '#83C167', 'stroke_width': 1.5, 'fill': '#83C167'} | styling_kwargs
        xmin, xmax = self.x_min.at_time(creation), self.x_max.at_time(creation)
        ymin, ymax = self.y_min.at_time(creation), self.y_max.at_time(creation)
        arrows = []
        x = xmin
        while x <= xmax + 1e-9:
            y = ymin
            while y <= ymax + 1e-9:
                try:
                    u, v = func(x, y)
                except (ZeroDivisionError, ValueError):
                    y += y_step
                    continue
                mag = math.hypot(u, v)
                if mag < 1e-9:
                    y += y_step
                    continue
                # Scale to max_length pixels, capped
                scale = min(max_length, mag * 30) / mag
                sx1, sy1 = self.coords_to_point(x, y, creation)
                sx2 = sx1 + u * scale
                sy2 = sy1 - v * scale  # SVG y is inverted
                arrows.append(Arrow(x1=sx1, y1=sy1, x2=sx2, y2=sy2,
                                     tip_length=8, tip_width=6,
                                     creation=creation, z=z, **style_kw))
                y += y_step
            x += x_step
        group = VCollection(*arrows, creation=creation, z=z)
        self._add_plot_obj(group)
        return group

    def get_tangent_line(self, func, x_val, length=200, creation=0, z=0, **styling_kwargs):
        """Draw a tangent line to func at x=x_val.
        Uses numerical derivative. Returns a Line object."""
        style_kw = {'stroke': '#FFFF00', 'stroke_width': 2} | styling_kwargs
        h = 1e-6
        slope = (func(x_val + h) - func(x_val - h)) / (2 * h)
        cx_svg = self._math_to_svg_x(x_val, creation)
        cy_svg = self._math_to_svg_y(func(x_val), creation)
        # Tangent direction in SVG: dx_svg per unit x = plot_width / (xmax - xmin)
        # dy_svg per unit y = -plot_height / (ymax - ymin)
        xspan = self.x_max.at_time(creation) - self.x_min.at_time(creation)
        yspan = self.y_max.at_time(creation) - self.y_min.at_time(creation)
        if xspan == 0 or yspan == 0:
            return Line(x1=cx_svg, y1=cy_svg, x2=cx_svg + length, y2=cy_svg,
                        creation=creation, z=z, **style_kw)
        dx_px = self.plot_width / xspan
        dy_px = -self.plot_height / yspan
        dir_x = dx_px
        dir_y = slope * dy_px
        mag = math.hypot(dir_x, dir_y)
        if mag == 0:
            mag = 1
        half = length / 2
        nx, ny = dir_x / mag * half, dir_y / mag * half
        line = Line(x1=cx_svg - nx, y1=cy_svg - ny, x2=cx_svg + nx, y2=cy_svg + ny,
                    creation=creation, z=z, **style_kw)
        self._add_plot_obj(line)
        return line

    def get_secant_line(self, func, x1, x2, length=300, creation=0, z=0, **styling_kwargs):
        """Draw a secant line through func at x1 and x2. Returns a Line."""
        style_kw = {'stroke': '#83C167', 'stroke_width': 2} | styling_kwargs
        line = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z, **style_kw)
        _x1, _x2, _len = x1, x2, length
        def _secant_p1(t, _x1=_x1, _x2=_x2, _len=_len):
            sx1, sy1 = self.coords_to_point(_x1, func(_x1), t)
            sx2, sy2 = self.coords_to_point(_x2, func(_x2), t)
            dx, dy = sx2 - sx1, sy2 - sy1
            mag = max(math.hypot(dx, dy), 1e-9)
            half = _len / 2
            mx, my = (sx1 + sx2) / 2, (sy1 + sy2) / 2
            return (mx - dx / mag * half, my - dy / mag * half)
        def _secant_p2(t, _x1=_x1, _x2=_x2, _len=_len):
            sx1, sy1 = self.coords_to_point(_x1, func(_x1), t)
            sx2, sy2 = self.coords_to_point(_x2, func(_x2), t)
            dx, dy = sx2 - sx1, sy2 - sy1
            mag = max(math.hypot(dx, dy), 1e-9)
            half = _len / 2
            mx, my = (sx1 + sx2) / 2, (sy1 + sy2) / 2
            return (mx + dx / mag * half, my + dy / mag * half)
        line.p1.set_onward(creation, _secant_p1)
        line.p2.set_onward(creation, _secant_p2)
        self._add_plot_obj(line)
        return line

    def add_secant_fade(self, func, x, dx_start=2, dx_end=0.01,
                         start: float = 0, end: float = 1, length=300,
                         creation=0, z=0, easing=easings.smooth, **styling_kwargs):
        """Animate a secant line approaching a tangent line at x.
        dx shrinks from dx_start to dx_end over [start, end].
        Returns a Line object with animated endpoints."""
        style_kw = {'stroke': '#83C167', 'stroke_width': 2} | styling_kwargs
        line = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z, **style_kw)
        _x, _dxs, _dxe = x, dx_start, dx_end
        _s, _d, _len = start, max(end - start, 1e-9), length
        def _p1(t, _x=_x, _dxs=_dxs, _dxe=_dxe, _s=_s, _d=_d, _len=_len, _easing=easing):
            progress = _easing((t - _s) / _d)
            dx = _dxs + (_dxe - _dxs) * progress
            x1, x2 = _x, _x + dx
            sx1, sy1 = self.coords_to_point(x1, func(x1), t)
            sx2, sy2 = self.coords_to_point(x2, func(x2), t)
            ddx, dy = sx2 - sx1, sy2 - sy1
            mag = max(math.hypot(ddx, dy), 1e-9)
            half = _len / 2
            mx, my = (sx1 + sx2) / 2, (sy1 + sy2) / 2
            return (mx - ddx / mag * half, my - dy / mag * half)
        def _p2(t, _x=_x, _dxs=_dxs, _dxe=_dxe, _s=_s, _d=_d, _len=_len, _easing=easing):
            progress = _easing((t - _s) / _d)
            dx = _dxs + (_dxe - _dxs) * progress
            x1, x2 = _x, _x + dx
            sx1, sy1 = self.coords_to_point(x1, func(x1), t)
            sx2, sy2 = self.coords_to_point(x2, func(x2), t)
            ddx, dy = sx2 - sx1, sy2 - sy1
            mag = max(math.hypot(ddx, dy), 1e-9)
            half = _len / 2
            mx, my = (sx1 + sx2) / 2, (sy1 + sy2) / 2
            return (mx + ddx / mag * half, my + dy / mag * half)
        line.p1.set(start, end, _p1, stay=True)
        line.p2.set(start, end, _p2, stay=True)
        self._add_plot_obj(line)
        return line

    def get_slope_field(self, func, x_step=1, y_step=1, length=0.6, creation=0, z=0, **styling_kwargs):
        """Draw a slope field for dy/dx = func(x, y).
        func: callable(x, y) -> slope.
        length: arrow length in math units.
        Returns a VCollection of Line segments."""
        style_kw = {'stroke': '#58C4DD', 'stroke_width': 1.5, 'stroke_opacity': 0.7} | styling_kwargs
        xmin, xmax = self.x_min.at_time(creation), self.x_max.at_time(creation)
        ymin, ymax = self.y_min.at_time(creation), self.y_max.at_time(creation)
        lines = []
        x = xmin
        while x <= xmax + 1e-9:
            y = ymin
            while y <= ymax + 1e-9:
                try:
                    slope = func(x, y)
                except (ZeroDivisionError, ValueError):
                    y += y_step
                    continue
                angle = math.atan(slope)
                dx = length / 2 * math.cos(angle)
                dy = length / 2 * math.sin(angle)
                sx1, sy1 = self.coords_to_point(x - dx, y - dy, creation)
                sx2, sy2 = self.coords_to_point(x + dx, y + dy, creation)
                lines.append(Line(x1=sx1, y1=sy1, x2=sx2, y2=sy2,
                                  creation=creation, z=z, **style_kw))
                y += y_step
            x += x_step
        group = VCollection(*lines, creation=creation, z=z)
        self._add_plot_obj(group)
        return group

    def get_riemann_rectangles(self, func, x_range, dx=0.1, creation=0, z=0, **styling_kwargs):
        """Create rectangles approximating the area under func.

        Returns a DynamicObject that rebuilds each frame."""
        style_kw = {'fill': '#58C4DD', 'fill_opacity': 0.5, 'stroke': '#fff', 'stroke_width': 1} | styling_kwargs
        def _build(time):
            x_lo, x_hi = x_range
            by = self._baseline_y(time)
            rects = []
            xv = x_lo
            while xv < x_hi - 1e-9:
                x_next = min(xv + dx, x_hi)
                sx1 = self._math_to_svg_x(xv, time)
                sx2 = self._math_to_svg_x(x_next, time)
                sy = self._math_to_svg_y(func(xv), time)
                rects.append(Rectangle(width=sx2 - sx1, height=abs(by - sy),
                                       x=sx1, y=min(sy, by),
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
    length = math.hypot(dx, dy) or 1
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


    def get_start(self, time=0):
        """Return the start point (x1, y1) of the arrow shaft."""
        return self.shaft.p1.at_time(time)

    def get_end(self, time=0):
        """Return the end point (x2, y2) of the arrow shaft."""
        return self.shaft.p2.at_time(time)


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


class LinearGradient:
    """SVG linear gradient definition. Register with canvas.add_def().
    Apply to objects: obj.set_style(fill='url(#gradient_id)').

    stops: list of (offset, color) or (offset, color, opacity) tuples.
           offset is 0-1 (0=start, 1=end).
    """
    def __init__(self, stops, x1='0%', y1='0%', x2='100%', y2='0%'):
        self.id = f'lg{id(self)}'
        self.stops = stops
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2

    def to_svg_def(self, time=0):
        parts = [f"<linearGradient id='{self.id}' x1='{self.x1}' y1='{self.y1}' "
                 f"x2='{self.x2}' y2='{self.y2}'>"]
        for stop in self.stops:
            off, color = stop[0], stop[1]
            opacity = stop[2] if len(stop) > 2 else 1
            parts.append(f"<stop offset='{off}' stop-color='{color}' stop-opacity='{opacity}'/>")
        parts.append("</linearGradient>")
        return ''.join(parts)

    def fill_ref(self):
        return f'url(#{self.id})'


class RadialGradient:
    """SVG radial gradient definition. Register with canvas.add_def().
    Apply to objects: obj.set_style(fill='url(#gradient_id)').

    stops: list of (offset, color) or (offset, color, opacity) tuples.
    """
    def __init__(self, stops, cx='50%', cy='50%', r='50%'):
        self.id = f'rg{id(self)}'
        self.stops = stops
        self.cx, self.cy, self.r = cx, cy, r

    def to_svg_def(self, time=0):
        parts = [f"<radialGradient id='{self.id}' cx='{self.cx}' cy='{self.cy}' r='{self.r}'>"]
        for stop in self.stops:
            off, color = stop[0], stop[1]
            opacity = stop[2] if len(stop) > 2 else 1
            parts.append(f"<stop offset='{off}' stop-color='{color}' stop-opacity='{opacity}'/>")
        parts.append("</radialGradient>")
        return ''.join(parts)

    def fill_ref(self):
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
                d = max(e - s, 1e-9)
                c.add_onward(s, lambda t, _s=s, _d=d: (dx * easing((t-_s)/_d), dy * easing((t-_s)/_d)), last_change=e)
        return self


class RightAngle(VCollection):
    """Right angle indicator (small square) at a vertex between two perpendicular lines."""
    def __init__(self, vertex, p1, p2, size=18, creation=0, z=0, **styling_kwargs):
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
        span = self.x_end - self.x_start
        if span == 0:
            return (self.origin_x, self.origin_y)
        t = (value - self.x_start) / span
        return (self.origin_x + t * self.length, self.origin_y)

    def add_pointer(self, value, label=None, color='#FF6B6B', creation=0, z=1):
        """Add a triangular pointer above the number line at *value*.
        Returns an Arrow pointing down at the position."""
        px, py = self.number_to_point(value)
        arrow = Arrow(x1=px, y1=py - 50, x2=px, y2=py - 8,
                      creation=creation, z=z, stroke=color, fill=color)
        self.objects.append(arrow)
        if label is not None:
            from vectormation._shapes import Text as _Text
            lbl = _Text(text=str(label), x=px, y=py - 58,
                        font_size=20, fill=color, stroke_width=0,
                        text_anchor='middle', creation=creation, z=z)
            self.objects.append(lbl)
        return arrow

    def move_pointer(self, arrow, value, start=0, end=1, easing=None):
        """Animate a pointer arrow to a new value on the number line."""
        if easing is None:
            import vectormation.easings as _easings
            easing = _easings.smooth
        px, py = self.number_to_point(value)
        # Arrow is a VCollection with a line and tip; shift all to new x
        cur_x = arrow.bbox(start)[0] + arrow.bbox(start)[2] / 2
        dx = px - cur_x
        arrow.shift(dx=dx, start_time=start, end_time=end, easing=easing)
        return self


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
        sector.shift(dx=dx, dy=dy, start_time=start, end_time=start + dur / 2, easing=easing)
        return self


class DonutChart(VCollection):
    """Donut (ring) chart — PieChart with a hollow center.

    values: list of numeric values (proportional sizes).
    labels: optional list of labels.
    inner_radius: radius of the hole (0 < inner_radius < r).
    """
    def __init__(self, values, labels=None, colors=None, cx=960, cy=540,
                 r=240, inner_radius=120, start_angle=90,
                 center_text=None, font_size=17, creation=0, z=0):
        if colors is None:
            colors = ['#58C4DD', '#83C167', '#FC6255', '#FFFF00', '#9A72AC',
                      '#F0AC5F', '#C55F73', '#5CD0B3']
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
        if center_text is not None:
            ct = Text(text=str(center_text), x=cx, y=cy + font_size * 0.35,
                      font_size=int(font_size * 1.5), text_anchor='middle',
                      fill='#fff', stroke_width=0, creation=creation, z=z + 0.1)
            objects.append(ct)
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
        if n == 0:
            super().__init__(creation=creation, z=z)
            self.values, self.bar_count, self._bars = [], 0, []
            self._height, self._y = height, y
            return
        max_val = max(abs(v) for v in values) if values else 1
        bar_width = width / n
        inner_width = bar_width * (1 - bar_spacing)
        objects: list[VObject] = []
        bars: list = []

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

        # Baseline
        baseline = Line(x1=x, y1=y + height, x2=x + width, y2=y + height,
                        creation=creation, z=z, stroke='#fff', stroke_width=3)
        objects.append(baseline)
        super().__init__(*objects, creation=creation, z=z)
        self.values = values
        self.bar_count = n
        self._bars = bars
        self._height = height
        self._y = y

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
            s, d = start, dur
            bar.height.set(start, end, lambda t, _oh=old_h, _nh=new_h, _s=s, _d=d: _oh + (_nh - _oh) * easing((t - _s) / _d), stay=True)
            bar.y.set(start, end, lambda t, _oy=old_y, _ny=new_y, _s=s, _d=d: _oy + (_ny - _oy) * easing((t - _s) / _d), stay=True)
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

    def highlight_row(self, row, start=0, end=1, color='#FFFF00', easing=easings.there_and_back):
        """Flash-highlight all cells in a row."""
        for entry in self.entries[row]:
            entry.flash(start, end, color=color, easing=easing)
        return self

    def highlight_column(self, col, start=0, end=1, color='#FFFF00', easing=easings.there_and_back):
        """Flash-highlight all cells in a column."""
        for row in self.entries:
            if col < len(row):
                row[col].flash(start, end, color=color, easing=easing)
        return self


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

    def get_row(self, row):
        """Return a VCollection of all Text objects in the given row."""
        return VCollection(*self.entries[row])

    def get_column(self, col):
        """Return a VCollection of all Text objects in the given column."""
        return VCollection(*(row[col] for row in self.entries if col < len(row)))


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


class Variable(VCollection):
    """Display a variable label with an animated numeric value.

    label: string label (e.g. 'x = ')
    value: initial numeric value, or a Real/ValueTracker.
    fmt: format string for the value.
    """
    def __init__(self, label='x', value=0, fmt='{:.2f}', x=960, y=540,
                 font_size=48, creation=0, z=0, **styling_kwargs):
        from vectormation._shapes import Text, DecimalNumber
        style_kw = {'fill': '#fff', 'stroke_width': 0} | styling_kwargs
        label_text = f'{label} = '
        self.label = Text(label_text, x=x, y=y, font_size=font_size,
                          text_anchor='end', creation=creation, z=z, **style_kw)
        self.number = DecimalNumber(value, fmt=fmt, x=x, y=y,
                                    font_size=font_size, creation=creation, z=z, **style_kw)
        super().__init__(self.label, self.number, creation=creation, z=z)

    @property
    def tracker(self):
        return self.number.tracker

    def set_value(self, val, start=0):
        self.number.set_value(val, start)
        return self

    def animate_value(self, target, start, end, easing=easings.smooth):
        self.number.animate_value(target, start, end, easing)
        return self


class Underline(VCollection):
    """Underline beneath a target object."""
    def __init__(self, target, buff=4, follow=True, creation=0, z=0, **styling_kwargs):
        style_kw = {'stroke': '#fff', 'stroke_width': 3} | styling_kwargs
        bx, by, bw, bh = target.bbox(creation)
        line = Line(x1=bx, y1=by + bh + buff, x2=bx + bw, y2=by + bh + buff,
                    creation=creation, z=z, **style_kw)
        if follow:
            _cache = {}
            def _bbox(t):
                if t not in _cache:
                    _cache.clear()
                    _cache[t] = target.bbox(t)
                return _cache[t]
            line.p1.set_onward(creation, lambda t: (_bbox(t)[0], _bbox(t)[1] + _bbox(t)[3] + buff))
            line.p2.set_onward(creation, lambda t: (_bbox(t)[0] + _bbox(t)[2], _bbox(t)[1] + _bbox(t)[3] + buff))
        super().__init__(line, creation=creation, z=z)
        self.line = line


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
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    # Determine direction
    if direction is None:
        # Perpendicular (pointing to the left of p1→p2)
        nx, ny = -dy / dist, dx / dist
        if ny > 0:
            direction = 'down'
        elif ny < 0:
            direction = 'up'
        elif nx > 0:
            direction = 'right'
        else:
            direction = 'left'
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


class ComplexPlane(Axes):
    """Complex number plane with Re/Im axes.

    Extends Axes with complex-number-specific methods.
    """
    def __init__(self, x_range=(-5, 5), y_range=(-5, 5),
                 x_label='Re', y_label='Im', show_grid=True,
                 creation=0, z=0, **kwargs):
        super().__init__(x_range=x_range, y_range=y_range,
                         x_label=x_label, y_label=y_label,
                         show_grid=show_grid, creation=creation, z=z, **kwargs)

    def number_to_point(self, z_val, time=0):
        """Convert a complex number to SVG coordinates."""
        if isinstance(z_val, complex):
            return self.coords_to_point(z_val.real, z_val.imag, time)
        return self.coords_to_point(float(z_val), 0, time)

    def point_to_number(self, x, y, time=0):
        """Convert SVG coordinates to a complex number."""
        xmin, xmax, ymin, ymax = self._get_bounds(time)
        re = xmin + (x - self.plot_x) / self.plot_width * (xmax - xmin)
        im = ymax - (y - self.plot_y) / self.plot_height * (ymax - ymin)
        return complex(re, im)


class Code(VCollection):
    """Syntax-highlighted code display.

    text: the source code string.
    language: programming language (used for color hints, basic highlighting).
    """
    _KEYWORD_COLORS = {
        'python': {'def', 'class', 'return', 'if', 'else', 'elif', 'for', 'while',
                   'import', 'from', 'in', 'not', 'and', 'or', 'with', 'as', 'try',
                   'except', 'finally', 'raise', 'yield', 'lambda', 'pass', 'break',
                   'continue', 'True', 'False', 'None', 'is', 'async', 'await'},
        'javascript': {'function', 'const', 'let', 'var', 'return', 'if', 'else',
                       'for', 'while', 'class', 'import', 'export', 'from', 'new',
                       'this', 'async', 'await', 'try', 'catch', 'throw', 'true',
                       'false', 'null', 'undefined', 'typeof', 'instanceof'},
    }

    def __init__(self, text, language='python', x=120, y=120, font_size=24,
                 line_height=1.5, tab_width=4, creation=0, z=0, **styling_kwargs):
        lines = text.strip('\n').split('\n')
        objects = []
        keywords = self._KEYWORD_COLORS.get(language, set())
        bg_width = max(len(line) for line in lines) * font_size * 0.6 + 40 if lines else 200
        bg_height = len(lines) * font_size * line_height + 20

        from vectormation._shapes import RoundedRectangle
        bg_style = {'fill': '#1e1e2e', 'fill_opacity': 0.95, 'stroke': '#444', 'stroke_width': 1} | styling_kwargs
        bg = RoundedRectangle(bg_width, bg_height, x=x - 10, y=y - font_size - 5,
                              corner_radius=8, creation=creation, z=z, **bg_style)
        objects.append(bg)

        for i, line in enumerate(lines):
            ly = y + i * font_size * line_height
            # Line number
            ln = Text(text=f'{i+1:>3}', x=x, y=ly, font_size=font_size,
                      creation=creation, z=z, fill='#666', stroke_width=0)
            objects.append(ln)
            # Code content with basic keyword highlighting
            code_x = x + font_size * 2.5
            expanded = line.replace('\t', ' ' * tab_width)
            words = re.split(r'(\s+)', expanded)
            wx = code_x
            for word in words:
                if not word:
                    continue
                if word.isspace():
                    wx += len(word) * font_size * 0.6
                    continue
                color = '#c678dd' if word in keywords else '#abb2bf'
                if word.startswith(('#', '//')):
                    color = '#5c6370'
                elif word.startswith(("'", '"')) or word.endswith(("'", '"')):
                    color = '#98c379'
                elif word.replace('.', '').replace('-', '').isdigit():
                    color = '#d19a66'
                t = Text(text=word, x=wx, y=ly, font_size=font_size,
                         creation=creation, z=z, fill=color, stroke_width=0)
                objects.append(t)
                wx += len(word) * font_size * 0.6
        super().__init__(*objects, creation=creation, z=z)
        self._code_x = x
        self._code_y = y
        self._font_size = font_size
        self._line_height = line_height
        self._bg_width = bg_width
        self._num_lines = len(lines)

    def highlight_lines(self, line_nums, start=0, end=1, color='#FFFF00', opacity=0.15,
                        easing=easings.there_and_back):
        """Highlight specific code lines with a colored overlay.
        line_nums: int or list of 1-based line numbers.
        Returns the highlight rectangles (add to canvas)."""
        if isinstance(line_nums, int):
            line_nums = [line_nums]
        rects = []
        for ln in line_nums:
            if ln < 1 or ln > self._num_lines:
                continue
            ry = self._code_y + (ln - 1) * self._font_size * self._line_height - self._font_size
            rect = Rectangle(self._bg_width, self._font_size * self._line_height,
                             x=self._code_x - 10, y=ry,
                             creation=start, fill=color, fill_opacity=0, stroke_width=0)
            dur = end - start
            if dur > 0:
                rect.styling.fill_opacity.set(start, end,
                    lambda t, _s=start, _d=dur: opacity * easing((t - _s) / _d), stay=True)
            rects.append(rect)
        return VCollection(*rects) if rects else VCollection()


class ChessBoard(VCollection):
    """Chess board visualization.

    size: pixel size of the board.
    show_coordinates: whether to show rank/file labels.
    """
    _PIECE_SYMBOLS = {
        'K': '\u2654', 'Q': '\u2655', 'R': '\u2656', 'B': '\u2657', 'N': '\u2658', 'P': '\u2659',
        'k': '\u265a', 'q': '\u265b', 'r': '\u265c', 'b': '\u265d', 'n': '\u265e', 'p': '\u265f',
    }

    def __init__(self, fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR',
                 cx=960, cy=540, size=600, show_coordinates=True,
                 light_color='#f0d9b5', dark_color='#b58863',
                 creation=0, z=0):
        cell = size / 8
        x0 = cx - size / 2
        y0 = cy - size / 2
        objects = []
        self._pieces = {}
        self._cell = cell
        self._x0, self._y0 = x0, y0

        # Draw squares
        for row in range(8):
            for col in range(8):
                color = light_color if (row + col) % 2 == 0 else dark_color
                sq = Rectangle(cell, cell, x=x0 + col * cell, y=y0 + row * cell,
                               creation=creation, z=z,
                               fill=color, fill_opacity=1, stroke_width=0)
                objects.append(sq)

        # Coordinate labels
        if show_coordinates:
            for col in range(8):
                lbl = Text(text=chr(ord('a') + col),
                           x=x0 + col * cell + cell / 2,
                           y=y0 + size + 18,
                           font_size=16, text_anchor='middle',
                           creation=creation, z=z, fill='#aaa', stroke_width=0)
                objects.append(lbl)
            for row in range(8):
                lbl = Text(text=str(8 - row),
                           x=x0 - 14,
                           y=y0 + row * cell + cell / 2 + 6,
                           font_size=16, text_anchor='middle',
                           creation=creation, z=z, fill='#aaa', stroke_width=0)
                objects.append(lbl)

        # Place pieces from FEN
        rows = fen.split('/')
        for row_idx, row_str in enumerate(rows):
            col_idx = 0
            for ch in row_str:
                if ch.isdigit():
                    col_idx += int(ch)
                elif ch in self._PIECE_SYMBOLS:
                    px = x0 + col_idx * cell + cell / 2
                    py = y0 + row_idx * cell + cell / 2 + cell * 0.1
                    piece = Text(text=self._PIECE_SYMBOLS[ch],
                                 x=px, y=py, font_size=cell * 0.7,
                                 text_anchor='middle',
                                 creation=creation, z=z + 1,
                                 fill='#fff' if ch.isupper() else '#222',
                                 stroke_width=0)
                    sq_name = chr(ord('a') + col_idx) + str(8 - row_idx)
                    self._pieces[sq_name] = piece
                    objects.append(piece)
                    col_idx += 1

        super().__init__(*objects, creation=creation, z=z)

    def move_piece(self, from_sq, to_sq, start=0, end=1, easing=easings.smooth):
        """Animate moving a piece from one square to another (e.g. 'e2' → 'e4')."""
        piece = self._pieces.get(from_sq)
        if piece is None:
            return self
        fc, fr = ord(from_sq[0]) - ord('a'), 8 - int(from_sq[1])
        tc, tr = ord(to_sq[0]) - ord('a'), 8 - int(to_sq[1])
        dx = (tc - fc) * self._cell
        dy = (tr - fr) * self._cell
        piece.shift(dx=dx, dy=dy, start_time=start, end_time=end, easing=easing)
        # Update piece mapping
        self._pieces[to_sq] = piece
        del self._pieces[from_sq]
        return self


_ELEMENT_DATA = [
    (1, 'H', 'Hydrogen', 1, 1), (2, 'He', 'Helium', 18, 1),
    (3, 'Li', 'Lithium', 1, 2), (4, 'Be', 'Beryllium', 2, 2),
    (5, 'B', 'Boron', 13, 2), (6, 'C', 'Carbon', 14, 2),
    (7, 'N', 'Nitrogen', 15, 2), (8, 'O', 'Oxygen', 16, 2),
    (9, 'F', 'Fluorine', 17, 2), (10, 'Ne', 'Neon', 18, 2),
    (11, 'Na', 'Sodium', 1, 3), (12, 'Mg', 'Magnesium', 2, 3),
    (13, 'Al', 'Aluminium', 13, 3), (14, 'Si', 'Silicon', 14, 3),
    (15, 'P', 'Phosphorus', 15, 3), (16, 'S', 'Sulfur', 16, 3),
    (17, 'Cl', 'Chlorine', 17, 3), (18, 'Ar', 'Argon', 18, 3),
    (19, 'K', 'Potassium', 1, 4), (20, 'Ca', 'Calcium', 2, 4),
    (21, 'Sc', 'Scandium', 3, 4), (22, 'Ti', 'Titanium', 4, 4),
    (23, 'V', 'Vanadium', 5, 4), (24, 'Cr', 'Chromium', 6, 4),
    (25, 'Mn', 'Manganese', 7, 4), (26, 'Fe', 'Iron', 8, 4),
    (27, 'Co', 'Cobalt', 9, 4), (28, 'Ni', 'Nickel', 10, 4),
    (29, 'Cu', 'Copper', 11, 4), (30, 'Zn', 'Zinc', 12, 4),
    (31, 'Ga', 'Gallium', 13, 4), (32, 'Ge', 'Germanium', 14, 4),
    (33, 'As', 'Arsenic', 15, 4), (34, 'Se', 'Selenium', 16, 4),
    (35, 'Br', 'Bromine', 17, 4), (36, 'Kr', 'Krypton', 18, 4),
]

_CATEGORY_COLORS = {
    'nonmetal': '#58C4DD', 'noble_gas': '#9A72AC', 'alkali': '#FC6255',
    'alkaline': '#F0AC5F', 'metalloid': '#5CD0B3', 'halogen': '#FFFF00',
    'transition': '#C55F73', 'post_transition': '#83C167',
}

def _element_category(z):
    if z in (1, 6, 7, 8, 15, 16, 34): return 'nonmetal'
    if z in (2, 10, 18, 36): return 'noble_gas'
    if z in (3, 11, 19): return 'alkali'
    if z in (4, 12, 20): return 'alkaline'
    if z in (5, 14, 32, 33): return 'metalloid'
    if z in (9, 17, 35): return 'halogen'
    if 21 <= z <= 30: return 'transition'
    return 'post_transition'


class PeriodicTable(VCollection):
    """Periodic table of elements (first 36 elements).

    cell_size: pixel size of each element cell.
    """
    def __init__(self, cx=960, cy=540, cell_size=48, creation=0, z=0):
        objects = []
        total_w = 18 * cell_size
        total_h = 4 * cell_size
        x0 = cx - total_w / 2
        y0 = cy - total_h / 2

        self._cells = {}
        for atomic_num, symbol, _name, col, row in _ELEMENT_DATA:
            cat = _element_category(atomic_num)
            color = _CATEGORY_COLORS.get(cat, '#888')
            ex = x0 + (col - 1) * cell_size
            ey = y0 + (row - 1) * cell_size
            bg = Rectangle(cell_size - 2, cell_size - 2, x=ex + 1, y=ey + 1,
                           creation=creation, z=z,
                           fill=color, fill_opacity=0.3, stroke=color, stroke_width=1)
            objects.append(bg)
            num_t = Text(text=str(atomic_num), x=ex + 4, y=ey + 12,
                         font_size=10, creation=creation, z=z,
                         fill='#aaa', stroke_width=0)
            objects.append(num_t)
            sym_t = Text(text=symbol, x=ex + cell_size / 2, y=ey + cell_size / 2 + 4,
                         font_size=18, text_anchor='middle',
                         creation=creation, z=z, fill='#fff', stroke_width=0)
            objects.append(sym_t)
            self._cells[symbol] = (bg, num_t, sym_t)

        super().__init__(*objects, creation=creation, z=z)

    def highlight(self, symbol, start=0, end=1, color='#FFFF00', easing=easings.there_and_back):
        """Highlight an element by symbol."""
        if symbol in self._cells:
            bg, _, sym = self._cells[symbol]
            bg.indicate(start, end, easing=easing)
            sym.flash(start, end, color=color, easing=easing)
        return self


class BohrAtom(VCollection):
    """Bohr model of an atom with electron shells.

    protons: number of protons (atomic number).
    neutrons: number of neutrons.
    electrons: list of electrons per shell, e.g. [2, 8, 1] for sodium.
    """
    def __init__(self, protons=1, neutrons=0, electrons=None, cx=960, cy=540,
                 nucleus_r=30, shell_spacing=40, creation=0, z=0):
        from vectormation._shapes import Circle, Dot, Text
        objects = []

        # Nucleus
        nucleus = Circle(r=nucleus_r, cx=cx, cy=cy, creation=creation, z=z + 1,
                         fill='#FC6255', fill_opacity=0.8, stroke='#fff', stroke_width=2)
        objects.append(nucleus)
        nucleus_text = f'{protons}p\u207a' if neutrons == 0 else f'{protons}p {neutrons}n'
        label = Text(text=nucleus_text, x=cx, y=cy + 6,
                     font_size=max(10, nucleus_r * 0.5), text_anchor='middle',
                     creation=creation, z=z + 2, fill='#fff', stroke_width=0)
        objects.append(label)

        if electrons is None:
            # Auto-fill shells: 2, 8, 8, 18, ...
            remaining = protons
            electrons = []
            for cap in [2, 8, 8, 18, 18, 32]:
                if remaining <= 0:
                    break
                electrons.append(min(remaining, cap))
                remaining -= electrons[-1]

        # Electron shells
        self._electron_dots = []
        for shell_idx, n_electrons in enumerate(electrons):
            r = nucleus_r + (shell_idx + 1) * shell_spacing
            orbit = Circle(r=r, cx=cx, cy=cy, creation=creation, z=z,
                           fill_opacity=0, stroke='#58C4DD', stroke_width=1, stroke_opacity=0.4)
            objects.append(orbit)
            for e in range(n_electrons):
                angle = 2 * math.pi * e / n_electrons
                ex = cx + r * math.cos(angle)
                ey = cy - r * math.sin(angle)
                dot = Dot(r=5, cx=ex, cy=ey, creation=creation, z=z + 1,
                          fill='#58C4DD', fill_opacity=1)
                objects.append(dot)
                self._electron_dots.append(dot)

        super().__init__(*objects, creation=creation, z=z)

    def orbit(self, start=0, end=None, speed=45):
        """Animate all electrons orbiting around the nucleus."""
        for dot in self._electron_dots:
            dot.always_rotate(start=start, end=end, degrees_per_second=speed)
        return self


class Automaton(VCollection):
    """Finite state machine / automaton visualization.

    states: list of state names, e.g. ['q0', 'q1', 'q2']
    transitions: list of (from_state, to_state, label) tuples
    accept_states: set of accepting state names (drawn with double circle)
    initial_state: name of the initial state (gets an incoming arrow)
    """
    def __init__(self, states, transitions, accept_states=None, initial_state=None,
                 cx=960, cy=540, radius=300, state_r=35, font_size=20,
                 creation=0, z=0):
        from vectormation._shapes import Circle, Text
        objects = []
        accept_states = accept_states or set()
        n = len(states)
        self._state_positions = {}
        self._state_circles = {}
        if n == 0:
            super().__init__(creation=creation, z=z)
            return

        # Arrange states in a circle
        for i, name in enumerate(states):
            angle = 2 * math.pi * i / n - math.pi / 2
            sx = cx + radius * math.cos(angle)
            sy = cy + radius * math.sin(angle)
            self._state_positions[name] = (sx, sy)

            circle = Circle(r=state_r, cx=sx, cy=sy, creation=creation, z=z,
                            fill='#1e1e2e', fill_opacity=0.9, stroke='#58C4DD', stroke_width=2)
            objects.append(circle)
            self._state_circles[name] = circle

            if name in accept_states:
                inner = Circle(r=state_r - 5, cx=sx, cy=sy, creation=creation, z=z,
                               fill_opacity=0, stroke='#58C4DD', stroke_width=2)
                objects.append(inner)

            label = Text(text=name, x=sx, y=sy + font_size * 0.35,
                         font_size=font_size, text_anchor='middle',
                         creation=creation, z=z + 1, fill='#fff', stroke_width=0)
            objects.append(label)

        # Initial state arrow
        if initial_state and initial_state in self._state_positions:
            sx, sy = self._state_positions[initial_state]
            objects.append(Arrow(x1=sx - state_r - 50, y1=sy, x2=sx - state_r - 2, y2=sy,
                                 tip_length=12, tip_width=10,
                                 creation=creation, z=z, stroke='#fff', stroke_width=2))

        # Transitions
        for from_s, to_s, label_text in transitions:
            if from_s not in self._state_positions or to_s not in self._state_positions:
                continue
            fx, fy = self._state_positions[from_s]
            tx, ty = self._state_positions[to_s]

            if from_s == to_s:
                # Self-loop: arc above the state
                loop_r = state_r * 0.8
                loop = Arc(cx=fx, cy=fy - state_r - loop_r, r=loop_r,
                           start_angle=210, end_angle=330,
                           creation=creation, z=z, stroke='#83C167', stroke_width=2)
                objects.append(loop)
                lbl = Text(text=label_text, x=fx, y=fy - state_r - loop_r * 2 - 8,
                           font_size=font_size * 0.8, text_anchor='middle',
                           creation=creation, z=z + 1, fill='#83C167', stroke_width=0)
                objects.append(lbl)
            else:
                dx, dy = tx - fx, ty - fy
                dist = math.hypot(dx, dy) or 1
                ux, uy = dx / dist, dy / dist
                # Shorten to circle edges
                sx, sy = fx + ux * state_r, fy + uy * state_r
                ex, ey = tx - ux * state_r, ty - uy * state_r
                arrow = Arrow(x1=sx, y1=sy, x2=ex, y2=ey,
                              tip_length=12, tip_width=10,
                              creation=creation, z=z, stroke='#83C167', stroke_width=2)
                objects.append(arrow)
                mx, my = (sx + ex) / 2, (sy + ey) / 2
                # Offset label perpendicular to arrow
                px, py = -uy * 15, ux * 15
                lbl = Text(text=label_text, x=mx + px, y=my + py + font_size * 0.35,
                           font_size=font_size * 0.8, text_anchor='middle',
                           creation=creation, z=z + 1, fill='#83C167', stroke_width=0)
                objects.append(lbl)

        super().__init__(*objects, creation=creation, z=z)

    def highlight_state(self, state_name, start=0, end=1, color='#FFFF00', easing=easings.there_and_back):
        """Highlight a state by flashing its circle."""
        if state_name in self._state_circles:
            self._state_circles[state_name].flash(start, end, color=color, easing=easing)
        return self


class NetworkGraph(VCollection):
    """Network/graph visualization with nodes and edges.

    nodes: dict mapping node_id -> label string, or a list of labels.
    edges: list of (from_id, to_id) or (from_id, to_id, label) tuples.
    layout: 'circular', 'spring', or 'grid'.
    directed: whether to draw arrows (True) or lines (False).
    """
    def __init__(self, nodes, edges=None, cx=960, cy=540, radius=300,
                 node_r=30, font_size=20, layout='circular', directed=False,
                 creation=0, z=0):
        from vectormation._shapes import Circle, Text, Line as SLine
        objects = []
        edges = edges or []

        # Normalize nodes to dict
        if isinstance(nodes, (list, tuple)):
            nodes = {i: str(v) for i, v in enumerate(nodes)}

        node_ids = list(nodes.keys())
        n = len(node_ids)
        self._node_positions = {}
        self._node_circles = {}
        if n == 0:
            super().__init__(creation=creation, z=z)
            return

        # Layout
        if layout == 'circular':
            for i, nid in enumerate(node_ids):
                angle = 2 * math.pi * i / max(n, 1) - math.pi / 2
                nx = cx + radius * math.cos(angle)
                ny = cy + radius * math.sin(angle)
                self._node_positions[nid] = (nx, ny)
        elif layout == 'grid':
            cols = max(1, int(math.ceil(math.sqrt(n))))
            spacing = radius * 2 / max(cols - 1, 1) if cols > 1 else 0
            x0 = cx - (cols - 1) * spacing / 2
            y0 = cy - ((n - 1) // cols) * spacing / 2
            for i, nid in enumerate(node_ids):
                r, c = divmod(i, cols)
                self._node_positions[nid] = (x0 + c * spacing, y0 + r * spacing)
        else:  # spring (simple force-directed, few iterations)
            import random
            rng = random.Random(42)
            pos = {nid: (cx + rng.uniform(-radius, radius), cy + rng.uniform(-radius, radius))
                   for nid in node_ids}
            for _ in range(50):
                forces = {nid: [0.0, 0.0] for nid in node_ids}
                # Repulsion
                for i, a in enumerate(node_ids):
                    for b in node_ids[i + 1:]:
                        dx = pos[a][0] - pos[b][0]
                        dy = pos[a][1] - pos[b][1]
                        d = math.hypot(dx, dy) + 1
                        f = 5000 / (d * d)
                        forces[a][0] += f * dx / d
                        forces[a][1] += f * dy / d
                        forces[b][0] -= f * dx / d
                        forces[b][1] -= f * dy / d
                # Attraction (edges)
                for edge in edges:
                    a, b = edge[0], edge[1]
                    if a not in pos or b not in pos:
                        continue
                    dx = pos[b][0] - pos[a][0]
                    dy = pos[b][1] - pos[a][1]
                    d = math.hypot(dx, dy) + 1
                    f = d * 0.01
                    forces[a][0] += f * dx / d
                    forces[a][1] += f * dy / d
                    forces[b][0] -= f * dx / d
                    forces[b][1] -= f * dy / d
                for nid in node_ids:
                    pos[nid] = (pos[nid][0] + forces[nid][0] * 0.1,
                                pos[nid][1] + forces[nid][1] * 0.1)
            # Center the layout
            avg_x = sum(p[0] for p in pos.values()) / n if n else cx
            avg_y = sum(p[1] for p in pos.values()) / n if n else cy
            for nid in node_ids:
                self._node_positions[nid] = (pos[nid][0] - avg_x + cx,
                                             pos[nid][1] - avg_y + cy)

        # Draw edges
        for edge in edges:
            a, b = edge[0], edge[1]
            label = edge[2] if len(edge) > 2 else None
            if a not in self._node_positions or b not in self._node_positions:
                continue
            ax, ay = self._node_positions[a]
            bx, by = self._node_positions[b]
            if directed:
                dx, dy = bx - ax, by - ay
                d = math.hypot(dx, dy) or 1
                # Shorten to not overlap circles
                ax2 = ax + dx / d * node_r
                ay2 = ay + dy / d * node_r
                bx2 = bx - dx / d * node_r
                by2 = by - dy / d * node_r
                arrow = Arrow(x1=ax2, y1=ay2, x2=bx2, y2=by2,
                              tip_length=12, tip_width=10,
                              creation=creation, z=z, stroke='#888', stroke_width=2)
                objects.append(arrow)
            else:
                line = SLine(x1=ax, y1=ay, x2=bx, y2=by,
                             creation=creation, z=z, stroke='#888', stroke_width=2)
                objects.append(line)
            if label:
                mx, my = (ax + bx) / 2, (ay + by) / 2
                lbl = Text(text=str(label), x=mx, y=my - 10,
                           font_size=font_size * 0.8, text_anchor='middle',
                           creation=creation, z=z + 2, fill='#aaa', stroke_width=0)
                objects.append(lbl)

        # Draw nodes
        for nid in node_ids:
            nx, ny = self._node_positions[nid]
            circle = Circle(r=node_r, cx=nx, cy=ny, creation=creation, z=z + 1,
                            fill='#1e1e2e', fill_opacity=0.9, stroke='#58C4DD', stroke_width=2)
            objects.append(circle)
            self._node_circles[nid] = circle
            lbl_text = str(nodes[nid])
            lbl = Text(text=lbl_text, x=nx, y=ny + font_size * 0.35,
                       font_size=font_size, text_anchor='middle',
                       creation=creation, z=z + 2, fill='#fff', stroke_width=0)
            objects.append(lbl)

        super().__init__(*objects, creation=creation, z=z)

    def highlight_node(self, node_id, start=0, end=1, color='#FFFF00', easing=easings.there_and_back):
        """Flash-highlight a node by its ID."""
        if node_id in self._node_circles:
            self._node_circles[node_id].flash(start, end, color=color, easing=easing)
        return self

    def get_node_position(self, node_id):
        """Get the (x, y) position of a node."""
        return self._node_positions.get(node_id, (960, 540))


class Label(VCollection):
    """Text label with a surrounding box/frame for annotations."""
    def __init__(self, text, x=960, y=540, font_size=36, padding=10,
                 corner_radius=4, creation=0, z=0, **styling_kwargs):
        from vectormation._shapes import Text, RoundedRectangle
        style_kw = {'fill': '#fff', 'stroke_width': 0} | styling_kwargs
        txt = Text(text=text, x=x, y=y, font_size=font_size,
                   text_anchor='middle', creation=creation, z=z + 1, **style_kw)
        _, _, tw, th = txt.bbox(creation)
        bg = RoundedRectangle(tw + 2 * padding, th + 2 * padding,
                              x=x - tw / 2 - padding, y=y - th - padding + 4,
                              corner_radius=corner_radius, creation=creation, z=z,
                              fill='#1e1e2e', fill_opacity=0.9, stroke='#555', stroke_width=1)
        super().__init__(bg, txt, creation=creation, z=z)


class LabeledArrow(VCollection):
    """Arrow with a text label placed at its midpoint."""
    def __init__(self, x1=860, y1=540, x2=1060, y2=540, label='',
                 font_size=24, label_buff=10, creation=0, z=0, **styling_kwargs):
        from vectormation._shapes import Text
        style_kw = {'stroke': '#fff', 'stroke_width': 3} | styling_kwargs
        arrow = Arrow(x1=x1, y1=y1, x2=x2, y2=y2, creation=creation, z=z, **style_kw)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy) or 1
        # Perpendicular offset for the label
        nx, ny = -dy / dist * label_buff, dx / dist * label_buff
        lbl = Text(text=label, x=mx + nx, y=my + ny + font_size * 0.35,
                   font_size=font_size, text_anchor='middle',
                   creation=creation, z=z + 1, fill='#fff', stroke_width=0)
        super().__init__(arrow, lbl, creation=creation, z=z)
        self.arrow = arrow
        self.label_obj = lbl


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
                    if cx < 0 or cx > 1920 or cy < 0 or cy > 1080:
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
            angle = 2 * math.pi * i / n_sectors
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


class Callout(VCollection):
    """Text callout with a pointer line to a target position.

    text: annotation text.
    target: (x, y) tuple or VObject to point to.
    direction: 'up', 'down', 'left', 'right' — where the callout box sits relative to target.
    """
    def __init__(self, text, target, direction='up', distance=80, font_size=24,
                 padding=8, corner_radius=4, creation=0, z=0, **styling_kwargs):
        from vectormation._shapes import Text as SText, RoundedRectangle, Line as SLine

        # Resolve target position
        if hasattr(target, 'bbox'):
            bx, by, bw, bh = target.bbox(creation)
            tx, ty = bx + bw / 2, by + bh / 2
        else:
            tx, ty = target

        # Position the label box
        offsets = {'up': (0, -distance), 'down': (0, distance),
                   'left': (-distance, 0), 'right': (distance, 0)}
        ox, oy = offsets.get(direction, (0, -distance))
        lx, ly = tx + ox, ty + oy

        style_kw = {'fill': '#fff', 'stroke_width': 0} | styling_kwargs
        lbl = SText(text=text, x=lx, y=ly, font_size=font_size,
                    text_anchor='middle', creation=creation, z=z + 2, **style_kw)
        _, _, tw, th = lbl.bbox(creation)
        bg = RoundedRectangle(tw + 2 * padding, th + 2 * padding,
                              x=lx - tw / 2 - padding, y=ly - th - padding + 4,
                              corner_radius=corner_radius, creation=creation, z=z + 1,
                              fill='#1e1e2e', fill_opacity=0.9, stroke='#555', stroke_width=1)
        pointer = SLine(x1=tx, y1=ty, x2=lx, y2=ly - th / 2 if direction == 'up' else ly + th / 2 if direction == 'down' else ly,
                        creation=creation, z=z, stroke='#888', stroke_width=1)
        super().__init__(pointer, bg, lbl, creation=creation, z=z)


class DimensionLine(VCollection):
    """Technical dimension line between two points with measurement label.

    p1, p2: (x, y) endpoints.
    label: text label (default: auto-calculated pixel distance).
    offset: perpendicular offset from the line between p1 and p2.
    """
    def __init__(self, p1, p2, label=None, offset=30, font_size=20,
                 tick_size=10, creation=0, z=0, **styling_kwargs):
        from vectormation._shapes import Text as SText, Line as SLine
        x1, y1 = p1
        x2, y2 = p2
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy) or 1
        # Perpendicular unit vector
        nx, ny = -dy / length * offset, dx / length * offset
        # Offset endpoints
        ox1, oy1 = x1 + nx, y1 + ny
        ox2, oy2 = x2 + nx, y2 + ny

        style_kw = {'stroke': '#aaa', 'stroke_width': 1} | styling_kwargs

        # Main dimension line
        main = SLine(x1=ox1, y1=oy1, x2=ox2, y2=oy2, creation=creation, z=z, **style_kw)
        # Extension lines (ticks from original points to dimension line)
        ext1 = SLine(x1=x1, y1=y1, x2=ox1 + nx * 0.3, y2=oy1 + ny * 0.3,
                     creation=creation, z=z, **style_kw)
        ext2 = SLine(x1=x2, y1=y2, x2=ox2 + nx * 0.3, y2=oy2 + ny * 0.3,
                     creation=creation, z=z, **style_kw)
        # Tick marks at ends of dimension line
        tnx, tny = -dy / length * tick_size / 2, dx / length * tick_size / 2
        tick1 = SLine(x1=ox1 - tnx, y1=oy1 - tny, x2=ox1 + tnx, y2=oy1 + tny,
                      creation=creation, z=z, **style_kw)
        tick2 = SLine(x1=ox2 - tnx, y1=oy2 - tny, x2=ox2 + tnx, y2=oy2 + tny,
                      creation=creation, z=z, **style_kw)

        # Label
        if label is None:
            label = f'{length:.0f}'
        mx, my = (ox1 + ox2) / 2, (oy1 + oy2) / 2
        lbl = SText(text=str(label), x=mx + nx * 0.5, y=my + ny * 0.5,
                    font_size=font_size, text_anchor='middle',
                    creation=creation, z=z + 1, fill='#aaa', stroke_width=0)
        super().__init__(main, ext1, ext2, tick1, tick2, lbl, creation=creation, z=z)


class Tooltip(VCollection):
    """Small animated tooltip that appears and disappears near a target.

    text: tooltip text.
    target: (x, y) tuple or VObject.
    """
    def __init__(self, text, target, start=0, duration=1.5, font_size=18,
                 padding=6, creation=0, z=10, **styling_kwargs):
        from vectormation._shapes import Text as SText, RoundedRectangle
        if hasattr(target, 'bbox'):
            bx, by, bw, bh = target.bbox(creation)
            tx, ty = bx + bw / 2, by
        else:
            tx, ty = target

        style_kw = {'fill': '#fff', 'stroke_width': 0} | styling_kwargs
        lbl = SText(text=text, x=tx, y=ty - 20, font_size=font_size,
                    text_anchor='middle', creation=creation, z=z + 1, **style_kw)
        _, _, tw, th = lbl.bbox(creation)
        bg = RoundedRectangle(tw + 2 * padding, th + 2 * padding,
                              x=tx - tw / 2 - padding, y=ty - 20 - th - padding + 4,
                              corner_radius=4, creation=creation, z=z,
                              fill='#333', fill_opacity=0.9, stroke='#666', stroke_width=1)
        super().__init__(bg, lbl, creation=creation, z=z)
        # Auto-animate: fade in, hold, fade out
        if duration <= 0:
            duration = 0.1
        fade_time = min(0.3, duration / 3)
        self.fadein(start, start + fade_time)
        self.fadeout(start + duration - fade_time, start + duration)


class Tree(VCollection):
    """Hierarchical tree layout visualization.

    data: nested dict like {'root': {'child1': {}, 'child2': {'leaf': {}}}}
          or a tuple tree: ('root', [('child1', []), ('child2', [('leaf', [])])])
    layout: 'down' (root at top) or 'right' (root at left).
    """
    def __init__(self, data, cx=960, cy=100, h_spacing=120, v_spacing=100,
                 node_r=20, font_size=18, layout='down',
                 creation=0, z=0):
        from vectormation._shapes import Circle, Text as SText, Line as SLine
        objects = []

        # Normalize data to (label, children) format
        if isinstance(data, dict):
            data = self._dict_to_tree(data)

        # Use id(node_tuple) as key to handle duplicate labels
        positions = {}   # id(node) -> (x, y)
        labels = {}      # id(node) -> label string
        widths = {}      # id(node) -> subtree width
        node_map = {}    # label -> id(node) (first occurrence, for API)

        self._collect_nodes(data, labels, node_map)
        self._calc_widths(data, widths, h_spacing)
        self._layout(data, cx, cy, widths, h_spacing, v_spacing, positions, layout)

        # Draw edges
        self._draw_edges_impl(data, positions, objects, creation, z, SLine)

        # Draw nodes (skip empty-label nodes)
        self._node_objects = {}
        self._positions_by_label = {}
        for node_tuple, (nx, ny) in [(n, positions[id(n)]) for n in self._all_nodes(data) if id(n) in positions]:
            label = node_tuple[0]
            if not label:
                continue
            circle = Circle(r=node_r, cx=nx, cy=ny, creation=creation, z=z + 1,
                            fill='#1e1e2e', fill_opacity=0.9, stroke='#58C4DD', stroke_width=2)
            objects.append(circle)
            nid = id(node_tuple)
            self._node_objects[nid] = circle
            if label not in self._positions_by_label:
                self._positions_by_label[label] = (nx, ny)
                self._node_objects[label] = circle  # label-based lookup (first occurrence)
            lbl = SText(text=str(label), x=nx, y=ny + font_size * 0.35,
                        font_size=font_size, text_anchor='middle',
                        creation=creation, z=z + 2, fill='#fff', stroke_width=0)
            objects.append(lbl)

        super().__init__(*objects, creation=creation, z=z)

    @staticmethod
    def _all_nodes(node):
        """Yield all nodes in pre-order."""
        yield node
        for child in node[1]:
            yield from Tree._all_nodes(child)

    @staticmethod
    def _collect_nodes(node, labels, node_map):
        label = node[0]
        labels[id(node)] = label
        if label and label not in node_map:
            node_map[label] = id(node)
        for child in node[1]:
            Tree._collect_nodes(child, labels, node_map)

    @staticmethod
    def _dict_to_tree(d):
        """Convert dict tree to tuple tree."""
        if not d:
            return ('', [])
        key = next(iter(d))
        children = d[key]
        if isinstance(children, dict):
            return (key, [Tree._dict_to_tree({k: v}) for k, v in children.items()])
        return (key, [])

    @staticmethod
    def _calc_widths(node, widths, spacing):
        if not node[1]:
            widths[id(node)] = spacing
        else:
            total = 0
            for child in node[1]:
                Tree._calc_widths(child, widths, spacing)
                total += widths[id(child)]
            widths[id(node)] = max(total, spacing)

    @staticmethod
    def _layout(node, x, y, widths, h_spacing, v_spacing, positions, layout):
        positions[id(node)] = (x, y)
        children = node[1]
        if not children:
            return
        total_w = sum(widths[id(c)] for c in children)
        cur = x - total_w / 2
        for child in children:
            cw = widths[id(child)]
            child_x = cur + cw / 2
            if layout == 'down':
                Tree._layout(child, child_x, y + v_spacing, widths, h_spacing, v_spacing, positions, layout)
            else:
                Tree._layout(child, x + v_spacing, child_x, widths, h_spacing, v_spacing, positions, layout)
            cur += cw

    @staticmethod
    def _draw_edges_impl(node, positions, objects, creation, z, LineClass):
        px, py = positions[id(node)]
        for child in node[1]:
            if id(child) in positions:
                ccx, ccy = positions[id(child)]
                objects.append(LineClass(x1=px, y1=py, x2=ccx, y2=ccy,
                                        creation=creation, z=z, stroke='#888', stroke_width=2))
            Tree._draw_edges_impl(child, positions, objects, creation, z, LineClass)

    def get_node_position(self, label):
        """Get (x, y) position of a node by label (first occurrence if duplicates)."""
        return self._positions_by_label.get(label, (960, 540))

    def highlight_node(self, label, start=0, end=1, color='#FFFF00', easing=easings.there_and_back):
        """Flash-highlight a node by label."""
        if label in self._node_objects:
            self._node_objects[label].flash(start, end, color=color, easing=easing)
        return self


def always_redraw(func, creation=0, z=0):
    """Convenience wrapper: create a DynamicObject from a callable.
    func(time) should return a VObject."""
    return DynamicObject(func, creation=creation, z=z)


class Stamp(VCollection):
    """Place copies of a template object at specified positions.

    template: the VObject to copy.
    points: list of (x, y) positions to place copies at.
    """
    def __init__(self, template, points, creation=0, z=0):
        from copy import deepcopy
        objects = []
        for px, py in points:
            c = deepcopy(template)
            bx, by, bw, bh = c.bbox(creation)
            cx, cy = bx + bw / 2, by + bh / 2
            c.shift(dx=px - cx, dy=py - cy, start_time=creation)
            objects.append(c)
        super().__init__(*objects, creation=creation, z=z)


class TimelineBar(VCollection):
    """Visual timeline bar with labeled markers.

    markers: dict of {time_val: label} pairs.
    total_duration: the max time value represented.
    """
    def __init__(self, markers, total_duration=10, x=200, y=900,
                 width=1520, height=6, marker_color='#FFFF00',
                 font_size=14, creation=0, z=0):
        from vectormation._shapes import Rectangle, Line, Text, Circle
        objects = []
        # Track bar
        track = Rectangle(width, height, x=x, y=y - height / 2,
                          fill='#444', fill_opacity=0.8, stroke_width=0,
                          creation=creation, z=z)
        objects.append(track)
        # Markers
        if total_duration <= 0:
            total_duration = 1
        for t_val, label in markers.items():
            frac = t_val / total_duration
            mx = x + frac * width
            tick = Line(x1=mx, y1=y - 15, x2=mx, y2=y + 15,
                        stroke=marker_color, stroke_width=2,
                        creation=creation, z=z + 0.1)
            dot = Circle(r=4, cx=mx, cy=y, fill=marker_color,
                         fill_opacity=1, stroke_width=0,
                         creation=creation, z=z + 0.2)
            txt = Text(text=str(label), x=mx, y=y - 22,
                       font_size=font_size, fill='#ccc', stroke_width=0,
                       text_anchor='middle', creation=creation, z=z + 0.1)
            objects.extend([tick, dot, txt])
        super().__init__(*objects, creation=creation, z=z)


class Legend(VCollection):
    """Chart legend with colored swatches and labels.

    items: list of (color, label) tuples.
    """
    def __init__(self, items, x=100, y=100, swatch_size=16, spacing=8,
                 font_size=16, direction='down', creation=0, z=0):
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
                cursor_x += swatch_size + spacing + len(label) * font_size * 0.6 + spacing * 2
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
                 fill_opacity=0.3, creation=0, z=0):
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
        angles = [i * 2 * math.pi / n - math.pi / 2 for i in range(n)]
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
                txt = Text(text=label, x=lx, y=ly + font_size * 0.35,
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
                 corner_radius=6, creation=0, z=0):
        from vectormation._shapes import RoundedRectangle
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


class FlowChart(VCollection):
    """Simple flow chart with labeled boxes connected by arrows.

    steps: list of str labels for each box.
    direction: 'right' or 'down'.
    """
    def __init__(self, steps, direction='right', x=200, y=400,
                 box_width=200, box_height=60, spacing=80,
                 box_color='#58C4DD', text_color='#fff', arrow_color='#999',
                 font_size=20, corner_radius=8, creation=0, z=0):
        from vectormation._shapes import RoundedRectangle, Text
        objects = []
        self._boxes = []
        self._labels = []
        horizontal = direction == 'right'
        for i, label in enumerate(steps):
            if horizontal:
                bx = x + i * (box_width + spacing)
                by = y
            else:
                bx = x
                by = y + i * (box_height + spacing)
            box = RoundedRectangle(box_width, box_height, x=bx, y=by,
                                   corner_radius=corner_radius,
                                   fill=box_color, fill_opacity=0.8,
                                   stroke=box_color, creation=creation, z=z)
            txt = Text(text=label, x=bx + box_width / 2, y=by + box_height / 2 + font_size * 0.35,
                       font_size=font_size, fill=text_color, stroke_width=0,
                       text_anchor='middle', creation=creation, z=z + 0.1)
            self._boxes.append(box)
            self._labels.append(txt)
            objects.extend([box, txt])
            # Arrow between boxes
            if i > 0:
                if horizontal:
                    prev_bx = x + (i - 1) * (box_width + spacing)
                    ax1, ay1 = prev_bx + box_width, y + box_height / 2
                    ax2, ay2 = bx, y + box_height / 2
                else:
                    prev_by = y + (i - 1) * (box_height + spacing)
                    ax1, ay1 = x + box_width / 2, prev_by + box_height
                    ax2, ay2 = x + box_width / 2, by
                arr = Arrow(ax1, ay1, ax2, ay2, stroke=arrow_color,
                            creation=creation, z=z - 0.1)
                objects.append(arr)
        super().__init__(*objects, creation=creation, z=z)


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
                 show_total=True, creation=0, z=0):
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
                 font_size=16, creation=0, z=0):
        n = len(tasks)
        if n == 0:
            super().__init__(creation=creation, z=z)
            return
        if colors is None:
            colors = ['#58C4DD', '#83C167', '#FF6B6B', '#FFFF00',
                      '#FF79C6', '#B8BB26', '#BD93F9', '#FFB86C']
        total_h = height if height else n * (bar_height + bar_spacing) + 40
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
            lbl = Text(text=task_label, x=x + 5, y=by + bar_height / 2 + font_size * 0.35,
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
                 font_size=16, creation=0, z=0):
        if not flows:
            super().__init__(creation=creation, z=z)
            return
        if colors is None:
            colors = ['#58C4DD', '#83C167', '#FF6B6B', '#FFFF00',
                      '#FF79C6', '#B8BB26', '#BD93F9', '#FFB86C']
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
                                    y=by + bh / 2 + font_size * 0.35,
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
                 colors=None, font_size=18, gap=4, creation=0, z=0):
        if not stages:
            super().__init__(creation=creation, z=z)
            return
        if colors is None:
            colors = ['#58C4DD', '#83C167', '#FF6B6B', '#FFFF00',
                      '#FF79C6', '#B8BB26', '#BD93F9', '#FFB86C']
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
            lbl = Text(text=f'{label} ({val})', x=cx, y=ty + row_h / 2 + font_size * 0.35,
                       font_size=font_size, fill='#fff', stroke_width=0,
                       text_anchor='middle', creation=creation, z=z + 0.1)
            objects.append(lbl)
        super().__init__(*objects, creation=creation, z=z)


class TreeMap(VCollection):
    """Treemap visualization using squarified layout.

    data: list of (label, value) tuples.
    """
    def __init__(self, data, x=100, y=100, width=800, height=600,
                 colors=None, font_size=14, padding=2, creation=0, z=0):
        if not data:
            super().__init__(creation=creation, z=z)
            return
        if colors is None:
            colors = ['#58C4DD', '#83C167', '#FF6B6B', '#FFFF00',
                      '#FF79C6', '#B8BB26', '#BD93F9', '#FFB86C']
        total = sum(v for _, v in data) or 1
        # Sort descending by value for squarified layout
        sorted_data = sorted(enumerate(data), key=lambda iv: iv[1][1], reverse=True)
        rects = self._squarify(sorted_data, x, y, width, height, total)
        objects = []
        for orig_idx, (label, val), (rx, ry, rw, rh) in rects:
            color = colors[orig_idx % len(colors)]
            rect = Rectangle(width=max(rw - padding, 1), height=max(rh - padding, 1),
                              x=rx + padding / 2, y=ry + padding / 2,
                              fill=color, fill_opacity=0.8, stroke='#222', stroke_width=1,
                              creation=creation, z=z)
            objects.append(rect)
            if rw > font_size * 2 and rh > font_size * 1.5:
                lbl = Text(text=str(label), x=rx + rw / 2, y=ry + rh / 2 + font_size * 0.35,
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
                 tick_count=5, creation=0, z=0):
        if colors is None:
            colors = [('#83C167', 0.0), ('#FFFF00', 0.5), ('#FF6B6B', 1.0)]
        objects = []
        # Background arc segments (colored bands)
        n_segments = 60
        sa_rad = math.radians(start_angle)
        ea_rad = math.radians(end_angle)
        if ea_rad > sa_rad:
            ea_rad -= 2 * math.pi
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
                 show_endpoint=False, creation=0, z=0, **styling_kwargs):
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


class VennDiagram(VCollection):
    """Venn diagram with 2 or 3 overlapping circles.

    labels: list of 2 or 3 labels.
    sizes: optional list of radii (default equal).
    """
    def __init__(self, labels, sizes=None, x=960, y=540, radius=150,
                 colors=None, font_size=24, creation=0, z=0):
        n = len(labels)
        if n < 2 or n > 3:
            super().__init__(creation=creation, z=z)
            return
        if colors is None:
            colors = ['#58C4DD', '#FF6B6B', '#83C167']
        if sizes is None:
            sizes = [radius] * n
        objects = []
        # Circle positions
        if n == 2:
            sep = radius * 0.7
            positions = [(x - sep / 2, y), (x + sep / 2, y)]
        else:
            sep = radius * 0.65
            ang120 = 2 * math.pi / 3
            positions = [(x + sep * math.cos(math.pi / 2 + i * ang120),
                          y - sep * math.sin(math.pi / 2 + i * ang120))
                         for i in range(3)]
        for i, (cx, cy) in enumerate(positions):
            c = Circle(r=sizes[i], cx=cx, cy=cy,
                       fill=colors[i % len(colors)], fill_opacity=0.25,
                       stroke=colors[i % len(colors)], stroke_width=2,
                       creation=creation, z=z)
            objects.append(c)
        # Labels outside circles
        for i, (cx, cy) in enumerate(positions):
            if n == 2:
                lx = cx + (-1 if i == 0 else 1) * sizes[i] * 0.5
                ly = cy - sizes[i] - 15
            else:
                dx = cx - x
                dy = cy - y
                dist = math.hypot(dx, dy) or 1
                lx = cx + dx / dist * (sizes[i] + 20)
                ly = cy + dy / dist * (sizes[i] + 20) + font_size * 0.35
            lbl = Text(text=str(labels[i]), x=lx, y=ly,
                       font_size=font_size, fill=colors[i % len(colors)],
                       stroke_width=0, text_anchor='middle',
                       creation=creation, z=z + 0.1)
            objects.append(lbl)
        super().__init__(*objects, creation=creation, z=z)


class OrgChart(VCollection):
    """Organization chart from a tree structure.

    root: (label, [children]) where children are the same structure.
    Example: ('CEO', [('CTO', [('Dev', [])]), ('CFO', [])])
    """
    def __init__(self, root, x=960, y=80, h_spacing=180, v_spacing=100,
                 box_width=120, box_height=40, font_size=16,
                 colors=None, creation=0, z=0):
        if colors is None:
            colors = ['#58C4DD', '#83C167', '#FF6B6B', '#FFFF00',
                      '#FF79C6', '#B8BB26', '#BD93F9', '#FFB86C']
        # Layout: BFS to compute positions
        levels = []
        queue = [(root, 0)]
        while queue:
            node, depth = queue.pop(0)
            while len(levels) <= depth:
                levels.append([])
            levels[depth].append(node)
            label, children = node
            for child in children:
                queue.append((child, depth + 1))
        # Assign x positions per level
        positions = {}
        for depth, nodes in enumerate(levels):
            total_w = len(nodes) * h_spacing
            start_x = x - total_w / 2 + h_spacing / 2
            for i, node in enumerate(nodes):
                nx = start_x + i * h_spacing
                ny = y + depth * v_spacing
                positions[id(node)] = (nx, ny)
        objects = []
        # Draw connections then boxes (so boxes are on top)
        self._draw_tree(root, positions, objects, colors, 0,
                        box_width, box_height, font_size, creation, z)
        super().__init__(*objects, creation=creation, z=z)

    def _draw_tree(self, node, positions, objects, colors, depth,
                   box_width, box_height, font_size, creation, z):
        label, children = node
        nx, ny = positions[id(node)]
        color = colors[depth % len(colors)]
        # Connection lines to children
        for child in children:
            cx, cy = positions[id(child)]
            mid_y = ny + box_height / 2 + (cy - ny - box_height / 2) / 2
            # L-shaped connector: down, across, down
            d = (f'M{nx:.1f},{ny + box_height:.1f} '
                 f'L{nx:.1f},{mid_y:.1f} '
                 f'L{cx:.1f},{mid_y:.1f} '
                 f'L{cx:.1f},{cy:.1f}')
            conn = Path(d, stroke='#666', stroke_width=1.5,
                        fill_opacity=0, creation=creation, z=z)
            objects.append(conn)
        # Box
        from vectormation._shapes import RoundedRectangle
        rect = RoundedRectangle(width=box_width, height=box_height,
                                 x=nx - box_width / 2, y=ny,
                                 corner_radius=6, fill=color, fill_opacity=0.85,
                                 stroke=color, stroke_width=1,
                                 creation=creation, z=z + 0.1)
        objects.append(rect)
        # Label
        lbl = Text(text=str(label), x=nx, y=ny + box_height / 2 + font_size * 0.35,
                   font_size=font_size, fill='#fff', stroke_width=0,
                   text_anchor='middle', creation=creation, z=z + 0.2)
        objects.append(lbl)
        for child in children:
            self._draw_tree(child, positions, objects, colors, depth + 1,
                            box_width, box_height, font_size, creation, z)


class KPICard(VCollection):
    """Metric card showing a title, large value, optional subtitle and trend sparkline.

    title: metric name.  value: displayed value string.
    """
    def __init__(self, title, value, subtitle=None, trend_data=None,
                 x=100, y=100, width=280, height=160,
                 bg_color='#1a1a2e', title_color='#aaa', value_color='#fff',
                 font_size=48, creation=0, z=0):
        objects = []
        # Background card
        from vectormation._shapes import RoundedRectangle
        bg = RoundedRectangle(width=width, height=height, x=x, y=y,
                               corner_radius=10, fill=bg_color, fill_opacity=0.9,
                               stroke='#333', stroke_width=1,
                               creation=creation, z=z)
        objects.append(bg)
        # Title
        t_lbl = Text(text=str(title), x=x + width / 2, y=y + 30,
                     font_size=font_size * 0.35, fill=title_color, stroke_width=0,
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
                         y=y + height * 0.5 + font_size * 0.3 + font_size * 0.6,
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
                 font_size=16, max_val=None, creation=0, z=0):
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
            lbl = Text(text=str(label), x=x - 10, y=y + height / 2 + font_size * 0.35,
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
                 creation=0, z=0):
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
                 cell_size=20, gap=3, font_size=14, creation=0, z=0):
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


class MindMap(VCollection):
    """Radial mind map diagram.

    root: (label, [children]) where children have the same structure.
    """
    def __init__(self, root, cx=960, cy=540, radius=250, font_size=18,
                 colors=None, creation=0, z=0):
        if colors is None:
            colors = ['#58C4DD', '#83C167', '#FF6B6B', '#FFFF00',
                      '#FF79C6', '#B8BB26', '#BD93F9', '#FFB86C']
        objects = []
        root_label, children = root
        # Central node
        root_dot = Circle(r=35, cx=cx, cy=cy, fill=colors[0], fill_opacity=0.9,
                          stroke=colors[0], stroke_width=2, creation=creation, z=z + 0.2)
        objects.append(root_dot)
        root_txt = Text(text=str(root_label), x=cx, y=cy + font_size * 0.35,
                        font_size=font_size, fill='#fff', stroke_width=0,
                        text_anchor='middle', creation=creation, z=z + 0.3)
        objects.append(root_txt)
        if not children:
            super().__init__(*objects, creation=creation, z=z)
            return
        n = len(children)
        for i, (child_label, grandchildren) in enumerate(children):
            angle = 2 * math.pi * i / n - math.pi / 2
            bx = cx + radius * math.cos(angle)
            by = cy + radius * math.sin(angle)
            color = colors[(i + 1) % len(colors)]
            # Branch line
            line = Line(x1=cx, y1=cy, x2=bx, y2=by, stroke=color,
                        stroke_width=2, stroke_opacity=0.5,
                        creation=creation, z=z)
            objects.append(line)
            # Branch node
            br = 25
            bdot = Circle(r=br, cx=bx, cy=by, fill=color, fill_opacity=0.85,
                          stroke=color, stroke_width=1.5, creation=creation, z=z + 0.2)
            objects.append(bdot)
            btxt = Text(text=str(child_label), x=bx, y=by + font_size * 0.3,
                        font_size=font_size * 0.85, fill='#fff', stroke_width=0,
                        text_anchor='middle', creation=creation, z=z + 0.3)
            objects.append(btxt)
            # Grandchildren as smaller nodes
            if grandchildren:
                gn = len(grandchildren)
                spread = math.pi * 0.6
                base_angle = angle - spread / 2
                for j, (gc_label, _) in enumerate(grandchildren):
                    ga = base_angle + spread * j / max(gn - 1, 1)
                    gx = bx + radius * 0.5 * math.cos(ga)
                    gy = by + radius * 0.5 * math.sin(ga)
                    gl = Line(x1=bx, y1=by, x2=gx, y2=gy, stroke=color,
                              stroke_width=1, stroke_opacity=0.4,
                              creation=creation, z=z)
                    objects.append(gl)
                    gdot = Dot(cx=gx, cy=gy, r=15, fill=color, fill_opacity=0.7,
                               stroke_width=0, creation=creation, z=z + 0.2)
                    objects.append(gdot)
                    gtxt = Text(text=str(gc_label), x=gx, y=gy + font_size * 0.25,
                                font_size=font_size * 0.65, fill='#ddd', stroke_width=0,
                                text_anchor='middle', creation=creation, z=z + 0.3)
                    objects.append(gtxt)
        super().__init__(*objects, creation=creation, z=z)


class CircularProgressBar(VCollection):
    """Circular progress indicator with percentage text.

    value: 0-100 (percent complete).
    """
    def __init__(self, value, x=960, y=540, radius=80, stroke_width=12,
                 track_color='#2a2a3a', bar_color='#58C4DD',
                 font_size=36, show_text=True, creation=0, z=0):
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
            lbl = Text(text=f'{pct:.0f}%', x=x, y=y + font_size * 0.35,
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
                 font_size=28, cols=None, creation=0, z=0):
        if not entries:
            super().__init__(creation=creation, z=z)
            return
        if cols is None:
            cols = min(len(entries), 4)
        rows_count = math.ceil(len(entries) / cols)
        total_w = cols * col_width
        total_h = rows_count * row_height
        from vectormation._shapes import RoundedRectangle
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
                 creation=0, z=0):
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
                                x=rx + cell_size / 2, y=ry + cell_size / 2 + font_size * 0.35,
                                font_size=font_size * 0.8, fill='#fff', stroke_width=0,
                                text_anchor='middle', creation=creation, z=z + 0.1)
                    objects.append(vlbl)
        # Row labels
        if row_labels:
            for r, label in enumerate(row_labels[:n_rows]):
                ry = y + col_offset + r * (cell_size + gap)
                lbl = Text(text=str(label), x=x + label_offset - 8,
                           y=ry + cell_size / 2 + font_size * 0.35,
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
                 font_size=12, creation=0, z=0):
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


class TextBox(VCollection):
    """Text with a surrounding rectangle. Useful for labels and callouts.

    text: string to display.
    Sizing: padding around the text, auto-computed from font_size if width/height not given.
    """
    def __init__(self, text, x=100, y=100, font_size=20, padding=12,
                 width=None, height=None, corner_radius=6,
                 box_fill='#333', box_opacity=0.9, text_color='#fff',
                 creation=0, z=0, **styling_kwargs):
        char_w = font_size * 0.6
        if width is None:
            width = len(text) * char_w + padding * 2
        if height is None:
            height = font_size + padding * 2
        from vectormation._shapes import RoundedRectangle
        box = RoundedRectangle(width=width, height=height, x=x, y=y,
                                corner_radius=corner_radius,
                                fill=box_fill, fill_opacity=box_opacity,
                                stroke_width=0, creation=creation, z=z,
                                **styling_kwargs)
        lbl = Text(text=text, x=x + width / 2, y=y + height / 2 + font_size * 0.35,
                   font_size=font_size, fill=text_color, stroke_width=0,
                   text_anchor='middle', creation=creation, z=z + 0.1)
        super().__init__(box, lbl, creation=creation, z=z)
        self.box = box
        self.label = lbl


class Bracket(VCollection):
    """Square bracket decoration pointing at a range.

    direction: 'up', 'down', 'left', 'right' — which way the bracket opens.
    """
    def __init__(self, x=100, y=100, width=100, height=20,
                 direction='down', stroke='#fff', stroke_width=2,
                 text='', font_size=16, text_color='#aaa',
                 creation=0, z=0):
        tip = height
        if direction in ('down', 'up'):
            sign = 1 if direction == 'down' else -1
            bracket = Lines(
                (x, y), (x, y + sign * tip),
                (x + width, y + sign * tip), (x + width, y),
                stroke=stroke, stroke_width=stroke_width,
                fill_opacity=0, creation=creation, z=z)
            tx, ty = x + width / 2, y + sign * (tip + font_size + 4)
        else:
            sign = 1 if direction == 'right' else -1
            bracket = Lines(
                (x, y), (x + sign * tip, y),
                (x + sign * tip, y + width), (x, y + width),
                stroke=stroke, stroke_width=stroke_width,
                fill_opacity=0, creation=creation, z=z)
            tx, ty = x + sign * (tip + font_size), y + width / 2
        objects = [bracket]
        if text:
            lbl = Text(text=text, x=tx, y=ty + font_size * 0.35,
                       font_size=font_size, fill=text_color, stroke_width=0,
                       text_anchor='middle', creation=creation, z=z + 0.1)
            objects.append(lbl)
        super().__init__(*objects, creation=creation, z=z)


class IconGrid(VCollection):
    """Grid of colored shapes (circles, squares) for infographic-style visualizations.

    data: list of (count, color) tuples.
    shape: 'circle' or 'square'.
    """
    def __init__(self, data, x=100, y=100, cols=10, size=15, gap=3,
                 shape='circle', creation=0, z=0):
        objects = []
        idx = 0
        # Flatten data into a list of colors
        colors = []
        for count, color in data:
            colors.extend([color] * count)
        for i, color in enumerate(colors):
            r = i // cols
            c = i % cols
            px = x + c * (size + gap)
            py = y + r * (size + gap)
            if shape == 'circle':
                obj = Dot(cx=px + size / 2, cy=py + size / 2, r=size / 2,
                          fill=color, stroke_width=0, creation=creation, z=z)
            else:
                obj = Rectangle(width=size, height=size, x=px, y=py,
                                fill=color, stroke_width=0, creation=creation, z=z)
            objects.append(obj)
        super().__init__(*objects, creation=creation, z=z)


class SpeechBubble(VCollection):
    """Rounded rectangle with a triangular tail, useful for dialogue/annotations.

    text: string to display inside.
    tail_direction: 'down', 'up', 'left', 'right' — where the tail points.
    tail_width: width of the tail base.
    tail_height: length of the tail.
    """
    def __init__(self, text='', x=100, y=100, font_size=20, padding=14,
                 width=None, height=None, corner_radius=10,
                 box_fill='#1e1e2e', box_opacity=0.95, text_color='#fff',
                 tail_direction='down', tail_width=20, tail_height=18,
                 creation=0, z=0, **styling_kwargs):
        from vectormation._shapes import RoundedRectangle, Text as SText
        char_w = font_size * 0.6
        if width is None:
            width = max(len(text) * char_w + padding * 2, 60)
        if height is None:
            height = font_size + padding * 2
        box_kw = {'stroke': '#555', 'stroke_width': 1} | styling_kwargs
        box = RoundedRectangle(width=width, height=height, x=x, y=y,
                               corner_radius=corner_radius,
                               fill=box_fill, fill_opacity=box_opacity,
                               creation=creation, z=z, **box_kw)
        cx, cy = x + width / 2, y + height / 2
        hw, hh = tail_width / 2, tail_height
        if tail_direction == 'down':
            pts = [(cx - hw, y + height), (cx + hw, y + height), (cx, y + height + hh)]
        elif tail_direction == 'up':
            pts = [(cx - hw, y), (cx + hw, y), (cx, y - hh)]
        elif tail_direction == 'left':
            pts = [(x, cy - hw), (x, cy + hw), (x - hh, cy)]
        else:  # right
            pts = [(x + width, cy - hw), (x + width, cy + hw), (x + width + hh, cy)]
        tail = Polygon(*pts, fill=box_fill, fill_opacity=box_opacity,
                       stroke=box_fill, stroke_width=1, creation=creation, z=z - 0.1)
        lbl = SText(text=text, x=cx, y=cy + font_size * 0.35,
                    font_size=font_size, fill=text_color, stroke_width=0,
                    text_anchor='middle', creation=creation, z=z + 0.1)
        super().__init__(tail, box, lbl, creation=creation, z=z)
        self.box = box
        self.tail = tail
        self.label = lbl


class Badge(VCollection):
    """Pill-shaped label (fully rounded corners), like GitHub badges/tags.

    text: string to display.
    bg_color: background fill color.
    """
    def __init__(self, text='Label', x=100, y=100, font_size=16, padding_x=14,
                 padding_y=6, bg_color='#58C4DD', text_color='#000',
                 creation=0, z=0, **styling_kwargs):
        from vectormation._shapes import RoundedRectangle, Text as SText
        char_w = font_size * 0.6
        width = len(text) * char_w + padding_x * 2
        height = font_size + padding_y * 2
        corner_radius = height / 2  # fully rounded = pill shape
        box = RoundedRectangle(width=width, height=height, x=x, y=y,
                               corner_radius=corner_radius,
                               fill=bg_color, fill_opacity=1,
                               stroke_width=0, creation=creation, z=z,
                               **styling_kwargs)
        lbl = SText(text=text, x=x + width / 2, y=y + height / 2 + font_size * 0.35,
                    font_size=font_size, fill=text_color, stroke_width=0,
                    text_anchor='middle', creation=creation, z=z + 0.1)
        super().__init__(box, lbl, creation=creation, z=z)
        self.box = box
        self.label = lbl


class Divider(VCollection):
    """Horizontal or vertical line with an optional centered text label.

    direction: 'horizontal' or 'vertical'.
    length: total line length in pixels.
    label: optional text to center on the divider (splits the line).
    """
    def __init__(self, x=100, y=300, length=400, direction='horizontal',
                 label=None, font_size=16, gap=12,
                 creation=0, z=0, **styling_kwargs):
        from vectormation._shapes import Text as SText, Line as SLine
        style_kw = {'stroke': '#555', 'stroke_width': 1} | styling_kwargs
        objects = []
        if label:
            char_w = font_size * 0.6
            label_w = len(label) * char_w + gap * 2
            if direction == 'horizontal':
                half = (length - label_w) / 2
                l1 = SLine(x1=x, y1=y, x2=x + half, y2=y,
                           creation=creation, z=z, **style_kw)
                l2 = SLine(x1=x + half + label_w, y1=y, x2=x + length, y2=y,
                           creation=creation, z=z, **style_kw)
                lbl = SText(text=label, x=x + length / 2, y=y + font_size * 0.35,
                            font_size=font_size, fill=style_kw.get('stroke', '#555'),
                            stroke_width=0, text_anchor='middle',
                            creation=creation, z=z + 0.1)
            else:
                half = (length - label_w) / 2
                l1 = SLine(x1=x, y1=y, x2=x, y2=y + half,
                           creation=creation, z=z, **style_kw)
                l2 = SLine(x1=x, y1=y + half + label_w, x2=x, y2=y + length,
                           creation=creation, z=z, **style_kw)
                lbl = SText(text=label, x=x, y=y + length / 2 + font_size * 0.35,
                            font_size=font_size, fill=style_kw.get('stroke', '#555'),
                            stroke_width=0, text_anchor='middle',
                            creation=creation, z=z + 0.1)
            objects = [l1, l2, lbl]
        else:
            if direction == 'horizontal':
                ln = SLine(x1=x, y1=y, x2=x + length, y2=y,
                           creation=creation, z=z, **style_kw)
            else:
                ln = SLine(x1=x, y1=y, x2=x, y2=y + length,
                           creation=creation, z=z, **style_kw)
            objects = [ln]
        super().__init__(*objects, creation=creation, z=z)


class Checklist(VCollection):
    """List of items with checkbox indicators (checked or unchecked).

    items: list of (text, checked) tuples, or just strings (all unchecked).
    check_color: fill color for checked boxes.
    uncheck_color: fill color for unchecked boxes.
    """
    def __init__(self, *items, x=100, y=100, font_size=24, spacing=1.6,
                 box_size=None, check_color='#83C167', uncheck_color='#555',
                 text_color='#fff', creation=0, z=0):
        from vectormation._shapes import RoundedRectangle, Text as SText
        if box_size is None:
            box_size = font_size * 0.75
        objects = []
        self._boxes = []
        self._labels = []
        for i, item in enumerate(items):
            if isinstance(item, str):
                label_text, checked = item, False
            else:
                label_text, checked = item
            ly = y + i * font_size * spacing
            fill = check_color if checked else uncheck_color
            box = RoundedRectangle(width=box_size, height=box_size,
                                   x=x, y=ly, corner_radius=3,
                                   fill=fill, fill_opacity=0.9, stroke_width=0,
                                   creation=creation, z=z)
            # Checkmark or empty
            mark = SText(text='\u2713' if checked else '',
                         x=x + box_size / 2, y=ly + box_size * 0.8,
                         font_size=font_size * 0.7, fill='#fff', stroke_width=0,
                         text_anchor='middle', creation=creation, z=z + 0.1)
            lbl = SText(text=label_text, x=x + box_size + 10,
                        y=ly + box_size * 0.75,
                        font_size=font_size, fill=text_color, stroke_width=0,
                        creation=creation, z=z)
            objects.extend([box, mark, lbl])
            self._boxes.append(box)
            self._labels.append(lbl)
        super().__init__(*objects, creation=creation, z=z)


class Stepper(VCollection):
    """Step indicator: numbered circles connected by a line, with active step highlight.

    steps: list of step labels (strings), or int for numbered steps.
    active: 0-based index of the currently active step.
    """
    def __init__(self, steps, x=100, y=300, spacing=150, radius=20,
                 active=0, direction='horizontal', font_size=16,
                 active_color='#58C4DD', inactive_color='#555',
                 text_color='#fff', creation=0, z=0):
        if isinstance(steps, int):
            steps = [str(i + 1) for i in range(steps)]
        objects = []
        self._circles = []
        n = len(steps)
        for i, label in enumerate(steps):
            if direction == 'horizontal':
                cx, cy = x + i * spacing, y
            else:
                cx, cy = x, y + i * spacing
            fill = active_color if i <= active else inactive_color
            circ = Circle(cx=cx, cy=cy, r=radius,
                          fill=fill, fill_opacity=1, stroke_width=0,
                          creation=creation, z=z + 1)
            lbl = Text(text=label, x=cx, y=cy + font_size * 0.35,
                       font_size=font_size, fill=text_color, stroke_width=0,
                       text_anchor='middle', creation=creation, z=z + 2)
            objects.extend([circ, lbl])
            self._circles.append(circ)
            # Connecting line to next step
            if i < n - 1:
                if direction == 'horizontal':
                    nx, ny = x + (i + 1) * spacing, y
                    lx1, ly1, lx2, ly2 = cx + radius, cy, nx - radius, ny
                else:
                    nx, ny = x, y + (i + 1) * spacing
                    lx1, ly1, lx2, ly2 = cx, cy + radius, nx, ny - radius
                line_color = active_color if i < active else inactive_color
                conn = Line(x1=lx1, y1=ly1, x2=lx2, y2=ly2,
                            stroke=line_color, stroke_width=2,
                            creation=creation, z=z)
                objects.append(conn)
        super().__init__(*objects, creation=creation, z=z)


class TagCloud(VCollection):
    """Word/tag cloud with varying font sizes based on weights.

    data: list of (text, weight) tuples. Higher weight = larger font.
    """
    def __init__(self, data, x=100, y=100, width=500, min_font=14, max_font=48,
                 colors=None, creation=0, z=0):
        if colors is None:
            colors = ['#58C4DD', '#83C167', '#FF6B6B', '#FFFF00',
                      '#FF79C6', '#BD93F9', '#F1FA8C', '#8BE9FD']
        if not data:
            super().__init__(creation=creation, z=z)
            return
        weights = [w for _, w in data]
        wmin, wmax = min(weights), max(weights)
        wrange = wmax - wmin if wmax > wmin else 1
        objects = []
        cx, cy = x, y
        row_height = 0
        for i, (text, weight) in enumerate(data):
            frac = (weight - wmin) / wrange
            fs = min_font + frac * (max_font - min_font)
            char_w = fs * 0.6
            tw = len(text) * char_w + 12  # word width + gap
            # Wrap to next row if exceeding width
            if cx + tw > x + width and cx > x:
                cx = x
                cy += row_height + 8
                row_height = 0
            color = colors[i % len(colors)]
            lbl = Text(text=text, x=cx, y=cy + fs,
                       font_size=fs, fill=color, stroke_width=0,
                       creation=creation, z=z)
            objects.append(lbl)
            cx += tw
            row_height = max(row_height, fs + 4)
        super().__init__(*objects, creation=creation, z=z)


class StatusIndicator(VCollection):
    """Colored dot with a text label, like a server/service status indicator.

    status: 'online', 'offline', 'warning', or a custom color string.
    """
    _STATUS_COLORS = {
        'online': '#83C167', 'ok': '#83C167', 'success': '#83C167',
        'offline': '#FF6B6B', 'error': '#FF6B6B', 'fail': '#FF6B6B',
        'warning': '#FFFF00', 'warn': '#FFFF00',
        'pending': '#888', 'unknown': '#888',
    }

    def __init__(self, label, status='online', x=100, y=100, font_size=18,
                 dot_radius=6, gap=10, creation=0, z=0):
        color = self._STATUS_COLORS.get(status, status)
        dot = Dot(cx=x + dot_radius, cy=y, r=dot_radius,
                  fill=color, stroke_width=0, creation=creation, z=z)
        lbl = Text(text=label, x=x + dot_radius * 2 + gap, y=y + font_size * 0.35,
                   font_size=font_size, fill='#fff', stroke_width=0,
                   creation=creation, z=z)
        super().__init__(dot, lbl, creation=creation, z=z)
        self.dot = dot
        self.label = lbl


class Meter(VCollection):
    """Vertical or horizontal bar meter (like a battery level or VU meter).

    value: current level (0.0 to 1.0).
    """
    def __init__(self, value=0.5, x=100, y=100, width=30, height=150,
                 direction='vertical', fill_color='#58C4DD',
                 bg_color='#333', border_color='#888',
                 creation=0, z=0):
        from vectormation._shapes import RoundedRectangle
        bg = RoundedRectangle(width=width, height=height, x=x, y=y,
                              corner_radius=3, fill=bg_color, fill_opacity=0.8,
                              stroke=border_color, stroke_width=1,
                              creation=creation, z=z)
        value = max(0.0, min(1.0, value))
        if direction == 'vertical':
            fh = height * value
            fill_rect = Rectangle(width=width - 4, height=fh,
                                  x=x + 2, y=y + height - fh - 2,
                                  fill=fill_color, fill_opacity=0.9,
                                  stroke_width=0, creation=creation, z=z + 0.1)
        else:
            fw = width * value
            fill_rect = Rectangle(width=fw, height=height - 4,
                                  x=x + 2, y=y + 2,
                                  fill=fill_color, fill_opacity=0.9,
                                  stroke_width=0, creation=creation, z=z + 0.1)
        super().__init__(bg, fill_rect, creation=creation, z=z)
        self.bg = bg
        self.fill_rect = fill_rect


class Breadcrumb(VCollection):
    """Navigation breadcrumb trail (e.g., Home > Products > Details).

    items: list of breadcrumb strings.
    separator: character between items.
    active_index: index of the active/current item (highlighted).
    """
    def __init__(self, *items, x=100, y=100, font_size=18, separator='\u203a',
                 gap=8, active_index=None, active_color='#58C4DD',
                 inactive_color='#888', creation=0, z=0):
        objects = []
        cx = x
        if active_index is None:
            active_index = len(items) - 1
        for i, item in enumerate(items):
            color = active_color if i == active_index else inactive_color
            lbl = Text(text=item, x=cx, y=y,
                       font_size=font_size, fill=color, stroke_width=0,
                       creation=creation, z=z)
            objects.append(lbl)
            cx += len(item) * font_size * 0.6 + gap
            if i < len(items) - 1:
                sep = Text(text=separator, x=cx, y=y,
                           font_size=font_size, fill=inactive_color, stroke_width=0,
                           creation=creation, z=z)
                objects.append(sep)
                cx += font_size * 0.6 + gap
        super().__init__(*objects, creation=creation, z=z)


def parse_args():
    """Parse common CLI arguments for VectorMation scripts."""
    import argparse
    parser = argparse.ArgumentParser(description='VectorMation animation script')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--port', type=int, default=8765, help='Browser viewer port')
    parser.add_argument('--fps', type=int, default=60, help='Frames per second')
    parser.add_argument('--no-display', action='store_true', help='Skip browser display')
    return parser.parse_args()

