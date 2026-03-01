"""UI component classes: TextBox, Badge, Checklist, Code, etc."""
import math
import re

import vectormation.easings as easings
import vectormation.style as style
from vectormation._constants import (
    ORIGIN, DEFAULT_OBJECT_TO_EDGE_BUFF, DEFAULT_CHART_COLORS,
    CHAR_WIDTH_FACTOR, TEXT_Y_OFFSET, _normalize, _label_text, _get_arrow,
)
from vectormation._base import VObject, VCollection, _norm_dir, _ramp
from vectormation._collection import _stagger_timing
from vectormation._shapes import (
    Polygon, Circle, Dot, Rectangle, RoundedRectangle, Line, Lines,
    Text, DecimalNumber,
)

_TEXT_STYLE = {'fill': '#fff', 'stroke_width': 0}
_LINE_STYLE = {'stroke': '#fff', 'stroke_width': 3}
_Text = Text  # module-level alias; avoids shadowing in methods that accept 'text' param
_Line = Line  # module-level alias; avoids shadowing in methods that accept 'line' param

# ---------------------------------------------------------------------------
# Title / Variable / Underline
# ---------------------------------------------------------------------------

class Title(VCollection):
    """Centered title text at the top of the canvas.
    Accepts the same keyword args as Text (font_size, fill, etc.)."""
    def __init__(self, text, creation: float = 0, z: float = 0, **kwargs):
        defaults = {'font_size': 60, 'text_anchor': 'middle', 'fill': '#fff',
                    'stroke_width': 0} | kwargs
        txt = Text(text, x=ORIGIN[0], y=DEFAULT_OBJECT_TO_EDGE_BUFF + 60,
                   creation=creation, z=z, **defaults)
        underline = Line(x1=ORIGIN[0] - 200, y1=DEFAULT_OBJECT_TO_EDGE_BUFF + 80,
                         x2=ORIGIN[0] + 200, y2=DEFAULT_OBJECT_TO_EDGE_BUFF + 80,
                         stroke='#888', stroke_width=2, creation=creation, z=z)
        super().__init__(txt, underline, creation=creation, z=z)

    def __repr__(self):
        return 'Title()'

class Variable(VCollection):
    """Display a variable label with an animated numeric value."""
    def __init__(self, label='x', value: float = 0, fmt='{:.2f}', x=ORIGIN[0], y=ORIGIN[1],
                 font_size=48, creation: float = 0, z: float = 0, **styling_kwargs):
        style_kw = _TEXT_STYLE | styling_kwargs
        label_text = f'{label} = '
        self.label = Text(label_text, x=x, y=y, font_size=font_size,
                          text_anchor='end', creation=creation, z=z, **style_kw)
        self.number = DecimalNumber(value, fmt=fmt, x=x, y=y,
                                    font_size=font_size, creation=creation, z=z, **style_kw)
        super().__init__(self.label, self.number, creation=creation, z=z)

    @property
    def tracker(self):
        return self.number.tracker

    def set_value(self, val, start: float = 0):
        self.number.set_value(val, start)
        return self

    def animate_value(self, target, start: float, end: float, easing=easings.smooth):
        self.number.animate_value(target, start, end, easing)
        return self

    def __repr__(self):
        return 'Variable()'

class Underline(VCollection):
    """Underline beneath a target object."""
    def __init__(self, target, buff=4, follow=True, creation: float = 0, z: float = 0, **styling_kwargs):
        style_kw = _LINE_STYLE | styling_kwargs
        bx, by, bw, bh = target.bbox(creation)
        line = Line(x1=bx, y1=by + bh + buff, x2=bx + bw, y2=by + bh + buff,
                    creation=creation, z=z, **style_kw)
        if follow:
            _cache = [None, None]
            def _bbox(t):
                if _cache[0] != t:
                    _cache[0] = t
                    _cache[1] = target.bbox(t)
                return _cache[1]
            line.p1.set_onward(creation, lambda t: ((b := _bbox(t))[0], b[1] + b[3] + buff))
            line.p2.set_onward(creation, lambda t: ((b := _bbox(t))[0] + b[2], b[1] + b[3] + buff))
        super().__init__(line, creation=creation, z=z)
        self.line = line

    def __repr__(self):
        return 'Underline()'

# ---------------------------------------------------------------------------
# Code
# ---------------------------------------------------------------------------

class Code(VCollection):
    """Syntax-highlighted code display."""
    _KEYWORD_COLORS = {
        'python': {'def', 'class', 'return', 'if', 'else', 'elif', 'for', 'while',
                   'import', 'from', 'in', 'not', 'and', 'or', 'with', 'as', 'try',
                   'except', 'finally', 'raise', 'yield', 'lambda', 'pass', 'break',
                   'continue', 'True', 'False', 'None', 'is', 'async', 'await'},
        'javascript': {'function', 'const', 'let', 'var', 'return', 'if', 'else',
                       'for', 'while', 'class', 'import', 'export', 'from', 'new',
                       'this', 'async', 'await', 'try', 'catch', 'throw', 'true',
                       'false', 'null', 'undefined', 'typeof', 'instanceof'},
        'c': {'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break',
              'continue', 'return', 'struct', 'typedef', 'enum', 'union',
              'void', 'int', 'char', 'float', 'double', 'long', 'short',
              'unsigned', 'signed', 'const', 'static', 'extern', 'sizeof',
              'NULL', 'include', 'define', 'ifdef', 'endif'},
        'java': {'class', 'public', 'private', 'protected', 'static', 'final',
                 'abstract', 'interface', 'extends', 'implements', 'new',
                 'return', 'if', 'else', 'for', 'while', 'do', 'switch',
                 'case', 'break', 'continue', 'try', 'catch', 'finally',
                 'throw', 'throws', 'import', 'package', 'void', 'int',
                 'boolean', 'String', 'true', 'false', 'null', 'this', 'super'},
        'rust': {'fn', 'let', 'mut', 'if', 'else', 'for', 'while', 'loop',
                 'match', 'return', 'struct', 'enum', 'impl', 'trait', 'pub',
                 'use', 'mod', 'crate', 'self', 'super', 'where', 'async',
                 'await', 'move', 'ref', 'type', 'const', 'static', 'unsafe',
                 'true', 'false', 'None', 'Some', 'Ok', 'Err'},
        'go': {'func', 'var', 'const', 'type', 'struct', 'interface', 'map',
               'chan', 'if', 'else', 'for', 'range', 'switch', 'case',
               'default', 'break', 'continue', 'return', 'go', 'select',
               'defer', 'package', 'import', 'true', 'false', 'nil',
               'make', 'append', 'len', 'cap'},
    }

    def __init__(self, text, language='python', x=120, y=120, font_size=24,
                 line_height=1.5, tab_width=4, creation: float = 0, z: float = 0, **styling_kwargs):
        lines = text.strip('\n').split('\n')
        objects = []
        keywords = self._KEYWORD_COLORS.get(language, set())
        bg_width = max(len(line) for line in lines) * font_size * CHAR_WIDTH_FACTOR + 40 if lines else 200
        bg_height = len(lines) * font_size * line_height + 20

        bg_style = {'fill': '#1e1e2e', 'fill_opacity': 0.95, 'stroke': '#444', 'stroke_width': 1} | styling_kwargs
        bg = RoundedRectangle(bg_width, bg_height, x=x - 10, y=y - font_size - 5,
                              corner_radius=8, creation=creation, z=z, **bg_style)
        objects.append(bg)

        line_groups = []  # list of lists, one per source line
        for i, line in enumerate(lines):
            ly = y + i * font_size * line_height
            line_objs = []
            # Line number
            ln = Text(text=f'{i+1:>3}', x=x, y=ly, font_size=font_size,
                      creation=creation, z=z, fill='#666', stroke_width=0)
            objects.append(ln)
            line_objs.append(ln)
            # Code content with basic keyword highlighting
            code_x = x + font_size * 2.5
            expanded = line.replace('\t', ' ' * tab_width)
            words = re.split(r'(\s+)', expanded)
            wx = code_x
            for word in words:
                if not word:
                    continue
                if word.isspace():
                    wx += len(word) * font_size * CHAR_WIDTH_FACTOR
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
                line_objs.append(t)
                wx += len(word) * font_size * CHAR_WIDTH_FACTOR
            line_groups.append(line_objs)
        super().__init__(*objects, creation=creation, z=z)
        self._code_x = x
        self._code_y = y
        self._font_size = font_size
        self._line_height = line_height
        self._bg_width = bg_width
        self._num_lines = len(lines)
        self._language = language
        self._line_groups = line_groups

    def __repr__(self):
        return f'Code({self._num_lines} lines, lang={self._language!r})'

    def highlight_lines(self, line_nums, start: float = 0, end: float = 1, color='#FFFF00', opacity=0.2,
                        easing=easings.there_and_back):
        """Highlight specific code lines with a colored overlay."""
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
                    _ramp(start, dur, opacity, easing), stay=True)
            rects.append(rect)
        return VCollection(*rects) if rects else VCollection()

    def reveal_lines(self, start: float = 0, end: float = 1, overlap=0.5):
        """Reveal code lines sequentially with staggered fadein."""
        n = self._num_lines
        dur = end - start
        if n == 0 or dur <= 0:
            return self
        line_dur, step = _stagger_timing(n, dur, overlap)
        for i, group in enumerate(self._line_groups):
            t0 = start + i * step
            for obj in group:
                obj.fadein(start=t0, end=t0 + line_dur)
        return self

# ---------------------------------------------------------------------------
# Label / LabeledArrow
# ---------------------------------------------------------------------------

def _text_with_box(text, x, y, font_size, padding, corner_radius, creation, z_txt, z_bg,
                   box_fill='#1e1e2e', box_opacity=0.9, box_stroke='#555', **text_kw):
    """Create a centered Text + RoundedRectangle background pair."""
    txt = Text(text=text, x=x, y=y, font_size=font_size,
               text_anchor='middle', creation=creation, z=z_txt, **text_kw)
    _, _, tw, th = txt.bbox(creation)
    bg = RoundedRectangle(tw + 2 * padding, th + 2 * padding,
                          x=x - tw / 2 - padding, y=y - th - padding + 4,
                          corner_radius=corner_radius, creation=creation, z=z_bg,
                          fill=box_fill, fill_opacity=box_opacity, stroke=box_stroke, stroke_width=1)
    return bg, txt

class Label(VCollection):
    """Text label with a surrounding box/frame for annotations."""
    def __init__(self, text, x=ORIGIN[0], y=ORIGIN[1], font_size=36, padding=10,
                 corner_radius=4, creation: float = 0, z: float = 0, **styling_kwargs):
        style_kw = _TEXT_STYLE | styling_kwargs
        bg, txt = _text_with_box(text, x, y, font_size, padding, corner_radius,
                                 creation, z + 1, z, **style_kw)
        super().__init__(bg, txt, creation=creation, z=z)

    def __repr__(self):
        return 'Label()'

def _labeled_line_init(self, line_obj, x1, y1, x2, y2, label, font_size, label_buff, creation, z):
    """Shared init for LabeledLine and LabeledArrow."""
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    dx, dy = x2 - x1, y2 - y1
    ux, uy = _normalize(dx, dy)
    nx, ny = -uy * label_buff, ux * label_buff
    lbl = _label_text(label, mx + nx, my + ny, font_size, creation=creation, z=z + 1)
    VCollection.__init__(self, line_obj, lbl, creation=creation, z=z)
    self.line = line_obj
    self.label_obj = lbl

class LabeledLine(VCollection):
    """Line with a text label placed at its midpoint."""
    def __init__(self, x1=860, y1=ORIGIN[1], x2=1060, y2=ORIGIN[1], label='',
                 font_size=24, label_buff=10, creation: float = 0, z: float = 0, **styling_kwargs):
        style_kw = _LINE_STYLE | styling_kwargs
        line = Line(x1=x1, y1=y1, x2=x2, y2=y2, creation=creation, z=z, **style_kw)
        _labeled_line_init(self, line, x1, y1, x2, y2, label, font_size, label_buff, creation, z)

    def __repr__(self):
        return 'LabeledLine()'

class LabeledArrow(VCollection):
    """Arrow with a text label placed at its midpoint."""
    def __init__(self, x1=860, y1=ORIGIN[1], x2=1060, y2=ORIGIN[1], label='',
                 font_size=24, label_buff=10, creation: float = 0, z: float = 0, **styling_kwargs):
        Arrow = _get_arrow()
        style_kw = _LINE_STYLE | styling_kwargs
        arrow = Arrow(x1=x1, y1=y1, x2=x2, y2=y2, creation=creation, z=z, **style_kw)
        _labeled_line_init(self, arrow, x1, y1, x2, y2, label, font_size, label_buff, creation, z)
        self.arrow = arrow  # backward compat alias

    def __repr__(self):
        return 'LabeledArrow()'

# ---------------------------------------------------------------------------
# Callout / DimensionLine / Tooltip
# ---------------------------------------------------------------------------

class Callout(VCollection):
    """Text callout with a pointer line to a target position."""
    def __init__(self, text, target, direction='up', distance=80, font_size=24,
                 padding=8, corner_radius=4, creation: float = 0, z: float = 0, **styling_kwargs):
        direction = _norm_dir(direction, 'up')

        # Resolve target position
        if hasattr(target, 'center'):
            tx, ty = target.center(creation)
        else:
            tx, ty = target

        # Position the label box
        offsets = {'up': (0, -distance), 'down': (0, distance),
                   'left': (-distance, 0), 'right': (distance, 0)}
        ox, oy = offsets.get(direction, (0, -distance))
        lx, ly = tx + ox, ty + oy

        style_kw = _TEXT_STYLE | styling_kwargs
        bg, lbl = _text_with_box(text, lx, ly, font_size, padding, corner_radius,
                                 creation, z + 2, z + 1, **style_kw)
        _, _, _, th = lbl.bbox(creation)
        pointer = _Line(x1=tx, y1=ty, x2=lx, y2=ly + th / 2 if direction == 'up' else ly - th / 2 if direction == 'down' else ly,
                        creation=creation, z=z, stroke='#888', stroke_width=1)
        super().__init__(pointer, bg, lbl, creation=creation, z=z)

    def __repr__(self):
        return 'Callout()'

class DimensionLine(VCollection):
    """Technical dimension line between two points with measurement label."""
    def __init__(self, p1, p2, label=None, offset=30, font_size=20,
                 tick_size=10, creation: float = 0, z: float = 0, **styling_kwargs):
        x1, y1 = p1
        x2, y2 = p2
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy) or 1
        ux, uy = _normalize(dx, dy)
        # Perpendicular unit vector
        nx, ny = -uy * offset, ux * offset
        # Offset endpoints
        ox1, oy1 = x1 + nx, y1 + ny
        ox2, oy2 = x2 + nx, y2 + ny

        style_kw = {'stroke': '#aaa', 'stroke_width': 1} | styling_kwargs

        # Main dimension line
        main = _Line(x1=ox1, y1=oy1, x2=ox2, y2=oy2, creation=creation, z=z, **style_kw)
        # Extension lines (ticks from original points to dimension line)
        ext1 = _Line(x1=x1, y1=y1, x2=ox1 + nx * 0.3, y2=oy1 + ny * 0.3,
                     creation=creation, z=z, **style_kw)
        ext2 = _Line(x1=x2, y1=y2, x2=ox2 + nx * 0.3, y2=oy2 + ny * 0.3,
                     creation=creation, z=z, **style_kw)
        # Tick marks at ends of dimension line
        tnx, tny = -uy * tick_size / 2, ux * tick_size / 2
        tick1 = _Line(x1=ox1 - tnx, y1=oy1 - tny, x2=ox1 + tnx, y2=oy1 + tny,
                      creation=creation, z=z, **style_kw)
        tick2 = _Line(x1=ox2 - tnx, y1=oy2 - tny, x2=ox2 + tnx, y2=oy2 + tny,
                      creation=creation, z=z, **style_kw)

        # Label
        if label is None:
            label = f'{length:.0f}'
        mx, my = (ox1 + ox2) / 2, (oy1 + oy2) / 2
        lbl = _Text(text=str(label), x=mx + nx * 0.5, y=my + ny * 0.5,
                    font_size=font_size, text_anchor='middle',
                    creation=creation, z=z + 1, fill='#aaa', stroke_width=0)
        super().__init__(main, ext1, ext2, tick1, tick2, lbl, creation=creation, z=z)

    def __repr__(self):
        return 'DimensionLine()'

class Tooltip(VCollection):
    """Small animated tooltip that appears and disappears near a target."""
    def __init__(self, text, target, start=0, duration=1.5, font_size=18,
                 padding=6, creation: float = 0, z=10, **styling_kwargs):
        if hasattr(target, 'bbox'):
            tx = target.center(creation)[0]
            ty = target.bbox(creation)[1]
        else:
            tx, ty = target

        style_kw = _TEXT_STYLE | styling_kwargs
        bg, lbl = _text_with_box(text, tx, ty - 20, font_size, padding, 4,
                                 creation, z + 1, z,
                                 box_fill='#333', box_stroke='#666', **style_kw)
        super().__init__(bg, lbl, creation=creation, z=z)
        # Auto-animate: fade in, hold, fade out
        if duration <= 0:
            duration = 0.1
        fade_time = min(0.3, duration / 3)
        self.fadein(start, start + fade_time)
        self.fadeout(start + duration - fade_time, start + duration)

    def __repr__(self):
        return 'Tooltip()'

# ---------------------------------------------------------------------------
# TextBox / Bracket / IconGrid / SpeechBubble / Badge / Divider
# ---------------------------------------------------------------------------

class TextBox(VCollection):
    """Text with a surrounding rectangle. Useful for labels and callouts."""
    def __init__(self, text, x=100, y=100, font_size=20, padding=12,
                 width=None, height=None, corner_radius=6,
                 box_fill='#333', box_opacity=0.9, text_color='#fff',
                 creation: float = 0, z: float = 0, **styling_kwargs):
        char_w = font_size * CHAR_WIDTH_FACTOR
        if width is None:
            width = len(text) * char_w + padding * 2
        if height is None:
            height = font_size + padding * 2

        box = RoundedRectangle(width=width, height=height, x=x, y=y,
                                corner_radius=corner_radius,
                                fill=box_fill, fill_opacity=box_opacity,
                                stroke_width=0, creation=creation, z=z,
                                **styling_kwargs)
        lbl = Text(text=text, x=x + width / 2, y=y + height / 2 + font_size * TEXT_Y_OFFSET,
                   font_size=font_size, fill=text_color, stroke_width=0,
                   text_anchor='middle', creation=creation, z=z + 0.1)
        super().__init__(box, lbl, creation=creation, z=z)
        self.box = box
        self.label = lbl

    def __repr__(self):
        return 'TextBox()'

class Bracket(VCollection):
    """Square bracket decoration pointing at a range."""
    def __init__(self, x=100, y=100, width=100, height=20,
                 direction='down', stroke='#fff', stroke_width=2,
                 text='', font_size=16, text_color='#aaa',
                 creation: float = 0, z: float = 0):
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
            lbl = Text(text=text, x=tx, y=ty + font_size * TEXT_Y_OFFSET,
                       font_size=font_size, fill=text_color, stroke_width=0,
                       text_anchor='middle', creation=creation, z=z + 0.1)
            objects.append(lbl)
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return 'Bracket()'

class IconGrid(VCollection):
    """Grid of colored shapes (circles, squares) for infographic-style visualizations."""
    def __init__(self, data, x=100, y=100, cols=10, size=15, gap=3,
                 shape='circle', creation: float = 0, z: float = 0):
        objects = []
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

    def __repr__(self):
        return 'IconGrid()'

class SpeechBubble(VCollection):
    """Rounded rectangle with a triangular tail, useful for dialogue/annotations."""
    def __init__(self, text='', x=100, y=100, font_size=20, padding=14,
                 width=None, height=None, corner_radius=10,
                 box_fill='#1e1e2e', box_opacity=0.95, text_color='#fff',
                 tail_direction='down', tail_width=20, tail_height=18,
                 creation: float = 0, z: float = 0, **styling_kwargs):

        char_w = font_size * CHAR_WIDTH_FACTOR
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
        lbl = _Text(text=text, x=cx, y=cy + font_size * TEXT_Y_OFFSET,
                    font_size=font_size, fill=text_color, stroke_width=0,
                    text_anchor='middle', creation=creation, z=z + 0.1)
        super().__init__(tail, box, lbl, creation=creation, z=z)
        self.box = box
        self.tail = tail
        self.label = lbl

    def __repr__(self):
        return 'SpeechBubble()'

class Badge(VCollection):
    """Pill-shaped label (fully rounded corners), like GitHub badges/tags."""
    def __init__(self, text='Label', x=100, y=100, font_size=16, padding_x=14,
                 padding_y=6, bg_color='#58C4DD', text_color='#000',
                 creation: float = 0, z: float = 0, **styling_kwargs):

        char_w = font_size * CHAR_WIDTH_FACTOR
        width = len(text) * char_w + padding_x * 2
        height = font_size + padding_y * 2
        corner_radius = height / 2  # fully rounded = pill shape
        box = RoundedRectangle(width=width, height=height, x=x, y=y,
                               corner_radius=corner_radius,
                               fill=bg_color, fill_opacity=1,
                               stroke_width=0, creation=creation, z=z,
                               **styling_kwargs)
        lbl = _Text(text=text, x=x + width / 2, y=y + height / 2 + font_size * TEXT_Y_OFFSET,
                    font_size=font_size, fill=text_color, stroke_width=0,
                    text_anchor='middle', creation=creation, z=z + 0.1)
        super().__init__(box, lbl, creation=creation, z=z)
        self.box = box
        self.label = lbl

    def __repr__(self):
        return 'Badge()'

class Divider(VCollection):
    """Horizontal or vertical line with an optional centered text label."""
    def __init__(self, x=100, y=300, length=400, direction='horizontal',
                 label=None, font_size=16, gap=12,
                 creation: float = 0, z: float = 0, **styling_kwargs):
        style_kw = {'stroke': '#555', 'stroke_width': 1} | styling_kwargs
        objects = []
        if label:
            char_w = font_size * CHAR_WIDTH_FACTOR
            label_w = len(label) * char_w + gap * 2
            half = (length - label_w) / 2
            if direction == 'horizontal':
                l1 = _Line(x1=x, y1=y, x2=x + half, y2=y,
                           creation=creation, z=z, **style_kw)
                l2 = _Line(x1=x + half + label_w, y1=y, x2=x + length, y2=y,
                           creation=creation, z=z, **style_kw)
                lbl = _Text(text=label, x=x + length / 2, y=y + font_size * TEXT_Y_OFFSET,
                            font_size=font_size, fill=style_kw.get('stroke', '#555'),
                            stroke_width=0, text_anchor='middle',
                            creation=creation, z=z + 0.1)
            else:
                l1 = _Line(x1=x, y1=y, x2=x, y2=y + half,
                           creation=creation, z=z, **style_kw)
                l2 = _Line(x1=x, y1=y + half + label_w, x2=x, y2=y + length,
                           creation=creation, z=z, **style_kw)
                lbl = _Text(text=label, x=x, y=y + length / 2 + font_size * TEXT_Y_OFFSET,
                            font_size=font_size, fill=style_kw.get('stroke', '#555'),
                            stroke_width=0, text_anchor='middle',
                            creation=creation, z=z + 0.1)
            objects = [l1, l2, lbl]
        else:
            if direction == 'horizontal':
                ln = _Line(x1=x, y1=y, x2=x + length, y2=y,
                           creation=creation, z=z, **style_kw)
            else:
                ln = _Line(x1=x, y1=y, x2=x, y2=y + length,
                           creation=creation, z=z, **style_kw)
            objects = [ln]
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return 'Divider()'

# ---------------------------------------------------------------------------
# Checklist / Stepper / TagCloud / StatusIndicator / Meter / Breadcrumb
# ---------------------------------------------------------------------------

class Checklist(VCollection):
    """List of items with checkbox indicators (checked or unchecked)."""
    def __init__(self, *items, x=100, y=100, font_size=24, spacing=1.6,
                 box_size=None, check_color='#83C167', uncheck_color='#555',
                 text_color='#fff', creation: float = 0, z: float = 0):

        if box_size is None:
            box_size = font_size * 0.75
        objects = []
        self._boxes = []
        self._marks = []
        self._labels = []
        self._check_color = check_color
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
            mark = _Text(text='\u2713' if checked else '',
                         x=x + box_size / 2, y=ly + box_size * 0.8,
                         font_size=font_size * 0.7, fill='#fff', stroke_width=0,
                         text_anchor='middle', creation=creation, z=z + 0.1)
            lbl = _Text(text=label_text, x=x + box_size + 10,
                        y=ly + box_size * 0.75,
                        font_size=font_size, fill=text_color, stroke_width=0,
                        creation=creation, z=z)
            objects.extend([box, mark, lbl])
            self._boxes.append(box)
            self._marks.append(mark)
            self._labels.append(lbl)
        super().__init__(*objects, creation=creation, z=z)

    def check_item(self, index, start: float = 0, end: float = 0.3):
        """Animate checking the item at index (shows the check mark)."""
        if 0 <= index < len(self._marks):
            self._marks[index].text.set_onward(start, '\u2713')
            self._marks[index].fadein(start, end)
            self._boxes[index].set_fill(self._check_color, start=start, end=end)
        return self

    def reveal_items(self, start: float = 0, end: float = 1, overlap=0.5):
        """Cascade items into view sequentially."""
        n = len(self._boxes)
        if n == 0:
            return self
        dur = end - start
        step = dur / n
        for i in range(n):
            obj_start = start + i * step * (1 - overlap)
            obj_end = obj_start + step
            for obj in (self._boxes[i], self._marks[i], self._labels[i]):
                obj.fadein(obj_start, min(obj_end, end))
        return self

    def __repr__(self):
        return 'Checklist()'

class Stepper(VCollection):
    """Step indicator: numbered circles connected by a line, with active step highlight."""
    def __init__(self, steps, x=100, y=300, spacing=150, radius=20,
                 active=0, direction='horizontal', font_size=16,
                 active_color='#58C4DD', inactive_color='#555',
                 text_color='#fff', creation: float = 0, z: float = 0):
        if isinstance(steps, int):
            steps = [str(i + 1) for i in range(steps)]
        objects = []
        self._circles = []
        self._lines = []
        self._active_color = active_color
        self._inactive_color = inactive_color
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
            lbl = Text(text=label, x=cx, y=cy + font_size * TEXT_Y_OFFSET,
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
                self._lines.append(conn)
        super().__init__(*objects, creation=creation, z=z)

    def advance(self, from_step, to_step, start: float = 0, end: float = 0.5):
        """Animate transitioning active step highlight from from_step to to_step."""
        # Dim old step circle
        if 0 <= from_step < len(self._circles):
            self._circles[from_step].set_fill(self._inactive_color, start=start, end=end)
        # Highlight new step circle
        if 0 <= to_step < len(self._circles):
            self._circles[to_step].set_fill(self._active_color, start=start, end=end)
        # Update connecting lines between steps
        for i, line in enumerate(self._lines):
            if i < to_step:
                line.set_stroke(self._active_color, start=start, end=end)
            else:
                line.set_stroke(self._inactive_color, start=start, end=end)
        return self

    def __repr__(self):
        return 'Stepper()'

class TagCloud(VCollection):
    """Word/tag cloud with varying font sizes based on weights."""
    def __init__(self, data, x=100, y=100, width=500, min_font=14, max_font=48,
                 colors=None, creation: float = 0, z: float = 0):
        if colors is None:
            colors = list(DEFAULT_CHART_COLORS)
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
            char_w = fs * CHAR_WIDTH_FACTOR
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

    def __repr__(self):
        return 'TagCloud()'

class StatusIndicator(VCollection):
    """Colored dot with a text label, like a server/service status indicator."""
    _STATUS_COLORS = {
        'online': '#83C167', 'ok': '#83C167', 'success': '#83C167',
        'offline': '#FF6B6B', 'error': '#FF6B6B', 'fail': '#FF6B6B',
        'warning': '#FFFF00', 'warn': '#FFFF00',
        'pending': '#888', 'unknown': '#888',
    }

    def __init__(self, label, status='online', x=100, y=100, font_size=18,
                 dot_radius=6, gap=10, creation: float = 0, z: float = 0):
        color = self._STATUS_COLORS.get(status, status)
        dot = Dot(cx=x + dot_radius, cy=y, r=dot_radius,
                  fill=color, stroke_width=0, creation=creation, z=z)
        lbl = Text(text=label, x=x + dot_radius * 2 + gap, y=y + font_size * TEXT_Y_OFFSET,
                   font_size=font_size, fill='#fff', stroke_width=0,
                   creation=creation, z=z)
        super().__init__(dot, lbl, creation=creation, z=z)
        self.dot = dot
        self.label = lbl

    def __repr__(self):
        return 'StatusIndicator()'

class Meter(VCollection):
    """Vertical or horizontal bar meter (like a battery level or VU meter)."""
    def __init__(self, value=0.5, x=100, y=100, width=30, height=150,
                 direction='vertical', fill_color='#58C4DD',
                 bg_color='#333', border_color='#888',
                 creation: float = 0, z: float = 0):

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

    def __repr__(self):
        return 'Meter()'

class Breadcrumb(VCollection):
    """Navigation breadcrumb trail (e.g., Home > Products > Details)."""
    def __init__(self, *items, x=100, y=100, font_size=18, separator='\u203a',
                 gap=8, active_index=None, active_color='#58C4DD',
                 inactive_color='#888', creation: float = 0, z: float = 0):
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
            cx += len(item) * font_size * CHAR_WIDTH_FACTOR + gap
            if i < len(items) - 1:
                sep = Text(text=separator, x=cx, y=y,
                           font_size=font_size, fill=inactive_color, stroke_width=0,
                           creation=creation, z=z)
                objects.append(sep)
                cx += font_size * CHAR_WIDTH_FACTOR + gap
        super().__init__(*objects, creation=creation, z=z)

    def __repr__(self):
        return 'Breadcrumb()'

# ---------------------------------------------------------------------------
# Countdown / Filmstrip
# ---------------------------------------------------------------------------

class Countdown(VCollection):
    """Animated countdown timer from start_value to end_value."""
    def __init__(self, start_value=10, end_value=0, x=ORIGIN[0], y=ORIGIN[1], font_size=120,
                 start=0, end=3, creation: float = 0, z: float = 0, **styling_kwargs):
        txt = _label_text(start_value, x, y, font_size, creation=creation, z=z, **styling_kwargs)
        _sv, _ev, _s, _e = start_value, end_value, start, end
        dur = _e - _s
        if dur > 0:
            txt.text.set(_s, _e, lambda t: str(int(_sv + (_ev - _sv) * min(1, (t - _s) / dur))),
                         stay=True)
        super().__init__(txt, creation=creation, z=z)
        self._text = txt

    def __repr__(self):
        return 'Countdown()'

class Filmstrip(VCollection):
    """Horizontal row of labeled thumbnail boxes (like a storyboard/filmstrip)."""
    def __init__(self, labels, x=100, y=400, frame_width=200, frame_height=130,
                 spacing=20, font_size=16, creation: float = 0, z: float = 0, **styling_kwargs):

        objects = []
        self._frames = []
        frame_style = {'fill': '#1e1e2e', 'fill_opacity': 0.9,
                        'stroke': '#555', 'stroke_width': 1} | styling_kwargs
        for i, label in enumerate(labels):
            fx = x + i * (frame_width + spacing)
            frame = RoundedRectangle(frame_width, frame_height, x=fx, y=y,
                                     corner_radius=6, creation=creation, z=z, **frame_style)
            lbl = _label_text(label, fx + frame_width / 2, y + frame_height + 5,
                              font_size, creation=creation, z=z + 0.1, fill='#ccc')
            num = _label_text(str(i + 1), fx + frame_width / 2, y + frame_height / 2,
                              font_size * 2, creation=creation, z=z + 0.1, fill='#333')
            self._frames.append(frame)
            objects.extend([frame, lbl, num])
        super().__init__(*objects, creation=creation, z=z)

    def highlight_frame(self, index, start: float = 0, end: float = 1, color='#58C4DD',
                        easing=easings.there_and_back):
        """Flash-highlight a frame by index."""
        if 0 <= index < len(self._frames):
            self._frames[index].flash(start, end, color=color, easing=easing)
        return self

    def __repr__(self):
        return 'Filmstrip()'

# ---------------------------------------------------------------------------
# RoundedCornerPolygon
# ---------------------------------------------------------------------------

class RoundedCornerPolygon(VObject):
    """Polygon with rounded (filleted) corners."""
    def __init__(self, *vertices, radius=20, creation: float = 0, z: float = 0, **styling_kwargs):
        super().__init__(creation=creation, z=z)
        self._vertices = list(vertices)
        self._radius = radius
        defaults = {'fill': '#58C4DD', 'fill_opacity': 0.5,
                    'stroke': '#fff', 'stroke_width': 2}
        self.styling = style.Styling(styling_kwargs, creation=creation, **defaults)

    def _extra_attrs(self):
        return [self.styling]

    def _compute_path(self):
        pts = self._vertices
        n = len(pts)
        if n < 3:
            return ''
        r = self._radius
        segs = []
        for i in range(n):
            p_prev = pts[(i - 1) % n]
            p_curr = pts[i]
            p_next = pts[(i + 1) % n]
            # Vectors from current to previous and next
            dx1, dy1 = p_prev[0] - p_curr[0], p_prev[1] - p_curr[1]
            dx2, dy2 = p_next[0] - p_curr[0], p_next[1] - p_curr[1]
            d1 = math.hypot(dx1, dy1) or 1
            d2 = math.hypot(dx2, dy2) or 1
            # Limit radius to half the shorter edge
            max_r = min(d1, d2) / 2
            cr = min(r, max_r)
            # Points on edges where the arc starts/ends
            sx = p_curr[0] + dx1 / d1 * cr
            sy = p_curr[1] + dy1 / d1 * cr
            ex = p_curr[0] + dx2 / d2 * cr
            ey = p_curr[1] + dy2 / d2 * cr
            # Determine sweep direction
            cross = dx1 * dy2 - dy1 * dx2
            sweep = 0 if cross > 0 else 1
            if i == 0:
                segs.append(f'M{sx:.1f} {sy:.1f}')
            else:
                segs.append(f'L{sx:.1f} {sy:.1f}')
            segs.append(f'A{cr:.1f} {cr:.1f} 0 0 {sweep} {ex:.1f} {ey:.1f}')
        segs.append('Z')
        return ''.join(segs)

    def path(self, time=0):
        return self._compute_path()

    def to_svg(self, time):
        self._run_updaters(time)
        d = self._compute_path()
        if not d:
            return ''
        return f'<path d="{d}"{self.styling.svg_style(time)} />'

    def __repr__(self):
        return 'RoundedCornerPolygon()'
