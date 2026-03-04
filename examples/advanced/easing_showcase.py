"""Easing Functions Showcase — visual comparison of all easing families."""
from vectormation.objects import *
from vectormation import easings

v = VectorMathAnim()
v.set_background()
T = 24.0

BLUE   = '#58C4DD'
RED    = '#FC6255'
GREEN  = '#83C167'
YELLOW = '#FFFF00'
PURPLE = '#9A72AC'
ORANGE = '#FF862F'
CYAN   = '#00CED1'
WHITE  = '#FFFFFF'
GREY   = '#888888'

# Row y-positions for 4 rows per phase
ROW_Y = [115, 270, 425, 580]
GRAPH_H = 110


def easing_row(canvas, easings_list, y_top, t_start, row_label,
               colors=None, graph_w=340, graph_h=GRAPH_H, gap=50):
    """Draw a row of small easing graphs with animated dots."""
    n = len(easings_list)
    total_w = n * graph_w + (n - 1) * gap
    x_left = (1920 - total_w) / 2

    label = Text(text=row_label, x=960, y=y_top - 25, font_size=24,
                 fill=WHITE, stroke_width=0, text_anchor='middle')
    label.fadein(t_start, t_start + 0.3)
    label.fadeout(t_start + 5.0, t_start + 5.5)
    canvas.add(label)

    for i, (name, easing_fn) in enumerate(easings_list):
        cx = x_left + i * (graph_w + gap) + graph_w / 2
        color = (colors[i] if colors else
                 [BLUE, RED, GREEN, YELLOW, PURPLE, ORANGE, CYAN][i % 7])

        bg = Rectangle(graph_w, graph_h, x=cx - graph_w / 2, y=y_top,
                        fill='#222244', fill_opacity=0.7, stroke='#555577',
                        stroke_width=1.5, rx=4, creation=t_start + 0.1)
        bg.fadeout(t_start + 5.0, t_start + 5.5)
        canvas.add(bg)

        pad = 10
        gx0 = cx - graph_w / 2 + pad
        gx1 = cx + graph_w / 2 - pad
        gy0 = y_top + graph_h - pad
        gy1 = y_top + pad

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

        txt = Text(text=name, x=cx, y=y_top + graph_h + 18, font_size=14,
                   fill=GREY, stroke_width=0, text_anchor='middle',
                   creation=t_start + 0.2)
        txt.fadeout(t_start + 5.0, t_start + 5.5)
        canvas.add(txt)

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

        dot = Dot(r=5, cx=gx0, cy=gy0,
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
title1 = Text(text='Basic Easings', x=960, y=55, font_size=44,
              fill=WHITE, stroke_width=0, text_anchor='middle')
title1.write(0, 0.6)
title1.fadeout(5.0, 5.5)
v.add(title1)

easing_row(v, [
    ('linear', easings.linear),
    ('smooth', easings.smooth),
    ('rush_into', easings.rush_into),
    ('rush_from', easings.rush_from),
], y_top=ROW_Y[0], t_start=0.3, row_label='Sigmoid-based')

easing_row(v, [
    ('slow_into', easings.slow_into),
    ('double_smooth', easings.double_smooth),
    ('there_and_back', easings.there_and_back),
    ('smoothstep', easings.smoothstep),
], y_top=ROW_Y[1], t_start=0.5, row_label='Smooth Variants')

easing_row(v, [
    ('smootherstep', easings.smootherstep),
    ('smoothererstep', easings.smoothererstep),
    ('lingering', easings.lingering),
    ('running_start', easings.running_start),
], y_top=ROW_Y[2], t_start=0.7, row_label='Advanced Smooth')

easing_row(v, [
    ('there_and_back_wp', easings.there_and_back_with_pause),
    ('exp_decay', easings.exponential_decay),
    ('wiggle', easings.wiggle),
    ('not_quite_there', easings.not_quite_there()),
], y_top=ROW_Y[3], t_start=0.9, row_label='Special')

# =============================================================================
# Phase 2 (6-12s): Sine & Power Easings
# =============================================================================
title2 = Text(text='Sine & Power Easings', x=960, y=55, font_size=44,
              fill=WHITE, stroke_width=0, text_anchor='middle')
title2.write(6, 6.6)
title2.fadeout(11.0, 11.5)
v.add(title2)

easing_row(v, [
    ('ease_in_sine', easings.ease_in_sine),
    ('ease_out_sine', easings.ease_out_sine),
    ('ease_in_out_sine', easings.ease_in_out_sine),
    ('ease_in_quad', easings.ease_in_quad),
], y_top=ROW_Y[0], t_start=6.3, row_label='Sine & Quad In')

easing_row(v, [
    ('ease_out_quad', easings.ease_out_quad),
    ('ease_in_out_quad', easings.ease_in_out_quad),
    ('ease_in_cubic', easings.ease_in_cubic),
    ('ease_out_cubic', easings.ease_out_cubic),
], y_top=ROW_Y[1], t_start=6.5, row_label='Quad Out & Cubic')

easing_row(v, [
    ('ease_in_out_cubic', easings.ease_in_out_cubic),
    ('ease_in_quart', easings.ease_in_quart),
    ('ease_out_quart', easings.ease_out_quart),
    ('ease_in_out_quart', easings.ease_in_out_quart),
], y_top=ROW_Y[2], t_start=6.7, row_label='Cubic InOut & Quart')

easing_row(v, [
    ('ease_in_quint', easings.ease_in_quint),
    ('ease_out_quint', easings.ease_out_quint),
    ('ease_in_out_quint', easings.ease_in_out_quint),
    ('ease_in_expo', easings.ease_in_expo),
], y_top=ROW_Y[3], t_start=6.9, row_label='Quint & Expo In')

# =============================================================================
# Phase 3 (12-18s): Expo, Circ, Back & Elastic
# =============================================================================
title3 = Text(text='Expo, Circ, Back & Elastic', x=960, y=55, font_size=44,
              fill=WHITE, stroke_width=0, text_anchor='middle')
title3.write(12, 12.6)
title3.fadeout(17.0, 17.5)
v.add(title3)

easing_row(v, [
    ('ease_out_expo', easings.ease_out_expo),
    ('ease_in_out_expo', easings.ease_in_out_expo),
    ('ease_in_circ', easings.ease_in_circ),
    ('ease_out_circ', easings.ease_out_circ),
], y_top=ROW_Y[0], t_start=12.3, row_label='Expo Out & Circ')

easing_row(v, [
    ('ease_in_out_circ', easings.ease_in_out_circ),
    ('ease_in_back', easings.ease_in_back),
    ('ease_out_back', easings.ease_out_back),
    ('ease_in_out_back', easings.ease_in_out_back),
], y_top=ROW_Y[1], t_start=12.5, row_label='Circ InOut & Back')

easing_row(v, [
    ('ease_in_elastic', easings.ease_in_elastic),
    ('ease_out_elastic', easings.ease_out_elastic),
    ('ease_in_out_elastic', easings.ease_in_out_elastic),
    ('ease_in_bounce', easings.ease_in_bounce),
], y_top=ROW_Y[2], t_start=12.7, row_label='Elastic & Bounce In')

easing_row(v, [
    ('ease_out_bounce', easings.ease_out_bounce),
    ('ease_in_out_bounce', easings.ease_in_out_bounce),
    ('step(4)', easings.step(4)),
    ('step(8)', easings.step(8)),
], y_top=ROW_Y[3], t_start=12.9, row_label='Bounce Out & Step')

# =============================================================================
# Phase 4 (18-24s): Combinators
# =============================================================================
title4 = Text(text='Easing Combinators', x=960, y=55, font_size=44,
              fill=WHITE, stroke_width=0, text_anchor='middle')
title4.write(18, 18.6)
title4.fadeout(23.0, 23.5)
v.add(title4)

easing_row(v, [
    ('step(16)', easings.step(16)),
    ('reverse(smooth)', easings.reverse(easings.smooth)),
    ('reverse(in_cubic)', easings.reverse(easings.ease_in_cubic)),
    ('reverse(out_bounce)', easings.reverse(easings.ease_out_bounce)),
], y_top=ROW_Y[0], t_start=18.3, row_label='Step & Reverse')

easing_row(v, [
    ('repeat(smooth,2)', easings.repeat(easings.smooth, 2)),
    ('repeat(smooth,3)', easings.repeat(easings.smooth, 3)),
    ('oscillate(smooth,1)', easings.oscillate(easings.smooth, 1)),
    ('oscillate(smooth,2)', easings.oscillate(easings.smooth, 2)),
], y_top=ROW_Y[1], t_start=18.5, row_label='Repeat & Oscillate')

easing_row(v, [
    ('clamp(smooth,.2,.8)', easings.clamp(easings.smooth, 0.2, 0.8)),
    ('blend(lin,bounce)', easings.blend(easings.linear, easings.ease_out_bounce)),
    ('compose(in,out)', easings.compose(easings.ease_in_cubic, easings.ease_out_elastic)),
    ('blend(smooth,elastic)', easings.blend(easings.smooth, easings.ease_out_elastic)),
], y_top=ROW_Y[2], t_start=18.7, row_label='Clamp, Blend & Compose')

easing_row(v, [
    ('repeat(bounce,2)', easings.repeat(easings.ease_out_bounce, 2)),
    ('oscillate(expo,2)', easings.oscillate(easings.ease_in_out_expo, 2)),
    ('clamp(elastic,.1,.9)', easings.clamp(easings.ease_out_elastic, 0.1, 0.9)),
    ('compose(sine,bounce)', easings.compose(easings.ease_in_sine, easings.ease_out_bounce)),
], y_top=ROW_Y[3], t_start=18.9, row_label='Advanced Combos')

# =============================================================================
# Display
# =============================================================================

v.show(end=T)
