"""Advanced Axes methods — annotations, statistics, visualization extras."""
import math

import vectormation.easings as easings
from vectormation._constants import (
    DEFAULT_CHART_COLORS, TEXT_Y_OFFSET, _normalize,
)
from vectormation._base import VCollection
from vectormation._shapes import (
    Polygon, Dot, Rectangle, RoundedRectangle, Line,
    Text, Path,
)
from vectormation._axes_helpers import (
    _AREA_STYLE, _HIGHLIGHT_STYLE, _MARCH_SEGS,
    _get_arrow, _get_dynamic_object,
)

_LABEL_STYLE = {'fill': '#ddd', 'stroke_width': 0}

def _dyn_line(line, creation, p1_func, p2_func):
    """Set dynamic endpoint functions on a Line (saves repeated set_onward boilerplate)."""
    line.p1.set_onward(creation, p1_func)
    line.p2.set_onward(creation, p2_func)
    return line

def _dir_endpoints(cx, cy, dx, dy, length):
    """Return (p1, p2) endpoints centered at (cx, cy) along direction (dx, dy), scaled to *length*."""
    ux, uy = _normalize(dx, dy)
    half = length / 2
    nx, ny = ux * half, uy * half
    return (cx - nx, cy - ny), (cx + nx, cy + ny)


def _band_path(pts_hi, pts_lo):
    """Build a closed SVG path string around *pts_hi* (forward) and *pts_lo* (reversed)."""
    if not pts_hi:
        return ''
    parts = [f'M{pts_hi[0][0]:.1f},{pts_hi[0][1]:.1f}']
    parts.extend(f'L{sx:.1f},{sy:.1f}' for sx, sy in pts_hi[1:])
    parts.extend(f'L{sx:.1f},{sy:.1f}' for sx, sy in reversed(pts_lo))
    parts.append('Z')
    return ''.join(parts)


def _regression(x_data, y_data):
    """Return (slope, intercept) for a least-squares fit, or None if degenerate."""
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
    return slope, intercept


class _AxesExtMixin:
    """Advanced annotation and analysis methods for Axes, mixed in at definition time."""

    def _cf(self, mx, my):
        """Lambda returning SVG Coor for math point (mx, my) at time t."""
        return lambda t, _x=mx, _y=my: self.coords_to_point(_x, _y, t)

    def _xf(self, mx, my=None, offset=0):
        """Lambda returning SVG x for math point at time t (with optional offset)."""
        if my is not None:
            return lambda t, _x=mx, _y=my, _o=offset: self.coords_to_point(_x, _y, t)[0] + _o
        return lambda t, _x=mx, _o=offset: self._math_to_svg_x(_x, t) + _o

    def _yf(self, my, mx=None, offset=0):
        """Lambda returning SVG y for math point at time t (with optional offset)."""
        if mx is not None:
            return lambda t, _x=mx, _y=my, _o=offset: self.coords_to_point(_x, _y, t)[1] + _o
        return lambda t, _y=my, _o=offset: self._math_to_svg_y(_y, t) + _o

    def get_dashed_line(self, x1, y1, x2, y2, creation=0, z=0, **styling_kwargs):
        """Draw a dashed line between two math coordinate points.
        Returns a Line object."""
        style_kw = {'stroke': '#aaa', 'stroke_width': 2, 'stroke_dasharray': '6 4'} | styling_kwargs
        return self.get_line_from_to(x1, y1, x2, y2, creation=creation, z=z, **style_kw)

    def add_title(self, text, font_size=32, buff=20, creation=0, z=5, **styling_kwargs):
        """Add a title above the axes. Returns the Text object."""
        style_kw = _LABEL_STYLE | styling_kwargs
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
        line = Line(x1=0, y1=0, x2=0, y2=0,
                    creation=creation, z=z, stroke=arrow_color, stroke_width=1)
        _dyn_line(line, creation,
                  lambda t, _x=x, _y=y, _dx=dx, _dy=dy:
                      ((_p := self.coords_to_point(_x, _y, t))[0] + _dx, _p[1] + _dy),
                  lambda t, _x=x, _y=y: self.coords_to_point(_x, _y, t))

        label = Text(text=str(text), x=0, y=0, font_size=font_size,
                     fill=color, stroke_width=0, text_anchor='middle',
                     creation=creation, z=z + 0.1)
        label.x.set_onward(creation, self._xf(x, y, dx))
        label.y.set_onward(creation, self._yf(y, x, dy - font_size))

        group = VCollection(line, label, creation=creation, z=z)
        self._add_plot_obj(group)
        return group

    def add_horizontal_label(self, y, text, side='right', buff=10, font_size=18,
                              creation=0, z=5, **styling_kwargs):
        """Add a text label at y-coordinate on the specified side of the plot."""
        style_kw = _LABEL_STYLE | styling_kwargs
        lx = (self.plot_x - buff) if side == 'left' else (self.plot_x + self.plot_width + buff)
        anchor = 'end' if side == 'left' else 'start'
        lbl = Text(text=str(text), x=lx, y=0, font_size=font_size,
                    text_anchor=anchor, creation=creation, z=z, **style_kw)
        lbl.y.set_onward(creation, self._yf(y))
        self._add_plot_obj(lbl)
        return lbl

    def add_vertical_label(self, x, text, side='bottom', buff=10, font_size=18,
                            creation=0, z=5, **styling_kwargs):
        """Add a text label at x-coordinate above or below the plot."""
        style_kw = _LABEL_STYLE | styling_kwargs
        ly = (self.plot_y - buff) if side == 'top' else (self.plot_y + self.plot_height + buff + font_size)
        lbl = Text(text=str(text), x=0, y=ly, font_size=font_size,
                    text_anchor='middle', creation=creation, z=z, **style_kw)
        lbl.x.set_onward(creation, self._xf(x))
        self._add_plot_obj(lbl)
        return lbl

    def get_horizontal_line(self, x, y_val, creation=0, z=0, **styling_kwargs):
        """Draw a horizontal line at math y-coordinate from the y-axis to x."""
        style_kw = {'stroke': '#FFFF00', 'stroke_width': 2, 'stroke_dasharray': '5 5'} | styling_kwargs
        line = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z, **style_kw)
        _dyn_line(line, creation,
                  lambda t: (self.plot_x, self._math_to_svg_y(y_val, t)),
                  lambda t: (self._math_to_svg_x(x, t), self._math_to_svg_y(y_val, t)))
        self._add_plot_obj(line)
        return line

    def _make_span_line(self, value, direction, creation, z, style_kw):
        """Create a Line spanning the full plot along one axis at a given math value.
        direction: 'vertical' (x=value) or 'horizontal' (y=value)."""
        line = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z, **style_kw)
        _v = value
        if direction == 'vertical':
            _dyn_line(line, creation,
                      lambda t, _v=_v: (self._math_to_svg_x(_v, t), self.plot_y),
                      lambda t, _v=_v: (self._math_to_svg_x(_v, t), self.plot_y + self.plot_height))
        else:
            _dyn_line(line, creation,
                      lambda t, _v=_v: (self.plot_x, self._math_to_svg_y(_v, t)),
                      lambda t, _v=_v: (self.plot_x + self.plot_width, self._math_to_svg_y(_v, t)))
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
        dot.c.set_onward(creation, self._cf(mx, my))
        lbl = Text(text=label_text, x=sx, y=sy + offset_y,
                   font_size=font_size, fill=fill_color, stroke_width=0,
                   text_anchor='middle', creation=creation, z=z + 2)
        lbl.x.set_onward(creation, self._xf(mx, my))
        lbl.y.set_onward(creation, self._yf(my, mx, offset_y))
        self._add_plot_obj(dot)
        self._add_plot_obj(lbl)
        return dot, lbl

    def add_inflection_points(self, func, x_range=None, samples=200, h=1e-5,
                              creation=0, z=3, dot_radius=5, font_size=18,
                              color='#FFA726', **styling_kwargs):
        """Find and label inflection points of *func* within *x_range*."""
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
        """Find and mark critical points (local minima and maxima) of *func*."""
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
        result = _regression(x_data, y_data)
        if result is None:
            return None
        slope, intercept = result
        xlo = min(x_data) - extend
        xhi = max(x_data) + extend
        _m, _b, _xlo, _xhi = slope, intercept, xlo, xhi
        line = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z, **style_kw)
        _dyn_line(line, creation,
                  lambda t, _m=_m, _b=_b, _xlo=_xlo: self.coords_to_point(_xlo, _m * _xlo + _b, t),
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
            return _band_path(pts_hi, pts_lo)
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
                cell_kw = {'fill': color, 'fill_opacity': 0.85, 'stroke': color,
                           'stroke_width': 0.5} | styling_kwargs
                rect = Rectangle(width=0, height=0, x=0, y=0,
                                  creation=creation, z=z, **cell_kw)
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
        _dyn_line(v_line, creation,
                  lambda t: (_cached(t)[1][0], self.plot_y + self.plot_height),
                  lambda t: _cached(t)[1])
        # Horizontal line from y-axis to curve point
        h_line = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z, **style_kw)
        _dyn_line(h_line, creation,
                  lambda t: (self.plot_x, _cached(t)[1][1]),
                  lambda t: _cached(t)[1])
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
                parts.extend(f'L{sx:.1f},{sy:.1f}' for sx, sy in right_pts[1:])
                parts.extend(f'L{sx:.1f},{sy:.1f}' for sx, sy in reversed(left_pts))
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
            _dyn_line(med_line, creation,
                      lambda t, _xp=_xp2, _hw=_hw2, _m=_med: (
                          self._math_to_svg_x(_xp - _hw, t), self._math_to_svg_y(_m, t)),
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

    def plot_stacked_area(self, data, labels=None, colors=None, x_values=None,  # noqa: ARG002 (labels reserved for legend)
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
                return _band_path(pts_hi, pts_lo)
            area.d.set_onward(creation, _area_d)
            self._add_plot_obj(area)
            areas.append(area)
        return VCollection(*areas, creation=creation, z=z)

    def plot_candlestick(self, data, bar_width=0.6, creation: float = 0, z: float = 1,
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
            body_kw = {'fill': color, 'fill_opacity': 0.8, 'stroke': color,
                       'stroke_width': 1} | styling_kwargs
            rect = Rectangle(width=0, height=0, x=0, y=0,
                              creation=creation, z=z + 0.1, **body_kw)
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
                       creation: float = 0, z: float = 1, **styling_kwargs):
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
            _dyn_line(line, creation,
                      lambda t, _y=_yp, _x=_sv: self.coords_to_point(_x, _y, t),
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
                             samples=200, creation: float = 0, z: float = -1, **styling_kwargs):
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
            parts.extend(f'L{sx:.1f},{sy:.1f}' for sx, sy in pts[1:])
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
        style_kw = _LABEL_STYLE | styling_kwargs
        objs = []
        for xv, yv in zip(x_data, y_data):
            lbl = Text(text=fmt.format(yv), x=0, y=0, font_size=font_size,
                        text_anchor='middle', creation=creation, z=z, **style_kw)
            lbl.x.set_onward(creation, self._xf(xv, yv))
            lbl.y.set_onward(creation, self._yf(yv, xv, offset_y))
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
            _dyn_line(line, creation,
                      lambda t, _y=yp, _x=baseline: self.coords_to_point(_x, _y, t),
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
        style_kw = _LABEL_STYLE | styling_kwargs
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

    def _add_span(self, v0, v1, vertical, creation, z, styling_kwargs):
        """Shade a band between two values (vertical=True for x-band, False for y-band)."""
        style_kw = _HIGHLIGHT_STYLE | styling_kwargs
        rect = Rectangle(width=0, height=0, x=0, y=0, creation=creation, z=z, **style_kw)
        if vertical:
            rect.x.set_onward(creation, lambda t, _a=v0: self._math_to_svg_x(_a, t))
            rect.y.set_onward(creation, lambda t: self.plot_y)
            rect.width.set_onward(creation, lambda t, _a=v0, _b=v1: self._math_to_svg_x(_b, t) - self._math_to_svg_x(_a, t))
            rect.height.set_onward(creation, lambda t: self.plot_height)
        else:
            rect.x.set_onward(creation, lambda t: self.plot_x)
            rect.y.set_onward(creation, lambda t, _a=v1: self._math_to_svg_y(_a, t))
            rect.width.set_onward(creation, lambda t: self.plot_width)
            rect.height.set_onward(creation, lambda t, _a=v0, _b=v1: self._math_to_svg_y(_a, t) - self._math_to_svg_y(_b, t))
        self._add_plot_obj(rect)
        return rect

    def add_vertical_span(self, x0, x1, creation=0, z=-1, **styling_kwargs):
        """Shade a vertical band between x0 and x1 (math coords)."""
        return self._add_span(x0, x1, True, creation, z, styling_kwargs)

    def add_horizontal_span(self, y0, y1, creation=0, z=-1, **styling_kwargs):
        """Shade a horizontal band between y0 and y1 (math coords)."""
        return self._add_span(y0, y1, False, creation, z, styling_kwargs)

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
        _cache = [None, None]
        def _pt(t, _x=_xc, _y=_yc):
            if _cache[0] != t:
                _cache[0] = t
                _cache[1] = self.coords_to_point(_x, _y, t)
            return _cache[1]
        lbl.x.set_onward(creation, lambda t: _pt(t)[0] + ox)
        lbl.y.set_onward(creation, lambda t: _pt(t)[1] + oy)
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
        """Add a text annotation at graph coordinates (x, y), wrapper around add_point_label."""
        kwargs.setdefault('creation', start)
        return self.add_point_label(x, y, text=text, **kwargs)

    def add_annotation_box(self, x_coord, y_coord, text, box_width=120, box_height=40,
                            offset=(60, -60), font_size=14, creation=0, z=5, **styling_kwargs):
        """Add a text box with an arrow pointing to (x_coord, y_coord).
        offset: (dx, dy) from the point to the box center.
        Returns a VCollection with arrow, box, and label."""

        style_kw = _LABEL_STYLE | styling_kwargs
        ox, oy = offset
        # Point SVG coordinates
        _xc, _yc = x_coord, y_coord
        def _pt(t):
            return self.coords_to_point(_xc, _yc, t)
        # Arrow from point to box edge
        arr = _get_arrow()(x1=0, y1=0, x2=0, y2=0, stroke='#aaa', stroke_width=1.5,
                    creation=creation, z=z)
        arr.shaft.p1.set_onward(creation, lambda t: _pt(t))
        arr.shaft.p2.set_onward(creation, lambda t, _ox=ox, _oy=oy: ((_p := _pt(t))[0] + _ox, _p[1] + _oy))
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

    def plot_quiver(self, func, x_step: float = 1, y_step: float = 1, scale=0.3,
                     tip_length=8, tip_width=6,
                     creation: float = 0, z: float = 0, **styling_kwargs):
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
            pts = []
            for i, (x, y) in enumerate(_data):
                sx, sy = self.coords_to_point(x, y, time)
                pts.append(f'{"M" if i == 0 else "L"}{sx:.1f},{sy:.1f}')
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
                _dyn_line(line, creation,
                          lambda t, _x=x, _y=y, _dx=dx, _dy=dy:
                              self.coords_to_point(_x - _dx, _y - _dy, t),
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
            ux, uy = _normalize(ddx, ddy)
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
            def _p1(t, _yv=yv, _xs=x_start):
                sy = self._math_to_svg_y(_yv, t)
                sx = self._math_to_svg_x(_xs, t) if _xs is not None else self.plot_x
                return (sx, sy)
            def _p2(t, _yv=yv, _xe=x_end):
                sy = self._math_to_svg_y(_yv, t)
                sx = self._math_to_svg_x(_xe, t) if _xe is not None else self.plot_x + self.plot_width
                return (sx, sy)
            _dyn_line(line, creation, _p1, _p2)
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
        _dyn_line(v_line, creation, _pt,
                  lambda t: (_pt(t)[0], self.plot_y + self.plot_height))
        # Dashed line to y-axis
        h_line = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z,
                      stroke=style_kw.get('stroke', '#FFFF00'),
                      stroke_width=1, stroke_dasharray='4 3')
        _dyn_line(h_line, creation, _pt,
                  lambda t: (self.plot_x, _pt(t)[1]))
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
        xspan = self.x_max.at_time(creation) - self.x_min.at_time(creation)
        yspan = self.y_max.at_time(creation) - self.y_min.at_time(creation)
        if xspan == 0 or yspan == 0:
            return Line(x1=cx_svg, y1=cy_svg, x2=cx_svg + length, y2=cy_svg,
                        creation=creation, z=z, **style_kw)
        dx_px = self.plot_width / xspan
        (x1, y1), (x2, y2) = _dir_endpoints(cx_svg, cy_svg, dx_px, slope * (-self.plot_height / yspan), length)
        line = Line(x1=x1, y1=y1, x2=x2, y2=y2,
                    creation=creation, z=z, **style_kw)
        self._add_plot_obj(line)
        return line

    def add_tangent_at(self, func, x_val, length=200, creation=0, **kwargs):
        """Alias for :meth:`get_tangent_line` that adds the line to the axes."""
        return self.get_tangent_line(func, x_val, length=length, creation=creation, **kwargs)

    def animated_tangent_line(self, func, x_start, x_end, start=0, end=1,
                               length=200, creation=0, z=0, easing=None, **styling_kwargs):
        """Tangent line that slides along func from x_start to x_end over [start, end].

        Returns a Line that is dynamically positioned as a tangent.
        """
        easing = easing or easings.smooth
        style_kw = {'stroke': '#FFFF00', 'stroke_width': 2} | styling_kwargs
        line = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z, **style_kw)
        _xs, _xe, _s, _d = x_start, x_end, start, max(end - start, 1e-9)
        _len, h = length, 1e-6
        def _tangent_ep(sign):
            def _pt(t, _xs=_xs, _xe=_xe, _s=_s, _d=_d, _len=_len, _sign=sign):
                alpha = easing(max(0, min(1, (t - _s) / _d)))
                xv = _xs + alpha * (_xe - _xs)
                slope = (func(xv + h) - func(xv - h)) / (2 * h)
                cx_svg, cy_svg = self.coords_to_point(xv, func(xv), t)
                xspan = self.x_max.at_time(t) - self.x_min.at_time(t)
                yspan = self.y_max.at_time(t) - self.y_min.at_time(t)
                if xspan == 0 or yspan == 0:
                    return (cx_svg + _sign * _len / 2, cy_svg)
                dx_px = self.plot_width / xspan
                ep = _dir_endpoints(cx_svg, cy_svg, dx_px, slope * (-self.plot_height / yspan), _len)
                return ep[0] if _sign < 0 else ep[1]
            return _pt
        _dyn_line(line, creation, _tangent_ep(-1), _tangent_ep(+1))
        self._add_plot_obj(line)
        return line

    def get_secant_line(self, func, x1, x2, length=300, creation=0, z=0, **styling_kwargs):
        """Draw a secant line through func at x1 and x2. Returns a Line."""
        style_kw = {'stroke': '#83C167', 'stroke_width': 2} | styling_kwargs
        line = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z, **style_kw)
        _x1, _x2, _len = x1, x2, length
        def _secant_endpoint(sign):
            def _pt(t, _x1=_x1, _x2=_x2, _len=_len, _sign=sign):
                sx1, sy1 = self.coords_to_point(_x1, func(_x1), t)
                sx2, sy2 = self.coords_to_point(_x2, func(_x2), t)
                mx, my = (sx1 + sx2) / 2, (sy1 + sy2) / 2
                ep = _dir_endpoints(mx, my, sx2 - sx1, sy2 - sy1, _len)
                return ep[0] if _sign < 0 else ep[1]
            return _pt
        _dyn_line(line, creation, _secant_endpoint(-1), _secant_endpoint(+1))
        self._add_plot_obj(line)
        return line

    def get_intersection_point(self, func1, func2, x_range, tol=0.01):
        """Find the x-value where two functions intersect using bisection on *x_range*."""
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
        """Find the intersection of two functions and place a Dot (and optional label) there."""
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
        def _secant_endpoint(sign):
            def _ep(t, _x=_x, _dxs=_dxs, _dxe=_dxe, _s=_s, _d=_d, _len=_len, _easing=easing):
                progress = _easing((t - _s) / _d)
                dx = _dxs + (_dxe - _dxs) * progress
                x1, x2 = _x, _x + dx
                sx1, sy1 = self.coords_to_point(x1, func(x1), t)
                sx2, sy2 = self.coords_to_point(x2, func(x2), t)
                ddx, dy = sx2 - sx1, sy2 - sy1
                mag = max(math.hypot(ddx, dy), 1e-9)
                half = _len / 2
                mx, my = (sx1 + sx2) / 2, (sy1 + sy2) / 2
                return (mx + sign * ddx / mag * half, my + sign * dy / mag * half)
            return _ep
        line.p1.set(start, end, _secant_endpoint(-1), stay=True)
        line.p2.set(start, end, _secant_endpoint(+1), stay=True)
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
        """Plot the numerical derivative of a function using central differences."""
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
        """Visualize the trapezoidal rule approximation of the area under *func*."""
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
        """Draw vertical residual lines from each data point to the regression line."""
        style_kw = {'stroke': '#FF6B6B', 'stroke_width': 2, 'stroke_dasharray': '4 3'} | styling_kwargs
        result = _regression(x_data, y_data)
        if result is None:
            return VCollection(creation=creation, z=z)
        slope, intercept = result
        lines = []
        for xi, yi in zip(x_data, y_data):
            predicted = slope * xi + intercept
            line = Line(x1=0, y1=0, x2=0, y2=0, creation=creation, z=z, **style_kw)
            _dyn_line(line, creation,
                      lambda t, _x=xi, _y=yi: self.coords_to_point(_x, _y, t),
                      lambda t, _x=xi, _p=predicted: self.coords_to_point(_x, _p, t))
            lines.append(line)
            self._add_plot_obj(line)
        group = VCollection(*lines, creation=creation, z=z)
        return group

    def add_spread_band(self, func, spread_func, x_range=None, num_points=100,
                        color='#58C4DD', opacity=0.2, creation=0):
        """Draw a shaded band from func(x)-spread_func(x) to func(x)+spread_func(x)."""
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
            return _band_path(pts_hi, pts_lo)
        band.d.set_onward(creation, _band_d)
        self._add_plot_obj(band)
        return band

    def add_mean_line(self, func_or_data, x_range=None, creation=0, **kwargs):
        """Add a horizontal dashed line at the mean value of a function or data."""
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
        """Add a text label near a function curve at a specific x-position."""
        func = getattr(func_or_curve, '_func', None) or func_or_curve
        buff = 12
        sign = -1 if direction == 'above' else 1

        style_kw = {'fill': '#fff', 'stroke_width': 0, 'text_anchor': 'middle'} | kwargs
        lbl = Text(text=str(label_text), x=0, y=0, font_size=font_size,
                   creation=creation, z=z, **style_kw)

        _get_xv = ((lambda _t, _xp=x_pos: _xp) if x_pos is not None
                   else lambda t: self.x_max.at_time(t))

        def _lbl_x(t): return self._math_to_svg_x(_get_xv(t), t)
        def _lbl_y(t, _f=func, _s=sign, _b=buff, _fz=font_size):
            try:
                yv = _f(_get_xv(t))
            except Exception:
                yv = 0
            return self._math_to_svg_y(yv, t) + _s * (_fz / 2 + _b)
        lbl.x.set_onward(creation, _lbl_x)
        lbl.y.set_onward(creation, _lbl_y)

        self._add_plot_obj(lbl)
        return lbl

    def annotate_area(self, func_or_curve, x_range, label=None, color='#58C4DD',
                       opacity=0.3, start=0, **kwargs):
        """Create a shaded area under a curve with an optional centered label."""
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

