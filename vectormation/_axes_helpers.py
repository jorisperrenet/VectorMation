"""Axes helper functions and constants shared by _axes.py and _axes_ext.py."""
import math

from vectormation._constants import (
    CANVAS_WIDTH, CANVAS_HEIGHT, ORIGIN,
    UNIT, SMALL_BUFF, DEFAULT_FONT_SIZE,
    CHAR_WIDTH_FACTOR, TEXT_Y_OFFSET,
)
from vectormation._base import VCollection
from vectormation._shapes import Line, Text

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


def pi_format(val):
    """Format a numeric value as a multiple of pi using Unicode (e.g. 'pi/2', '2pi')."""
    if abs(val) < 1e-9:
        return '0'
    ratio = val / math.pi
    for denom in [1, 2, 3, 4, 6, 8, 12]:
        numer = round(ratio * denom)
        if abs(ratio - numer / denom) < 1e-9:
            if denom == 1:
                if numer == 1: return '\u03c0'
                if numer == -1: return '-\u03c0'
                return f'{numer}\u03c0'
            if numer == 1: return f'\u03c0/{denom}'
            if numer == -1: return f'-\u03c0/{denom}'
            return f'{numer}\u03c0/{denom}'
    return f'{ratio:.2g}\u03c0'


def pi_ticks(vmin, vmax, step=None):
    """Generate tick values at multiples of pi. Auto-selects step if None."""
    pi = math.pi
    if step is None:
        span = vmax - vmin
        pi_span = span / pi
        if pi_span <= 2: step = pi / 4
        elif pi_span <= 4: step = pi / 2
        elif pi_span <= 8: step = pi
        else: step = 2 * pi
    start = math.ceil(vmin / step - 0.01) * step
    ticks = []
    val = start
    while val <= vmax + step * 0.01:
        if abs(val) < step * 0.01:
            val = 0.0
        ticks.append(val)
        val += step
    return ticks


def _build_axes_decoration(x_min, x_max, y_min, y_max, plot_x, plot_y, plot_width, plot_height,
                            show_grid, time, x_scale='linear', y_scale='linear', tick_format=None,
                            x_tick_format=None, y_tick_format=None,
                            x_ticks=None, y_ticks=None):
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

    # Choose tick values based on scale (allow user override)
    if x_ticks is None:
        x_ticks = _log_ticks(x_min, x_max) if x_scale == 'log' else _nice_ticks(x_min, x_max)
    if y_ticks is None:
        y_ticks = _log_ticks(y_min, y_max) if y_scale == 'log' else _nice_ticks(y_min, y_max)
    # Per-axis tick format falls back to shared tick_format
    _x_fmt = x_tick_format if x_tick_format is not None else tick_format
    _y_fmt = y_tick_format if y_tick_format is not None else tick_format

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
    def _add_ticks(ticks, scale, to_svg_fn, is_x_axis, fmt):
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
            label = _format_tick(val, fmt)
            if is_x_axis:
                objects.append(Text(text=label, x=sv, y=y_zero + tick_len + _TICK_GAP + _TICK_FONT_SIZE * 0.35,
                                    font_size=_TICK_FONT_SIZE, text_anchor='middle',
                                    creation=time, fill='#aaa', stroke_width=0))
            else:
                objects.append(Text(text=label, x=x_zero - tick_len - _TICK_GAP, y=sv + _TICK_FONT_SIZE * 0.35,
                                    font_size=_TICK_FONT_SIZE, text_anchor='end',
                                    creation=time, fill='#aaa', stroke_width=0))
    _add_ticks(x_ticks, x_scale, _to_svg_x, is_x_axis=True, fmt=_x_fmt)
    _add_ticks(y_ticks, y_scale, _to_svg_y, is_x_axis=False, fmt=_y_fmt)

    return VCollection(*objects, creation=time)


