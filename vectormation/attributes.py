"""Time-varying attribute system for VectorMation.

Each attribute (Real, Coor, Color, etc.) wraps a function of time,
enabling smooth animations via set(), move_to(), interpolate(), etc.
"""
from __future__ import annotations
import math
from typing import Any
import vectormation.colors as colors
import vectormation.easings as easings


def _rgb_to_hsl(r, g, b):
    """Convert RGB (0-255) to HSL (0-1)."""
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    mx, mn = max(r, g, b), min(r, g, b)
    l = (mx + mn) / 2.0
    if mx == mn:
        return 0.0, 0.0, l
    d = mx - mn
    s = d / (2.0 - mx - mn) if l > 0.5 else d / (mx + mn)
    if mx == r:
        h = (g - b) / d + (6 if g < b else 0)
    elif mx == g:
        h = (b - r) / d + 2
    else:
        h = (r - g) / d + 4
    return h / 6.0, s, l


def _hue2rgb(p, q, t):
    if t < 0: t += 1
    if t > 1: t -= 1
    if t < 1/6: return p + (q - p) * 6 * t
    if t < 1/2: return q
    if t < 2/3: return p + (q - p) * (2/3 - t) * 6
    return p


def _hsl_to_rgb(h, s, l):
    """Convert HSL (0-1) to RGB (0-255) tuple."""
    if s == 0:
        v = round(l * 255)
        return (v, v, v)
    q = l * (1 + s) if l < 0.5 else l + s - l * s
    p = 2 * l - q
    return (round(_hue2rgb(p, q, h + 1/3) * 255),
            round(_hue2rgb(p, q, h) * 255),
            round(_hue2rgb(p, q, h - 1/3) * 255))


def _wrap(outer, inner, start, end=None, lincl=True, rincl=True, stay=False):
    """Wrap outer time_func with inner on an interval.
    If end is None, applies inner from start onward.
    If end is given, applies inner on [start, end] with optional stay."""
    if end is None:
        def f(t):
            if t < start or (not lincl and t == start):
                return outer(t)
            return inner(t)
    else:
        def f(t):
            if t < start or (not lincl and t == start):
                return outer(t)
            if t > end:
                return f(end) if stay else outer(t)
            if not rincl and t == end:
                return outer(t)
            return inner(t)
    return f


class Real:
    """Real-valued time-varying attribute.

    Example: ``Real(0, 5).at_time(0)`` → ``5``
    """
    time_func: Any

    def __init__(self, creation, start_val: float = 0):
        if isinstance(start_val, Real):
            self.set_to(start_val)
        else:
            self.time_func = lambda t, _c=creation, _v=start_val: _v if t >= _c else 0
            self.last_change = creation

    def set(self, start, end, func_inner, lincl=True, rincl=True, stay=False):
        """Override the value with a custom function on [start, end].

        Example: ``real.set(0, 1, lambda t: t * 10)``
        """
        self.time_func = _wrap(self.time_func, func_inner, start, end, lincl, rincl, stay)
        self.last_change = max(self.last_change, end)

    def add(self, start, end, func_inner, lincl=True, rincl=True, stay=False):
        """Add a function's output to the current value on [start, end].

        Example: ``real.add(0, 1, lambda t: t * 2)``
        """
        outer = self.time_func
        self.time_func = _wrap(outer, lambda t: float(outer(t)) + func_inner(t),
                               start, end, lincl, rincl, stay)
        self.last_change = max(self.last_change, end)

    def set_onward(self, start, value, lincl=True):
        """Set a new value (or function) from ``start`` onward.

        Example: ``real.set_onward(1, 10)``
        """
        inner = value if callable(value) else lambda t: value
        self.time_func = _wrap(self.time_func, inner, start, lincl=lincl)
        self.last_change = max(self.last_change, start)

    def add_onward(self, start, func, lincl=True, last_change=None):
        """Add a constant or function to the current value from ``start`` onward.

        Example: ``real.add_onward(1, 3)``
        """
        outer = self.time_func
        if callable(func):
            inner = lambda t: float(outer(t)) + func(t)  # type: ignore[operator]
        else:
            inner = lambda t: float(outer(t)) + func
        self.time_func = _wrap(outer, inner, start, lincl=lincl)
        self.last_change = max(self.last_change, start)
        if last_change is not None:
            self.last_change = max(self.last_change, last_change)

    def set_at(self, time, value, eps=1e-9):
        """Set the value at exactly one point in time.

        Example: ``real.set_at(1, 99)``
        """
        func_otherwise = self.time_func
        def new_func(t):
            if abs(t - time) < eps: return value
            else: return func_otherwise(t)
        self.time_func = new_func
        self.last_change = max(self.last_change, time)

    def add_at(self, time, value):
        """Add to the current value at exactly one point in time.

        Example: ``real.add_at(1, 3)``
        """
        old = float(self.time_func(time))
        func_otherwise = self.time_func
        def new_func(t):
            if t == time: return old + value
            else: return func_otherwise(t)
        self.time_func = new_func
        self.last_change = max(self.last_change, time)

    def at_time(self, time):
        """Return the value at the given time.

        Example: ``Real(0, 5).at_time(0)`` → ``5``
        """
        return self.time_func(time)

    def set_to(self, other):
        """Copy another attribute's time function and last_change.

        Example: ``real_b.set_to(real_a)``
        """
        self.time_func = lambda t: other.time_func(t)
        self.last_change = other.last_change

    def move_to(self, start, end, end_val, stay=True, easing=easings.smooth):
        """Animate smoothly from the current value to ``end_val``.

        Example: ``real.move_to(0, 1, 10)``
        """
        start_val = self.time_func(start)
        diff = start_val - end_val
        dur = end - start
        if dur <= 0:
            self.set_onward(start, end_val)
        else:
            self.set(start, end, lambda t, _s=start, _d=dur: diff * (1-easing((t-_s)/_d)) + end_val, stay=stay)
        self.last_change = max(self.last_change, end)
        return self

    def apply(self, func):
        """Return a new Real where ``result.at_time(t) = func(self.at_time(t))``.

        Example: ``real.apply(lambda x: x * 2)``
        """
        new = Real(0)
        new.time_func = lambda t: func(self.at_time(t))
        new.last_change = self.last_change
        return new

    def interpolate(self, other, start, end, easing=easings.linear):
        """Create a new Real that interpolates between self and other.

        Example: ``real_a.interpolate(real_b, 0, 1)``
        """
        assert self.__class__ == Real
        assert other.__class__ == Real
        start_val = self.time_func(start)
        end_val = other.time_func(end)
        d = max(end - start, 1e-9)
        new = Real(0)
        new.time_func = lambda t, _s=start, _d=d, _sv=start_val, _ev=end_val: _sv + (_ev - _sv) * easing((t - _s) / _d)
        new.last_change = end
        return new


class Tup(Real):
    """Tuple-valued time-varying attribute (arbitrary length).

    Example: ``Tup(0, (0, 100, 200)).at_time(0)`` → ``(0, 100, 200)``
    """
    def __init__(self, creation, start_val: tuple = ()):
        if isinstance(start_val, Tup):
            self.set_to(start_val)
        else:
            zero = tuple(0 for _ in start_val)
            self.time_func = lambda t, _c=creation, _v=start_val, _z=zero: _v if t >= _c else _z
            self.last_change = creation

    def at_time(self, time) -> tuple:
        return self.time_func(time)

    def add(self, start, end, func_inner, lincl=True, rincl=True, stay=False):
        """Add a tuple element-wise to the current value on [start, end].

        Example: ``tup.add(0, 1, (1, 2, 3))``
        """
        outer = self.time_func
        self.time_func = _wrap(outer,
            lambda t: tuple(float(i) + func_inner[idx] for idx, i in enumerate(outer(t))),
            start, end, lincl, rincl, stay)
        self.last_change = max(self.last_change, end)

    def interpolate(self, other, start, end, easing=easings.linear):
        """Create a new Tup that interpolates element-wise between self and other.

        Example: ``tup_a.interpolate(tup_b, 0, 1)``
        """
        assert self.__class__ == Tup
        assert other.__class__ == Tup
        start_val = self.time_func(start)
        end_val = other.time_func(end)
        d = max(end - start, 1e-9)
        new = Tup(0, ())
        new.time_func = lambda t, _s=start, _d=d, _sv=start_val, _ev=end_val: tuple(
            sv + (ev - sv) * easing((t - _s) / _d) for sv, ev in zip(_sv, _ev))
        new.last_change = end
        return new


class Coor(Real):
    """2D coordinate (x, y) time-varying attribute.

    Example: ``Coor(0, (100, 200)).at_time(0)`` → ``(100, 200)``
    """
    def __init__(self, creation, start_val: tuple[float, float] = (0, 0)):
        self.time_func = lambda t, _c=creation, _v=start_val: _v if t >= _c else (0, 0)
        self.last_change = creation

    def at_time(self, time) -> tuple[float, float]:
        return self.time_func(time)

    def add_onward(self, start, func: tuple | Any, lincl=True, last_change=None):
        """Add a (dx, dy) offset to the current position from ``start`` onward.

        Example: ``coor.add_onward(1, (10, -20))``
        """
        outer = self.time_func
        if callable(func):
            inner = lambda t: (outer(t)[0] + func(t)[0], outer(t)[1] + func(t)[1])  # type: ignore[index]
        else:
            inner = lambda t: (outer(t)[0] + func[0], outer(t)[1] + func[1])
        self.time_func = _wrap(outer, inner, start, lincl=lincl)
        self.last_change = max(self.last_change, start)
        if last_change is not None:
            self.last_change = max(self.last_change, last_change)

    def rotate_around(self, start, end, pivot_point: tuple | Any, degrees, clockwise=False, stay=True):
        """Rotate the coordinate around a pivot point over time.

        Example: ``coor.rotate_around(0, 1, (0, 0), 90)``
        """
        old_func = self.time_func
        sign = -1 if clockwise else 1
        dur = end - start
        if dur <= 0:
            return self
        def f(t):
            now = old_func(t)
            pp: tuple = pivot_point(t) if callable(pivot_point) else pivot_point  # type: ignore[assignment]
            dx, dy = now[0] - pp[0], now[1] - pp[1]
            r = math.hypot(dx, dy)
            base_angle = math.atan2(dy, dx)
            phi = base_angle + sign * math.radians(degrees * (t - start) / dur)
            return (pp[0] + r * math.cos(phi), pp[1] + r * math.sin(phi))
        self.set(start, end, f, stay=stay)
        self.last_change = end
        return self

    def move_to(self, start, end, end_val, stay=True, easing=easings.smooth):
        """Animate smoothly from the current position to ``end_val``.

        Example: ``coor.move_to(0, 1, (100, 200))``
        """
        start_pos = self.time_func(start)
        dx, dy = start_pos[0]-end_val[0], start_pos[1]-end_val[1]
        dur = end - start
        if dur <= 0:
            self.set_onward(start, end_val)
        else:
            self.set(start, end, lambda t, _s=start, _d=dur: (
                dx * (1-easing((t-_s)/_d)) + end_val[0],
                dy * (1-easing((t-_s)/_d)) + end_val[1],
            ), stay=stay)
        self.last_change = max(self.last_change, end)
        return self

    def add(self, start, end, func_inner, lincl=True, rincl=True, stay=False):
        """Add a (dx, dy) function's output to the current position on [start, end].

        Example: ``coor.add(0, 1, lambda t: (t * 10, t * 20))``
        """
        outer = self.time_func
        self.time_func = _wrap(outer,
            lambda t: (float(outer(t)[0]) + func_inner(t)[0], float(outer(t)[1]) + func_inner(t)[1]),
            start, end, lincl, rincl, stay)
        self.last_change = max(self.last_change, end)

    def along_path(self, start, end, path_d, easing=easings.smooth, stay=True):
        """Move the coordinate along an SVG path string over time.

        Example: ``coor.along_path(0, 2, "M 0 0 C 50 0 50 100 100 100")``
        """
        import svgpathtools
        parsed = svgpathtools.parse_path(path_d)
        total_length = parsed.length()
        dur = end - start
        if dur <= 0:
            return self
        def position_at(t, _s=start, _d=dur):
            progress = max(0, min(1, easing((t - _s) / _d)))
            point = parsed.point(parsed.ilength(progress * total_length))  # type: ignore[operator]
            return (point.real, point.imag)
        self.set(start, end, position_at, stay=stay)
        self.last_change = max(self.last_change, end)
        return self


class String(Real):
    """String-valued time-varying attribute.

    Example: ``String(0, 'nonzero').at_time(0)`` → ``'nonzero'``
    """
    def __init__(self, creation, start_val: str = ''):
        if isinstance(start_val, String):
            self.set_to(start_val)
        else:
            self.time_func = lambda t, _c=creation, _v=start_val: _v if t >= _c else ''
            self.last_change = creation


class Color:
    """Time-varying color attribute. Accepts hex, named colors, RGB/RGBA tuples, or gradients.

    Example: ``Color(0, '#ff0000').at_time(0)`` → ``'rgb(255,0,0)'``
    """
    def __init__(self, creation: float = 0, start_color: 'str | tuple' = '#000', use=None):
        assert isinstance(creation, int | float)
        if use is not None:
            assert isinstance(use, str)
            self.use = use
        if isinstance(start_color, Color):
            self.set_to(start_color)
        else:
            self.use, col = self.parse(start_color)
            if self.use in ('rgb', 'rgba'):
                self.time_func = lambda t, _c=creation, _v=col: _v if t >= _c else tuple(0 for _ in _v)
            elif self.use == 'url':
                self.time_func = lambda t: col
            else:
                raise NotImplementedError(f'Color type {self.use!r} not supported')
        self.last_change = creation

    def set(self, start, end, func_inner, lincl=True, rincl=True, stay=False):
        """Override the color with a custom function returning ``(r, g, b)`` on [start, end].

        Example: ``color.set(0, 1, lambda t: (255, int(t*255), 0))``
        """
        self.time_func = _wrap(self.time_func, func_inner, start, end, lincl, rincl, stay)
        self.last_change = max(self.last_change, end)

    def set_to(self, other):
        """Copy another Color's time function, use type, and last_change.

        Example: ``color_b.set_to(color_a)``
        """
        assert isinstance(other, Color)
        self.use = other.use
        self.time_func = lambda t: other.time_func(t)
        self.last_change = other.last_change

    def parse(self, color):
        """Parse a color input into a ``(use_type, value)`` tuple.

        Example: ``Color().parse('#ff0000')`` → ``('rgb', (255, 0, 0))``
        """
        if isinstance(color, colors._Gradient):
            return ('url', color.fill_ref())
        elif isinstance(color, tuple):
            if len(color) == 3:
                return ('rgb', color)
            elif len(color) == 4:
                return ('rgba', color)
            else:
                raise ValueError('Length of tuple does not match rgb or rgba lengths')
        elif isinstance(color, str):
            if color.startswith('url('):
                return ('url', color)
            if color[0] != '#':
                color = colors.color_from_name(color.upper())
            if color[0] == '#':
                if len(color) == 4:
                    return ('rgb', (int(color[1]*2, 16), int(color[2]*2, 16), int(color[3]*2, 16)))
                elif len(color) == 7:
                    return ('rgb', (int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)))
                elif len(color) == 9:
                    return ('rgba', (int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16), int(color[7:9], 16)))
                else:
                    raise ValueError(f'Invalid hex color length: {color!r}')
            raise ValueError(f'Invalid color string: {color!r}')
        else:
            raise ValueError('Type of color unknown')

    def at_time(self, time, rounding_func=round):
        """Return the SVG color string at the given time.

        Example: ``Color(0, '#ff0000').at_time(0)`` → ``'rgb(255,0,0)'``
        """
        if self.use in ('rgb', 'rgba'):
            vals = ','.join(str(rounding_func(v)) for v in self.time_func(time))
            return f'{self.use}({vals})'
        elif self.use == 'url':
            return self.time_func(time)
        else:
            raise NotImplementedError(f'Color type {self.use!r} not supported')

    def interpolate(self, other, start, end, easing=easings.linear, color_space='rgb'):
        """Create a new Color that interpolates between self and other.

        Example: ``Color(0, '#f00').interpolate(Color(0, '#00f'), 0, 1)``
        """
        assert self.__class__ == Color
        assert other.__class__ == Color
        if color_space == 'hsl':
            return self.interpolate_hsl(other, start, end, easing=easing)
        if self.use == other.use == 'rgb':
            start_val = self.time_func(start)
            end_val = other.time_func(end)
            d = max(end - start, 1e-9)
            new = Color(use='rgb')
            new.time_func = lambda t, _s=start, _d=d, _sv=start_val, _ev=end_val: tuple(
                sv + (ev - sv) * easing((t - _s) / _d) for sv, ev in zip(_sv, _ev))
            new.last_change = end
            return new
        else:
            raise NotImplementedError('Only rgb colors can be transformed yet.')

    def interpolate_hsl(self, other, start, end, easing=easings.linear):
        """Interpolate through HSL color space (smoother hue transitions).

        Example: ``Color(0, '#f00').interpolate(Color(0, '#00f'), 0, 1, color_space='hsl')``
        """
        assert self.__class__ == Color
        assert other.__class__ == Color

        h1, s1, l1 = _rgb_to_hsl(*self.time_func(start)[:3])
        h2, s2, l2 = _rgb_to_hsl(*other.time_func(end)[:3])

        dh = h2 - h1
        if dh > 0.5: dh -= 1.0
        elif dh < -0.5: dh += 1.0

        new = Color(use='rgb')
        _d = max(end - start, 1e-9)
        _dh, _ds, _dl = dh, s2 - s1, l2 - l1
        def _interp(t, _st=start, _dur=_d, _h1=h1, _s1=s1, _l1=l1, _ddh=_dh, _dds=_ds, _ddl=_dl):
            p = easing((t - _st) / _dur)
            return _hsl_to_rgb((_h1 + _ddh * p) % 1.0, _s1 + _dds * p, _l1 + _ddl * p)
        new.time_func = _interp
        new.last_change = end
        return new

    def apply(self, func):
        """Return a new Color where ``result.time_func(t) = func(self.time_func(t))``.

        Example: ``color.apply(lambda rgb: (255 - rgb[0], 255 - rgb[1], 255 - rgb[2]))``
        """
        new = Color(use=self.use)
        new.time_func = lambda t: func(self.time_func(t))
        new.last_change = self.last_change
        return new

    def set_onward(self, start, value, lincl=True):
        """Set a new color from ``start`` onward.

        Example: ``color.set_onward(1, '#00ff00')``
        """
        if callable(value):
            inner = value
        else:
            use, color = self.parse(value)
            assert use == self.use, f'Color type mismatch: {use} vs {self.use}'
            inner = lambda t: color
        self.time_func = _wrap(self.time_func, inner, start, lincl=lincl)
        self.last_change = max(self.last_change, start)
