"""Easing Functions Showcase — visual comparison of all easing families."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from vectormation.objects import *
from vectormation import easings

args = parse_args()
v = VectorMathAnim(verbose=args.verbose, save_dir='svgs/easing_showcase')
v.set_background()
T = 36.0

BLUE   = '#58C4DD'
RED    = '#FC6255'
GREEN  = '#83C167'
YELLOW = '#FFFF00'
PURPLE = '#9A72AC'
ORANGE = '#FF862F'
CYAN   = '#00CED1'
WHITE  = '#FFFFFF'
GREY   = '#888888'

# =============================================================================
# Helper: draw a row of easing curves with moving dots
# =============================================================================
def easing_row(canvas, easings_list, y_top, t_start, row_label,
               colors=None, graph_w=340, graph_h=120, gap=50):
    """Draw a row of small easing graphs with animated dots."""
    n = len(easings_list)
    total_w = n * graph_w + (n - 1) * gap
    x_left = (1920 - total_w) / 2

    label = Text(text=row_label, x=960, y=y_top - 30, font_size=30,
                 fill=WHITE, stroke_width=0, text_anchor='middle')
    label.fadein(t_start, t_start + 0.3)
    label.fadeout(t_start + 5.0, t_start + 5.5)
    canvas.add(label)

    for i, (name, easing_fn) in enumerate(easings_list):
        cx = x_left + i * (graph_w + gap) + graph_w / 2
        color = (colors[i] if colors else
                 [BLUE, RED, GREEN, YELLOW, PURPLE, ORANGE, CYAN][i % 7])

        # Background box
        bg = Rectangle(graph_w, graph_h, x=cx - graph_w / 2, y=y_top,
                        fill='#1a1a2e', fill_opacity=0.6, stroke=GREY,
                        stroke_width=1, creation=t_start + 0.1)
        bg.fadeout(t_start + 5.0, t_start + 5.5)
        canvas.add(bg)

        # Easing name
        txt = Text(text=name, x=cx, y=y_top + graph_h + 22, font_size=16,
                   fill=GREY, stroke_width=0, text_anchor='middle',
                   creation=t_start + 0.2)
        txt.fadeout(t_start + 5.0, t_start + 5.5)
        canvas.add(txt)

        # Easing curve (sampled as a Path)
        points = []
        steps = 60
        for s in range(steps + 1):
            t = s / steps
            val = easing_fn(t)
            px = cx - graph_w / 2 + 10 + t * (graph_w - 20)
            py = y_top + graph_h - 10 - val * (graph_h - 20)
            points.append((px, py))

        d = f'M {points[0][0]:.1f} {points[0][1]:.1f}'
        for px, py in points[1:]:
            d += f' L {px:.1f} {py:.1f}'
        curve = Path(d, stroke=color, stroke_width=2, fill_opacity=0,
                     creation=t_start + 0.3)
        curve.fadeout(t_start + 5.0, t_start + 5.5)
        canvas.add(curve)

        # Animated dot moving along x, y driven by easing
        dot = Dot(r=6, cx=cx - graph_w / 2 + 10, cy=y_top + graph_h - 10,
                  fill=color, creation=t_start + 0.5)
        anim_dur = 3.5
        anim_start = t_start + 0.8

        x_start_pos = cx - graph_w / 2 + 10
        x_end_pos = cx + graph_w / 2 - 10
        y_bottom = y_top + graph_h - 10
        y_top_pos = y_top + 10

        dot.add_updater(
            lambda obj, time, _es=easing_fn, _xs=x_start_pos, _xe=x_end_pos,
                   _yb=y_bottom, _yt=y_top_pos, _as=anim_start, _ad=anim_dur:
            _dot_update(obj, time, _es, _xs, _xe, _yb, _yt, _as, _ad),
            start=anim_start, end=anim_start + anim_dur
        )
        dot.fadeout(t_start + 5.0, t_start + 5.5)
        canvas.add(dot)


def _dot_update(obj, time, easing_fn, x_start, x_end, y_bottom, y_top, anim_start, anim_dur):
    t = max(0, min(1, (time - anim_start) / anim_dur))
    val = easing_fn(t)
    px = x_start + t * (x_end - x_start)
    py = y_bottom - val * (y_bottom - y_top)
    obj.cx.set_to(px, time)
    obj.cy.set_to(py, time)


# =============================================================================
# Phase 1 (0-6s): Basic Easings
# =============================================================================
title1 = Text(text='Basic Easings', x=960, y=60, font_size=48,
              fill=WHITE, stroke_width=0, text_anchor='middle')
title1.write(0, 0.6)
title1.fadeout(5.0, 5.5)
v.add(title1)

easing_row(v, [
    ('linear', easings.linear),
    ('smooth', easings.smooth),
    ('rush_into', easings.rush_into),
    ('rush_from', easings.rush_from),
], y_top=120, t_start=0.3, row_label='Sigmoid-based')

easing_row(v, [
    ('slow_into', easings.slow_into),
    ('double_smooth', easings.double_smooth),
    ('there_and_back', easings.there_and_back),
    ('smoothstep', easings.smoothstep),
], y_top=340, t_start=0.5, row_label='Smooth Variants')

easing_row(v, [
    ('smootherstep', easings.smootherstep),
    ('smoothererstep', easings.smoothererstep),
    ('lingering', easings.lingering),
    ('running_start', easings.running_start),
], y_top=560, t_start=0.7, row_label='Advanced Smooth')

# =============================================================================
# Phase 2 (6-12s): Sine & Power Easings
# =============================================================================
title2 = Text(text='Sine & Power Easings', x=960, y=60, font_size=48,
              fill=WHITE, stroke_width=0, text_anchor='middle')
title2.write(6, 6.6)
title2.fadeout(11.0, 11.5)
v.add(title2)

easing_row(v, [
    ('ease_in_sine', easings.ease_in_sine),
    ('ease_out_sine', easings.ease_out_sine),
    ('ease_in_out_sine', easings.ease_in_out_sine),
], y_top=120, t_start=6.3, row_label='Sine', graph_w=480, gap=40)

easing_row(v, [
    ('ease_in_quad', easings.ease_in_quad),
    ('ease_out_quad', easings.ease_out_quad),
    ('ease_in_cubic', easings.ease_in_cubic),
    ('ease_out_cubic', easings.ease_out_cubic),
], y_top=340, t_start=6.5, row_label='Quad & Cubic')

easing_row(v, [
    ('ease_in_quart', easings.ease_in_quart),
    ('ease_out_quart', easings.ease_out_quart),
    ('ease_in_quint', easings.ease_in_quint),
    ('ease_out_quint', easings.ease_out_quint),
], y_top=560, t_start=6.7, row_label='Quart & Quint')

# =============================================================================
# Phase 3 (12-18s): Expo, Circ, Back
# =============================================================================
title3 = Text(text='Expo, Circ & Back Easings', x=960, y=60, font_size=48,
              fill=WHITE, stroke_width=0, text_anchor='middle')
title3.write(12, 12.6)
title3.fadeout(17.0, 17.5)
v.add(title3)

easing_row(v, [
    ('ease_in_expo', easings.ease_in_expo),
    ('ease_out_expo', easings.ease_out_expo),
    ('ease_in_out_expo', easings.ease_in_out_expo),
], y_top=120, t_start=12.3, row_label='Exponential', graph_w=480, gap=40)

easing_row(v, [
    ('ease_in_circ', easings.ease_in_circ),
    ('ease_out_circ', easings.ease_out_circ),
    ('ease_in_out_circ', easings.ease_in_out_circ),
], y_top=340, t_start=12.5, row_label='Circular', graph_w=480, gap=40)

easing_row(v, [
    ('ease_in_back', easings.ease_in_back),
    ('ease_out_back', easings.ease_out_back),
    ('ease_in_out_back', easings.ease_in_out_back),
], y_top=560, t_start=12.7, row_label='Back (overshoot)', graph_w=480, gap=40)

# =============================================================================
# Phase 4 (18-24s): Elastic & Bounce
# =============================================================================
title4 = Text(text='Elastic & Bounce Easings', x=960, y=60, font_size=48,
              fill=WHITE, stroke_width=0, text_anchor='middle')
title4.write(18, 18.6)
title4.fadeout(23.0, 23.5)
v.add(title4)

easing_row(v, [
    ('ease_in_elastic', easings.ease_in_elastic),
    ('ease_out_elastic', easings.ease_out_elastic),
    ('ease_in_out_elastic', easings.ease_in_out_elastic),
], y_top=120, t_start=18.3, row_label='Elastic', graph_w=480, gap=40)

easing_row(v, [
    ('ease_in_bounce', easings.ease_in_bounce),
    ('ease_out_bounce', easings.ease_out_bounce),
    ('ease_in_out_bounce', easings.ease_in_out_bounce),
], y_top=340, t_start=18.5, row_label='Bounce', graph_w=480, gap=40)

easing_row(v, [
    ('exp_decay', easings.exponential_decay),
    ('wiggle', easings.wiggle),
    ('not_quite_there', easings.not_quite_there()),
], y_top=560, t_start=18.7, row_label='Special', graph_w=480, gap=40)

# =============================================================================
# Phase 5 (24-30s): Combinators
# =============================================================================
title5 = Text(text='Easing Combinators', x=960, y=60, font_size=48,
              fill=WHITE, stroke_width=0, text_anchor='middle')
title5.write(24, 24.6)
title5.fadeout(29.0, 29.5)
v.add(title5)

easing_row(v, [
    ('step(4)', easings.step(4)),
    ('step(8)', easings.step(8)),
    ('reverse(smooth)', easings.reverse(easings.smooth)),
], y_top=120, t_start=24.3, row_label='Step & Reverse', graph_w=480, gap=40)

easing_row(v, [
    ('repeat(smooth,3)', easings.repeat(easings.smooth, 3)),
    ('oscillate(smooth,2)', easings.oscillate(easings.smooth, 2)),
    ('clamp(smooth,0.2,0.8)', easings.clamp(easings.smooth, 0.2, 0.8)),
], y_top=340, t_start=24.5, row_label='Repeat, Oscillate & Clamp', graph_w=480, gap=40)

easing_row(v, [
    ('blend(linear,bounce)', easings.blend(easings.linear, easings.ease_out_bounce)),
    ('compose(in,out)', easings.compose(easings.ease_in_cubic, easings.ease_out_elastic)),
], y_top=560, t_start=24.7, row_label='Blend & Compose', graph_w=680, gap=60)

# =============================================================================
# Phase 6 (30-36s): Side-by-side comparison
# =============================================================================
title6 = Text(text='Side-by-Side Comparison', x=960, y=60, font_size=48,
              fill=WHITE, stroke_width=0, text_anchor='middle')
title6.write(30, 30.6)
title6.fadeout(35.0, 35.5)
v.add(title6)

# Race: move circles across the screen with different easings
compare_easings = [
    ('linear', easings.linear, GREY),
    ('smooth', easings.smooth, BLUE),
    ('ease_in_cubic', easings.ease_in_cubic, RED),
    ('ease_out_cubic', easings.ease_out_cubic, GREEN),
    ('ease_in_out_expo', easings.ease_in_out_expo, YELLOW),
    ('ease_out_bounce', easings.ease_out_bounce, ORANGE),
    ('ease_out_elastic', easings.ease_out_elastic, PURPLE),
    ('ease_out_back', easings.ease_out_back, CYAN),
]

lane_h = 80
total_h = len(compare_easings) * lane_h
y_start_race = (1080 - total_h) / 2 + 40
x_left_race = 250
x_right_race = 1670

for i, (name, easing_fn, color) in enumerate(compare_easings):
    y = y_start_race + i * lane_h

    # Lane line
    lane = Line(x1=x_left_race, y1=y + lane_h - 5, x2=x_right_race, y2=y + lane_h - 5,
                stroke='#333333', stroke_width=1, creation=30.2)
    lane.fadeout(35.0, 35.5)
    v.add(lane)

    # Label
    lbl = Text(text=name, x=x_left_race - 15, y=y + lane_h / 2 + 5, font_size=18,
               fill=color, stroke_width=0, text_anchor='end', creation=30.3)
    lbl.fadeout(35.0, 35.5)
    v.add(lbl)

    # Racing dot
    dot = Dot(r=12, cx=x_left_race, cy=y + lane_h / 2 - 5, fill=color, creation=30.5)
    dot.shift(dx=x_right_race - x_left_race, dy=0, start=31.0, end=34.5,
              easing=easing_fn)
    dot.fadeout(35.0, 35.5)
    v.add(dot)

# =============================================================================
# Display
# =============================================================================
v.browser_display(
        start=args.start or 0,
        end=args.end or T,
        fps=args.fps,
        port=args.port,
    )
