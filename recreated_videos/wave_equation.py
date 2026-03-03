"""Wave Equation — standing waves on a vibrating string.

Shows the fundamental mode and first few harmonics of a vibrating string,
demonstrating superposition and standing wave patterns.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/wave_equation')
canvas.set_background()

# ── Parameters ────────────────────────────────────────────────────────
string_length = 1200  # pixels
amplitude = 60        # pixels
x_start = 360
y_center = 300
T = 10.0

# ── Individual mode shapes ───────────────────────────────────────────
mode_colors = ['#58C4DD', '#83C167', '#FFFF00', '#FC6255']
n_modes = 4
mode_spacing = 160
n_points = 200

for mode in range(1, n_modes + 1):
    y_base = y_center + (mode - 1) * mode_spacing
    color = mode_colors[mode - 1]
    freq = mode * 0.5  # frequency increases with mode number

    # Fixed endpoints
    pin_left = Dot(cx=x_start, cy=y_base, r=5, fill='#fff', stroke_width=0, creation=0)
    pin_right = Dot(cx=x_start + string_length, cy=y_base, r=5,
                     fill='#fff', stroke_width=0, creation=0)

    # Mode label
    label = Text(text=f'n = {mode}', x=x_start - 60, y=y_base + 5,
                 font_size=22, fill=color, stroke_width=0,
                 text_anchor='end', creation=0)
    label.fadein(0.5 + mode * 0.3, 1 + mode * 0.3)

    # Frequency label
    freq_label = Text(text=f'f = {mode}f\u2081',
                      x=x_start + string_length + 60, y=y_base + 5,
                      font_size=18, fill='#888', stroke_width=0,
                      text_anchor='start', creation=0)
    freq_label.fadein(0.5 + mode * 0.3, 1 + mode * 0.3)

    # Animated wave path
    def _make_wave(m=mode, yb=y_base, f=freq):
        def _path(t):
            pts = []
            for i in range(n_points + 1):
                x_frac = i / n_points
                x = x_start + x_frac * string_length
                # Standing wave: sin(n*pi*x/L) * cos(omega*t)
                y = yb - amplitude * math.sin(m * math.pi * x_frac) * math.cos(2 * math.pi * f * t)
                pts.append((x, y))
            d = f'M{pts[0][0]:.1f},{pts[0][1]:.1f}'
            for px, py in pts[1:]:
                d += f'L{px:.1f},{py:.1f}'
            return d
        return _path

    wave = Path('', stroke=color, stroke_width=3, fill_opacity=0, creation=0)
    wave.d.set_onward(0, _make_wave())

    # Node indicators (dots at zero-crossing points)
    for k in range(1, mode):
        node_x = x_start + k * string_length / mode
        node = Dot(cx=node_x, cy=y_base, r=4, fill='#fff',
                    stroke=color, stroke_width=1, creation=0)
        node.fadein(1 + mode * 0.3, 1.5 + mode * 0.3)
        canvas.add(node)

    # Equilibrium line (dashed)
    eq_line = Line(x1=x_start, y1=y_base, x2=x_start + string_length, y2=y_base,
                    stroke='#333', stroke_width=1, stroke_dasharray='4 4', creation=0)

    canvas.add(eq_line, wave, pin_left, pin_right, label, freq_label)

# ── Title ────────────────────────────────────────────────────────────
title = Text(text='Standing Waves on a String', x=960, y=50,
             font_size=42, fill='#fff', stroke_width=0,
             text_anchor='middle', creation=0)
title.fadein(0, 0.5)

equation = Text(text='y(x,t) = A sin(n\u03c0x/L) cos(\u03c9t)',
                x=960, y=1020, font_size=22, fill='#aaa',
                stroke_width=0, text_anchor='middle', creation=0)
equation.fadein(0.5, 1)

canvas.add(title, equation)

canvas.browser_display(start=args.start or 0, end=args.end or T,
                           fps=args.fps, port=args.port)
