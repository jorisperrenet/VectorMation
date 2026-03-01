"""Axes, Graph, NumberPlane, and ComplexPlane classes."""
import math

import vectormation.easings as easings
import vectormation.attributes as attributes
from vectormation._constants import (
    CANVAS_WIDTH, CANVAS_HEIGHT, UNIT, SMALL_BUFF, DEFAULT_FONT_SIZE, TEXT_Y_OFFSET, ORIGIN,
    _sample_function, _normalize,
)
from vectormation._base import VObject, VCollection, _lerp
from vectormation._base_helpers import _clamp01, _lerp_point, _norm_dir
from vectormation._collection import _scale_transform
from vectormation._axes_helpers import (
    _CURVE_STYLE, _AREA_STYLE, _HIGHLIGHT_STYLE,
    _get_arrow, _get_dynamic_object, _get_tex_object,
    _nice_ticks, _build_axes_decoration,
    _TICK_FONT_SIZE, _LABEL_GAP,
    pi_format, pi_ticks, pi_tex_format,
    log_tex_format, scientific_format, engineering_format,
    percent_format, degree_format,
)

from vectormation._shapes import (
    Dot, Rectangle, RoundedRectangle, Line,
    Text, Path,
)
from vectormation._axes_ext import _AxesExtMixin

class Axes(_AxesExtMixin, VCollection):
    """Coordinate axes with ticks and labels."""
    x_min: attributes.Real
    x_max: attributes.Real
    y_min: 'attributes.Real | None'
    y_max: 'attributes.Real | None'
    # Mapping from tick_type string to (format_func, ticks_func_or_None, tex_ticks_bool)
    _TICK_TYPES = {
        'pi':          (pi_format,          pi_ticks, False),
        'pi_tex':      (pi_tex_format,      pi_ticks, True),
        'log_tex':     (log_tex_format,     None,     True),
        'scientific':  (scientific_format,  None,     False),
        'engineering': (engineering_format, None,     False),
        'percent':     (percent_format,     None,     False),
        'degree':      (degree_format,      None,     False),
    }

    def __init__(self, x_range=(-5, 5), y_range=None,
                 x: float = 260, y: float = 100, plot_width: float = 1400, plot_height: float = 880,
                 x_label=None, y_label=None,
                 show_grid=False, equal_aspect=False,
                 x_scale='linear', y_scale='linear',
                 tick_format=None, x_tick_format=None, y_tick_format=None,
                 x_ticks=None, y_ticks=None,
                 tex_ticks=False,
                 x_tick_type=None, y_tick_type=None,
                 creation: float = 0, z: float = 0):
        """
        Args:
            x_tick_type: Shorthand tick preset for the x-axis.  One of
                'pi', 'pi_tex', 'log_tex', 'scientific', 'engineering',
                'percent', 'degree'.  Overrides *x_tick_format* and *x_ticks*
                when set.
            y_tick_type: Same as *x_tick_type* but for the y-axis.
        """
        # Resolve tick_type shortcuts into tick_format / ticks / tex_ticks
        for axis, tick_type in [('x', x_tick_type), ('y', y_tick_type)]:
            if tick_type is None:
                continue
            if tick_type not in self._TICK_TYPES:
                raise ValueError(
                    f"Unknown {axis}_tick_type {tick_type!r}. "
                    f"Choose from {sorted(self._TICK_TYPES)}.")
            fmt_func, ticks_func, needs_tex = self._TICK_TYPES[tick_type]
            if axis == 'x':
                x_tick_format = fmt_func
                if ticks_func is not None:
                    x_ticks = ticks_func(x_range[0], x_range[1])
            else:
                y_tick_format = fmt_func
                if ticks_func is not None and y_range is not None:
                    y_ticks = ticks_func(y_range[0], y_range[1])
            if needs_tex:
                tex_ticks = True

        self.x_min = attributes.Real(creation, x_range[0])
        self.x_max = attributes.Real(creation, x_range[1])
        if equal_aspect and y_range is not None and x_range[1] != x_range[0]:
            plot_height = int(plot_width * (y_range[1] - y_range[0])
                              / (x_range[1] - x_range[0]))
            y = (CANVAS_HEIGHT - plot_height) // 2
        self.plot_x, self.plot_y = x, y
        self.plot_width, self.plot_height = plot_width, plot_height
        self.num_points = 200
        self._show_grid = show_grid
        self._x_scale = x_scale  # 'linear' or 'log'
        self._y_scale = y_scale  # 'linear' or 'log'
        self._tick_format = tick_format  # None, callable, or format string
        self._x_tick_format = x_tick_format
        self._y_tick_format = y_tick_format
        self._x_ticks = x_ticks  # None or list of tick values
        self._y_ticks = y_ticks
        self._tex_ticks = tex_ticks  # render tick labels as TeX objects

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

        self.axes = _get_dynamic_object()(self._build_axes_at, creation=creation, z=z)

    def _build_label_objects(self, x_label, y_label, creation, z):
        """Build axis title TexObjects (x_label, y_label) with dynamic position."""
        objects = []
        for label_text, is_x in [(x_label, True), (y_label, False)]:
            if not label_text:
                continue
            tex = label_text if '$' in label_text else f'${label_text}$'
            lbl = _get_tex_object()(tex, font_size=DEFAULT_FONT_SIZE, creation=creation, z=z,
                            fill='#fff', stroke_width=0)
            _, _, lw, lh = lbl.bbox(creation)
            if is_x:
                lbl.x.set_onward(creation, self.plot_x + self.plot_width + _LABEL_GAP)
                lbl.y.set_onward(creation, lambda t, _lh=lh: self._baseline_y(t) - _lh / 2)
            else:
                def _cx_y(t):
                    xmin = self.x_min.at_time(t)
                    xmax = self.x_max.at_time(t)
                    return self.plot_x + (0 - xmin) / (xmax - xmin) * self.plot_width if xmin <= 0 <= xmax and xmax != xmin else self.plot_x
                lbl.x.set_onward(creation, lambda t, _lw=lw: _cx_y(t) - _lw / 2)
                lbl.y.set_onward(creation, self.plot_y - _LABEL_GAP - lh)
            objects.append(lbl)
        return objects

    def __repr__(self):
        xn, xx = self.x_min.at_time(0), self.x_max.at_time(0)
        if self.y_min is not None:
            yn, yx = self.y_min.at_time(0), self.y_max.at_time(0)
            return f'Axes(x=[{xn:.1f}, {xx:.1f}], y=[{yn:.1f}, {yx:.1f}])'
        return f'Axes(x=[{xn:.1f}, {xx:.1f}])'

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
            self._show_grid, time, self._x_scale, self._y_scale, self._tick_format,
            x_tick_format=self._x_tick_format, y_tick_format=self._y_tick_format,
            x_ticks=self._x_ticks, y_ticks=self._y_ticks,
            tex_ticks=self._tex_ticks)
        # Include the persistent axis title labels (TexObjects created once)
        for lbl in self._axis_labels:
            coll.objects.append(lbl)
        return coll

    def _get_bounds(self, time: float = 0):
        """Return (xmin, xmax, ymin, ymax) at the given time."""
        return (self.x_min.at_time(time), self.x_max.at_time(time),
                self.y_min.at_time(time), self.y_max.at_time(time))

    def get_plot_area(self):
        """Return (plot_x, plot_y, plot_width, plot_height) for the SVG plot region."""
        return (self.plot_x, self.plot_y, self.plot_width, self.plot_height)

    def _math_to_svg_x(self, val, time: float = 0):
        xmin, xmax = self.x_min.at_time(time), self.x_max.at_time(time)
        if self._x_scale == 'log':
            if val <= 0 or xmin <= 0 or xmax <= 0:
                return self.plot_x
            val, xmin, xmax = math.log10(val), math.log10(xmin), math.log10(xmax)
        span = xmax - xmin
        if span == 0:
            span = 1
        return self.plot_x + (val - xmin) / span * self.plot_width

    def _math_to_svg_y(self, val, time: float = 0):
        ymin, ymax = self.y_min.at_time(time), self.y_max.at_time(time)
        if self._y_scale == 'log':
            if val <= 0 or ymin <= 0 or ymax <= 0:
                return self.plot_y + self.plot_height
            val, ymin, ymax = math.log10(val), math.log10(ymin), math.log10(ymax)
        span = ymax - ymin
        if span == 0:
            span = 1
        return self.plot_y + (1 - (val - ymin) / span) * self.plot_height

    def _baseline_y(self, time: float = 0):
        """SVG y-coordinate of y=0 (or bottom edge if 0 is out of range)."""
        ymin, ymax = self.y_min.at_time(time), self.y_max.at_time(time)
        if ymin <= 0 <= ymax and ymax != ymin:
            return self.plot_y + (1 - (0 - ymin) / (ymax - ymin)) * self.plot_height
        return self.plot_y + self.plot_height

    def _make_curve(self, func, creation, z, num_points=None, x_range=None,
                    lincl=True, rincl=True, **style_kwargs):
        """Create a Path whose 'd' attribute resamples func each frame."""
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
                def _in_domain(x, _lo=lo, _hi=hi, _li=lincl, _ri=rincl):
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
        visible = [((z.at_time(time) if (z := getattr(o, 'z', None)) is not None else 0), o)
                    for o in self.objects if o.show.at_time(time)]
        for _, obj in sorted(visible, key=lambda x: x[0]):
            parts.append(obj.to_svg(time))

        inner = '\n'.join(parts)
        transform = _scale_transform(self._scale_x.at_time(time),
                                     self._scale_y.at_time(time), self._scale_origin)
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
                     creation: float = 0, z: float = 0, **styling_kwargs):
        """Add a function curve to these axes. Returns the Path object."""
        if 'color' in styling_kwargs:
            styling_kwargs.setdefault('stroke', styling_kwargs.pop('color'))
        if hasattr(self, '_deferred_axes'):
            self._build_deferred_axes(func, num_points)
        style_kw = _CURVE_STYLE | styling_kwargs
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

    def add_filled_curve(self, func, x_range=None, color='#58C4DD',
                         opacity: float = 0.3, start=0, end=None, reveal=True, **kwargs):
        """Plot a curve and its filled area underneath in one call."""
        curve_kwargs = {k: v for k, v in kwargs.items()
                        if k not in ('fill', 'fill_opacity')}
        curve = self.add_function(func, x_range=x_range, creation=start,
                                  stroke=color, **curve_kwargs)
        area = self.get_area(func, x_range=x_range, creation=start,
                             fill=color, fill_opacity=opacity, stroke_width=0)
        if reveal and end is not None and end > start:
            curve.draw_along(start, end)
            area.set_opacity(0, start=start)
            area.set_opacity(1, start=start, end=end)
        return VCollection(curve, area, creation=start)

    def add_parametric_plot(self, fx, fy, t_range=(0, 1), num_points: int = 100,
                            creation: float = 0, z: float = 0, **styling_kwargs):
        """Plot a parametric curve x=fx(t), y=fy(t). Returns a Path object."""
        if num_points < 1:
            num_points = 1
        if hasattr(self, '_deferred_axes'):
            # Sample fy over t_range (not x_range) to auto-detect y bounds
            t_min, t_max = t_range
            y_vals = [fy(t_min + (t_max - t_min) * i / num_points)
                      for i in range(num_points + 1)]
            y_vals = [v for v in y_vals if math.isfinite(v)]
            if y_vals:
                margin = (max(y_vals) - min(y_vals)) * 0.1 or 1.0
                y_lo = min(y_vals) - margin
                y_hi = max(y_vals) + margin
            else:
                y_lo, y_hi = -1, 1
            x_label, y_label, ax_creation, ax_z = self._deferred_axes
            self.y_min = attributes.Real(ax_creation, y_lo)
            self.y_max = attributes.Real(ax_creation, y_hi)
            self._axis_labels = self._build_label_objects(x_label, y_label, ax_creation, ax_z)
            del self._deferred_axes
        style_kw = _CURVE_STYLE | styling_kwargs
        curve = Path('', x=0, y=0, creation=creation, z=z, **style_kw)
        def _compute_d(time, _fx=fx, _fy=fy, _np=num_points,
                       _axes=self, _t_min=t_range[0], _t_max=t_range[1]):
            pts = []
            for i in range(_np + 1):
                t = _t_min + (_t_max - _t_min) * i / _np
                xv = _fx(t)
                yv = _fy(t)
                if not (math.isfinite(xv) and math.isfinite(yv)):
                    continue
                sx, sy = _axes.coords_to_point(xv, yv, time)
                pts.append(f'{sx},{sy}')
            if not pts:
                return ''
            return 'M' + 'L'.join(pts)

        curve.d.set_onward(creation, _compute_d)
        curve._func = None  # no single-variable function
        curve._num_points = num_points
        self._add_plot_obj(curve)
        return curve

    def plot_piecewise(self, pieces, creation: float = 0, **kwargs):
        """Plot a piecewise function defined by ``[(func, x_min, x_max), ...]``. Returns a VGroup."""
        from vectormation._base import VGroup
        curves = []
        for func, x_min, x_max in pieces:
            curve = self.add_function(func, x_range=(x_min, x_max),
                                      creation=creation, **kwargs)
            curves.append(curve)
        return VGroup(*curves)

    def animate_draw_function(self, func, start: float = 0, end: float = 1, x_range=None,
                               num_points=200, easing=easings.smooth,
                               creation: float = 0, z: float = 0, **styling_kwargs):
        """Draw a function curve progressively from left to right."""
        def _make_d(time, _axes=self, _x_range=x_range, _easing=easing):
            if _x_range:
                xmin, xmax = _x_range[0], _x_range[1]
            else:
                xmin = _axes.x_min.at_time(time)
                xmax = _axes.x_max.at_time(time)
            dur = end - start
            if dur <= 0:
                progress = 1.0
            else:
                progress = _easing(_clamp01((time - start) / dur))
            if progress <= 0:
                return ''
            xlo, xhi = min(xmin, xmax), max(xmin, xmax)
            cur_xhi = xlo + (xhi - xlo) * progress
            pts = []
            n = max(2, int(num_points * progress))
            for i in range(n + 1):
                xv = xlo + i * (cur_xhi - xlo) / n
                yv = func(xv)
                if not math.isfinite(yv):
                    continue
                sx, sy = _axes.coords_to_point(xv, yv, time)
                pts.append((sx, sy))
            if not pts:
                return ''
            return 'M' + 'L'.join(f'{sx},{sy}' for sx, sy in pts)

        defaults = {'stroke': '#58C4DD', 'stroke_width': 3, 'fill_opacity': 0} | styling_kwargs
        path = Path('', creation=creation, z=z, **defaults)
        path.d.set_onward(start, _make_d)
        self.objects.append(path)
        return path

    def add_coordinates(self, creation: float = 0, font_size=None, color='#aaa'):
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
            sy = self._math_to_svg_y(val, creation) + font_size * TEXT_Y_OFFSET
            lbl = Text(text=f'{val:g}', x=sx, y=sy, font_size=font_size,
                       text_anchor='end', fill=color, stroke_width=0, creation=creation)
            self._add_plot_obj(lbl)
        return self

    def add_grid(self):
        """Enable background grid lines on the axes."""
        self._show_grid = True
        return self

    def add_zero_line(self, axis='x', creation: float = 0, z: float = -1, **styling_kwargs):
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
        return self

    def set_x_range(self, x_min, x_max, start: float = 0):
        """Set the x-axis range from start time onward."""
        self.x_min.set_onward(start, x_min)
        self.x_max.set_onward(start, x_max)
        return self

    def set_y_range(self, y_min, y_max, start: float = 0):
        """Set the y-axis range from start time onward."""
        self.y_min.set_onward(start, y_min)
        self.y_max.set_onward(start, y_max)
        return self

    def animate_x_range(self, start, end, x_range, **kwargs):
        """Animate the x-axis range to new bounds."""
        self.x_min.move_to(start, end, x_range[0], **kwargs)
        self.x_max.move_to(start, end, x_range[1], **kwargs)
        return self

    def animate_y_range(self, start, end, y_range, **kwargs):
        """Animate the y-axis range to new bounds."""
        self.y_min.move_to(start, end, y_range[0], **kwargs)
        self.y_max.move_to(start, end, y_range[1], **kwargs)
        return self

    def set_ranges(self, start, end, x_range, y_range, **kwargs):
        """Animate both axis ranges to new bounds."""
        self.animate_x_range(start, end, x_range, **kwargs)
        self.animate_y_range(start, end, y_range, **kwargs)
        return self

    def zoom_to_fit(self, func, x_range=None, padding: float = 0.1, start: float = 0, end: float = 1, **kwargs):
        """Animate axes ranges to fit a function's output with optional padding.

        *func*: a callable f(x) -> y.
        *x_range*: (lo, hi) for evaluation; defaults to current x range.
        *padding*: fractional padding around data (0.1 = 10% on each side).
        """
        xmin = x_range[0] if x_range else self.x_min.at_time(start)
        xmax = x_range[1] if x_range else self.x_max.at_time(start)
        n = 200
        step = (xmax - xmin) / n
        ys = []
        for i in range(n + 1):
            try:
                y = func(xmin + i * step)
                if isinstance(y, (int, float)) and math.isfinite(y):
                    ys.append(y)
            except (TypeError, ValueError, ZeroDivisionError, OverflowError):
                continue
        if not ys:
            return self
        ylo, yhi = min(ys), max(ys)
        span = yhi - ylo or 1
        ylo -= span * padding
        yhi += span * padding
        if x_range:
            self.animate_x_range(start, end, x_range, **kwargs)
        self.animate_y_range(start, end, (ylo, yhi), **kwargs)
        return self

    def get_origin(self, time: float = 0):
        """Return the SVG pixel coordinates of the axes origin (0, 0)."""
        return self.coords_to_point(0, 0, time)

    def coords_to_point(self, x, y, time: float = 0):
        """Convert math coordinates to SVG pixel coordinates."""
        return (self._math_to_svg_x(x, time), self._math_to_svg_y(y, time))

    coords_to_screen = coords_to_point

    def screen_to_coords(self, sx, sy, time: float = 0):
        """Convert SVG pixel coordinates to math (axis) coordinates (inverse of coords_to_point)."""
        def _invert(sv, vmin, vmax, origin, size, scale, invert=False):
            frac = (sv - origin) / size
            if invert:
                frac = 1 - frac
            span = vmax - vmin if vmax != vmin else 1
            if scale == 'log' and vmin > 0 and vmax > 0:
                lmin, lmax = math.log10(vmin), math.log10(vmax)
                span = lmax - lmin if lmax != lmin else 1
                return 10 ** (lmin + frac * span)
            return vmin + frac * span
        xmin, xmax = self.x_min.at_time(time), self.x_max.at_time(time)
        ymin, ymax = self.y_min.at_time(time), self.y_max.at_time(time)
        return (_invert(sx, xmin, xmax, self.plot_x, self.plot_width, self._x_scale),
                _invert(sy, ymin, ymax, self.plot_y, self.plot_height, self._y_scale, invert=True))

    def get_plot_center(self, time: float = 0):
        """Return the SVG pixel coordinates of the center of the plot rectangle."""
        return (self.plot_x + self.plot_width / 2, self.plot_y + self.plot_height / 2)

    def input_to_graph_point(self, x, func, time: float = 0):
        """Convert a math x-value and function to SVG pixel coordinates: (x, f(x))."""
        return self.coords_to_point(x, func(x), time)

    def get_graph_value(self, func, x, time: float = 0):
        """Evaluate *func* at *x* and return the y-value."""
        return func(x)

    def get_point_on_graph(self, func, x, time: float = 0):
        """Like :meth:`input_to_graph_point` but returns ``None`` on error."""
        try:
            y = func(x)
        except (TypeError, ValueError, ZeroDivisionError, OverflowError):
            return None
        return self.coords_to_point(x, y, time=time)

    def graph_position(self, func, x_attr):
        """Return a callable(time) -> (svg_x, svg_y) that tracks a point on func."""
        get_x = x_attr.at_time if hasattr(x_attr, 'at_time') else x_attr
        def _pos(time):
            xv = get_x(time)
            return self.coords_to_point(xv, func(xv), time)
        return _pos

    def get_graph_label(self, func, label, x_val=None, direction='up', buff=SMALL_BUFF,
                         font_size: float = 48, creation: float = 0, z: float = 0, **styling_kwargs):
        """Create a TeX label positioned near a plotted function curve."""
        direction = _norm_dir(direction, 'up')
        style_kw = {'fill': '#fff', 'stroke_width': 0} | styling_kwargs
        label_obj = _get_tex_object()(label, font_size=font_size, creation=creation, z=z, **style_kw)
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

    def plot_parametric(self, func, t_range=(0, 1), num_points: int = 200,
                        creation: float = 0, z: float = 0, **styling_kwargs):
        """Plot a parametric curve func(t) -> (x, y) in math coordinates. Returns a Path."""
        if 'color' in styling_kwargs:
            styling_kwargs.setdefault('stroke', styling_kwargs.pop('color'))
        style_kw = _CURVE_STYLE | styling_kwargs
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

    def plot_polar(self, func, theta_range=(0, math.tau), num_points: int = 200,
                    creation: float = 0, z: float = 0, **styling_kwargs):
        """Plot a polar curve r=func(theta) on these axes. Returns a Path."""
        def _parametric(theta):
            r = func(theta)
            return (r * math.cos(theta), r * math.sin(theta))
        return self.plot_parametric(_parametric, t_range=theta_range,
                                    num_points=num_points, creation=creation,
                                    z=z, **styling_kwargs)

    def plot_implicit(self, func, num_points: int = 100, creation: float = 0, z: float = 0, **styling_kwargs):
        """Plot an implicit curve f(x, y) = 0 using marching squares. Returns a Path."""
        if 'color' in styling_kwargs:
            styling_kwargs.setdefault('stroke', styling_kwargs.pop('color'))
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

    def plot_line_graph(self, x_values, y_values, creation: float = 0, z: float = 0, **styling_kwargs):
        """Plot a line graph from discrete data points. Returns a VCollection with animate_data()."""
        if 'color' in styling_kwargs:
            styling_kwargs.setdefault('stroke', styling_kwargs.pop('color'))
        style_kw = _CURVE_STYLE | styling_kwargs
        # Mutable container so animate_data can update the data reference
        data_ref = [list(zip(x_values, y_values))]
        axes_ref = self
        curve = Path('', x=0, y=0, creation=creation, z=z, **style_kw)
        def _compute_d(time):
            pts = [(axes_ref._math_to_svg_x(x, time), axes_ref._math_to_svg_y(y, time))
                   for x, y in data_ref[0]]
            if not pts:
                return ''
            return 'M' + 'L'.join(f'{x},{y}' for x, y in pts)
        curve.d.set_onward(creation, _compute_d)
        # Dynamic dots that track animated axis ranges
        dots = []
        for x, y in data_ref[0]:
            dot = Dot(cx=self._math_to_svg_x(x, creation), cy=self._math_to_svg_y(y, creation),
                      r=3, creation=creation, z=z,
                      fill=style_kw.get('stroke', '#58C4DD'))
            dot.c.set_onward(creation,
                lambda t, _x=x, _y=y: self.coords_to_point(_x, _y, t))
            dots.append(dot)
        group = VCollection(curve, *dots, creation=creation, z=z)

        def _animate_data(new_x, new_y, start: float = 0, end: float = 1, easing=None):
            """Animate the line graph data to new values over [start, end]."""
            _easing = easing or easings.smooth
            old_data = list(data_ref[0])
            new_data = list(zip(new_x, new_y))
            data_ref[0] = new_data
            dur = end - start
            if dur <= 0:
                # Instant update: just swap data and update dot positions
                for i, dot in enumerate(dots):
                    if i < len(new_data):
                        nx, ny = new_data[i]
                        dot.c.set_onward(start,
                            lambda t, _x=nx, _y=ny: axes_ref.coords_to_point(_x, _y, t))
                return group
            # Animated update: interpolate between old and new data for the
            # line path, and animate each dot's position.
            # Override the curve d with an interpolating function
            def _interp_d(time):
                if time >= end:
                    pts = [(axes_ref._math_to_svg_x(x, time),
                            axes_ref._math_to_svg_y(y, time))
                           for x, y in new_data]
                elif time <= start:
                    pts = [(axes_ref._math_to_svg_x(x, time),
                            axes_ref._math_to_svg_y(y, time))
                           for x, y in old_data]
                else:
                    p = _easing((time - start) / dur)
                    pts = []
                    n = max(len(old_data), len(new_data))
                    for i in range(n):
                        ox, oy = old_data[i] if i < len(old_data) else (old_data[-1] if old_data else new_data[i])
                        nx, ny = new_data[i] if i < len(new_data) else (new_data[-1] if new_data else old_data[i])
                        ix = ox + (nx - ox) * p
                        iy = oy + (ny - oy) * p
                        pts.append((axes_ref._math_to_svg_x(ix, time),
                                    axes_ref._math_to_svg_y(iy, time)))
                if not pts:
                    return ''
                return 'M' + 'L'.join(f'{x},{y}' for x, y in pts)
            curve.d.set_onward(start, _interp_d)
            # Animate dots
            for i, dot in enumerate(dots):
                if i < len(old_data) and i < len(new_data):
                    ox, oy = old_data[i]
                    nx, ny = new_data[i]
                    _ox, _oy, _nx, _ny = ox, oy, nx, ny
                    _s, _d, _e_fn = start, dur, _easing
                    def _dot_pos(t, _ox=_ox, _oy=_oy, _nx=_nx, _ny=_ny,
                                 _s=_s, _d=_d, _e=_e_fn, _end=end):
                        if t >= _end:
                            return axes_ref.coords_to_point(_nx, _ny, t)
                        elif t <= _s:
                            return axes_ref.coords_to_point(_ox, _oy, t)
                        p = _e((t - _s) / _d)
                        ix = _ox + (_nx - _ox) * p
                        iy = _oy + (_ny - _oy) * p
                        return axes_ref.coords_to_point(ix, iy, t)
                    dot.c.set_onward(start, _dot_pos)
            return group

        group.animate_data = _animate_data
        self._add_plot_obj(group)
        return group

    def plot_scatter(self, x_values, y_values, r: float = 5, creation: float = 0, z: float = 0, **styling_kwargs):
        """Plot a scatter plot (dots only, no connecting lines). Returns a VCollection."""
        if 'color' in styling_kwargs:
            styling_kwargs.setdefault('fill', styling_kwargs.pop('color'))
        style_kw = {'fill': '#58C4DD', 'stroke_width': 0} | styling_kwargs
        data = list(zip(x_values, y_values))
        dots = []
        for x, y in data:
            dot = Dot(cx=0, cy=0, r=r, creation=creation, z=z, **style_kw)
            dot.c.set_onward(creation, lambda t, _xv=x, _yv=y: self.coords_to_point(_xv, _yv, t))
            dots.append(dot)
        group = VCollection(*dots, creation=creation, z=z)
        self._add_plot_obj(group)
        return group

    def plot_step(self, x_values, y_values, creation: float = 0, z: float = 0, **styling_kwargs):
        """Plot a step function (horizontal then vertical segments).
        Returns a Path object."""
        if 'color' in styling_kwargs:
            styling_kwargs.setdefault('stroke', styling_kwargs.pop('color'))
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

    def plot_filled_step(self, x_values, y_values, baseline: float = 0, creation: float = 0, z: float = 0, **styling_kwargs):
        """Plot a step function with shaded area down to baseline.
        Returns a Path object."""
        if 'color' in styling_kwargs:
            c = styling_kwargs.pop('color')
            styling_kwargs.setdefault('stroke', c)
            styling_kwargs.setdefault('fill', c)
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

    def plot_histogram(self, data, bins: int = 10, creation: float = 0, z: float = 0, **styling_kwargs):
        """Plot a histogram from raw data values. Returns a VCollection of Rectangles."""
        if not data:
            return VCollection()
        if 'color' in styling_kwargs:
            c = styling_kwargs.pop('color')
            styling_kwargs.setdefault('fill', c)
            styling_kwargs.setdefault('stroke', c)
        style_kw = {'fill': '#58C4DD', 'fill_opacity': 0.5,
                    'stroke': '#58C4DD', 'stroke_width': 1} | styling_kwargs
        if isinstance(bins, int):
            if bins < 1:
                bins = 1
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

    def plot_bar(self, x_values, y_values, bar_width: float = 0.6, creation: float = 0, z: float = 0, **styling_kwargs):
        """Plot a bar chart inside the axes coordinate system. Returns a VCollection."""
        # Pop 'width'/'height' from kwargs — they conflict with Rectangle positional args
        styling_kwargs.pop('width', None)
        styling_kwargs.pop('height', None)
        style_kw = {'fill': '#58C4DD', 'fill_opacity': 0.7,
                    'stroke': '#58C4DD', 'stroke_width': 1} | styling_kwargs
        data = list(zip(x_values, y_values))
        rects = []
        for xv, yv in data:
            # Each bar: from baseline (y=0) up to yv
            rect = Rectangle(1, 1, x=0, y=0, creation=creation, z=z, **style_kw)
            _xv, _yv, _bw = xv, yv, bar_width
            def _compute_rect(time, _xv=_xv, _yv=_yv, _bw=_bw):
                left = self._math_to_svg_x(_xv - _bw / 2, time)
                right = self._math_to_svg_x(_xv + _bw / 2, time)
                top = self._math_to_svg_y(_yv, time)
                bottom = self._math_to_svg_y(0, time)
                return left, min(top, bottom), right - left, abs(top - bottom)
            rect.x.set_onward(creation, lambda t, _f=_compute_rect: _f(t)[0])
            rect.y.set_onward(creation, lambda t, _f=_compute_rect: _f(t)[1])
            rect.width.set_onward(creation, lambda t, _f=_compute_rect: _f(t)[2])
            rect.height.set_onward(creation, lambda t, _f=_compute_rect: _f(t)[3])
            rects.append(rect)
        group = VCollection(*rects, creation=creation, z=z)
        self._add_plot_obj(group)
        return group

    def plot_stem(self, x_values, y_values, baseline: float = 0, r: float = 4, creation: float = 0, z: float = 0,
                   **styling_kwargs):
        """Plot a stem chart with vertical lines and dot markers. Returns a VCollection."""
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

    def plot_grouped_bar(self, data, group_labels=None, bar_width: float = 0.25,
                          group_spacing=1.0, colors=None, creation: float = 0, z: float = 0,
                          **styling_kwargs):
        """Plot a grouped bar chart. Returns a VCollection of all bars."""
        n_series = len(data)
        if n_series == 0:
            return VCollection(creation=creation, z=z)
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
        if group_labels:
            for gi, label in enumerate(group_labels):
                x_center = (gi + 1) * group_spacing
                sx = self._math_to_svg_x(x_center, creation)
                sy = self._math_to_svg_y(0, creation) + 20
                t = Text(str(label), x=sx, y=sy, font_size=14,
                         text_anchor='middle', stroke_width=0,
                         creation=creation, z=z)
                rects.append(t)
        group = VCollection(*rects, creation=creation, z=z)
        self._add_plot_obj(group)
        return group

    @staticmethod
    def _lerp_colormap(frac, colormap):
        """Interpolate a color from a colormap: list of (frac, '#rrggbb') stops."""
        frac = _clamp01(frac)
        for (f0, c0), (f1, c1) in zip(colormap, colormap[1:]):
            if f0 <= frac <= f1:
                from vectormation.colors import interpolate_color
                t = (frac - f0) / max(f1 - f0, 1e-9)
                return interpolate_color(c0, c1, t)
        return colormap[-1][1]

    @staticmethod
    def _resolve_func(obj, label='argument'):
        """Extract a callable from a function or a curve with ._func."""
        if hasattr(obj, '_func'):
            return obj._func
        if callable(obj):
            return obj
        raise TypeError(f'{label} must be a function or a curve returned by plot()')

    def _resolve_x_range(self, x_start=None, x_end=None):
        """Return ``(x0, x1)`` falling back to the current axis range."""
        x0 = float(self.x_min.at_time(0)) if x_start is None else float(x_start)
        x1 = float(self.x_max.at_time(0)) if x_end is None else float(x_end)
        return x0, x1

    def get_graph_intersection(self, f1, f2, x_range=None, n: int = 1000):
        """Find approximate intersection points between two functions/curves."""
        func1 = self._resolve_func(f1, 'f1')
        func2 = self._resolve_func(f2, 'f2')
        xmin = x_range[0] if x_range else self.x_min.at_time(0)
        xmax = x_range[1] if x_range else self.x_max.at_time(0)
        step = (xmax - xmin) / n
        points = []
        prev_diff = None
        prev_x = xmin
        for i in range(n + 1):
            x = xmin + i * step
            try:
                diff = func1(x) - func2(x)
            except (ValueError, ZeroDivisionError):
                prev_diff = None
                continue
            if abs(diff) < 1e-12:
                # Exact (or near-exact) intersection at sample point
                points.append((x, func1(x)))
            elif prev_diff is not None and prev_diff * diff < 0:
                # Sign change: linear interpolation for sub-step accuracy
                t = prev_diff / (prev_diff - diff)
                ix = prev_x + t * step
                iy = func1(ix)
                points.append((ix, iy))
            prev_diff = diff
            prev_x = x
        return points

    def get_area(self, curve_or_func, x_range=None, bounded_graph=None, creation: float = 0, z: float = 0, **styling_kwargs):
        """Create a shaded area under a curve/function (or between two curves).
        Returns a dynamic Path object."""
        style_kw = _AREA_STYLE | styling_kwargs
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
                    try:
                        yv = f(xv)
                    except (ValueError, ZeroDivisionError, OverflowError):
                        continue
                    if not math.isfinite(yv):
                        continue
                    sx = self._math_to_svg_x(xv, time)
                    sy = self._math_to_svg_y(yv, time)
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

    def get_area_value(self, func, x_start, x_end, samples: int = 100):
        """Return the numerical integral of *func* over [x_start, x_end] using the trapezoidal rule."""
        fn = self._resolve_func(func, 'func')
        n = max(int(samples), 2)
        step = (x_end - x_start) / n
        xs = [x_start + i * step for i in range(n + 1)]
        ys = [fn(x) for x in xs]
        return sum(0.5 * (ys[i] + ys[i + 1]) * step for i in range(n))

    get_integral = get_area_value

    def get_average(self, func, x_start=None, x_end=None, samples: int = 200):
        """Return the average value of *func* over [x_start, x_end]."""
        x0, x1 = self._resolve_x_range(x_start, x_end)
        if x0 == x1:
            fn = self._resolve_func(func, 'func')
            return fn(x0)
        integral = self.get_area_value(func, x0, x1, samples)
        return integral / (x1 - x0)

    def get_graph_length(self, func, x_start=None, x_end=None, samples: int = 200):
        """Return approximate arc length of *func*'s graph in SVG pixel coordinates."""
        fn = self._resolve_func(func, 'func')
        x0, x1 = self._resolve_x_range(x_start, x_end)
        total = 0.0
        prev = None
        for i in range(samples + 1):
            x = x0 + (x1 - x0) * i / samples
            try:
                y = fn(x)
            except (TypeError, ValueError, ZeroDivisionError, OverflowError):
                prev = None
                continue
            if not math.isfinite(y):
                prev = None
                continue
            sx, sy = self.coords_to_point(x, y)
            if prev is not None:
                total += math.hypot(sx - prev[0], sy - prev[1])
            prev = (sx, sy)
        return total

    def _find_extremum(self, func, x_start, x_end, samples, is_max):
        """Shared helper for get_function_max / get_function_min."""
        fn = self._resolve_func(func, 'func')
        n = max(int(samples), 2)
        step = (x_end - x_start) / n
        best_x, best_y = None, None
        for i in range(n + 1):
            x = x_start + i * step
            try:
                y = fn(x)
            except (TypeError, ValueError, ZeroDivisionError, OverflowError):
                continue
            if not math.isfinite(y):
                continue
            if best_y is None or (y > best_y if is_max else y < best_y):
                best_x, best_y = x, y
        if best_x is None:
            raise ValueError(f'No finite function values found in x=[{x_start}, {x_end}] ({samples} samples).')
        return (best_x, best_y)

    def get_function_max(self, func, x_start, x_end, samples: int = 200):
        """Return ``(x, y)`` where *func* achieves its maximum over [x_start, x_end]."""
        return self._find_extremum(func, x_start, x_end, samples, is_max=True)

    def get_function_min(self, func, x_start, x_end, samples: int = 200):
        """Return ``(x, y)`` where *func* achieves its minimum over [x_start, x_end]."""
        return self._find_extremum(func, x_start, x_end, samples, is_max=False)

    def get_zeros(self, func, x_start, x_end, samples: int = 200):
        """Return list of ``(x, 0.0)`` tuples where *func* crosses zero, using bisection."""
        fn = self._resolve_func(func, 'func')
        n = max(int(samples), 2)
        step = (x_end - x_start) / n
        xs = [x_start + i * step for i in range(n + 1)]
        # Evaluate, replacing non-finite values with None
        ys = []
        for x in xs:
            try:
                y = fn(x)
                ys.append(y if math.isfinite(y) else None)
            except (TypeError, ValueError, ZeroDivisionError, OverflowError):
                ys.append(None)
        zeros = []
        for i in range(n):
            ya, yb = ys[i], ys[i + 1]
            xa, xb = xs[i], xs[i + 1]
            if ya is None or yb is None:
                continue
            if ya == 0.0:
                # Exact zero at left endpoint (avoid double-counting with previous interval)
                if i == 0 or ys[i - 1] is None or ys[i - 1] != 0.0:
                    zeros.append((xa, 0.0))
                continue
            if ya * yb >= 0:
                continue  # no sign change
            # Bisection refinement
            lo, hi = xa, xb
            flo = ya
            for _ in range(52):  # ~52 bisection steps gives float precision
                mid = (lo + hi) * 0.5
                if mid == lo or mid == hi:
                    break
                try:
                    fmid = fn(mid)
                except (TypeError, ValueError, ZeroDivisionError, OverflowError):
                    break
                if not math.isfinite(fmid):
                    break
                if fmid == 0.0:
                    lo = hi = mid
                    break
                if flo * fmid < 0:
                    hi = mid
                else:
                    lo = mid
                    flo = fmid
            zeros.append(((lo + hi) * 0.5, 0.0))
        # Handle exact zero at final sample point
        if ys[-1] == 0.0 and n > 0:
            if ys[-2] is None or ys[-2] != 0.0:
                zeros.append((xs[-1], 0.0))
        zeros.sort(key=lambda p: p[0])
        return zeros

    def get_x_intercept(self, func, x_start=None, x_end=None):
        """Return the first x where func(x) is approximately 0, or None."""
        x0, x1 = self._resolve_x_range(x_start, x_end)
        zeros = self.get_zeros(func, x0, x1)
        if zeros:
            return zeros[0][0]
        return None

    def get_y_intercept(self, func):
        """Return func(0) (the y-intercept), or None on error."""
        fn = self._resolve_func(func, 'func')
        try:
            return fn(0)
        except (TypeError, ValueError, ZeroDivisionError, OverflowError):
            return None

    def get_derivative(self, func, x_val, h: float = 0.001):
        """Return the numerical derivative of *func* at *x_val* using central differences."""
        fn = self._resolve_func(func, 'func')
        return (fn(x_val + h) - fn(x_val - h)) / (2 * h)

    get_slope = get_derivative

    def get_secant_slope(self, func, x, dx):
        """Return the secant slope ``(f(x + dx) - f(x)) / dx``."""
        if dx == 0:
            raise ValueError("get_secant_slope: dx must not be zero")
        fn = self._resolve_func(func, 'func')
        return (fn(x + dx) - fn(x)) / dx

    def add_legend(self, entries, position='upper right', font_size: float = 18,
                    bg_color='#1a1a2e', bg_opacity=0.8, creation: float = 0, z: float = 10):
        """Add a legend box with colored swatches and labels. Returns a VCollection."""
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
            row_y = by + 8 + i * row_h
            swatch = Rectangle(width=swatch_w, height=swatch_w,
                                x=bx + 8, y=row_y, fill=color, stroke_width=0,
                                creation=creation, z=z + 1)
            lbl = Text(text=label, x=bx + 8 + swatch_w + 8, y=row_y + font_size - 2,
                        font_size=font_size, fill='#ddd', stroke_width=0,
                        creation=creation, z=z + 1)
            objs.extend([swatch, lbl])
        group = VCollection(*objs, creation=creation, z=z)
        self._add_plot_obj(group)
        return group

    def get_area_between(self, func1, func2, x_range=None, creation: float = 0, z: float = 0, **styling_kwargs):
        """Shade the area between two functions. Returns a Path."""
        style_kw = _AREA_STYLE | styling_kwargs
        return self.get_area(func1, bounded_graph=func2, x_range=x_range,
                             creation=creation, z=z, **style_kw)

    def shade_between(self, func1, func2, x_range=None, color='#58C4DD',
                      opacity: float = 0.2, creation: float = 0, z: float = 0, **styling_kwargs):
        """Shade the region between two functions with given color and opacity."""
        kw = {'fill': color, 'fill_opacity': opacity} | styling_kwargs
        return self.get_area_between(func1, func2, x_range=x_range,
                                     creation=creation, z=z, **kw)

    def get_rect(self, x1, y1, x2, y2, creation: float = 0, z: float = 0, **styling_kwargs):
        """Create a Rectangle from two corners in math coordinates."""
        style_kw = {'fill': '#58C4DD', 'fill_opacity': 0.3, 'stroke': '#fff', 'stroke_width': 1} | styling_kwargs
        rect = Rectangle(width=0, height=0, creation=creation, z=z, **style_kw)
        _v = lambda c, t: c.at_time(t) if hasattr(c, 'at_time') else c
        def _corners(t):
            sx1, sx2 = self._math_to_svg_x(_v(x1, t), t), self._math_to_svg_x(_v(x2, t), t)
            sy1, sy2 = self._math_to_svg_y(_v(y1, t), t), self._math_to_svg_y(_v(y2, t), t)
            return min(sx1, sx2), min(sy1, sy2), abs(sx2 - sx1), abs(sy2 - sy1)
        rect.x.set_onward(creation, lambda t: _corners(t)[0])
        rect.y.set_onward(creation, lambda t: _corners(t)[1])
        rect.width.set_onward(creation, lambda t: _corners(t)[2])
        rect.height.set_onward(creation, lambda t: _corners(t)[3])
        self._add_plot_obj(rect)
        return rect

    def get_vertical_line(self, x, y_val=None, creation: float = 0, z: float = 0, **styling_kwargs):
        """Draw a vertical line at math x-coordinate. If *y_val* is given, the line
        extends from the baseline to that y-value; otherwise it spans the full plot height.
        Returns a Line object."""
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

    def add_dot_label(self, x, y, label=None, dot_color='#FF6B6B', dot_radius: float = 6,
                       label_offset=(10, -10), font_size: float = 20, creation: float = 0, z: float = 0):
        """Add a labeled dot at math coordinates (x, y). Returns (dot, label) where
        label is None if no *label* text was provided."""
        sx, sy = self.coords_to_point(x, y, time=creation)
        dot = Dot(cx=sx, cy=sy, r=dot_radius, fill=dot_color,
                  creation=creation, z=z)
        dot.c.set_onward(creation,
            lambda t, _x=x, _y=y: self.coords_to_point(_x, _y, t))
        self._add_plot_obj(dot)
        lbl = None
        if label is not None:
            lx, ly = sx + label_offset[0], sy + label_offset[1]
            lbl = Text(text=str(label), x=lx, y=ly, font_size=font_size,
                       fill=dot_color, stroke_width=0, creation=creation, z=z)
            _ox, _oy = label_offset
            lbl.x.set_onward(creation, self._xf(x, y, _ox))
            lbl.y.set_onward(creation, self._yf(y, x, _oy))
            self._add_plot_obj(lbl)
        return dot, lbl

    def add_point_label(self, x, y, text=None, dot_radius: float = 6, font_size: float = 20, buff: float = 10,
                        creation: float = 0, **kwargs) -> 'tuple[Dot, Text]':
        """Add a dot at math coordinates (x, y) with an optional text label. Returns (dot, label)."""
        if text is None:
            text = f'({x:g}, {y:g})'
        dot_color = kwargs.pop('dot_color', '#FF6B6B')
        return self.add_dot_label(x, y, label=str(text),  # type: ignore[return-value]
                                  dot_color=dot_color, dot_radius=dot_radius,
                                  label_offset=(0, -dot_radius - buff),
                                  font_size=font_size, creation=creation,
                                  z=kwargs.pop('z', 0))

    def add_labeled_points(self, points, dot_color='#FF6B6B', dot_radius: float = 6,
                            font_size: float = 14, creation: float = 0, z: float = 1):
        """Add multiple labeled dots to the axes. Returns a VCollection."""
        objs = []
        for item in points:
            x, y = item[0], item[1]
            label = item[2] if len(item) > 2 else ''
            sx, sy = self.coords_to_point(x, y)
            dot = Dot(cx=sx, cy=sy, r=dot_radius, fill=dot_color,
                      creation=creation, z=z)
            objs.append(dot)
            if label:
                lbl = Text(text=str(label), x=sx, y=sy - dot_radius - 8,
                           font_size=font_size, fill='#ddd', stroke_width=0,
                           text_anchor='middle', creation=creation, z=z)
                objs.append(lbl)
        group = VCollection(*objs, creation=creation, z=z)
        self._add_plot_obj(group)
        return group

    def add_marked_region(self, x1, x2, color='#FFFF00', opacity: float = 0.2, creation: float = 0, z: float = 0):
        """Highlight a vertical region on the axes between x1 and x2. Returns a Rectangle."""
        sx1 = self._math_to_svg_x(x1, time=creation)
        sx2 = self._math_to_svg_x(x2, time=creation)
        rect = Rectangle(
            width=abs(sx2 - sx1), height=self.plot_height,
            x=min(sx1, sx2), y=self.plot_y,
            fill=color, fill_opacity=opacity, stroke_width=0,
            creation=creation, z=z)
        self._add_plot_obj(rect)
        return rect

    def add_labeled_point(self, x, y, label=None, dot_radius: float = 5, direction='above',
                          creation: float = 0, **kwargs):
        """Add a Dot at (*x*, *y*) with an optional directional Text label."""
        _LP_DIR = {(0, -1): 'above', (0, 1): 'below', (-1, 0): 'left', (1, 0): 'right'}
        if isinstance(direction, tuple):
            direction = _LP_DIR.get(direction, 'above')
        z = kwargs.pop('z', 0)
        font_size = kwargs.pop('font_size', 20)
        label_color = kwargs.pop('label_color', '#fff')
        sx, sy = self.coords_to_point(x, y, time=creation)
        dot = Dot(cx=sx, cy=sy, r=dot_radius, creation=creation, z=z, **kwargs)
        dot.c.set_onward(creation,
            lambda t, _x=x, _y=y: self.coords_to_point(_x, _y, t))
        self._add_plot_obj(dot)
        objs = [dot]
        if label is not None:
            _offsets = {
                'above': (0, -dot_radius - 8),
                'below': (0, dot_radius + font_size),
                'left':  (-dot_radius - 8, 0),
                'right': (dot_radius + 8, 0),
            }
            ox, oy = _offsets.get(direction, (0, -dot_radius - 8))
            anchor = 'middle' if direction in ('above', 'below') else (
                'end' if direction == 'left' else 'start')
            lx, ly = sx + ox, sy + oy
            lbl = Text(text=str(label), x=lx, y=ly, font_size=font_size,
                       fill=label_color, stroke_width=0, text_anchor=anchor,
                       creation=creation, z=z)
            lbl.x.set_onward(creation, self._xf(x, y, ox))
            lbl.y.set_onward(creation, self._yf(y, x, oy))
            self._add_plot_obj(lbl)
            objs.append(lbl)
        return VCollection(*objs, creation=creation, z=z)

    def add_function_region(self, func, x_range=None, label=None,
                            color='#58C4DD', opacity: float = 0.2, creation: float = 0):
        """Plot a function and shade the area under it in one call. Returns the area Path."""
        self.add_function(func, label=label, x_range=x_range,
                          creation=creation, stroke=color)
        area = self.get_area(func, x_range=x_range, creation=creation,
                             fill=color, fill_opacity=opacity, stroke_width=0)
        return area

    def add_arrow_annotation(self, x, y, text, direction='up', length: float = 80, buff: float = 10,
                              font_size: float = 20, creation: float = 0, z: float = 5, **styling_kwargs):
        """Add a labeled arrow pointing to a math coordinate. Returns a VCollection."""
        direction = _norm_dir(direction, 'up')
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
        arrow = _get_arrow()(x1=ax1, y1=ay1, x2=ax2, y2=ay2,
                       tip_length=_tl, tip_width=_tw,
                       creation=creation, z=z, **style_kw)
        # Dynamic arrow endpoints
        def _base(t, _x=x, _y=y):
            return self.coords_to_point(_x, _y, t)
        arrow.shaft.p1.set_onward(creation,
            lambda t, _dx=dx, _dy=dy, _lb=length + buff: (
                (_b := _base(t))[0] + _dx * _lb, _b[1] + _dy * _lb))
        arrow.shaft.p2.set_onward(creation,
            lambda t, _dx=dx, _dy=dy, _bb=buff: (
                (_b := _base(t))[0] + _dx * _bb, _b[1] + _dy * _bb))
        # Dynamic arrowhead tip (3 vertices) — precompute constants
        _hw = _tw / 2
        _ux, _uy = _normalize(dx, dy)
        _px, _py = -_uy, _ux
        # Precompute fixed offsets from the tip base point
        _back_x, _back_y = -_ux * _tl, -_uy * _tl
        _perp_x, _perp_y = _px * _hw, _py * _hw
        _tb_cache = [None, None]  # [time, (bx, by)]
        def _tip_base(t, _dx=dx, _dy=dy, _bb=buff):
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

    def add_callout(self, x, y, text, offset_x: float = 60, offset_y=-60,
                    font_size: float = 18, box_padding=8, corner_radius=4,
                    creation: float = 0, z: float = 5, **styling_kwargs):
        """Add a floating text callout box with a leader line to a data point. Returns a VCollection."""
        text_color = styling_kwargs.pop('text_color', '#fff')
        box_fill = styling_kwargs.pop('box_fill', '#333')
        box_stroke = styling_kwargs.pop('box_stroke', '#aaa')
        box_stroke_width = styling_kwargs.pop('box_stroke_width', 1)

        sx, sy = self.coords_to_point(x, y, creation)

        # Rough text size estimate for initial box placement
        char_w = font_size * 0.6
        est_w = len(text) * char_w + 2 * box_padding
        est_h = font_size + 2 * box_padding

        bx = sx + offset_x - est_w / 2
        by = sy + offset_y - est_h / 2

        # Leader line from data point to box edge
        line = Line(x1=sx, y1=sy, x2=sx + offset_x, y2=sy + offset_y,
                    creation=creation, z=z,
                    stroke=box_stroke, stroke_width=box_stroke_width, fill_opacity=0)

        # Background box
        box = RoundedRectangle(width=est_w, height=est_h,
                               x=bx, y=by, corner_radius=corner_radius,
                               creation=creation, z=z + 0.1,
                               fill=box_fill, fill_opacity=0.92,
                               stroke=box_stroke, stroke_width=box_stroke_width)

        # Label centered in the box
        lbl = Text(text=text, x=sx + offset_x, y=sy + offset_y,
                   font_size=font_size, text_anchor='middle',
                   fill=text_color, stroke_width=0,
                   creation=creation, z=z + 0.2)

        # Make all elements track the data point dynamically
        _ox, _oy = offset_x, offset_y
        _ew, _eh = est_w, est_h

        def _pt(t, _x=x, _y=y):
            return self.coords_to_point(_x, _y, t)

        line.p1.set_onward(creation, lambda t: _pt(t))
        line.p2.set_onward(creation,
            lambda t, _ox=_ox, _oy=_oy: (_pt(t)[0] + _ox, _pt(t)[1] + _oy))
        box.x.set_onward(creation,
            lambda t, _ox=_ox, _ew=_ew: _pt(t)[0] + _ox - _ew / 2)
        box.y.set_onward(creation,
            lambda t, _oy=_oy, _eh=_eh: _pt(t)[1] + _oy - _eh / 2)
        lbl.x.set_onward(creation,
            lambda t, _ox=_ox: _pt(t)[0] + _ox)
        lbl.y.set_onward(creation,
            lambda t, _oy=_oy: _pt(t)[1] + _oy)

        group = VCollection(line, box, lbl, creation=creation, z=z)
        self._add_plot_obj(group)
        return group

    def add_cursor(self, func, x_start, x_end, start: float = 0, end: float = 1,
                    r: float = 6, creation: float = 0, z: float = 5, easing=easings.smooth, **styling_kwargs):
        """Add an animated dot that travels along func from x_start to x_end. Returns a Dot."""
        style_kw = {'fill': '#FFFF00', 'stroke_width': 0} | styling_kwargs
        dot = Dot(cx=0, cy=0, r=r, creation=creation, z=z, **style_kw)
        dur = end - start
        if dur <= 0:
            sx, sy = self.coords_to_point(x_start, func(x_start), creation)
            dot.c.set_onward(creation, (sx, sy))
        else:
            def _pos(t, _s=start, _d=dur, _xs=x_start, _xe=x_end, _easing=easing):
                progress = _easing((t - _s) / _d)
                xv = _xs + (_xe - _xs) * progress
                return self.coords_to_point(xv, func(xv), t)
            dot.c.set(start, end, _pos, stay=True)
        dot._show_from(start)
        self._add_plot_obj(dot)
        return dot

    def add_trace(self, func, x_start, x_end, start: float = 0, end: float = 1,
                   r: float = 5, trail_width: float = 2, creation: float = 0, z: float = 5, easing=easings.smooth,
                   **styling_kwargs):
        """Animated dot that traces along func, leaving a growing trail. Returns a VCollection."""
        style_kw = {'fill': '#FFFF00', 'stroke': '#FFFF00', 'stroke_width': 0} | styling_kwargs
        dot = self.add_cursor(func, x_start, x_end, start=start, end=end,
                               r=r, creation=creation, z=z + 1, easing=easing,
                               **{k: v for k, v in style_kw.items()
                                  if k in ('fill', 'stroke_width')})
        # Trail path that grows as the dot moves
        trail = Path('', x=0, y=0, creation=creation, z=z,
                     stroke=style_kw.get('stroke', '#FFFF00'),
                     stroke_width=trail_width, fill_opacity=0)
        _d = max(end - start, 1e-9)
        n_pts = 80
        def _compute_trail(t, _s=start, _d=_d, _xs=x_start, _xe=x_end, _n=n_pts, _easing=easing):
            progress = _clamp01(_easing((t - _s) / _d))
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
        return VCollection(dot, trail, creation=creation, z=z)

    def add_animation_trace(self, func, x_start, x_end, start: float = 0, end: float = 1,
                             dot=True, trail=True, color='#FFFF00', **kwargs):
        """Add a moving dot on a function curve with an optional trailing path."""
        # Filter kwargs for each target method to avoid passing
        # unsupported parameters (e.g. trail_width to add_cursor).
        _cursor_keys = {'r', 'creation', 'z', 'easing'}
        _trace_keys = _cursor_keys | {'trail_width'}
        cursor_kw = {k: v for k, v in kwargs.items() if k in _cursor_keys or k not in _trace_keys}
        trace_kw = kwargs
        if trail and dot:
            # add_trace already creates both dot and trail
            self.add_trace(func, x_start, x_end, start=start, end=end,
                           fill=color, stroke=color, **trace_kw)
        elif dot:
            self.add_cursor(func, x_start, x_end, start=start, end=end,
                            fill=color, **cursor_kw)
        elif trail:
            # Trail only: use add_trace with r=0 to hide the dot
            kw = {k: v for k, v in trace_kw.items() if k != 'r'}
            self.add_trace(func, x_start, x_end, start=start, end=end,
                           r=0, fill=color, stroke=color, **kw)
        return self

    def get_line_from_to(self, x1, y1, x2, y2, creation: float = 0, z: float = 0, **styling_kwargs):
        """Draw a line between two math coordinate points. Returns a Line."""
        style_kw = {'stroke': '#fff', 'stroke_width': 2} | styling_kwargs
        line = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z, **style_kw)
        _x1, _y1, _x2, _y2 = x1, y1, x2, y2
        line.p1.set_onward(creation, lambda t, _a=_x1, _b=_y1: self.coords_to_point(_a, _b, t))
        line.p2.set_onward(creation, lambda t, _a=_x2, _b=_y2: self.coords_to_point(_a, _b, t))
        self._add_plot_obj(line)
        return line

    def _highlight_range(self, lo, hi, axis, creation, z, styling_kwargs):
        """Shade a strip along one axis. Returns a Rectangle."""
        style_kw = _HIGHLIGHT_STYLE | styling_kwargs
        rect = Rectangle(width=0, height=0, x=0, y=0, creation=creation, z=z, **style_kw)
        if axis == 'x':
            conv = self._math_to_svg_x
            rect.y.set_onward(creation, lambda t: self.plot_y)
            rect.height.set_onward(creation, lambda t: self.plot_height)
            pos_attr, size_attr = rect.x, rect.width
        else:
            conv = self._math_to_svg_y
            rect.x.set_onward(creation, lambda t: self.plot_x)
            rect.width.set_onward(creation, lambda t: self.plot_width)
            pos_attr, size_attr = rect.y, rect.height
        pos_attr.set_onward(creation, lambda t, _l=lo, _h=hi, _c=conv: min(_c(_l, t), _c(_h, t)))
        size_attr.set_onward(creation, lambda t, _l=lo, _h=hi, _c=conv: abs(_c(_h, t) - _c(_l, t)))
        self._add_plot_obj(rect)
        return rect

    def highlight_x_range(self, x_lo, x_hi, creation: float = 0, z: float = -1, **styling_kwargs):
        """Shade a vertical strip between x_lo and x_hi. Returns a Rectangle."""
        return self._highlight_range(x_lo, x_hi, 'x', creation, z, styling_kwargs)

    def highlight_y_range(self, y_lo, y_hi, creation: float = 0, z: float = -1, **styling_kwargs):
        """Shade a horizontal strip between y_lo and y_hi. Returns a Rectangle."""
        return self._highlight_range(y_lo, y_hi, 'y', creation, z, styling_kwargs)

    def add_horizontal_band(self, y1, y2, color='#FFFF00', opacity: float = 0.2, creation: float = 0):
        """Add a shaded horizontal band between y-values y1 and y2. Returns a Rectangle."""
        return self.highlight_y_range(y1, y2, creation=creation, z=-1,
                                      fill=color, fill_opacity=opacity, stroke_width=0)

    def shade_region(self, x_start, x_end, y_start=None, y_end=None,
                     creation: float = 0, z: float = -1, **styling_kwargs):
        """Shade an axis-aligned rectangular region in math coordinates. Returns a Rectangle."""
        style_kw = _HIGHLIGHT_STYLE | styling_kwargs
        rect = Rectangle(width=0, height=0, x=0, y=0, creation=creation, z=z, **style_kw)
        for lo, hi, conv, plot_pos, plot_size, pos_attr, size_attr in [
            (x_start, x_end, self._math_to_svg_x, 'plot_x', 'plot_width', rect.x, rect.width),
            (y_start, y_end, self._math_to_svg_y, 'plot_y', 'plot_height', rect.y, rect.height),
        ]:
            if lo is None or hi is None:
                pos_attr.set_onward(creation, lambda t, _p=plot_pos: getattr(self, _p))
                size_attr.set_onward(creation, lambda t, _s=plot_size: getattr(self, _s))
            else:
                pos_attr.set_onward(creation, lambda t, _l=lo, _h=hi, _c=conv: min(_c(_l, t), _c(_h, t)))
                size_attr.set_onward(creation, lambda t, _l=lo, _h=hi, _c=conv: abs(_c(_h, t) - _c(_l, t)))
        self._add_plot_obj(rect)
        return rect

    def animate_range(self, start, end, x_range=None, y_range=None, easing=easings.smooth):
        """Animate the axis ranges to new bounds."""
        dur = end - start
        if dur <= 0:
            return self
        _d = max(dur, 1e-9)
        pairs = []
        if x_range is not None:
            pairs += [(self.x_min, x_range[0]), (self.x_max, x_range[1])]
        if y_range is not None and self.y_min is not None:
            pairs += [(self.y_min, y_range[0]), (self.y_max, y_range[1])]
        for attr, target in pairs:
            attr.set(start, end, _lerp(start, _d, attr.at_time(start), target, easing), stay=True)
        return self

    def add_shaded_inequality(self, func, direction='below', x_range=None,
                               samples: int = 100, creation: float = 0, z: float = -1, **styling_kwargs):
        """Shade the region above or below a curve. Returns a dynamic Path."""
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
            edge_y = (self.plot_y + self.plot_height) if _dir == 'below' else self.plot_y
            parts = [f'M{pts[0][0]:.1f},{pts[0][1]:.1f}']
            parts.extend(f'L{sx:.1f},{sy:.1f}' for sx, sy in pts[1:])
            parts.extend([f'L{pts[-1][0]:.1f},{edge_y:.1f}',
                          f'L{pts[0][0]:.1f},{edge_y:.1f}', 'Z'])
            return ''.join(parts)
        region.d.set_onward(creation, _region_d)
        self._add_plot_obj(region)
        return region

    def add_area_label(self, func, x_start=None, x_end=None, x_range=None,
                        text=None, font_size: float = 20,
                        creation: float = 0, z: float = 3, samples: int = 100, **styling_kwargs):
        """Add a label showing the numerical area under the curve, positioned at the centroid."""
        style_kw = {'fill': '#ddd', 'stroke_width': 0} | styling_kwargs
        fn = self._resolve_func(func, 'func')
        # Resolve bounds: explicit params > x_range > axis range
        if x_start is not None:
            xlo = x_start
        elif x_range:
            xlo = x_range[0]
        else:
            xlo = self.x_min.at_time(creation)
        if x_end is not None:
            xhi = x_end
        elif x_range:
            xhi = x_range[1]
        else:
            xhi = self.x_max.at_time(creation)
        # Trapezoidal integration and centroid estimation
        n = max(samples, 2)
        step = (xhi - xlo) / n
        xs = [xlo + i * step for i in range(n + 1)]
        ys = [fn(x) for x in xs]
        # Trapezoidal area: sum of 0.5*(y[i]+y[i+1])*step
        total_area = sum(0.5 * (ys[i] + ys[i + 1]) * step for i in range(n))
        # Centroid: weighted by |y| using midpoints for stability
        cx_sum = 0.0
        cy_sum = 0.0
        abs_area_sum = 0.0
        for i in range(n):
            xm = 0.5 * (xs[i] + xs[i + 1])
            ym = 0.5 * (ys[i] + ys[i + 1])
            w = abs(ym) * step
            cx_sum += xm * w
            cy_sum += 0.5 * ym * w
            abs_area_sum += w
        if abs_area_sum < 1e-9:
            cx_math = (xlo + xhi) / 2
            cy_math = 0
        else:
            cx_math = cx_sum / abs_area_sum
            cy_math = cy_sum / abs_area_sum
        label_text = text if text is not None else f'A = {total_area:.2f}'
        sx, sy = self.coords_to_point(cx_math, cy_math, creation)
        lbl = Text(text=label_text, x=sx, y=sy, font_size=font_size,
                    text_anchor='middle', creation=creation, z=z, **style_kw)
        lbl.x.set_onward(creation, self._xf(cx_math, cy_math))
        lbl.y.set_onward(creation, self._yf(cy_math, cx_math))
        self._add_plot_obj(lbl)
        return lbl

    def add_moving_tangent(self, func, x_start, x_end, start: float = 0, end: float = 1,
                            length: float = 200, creation: float = 0, z: float = 2, easing=easings.smooth,
                            **styling_kwargs):
        """Draw a tangent line that slides along func from x_start to x_end. Returns a Line."""
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
            dx = 1 / math.hypot(1, slope) * _hl
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

class Graph(Axes):
    """Axes with an initial function curve plotted."""
    def __init__(self, func, x_range=(-5, 5), y_range=None, num_points: int = 200,
                 x: float = 260, y: float = 100, plot_width: float = 1400, plot_height: float = 880,
                 x_label='x', y_label='y', label=None, label_direction='up',
                 label_x_val=None, show_grid=False,
                 creation: float = 0, z: float = 0, **styling_kwargs):
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
        curve_style = _CURVE_STYLE | styling_kwargs
        self.curve = self._make_curve(func, creation, z, num_points=num_points, **curve_style)
        self._add_plot_obj(self.curve)
        if label is not None:
            self.get_graph_label(func, label, x_val=label_x_val,
                                direction=label_direction,
                                fill=curve_style['stroke'], creation=creation, z=z)

    def __repr__(self):
        xn, xx = self.x_min.at_time(0), self.x_max.at_time(0)
        return f'Graph(x=[{xn:.1f}, {xx:.1f}])'

class NumberPlane(VCollection):
    """Cartesian coordinate plane with background grid lines."""
    def __init__(self, x_range=None, y_range=None,
                 cx=ORIGIN[0], cy=ORIGIN[1], width=CANVAS_WIDTH, height=CANVAS_HEIGHT,
                 faded_line_ratio=4,
                 background_line_style=None, faded_line_style=None,
                 axis_style=None, creation: float = 0, z: float = 0):
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

    def __repr__(self):
        return f'NumberPlane(x={self._x_range}, y={self._y_range})'

    def coords_to_point(self, x, y):
        """Convert logical coordinates to SVG pixel coordinates."""
        return (self._cx + x * self._unit, self._cy - y * self._unit)

    def apply_function(self, func, start: float = 0, end: float = 1, easing=easings.smooth, resolution: int = 20):
        """Animate a non-linear transformation of the grid."""
        # Rebuild grid as individual short line segments so they warp smoothly
        unit = self._unit
        cx, cy = self._cx, self._cy
        x_min, x_max, x_step = self._x_range
        y_min, y_max, y_step = self._y_range

        # Clear existing objects and rebuild with segmented lines
        new_objects = []
        dur = max(end - start, 1e-9)

        def _make_segment(lx0, ly0, lx1, ly1, style_kw, creation_t, z_val):
            """Create a Line segment that morphs from original to transformed position."""
            sx0, sy0 = cx + lx0 * unit, cy - ly0 * unit
            sx1, sy1 = cx + lx1 * unit, cy - ly1 * unit
            tx0, ty0 = func(lx0, ly0)
            tx1, ty1 = func(lx1, ly1)
            tsx0, tsy0 = cx + tx0 * unit, cy - ty0 * unit
            tsx1, tsy1 = cx + tx1 * unit, cy - ty1 * unit
            seg = Line(x1=sx0, y1=sy0, x2=sx1, y2=sy1,
                       creation=creation_t, z=z_val, **style_kw)
            seg.shift(dx=0, dy=0, start=start, end=start)  # anchor
            # Animate endpoints
            seg.p1.set(start, end,
                _lerp_point(start, dur, (sx0, sy0), (tsx0, tsy0), easing))
            seg.p2.set(start, end,
                _lerp_point(start, dur, (sx1, sy1), (tsx1, tsy1), easing))
            return seg

        style = {'stroke': '#4488AA', 'stroke_width': 2, 'stroke_opacity': 0.6}

        # Vertical lines (varying x, stepping through y)
        v = x_min
        while v <= x_max + 1e-9:
            for i in range(resolution):
                t0 = y_min + (y_max - y_min) * i / resolution
                t1 = y_min + (y_max - y_min) * (i + 1) / resolution
                new_objects.append(_make_segment(v, t0, v, t1, style, 0, 0))
            v += x_step

        # Horizontal lines (varying y, stepping through x)
        v = y_min
        while v <= y_max + 1e-9:
            for i in range(resolution):
                t0 = x_min + (x_max - x_min) * i / resolution
                t1 = x_min + (x_max - x_min) * (i + 1) / resolution
                new_objects.append(_make_segment(t0, v, t1, v, style, 0, 0))
            v += y_step

        self.objects = new_objects
        return self

    def add_coordinate_labels(self, font_size: float = 18, x_values=None, y_values=None, creation: float = 0):
        """Create Text labels at tick positions on both axes. Skips 0."""
        x_min, x_max, x_step = self._x_range
        y_min, y_max, y_step = self._y_range

        if x_values is None:
            v = math.ceil(x_min / x_step - 1e-9) * x_step
            x_values = []
            while v <= x_max + 1e-9:
                x_values.append(v)
                v += x_step

        if y_values is None:
            v = math.ceil(y_min / y_step - 1e-9) * y_step
            y_values = []
            while v <= y_max + 1e-9:
                y_values.append(v)
                v += y_step

        labels = []
        for x in x_values:
            if abs(x) < 1e-9:
                continue
            px, py = self.coords_to_point(x, 0)
            lbl = Text(
                str(int(x) if x == int(x) else x),
                x=px, y=py + font_size * 1.2,
                font_size=font_size, creation=creation,
            )
            labels.append(lbl)

        for y in y_values:
            if abs(y) < 1e-9:
                continue
            px, py = self.coords_to_point(0, y)
            lbl = Text(
                str(int(y) if y == int(y) else y),
                x=px - font_size * 1.2, y=py,
                font_size=font_size, creation=creation,
            )
            labels.append(lbl)

        self.objects.extend(labels)
        return self

    def apply_matrix(self, matrix, start: float = 0, end: float = 1, easing=easings.smooth, resolution: int = 20):
        """Apply a 2x2 linear transformation matrix as an animated grid transformation."""
        return self.apply_function(
            lambda x, y: (
                matrix[0][0] * x + matrix[0][1] * y,
                matrix[1][0] * x + matrix[1][1] * y,
            ),
            start=start, end=end, easing=easing, resolution=resolution,
        )

    def point_to_coords(self, x, y):
        """Inverse of coords_to_point. Returns logical coordinates from SVG pixel coordinates."""
        return ((x - self._cx) / self._unit, -(y - self._cy) / self._unit)

    def get_vector(self, x, y, creation: float = 0, **kwargs):
        """Return an Arrow from the origin to point (x, y) in logical coordinates."""
        from vectormation._arrows import Arrow
        sx0, sy0 = self.coords_to_point(0, 0)
        sx1, sy1 = self.coords_to_point(x, y)
        kw = {'stroke': '#E74C3C', 'stroke_width': 4} | kwargs
        arrow = Arrow(x1=sx0, y1=sy0, x2=sx1, y2=sy1, creation=creation, **kw)
        self.objects.append(arrow)
        return arrow

class ComplexPlane(Axes):
    """Complex number plane with Re/Im axes."""
    def __init__(self, x_range=(-5, 5), y_range=(-5, 5),
                 x_label='Re', y_label='Im', show_grid=True,
                 creation: float = 0, z: float = 0, **kwargs):
        super().__init__(x_range=x_range, y_range=y_range,
                         x_label=x_label, y_label=y_label,
                         show_grid=show_grid, creation=creation, z=z, **kwargs)

    def __repr__(self):
        xn, xx = self.x_min.at_time(0), self.x_max.at_time(0)
        return f'ComplexPlane(Re=[{xn:.1f}, {xx:.1f}])'

    def number_to_point(self, z_val, time: float = 0):
        """Convert a complex number to SVG coordinates."""
        if isinstance(z_val, complex):
            return self.coords_to_point(z_val.real, z_val.imag, time)
        return self.coords_to_point(float(z_val), 0, time)

    def point_to_number(self, x, y, time: float = 0):
        """Convert SVG coordinates to a complex number."""
        xmin, xmax, ymin, ymax = self._get_bounds(time)
        re = xmin + (x - self.plot_x) / self.plot_width * (xmax - xmin)
        im = ymax - (y - self.plot_y) / self.plot_height * (ymax - ymin)
        return complex(re, im)

    def add_complex_label(self, z, text=None, **styling):
        """Add a labelled dot at the complex number *z*."""
        if isinstance(z, complex):
            re_val, im_val = z.real, z.imag
        else:
            re_val, im_val = float(z), 0.0
        label = text if text is not None else f'{re_val:g}+{im_val:g}i'
        return self.add_dot_label(re_val, im_val, label=label, **styling)

    def apply_complex_function(self, func, start: float = 0, end: float = 1, easing=easings.smooth,
                               resolution=20, step: float = 1.0):
        """Animate a complex function transformation of the plane."""
        xmin = self.x_min.at_time(0)
        xmax = self.x_max.at_time(0)
        ymin = self.y_min.at_time(0)
        ymax = self.y_max.at_time(0)

        dur = max(end - start, 1e-9)
        new_objects = []
        style_kw = {'stroke': '#4488AA', 'stroke_width': 2, 'stroke_opacity': 0.6}

        def _make_seg(lx0, ly0, lx1, ly1):
            """Create a Line that morphs from (lx0,ly0)-(lx1,ly1) to func(z)-mapped positions."""
            z0 = complex(lx0, ly0)
            z1 = complex(lx1, ly1)
            try:
                w0 = func(z0)
                w1 = func(z1)
            except (ZeroDivisionError, ValueError, OverflowError):
                return None

            # Skip segments where the function blows up
            if not (math.isfinite(w0.real) and math.isfinite(w0.imag)
                    and math.isfinite(w1.real) and math.isfinite(w1.imag)):
                return None

            sx0 = self._math_to_svg_x(lx0)
            sy0 = self._math_to_svg_y(ly0)
            sx1 = self._math_to_svg_x(lx1)
            sy1 = self._math_to_svg_y(ly1)
            tsx0 = self._math_to_svg_x(w0.real)
            tsy0 = self._math_to_svg_y(w0.imag)
            tsx1 = self._math_to_svg_x(w1.real)
            tsy1 = self._math_to_svg_y(w1.imag)

            seg = Line(x1=sx0, y1=sy0, x2=sx1, y2=sy1, creation=0, **style_kw)
            seg.p1.set(start, end,
                _lerp_point(start, dur, (sx0, sy0), (tsx0, tsy0), easing))
            seg.p2.set(start, end,
                _lerp_point(start, dur, (sx1, sy1), (tsx1, tsy1), easing))
            return seg

        # Vertical lines: for each x on the grid, subdivide the y range
        x_val = math.ceil(xmin / step) * step
        while x_val <= xmax + 1e-9:
            for i in range(resolution):
                t0 = ymin + (ymax - ymin) * i / resolution
                t1 = ymin + (ymax - ymin) * (i + 1) / resolution
                seg = _make_seg(x_val, t0, x_val, t1)
                if seg is not None:
                    new_objects.append(seg)
            x_val += step

        # Horizontal lines: for each y on the grid, subdivide the x range
        y_val = math.ceil(ymin / step) * step
        while y_val <= ymax + 1e-9:
            for i in range(resolution):
                t0 = xmin + (xmax - xmin) * i / resolution
                t1 = xmin + (xmax - xmin) * (i + 1) / resolution
                seg = _make_seg(t0, y_val, t1, y_val)
                if seg is not None:
                    new_objects.append(seg)
            y_val += step

        self.objects.extend(new_objects)
        return self

    n2p = number_to_point
    p2n = point_to_number

    def add_coordinate_labels(self, font_size: float = 18, creation: float = 0):
        """Create Text labels on real and imaginary axes (e.g. '2', '-3i')."""
        xmin, xmax, ymin, ymax = self._get_bounds(0)
        x_step = max(1, round((xmax - xmin) / 10))
        y_step = max(1, round((ymax - ymin) / 10))

        labels = []

        # Real axis labels (integers along x, y=0)
        v = math.ceil(xmin / x_step - 1e-9) * x_step
        while v <= xmax + 1e-9:
            if abs(v) > 1e-9:
                px = self._math_to_svg_x(v)
                py = self._math_to_svg_y(0)
                iv = int(round(v))
                lbl = Text(
                    str(iv),
                    x=px, y=py + font_size * 1.2,
                    font_size=font_size, creation=creation,
                )
                labels.append(lbl)
            v += x_step

        # Imaginary axis labels (integers along y, x=0)
        v = math.ceil(ymin / y_step - 1e-9) * y_step
        while v <= ymax + 1e-9:
            if abs(v) > 1e-9:
                px = self._math_to_svg_x(0)
                py = self._math_to_svg_y(v)
                iv = int(round(v))
                text = f'{iv}i' if iv != 1 else 'i'
                if iv == -1:
                    text = '-i'
                lbl = Text(
                    text,
                    x=px - font_size * 1.2, y=py,
                    font_size=font_size, creation=creation,
                )
                labels.append(lbl)
            v += y_step

        self.objects.extend(labels)
        return self
