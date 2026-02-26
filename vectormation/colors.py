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
    """Convert hex color string to (r, g, b) tuple (0-255)."""
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _rgb_to_hex(r, g, b):
    """Convert (r, g, b) values (0-255) to hex color string."""
    return f'#{int(r):02x}{int(g):02x}{int(b):02x}'


def color_gradient(color1, color2, n=5):
    """Generate a list of n hex colors interpolated between color1 and color2.
    Colors can be hex strings or named colors."""
    if color1 in colors:
        color1 = colors[color1]
    if color2 in colors:
        color2 = colors[color2]
    r1, g1, b1 = _hex_to_rgb(color1)
    r2, g2, b2 = _hex_to_rgb(color2)
    return [_rgb_to_hex(r1 + (r2 - r1) * i / (n - 1),
                        g1 + (g2 - g1) * i / (n - 1),
                        b1 + (b2 - b1) * i / (n - 1))
            for i in range(n)]


def interpolate_color(color1, color2, t):
    """Interpolate between two colors at parameter t (0 to 1).
    Returns a hex color string."""
    if color1 in colors:
        color1 = colors[color1]
    if color2 in colors:
        color2 = colors[color2]
    r1, g1, b1 = _hex_to_rgb(color1)
    r2, g2, b2 = _hex_to_rgb(color2)
    return _rgb_to_hex(r1 + (r2 - r1) * t, g1 + (g2 - g1) * t, b1 + (b2 - b1) * t)


def lighten(color, amount=0.3):
    """Lighten a color by mixing with white."""
    return interpolate_color(color, '#FFFFFF', amount)


def darken(color, amount=0.3):
    """Darken a color by mixing with black."""
    return interpolate_color(color, '#000000', amount)


def _hex_to_hsl(hex_color):
    """Convert hex color to (h, s, l) where h in [0,360], s/l in [0,1]."""
    if hex_color in colors:
        hex_color = colors[hex_color]
    r, g, b = _hex_to_rgb(hex_color)
    r, g, b = r / 255, g / 255, b / 255
    mx, mn = max(r, g, b), min(r, g, b)
    l = (mx + mn) / 2
    if mx == mn:
        h = s = 0.0
    else:
        d = mx - mn
        s = d / (2 - mx - mn) if l > 0.5 else d / (mx + mn)
        if mx == r:
            h = ((g - b) / d + (6 if g < b else 0)) / 6
        elif mx == g:
            h = ((b - r) / d + 2) / 6
        else:
            h = ((r - g) / d + 4) / 6
    return (h * 360, s, l)


def _hsl_to_hex(h, s, l):
    """Convert (h, s, l) to hex string. h in [0,360], s/l in [0,1]."""
    h = (h % 360) / 360
    if s == 0:
        v = int(round(l * 255))
        return _rgb_to_hex(v, v, v)

    def hue_to_rgb(p, q, t):
        if t < 0: t += 1
        if t > 1: t -= 1
        if t < 1/6: return p + (q - p) * 6 * t
        if t < 1/2: return q
        if t < 2/3: return p + (q - p) * (2/3 - t) * 6
        return p

    q = l * (1 + s) if l < 0.5 else l + s - l * s
    p = 2 * l - q
    r = int(round(hue_to_rgb(p, q, h + 1/3) * 255))
    g = int(round(hue_to_rgb(p, q, h) * 255))
    b = int(round(hue_to_rgb(p, q, h - 1/3) * 255))
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


# Named palette presets
PALETTE_BLUE = ['#58C4DD', '#29ABCA', '#1C758A', '#236B8E', '#2C6FAC']
PALETTE_GREEN = ['#83C167', '#77B05D', '#699C52', '#5B8845', '#4E7438']
PALETTE_RED = ['#FC6255', '#E65A4C', '#CF4044', '#C5352F', '#B42727']
PALETTE_WARM = ['#FFFF00', '#FFD700', '#FF8C00', '#FF4500', '#DC143C']
PALETTE_COOL = ['#58C4DD', '#9CDCEB', '#A8E6CF', '#83C167', '#29ABCA']
PALETTE_RAINBOW = ['#FF0000', '#FF8C00', '#FFFF00', '#00FF00', '#0000FF', '#8B00FF']
