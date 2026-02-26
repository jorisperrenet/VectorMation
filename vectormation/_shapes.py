"""Shape classes: Polygon, Circle, Rectangle, Line, Text, Arc, etc."""
import math
from xml.sax.saxutils import escape as _xml_escape

import vectormation.easings as easings
import vectormation.attributes as attributes
import vectormation.style as style
from vectormation.pathbbox import path_bbox
from vectormation._constants import (
    SMALL_BUFF, DEFAULT_STROKE_WIDTH, DEFAULT_DOT_RADIUS,
    _rotate_point, _sample_function,
)
from vectormation._base import VObject

class Polygon(VObject):
    def __init__(self, *vertices, closed=True, z=0, creation=0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        self.closed = closed
        self.vertices = [attributes.Coor(creation, v) for v in vertices]
        defaults = dict(fill_opacity=0.7, stroke='#fff', stroke_width=DEFAULT_STROKE_WIDTH)
        if not closed:
            defaults = dict(stroke='#fff', stroke_width=DEFAULT_STROKE_WIDTH, fill_opacity=0)
        self.styling = style.Styling(styling_kwargs, creation=creation, **defaults)
        self._bbox_cache = None
        self._bbox_version = 0

    def _extra_attrs(self):
        return self.vertices

    def _shift_coors(self):
        return self.vertices

    def shift(self, *args, **kwargs):
        self._bbox_version += 1
        return super().shift(*args, **kwargs)

    def snap_points(self, time):
        return [(float(x), float(y)) for x, y in (v.at_time(time) for v in self.vertices)]

    def bbox(self, time):
        if self._bbox_cache and self._bbox_cache[0] == time and self._bbox_cache[1] == self._bbox_version:
            return self._bbox_cache[2]
        points = [v.at_time(time) for v in self.vertices]
        result = self._bbox_from_points(points, time) or super().bbox(time)
        self._bbox_cache = (time, self._bbox_version, result)
        return result

    def path(self, time):
        vert = [v.at_time(time) for v in self.vertices]
        parts = [f'M {vert[0][0]},{vert[0][1]}'] + [f'L {x},{y}' for x, y in vert[1:]]
        if self.closed:
            parts.append('Z')
        return ' '.join(parts)

    def to_svg(self, time):
        tag = 'polygon' if self.closed else 'polyline'
        pts = ' '.join(f'{x},{y}' for x, y in (v.at_time(time) for v in self.vertices))
        return f"<{tag} points='{pts}'{self.styling.svg_style(time)} />"


class Ellipse(VObject):
    def __init__(self, rx: float = 120, ry: float = 60, cx: float = 960, cy: float = 540, z=0, creation=0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        self.c = attributes.Coor(creation, (cx, cy))
        self.rx = attributes.Real(creation, rx)
        self.ry = attributes.Real(creation, ry)
        self.styling = style.Styling(styling_kwargs, creation=creation,
                                     fill_opacity=0.7, stroke='#fff', stroke_width=DEFAULT_STROKE_WIDTH)

    def _extra_attrs(self):
        return [self.c, self.rx, self.ry]

    def _shift_coors(self):
        return [self.c]

    def snap_points(self, time):
        cx, cy = self.c.at_time(time)
        return [(float(cx), float(cy))]

    def bbox(self, time):
        cx, cy = self.c.at_time(time)
        rx, ry = self.rx.at_time(time), self.ry.at_time(time)
        return self._bbox_from_points([(cx-rx, cy), (cx+rx, cy), (cx, cy-ry), (cx, cy+ry)], time) or super().bbox(time)

    def path(self, time):
        rx, ry = self.rx.at_time(time), self.ry.at_time(time)
        cx, cy = self.c.at_time(time)
        return f'M{cx-rx},{cy}a{rx},{ry} 0 1,0 {rx*2},0a{rx},{ry} 0 1,0 -{rx*2},0z'

    def to_svg(self, time):
        cx, cy = self.c.at_time(time)
        return f"<ellipse cx='{cx}' cy='{cy}' rx='{self.rx.at_time(time)}' ry='{self.ry.at_time(time)}'{self.styling.svg_style(time)} />"


class Circle(Ellipse):
    """Circle: Ellipse with rx == ry."""
    def __init__(self, r: float = 120, cx: float = 960, cy: float = 540, z=0, creation=0, **styling_kwargs):
        super().__init__(rx=r, ry=r, cx=cx, cy=cy, z=z, creation=creation, **styling_kwargs)

    @property
    def r(self):
        return self.rx

    @r.setter
    def r(self, value):
        self.rx = value
        self.ry = value

    def point_at_angle(self, degrees, time=0):
        """Return (x, y) on the circle at the given angle (degrees, CCW from right)."""
        cx, cy = self.c.at_time(time)
        r = self.rx.at_time(time)
        rad = math.radians(degrees)
        return (cx + r * math.cos(rad), cy - r * math.sin(rad))

    def to_svg(self, time):
        cx, cy = self.c.at_time(time)
        return f"<circle cx='{cx}' cy='{cy}' r='{self.rx.at_time(time)}'{self.styling.svg_style(time)} />"


class Dot(Circle):
    """Small filled circle, no stroke."""
    def __init__(self, r: float = DEFAULT_DOT_RADIUS, cx: float = 960, cy: float = 540, z=0, creation=0, **styling_kwargs):
        super().__init__(r=r, cx=cx, cy=cy, z=z, creation=creation,
                         **({'fill': '#fff', 'fill_opacity': 1, 'stroke_width': 0} | styling_kwargs))


class Rectangle(VObject):
    def __init__(self, width, height, x=960, y=540, rx=0, ry=0, creation=0, z=0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        self.x = attributes.Real(creation, x)
        self.y = attributes.Real(creation, y)
        self.width = attributes.Real(creation, width)
        self.height = attributes.Real(creation, height)
        self.rx = attributes.Real(creation, rx)
        self.ry = attributes.Real(creation, ry)
        self.styling = style.Styling(styling_kwargs, creation=creation, fill_opacity=0.7, stroke='#fff', stroke_width=DEFAULT_STROKE_WIDTH)

    def _extra_attrs(self):
        return [self.x, self.y, self.width, self.height, self.rx, self.ry]

    def _shift_reals(self):
        return [(self.x, self.y)]

    def snap_points(self, time):
        x, y = self.x.at_time(time), self.y.at_time(time)
        w, h = self.width.at_time(time), self.height.at_time(time)
        return [(float(x), float(y)), (float(x+w), float(y)),
                (float(x+w), float(y+h)), (float(x), float(y+h))]

    def bbox(self, time):
        x, y = self.x.at_time(time), self.y.at_time(time)
        w, h = self.width.at_time(time), self.height.at_time(time)
        return self._bbox_from_points([(x,y),(x+w,y),(x+w,y+h),(x,y+h)], time) or super().bbox(time)

    def path(self, time):
        x, y = self.x.at_time(time), self.y.at_time(time)
        w, h = self.width.at_time(time), self.height.at_time(time)
        rx, ry = self.rx.at_time(time), self.ry.at_time(time)
        if rx == 0 and ry == 0:
            return f'M{x},{y}l{w},0l0,{h}l-{w},0z'
        return (f'M{x+rx},{y} l {w-rx*2},0 '
                f'a {rx},{ry} 0 0,1 {rx},{ry} l 0,{h-ry*2} '
                f'a {rx},{ry} 0 0,1 -{rx},{ry} l {rx*2-w},0 '
                f'a {rx},{ry} 0 0,1 -{rx},-{ry} l 0,{ry*2-h} '
                f'a {rx},{ry} 0 0,1 {rx},-{ry} z')

    def to_svg(self, time):
        return (f"<rect x='{self.x.at_time(time)}' y='{self.y.at_time(time)}'"
                f" width='{self.width.at_time(time)}' height='{self.height.at_time(time)}'"
                f" rx='{self.rx.at_time(time)}' ry='{self.ry.at_time(time)}'"
                f"{self.styling.svg_style(time)} />")


class Line(VObject):
    def __init__(self, x1: float = 0, y1: float = 0, x2: float = 100, y2: float = 100, creation=0, z=0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        self.p1 = attributes.Coor(creation, (x1, y1))
        self.p2 = attributes.Coor(creation, (x2, y2))
        self.styling = style.Styling(styling_kwargs, creation=creation, stroke='#fff', stroke_width=DEFAULT_STROKE_WIDTH)

    def _extra_attrs(self):
        return [self.p1, self.p2]

    def _shift_coors(self):
        return [self.p1, self.p2]

    def snap_points(self, time):
        p1, p2 = self.p1.at_time(time), self.p2.at_time(time)
        return [(float(p1[0]), float(p1[1])), (float(p2[0]), float(p2[1]))]

    def bbox(self, time):
        return self._bbox_from_points([self.p1.at_time(time), self.p2.at_time(time)], time) or super().bbox(time)

    def path(self, time):
        x1, y1 = self.p1.at_time(time)
        x2, y2 = self.p2.at_time(time)
        return f'M{x1},{y1}L{x2},{y2}'

    def to_svg(self, time):
        p1, p2 = self.p1.at_time(time), self.p2.at_time(time)
        return f"<line x1='{p1[0]}' y1='{p1[1]}' x2='{p2[0]}' y2='{p2[1]}'{self.styling.svg_style(time)} />"


class Text(VObject):
    """Plain SVG text element."""
    _NARROW = set('iIlj1|!.,;:\'"()[]{}')
    _WIDE = set('mMwWOQD@')

    def __init__(self, text='', x: float = 960, y: float = 540, font_size: float = 48, text_anchor=None, creation: float = 0, z=0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        self.text = attributes.String(creation, text)
        self.x = attributes.Real(creation, x)
        self.y = attributes.Real(creation, y)
        self.font_size = attributes.Real(creation, font_size)
        self._text_anchor = text_anchor
        self.styling = style.Styling(styling_kwargs, creation=creation,
                                     fill='#fff', fill_opacity=1, stroke_width=0)

    def _extra_attrs(self):
        return [self.text, self.x, self.y, self.font_size]

    def _shift_reals(self):
        return [(self.x, self.y)]

    def snap_points(self, time):
        return [(float(self.x.at_time(time)), float(self.y.at_time(time)))]

    @staticmethod
    def _estimate_width(text, fs):
        return sum(fs * (0.35 if ch in Text._NARROW else 0.75 if ch in Text._WIDE
                         else 0.3 if ch == ' ' else 0.65 if ch.isupper() else 0.55)
                   for ch in str(text))

    def _text_left(self, x, w):
        if self._text_anchor == 'middle':
            return x - w / 2
        if self._text_anchor == 'end':
            return x - w
        return x

    def path(self, time):
        x, y, fs = self.x.at_time(time), self.y.at_time(time), self.font_size.at_time(time)
        w = self._estimate_width(self.text.at_time(time), fs)
        xl = self._text_left(x, w)
        return f'M{xl},{y-fs}L{xl+w},{y-fs}L{xl+w},{y}L{xl},{y}Z'

    def bbox(self, time):
        x, y, fs = self.x.at_time(time), self.y.at_time(time), self.font_size.at_time(time)
        w = self._estimate_width(self.text.at_time(time), fs)
        return (self._text_left(x, w), y - fs, w, fs)

    def typing(self, start: float = 0, end: float = 1, change_existence=True):
        """Typewriter effect: reveal text character by character over [start, end]."""
        full_text = self.text.at_time(start)
        n = len(full_text)
        if n == 0:
            return self
        if change_existence:
            self._show_from(start)
        s, e = start, end
        dur = e - s
        if dur <= 0:
            self.text.set_onward(s, full_text)
            return self
        self.text.set(s, e, lambda t, _s=s, _d=dur, _n=n: full_text[:max(1, int(_n * (t - _s) / _d))], stay=True)
        return self

    def highlight(self, start=0, end=1, color='#FFFF00', opacity=0.3, padding=4, easing=easings.there_and_back):
        """Highlight the text with a colored background rectangle that fades in/out.
        Returns the highlight Rectangle (must be added to canvas separately)."""
        bx, by, bw, bh = self.bbox(start)
        rect = Rectangle(bw + 2 * padding, bh + 2 * padding,
                         x=bx - padding, y=by - padding,
                         creation=start, fill=color, fill_opacity=0, stroke_width=0)
        dur = end - start
        if dur <= 0:
            return rect
        rect.styling.fill_opacity.set(start, end,
            lambda t, _s=start, _d=dur: opacity * easing((t - _s) / _d), stay=True)
        return rect

    def typewrite(self, start=0, end=1, cursor='|', change_existence=True):
        """Reveal text character by character like a typewriter.
        The text attribute is updated progressively with an optional cursor character."""
        if change_existence:
            self._show_from(start)
        full_text = self.text.at_time(start)
        n = len(full_text)
        if n == 0:
            return self
        dur = end - start
        if dur <= 0:
            return self
        s = start
        def _typed(t):
            progress = min(1, (t - s) / dur)
            chars = int(progress * n)
            shown = full_text[:chars]
            if chars < n:
                return shown + cursor
            return shown
        self.text.set(s, end, _typed, stay=True)
        self.text.set_onward(end, full_text)
        return self

    def untype(self, start=0, end=1, change_existence=True):
        """Reverse typewriter: remove characters right-to-left."""
        full_text = self.text.at_time(start)
        n = len(full_text)
        if n == 0:
            return self
        dur = end - start
        if dur <= 0:
            return self
        s = start
        def _untyped(t, _s=s, _d=dur, _n=n, _ft=full_text):
            progress = min(1, (t - _s) / _d)
            remaining = _n - int(progress * _n)
            return _ft[:max(0, remaining)]
        self.text.set(s, end, _untyped, stay=True)
        self.text.set_onward(end, '')
        if change_existence:
            self._hide_from(end)
        return self

    def scramble(self, start=0, end=1, charset=None, change_existence=True):
        """Decode/reveal text from random characters. Characters settle left-to-right."""
        if change_existence:
            self._show_from(start)
        full_text = self.text.at_time(start)
        n = len(full_text)
        if n == 0:
            return self
        dur = end - start
        if dur <= 0:
            return self
        if charset is None:
            charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%&*'
        import random
        rng = random.Random(42)  # deterministic for reproducibility
        _randoms = [[rng.choice(charset) for _ in range(20)] for _ in range(n)]
        s = start
        def _scrambled(t):
            progress = min(1, (t - s) / dur)
            settled = int(progress * n)
            result = list(full_text[:settled])
            frame = int((t - s) * 15) % 20  # cycle through pre-generated randoms
            for i in range(settled, n):
                if full_text[i] == ' ':
                    result.append(' ')
                else:
                    result.append(_randoms[i][frame])
            return ''.join(result)
        self.text.set(s, end, _scrambled, stay=True)
        self.text.set_onward(end, full_text)
        return self

    def set_text(self, start: float, end: float, new_text, easing=easings.smooth):
        """Fade out old text and fade in new text over [start, end].
        Opacity goes to 0 at midpoint, text changes, opacity returns."""
        if start >= end:
            self.text.set_onward(start, new_text)
            return self
        mid = (start + end) / 2
        dur1, dur2 = mid - start, end - mid
        self.styling.opacity.set(start, mid,
            lambda t, _s=start, _d=dur1: 1 - easing((t - _s) / _d), stay=True)
        self.text.set_onward(mid, new_text)
        self.styling.opacity.set(mid, end,
            lambda t, _m=mid, _d=dur2: easing((t - _m) / _d), stay=True)
        return self

    def underline_anim(self, start: float = 0, end: float = 1, color=None,
                        stroke_width=2, offset_y=5):
        """Create an animated underline under this text. Returns a Line object."""
        bx, by, bw, bh = self.bbox(start)
        line_y = by + bh + offset_y
        line_color = color or self.styling.fill.at_time(start)
        line = Line(x1=bx, y1=line_y, x2=bx, y2=line_y, creation=start,
                    stroke=line_color, stroke_width=stroke_width)
        dur = end - start
        if dur > 0:
            s, x1, x2 = start, bx, bx + bw
            line.p2.set(s, end,
                lambda t, _s=s, _d=dur, _x1=x1, _x2=x2, _y=line_y: (
                    _x1 + (_x2 - _x1) * easings.smooth((t - _s) / _d), _y),
                stay=True)
        return line

    def split_words(self, time=0):
        """Split text into a VCollection of individual word Text objects.
        Words are positioned horizontally at approximate character offsets."""
        from vectormation._base import VCollection
        full = str(self.text.at_time(time))
        words = full.split()
        if not words:
            return VCollection()
        x = self.x.at_time(time)
        y = self.y.at_time(time)
        fs = self.font_size.at_time(time)
        char_width = fs * 0.6  # approximate monospace char width
        parts = []
        cursor = 0
        for word in words:
            idx = full.index(word, cursor)
            wx = x + idx * char_width
            t = Text(text=word, x=wx, y=y, font_size=fs,
                     creation=time, stroke_width=0,
                     fill=self.styling.fill.at_time(time))
            parts.append(t)
            cursor = idx + len(word)
        return VCollection(*parts)

    def to_svg(self, time):
        anchor = f" text-anchor='{self._text_anchor}'" if self._text_anchor else ''
        txt = _xml_escape(str(self.text.at_time(time)))
        return (f"<text x='{self.x.at_time(time)}' y='{self.y.at_time(time)}'"
                f" font-size='{self.font_size.at_time(time)}'{anchor}{self.styling.svg_style(time)}"
                f">{txt}</text>")


class CountAnimation(Text):
    """Text that animates a number counting from start_val to end_val."""
    def __init__(self, start_val=0, end_val=100, start: float = 0, end: float = 1,
                 fmt='{:.0f}', easing=easings.smooth,
                 x: float = 960, y: float = 540, font_size: float = 60, text_anchor=None, creation: float = 0, z=0, **styling_kwargs):
        super().__init__(text=fmt.format(start_val), x=x, y=y,
                         font_size=font_size, text_anchor=text_anchor,
                         creation=creation, z=z, **styling_kwargs)
        s, e = start, end
        dur = e - s
        if dur <= 0:
            self.text.set_onward(s, fmt.format(end_val))
        else:
            self.text.set(s, e,
                lambda t, _s=s, _d=dur, _sv=start_val, _ev=end_val, _fmt=fmt: _fmt.format(_sv + (_ev - _sv) * easing((t - _s) / _d)),
                stay=True)
        self._fmt = fmt
        self._last_val = end_val

    def count_to(self, target, start, end, easing=easings.smooth):
        """Animate counting from the current value to a new target."""
        from_val = self._last_val
        fmt = self._fmt
        dur = end - start
        if dur <= 0:
            self.text.set_onward(start, fmt.format(target))
        else:
            s = start
            self.text.set(s, end,
                lambda t, _f=from_val, _t=target, _s=s, _d=dur, _fmt=fmt:
                    _fmt.format(_f + (_t - _f) * easing((t - _s) / _d)),
                stay=True)
        self._last_val = target
        return self


class ValueTracker:
    """Convenience wrapper around a time-varying Real attribute.

    Use to drive reactive animations (e.g. link a label's position to a value).
    """
    def __init__(self, value=0, creation=0):
        self.value = attributes.Real(creation, value)
        self.show = attributes.Real(creation, True)

    @property
    def last_change(self):
        return self.value.last_change

    def get_value(self, time=0):
        return self.value.at_time(time)

    def set_value(self, val, start=0):
        self.value.set_onward(start, val)
        return self

    def animate_value(self, target, start, end, easing=easings.smooth):
        self.value.move_to(start, end, target, easing=easing)
        return self

    def at_time(self, time):
        return self.value.at_time(time)


class DecimalNumber(Text):
    """Text that dynamically displays a numeric value, updating each frame.

    value: initial numeric value, or an attributes.Real / ValueTracker to track.
    fmt: format string for display.
    """
    def __init__(self, value=0, fmt='{:.2f}', x=960, y=540, font_size=48,
                 text_anchor=None, creation=0, z=0, **styling_kwargs):
        if isinstance(value, ValueTracker):
            tracker = value.value
        elif isinstance(value, attributes.Real):
            tracker = value
        else:
            tracker = attributes.Real(creation, value)
        self._tracker = tracker
        super().__init__(text=fmt.format(tracker.at_time(creation)), x=x, y=y,
                         font_size=font_size, text_anchor=text_anchor,
                         creation=creation, z=z, **styling_kwargs)
        self.text.set_onward(creation, lambda t: fmt.format(tracker.at_time(t)))

    @property
    def tracker(self):
        return self._tracker

    def set_value(self, val, start=0):
        self._tracker.set_onward(start, val)
        return self

    def animate_value(self, target, start, end, easing=easings.smooth):
        self._tracker.move_to(start, end, target, easing=easing)
        return self


class Lines(Polygon):
    """Open polyline — a Polygon with closed=False."""
    def __init__(self, *vertices, creation=0, z=0, **styling_kwargs):
        super().__init__(*vertices, closed=False, creation=creation, z=z, **styling_kwargs)


class Trace(VObject):
    """Follows a point every dt and renders as a polyline."""
    def __init__(self, point, start=0, end=None, dt=1/60, z=0, **styling_kwargs):
        super().__init__(creation=start, z=z)
        self.start = start
        self.end = end
        self.dt = dt
        self.p = point
        self.styling = style.Styling(styling_kwargs, creation=start, stroke='#fff', stroke_width=DEFAULT_STROKE_WIDTH)
        self._vert_cache = []
        self._str_parts = []  # List of "x,y" strings

    def _extra_attrs(self):
        return [self.p]

    def snap_points(self, time):
        pos = self.p.at_time(time)
        return [(float(pos[0]), float(pos[1]))]

    def shift(self, dx=0, dy=0, start_time: float = 0, end_time: float | None = None, easing=easings.smooth):
        """Shift via styling transform (Trace points are immutable)."""
        if end_time is None:
            self.styling.dx.add_onward(start_time, dx)
            self.styling.dy.add_onward(start_time, dy)
        else:
            s, e = start_time, end_time
            d = max(e - s, 1e-9)
            self.styling.dx.add_onward(s, lambda t, _s=s, _d=d: dx * easing((t-_s)/_d), last_change=e)
            self.styling.dy.add_onward(s, lambda t, _s=s, _d=d: dy * easing((t-_s)/_d), last_change=e)
        return self

    def path(self, time):
        verts = self.vertices(time)
        if not verts:
            return ''
        parts = [f'M {verts[0][0]},{verts[0][1]}']
        parts.extend(f'L {x},{y}' for x, y in verts[1:])
        return ' '.join(parts)

    def vertices(self, time):
        end = min(self.end, time) if self.end is not None else time
        steps = int((end - self.start) / self.dt)
        verts = self._vert_cache[:steps]
        t = self.start + len(verts) * self.dt
        prev_len = len(verts)
        for _ in range(steps - prev_len):
            verts.append(self.p.at_time(t))
            t += self.dt
        if len(verts) > prev_len:
            self._vert_cache = verts
            self._str_parts.extend(f'{x},{y}' for x, y in verts[prev_len:])
        return verts

    def to_svg(self, time):
        self.vertices(time)
        end = min(self.end, time) if self.end is not None else time
        steps = int((end - self.start) / self.dt)
        if steps == 0:
            return ''
        pts = ' '.join(self._str_parts[:steps])
        cur = self.p.at_time(time)
        return f"<polyline points='{pts} {cur[0]},{cur[1]}'{self.styling.svg_style(time)} />"

    def to_polygon(self, time):
        return Polygon(*self.vertices(time), creation=time, z=self.z.at_time(time), **self.styling.kwargs())

class Path(VObject):
    """SVG path element with a 'd' attribute."""
    def __init__(self, path, x=0, y=0, creation: float = 0, z=0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        self.d = attributes.String(creation, path)
        self.styling = style.Styling(styling_kwargs, creation=creation, stroke='#fff')
        self.styling.dx.add_onward(creation, lambda t: x * self.styling.scale_x.at_time(t))
        self.styling.dy.add_onward(creation, lambda t: y * self.styling.scale_y.at_time(t))

    def _extra_attrs(self):
        return [self.d]

    def snap_points(self, time):
        d = self.d.at_time(time)
        if d:
            xmin, xmax, ymin, ymax = path_bbox(d)
            return [(float(xmin), float(ymin)), (float(xmax), float(ymin)),
                    (float(xmax), float(ymax)), (float(xmin), float(ymax))]
        return []

    def shift(self, dx=0, dy=0, start_time: float = 0, end_time: float | None = None, easing=easings.smooth):
        """Shift via transform styling, accounting for current rotation."""
        rot = self.styling.rotation.at_time(0)
        if rot[0] != 0:
            dx, dy = _rotate_point(dx, dy, rot[1], rot[2], -rot[0] * math.pi / 180)
        if end_time is None:
            self.styling.dx.add_onward(start_time, dx)
            self.styling.dy.add_onward(start_time, dy)
        else:
            s, e = start_time, end_time
            d = max(e - s, 1e-9)
            self.styling.dx.add_onward(s, lambda t, _s=s, _d=d: dx * easing((t-_s)/_d), last_change=e)
            self.styling.dy.add_onward(s, lambda t, _s=s, _d=d: dy * easing((t-_s)/_d), last_change=e)
        return self

    def point_from_proportion(self, proportion, time=0):
        """Return (x, y) at a proportional distance along the path (0-1)."""
        try:
            from svgpathtools import parse_path
        except ImportError:
            raise ImportError("svgpathtools is required for point_from_proportion")
        d = self.d.at_time(time)
        if not d:
            return (0, 0)
        parsed = parse_path(d)
        total = parsed.length()
        if total == 0:
            pt = parsed.point(0)
            return (pt.real, pt.imag)
        pt = parsed.point(parsed.ilength(total * max(0, min(1, proportion))))
        return (pt.real, pt.imag)

    def path(self, time):
        return self.d.at_time(time)

    def to_svg(self, time):
        return f"<path d='{self.d.at_time(time)}'{self.styling.svg_style(time)} />"


class Image(VObject):
    """SVG <image> element."""
    def __init__(self, href, x=0, y=0, width=1, height=1, creation=0, z=0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        self.href = href
        self.x = attributes.Real(creation, x)
        self.y = attributes.Real(creation, y)
        self.width = attributes.Real(creation, width)
        self.height = attributes.Real(creation, height)
        self.styling = style.Styling(styling_kwargs, creation=creation, stroke_width=0)

    def _extra_attrs(self):
        return [self.x, self.y, self.width, self.height]

    def _shift_reals(self):
        return [(self.x, self.y)]

    def path(self, time):
        x, y = self.x.at_time(time), self.y.at_time(time)
        w, h = self.width.at_time(time), self.height.at_time(time)
        return f'M{x},{y}L{x+w},{y}L{x+w},{y+h}L{x},{y+h}Z'

    def bbox(self, time):
        x, y = self.x.at_time(time), self.y.at_time(time)
        w, h = self.width.at_time(time), self.height.at_time(time)
        return self._bbox_from_points([(x,y),(x+w,y),(x+w,y+h),(x,y+h)], time) or super().bbox(time)

    def to_svg(self, time):
        return (f"<image href='{self.href}' x='{self.x.at_time(time)}' y='{self.y.at_time(time)}'"
                f" width='{self.width.at_time(time)}' height='{self.height.at_time(time)}'"
                f"{self.styling.svg_style(time)} />")


class RegularPolygon(Polygon):
    """Regular n-sided polygon inscribed in a circle of given radius."""
    def __init__(self, n, radius=120, cx=960, cy=540, angle=0, creation=0, z=0, **styling_kwargs):
        n = max(n, 1)
        angle_rad = angle * math.pi / 180
        vertices = [
            (cx + radius * math.cos(2 * math.pi * k / n + angle_rad),
             cy - radius * math.sin(2 * math.pi * k / n + angle_rad))
            for k in range(n)
        ]
        super().__init__(*vertices, creation=creation, z=z, **styling_kwargs)


class Star(Polygon):
    """Star polygon with n outer points. outer_radius and inner_radius control the shape."""
    def __init__(self, n=5, outer_radius=120, inner_radius=None, cx=960, cy=540,
                 angle=90, creation=0, z=0, **styling_kwargs):
        n = max(n, 1)
        if inner_radius is None:
            inner_radius = outer_radius * 0.4
        angle_rad = angle * math.pi / 180
        vertices = []
        for k in range(2 * n):
            r = outer_radius if k % 2 == 0 else inner_radius
            a = math.pi * k / n + angle_rad
            vertices.append((cx + r * math.cos(a), cy - r * math.sin(a)))
        super().__init__(*vertices, creation=creation, z=z, **styling_kwargs)


class EquilateralTriangle(RegularPolygon):
    """Equilateral triangle: RegularPolygon with n=3.
    side_length is converted to the circumscribed radius."""
    def __init__(self, side_length, angle=0, cx=960, cy=540, creation=0, z=0, **styling_kwargs):
        radius = side_length / math.sqrt(3)
        super().__init__(3, radius=radius, cx=cx, cy=cy, angle=angle + 90,
                         creation=creation, z=z, **styling_kwargs)


class RoundedRectangle(Rectangle):
    """Rectangle with rounded corners (default corner_radius=10)."""
    def __init__(self, width, height, x=960, y=540, corner_radius=12, creation=0, z=0, **styling_kwargs):
        super().__init__(width, height, x=x, y=y, rx=corner_radius, ry=corner_radius,
                         creation=creation, z=z, **styling_kwargs)


class SurroundingRectangle(RoundedRectangle):
    """Rectangle that surrounds a target object with padding.
    If follow=True (default), tracks the target as it moves."""
    def __init__(self, target, buff=SMALL_BUFF, corner_radius=6, follow=True,
                 creation=0, z=0, **styling_kwargs):
        bx, by, bw, bh = target.bbox(creation)
        style_kw = {'fill_opacity': 0, 'stroke': '#FFFF00'} | styling_kwargs
        super().__init__(bw + 2*buff, bh + 2*buff, x=bx - buff, y=by - buff,
                         corner_radius=corner_radius, creation=creation, z=z, **style_kw)
        if follow:
            _cache = {}
            def _bbox(t):
                if t not in _cache:
                    _cache.clear()
                    _cache[t] = target.bbox(t)
                return _cache[t]
            self.x.set_onward(creation, lambda t: _bbox(t)[0] - buff)
            self.y.set_onward(creation, lambda t: _bbox(t)[1] - buff)
            self.width.set_onward(creation, lambda t: _bbox(t)[2] + 2*buff)
            self.height.set_onward(creation, lambda t: _bbox(t)[3] + 2*buff)


class SurroundingCircle(Circle):
    """Circle that surrounds a target object with padding.
    If follow=True (default), tracks the target as it moves."""
    def __init__(self, target, buff=SMALL_BUFF, follow=True,
                 creation=0, z=0, **styling_kwargs):
        bx, by, bw, bh = target.bbox(creation)
        r = math.hypot(bw, bh) / 2 + buff
        cx, cy = bx + bw / 2, by + bh / 2
        style_kw = {'fill_opacity': 0, 'stroke': '#FFFF00'} | styling_kwargs
        super().__init__(r=r, cx=cx, cy=cy, creation=creation, z=z, **style_kw)
        if follow:
            _cache = {}
            def _bbox(t):
                if t not in _cache:
                    _cache.clear()
                    _cache[t] = target.bbox(t)
                return _cache[t]
            self.c.set_onward(creation, lambda t: (_bbox(t)[0] + _bbox(t)[2] / 2,
                                                    _bbox(t)[1] + _bbox(t)[3] / 2))
            _r_func = lambda t: math.sqrt(_bbox(t)[2]**2 + _bbox(t)[3]**2) / 2 + buff
            self.rx.set_onward(creation, _r_func)
            self.ry.set_onward(creation, _r_func)


class BackgroundRectangle(Rectangle):
    """Semi-transparent rectangle behind a target object (useful for text backgrounds)."""
    def __init__(self, target, buff=SMALL_BUFF, creation=0, z=-1, **styling_kwargs):
        bx, by, bw, bh = target.bbox(creation)
        style_kw = {'fill': '#000', 'fill_opacity': 0.75, 'stroke_width': 0} | styling_kwargs
        super().__init__(bw + 2*buff, bh + 2*buff, x=bx - buff, y=by - buff,
                         creation=creation, z=z, **style_kw)


class Arc(VObject):
    """SVG arc segment defined by centre, radius, and start/end angles (degrees)."""
    def __init__(self, cx: float = 960, cy: float = 540, r: float = 120, start_angle: float = 0, end_angle: float = 90,
                 creation=0, z=0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        self.cx = attributes.Real(creation, cx)
        self.cy = attributes.Real(creation, cy)
        self.r = attributes.Real(creation, r)
        self.start_angle = attributes.Real(creation, start_angle)
        self.end_angle = attributes.Real(creation, end_angle)
        self.styling = style.Styling(styling_kwargs, creation=creation,
                                     stroke='#fff', stroke_width=DEFAULT_STROKE_WIDTH, fill_opacity=0)

    def _extra_attrs(self):
        return [self.cx, self.cy, self.r, self.start_angle, self.end_angle]

    def _shift_reals(self):
        return [(self.cx, self.cy)]

    def snap_points(self, time):
        return [(float(self.cx.at_time(time)), float(self.cy.at_time(time)))]

    def bbox(self, time):
        cx, cy, r = self.cx.at_time(time), self.cy.at_time(time), self.r.at_time(time)
        sa, ea = self.start_angle.at_time(time), self.end_angle.at_time(time)
        sa_rad, ea_rad = math.radians(sa), math.radians(ea)
        pts = [(cx + r * math.cos(sa_rad), cy - r * math.sin(sa_rad)),
               (cx + r * math.cos(ea_rad), cy - r * math.sin(ea_rad))]
        # Add cardinal extremes that fall within the arc sweep
        lo = sa % 360
        span = (ea - sa) % 360 or 360
        for card_deg, px, py in [(0, cx+r, cy), (90, cx, cy-r), (180, cx-r, cy), (270, cx, cy+r)]:
            if (card_deg - lo) % 360 < span:
                pts.append((px, py))
        return self._bbox_from_points(pts, time) or super().bbox(time)

    def path(self, time):
        cx, cy, r = self.cx.at_time(time), self.cy.at_time(time), self.r.at_time(time)
        sa, ea = self.start_angle.at_time(time), self.end_angle.at_time(time)
        sa_rad, ea_rad = math.radians(sa), math.radians(ea)
        x1, y1 = cx + r * math.cos(sa_rad), cy - r * math.sin(sa_rad)
        x2, y2 = cx + r * math.cos(ea_rad), cy - r * math.sin(ea_rad)
        large = 1 if abs(ea - sa) % 360 > 180 else 0
        sweep = 0 if ea > sa else 1
        return f'M{x1},{y1}A{r},{r} 0 {large},{sweep} {x2},{y2}'

    def to_svg(self, time):
        return f"<path d='{self.path(time)}'{self.styling.svg_style(time)} />"


class Wedge(Arc):
    """Arc that closes through the centre (pie/wedge shape)."""
    def __init__(self, cx: float = 960, cy: float = 540, r: float = 120, start_angle: float = 0, end_angle: float = 90,
                 creation=0, z=0, **styling_kwargs):
        super().__init__(cx=cx, cy=cy, r=r, start_angle=start_angle, end_angle=end_angle,
                         creation=creation, z=z, **({'fill_opacity': 0.7, 'stroke': '#fff', 'stroke_width': 5} | styling_kwargs))

    def path(self, time):
        return super().path(time) + f'L{self.cx.at_time(time)},{self.cy.at_time(time)}Z'


class Annulus(VObject):
    """Ring/donut shape defined by inner and outer radius."""
    def __init__(self, inner_radius=60, outer_radius=120, cx=960, cy=540,
                 creation=0, z=0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        self.c = attributes.Coor(creation, (cx, cy))
        self.inner_r = attributes.Real(creation, inner_radius)
        self.outer_r = attributes.Real(creation, outer_radius)
        self.styling = style.Styling(styling_kwargs, creation=creation,
                                     fill='#58C4DD', fill_opacity=0.7, stroke='#fff', stroke_width=DEFAULT_STROKE_WIDTH)

    def _extra_attrs(self):
        return [self.c, self.inner_r, self.outer_r]

    def _shift_coors(self):
        return [self.c]

    def snap_points(self, time):
        cx, cy = self.c.at_time(time)
        return [(float(cx), float(cy))]

    def bbox(self, time):
        cx, cy = self.c.at_time(time)
        r = self.outer_r.at_time(time)
        return self._bbox_from_points([(cx-r, cy-r), (cx+r, cy-r), (cx+r, cy+r), (cx-r, cy+r)], time) or super().bbox(time)

    def path(self, time):
        cx, cy = self.c.at_time(time)
        ri, ro = self.inner_r.at_time(time), self.outer_r.at_time(time)
        # Outer circle CW, then inner circle CCW (creates a ring with even-odd fill)
        return (f'M{cx-ro},{cy}a{ro},{ro} 0 1,0 {ro*2},0a{ro},{ro} 0 1,0 -{ro*2},0z'
                f'M{cx-ri},{cy}a{ri},{ri} 0 1,1 {ri*2},0a{ri},{ri} 0 1,1 -{ri*2},0z')

    def to_svg(self, time):
        return f"<path d='{self.path(time)}' fill-rule='evenodd'{self.styling.svg_style(time)} />"


class DashedLine(Line):
    """Line with a dashed stroke pattern."""
    def __init__(self, x1: float = 0, y1: float = 0, x2: float = 100, y2: float = 100, dash='10,5', creation=0, z=0, **styling_kwargs):
        super().__init__(x1=x1, y1=y1, x2=x2, y2=y2, creation=creation, z=z,
                         **({'stroke_dasharray': dash} | styling_kwargs))


class ScreenRectangle(Rectangle):
    """A rectangle with the canvas aspect ratio (16:9).
    height is derived from width automatically."""
    def __init__(self, width=480, creation=0, z=0, **kwargs):
        height = width * 9 / 16
        super().__init__(width=width, height=height, creation=creation, z=z, **kwargs)


class ArcBetweenPoints(Arc):
    """Arc connecting two points, bulging by a given angle.

    angle: how much the arc bulges (degrees). Positive = left of start→end.
    """
    def __init__(self, start, end, angle=60, creation=0, z=0, **styling_kwargs):
        x1, y1 = start
        x2, y2 = end
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy) or 1
        # Compute radius from chord length and angle
        half_angle = math.radians(abs(angle) / 2)
        r = dist / (2 * math.sin(half_angle)) if half_angle > 1e-9 else dist * 1000
        # Perpendicular direction (pointing left of start→end)
        px, py = -dy / dist, dx / dist
        sign = 1 if angle > 0 else -1
        sagitta = r - r * math.cos(half_angle)
        cx = mx + sign * px * (r - sagitta)
        cy = my + sign * py * (r - sagitta)
        sa = math.degrees(math.atan2(-(y1 - cy), x1 - cx))
        ea = math.degrees(math.atan2(-(y2 - cy), x2 - cx))
        if angle > 0 and (ea - sa) % 360 > 180:
            sa, ea = ea, sa
        elif angle < 0 and (sa - ea) % 360 > 180:
            sa, ea = ea, sa
        super().__init__(cx=cx, cy=cy, r=r, start_angle=sa, end_angle=ea,
                         creation=creation, z=z, **styling_kwargs)


class Elbow(Lines):
    """Right-angle connector (L-shape) between two directions.

    width/height: pixel size of each arm.
    """
    def __init__(self, cx=960, cy=540, width=40, height=40,
                 creation=0, z=0, **styling_kwargs):
        style_kw = {'stroke': '#fff', 'stroke_width': DEFAULT_STROKE_WIDTH, 'fill_opacity': 0} | styling_kwargs
        super().__init__(
            (cx + width, cy), (cx, cy), (cx, cy + height),
            creation=creation, z=z, **style_kw)


class AnnularSector(Arc):
    """Sector of an annulus (ring wedge).

    Like a Wedge but with an inner radius cut out.
    """
    def __init__(self, inner_radius=60, outer_radius=120, cx=960, cy=540,
                 start_angle=0, end_angle=90, creation=0, z=0, **styling_kwargs):
        super().__init__(cx=cx, cy=cy, r=outer_radius, start_angle=start_angle,
                         end_angle=end_angle, creation=creation, z=z,
                         **({'fill_opacity': 0.7, 'stroke': '#fff', 'stroke_width': DEFAULT_STROKE_WIDTH} | styling_kwargs))
        self.inner_r = attributes.Real(creation, inner_radius)

    def _extra_attrs(self):
        return super()._extra_attrs() + [self.inner_r]

    def path(self, time):
        cx, cy, ro = self.cx.at_time(time), self.cy.at_time(time), self.r.at_time(time)
        ri = self.inner_r.at_time(time)
        sa, ea = self.start_angle.at_time(time), self.end_angle.at_time(time)
        sa_rad, ea_rad = math.radians(sa), math.radians(ea)
        # Outer arc
        ox1, oy1 = cx + ro * math.cos(sa_rad), cy - ro * math.sin(sa_rad)
        ox2, oy2 = cx + ro * math.cos(ea_rad), cy - ro * math.sin(ea_rad)
        # Inner arc (reversed)
        ix1, iy1 = cx + ri * math.cos(ea_rad), cy - ri * math.sin(ea_rad)
        ix2, iy2 = cx + ri * math.cos(sa_rad), cy - ri * math.sin(sa_rad)
        large = 1 if abs(ea - sa) % 360 > 180 else 0
        sweep_out = 0 if ea > sa else 1
        sweep_in = 1 - sweep_out
        return (f'M{ox1},{oy1}A{ro},{ro} 0 {large},{sweep_out} {ox2},{oy2}'
                f'L{ix1},{iy1}A{ri},{ri} 0 {large},{sweep_in} {ix2},{iy2}Z')

    def to_svg(self, time):
        return f"<path d='{self.path(time)}'{self.styling.svg_style(time)} />"


class CubicBezier(VObject):
    """Cubic Bezier curve from four control points."""
    def __init__(self, p0=(860, 540), p1=(910, 440), p2=(1010, 440), p3=(1060, 540),
                 creation=0, z=0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        self.p0 = attributes.Coor(creation, p0)
        self.p1 = attributes.Coor(creation, p1)
        self.p2 = attributes.Coor(creation, p2)
        self.p3 = attributes.Coor(creation, p3)
        defaults = dict(stroke='#fff', stroke_width=DEFAULT_STROKE_WIDTH, fill_opacity=0)
        self.styling = style.Styling(styling_kwargs, creation=creation, **defaults)

    def _extra_attrs(self):
        return [self.p0, self.p1, self.p2, self.p3]

    def _shift_coors(self):
        return [self.p0, self.p1, self.p2, self.p3]

    def snap_points(self, time):
        return [self.p0.at_time(time), self.p3.at_time(time)]

    def path(self, time):
        x0, y0 = self.p0.at_time(time)
        x1, y1 = self.p1.at_time(time)
        x2, y2 = self.p2.at_time(time)
        x3, y3 = self.p3.at_time(time)
        return f'M{x0},{y0}C{x1},{y1} {x2},{y2} {x3},{y3}'

    def to_svg(self, time):
        return f"<path d='{self.path(time)}'{self.styling.svg_style(time)} />"


class Paragraph(VObject):
    """Multi-line text with alignment and line spacing.

    alignment: 'left', 'center', or 'right'.
    line_spacing: multiplier for vertical spacing between lines.
    """
    def __init__(self, *lines, x=960, y=540, font_size=36, alignment='left',
                 line_spacing=1.4, creation=0, z=0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        self.lines = list(lines)
        self.x = attributes.Real(creation, x)
        self.y = attributes.Real(creation, y)
        self.font_size = font_size
        self.alignment = alignment
        self.line_spacing = line_spacing
        defaults = dict(fill='#fff', stroke_width=0)
        self.styling = style.Styling(styling_kwargs, creation=creation, **defaults)

    def _extra_attrs(self):
        return [self.x, self.y]

    def _shift_reals(self):
        return [(self.x, self.y)]

    def snap_points(self, time):
        return [(self.x.at_time(time), self.y.at_time(time))]

    def path(self, time):
        return ''

    def bbox(self, time=0):
        x, y = self.x.at_time(time), self.y.at_time(time)
        max_chars = max((len(line) for line in self.lines), default=0)
        w = max_chars * self.font_size * 0.6
        h = len(self.lines) * self.font_size * self.line_spacing
        if self.alignment == 'center':
            return (x - w / 2, y - self.font_size, w, h)
        elif self.alignment == 'right':
            return (x - w, y - self.font_size, w, h)
        return (x, y - self.font_size, w, h)

    def to_svg(self, time):
        x, y = self.x.at_time(time), self.y.at_time(time)
        anchor = {'left': 'start', 'center': 'middle', 'right': 'end'}[self.alignment]
        parts = []
        for i, line in enumerate(self.lines):
            ly = y + i * self.font_size * self.line_spacing
            parts.append(f"<text x='{x}' y='{ly}' text-anchor='{anchor}' "
                         f"font-size='{self.font_size}'{self.styling.svg_style(time)}>{_xml_escape(line)}</text>")
        return '\n'.join(parts)


class BulletedList(VObject):
    """List of items with bullet points.

    bullet: character to use as bullet marker.
    indent: pixel indentation for each item.
    """
    def __init__(self, *items, x=200, y=200, font_size=36, bullet='\u2022',
                 indent=40, line_spacing=1.6, creation=0, z=0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        self.items = list(items)
        self.x = attributes.Real(creation, x)
        self.y = attributes.Real(creation, y)
        self.font_size = font_size
        self.bullet = bullet
        self.indent = indent
        self.line_spacing = line_spacing
        defaults = dict(fill='#fff', stroke_width=0)
        self.styling = style.Styling(styling_kwargs, creation=creation, **defaults)

    def _extra_attrs(self):
        return [self.x, self.y]

    def _shift_reals(self):
        return [(self.x, self.y)]

    def snap_points(self, time):
        return [(self.x.at_time(time), self.y.at_time(time))]

    def path(self, time):
        return ''

    def bbox(self, time=0):
        x, y = self.x.at_time(time), self.y.at_time(time)
        max_chars = max((len(item) for item in self.items), default=0)
        w = self.indent + max_chars * self.font_size * 0.6
        h = len(self.items) * self.font_size * self.line_spacing
        return (x, y - self.font_size, w, h)

    def to_svg(self, time):
        x, y = self.x.at_time(time), self.y.at_time(time)
        parts = []
        for i, item in enumerate(self.items):
            ly = y + i * self.font_size * self.line_spacing
            parts.append(f"<text x='{x}' y='{ly}' font-size='{self.font_size}'"
                         f"{self.styling.svg_style(time)}>{_xml_escape(self.bullet)}</text>")
            parts.append(f"<text x='{x + self.indent}' y='{ly}' font-size='{self.font_size}'"
                         f"{self.styling.svg_style(time)}>{_xml_escape(item)}</text>")
        return '\n'.join(parts)


class NumberedList(VObject):
    """List of items with numeric labels (1. 2. 3. ...).

    indent: pixel indentation for item text after the number.
    start_number: first number in the sequence.
    """
    def __init__(self, *items, x=200, y=200, font_size=36, indent=50,
                 line_spacing=1.6, start_number=1, creation=0, z=0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        self.items = list(items)
        self.x = attributes.Real(creation, x)
        self.y = attributes.Real(creation, y)
        self.font_size = font_size
        self.indent = indent
        self.line_spacing = line_spacing
        self.start_number = start_number
        defaults = dict(fill='#fff', stroke_width=0)
        self.styling = style.Styling(styling_kwargs, creation=creation, **defaults)

    def _extra_attrs(self):
        return [self.x, self.y]

    def _shift_reals(self):
        return [(self.x, self.y)]

    def snap_points(self, time):
        return [(self.x.at_time(time), self.y.at_time(time))]

    def path(self, time):
        return ''

    def bbox(self, time=0):
        x, y = self.x.at_time(time), self.y.at_time(time)
        max_chars = max((len(item) for item in self.items), default=0)
        w = self.indent + max_chars * self.font_size * 0.6
        h = len(self.items) * self.font_size * self.line_spacing
        return (x, y - self.font_size, w, h)

    def to_svg(self, time):
        x, y = self.x.at_time(time), self.y.at_time(time)
        parts = []
        for i, item in enumerate(self.items):
            ly = y + i * self.font_size * self.line_spacing
            num = f'{self.start_number + i}.'
            parts.append(f"<text x='{x}' y='{ly}' font-size='{self.font_size}'"
                         f"{self.styling.svg_style(time)}>{num}</text>")
            parts.append(f"<text x='{x + self.indent}' y='{ly}' font-size='{self.font_size}'"
                         f"{self.styling.svg_style(time)}>{_xml_escape(item)}</text>")
        return '\n'.join(parts)


class FunctionGraph(Lines):
    """Plot a mathematical function as a polyline (no axes, ticks, or labels).

    x_range: (start, end) in math coordinates.
    y_range: (min, max) or None for auto.
    x, y, width, height: SVG pixel area for the plot.
    """
    def __init__(self, func, x_range=(-5, 5), y_range=None, num_points=200,
                 x=120, y=60, width=1440, height=840,
                 creation=0, z=0, **styling_kwargs):
        x_min, x_max = x_range
        _, _, _, clamped = _sample_function(
            func, x_min, x_max, y_range, num_points, x, y, width, height)
        style_kw = {'stroke': '#58C4DD', 'stroke_width': 5, 'fill_opacity': 0} | styling_kwargs
        super().__init__(*clamped, creation=creation, z=z, **style_kw)
