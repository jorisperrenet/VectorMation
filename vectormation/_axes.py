"""Axes, Graph, NumberPlane, and ComplexPlane classes."""
import math

import vectormation.easings as easings
import vectormation.attributes as attributes
from vectormation._constants import (
    CANVAS_WIDTH, CANVAS_HEIGHT, ORIGIN,
    UNIT, SMALL_BUFF, DEFAULT_FONT_SIZE,
    DEFAULT_OBJECT_TO_EDGE_BUFF, DEFAULT_CHART_COLORS, CHAR_WIDTH_FACTOR, TEXT_Y_OFFSET,
    _sample_function, _normalize,
)
from vectormation._base import VObject, VCollection, _norm_dir, _lerp, _ramp, _lerp_point
from vectormation._shapes import (
    Polygon, Circle, Ellipse, Dot, Rectangle, RoundedRectangle, Line, Lines,
    Text, Path, Arc,
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

_AREA_STYLE = {'fill': '#58C4DD', 'fill_opacity': 0.3, 'stroke_width': 0}
_HIGHLIGHT_STYLE = {'fill': '#FFFF00', 'fill_opacity': 0.15, 'stroke_width': 0}


def _get_arrow():
    from vectormation._arrows import Arrow
    return Arrow

def _get_dynamic_object():
    from vectormation._composites import DynamicObject
    return DynamicObject

def _get_tex_object():
    from vectormation._composites import TexObject
    return TexObject

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

def _log_ticks(vmin, vmax):
    """Generate log-scale tick values (powers of 10) between vmin and vmax (both > 0)."""
    if vmin <= 0 or vmax <= 0:
        return []
    start_exp = math.floor(math.log10(vmin))
    end_exp = math.ceil(math.log10(vmax))
    ticks = []
    for e in range(start_exp, end_exp + 1):
        val = 10 ** e
        if vmin <= val <= vmax:
            ticks.append(val)
    return ticks


def _format_tick(val, tick_format):
    """Format a tick value using the given format (None, callable, or format string)."""
    if tick_format is None:
        return f'{val:g}'
    if callable(tick_format):
        return tick_format(val)
    return tick_format.format(val)


def _build_axes_decoration(x_min, x_max, y_min, y_max, plot_x, plot_y, plot_width, plot_height,
                            show_grid, time, x_scale='linear', y_scale='linear', tick_format=None):
    """Build axis lines, ticks, tick labels, and grid as VObjects for a single frame."""
    objects = []

    # For log scale, transform bounds to log space for positioning
    if x_scale == 'log' and x_min > 0 and x_max > 0:
        lx_min, lx_max = math.log10(x_min), math.log10(x_max)
    else:
        lx_min, lx_max = x_min, x_max
    if y_scale == 'log' and y_min > 0 and y_max > 0:
        ly_min, ly_max = math.log10(y_min), math.log10(y_max)
    else:
        ly_min, ly_max = y_min, y_max

    x_span = lx_max - lx_min if lx_max != lx_min else 1
    y_span = ly_max - ly_min if ly_max != ly_min else 1

    def _to_svg_x(val):
        v = math.log10(val) if x_scale == 'log' and val > 0 else val
        return plot_x + (v - lx_min) / x_span * plot_width

    def _to_svg_y(val):
        v = math.log10(val) if y_scale == 'log' and val > 0 else val
        return plot_y + (1 - (v - ly_min) / y_span) * plot_height

    # Axis baseline positions
    if x_scale == 'log':
        y_zero = plot_y + plot_height  # log axes have no zero; use bottom
        x_zero = plot_x               # use left edge
    else:
        y_zero = plot_y + (1 - (0 - ly_min) / y_span) * plot_height if ly_min <= 0 <= ly_max else plot_y + plot_height
        x_zero = plot_x + (0 - lx_min) / x_span * plot_width if lx_min <= 0 <= lx_max else plot_x
    tick_len = SMALL_BUFF

    # Choose tick values based on scale
    x_ticks = _log_ticks(x_min, x_max) if x_scale == 'log' else _nice_ticks(x_min, x_max)
    y_ticks = _log_ticks(y_min, y_max) if y_scale == 'log' else _nice_ticks(y_min, y_max)

    # Grid lines (behind axes)
    if show_grid:
        for tx in x_ticks:
            sx = _to_svg_x(tx)
            objects.append(Line(x1=sx, y1=plot_y, x2=sx, y2=plot_y + plot_height,
                                creation=time, stroke='#333', stroke_width=1))
        for ty in y_ticks:
            sy = _to_svg_y(ty)
            objects.append(Line(x1=plot_x, y1=sy, x2=plot_x + plot_width, y2=sy,
                                creation=time, stroke='#333', stroke_width=1))

    # Axis lines
    objects.append(Line(x1=plot_x, y1=y_zero, x2=plot_x + plot_width, y2=y_zero,
                        creation=time, stroke='#fff', stroke_width=_AXIS_STROKE_WIDTH))
    objects.append(Line(x1=x_zero, y1=plot_y, x2=x_zero, y2=plot_y + plot_height,
                        creation=time, stroke='#fff', stroke_width=_AXIS_STROKE_WIDTH))

    # Ticks and labels for both axes
    def _add_ticks(ticks, scale, to_svg_fn, is_x_axis):
        for val in ticks:
            sv = to_svg_fn(val)
            if is_x_axis:
                objects.append(Line(x1=sv, y1=y_zero - tick_len, x2=sv, y2=y_zero + tick_len,
                                    creation=time, stroke='#fff', stroke_width=_AXIS_STROKE_WIDTH))
            else:
                objects.append(Line(x1=x_zero - tick_len, y1=sv, x2=x_zero + tick_len, y2=sv,
                                    creation=time, stroke='#fff', stroke_width=_AXIS_STROKE_WIDTH))
            if scale != 'log' and abs(val) < 1e-9:
                continue
            label = _format_tick(val, tick_format)
            if is_x_axis:
                objects.append(Text(text=label, x=sv, y=y_zero + tick_len + _TICK_GAP + _TICK_FONT_SIZE * 0.35,
                                    font_size=_TICK_FONT_SIZE, text_anchor='middle',
                                    creation=time, fill='#aaa', stroke_width=0))
            else:
                objects.append(Text(text=label, x=x_zero - tick_len - _TICK_GAP, y=sv + _TICK_FONT_SIZE * 0.35,
                                    font_size=_TICK_FONT_SIZE, text_anchor='end',
                                    creation=time, fill='#aaa', stroke_width=0))
    _add_ticks(x_ticks, x_scale, _to_svg_x, is_x_axis=True)
    _add_ticks(y_ticks, y_scale, _to_svg_y, is_x_axis=False)

    return VCollection(*objects, creation=time)


class Axes(VCollection):
    """Coordinate axes with ticks and labels.

    x_range/y_range: (min, max) in math coordinates (animated via Real attributes).
    x/y/plot_width/plot_height: SVG pixel area for the axes.
    """
    x_min: attributes.Real
    x_max: attributes.Real
    y_min: 'attributes.Real | None'
    y_max: 'attributes.Real | None'
    def __init__(self, x_range=(-5, 5), y_range=None,
                 x=260, y=100, plot_width=1400, plot_height=880,
                 x_label=None, y_label=None,
                 show_grid=False, equal_aspect=False,
                 x_scale='linear', y_scale='linear',
                 tick_format=None, creation=0, z=0):
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
            self._show_grid, time, self._x_scale, self._y_scale, self._tick_format)
        # Include the persistent axis title labels (TexObjects created once)
        for lbl in self._axis_labels:
            coll.objects.append(lbl)
        return coll

    def _get_bounds(self, time=0):
        """Return (xmin, xmax, ymin, ymax) at the given time."""
        return (self.x_min.at_time(time), self.x_max.at_time(time),
                self.y_min.at_time(time), self.y_max.at_time(time))

    def get_plot_area(self):
        """Return (plot_x, plot_y, plot_width, plot_height) for the SVG plot region.

        These are the pixel coordinates of the axes bounding box, set at construction time.
        """
        return (self.plot_x, self.plot_y, self.plot_width, self.plot_height)

    def _math_to_svg_x(self, val, time=0):
        xmin, xmax = self.x_min.at_time(time), self.x_max.at_time(time)
        if self._x_scale == 'log':
            if val <= 0 or xmin <= 0 or xmax <= 0:
                return self.plot_x
            val, xmin, xmax = math.log10(val), math.log10(xmin), math.log10(xmax)
        span = xmax - xmin
        if span == 0:
            span = 1
        return self.plot_x + (val - xmin) / span * self.plot_width

    def _math_to_svg_y(self, val, time=0):
        ymin, ymax = self.y_min.at_time(time), self.y_max.at_time(time)
        if self._y_scale == 'log':
            if val <= 0 or ymin <= 0 or ymax <= 0:
                return self.plot_y + self.plot_height
            val, ymin, ymax = math.log10(val), math.log10(ymin), math.log10(ymax)
        span = ymax - ymin
        if span == 0:
            span = 1
        return self.plot_y + (1 - (val - ymin) / span) * self.plot_height

    def _baseline_y(self, time=0):
        """SVG y-coordinate of y=0 (or bottom edge if 0 is out of range)."""
        ymin, ymax = self.y_min.at_time(time), self.y_max.at_time(time)
        if ymin <= 0 <= ymax and ymax != ymin:
            return self.plot_y + (1 - (0 - ymin) / (ymax - ymin)) * self.plot_height
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

    def add_filled_curve(self, func, x_range=None, color='#58C4DD',
                         opacity=0.3, start=0, end=None, reveal=True, **kwargs):
        """Plot a curve AND its filled area underneath in one call.

        Combines :meth:`add_function` for the curve and :meth:`get_area`
        for the shaded region.  When *reveal* is ``True`` the curve is
        animated with ``draw_along`` and the area fades in over
        ``[start, end]``.

        Parameters
        ----------
        func:
            A callable ``f(x)`` to plot.
        x_range:
            Optional ``(x_min, x_max)`` domain for the curve and area.
        color:
            Stroke colour for the curve and fill colour for the area.
        opacity:
            Fill opacity for the shaded area.
        start:
            Animation start time for the reveal animation.
        end:
            Animation end time.  ``None`` means no animation — the curve
            and area appear instantly at *start*.
        reveal:
            If ``True`` and *end* is not ``None``, animate the curve with
            ``draw_along`` and fade the area in.
        **kwargs:
            Extra keyword arguments forwarded to :meth:`add_function`
            (e.g. ``num_points``, ``stroke_width``).

        Returns
        -------
        VCollection
            A two-element collection ``[curve, area]``.
        """
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
        result = VCollection(curve, area, creation=start)
        return result

    def add_parametric_plot(self, fx, fy, t_range=(0, 1), num_points=100,
                            creation=0, z=0, **styling_kwargs):
        """Plot a parametric curve x=fx(t), y=fy(t).

        Returns a Path object whose ``d`` attribute is recomputed each
        frame so that the curve follows animated axis ranges.

        Parameters
        ----------
        fx:
            Callable mapping parameter t to x math-coordinate.
        fy:
            Callable mapping parameter t to y math-coordinate.
        t_range:
            ``(t_min, t_max)`` parameter range.  Default ``(0, 1)``.
        num_points:
            Number of sample points along the curve.  Default 100.
        creation:
            Creation time of the returned Path.
        z:
            Z-layer ordering.
        **styling_kwargs:
            Extra keyword arguments forwarded to the Path styling
            (e.g. ``stroke``, ``stroke_width``).

        Returns
        -------
        Path
            The curve Path (already appended to this Axes' objects).
        """
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
        style_kw = {'stroke': '#58C4DD', 'stroke_width': 5, 'fill_opacity': 0} | styling_kwargs
        curve = Path('', x=0, y=0, creation=creation, z=z, **style_kw)
        _axes = self
        _fx, _fy = fx, fy
        _t_min, _t_max = t_range
        _np = num_points

        def _compute_d(time):
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

    def plot_piecewise(self, pieces, creation=0, **kwargs):
        """Plot a piecewise function defined by ``[(func, x_min, x_max), ...]``.

        Each *(func, x_min, x_max)* tuple is plotted only over its domain
        using :meth:`add_function` (alias ``plot``).

        Parameters
        ----------
        pieces:
            List of ``(callable, x_min, x_max)`` tuples.
        creation:
            Creation time forwarded to each curve.
        **kwargs:
            Extra keyword arguments forwarded to ``add_function`` for every
            piece (e.g. ``stroke``, ``stroke_width``).

        Returns
        -------
        VGroup
            A VGroup containing all of the individual curve segments.
        """
        from vectormation._base import VGroup
        curves = []
        for func, x_min, x_max in pieces:
            curve = self.add_function(func, x_range=(x_min, x_max),
                                      creation=creation, **kwargs)
            curves.append(curve)
        return VGroup(*curves)

    def animate_draw_function(self, func, start=0, end=1, x_range=None,
                               num_points=200, easing=easings.smooth,
                               creation=0, z=0, **styling_kwargs):
        """Draw a function curve progressively from left to right."""
        _axes = self
        _x_range = x_range
        _easing = easing

        def _make_d(time):
            if _x_range:
                xmin, xmax = _x_range[0], _x_range[1]
            else:
                xmin = _axes.x_min.at_time(time)
                xmax = _axes.x_max.at_time(time)
            dur = end - start
            if dur <= 0:
                progress = 1.0
            else:
                progress = _easing(max(0, min(1, (time - start) / dur)))
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
            d = f'M{pts[0][0]},{pts[0][1]}'
            for sx, sy in pts[1:]:
                d += f'L{sx},{sy}'
            return d

        defaults = {'stroke': '#58C4DD', 'stroke_width': 3, 'fill_opacity': 0} | styling_kwargs
        path = Path('', creation=creation, z=z, **defaults)
        path.d.set_onward(start, _make_d)
        self.objects.append(path)
        return path

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
            sy = self._math_to_svg_y(val, creation) + font_size * TEXT_Y_OFFSET
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
        return self

    def set_x_range(self, x_min, x_max, start=0):
        """Set the x-axis range from start time onward."""
        self.x_min.set_onward(start, x_min)
        self.x_max.set_onward(start, x_max)
        return self

    def set_y_range(self, y_min, y_max, start=0):
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

    def coords_to_point(self, x, y, time=0):
        """Convert math coordinates to SVG pixel coordinates."""
        return (self._math_to_svg_x(x, time), self._math_to_svg_y(y, time))

    def coords_to_screen(self, x, y, time=0):
        """Convert math coordinates to SVG pixel coordinates (alias for :meth:`coords_to_point`)."""
        return self.coords_to_point(x, y, time)

    def screen_to_coords(self, sx, sy, time=0):
        """Convert SVG pixel coordinates to math (axis) coordinates.

        This is the inverse of :meth:`coords_to_point`.  Given a point
        ``(sx, sy)`` in SVG pixel space it returns the corresponding
        ``(x, y)`` math-space coordinates according to the current axis
        ranges.  Log-scale axes are handled correctly.

        Parameters
        ----------
        sx:
            SVG x pixel coordinate.
        sy:
            SVG y pixel coordinate.
        time:
            Animation time at which to read the axis ranges.

        Returns
        -------
        (float, float)
            ``(x, y)`` math-space coordinates.
        """
        # --- X axis ---
        xmin, xmax = self.x_min.at_time(time), self.x_max.at_time(time)
        span_x = xmax - xmin if xmax != xmin else 1
        if self._x_scale == 'log' and xmin > 0 and xmax > 0:
            log_xmin, log_xmax = math.log10(xmin), math.log10(xmax)
            span_x = log_xmax - log_xmin if log_xmax != log_xmin else 1
            x = 10 ** (log_xmin + (sx - self.plot_x) / self.plot_width * span_x)
        else:
            x = xmin + (sx - self.plot_x) / self.plot_width * span_x

        # --- Y axis ---
        ymin, ymax = self.y_min.at_time(time), self.y_max.at_time(time)
        span_y = ymax - ymin if ymax != ymin else 1
        if self._y_scale == 'log' and ymin > 0 and ymax > 0:
            log_ymin, log_ymax = math.log10(ymin), math.log10(ymax)
            span_y = log_ymax - log_ymin if log_ymax != log_ymin else 1
            y = 10 ** (log_ymin + (1 - (sy - self.plot_y) / self.plot_height) * span_y)
        else:
            y = ymin + (1 - (sy - self.plot_y) / self.plot_height) * span_y

        return (x, y)

    def get_plot_center(self, time=0):
        """Return the SVG coordinates of the centre of the visible plot rectangle.

        This is the geometric centre of the pixel area defined by
        ``(plot_x, plot_y, plot_width, plot_height)`` — *not* the axes origin
        (i.e. the point where x=0 and y=0 in math space).

        The result is independent of the current axis ranges; it only depends
        on the SVG layout of the axes widget.

        Parameters
        ----------
        time:
            Animation time (unused for the layout geometry, included for API
            consistency with other axes helpers).

        Returns
        -------
        (float, float)
            ``(cx, cy)`` SVG pixel coordinates of the plot-area centre.

        Examples
        --------
        >>> ax = Axes(x_range=(-5, 5), y_range=(-3, 3))
        >>> cx, cy = ax.get_plot_center()
        >>> # cx == ax.plot_x + ax.plot_width / 2
        >>> # cy == ax.plot_y + ax.plot_height / 2
        """
        cx = self.plot_x + self.plot_width / 2
        cy = self.plot_y + self.plot_height / 2
        return (cx, cy)

    def input_to_graph_point(self, x, func, time=0):
        """Convert a math x-value and function to SVG pixel coordinates: (x, f(x))."""
        return self.coords_to_point(x, func(x), time)

    def get_graph_value(self, func, x, time=0):
        """Evaluate *func* at *x* and return the y-value.

        This is a simple convenience wrapper: ``axes.get_graph_value(f, 3)``
        is equivalent to ``f(3)``, but provides a consistent Axes-based API
        and a natural counterpart to :meth:`input_to_graph_point`.
        """
        return func(x)

    def get_point_on_graph(self, func, x, time=0):
        """Like :meth:`input_to_graph_point` but returns ``None`` on error."""
        try:
            y = func(x)
        except Exception:
            return None
        return self.coords_to_point(x, y, time=time)

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

    def plot_polar(self, func, theta_range=(0, math.tau), num_points=200,
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
        """Plot a line graph from discrete data points. Returns a VCollection.

        The returned VCollection has an ``animate_data`` method that can
        smoothly transition the data points to new values::

            graph = axes.plot_line_graph([1, 2, 3], [1, 4, 9])
            graph.animate_data([1, 2, 3], [2, 5, 7], start=1, end=2)
        """
        style_kw = {'stroke': '#58C4DD', 'stroke_width': 5, 'fill_opacity': 0} | styling_kwargs
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

        def _animate_data(new_x, new_y, start=0, end=1, easing=None):
            """Animate the line graph data to new values over [start, end].

            Parameters
            ----------
            new_x:
                New x data values.
            new_y:
                New y data values.
            start:
                Animation start time.
            end:
                Animation end time.
            easing:
                Easing function (default ``easings.smooth``).

            Returns
            -------
            VCollection
                The same group for chaining.
            """
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

    def plot_bar(self, x_values, y_values, bar_width=0.6, creation=0, z=0, **styling_kwargs):
        """Plot a bar chart inside the axes coordinate system.
        x_values: list of x positions (numeric), y_values: corresponding heights.
        Returns a VCollection of Rectangle objects."""
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

    def get_graph_intersection(self, f1, f2, x_range=None, n=1000):
        """Find approximate intersection points between two functions/curves.

        Returns a list of (math_x, math_y) tuples where f1(x) ~= f2(x).
        Uses sign-change detection with linear interpolation for sub-step accuracy.
        """
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

    def get_area(self, curve_or_func, x_range=None, bounded_graph=None, creation=0, z=0, **styling_kwargs):
        """Create a shaded area under a curve/function (or between two curves).

        *curve_or_func* can be a function, or a Path returned by plot() (which has ._func).
        """
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

    def get_area_value(self, func, x_start, x_end, samples=100):
        """Return the numerical integral of *func* over [x_start, x_end].

        Uses the trapezoidal rule with *samples* equally-spaced intervals.
        This is a pure numerical computation — no visual element is created.

        Parameters
        ----------
        func:
            A callable ``f(x)`` or a curve Path with a ``._func`` attribute
            (as returned by :meth:`plot`).
        x_start, x_end:
            Integration bounds in mathematical (axis) coordinates.
        samples:
            Number of trapezoid intervals (default 100).  More samples give
            a more accurate result.

        Returns
        -------
        float
            The approximate definite integral of *func* from *x_start* to
            *x_end*.

        Examples
        --------
        >>> ax = Axes(...)
        >>> ax.get_area_value(lambda x: x**2, 0, 3)   # approx 9.0
        >>> ax.get_area_value(math.sin, 0, math.pi)   # approx 2.0
        """
        fn = self._resolve_func(func, 'func')
        n = max(int(samples), 2)
        step = (x_end - x_start) / n
        xs = [x_start + i * step for i in range(n + 1)]
        ys = [fn(x) for x in xs]
        return sum(0.5 * (ys[i] + ys[i + 1]) * step for i in range(n))

    def get_integral(self, func, x_start, x_end, samples=200):
        """Alias for :meth:`get_area_value`."""
        return self.get_area_value(func, x_start, x_end, samples=samples)

    def get_average(self, func, x_start=None, x_end=None, samples=200):
        """Return the average value of *func* over [x_start, x_end].

        Computes ``(1 / (x1 - x0)) * integral(func, x0, x1)`` using the
        trapezoidal rule.

        Parameters
        ----------
        func:
            A callable ``f(x)`` or a curve Path with a ``._func`` attribute.
        x_start, x_end:
            Integration bounds in mathematical (axis) coordinates.  Default
            to the current axis x-range at time 0.
        samples:
            Number of trapezoid intervals (default 200).

        Returns
        -------
        float
            The average value of the function over the interval.
        """
        x0 = x_start if x_start is not None else float(self.x_min.at_time(0))
        x1 = x_end if x_end is not None else float(self.x_max.at_time(0))
        if x0 == x1:
            fn = self._resolve_func(func, 'func')
            return fn(x0)
        integral = self.get_area_value(func, x0, x1, samples)
        return integral / (x1 - x0)

    def get_graph_length(self, func, x_start=None, x_end=None, samples=200):
        """Return approximate arc length of *func*'s graph in SVG coordinates.

        Samples the function at *samples* + 1 equally-spaced x values, converts
        each (x, f(x)) to SVG coordinates via :meth:`coords_to_point`, and sums
        the Euclidean distances between consecutive points.  Non-finite values
        are skipped gracefully.

        Parameters
        ----------
        func:
            A callable ``f(x)`` or a curve Path with a ``._func`` attribute
            (as returned by :meth:`plot`).
        x_start, x_end:
            Domain bounds in mathematical (axis) coordinates.  Default to the
            current axis x-range.
        samples:
            Number of line segments to use for the approximation (default 200).

        Returns
        -------
        float
            The approximate arc length in SVG pixels.
        """
        import math as _math
        fn = self._resolve_func(func, 'func')
        x0 = x_start if x_start is not None else self.x_min.at_time(0)
        x1 = x_end if x_end is not None else self.x_max.at_time(0)
        total = 0.0
        prev = None
        for i in range(samples + 1):
            x = x0 + (x1 - x0) * i / samples
            try:
                y = fn(x)
            except Exception:
                prev = None
                continue
            if not _math.isfinite(y):
                prev = None
                continue
            sx, sy = self.coords_to_point(x, y)
            if prev is not None:
                total += _math.hypot(sx - prev[0], sy - prev[1])
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
            except Exception:
                continue
            if not math.isfinite(y):
                continue
            if best_y is None or (y > best_y if is_max else y < best_y):
                best_x, best_y = x, y
        if best_x is None:
            raise ValueError('No finite function values found in the given range.')
        return (best_x, best_y)

    def get_function_max(self, func, x_start, x_end, samples=200):
        """Return ``(x, y)`` where *func* achieves its maximum over [x_start, x_end]."""
        return self._find_extremum(func, x_start, x_end, samples, is_max=True)

    def get_function_min(self, func, x_start, x_end, samples=200):
        """Return ``(x, y)`` where *func* achieves its minimum over [x_start, x_end]."""
        return self._find_extremum(func, x_start, x_end, samples, is_max=False)

    def get_zeros(self, func, x_start, x_end, samples=200):
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
            except Exception:
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
                except Exception:
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
        """Return the first x where func(x) is approximately 0.

        Delegates to :meth:`get_zeros` to find all zero crossings, then
        returns the x coordinate of the first one.  Returns ``None`` if
        no zero is found.

        Parameters
        ----------
        func:
            A callable ``f(x)`` or a curve Path with a ``._func`` attribute.
        x_start, x_end:
            Domain bounds (default to the axis x range).
        """
        if x_start is None:
            x_start = float(self.x_min.at_time(0))
        if x_end is None:
            x_end = float(self.x_max.at_time(0))
        zeros = self.get_zeros(func, x_start, x_end)
        if zeros:
            return zeros[0][0]
        return None

    def get_y_intercept(self, func):
        """Return func(0) — the y-intercept.

        Evaluates the function at x = 0 and returns the result.  Returns
        ``None`` if the function raises an exception at x = 0 (e.g. for
        functions undefined at the origin).

        Parameters
        ----------
        func:
            A callable ``f(x)`` or a curve Path with a ``._func`` attribute.
        """
        fn = self._resolve_func(func, 'func')
        try:
            return fn(0)
        except Exception:
            return None

    def get_derivative(self, func, x_val, h=0.001):
        """Return the numerical derivative of *func* at *x_val*.

        Uses the symmetric central-difference formula::

            f'(x) ≈ (f(x + h) - f(x - h)) / (2h)

        This is a pure numerical computation — no visual element is created.

        Parameters
        ----------
        func:
            A callable ``f(x)`` or a curve Path with a ``._func`` attribute
            (as returned by :meth:`plot`).
        x_val:
            The x value at which to evaluate the derivative (in mathematical
            axis coordinates).
        h:
            Step size for the central-difference approximation (default
            ``0.001``).  Smaller values give more accurate results for smooth
            functions but may amplify floating-point noise.

        Returns
        -------
        float
            The approximate derivative f'(x_val).

        Examples
        --------
        >>> ax = Axes(x_range=(-5, 5), y_range=(-5, 5))
        >>> ax.get_derivative(lambda x: x**2, 3.0)   # approx 6.0
        >>> ax.get_derivative(math.sin, 0.0)          # approx 1.0
        """
        fn = self._resolve_func(func, 'func')
        return (fn(x_val + h) - fn(x_val - h)) / (2 * h)

    def get_slope(self, func, x_val, h=0.001):
        """Alias for :meth:`get_derivative`."""
        return self.get_derivative(func, x_val, h=h)

    def get_secant_slope(self, func, x, dx):
        """Return the secant slope ``(f(x + dx) - f(x)) / dx``."""
        if dx == 0:
            raise ValueError("dx must not be zero")
        fn = self._resolve_func(func, 'func')
        return (fn(x + dx) - fn(x)) / dx

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

    def get_area_between(self, func1, func2, x_range=None, creation=0, z=0, **styling_kwargs):
        """Shade the area between two functions.
        func1, func2: callables. The area between them is shaded.
        x_range: optional (min, max) to limit domain.
        Returns a Path object."""
        style_kw = _AREA_STYLE | styling_kwargs
        return self.get_area(func1, bounded_graph=func2, x_range=x_range,
                             creation=creation, z=z, **style_kw)

    def shade_between(self, func1, func2, x_range=None, color='#58C4DD',
                      opacity=0.2, creation=0, z=0, **styling_kwargs):
        """Shade the region between two functions.

        A convenience wrapper around :meth:`get_area_between` that accepts
        *color* and *opacity* as top-level parameters.  Both *func1* and
        *func2* may be callables or curve objects returned by :meth:`plot`.

        Parameters
        ----------
        func1, func2:
            Callables ``f(x)`` or curve Paths with ``._func`` attribute.
        x_range:
            Optional ``(min, max)`` to limit the shaded domain.
        color:
            Fill color (default ``'#58C4DD'``).
        opacity:
            Fill opacity (default 0.2).
        creation:
            Creation time.
        z:
            Z-layer.
        **styling_kwargs:
            Additional styling forwarded to the Path.

        Returns
        -------
        Path
            The filled area Path (already added to the axes).
        """
        kw = {'fill': color, 'fill_opacity': opacity} | styling_kwargs
        return self.get_area_between(func1, func2, x_range=x_range,
                                     creation=creation, z=z, **kw)

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
        """Add a labeled dot at math coordinates (x, y). Returns (dot, label_text).
        If no label is given, label_text is None."""
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
            lbl.x.set_onward(creation,
                lambda t, _x=x, _y=y, _ox=_ox: self.coords_to_point(_x, _y, t)[0] + _ox)
            lbl.y.set_onward(creation,
                lambda t, _x=x, _y=y, _oy=_oy: self.coords_to_point(_x, _y, t)[1] + _oy)
            self._add_plot_obj(lbl)
        return dot, lbl

    def add_point_label(self, x, y, text=None, dot_radius=6, font_size=20, buff=10,
                        creation=0, **kwargs) -> 'tuple[Dot, Text]':
        """Add a dot at math coordinates (x, y) with an optional text label.

        text: label string.  If None, defaults to '(x, y)' format.
        buff: pixel offset above the dot for the label.
        Returns (dot, label).
        """
        if text is None:
            text = f'({x:g}, {y:g})'
        dot_color = kwargs.pop('dot_color', '#FF6B6B')
        return self.add_dot_label(x, y, label=str(text),  # type: ignore[return-value]
                                  dot_color=dot_color, dot_radius=dot_radius,
                                  label_offset=(0, -dot_radius - buff),
                                  font_size=font_size, creation=creation,
                                  z=kwargs.pop('z', 0))

    def add_labeled_points(self, points, dot_color='#FF6B6B', dot_radius=6,
                            font_size=14, creation=0, z=1):
        """Add multiple labeled dots to the axes.

        points: list of (x, y, label) tuples in math coordinates.
        Returns VCollection of all dots and labels.
        """
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

    def add_marked_region(self, x1, x2, color='#FFFF00', opacity=0.2, creation=0, z=0):
        """Highlight a vertical region on the axes between x1 and x2.

        Returns the Rectangle highlight.
        """
        sx1 = self._math_to_svg_x(x1)
        sx2 = self._math_to_svg_x(x2)
        rect = Rectangle(
            width=abs(sx2 - sx1), height=self.plot_height,
            x=min(sx1, sx2), y=self.plot_y,
            fill=color, fill_opacity=opacity, stroke_width=0,
            creation=creation, z=z)
        self._add_plot_obj(rect)
        return rect

    def add_labeled_point(self, x, y, label=None, dot_radius=5, direction='above',
                          creation=0, **kwargs):
        """Add a Dot at (*x*, *y*) with an optional directional Text label."""
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
            lbl.x.set_onward(creation,
                lambda t, _x=x, _y=y, _ox=ox: self.coords_to_point(_x, _y, t)[0] + _ox)
            lbl.y.set_onward(creation,
                lambda t, _x=x, _y=y, _oy=oy: self.coords_to_point(_x, _y, t)[1] + _oy)
            self._add_plot_obj(lbl)
            objs.append(lbl)
        return VCollection(*objs, creation=creation, z=z)

    def add_function_region(self, func, x_range=None, label=None,
                            color='#58C4DD', opacity=0.2, creation=0):
        """Plot a function and shade the area under it in one call.

        This is a convenience method that combines :meth:`plot` and
        :meth:`get_area`.

        Parameters
        ----------
        func:
            A callable ``f(x)`` to plot.
        x_range:
            Optional ``(x_min, x_max)`` domain restriction for the curve
            and the shaded area.
        label:
            Optional label string passed to :meth:`plot`.
        color:
            Stroke colour for the curve and fill colour for the area
            (default ``'#58C4DD'``).
        opacity:
            Fill opacity for the shaded area (default ``0.2``).
        creation:
            Creation time for all created objects.

        Returns
        -------
        Path
            The filled area Path returned by :meth:`get_area`.
        """
        self.add_function(func, label=label, x_range=x_range,
                          creation=creation, stroke=color)
        area = self.get_area(func, x_range=x_range, creation=creation,
                             fill=color, fill_opacity=opacity, stroke_width=0)
        return area

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
        arrow = _get_arrow()(x1=ax1, y1=ay1, x2=ax2, y2=ay2,
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

    def add_callout(self, x, y, text, offset_x=60, offset_y=-60,
                    font_size=18, box_padding=8, corner_radius=4,
                    creation=0, z=5, **styling_kwargs):
        """Add a floating text callout box with a line pointing to a data point.

        Unlike :meth:`add_arrow_annotation` (which uses a full arrow with a tip),
        ``add_callout`` draws a plain leader line from the box to the data point,
        making it suitable for dense charts where arrowheads would clutter the view.

        Parameters
        ----------
        x, y:
            Data coordinates of the point to annotate.
        text:
            Label text shown inside the callout box.
        offset_x, offset_y:
            Pixel offset of the callout box centre from the data point.
            Positive x is right, positive y is down (SVG convention).
        font_size:
            Font size for the label text.
        box_padding:
            Padding inside the callout box around the text.
        corner_radius:
            Corner radius of the callout box rectangle.
        creation:
            Appearance time.
        z:
            Draw order.
        **styling_kwargs:
            Overrides for the default box and text colors.

        Returns
        -------
        VCollection with (leader_line, box, label).
        """
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

        # Label centred in the box
        lbl = Text(text=text, x=sx + offset_x, y=sy + offset_y,
                   font_size=font_size, text_anchor='middle',
                   fill=text_color, stroke_width=0,
                   creation=creation, z=z + 0.2)

        # Make all elements track the data point dynamically
        _ox, _oy = offset_x, offset_y
        _ew, _eh = est_w, est_h
        _pad = box_padding

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

    def add_animation_trace(self, func, x_start, x_end, start=0, end=1,
                             dot=True, trail=True, color='#FFFF00', **kwargs):
        """Combined convenience: moving dot on a function curve with trailing path.

        Internally uses :meth:`add_cursor` for the dot and :meth:`add_trace`
        for the trail, coordinating their timing.

        Parameters
        ----------
        func:
            The function ``f(x) -> y`` to trace.
        x_start, x_end:
            Math x-range for the animation.
        start, end:
            Animation time range.
        dot:
            If *True* (default), show a moving dot on the curve.
        trail:
            If *True* (default), draw a trailing path behind the dot.
        color:
            Color for both the dot and trail (default ``'#FFFF00'``).
        **kwargs:
            Extra keyword arguments forwarded to ``add_cursor``/``add_trace``
            (e.g. ``r``, ``trail_width``, ``easing``).

        Returns
        -------
        self
        """
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
        style_kw = _HIGHLIGHT_STYLE | styling_kwargs
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
        style_kw = _HIGHLIGHT_STYLE | styling_kwargs
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

    def add_horizontal_band(self, y1, y2, color='#FFFF00', opacity=0.2, creation=0):
        """Add a shaded horizontal band between y-values *y1* and *y2*.

        The band spans the full x-range of the axes and respects animated
        axis ranges via :meth:`coords_to_point`.  Delegates to
        :meth:`highlight_y_range` with the given styling.

        Parameters
        ----------
        y1, y2:
            Vertical math-coordinate bounds of the band.
        color:
            Fill color.  Default ``'#FFFF00'`` (yellow).
        opacity:
            Fill opacity.  Default ``0.15``.
        creation:
            Appearance time (seconds).

        Returns
        -------
        Rectangle
            The band rectangle (already added to the axes objects).
        """
        return self.highlight_y_range(y1, y2, creation=creation, z=-1,
                                      fill=color, fill_opacity=opacity, stroke_width=0)

    def shade_region(self, x_start, x_end, y_start=None, y_end=None,
                     creation=0, z=-1, **styling_kwargs):
        """Shade an axis-aligned rectangular region in math coordinates.

        More flexible than :meth:`highlight_x_range` / :meth:`highlight_y_range`:

        * If only *x_start* / *x_end* are given the region spans the full plot
          height (same as ``highlight_x_range``).
        * If only *y_start* / *y_end* are given (pass ``x_start=None``) the
          region spans the full plot width (same as ``highlight_y_range``).
        * When all four bounds are supplied, a rectangle is drawn that is
          constrained in both axes simultaneously.

        Parameters
        ----------
        x_start, x_end:
            Horizontal bounds in math coordinates.  Pass ``None`` for either
            to span the full plot width.
        y_start, y_end:
            Vertical bounds in math coordinates.  Default ``None`` spans the
            full plot height.
        creation:
            Appearance time (seconds).
        z:
            Draw order.
        **styling_kwargs:
            Overrides for the default highlight fill style.

        Returns
        -------
        Rectangle
        """
        style_kw = _HIGHLIGHT_STYLE | styling_kwargs
        rect = Rectangle(width=0, height=0, x=0, y=0, creation=creation, z=z, **style_kw)
        _xs, _xe = x_start, x_end
        _ys, _ye = y_start, y_end

        if _xs is None or _xe is None:
            # Full-width: span the entire plot horizontally
            rect.x.set_onward(creation, lambda t: self.plot_x)
            rect.width.set_onward(creation, lambda t: self.plot_width)
        else:
            rect.x.set_onward(creation,
                lambda t, _a=_xs, _b=_xe: min(
                    self._math_to_svg_x(_a, t), self._math_to_svg_x(_b, t)))
            rect.width.set_onward(creation,
                lambda t, _a=_xs, _b=_xe: abs(
                    self._math_to_svg_x(_b, t) - self._math_to_svg_x(_a, t)))

        if _ys is None or _ye is None:
            # Full-height: span the entire plot vertically
            rect.y.set_onward(creation, lambda t: self.plot_y)
            rect.height.set_onward(creation, lambda t: self.plot_height)
        else:
            rect.y.set_onward(creation,
                lambda t, _a=_ys, _b=_ye: min(
                    self._math_to_svg_y(_a, t), self._math_to_svg_y(_b, t)))
            rect.height.set_onward(creation,
                lambda t, _a=_ys, _b=_ye: abs(
                    self._math_to_svg_y(_b, t) - self._math_to_svg_y(_a, t)))

        self._add_plot_obj(rect)
        return rect

    def animate_range(self, start, end, x_range=None, y_range=None, easing=easings.smooth):
        """Animate the axis range to new bounds.
        x_range: (new_xmin, new_xmax) or None to keep current.
        y_range: (new_ymin, new_ymax) or None to keep current."""
        dur = end - start
        if dur <= 0:
            return self
        _d = max(dur, 1e-9)
        if x_range is not None:
            self.x_min.set(start, end,
                _lerp(start, _d, self.x_min.at_time(start), x_range[0], easing), stay=True)
            self.x_max.set(start, end,
                _lerp(start, _d, self.x_max.at_time(start), x_range[1], easing), stay=True)
        if y_range is not None and self.y_min is not None:
            self.y_min.set(start, end,
                _lerp(start, _d, self.y_min.at_time(start), y_range[0], easing), stay=True)
            self.y_max.set(start, end,
                _lerp(start, _d, self.y_max.at_time(start), y_range[1], easing), stay=True)
        return self

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

    def add_area_label(self, func, x_start=None, x_end=None, x_range=None,
                        text=None, font_size=20,
                        creation=0, z=3, samples=100, **styling_kwargs):
        """Add a label showing the numerical area under the curve between x_start and x_end.

        The label is positioned at the centroid of the region, and if *text* is
        ``None`` the numerical area value (computed by the trapezoidal rule) is
        displayed automatically.

        Parameters
        ----------
        func:
            A callable ``f(x)`` or a curve object with a ``._func`` attribute.
        x_start, x_end:
            Integration bounds.  You may alternatively pass *x_range* as a
            two-element sequence; ``x_start``/``x_end`` take precedence when
            both forms are provided.  Defaults to the current axis x-range.
        x_range:
            Legacy two-element ``[xlo, xhi]`` form; kept for backwards
            compatibility.  Superseded by *x_start*/*x_end*.
        text:
            Override the displayed string.  When ``None`` the area is computed
            and formatted as ``"A = <value>"``.
        font_size:
            Font size for the label (default 20).
        creation:
            Time at which the label appears.
        samples:
            Number of equally-spaced trapezoids used for integration and
            centroid estimation (default 100).

        Returns
        -------
        Text
            The label object, already added to the axes.
        """
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

    def get_dashed_line(self, x1, y1, x2, y2, creation=0, z=0, **styling_kwargs):
        """Draw a dashed line between two math coordinate points.
        Returns a Line object."""
        style_kw = {'stroke': '#aaa', 'stroke_width': 2, 'stroke_dasharray': '6 4'} | styling_kwargs
        return self.get_line_from_to(x1, y1, x2, y2, creation=creation, z=z, **style_kw)

    def add_title(self, text, font_size=32, buff=20, creation=0, z=5, **styling_kwargs):
        """Add a title above the axes. Returns the Text object."""
        style_kw = {'fill': '#ddd', 'stroke_width': 0} | styling_kwargs
        cx = self.get_plot_center()[0]
        ty = self.plot_y - buff
        lbl = Text(text=text, x=cx, y=ty, font_size=font_size,
                    text_anchor='middle', creation=creation, z=z, **style_kw)
        self._add_plot_obj(lbl)
        return lbl

    def add_text_annotation(self, x, y, text, creation=0, z=0, font_size=16,
                             dx=40, dy=-40, color='#fff', arrow_color='#888'):
        """Add a text annotation with a line pointing to (x, y) in math coordinates.
        dx, dy: offset of the text from the point (in pixels).
        Returns a VCollection with the line and text (added to canvas)."""
        from vectormation._base import VCollection

        line = Line(x1=0, y1=0, x2=0, y2=0,
                    creation=creation, z=z, stroke=arrow_color, stroke_width=1)
        line.p1.set_onward(creation,
            lambda t, _x=x, _y=y, _dx=dx, _dy=dy:
                (self.coords_to_point(_x, _y, t)[0] + _dx,
                 self.coords_to_point(_x, _y, t)[1] + _dy))
        line.p2.set_onward(creation,
            lambda t, _x=x, _y=y: self.coords_to_point(_x, _y, t))

        label = Text(text=str(text), x=0, y=0, font_size=font_size,
                     fill=color, stroke_width=0, text_anchor='middle',
                     creation=creation, z=z + 0.1)
        label.x.set_onward(creation,
            lambda t, _x=x, _y=y, _dx=dx:
                self.coords_to_point(_x, _y, t)[0] + _dx)
        label.y.set_onward(creation,
            lambda t, _x=x, _y=y, _dy=dy, _fs=font_size:
                self.coords_to_point(_x, _y, t)[1] + _dy - _fs)

        group = VCollection(line, label, creation=creation, z=z)
        self._add_plot_obj(group)
        return group

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

    def _make_span_line(self, value, direction, creation, z, style_kw):
        """Create a Line spanning the full plot along one axis at a given math value.
        direction: 'vertical' (x=value) or 'horizontal' (y=value)."""
        line = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z, **style_kw)
        _v = value
        if direction == 'vertical':
            line.p1.set_onward(creation, lambda t, _v=_v: (self._math_to_svg_x(_v, t), self.plot_y))
            line.p2.set_onward(creation, lambda t, _v=_v: (self._math_to_svg_x(_v, t), self.plot_y + self.plot_height))
        else:
            line.p1.set_onward(creation, lambda t, _v=_v: (self.plot_x, self._math_to_svg_y(_v, t)))
            line.p2.set_onward(creation, lambda t, _v=_v: (self.plot_x + self.plot_width, self._math_to_svg_y(_v, t)))
        return line

    def add_asymptote(self, value, direction='vertical', creation=0, z=0, **styling_kwargs):
        """Draw a dashed asymptote line spanning the full plot range.
        direction: 'vertical' (x=value) or 'horizontal' (y=value).
        Returns a Line object."""
        style_kw = {'stroke': '#aaa', 'stroke_width': 1.5,
                    'stroke_dasharray': '8 4'} | styling_kwargs
        line = self._make_span_line(value, direction, creation, z, style_kw)
        self._add_plot_obj(line)
        return line

    def add_vertical_asymptote(self, x_val, creation=0, **kwargs):
        """Add a vertical dashed asymptote at *x_val*."""
        return self.add_asymptote(x_val, direction='vertical', creation=creation, **kwargs)

    def add_horizontal_asymptote(self, y_val, creation=0, **kwargs):
        """Add a horizontal dashed asymptote at *y_val*."""
        return self.add_asymptote(y_val, direction='horizontal', creation=creation, **kwargs)

    def _add_guide_line(self, value, direction, start, end, creation, z, styling_kwargs):
        """Shared helper for add_horizontal_line / add_vertical_line."""
        style_kw = {'stroke': '#FFFF00', 'stroke_width': 1.5,
                    'stroke_dasharray': '6 3'} | styling_kwargs
        line = self._make_span_line(value, direction, creation, z, style_kw)
        self._add_plot_obj(line)
        if start is not None and end is not None:
            line.fadein(start=start, end=end)
        return line

    def add_horizontal_line(self, y, start=None, end=None, creation=0, z=1, **styling_kwargs):
        """Draw a horizontal dashed guide line at *y*."""
        return self._add_guide_line(y, 'horizontal', start, end, creation, z, styling_kwargs)

    def add_vertical_line(self, x, start=None, end=None, creation=0, z=1, **styling_kwargs):
        """Draw a vertical dashed guide line at *x*."""
        return self._add_guide_line(x, 'vertical', start, end, creation, z, styling_kwargs)

    def add_min_max_labels(self, func, x_range=None, samples=200, creation=0, z=3,
                            dot_radius=5, font_size=18, **styling_kwargs):
        """Find and label local min/max of func within x_range.
        Returns a VCollection of (dot, label) pairs."""
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
            offset_y = -15 if kind == 'max' else 20
            lbl_text = f'{kind}({mx:.1f}, {my:.1f})'
            dot, lbl = self._make_plot_dot_label(
                mx, my, lbl_text, offset_y, creation, z,
                dot_radius, font_size, color)
            objs.extend([dot, lbl])
        return VCollection(*objs, creation=creation, z=z)

    def _scan_sign_changes(self, deriv_func, eval_func, x_range, samples,
                           creation, classify=False):
        """Sample *deriv_func* and find x-values where it changes sign.

        Returns a list of ``(x, y)`` tuples (or ``(x, y, type)`` when
        *classify* is True, with type ``'min'``/``'max'`` based on the
        sign direction of the change).  *eval_func* is called to get the
        y-value at each detected crossing.
        """
        xlo = x_range[0] if x_range else self.x_min.at_time(creation)
        xhi = x_range[1] if x_range else self.x_max.at_time(creation)
        step = (xhi - xlo) / samples
        xs = [xlo + i * step for i in range(samples + 1)]
        ds = []
        for x in xs:
            try:
                d = deriv_func(x)
                ds.append(d if math.isfinite(d) else None)
            except Exception:
                ds.append(None)

        results = []
        for i in range(len(ds) - 1):
            if ds[i] is None or ds[i + 1] is None:
                continue
            cx = None
            sign_ref = None  # value whose sign determines classification
            if ds[i] * ds[i + 1] < 0:
                denom = abs(ds[i]) + abs(ds[i + 1])
                t = abs(ds[i]) / denom if denom > 0 else 0.5
                cx = xs[i] + t * step
                sign_ref = ds[i]
            elif abs(ds[i]) < 1e-8 and i > 0:
                if ds[i - 1] is not None and ds[i + 1] is not None and ds[i - 1] * ds[i + 1] < 0:
                    cx = xs[i]
                    sign_ref = ds[i - 1]
            if cx is not None:
                try:
                    cy = eval_func(cx)
                except Exception:
                    continue
                if not math.isfinite(cy):
                    continue
                if classify:
                    results.append((cx, cy, 'max' if sign_ref > 0 else 'min'))
                else:
                    results.append((cx, cy))
        return results

    def _make_plot_dot_label(self, mx, my, label_text, offset_y, creation, z,
                             dot_radius, font_size, fill_color):
        """Create an animated Dot + Text at math coords (mx, my).

        Returns ``(dot, label)`` and registers both via ``_add_plot_obj``.
        """
        sx, sy = self.coords_to_point(mx, my, creation)
        dot = Dot(cx=sx, cy=sy, r=dot_radius, fill=fill_color,
                  creation=creation, z=z + 1)
        dot.c.set_onward(creation,
            lambda t, _cx=mx, _cy=my: self.coords_to_point(_cx, _cy, t))
        lbl = Text(text=label_text, x=sx, y=sy + offset_y,
                   font_size=font_size, fill=fill_color, stroke_width=0,
                   text_anchor='middle', creation=creation, z=z + 2)
        lbl.x.set_onward(creation,
            lambda t, _cx=mx, _cy=my: self.coords_to_point(_cx, _cy, t)[0])
        lbl.y.set_onward(creation,
            lambda t, _cx=mx, _cy=my, _oy=offset_y: self.coords_to_point(_cx, _cy, t)[1] + _oy)
        self._add_plot_obj(dot)
        self._add_plot_obj(lbl)
        return dot, lbl

    def add_inflection_points(self, func, x_range=None, samples=200, h=1e-5,
                              creation=0, z=3, dot_radius=5, font_size=18,
                              color='#FFA726', **styling_kwargs):
        """Find and label inflection points of *func* within *x_range*.

        An inflection point is where the second derivative changes sign.  This
        method numerically approximates the second derivative at evenly-spaced
        sample points and detects sign changes.

        Parameters
        ----------
        func:
            A callable ``f(x) -> y``.
        x_range:
            ``(x_min, x_max)`` in math coordinates.  Defaults to the current
            axis range.
        samples:
            Number of sample points for scanning (default 200).
        h:
            Step size for the numerical second derivative (default 1e-5).
        creation:
            Creation time for the resulting objects.
        z:
            Z-index for the dots and labels.
        dot_radius:
            Radius of the marker dots (default 5).
        font_size:
            Font size for the labels (default 18).
        color:
            Default colour for dots and labels (default '#FFA726', orange).
        **styling_kwargs:
            Extra styling overrides (e.g. ``fill``).

        Returns
        -------
        VCollection
            A collection of (dot, label) pairs for each inflection point found.
        """
        def _f2(x):
            return (func(x + h) - 2 * func(x) + func(x - h)) / (h * h)

        inflections = self._scan_sign_changes(_f2, func, x_range, samples, creation)
        fill_color = styling_kwargs.get('fill', color)
        objs = []
        for ix, iy in inflections:
            dot, lbl = self._make_plot_dot_label(
                ix, iy, f'({ix:.2f}, {iy:.2f})', -15,
                creation, z, dot_radius, font_size, fill_color)
            objs.extend([dot, lbl])
        return VCollection(*objs, creation=creation, z=z)

    def get_critical_points(self, func, x_range=None, samples=200, h=1e-5,
                            creation=0, z=3, dot_radius=5, font_size=18,
                            color='#E040FB', label_type='both',
                            **styling_kwargs):
        """Find and mark critical points (local minima and maxima) of *func*.

        A critical point is where the first derivative changes sign.  This
        method numerically approximates the derivative at evenly-spaced
        sample points, detects sign changes, and classifies each as a
        local minimum (negative-to-positive) or local maximum
        (positive-to-negative).

        Parameters
        ----------
        func:
            A callable ``f(x) -> y`` or a curve returned by :meth:`plot`.
        x_range:
            ``(x_min, x_max)`` in math coordinates.  Defaults to the current
            axis range.
        samples:
            Number of sample points for scanning (default 200).
        h:
            Step size for the numerical derivative (default 1e-5).
        creation:
            Creation time for the resulting objects.
        z:
            Z-index for the dots and labels.
        dot_radius:
            Radius of the marker dots (default 5).
        font_size:
            Font size for the labels (default 18).
        color:
            Default colour for dots and labels (default '#E040FB', purple).
        label_type:
            What to show in labels: ``'coords'`` for ``(x, y)`` values,
            ``'type'`` for ``'min'``/``'max'``, or ``'both'`` (default)
            for type and coordinates.
        **styling_kwargs:
            Extra styling overrides (e.g. ``fill``).

        Returns
        -------
        VCollection
            A collection of (dot, label) pairs for each critical point found.
            Each dot has a ``._critical_type`` attribute set to ``'min'`` or
            ``'max'``.
        """
        fn = self._resolve_func(func, 'func')

        def _deriv(x):
            return (fn(x + h) - fn(x - h)) / (2 * h)

        criticals = self._scan_sign_changes(_deriv, fn, x_range, samples,
                                            creation, classify=True)
        fill_color = styling_kwargs.get('fill', color)
        objs = []
        for cx, cy, ctype in criticals:
            if label_type == 'coords':
                lbl_text = f'({cx:.2f}, {cy:.2f})'
            elif label_type == 'type':
                lbl_text = ctype
            else:
                lbl_text = f'{ctype} ({cx:.2f}, {cy:.2f})'
            offset_y = 15 if ctype == 'min' else -15
            dot, lbl = self._make_plot_dot_label(
                cx, cy, lbl_text, offset_y,
                creation, z, dot_radius, font_size, fill_color)
            dot._critical_type = ctype
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
            lbl = Text(text=f'{val:.1f}', x=lx, y=ly + font_size * TEXT_Y_OFFSET,
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
            colors = list(DEFAULT_CHART_COLORS)
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
        style_kw = _AREA_STYLE | styling_kwargs
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
        # 'horizontal' = y=value, 'vertical' = x=value — same convention as add_asymptote
        line = self._make_span_line(y, direction, creation, z, style_kw)
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
                    lambda t, _v=y: self._math_to_svg_y(_v, t) + font_size * TEXT_Y_OFFSET)
            else:
                lbl = Text(text=str(label),
                           x=0, y=self.plot_y - 5,
                           font_size=font_size, fill=lbl_color, stroke_width=0,
                           text_anchor='middle', creation=creation, z=z + 0.1)
                lbl.x.set_onward(creation,
                    lambda t, _v=y: self._math_to_svg_x(_v, t))
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
        style_kw = _HIGHLIGHT_STYLE | styling_kwargs
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
        style_kw = _HIGHLIGHT_STYLE | styling_kwargs
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
            return sum(math.exp(-0.5 * ((xv - d) / h) ** 2) for d in data) / (n * h * math.sqrt(math.tau))
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

    def add_label(self, x_coord, y_coord, text, offset=(0, -25), font_size=18,
                  creation=0, z=5, **styling_kwargs):
        """Add a text label at data coordinates (x_coord, y_coord).
        offset: (dx, dy) pixel offset from the point. Returns the Text object."""
        style_kw = {'fill': '#fff', 'stroke_width': 0, 'text_anchor': 'middle'} | styling_kwargs
        _xc, _yc = x_coord, y_coord
        ox, oy = offset
        lbl = Text(text=str(text), x=0, y=0, font_size=font_size,
                   creation=creation, z=z, **style_kw)
        lbl.x.set_onward(creation, lambda t: self.coords_to_point(_xc, _yc, t)[0] + ox)
        lbl.y.set_onward(creation, lambda t: self.coords_to_point(_xc, _yc, t)[1] + oy)
        self._add_plot_obj(lbl)
        return lbl

    def add_dot(self, x_coord, y_coord, r=6, creation=0, z=5, **styling_kwargs):
        """Add a dot at data coordinates (x_coord, y_coord). Returns the Dot."""
        style_kw = {'fill': '#FFFF00', 'fill_opacity': 1, 'stroke_width': 0} | styling_kwargs
        _xc, _yc = x_coord, y_coord
        dot = Dot(r=r, cx=0, cy=0, creation=creation, z=z, **style_kw)
        dot.c.set_onward(creation, lambda t: self.coords_to_point(_xc, _yc, t))
        self._add_plot_obj(dot)
        return dot

    def add_annotation(self, x, y, text, start=0, end=None, **kwargs):
        """Add a text annotation at graph coordinates (x, y).

        This is a convenience wrapper around :meth:`add_point_label`.

        Parameters
        ----------
        x, y:
            Math coordinates where the annotation should appear.
        text:
            The label text to display.
        start:
            Creation time (alias for the *creation* parameter).
        end:
            Unused — accepted for API consistency but ignored.
        **kwargs:
            Extra keyword arguments forwarded to :meth:`add_point_label`
            (e.g. ``dot_radius``, ``font_size``, ``buff``).
        """
        kwargs.setdefault('creation', start)
        return self.add_point_label(x, y, text=text, **kwargs)

    def add_annotation_box(self, x_coord, y_coord, text, box_width=120, box_height=40,
                            offset=(60, -60), font_size=14, creation=0, z=5, **styling_kwargs):
        """Add a text box with an arrow pointing to (x_coord, y_coord).
        offset: (dx, dy) from the point to the box center.
        Returns a VCollection with arrow, box, and label."""

        style_kw = {'fill': '#ddd', 'stroke_width': 0} | styling_kwargs
        ox, oy = offset
        # Point SVG coordinates
        _xc, _yc = x_coord, y_coord
        def _pt(t):
            return self.coords_to_point(_xc, _yc, t)
        # Arrow from point to box edge
        arr = _get_arrow()(x1=0, y1=0, x2=0, y2=0, stroke='#aaa', stroke_width=1.5,
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
        lbl.y.set_onward(creation, lambda t, _oy=oy: _pt(t)[1] + _oy + font_size * TEXT_Y_OFFSET)
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
                arr = _get_arrow()(x1=0, y1=0, x2=1, y2=0,
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
        arrow = _get_arrow()(x1=sx1, y1=sy1, x2=sx2, y2=sy2,
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

    def get_horizontal_lines(self, y_values, x_start=None, x_end=None, creation=0, z=1, **kwargs):
        """Draw horizontal lines at specified y_values across the plot area.

        y_values: list of y math-coordinates at which to draw horizontal lines.
        x_start: left x math-coordinate for the lines (defaults to x_min).
        x_end: right x math-coordinate for the lines (defaults to x_max).
        Returns a VCollection of Line objects."""
        style_kw = {'stroke': '#aaa', 'stroke_width': 1,
                    'stroke_dasharray': '4 3'} | kwargs
        lines = []
        for yv in y_values:
            line = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z, **style_kw)
            _yv = yv
            _x_start = x_start
            _x_end = x_end
            def _p1(t, _yv=_yv, _x_start=_x_start):
                sy = self._math_to_svg_y(_yv, t)
                sx = self._math_to_svg_x(_x_start, t) if _x_start is not None else self.plot_x
                return (sx, sy)
            def _p2(t, _yv=_yv, _x_end=_x_end):
                sy = self._math_to_svg_y(_yv, t)
                sx = self._math_to_svg_x(_x_end, t) if _x_end is not None else self.plot_x + self.plot_width
                return (sx, sy)
            line.p1.set_onward(creation, _p1)
            line.p2.set_onward(creation, _p2)
            self._add_plot_obj(line)
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
                arrows.append(_get_arrow()(x1=sx1, y1=sy1, x2=sx2, y2=sy2,
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

    def add_tangent_at(self, func, x_val, length=200, creation=0, **kwargs):
        """Alias for :meth:`get_tangent_line` that adds the line to the axes."""
        return self.get_tangent_line(func, x_val, length=length, creation=creation, **kwargs)

    def get_secant_line(self, func, x1, x2, length=300, creation=0, z=0, **styling_kwargs):
        """Draw a secant line through func at x1 and x2. Returns a Line."""
        style_kw = {'stroke': '#83C167', 'stroke_width': 2} | styling_kwargs
        line = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z, **style_kw)
        _x1, _x2, _len = x1, x2, length
        def _secant_endpoint(sign):
            def _pt(t, _x1=_x1, _x2=_x2, _len=_len, _sign=sign):
                sx1, sy1 = self.coords_to_point(_x1, func(_x1), t)
                sx2, sy2 = self.coords_to_point(_x2, func(_x2), t)
                dx, dy = sx2 - sx1, sy2 - sy1
                mag = max(math.hypot(dx, dy), 1e-9)
                half = _len / 2
                mx, my = (sx1 + sx2) / 2, (sy1 + sy2) / 2
                return (mx + _sign * dx / mag * half, my + _sign * dy / mag * half)
            return _pt
        line.p1.set_onward(creation, _secant_endpoint(-1))
        line.p2.set_onward(creation, _secant_endpoint(+1))
        self._add_plot_obj(line)
        return line

    def get_intersection_point(self, func1, func2, x_range, tol=0.01):
        """Find the x-value where two functions intersect using bisection.

        Searches for a root of ``func1(x) - func2(x)`` on *x_range* = (a, b).
        Requires that the difference changes sign across the interval (i.e. the
        functions cross at least once inside it).

        Parameters
        ----------
        func1, func2:
            Callables that each accept a single float x and return a float y.
        x_range:
            A ``(a, b)`` tuple defining the search interval.
        tol:
            Convergence tolerance on the x-axis.  Iteration stops when the
            interval width is smaller than *tol*.

        Returns
        -------
        (x, y) tuple
            The approximate intersection point in math coordinates, or ``None``
            if no sign change was found (functions may not cross in the range).
        """
        a, b = float(x_range[0]), float(x_range[1])
        fa = func1(a) - func2(a)
        fb = func1(b) - func2(b)
        if fa * fb > 0:
            return None  # No guaranteed crossing
        for _ in range(100):  # max iterations
            mid = (a + b) / 2
            fm = func1(mid) - func2(mid)
            if abs(b - a) < tol or abs(fm) < 1e-12:
                break
            if fa * fm <= 0:
                b = mid
                fb = fm
            else:
                a = mid
                fa = fm
        x = (a + b) / 2
        y = (func1(x) + func2(x)) / 2
        return (x, y)

    def mark_intersection(self, func1, func2, x_range=None, creation=0,
                          label=None, **kwargs):
        """Find the intersection of two functions and place a Dot there.

        Uses :meth:`get_intersection_point` to find the crossing, creates a
        :class:`Dot` at the corresponding SVG position, and optionally adds a
        :class:`Text` label above the dot.

        Parameters
        ----------
        func1, func2:
            Callables ``f(x) -> y`` whose intersection is sought.
        x_range:
            ``(a, b)`` search interval.  If ``None`` the axes' x-range is used.
        creation:
            Creation time for the dot (and label).
        label:
            Optional label string displayed above the dot.
        **kwargs:
            Forwarded to the :class:`Dot` constructor (e.g. ``fill``, ``r``).

        Returns
        -------
        Dot or VCollection
            The dot if no label was requested, otherwise a
            :class:`VCollection` containing the dot and label text.
            Returns ``None`` if no intersection was found.
        """
        if x_range is None:
            x_range = (self.x_min.at_time(creation), self.x_max.at_time(creation))
        result = self.get_intersection_point(func1, func2, x_range)
        if result is None:
            return None
        ix, iy = result
        sx, sy = self.coords_to_point(ix, iy, time=creation)

        dot_kw = {'fill': '#FF6B6B', 'r': 6} | kwargs
        dot = Dot(cx=sx, cy=sy, creation=creation, **dot_kw)
        self._add_plot_obj(dot)

        if label is not None:
            label_offset_y = -dot_kw.get('r', 6) - 12
            lbl = Text(text=str(label), x=sx, y=sy + label_offset_y,
                       font_size=20, text_anchor='middle',
                       fill=dot_kw.get('fill', '#FF6B6B'),
                       stroke_width=0, creation=creation)
            self._add_plot_obj(lbl)
            return VCollection(dot, lbl, creation=creation)
        return dot

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
        fn = self._resolve_func(func, 'func')
        def _build(time):
            x_lo, x_hi = x_range
            by = self._baseline_y(time)
            rects = []
            xv = x_lo
            while xv < x_hi - 1e-9:
                x_next = min(xv + dx, x_hi)
                sx1 = self._math_to_svg_x(xv, time)
                sx2 = self._math_to_svg_x(x_next, time)
                try:
                    sy = self._math_to_svg_y(fn(xv), time)
                except (ValueError, ZeroDivisionError):
                    xv = x_next
                    continue
                rects.append(Rectangle(width=sx2 - sx1, height=abs(by - sy),
                                       x=sx1, y=min(sy, by),
                                       creation=time, z=z, **style_kw))
                xv = x_next
            return VCollection(*rects, creation=time, z=z)
        dyn = _get_dynamic_object()(_build, creation=creation, z=z)
        self._add_plot_obj(dyn)
        return dyn

    def plot_derivative(self, func, h=0.001, num_points=200,
                        creation=0, z=0, **styling_kwargs):
        """Plot the numerical derivative of a function.

        Creates a new curve representing ``f'(x)`` computed via the
        central difference formula::

            f'(x) = (f(x + h) - f(x - h)) / (2 * h)

        The returned Path is a live curve that resamples each frame
        (like :meth:`plot`), so it responds to animated axis ranges.

        Parameters
        ----------
        func:
            A callable ``f(x)`` or a curve Path with a ``._func`` attribute
            (as returned by :meth:`plot`).
        h:
            Step size for the central difference (default 0.001).
        num_points:
            Number of sample points for the curve (default 200).
        creation:
            Creation time for the returned Path.
        z:
            Z-index for layering.
        **styling_kwargs:
            Styling overrides.  Defaults to a green dashed line.

        Returns
        -------
        Path
            A Path object (with ``._func`` set to the derivative function)
            added to the axes.
        """
        fn = self._resolve_func(func, 'func')

        def _deriv(x, _f=fn, _hh=h):
            try:
                return (_f(x + _hh) - _f(x - _hh)) / (2 * _hh)
            except (ValueError, ZeroDivisionError):
                return float('nan')

        style_kw = {'stroke': '#A6E22E', 'stroke_width': 3,
                    'fill_opacity': 0, 'stroke_dasharray': '8,4'} | styling_kwargs
        if hasattr(self, '_deferred_axes'):
            self._build_deferred_axes(fn, num_points)
        curve = self._make_curve(_deriv, creation, z, num_points=num_points,
                                 **style_kw)
        self._add_plot_obj(curve)
        return curve

    def get_trapezoidal_rule(self, func, x_range, dx=0.5, creation=0, z=0,
                             **styling_kwargs):
        """Visualize the trapezoidal rule approximation of the area under *func*.

        Unlike :meth:`get_riemann_rectangles` which draws axis-aligned
        rectangles evaluated at the left endpoint, this method draws
        trapezoids whose top edges connect the function values at the left
        and right endpoints of each sub-interval, giving a more accurate
        visual approximation of the integral.

        The result is a :class:`DynamicObject` that rebuilds each frame,
        so it responds correctly to animated axis ranges.

        Parameters
        ----------
        func:
            A callable ``f(x)`` to approximate.
        x_range:
            ``(x_min, x_max)`` bounds for the approximation domain in
            math coordinates.
        dx:
            Width of each sub-interval in math coordinates (default 0.5).
        creation:
            Creation time.
        z:
            Z-index for layering.
        **styling_kwargs:
            Styling overrides (default: semi-transparent blue fill with
            white stroke).

        Returns
        -------
        DynamicObject
            A dynamic collection of Polygon trapezoids, added to the axes.
        """
        style_kw = {'fill': '#58C4DD', 'fill_opacity': 0.4,
                    'stroke': '#fff', 'stroke_width': 1} | styling_kwargs
        fn = self._resolve_func(func, 'func')

        def _build(time):
            x_lo, x_hi = x_range
            by = self._baseline_y(time)
            traps = []
            xv = x_lo
            while xv < x_hi - 1e-9:
                x_next = min(xv + dx, x_hi)
                # Four corners of the trapezoid: bottom-left, top-left, top-right, bottom-right
                sx1 = self._math_to_svg_x(xv, time)
                sx2 = self._math_to_svg_x(x_next, time)
                try:
                    sy1 = self._math_to_svg_y(fn(xv), time)
                    sy2 = self._math_to_svg_y(fn(x_next), time)
                except (ValueError, ZeroDivisionError):
                    xv = x_next
                    continue
                # Clamp to plot area
                py_top = self.plot_y
                py_bot = self.plot_y + self.plot_height
                sy1 = max(py_top, min(py_bot, sy1))
                sy2 = max(py_top, min(py_bot, sy2))
                trap = Polygon(
                    (sx1, by), (sx1, sy1), (sx2, sy2), (sx2, by),
                    creation=time, z=z, **style_kw)
                traps.append(trap)
                xv = x_next
            return VCollection(*traps, creation=time, z=z)

        dyn = _get_dynamic_object()(_build, creation=creation, z=z)
        self._add_plot_obj(dyn)
        return dyn

    def get_x_axis_label(self):
        """Return the x-axis label object, or None if no label was set."""
        for lbl in self._axis_labels:
            if hasattr(lbl, 'x') and lbl.x.at_time(0) > self.plot_x + self.plot_width:
                return lbl
        return self._axis_labels[0] if len(self._axis_labels) >= 1 else None

    def get_y_axis_label(self):
        """Return the y-axis label object, or None if no label was set."""
        for lbl in self._axis_labels:
            if hasattr(lbl, 'y') and lbl.y.at_time(0) < self.plot_y:
                return lbl
        return self._axis_labels[1] if len(self._axis_labels) >= 2 else None

    def get_x_axis_line(self, creation=0, **kwargs):
        """Return a Line spanning the x-axis (y=0) of the plot area."""
        style_kw = {'stroke': '#888888', 'stroke_width': 2, 'fill_opacity': 0} | kwargs
        x1 = self.plot_x
        x2 = self.plot_x + self.plot_width
        y = self._baseline_y(creation)
        return Line(x1=x1, y1=y, x2=x2, y2=y, creation=creation, **style_kw)

    def get_y_axis_line(self, creation=0, **kwargs):
        """Return a Line spanning the y-axis (x=0) of the plot area."""
        style_kw = {'stroke': '#888888', 'stroke_width': 2, 'fill_opacity': 0} | kwargs
        y1 = self.plot_y
        y2 = self.plot_y + self.plot_height
        xmin = self.x_min.at_time(creation)
        xmax = self.x_max.at_time(creation)
        if xmin <= 0 <= xmax:
            x = self._math_to_svg_x(0, creation)
        else:
            x = self.plot_x
        return Line(x1=x, y1=y1, x2=x, y2=y2, creation=creation, **style_kw)

    def plot_normal(self, mean=0, std=1, color='#4FC3F7', num_points=100,
                    creation=0, fill=True, fill_opacity=0.3, **kwargs):
        """Plot a normal (Gaussian) distribution curve.

        Returns the curve Path.
        """
        if std <= 0:
            raise ValueError("std must be positive")
        inv_coeff = 1 / (std * math.sqrt(math.tau))
        def func(x):
            return inv_coeff * math.exp(-0.5 * ((x - mean) / std) ** 2)
        kwargs.setdefault('stroke', color)
        curve = self.plot(func, num_points=num_points, creation=creation, **kwargs)
        if fill:
            self.get_area(func, creation=creation, fill=color, fill_opacity=fill_opacity)
        return curve

    def plot_exponential(self, rate=1, color='#FF8A65', num_points=100,
                         creation=0, **kwargs):
        """Plot an exponential distribution: f(x) = rate * exp(-rate * x) for x >= 0.

        Returns the curve Path.
        """
        def func(x):
            return rate * math.exp(-rate * x) if x >= 0 else 0
        kwargs.setdefault('stroke', color)
        return self.plot(func, num_points=num_points, creation=creation, **kwargs)

    def plot_uniform(self, a=0, b=1, color='#81C784', creation=0, **kwargs):
        """Plot a uniform distribution: f(x) = 1/(b-a) for a <= x <= b, 0 otherwise.

        Returns the curve Path.
        """
        height = 1 / (b - a) if b != a else 0
        def func(x):
            return height if a <= x <= b else 0
        kwargs.setdefault('stroke', color)
        return self.plot(func, creation=creation, **kwargs)

    def add_residual_lines(self, x_data, y_data, creation=0, z=1, **styling_kwargs):
        """Draw vertical residual lines from each data point to the regression line.

        Computes least-squares regression (y = mx + b) from the data, then
        draws a vertical Line from each observed (x, y) to the predicted
        (x, mx + b).  Useful for visualising regression fit quality.

        Parameters
        ----------
        x_data, y_data:
            Sequences of numeric x and y values.
        creation:
            Appearance time.
        z:
            Draw order.
        **styling_kwargs:
            Styling overrides for the residual lines.

        Returns
        -------
        VCollection
            A VCollection of Line objects (one per data point).  Returns an
            empty VCollection if there are fewer than 2 data points or the
            regression is degenerate.
        """
        style_kw = {'stroke': '#FF6B6B', 'stroke_width': 2, 'stroke_dasharray': '4 3'} | styling_kwargs
        n = len(x_data)
        if n < 2:
            return VCollection(creation=creation, z=z)
        sx = sum(x_data)
        sy = sum(y_data)
        sxy = sum(x * y for x, y in zip(x_data, y_data))
        sxx = sum(x * x for x in x_data)
        denom = n * sxx - sx * sx
        if abs(denom) < 1e-12:
            return VCollection(creation=creation, z=z)
        slope = (n * sxy - sx * sy) / denom
        intercept = (sy - slope * sx) / n
        lines = []
        for xi, yi in zip(x_data, y_data):
            predicted = slope * xi + intercept
            line = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z, **style_kw)
            line.p1.set_onward(creation,
                lambda t, _x=xi, _y=yi: self.coords_to_point(_x, _y, t))
            line.p2.set_onward(creation,
                lambda t, _x=xi, _p=predicted: self.coords_to_point(_x, _p, t))
            lines.append(line)
            self._add_plot_obj(line)
        group = VCollection(*lines, creation=creation, z=z)
        return group

    def add_spread_band(self, func, spread_func, x_range=None, num_points=100,
                        color='#58C4DD', opacity=0.2, creation=0):
        """Draw a shaded band around a curve defined by a centre function and spread.

        The band extends from ``func(x) - spread_func(x)`` to
        ``func(x) + spread_func(x)`` for each x.

        Parameters
        ----------
        func:
            Centre function y = func(x), or a curve with ``._func``.
        spread_func:
            Half-width function: ``spread_func(x)`` returns the distance
            above and below the centre at x.
        x_range:
            Optional ``(x0, x1)`` tuple.  Defaults to the visible axis range.
        num_points:
            Number of sample points along x.
        color:
            Fill color for the band.
        opacity:
            Fill opacity.
        creation:
            Appearance time.

        Returns
        -------
        Path
            A filled Path representing the band (already added to the axes).
        """
        fn = self._resolve_func(func, 'func')
        spread_fn = self._resolve_func(spread_func, 'spread_func')
        band = Path('', x=0, y=0, creation=creation, z=-1,
                    fill=color, fill_opacity=opacity, stroke_width=0)
        _xr = x_range
        _n = num_points
        def _band_d(time, _fn=fn, _sf=spread_fn, _xr=_xr, _n=_n):
            xmin, xmax = self.x_min.at_time(time), self.x_max.at_time(time)
            x0 = _xr[0] if _xr else xmin
            x1 = _xr[1] if _xr else xmax
            step = (x1 - x0) / max(_n, 1)
            pts_hi, pts_lo = [], []
            for i in range(_n + 1):
                xv = x0 + i * step
                yc = _fn(xv)
                sp = _sf(xv)
                sx_hi, sy_hi = self.coords_to_point(xv, yc + sp, time)
                sx_lo, sy_lo = self.coords_to_point(xv, yc - sp, time)
                pts_hi.append((sx_hi, sy_hi))
                pts_lo.append((sx_lo, sy_lo))
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

    def add_mean_line(self, func_or_data, x_range=None, creation=0, **kwargs):
        """Add a horizontal dashed line at the mean value of a function or data.

        If *func_or_data* is callable, it is sampled uniformly over *x_range*
        (defaulting to the current axis x-range) and the mean of the sampled
        values is used.  If it is a list (or other sequence), the arithmetic
        mean is computed directly.

        Parameters
        ----------
        func_or_data:
            A callable ``f(x) -> y`` or a list/sequence of numeric values.
        x_range:
            ``(x_start, x_end)`` over which to sample a callable.  Ignored
            when *func_or_data* is a list.  Defaults to the axis x-range at
            time 0.
        creation:
            Creation time for the line.
        **kwargs:
            Override default styling (stroke, stroke_width, stroke_dasharray).

        Returns
        -------
        Line
            The horizontal mean line (already added to the axes).
        """
        if callable(func_or_data):
            if x_range is None:
                x_range = (self.x_min.at_time(0), self.x_max.at_time(0))
            n = 200
            x0, x1 = x_range
            step = (x1 - x0) / n
            values = [func_or_data(x0 + i * step) for i in range(n + 1)]
            mean_val = sum(values) / len(values)
        else:
            data = list(func_or_data)
            if not data:
                raise ValueError('add_mean_line requires non-empty data')
            mean_val = sum(data) / len(data)

        style_kw = {'stroke': '#FFFF00', 'stroke_width': 1.5,
                     'stroke_dasharray': '6 3'} | kwargs
        line = self._make_span_line(mean_val, 'horizontal', creation, 0, style_kw)
        self._add_plot_obj(line)
        return line

    def add_function_label(self, func_or_curve, label_text, x_pos=None,
                           direction='above', font_size=24, creation=0, z=1, **kwargs):
        """Add a text label near a function curve at a specific x-position.

        If *func_or_curve* is a callable, it is used directly as ``y = f(x)``.
        If it is a curve Path object with a ``_func`` attribute (as returned
        by :meth:`add_function`), its stored function is used.

        Parameters
        ----------
        func_or_curve:
            A callable ``f(x) -> y`` or a Path object with ``._func``.
        label_text:
            The string to display.
        x_pos:
            Math x-coordinate at which to place the label.  If ``None``,
            the label is placed at the rightmost visible x value (``x_max``).
        direction:
            ``'above'`` (default) or ``'below'`` — controls whether the
            label appears above or below the curve.
        font_size:
            Font size of the label text.
        creation:
            Creation time for the returned Text object.
        z:
            Z-layer ordering.
        **kwargs:
            Extra keyword arguments forwarded to the :class:`Text`
            constructor (e.g. ``fill``, ``stroke``).

        Returns
        -------
        Text
            The label Text object (already added to the axes).
        """
        func = getattr(func_or_curve, '_func', None) or func_or_curve
        buff = 12
        sign = -1 if direction == 'above' else 1

        style_kw = {'fill': '#fff', 'stroke_width': 0, 'text_anchor': 'middle'} | kwargs
        lbl = Text(text=str(label_text), x=0, y=0, font_size=font_size,
                   creation=creation, z=z, **style_kw)

        if x_pos is not None:
            sx = self._math_to_svg_x(x_pos, creation)
            try:
                sy = self._math_to_svg_y(func(x_pos), creation)
            except Exception:
                sy = self.get_plot_center()[1]
            lbl.x.set_onward(creation, sx)
            lbl.y.set_onward(creation, sy + sign * (font_size / 2 + buff))
        else:
            # Dynamic: track x_max
            def _lbl_x(t):
                xv = self.x_max.at_time(t)
                return self._math_to_svg_x(xv, t)
            def _lbl_y(t, _f=func, _s=sign, _b=buff, _fz=font_size):
                xv = self.x_max.at_time(t)
                try:
                    yv = _f(xv)
                except Exception:
                    yv = 0
                return self._math_to_svg_y(yv, t) + _s * (_fz / 2 + _b)
            lbl.x.set_onward(creation, _lbl_x)
            lbl.y.set_onward(creation, _lbl_y)

        self._add_plot_obj(lbl)
        return lbl

    def annotate_area(self, func_or_curve, x_range, label=None, color='#58C4DD',
                       opacity=0.3, start=0, **kwargs):
        """Create a shaded area under a curve with an optional centered label.

        Combines :meth:`get_area` with label placement.  The area is created
        using the existing ``get_area`` method and an optional ``Text`` label
        is placed at the center of the x_range on the curve midpoint.

        Parameters
        ----------
        func_or_curve:
            A callable ``f(x)`` or a Path with ``._func`` (as returned by
            :meth:`plot`).
        x_range:
            ``(x_start, x_end)`` in math coordinates.
        label:
            Optional text string for a label centered on the shaded area.
        color:
            Fill color for the area.
        opacity:
            Fill opacity for the area.
        start:
            Creation time for the area and label.
        **kwargs:
            Extra keyword arguments forwarded to ``get_area``.

        Returns
        -------
        VCollection
            A VCollection containing the area Path and (if provided) the label.
        """
        area = self.get_area(func_or_curve, x_range=x_range, creation=start,
                             fill=color, fill_opacity=opacity, **kwargs)
        objects = [area]

        if label is not None:
            func = self._resolve_func(func_or_curve, 'func_or_curve')
            x_mid = (x_range[0] + x_range[1]) / 2
            y_mid = func(x_mid)
            sx = self._math_to_svg_x(x_mid, start)
            sy = self._math_to_svg_y(y_mid / 2, start)
            lbl = Text(text=str(label), x=sx, y=sy,
                       font_size=24, text_anchor='middle',
                       creation=start, fill='#fff', stroke_width=0)
            self._add_plot_obj(lbl)
            objects.append(lbl)

        return VCollection(*objects, creation=start)

    def __repr__(self):
        xn, xx = self.x_min.at_time(0), self.x_max.at_time(0)
        if self.y_min is not None:
            yn, yx = self.y_min.at_time(0), self.y_max.at_time(0)
            return f'Axes(x=[{xn:.1f}, {xx:.1f}], y=[{yn:.1f}, {yx:.1f}])'
        return f'Axes(x=[{xn:.1f}, {xx:.1f}])'


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

    def __repr__(self):
        xn, xx = self.x_min.at_time(0), self.x_max.at_time(0)
        return f'Graph(x=[{xn:.1f}, {xx:.1f}])'


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

    def coords_to_point(self, x, y):
        """Convert logical coordinates to SVG pixel coordinates."""
        return (self._cx + x * self._unit, self._cy - y * self._unit)

    def apply_function(self, func, start=0, end=1, easing=easings.smooth, resolution=20):
        """Animate a non-linear transformation of the grid.

        *func* takes (x, y) in logical coords and returns (x', y').
        Each grid intersection is smoothly moved from its original to its transformed position.
        *resolution* controls the number of sample points per grid line segment.
        """
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

    def apply_complex_function(self, func, start=0, end=1, easing=easings.smooth,
                               resolution=20, step=1.0):
        """Animate a complex function transformation of the plane.

        Subdivides the existing grid into many small line segments and animates
        each segment from its original position to the position given by
        applying *func*.

        func: callable taking a complex number and returning a complex number.
        resolution: number of sub-segments per grid line between successive
            integer values.
        step: spacing between grid lines in math coordinates (default 1).
        """
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


from vectormation._diagrams import ChessBoard as ChessBoard  # noqa: E402,F811
from vectormation._diagrams import PeriodicTable as PeriodicTable  # noqa: E402,F811


from vectormation._diagrams import BohrAtom as BohrAtom  # noqa: E402,F811
from vectormation._diagrams import Automaton as Automaton  # noqa: E402,F811
from vectormation._diagrams import NetworkGraph as NetworkGraph  # noqa: E402,F811


