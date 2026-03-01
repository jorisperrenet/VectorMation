"""
NOTE: The color names to hex are copied from the color sheets from manim

MIT License

Copyright (c) 2018 3Blue1Brown LLC
Copyright (c) 2021, the Manim Community Developers

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

colors = {
    'WHITE': '#FFFFFF',
    'GRAY_A': '#DDDDDD',
    'GREY_A': '#DDDDDD',
    'GRAY_B': '#BBBBBB',
    'GREY_B': '#BBBBBB',
    'GRAY_C': '#888888',
    'GREY_C': '#888888',
    'GRAY_D': '#444444',
    'GREY_D': '#444444',
    'GRAY_E': '#222222',
    'GREY_E': '#222222',
    'BLACK': '#000000',
    'LIGHTER_GRAY': '#DDDDDD',
    'LIGHTER_GREY': '#DDDDDD',
    'LIGHT_GRAY': '#BBBBBB',
    'LIGHT_GREY': '#BBBBBB',
    'GRAY': '#888888',
    'GREY': '#888888',
    'DARK_GRAY': '#444444',
    'DARK_GREY': '#444444',
    'DARKER_GRAY': '#222222',
    'DARKER_GREY': '#222222',
    'BLUE_A': '#C7E9F1',
    'BLUE_B': '#9CDCEB',
    'BLUE_C': '#58C4DD',
    'BLUE_D': '#29ABCA',
    'BLUE_E': '#236B8E',
    'PURE_BLUE': '#0000FF',
    'BLUE': '#58C4DD',
    'DARK_BLUE': '#236B8E',
    'TEAL_A': '#ACEAD7',
    'TEAL_B': '#76DDC0',
    'TEAL_C': '#5CD0B3',
    'TEAL_D': '#55C1A7',
    'TEAL_E': '#49A88F',
    'TEAL': '#5CD0B3',
    'GREEN_A': '#C9E2AE',
    'GREEN_B': '#A6CF8C',
    'GREEN_C': '#83C167',
    'GREEN_D': '#77B05D',
    'GREEN_E': '#699C52',
    'PURE_GREEN': '#00FF00',
    'GREEN': '#83C167',
    'YELLOW_A': '#FFF1B6',
    'YELLOW_B': '#FFEA94',
    'YELLOW_C': '#FFFF00',
    'YELLOW_D': '#F4D345',
    'YELLOW_E': '#E8C11C',
    'YELLOW': '#FFFF00',
    'GOLD_A': '#F7C797',
    'GOLD_B': '#F9B775',
    'GOLD_C': '#F0AC5F',
    'GOLD_D': '#E1A158',
    'GOLD_E': '#C78D46',
    'GOLD': '#F0AC5F',
    'RED_A': '#F7A1A3',
    'RED_B': '#FF8080',
    'RED_C': '#FC6255',
    'RED_D': '#E65A4C',
    'RED_E': '#CF5044',
    'PURE_RED': '#FF0000',
    'RED': '#FC6255',
    'MAROON_A': '#ECABC1',
    'MAROON_B': '#EC92AB',
    'MAROON_C': '#C55F73',
    'MAROON_D': '#A24D61',
    'MAROON_E': '#94424F',
    'MAROON': '#C55F73',
    'PURPLE_A': '#CAA3E8',
    'PURPLE_B': '#B189C6',
    'PURPLE_C': '#9A72AC',
    'PURPLE_D': '#715582',
    'PURPLE_E': '#644172',
    'PURPLE': '#9A72AC',
    'PINK': '#D147BD',
    'LIGHT_PINK': '#DC75CD',
    'ORANGE': '#FF862F',
    'LIGHT_BROWN': '#CD853F',
    'DARK_BROWN': '#8B4513',
    'GRAY_BROWN': '#736357',
    'GREY_BROWN': '#736357'
}


class _Gradient:
    """Base class for SVG gradient definitions."""
    _tag = ''
    _prefix = ''

    def __init__(self, stops, **attrs):
        self.id = f'{self._prefix}{id(self)}'
        self.stops = stops
        self._attrs = attrs

    def to_svg_def(self, time=None):
        attr_str = ' '.join(f"{k}='{v}'" for k, v in self._attrs.items())
        def _stop_svg(s):
            if len(s) == 3:
                return f"<stop offset='{s[0]}' stop-color='{s[1]}' stop-opacity='{s[2]}'/>"
            return f"<stop offset='{s[0]}' stop-color='{s[1]}'/>"
        stops = ''.join(_stop_svg(s) for s in self.stops)
        return f"<{self._tag} id='{self.id}' {attr_str}>{stops}</{self._tag}>"

    def fill_ref(self):
        return f'url(#{self.id})'


class LinearGradient(_Gradient):
    """SVG linear gradient. stops: list of (offset, color) tuples."""
    _tag = 'linearGradient'
    _prefix = 'lg'

    def __init__(self, stops, x1='0%', y1='0%', x2='100%', y2='0%'):
        super().__init__(stops, x1=x1, y1=y1, x2=x2, y2=y2)


class RadialGradient(_Gradient):
    """SVG radial gradient. stops: list of (offset, color) tuples."""
    _tag = 'radialGradient'
    _prefix = 'rg'

    def __init__(self, stops, cx='50%', cy='50%', r='50%', fx=None, fy=None):
        super().__init__(stops, cx=cx, cy=cy, r=r,
                         fx=fx if fx is not None else cx,
                         fy=fy if fy is not None else cy)


def color_from_name(name):
    if name not in colors:
        raise ValueError(f'Color {name} is unknown')
    return colors[name]


def _hex_to_rgb(hex_color):
    """Convert hex color (or named color) to (r, g, b) tuple (0-255)."""
    if hex_color in colors:
        hex_color = colors[hex_color]
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _rgb_to_hex(r, g, b):
    """Convert (r, g, b) values (0-255) to hex color string."""
    return f'#{int(r):02x}{int(g):02x}{int(b):02x}'


def color_gradient(color1, color2=None, n: float = 5):
    """Generate a list of *n* hex colors.

    Accepts two forms:
    - ``color_gradient(color1, color2, n)`` — interpolate between two colors.
    - ``color_gradient([c1, c2, ...], n=k)`` — interpolate through a list of
      color stops, producing *k* evenly-spaced samples.
    """
    if isinstance(color1, (list, tuple)):
        colors = list(color1)
        if n <= 1:
            return [colors[0]]
        result = []
        for i in range(n):
            t = i / (n - 1) * (len(colors) - 1)
            idx = min(int(t), len(colors) - 2)
            result.append(interpolate_color(colors[idx], colors[idx + 1], t - idx))
        return result
    if n <= 1:
        return [color1]
    return [interpolate_color(color1, color2, i / (n - 1)) for i in range(n)]


def interpolate_color(color1, color2, t):
    """Interpolate between two colors at parameter t (0 to 1).
    Returns a hex color string."""
    r1, g1, b1 = _hex_to_rgb(color1)
    r2, g2, b2 = _hex_to_rgb(color2)
    return _rgb_to_hex(r1 + (r2 - r1) * t, g1 + (g2 - g1) * t, b1 + (b2 - b1) * t)


def lighten(color, amount=0.3):
    """Lighten a color by mixing with white."""
    return interpolate_color(color, '#FFFFFF', amount)


def darken(color, amount=0.3):
    """Darken a color by mixing with black."""
    return interpolate_color(color, '#000000', amount)


def _rgb_to_hsl(r, g, b):
    """Convert RGB (0-255) to HSL (h, s, l) all in [0,1]."""
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
    """Convert HSL (all in [0,1]) to RGB (0-255) tuple."""
    if s == 0:
        v = round(l * 255)
        return (v, v, v)
    q = l * (1 + s) if l < 0.5 else l + s - l * s
    p = 2 * l - q
    return (round(_hue2rgb(p, q, h + 1/3) * 255),
            round(_hue2rgb(p, q, h) * 255),
            round(_hue2rgb(p, q, h - 1/3) * 255))


def _hex_to_hsl(hex_color):
    """Convert hex color to (h, s, l) where h in [0,360], s/l in [0,1]."""
    h, s, l = _rgb_to_hsl(*_hex_to_rgb(hex_color))
    return (h * 360, s, l)


def _hsl_to_hex(h, s, l):
    """Convert (h, s, l) to hex string. h in [0,360], s/l in [0,1]."""
    r, g, b = _hsl_to_rgb((h % 360) / 360, s, l)
    return _rgb_to_hex(r, g, b)


def adjust_hue(color, degrees):
    """Rotate the hue of a color by the given degrees."""
    h, s, l = _hex_to_hsl(color)
    return _hsl_to_hex(h + degrees, s, l)


def saturate(color, amount=0.2):
    """Increase saturation by amount (0-1). Clamps to [0,1]."""
    h, s, l = _hex_to_hsl(color)
    return _hsl_to_hex(h, min(1, s + amount), l)


def desaturate(color, amount=0.2):
    """Decrease saturation by amount (0-1). Clamps to [0,1]."""
    h, s, l = _hex_to_hsl(color)
    return _hsl_to_hex(h, max(0, s - amount), l)


def complementary(color):
    """Return the complementary color (hue + 180 degrees)."""
    return adjust_hue(color, 180)


def set_saturation(color, level):
    """Set the saturation of a color to an absolute level (0.0-1.0)."""
    h, _s, l = _hex_to_hsl(color)
    return _hsl_to_hex(h, max(0, min(1, level)), l)


def set_lightness(color, level):
    """Set the lightness of a color to an absolute level (0.0-1.0)."""
    h, s, _l = _hex_to_hsl(color)
    return _hsl_to_hex(h, s, max(0, min(1, level)))


def invert(color):
    """Return the inverse (complementary negative) of a color."""
    r, g, b = _hex_to_rgb(color)
    return f'#{255-r:02x}{255-g:02x}{255-b:02x}'


def triadic(color):
    """Return the two triadic harmony colors (hue +/- 120 degrees)."""
    return [adjust_hue(color, 120), adjust_hue(color, 240)]


def analogous(color, angle: float = 30):
    """Return two analogous colors (hue +/- angle degrees, default 30)."""
    return [adjust_hue(color, -angle), adjust_hue(color, angle)]


def split_complementary(color):
    """Return the two split-complementary colors (hue +/- 150 degrees)."""
    return [adjust_hue(color, 150), adjust_hue(color, 210)]


# Named palette presets
PALETTE_BLUE = ['#58C4DD', '#29ABCA', '#1C758A', '#236B8E', '#2C6FAC']
PALETTE_GREEN = ['#83C167', '#77B05D', '#699C52', '#5B8845', '#4E7438']
PALETTE_RED = ['#FC6255', '#E65A4C', '#CF4044', '#C5352F', '#B42727']
PALETTE_WARM = ['#FFFF00', '#FFD700', '#FF8C00', '#FF4500', '#DC143C']
PALETTE_COOL = ['#58C4DD', '#9CDCEB', '#A8E6CF', '#83C167', '#29ABCA']
PALETTE_RAINBOW = ['#FF0000', '#FF8C00', '#FFFF00', '#00FF00', '#0000FF', '#8B00FF']
