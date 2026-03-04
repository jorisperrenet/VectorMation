"""Easing Functions Showcase — visual comparison of all easing families."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
from vectormation.objects import *
from vectormation import easings

args = parse_args()
v = VectorMathAnim(verbose=args.verbose, save_dir='svgs/easing_showcase')
v.set_background()
T = 38.0

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

        # Background box (lighter, more visible)
        bg = Rectangle(graph_w, graph_h, x=cx - graph_w / 2, y=y_top,
                        fill='#222244', fill_opacity=0.7, stroke='#555577',
                        stroke_width=1.5, rx=4, creation=t_start + 0.1)
        bg.fadeout(t_start + 5.0, t_start + 5.5)
        canvas.add(bg)

        # Axis markings: faint lines at y=0 and y=1, labels
        pad = 10
        gx0 = cx - graph_w / 2 + pad
        gx1 = cx + graph_w / 2 - pad
        gy0 = y_top + graph_h - pad  # y=0 (bottom)
        gy1 = y_top + pad            # y=1 (top)

        baseline = Line(x1=gx0, y1=gy0, x2=gx1, y2=gy0,
                        stroke='#444466', stroke_width=1,
                        stroke_dasharray='4 3', creation=t_start + 0.1)
        baseline.fadeout(t_start + 5.0, t_start + 5.5)
        canvas.add(baseline)

        topline = Line(x1=gx0, y1=gy1, x2=gx1, y2=gy1,
                       stroke='#444466', stroke_width=1,
                       stroke_dasharray='4 3', creation=t_start + 0.1)
        topline.fadeout(t_start + 5.0, t_start + 5.5)
        canvas.add(topline)

        lbl_0 = Text(text='0', x=gx0 - 8, y=gy0 + 4, font_size=11,
                      fill='#556', stroke_width=0, text_anchor='end',
                      creation=t_start + 0.1)
        lbl_0.fadeout(t_start + 5.0, t_start + 5.5)
        canvas.add(lbl_0)

        lbl_1 = Text(text='1', x=gx0 - 8, y=gy1 + 4, font_size=11,
                      fill='#556', stroke_width=0, text_anchor='end',
                      creation=t_start + 0.1)
        lbl_1.fadeout(t_start + 5.0, t_start + 5.5)
        canvas.add(lbl_1)

        # Easing name
        txt = Text(text=name, x=cx, y=y_top + graph_h + 22, font_size=16,
                   fill=GREY, stroke_width=0, text_anchor='middle',
                   creation=t_start + 0.2)
        txt.fadeout(t_start + 5.0, t_start + 5.5)
        canvas.add(txt)

        # Easing curve (drawn progressively with draw_along)
        points = []
        steps = 60
        for s in range(steps + 1):
            t = s / steps
            val = easing_fn(t)
            px = gx0 + t * (gx1 - gx0)
            py = gy0 - val * (gy0 - gy1)
            points.append((px, py))

        d = f'M {points[0][0]:.1f} {points[0][1]:.1f}'
        for px, py in points[1:]:
            d += f' L {px:.1f} {py:.1f}'
        curve = Path(d, stroke=color, stroke_width=2.5, fill_opacity=0,
                     creation=t_start + 0.3)
        curve.draw_along(t_start + 0.5, t_start + 0.5 + 1.2)
        curve.fadeout(t_start + 5.0, t_start + 5.5)
        canvas.add(curve)

        # Animated dot moving along x, y driven by easing
        dot = Dot(r=6, cx=gx0, cy=gy0,
                  fill=color, creation=t_start + 0.5)
        anim_dur = 3.5
        anim_start = t_start + 0.8

        dot.add_updater(
            lambda obj, time, _es=easing_fn, _xs=gx0, _xe=gx1,
                   _yb=gy0, _yt=gy1, _as=anim_start, _ad=anim_dur:
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
    obj.c.time_func = lambda t, _px=px, _py=py: (_px, _py)


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
# Phase 6 (30-38s): Side-by-side race (extended)
# =============================================================================
title6 = Text(text='Side-by-Side Race', x=960, y=60, font_size=48,
              fill=WHITE, stroke_width=0, text_anchor='middle')
title6.write(30, 30.6)
title6.fadeout(37.0, 37.5)
v.add(title6)

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

# Start line
start_line = Line(x1=x_left_race, y1=y_start_race - 10,
                  x2=x_left_race, y2=y_start_race + total_h,
                  stroke='#83C167', stroke_width=2, creation=30.2)
start_line.fadeout(37.0, 37.5)
v.add(start_line)

start_lbl = Text(text='START', x=x_left_race, y=y_start_race - 20,
                 font_size=14, fill='#83C167', stroke_width=0,
                 text_anchor='middle', creation=30.2)
start_lbl.fadeout(37.0, 37.5)
v.add(start_lbl)

# Finish line
finish_line = Line(x1=x_right_race, y1=y_start_race - 10,
                   x2=x_right_race, y2=y_start_race + total_h,
                   stroke='#FC6255', stroke_width=2,
                   stroke_dasharray='8 8', creation=30.2)
finish_line.fadeout(37.0, 37.5)
v.add(finish_line)

finish_lbl = Text(text='FINISH', x=x_right_race, y=y_start_race - 20,
                  font_size=14, fill='#FC6255', stroke_width=0,
                  text_anchor='middle', creation=30.2)
finish_lbl.fadeout(37.0, 37.5)
v.add(finish_lbl)

for i, (name, easing_fn, color) in enumerate(compare_easings):
    y = y_start_race + i * lane_h

    # Lane line
    lane = Line(x1=x_left_race, y1=y + lane_h - 5, x2=x_right_race, y2=y + lane_h - 5,
                stroke='#333333', stroke_width=1, creation=30.2)
    lane.fadeout(37.0, 37.5)
    v.add(lane)

    # Label
    lbl = Text(text=name, x=x_left_race - 15, y=y + lane_h / 2 + 5, font_size=18,
               fill=color, stroke_width=0, text_anchor='end', creation=30.3)
    lbl.fadeout(37.0, 37.5)
    v.add(lbl)

    # Racing dot (extended race: 31.0 to 36.0 = 5 seconds)
    dot = Dot(r=12, cx=x_left_race, cy=y + lane_h / 2 - 5, fill=color, creation=30.5)
    dot.shift(dx=x_right_race - x_left_race, dy=0, start=31.0, end=36.0,
              easing=easing_fn)
    dot.fadeout(37.0, 37.5)
    v.add(dot)

# =============================================================================
# Display
# =============================================================================
if args.for_docs:
    v.export_video('docs/source/_static/videos/easing_showcase.mp4', fps=30, end=T)
if not args.for_docs:
    v.browser_display(
    start=args.start or 0,
    end=args.end or T,
    fps=args.fps,
    port=args.port,
    )
