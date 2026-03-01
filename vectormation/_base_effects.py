"""Advanced animation methods for VObject (mixed in as a base class)."""
import math
from copy import deepcopy

import vectormation.easings as easings
import vectormation.attributes as attributes
import vectormation.style as style
from vectormation._base_helpers import (
    _clamp01, _lerp, _ramp, _clip_reveal,
    _coords_of, _parse_path,
    _make_brect, _wrap_to_svg, _EDGE_POINTS,
)
from vectormation._constants import (
    UP, RIGHT,
    SMALL_BUFF, MED_SMALL_BUFF,
)

def _apply_pos_offset(obj, time, dx, dy):
    """Shift all position attributes of *obj* by (*dx*, *dy*) at *time*."""
    for xa, ya in obj._shift_reals():
        xa.set_onward(time, xa.at_time(time) + dx)
        ya.set_onward(time, ya.at_time(time) + dy)
    for c in obj._shift_coors():
        val = c.at_time(time)
        c.set_onward(time, (val[0] + dx, val[1] + dy))


def _ensure_text(obj, method):
    """Raise TypeError if *obj* is not a Text instance."""
    from vectormation._shapes import Text as _Text
    if not isinstance(obj, _Text):
        raise TypeError(f"{method}() can only be called on Text objects")


class _VObjectEffectsMixin:
    """Advanced animation and effect methods, mixed into VObject."""
    def scale_to_fit(self, width=None, height=None, start: float = 0, end: float | None = None, easing=easings.smooth):
        """Scale to fit within the given *width*/*height*, preserving aspect ratio."""
        cur_w = self.get_width(start)
        cur_h = self.get_height(start)
        if cur_w <= 0 and cur_h <= 0:
            return self
        factors = []
        if width is not None and cur_w > 0:
            factors.append(width / cur_w)
        if height is not None and cur_h > 0:
            factors.append(height / cur_h)
        if not factors:
            return self
        return self.scale(min(factors), start=start, end=end, easing=easing)

    def match_position(self, other, time: float = 0):
        """Move this object so its center matches *other*'s center at *time*."""
        return self.move_to(*_coords_of(other, time), start=time)

    def point_from_proportion(self, t, time: float = 0):
        """Return the (x, y) point at proportion *t* (0-1) along this object's SVG path outline."""
        path_d = self.path(time)
        if not path_d:
            return self.center(time)
        parsed, total_length = _parse_path(path_d)
        if total_length <= 0:
            pt = parsed.point(0)
            return (pt.real, pt.imag)
        t = _clamp01(t)
        pt = parsed.point(parsed.ilength(t * total_length))
        return (pt.real, pt.imag)

    def connect(self, other, start_edge='right', end_edge='left', arrow=False,
                follow=False, start=0, **kwargs):
        """Create a Line (or Arrow) connecting *self* to *other* at specified edges."""
        p1 = self.get_edge(start_edge, time=start)
        p2 = other.get_edge(end_edge, time=start)
        if arrow:
            from vectormation._arrows import Arrow as _Arrow
            connector = _Arrow(x1=p1[0], y1=p1[1], x2=p2[0], y2=p2[1],
                               creation=start, **kwargs)
            if follow:
                connector.shaft.p1.set_onward(start,
                    lambda t, _s=self, _e=start_edge: _s.get_edge(_e, time=t))
                connector.shaft.p2.set_onward(start,
                    lambda t, _o=other, _e=end_edge: _o.get_edge(_e, time=t))
                connector._update_tip_dynamic(start)
        else:
            from vectormation._shapes import Line as _Line
            connector = _Line(x1=p1[0], y1=p1[1], x2=p2[0], y2=p2[1],
                              creation=start, **kwargs)
            if follow:
                connector.p1.set_onward(start,
                    lambda t, _s=self, _e=start_edge: _s.get_edge(_e, time=t))
                connector.p2.set_onward(start,
                    lambda t, _o=other, _e=end_edge: _o.get_edge(_e, time=t))
        return connector

    def match_style(self, other, time: float = 0):
        """Copy fill, stroke, opacity, and stroke_width from *other* at *time*."""
        self.styling.fill.set_onward(time, other.styling.fill.time_func(time))
        self.styling.stroke.set_onward(time, other.styling.stroke.time_func(time))
        self.styling.fill_opacity.set_onward(time, other.styling.fill_opacity.at_time(time))
        self.styling.stroke_opacity.set_onward(time, other.styling.stroke_opacity.at_time(time))
        self.styling.stroke_width.set_onward(time, other.styling.stroke_width.at_time(time))
        return self

    def telegraph(self, start: float = 0, end: float = 0.4,
                  scale_factor: float = 1.4, shake_amplitude: float = 8,
                  easing=easings.there_and_back):
        """Quick attention-grabbing burst: scale spike + shake + opacity dip."""
        if end <= start:
            return self
        self._ensure_scale_origin(start)
        _d = max(end - start, 1e-9)
        scale_fn = _lerp(start, _d, 1, scale_factor, easing)
        self._set_scale_xy(start, end, scale_fn)
        self.styling.opacity.set(start, end, _lerp(start, _d, 1, 0.7, easing))
        shake_freq = 12
        def _dx(t, _s=start, _d=_d, _a=shake_amplitude, _freq=shake_freq, _e=easing):
            p = (t - _s) / _d
            return _a * math.sin(math.tau * _freq * p) * _e(p)
        self._apply_shift_effect(start, end, dx_func=_dx)
        return self

    def skate(self, tx: float, ty: float, start: float = 0, end: float = 1,
              degrees: float = 360, easing=easings.smooth):
        """Slide to a target position while spinning, like skating on ice."""
        if end <= start:
            return self
        self.center_to_pos(tx, ty, start=start, end=end, easing=easing)
        self.spin(start=start, end=end, degrees=degrees, easing=easing)
        return self

    def flicker(self, start: float = 0, end: float = 1, frequency: float = 8,
                min_opacity: float = 0.1, easing=easings.smooth):
        """Random-looking opacity flickering, like a failing light bulb."""
        if end <= start:
            return self
        _d = max(end - start, 1e-9)
        def _opacity(t, _s=start, _d=_d, _freq=frequency, _mo=min_opacity, _e=easing):
            p = (t - _s) / _d
            flicker = (math.sin(math.tau * _freq * p) *
                       math.sin(3.7 * math.pi * _freq * p) *
                       math.sin(5.3 * math.pi * _freq * p))
            depth = (1 - _mo) * max(0, -flicker) * (1 - _e(p))
            return 1 - depth
        self.styling.opacity.set(start, end, _opacity, stay=True)
        return self

    def slingshot(self, tx: float, ty: float, start: float = 0, end: float = 1,
                  pullback: float = 0.3, overshoot: float = 0.15,
                  easing=easings.smooth):
        """Pull back then launch toward the target with overshoot."""
        if end <= start:
            return self
        ox, oy = self.center(start)
        total_dx, total_dy = tx - ox, ty - oy
        _d = max(end - start, 1e-9)
        def _progress(t, _s=start, _d=_d, _pb=pullback, _os=overshoot, _e=easing):
            p = _e((t - _s) / _d)
            if p < 0.2:
                return -_pb * math.sin(p / 0.2 * math.pi / 2)
            elif p < 0.8:
                phase = (p - 0.2) / 0.6
                return -_pb + (-_pb - (1 + _os)) * (math.cos(phase * math.pi) - 1) / 2
            else:
                phase = (p - 0.8) / 0.2
                return (1 + _os) - _os * math.sin(phase * math.pi / 2)
        _tdx, _tdy = total_dx, total_dy
        self._apply_shift_effect(start, end,
            dx_func=lambda t, _f=_progress, _tdx=_tdx: _f(t) * _tdx,
            dy_func=lambda t, _f=_progress, _tdy=_tdy: _f(t) * _tdy,
            stay=True)
        return self

    def elastic_bounce(self, start: float = 0, end: float = 1, height=100,
                       n_bounces=3, squash_factor=1.4, easing=easings.smooth):
        """Bounce the object with squash-and-stretch deformation at each impact."""
        dur = end - start
        if dur <= 0:
            return self
        sx0, sy0 = self._init_scale_anim(start)
        _d = max(dur, 1e-9)

        def _bounce_progress(t, _s=start, _d=_d, _b=n_bounces, _easing=easing):
            """Return (vertical_offset, squash_envelope) at time t."""
            p = _easing((t - _s) / _d)
            if p >= 1.0:
                return (0.0, 0.0)
            phase = p * _b
            bounce_idx = min(int(phase), _b - 1)
            frac = phase - bounce_idx
            arc = 4 * frac * (1 - frac)
            decay = (1.0 - p) / (1 + bounce_idx)
            vert = -arc * decay
            impact = max(math.exp(-((frac * 4) ** 2)),
                         math.exp(-(((1 - frac) * 4) ** 2)))
            return (vert, impact * decay)

        self._apply_shift_effect(start, end,
            dy_func=lambda t, _h=height: _bounce_progress(t)[0] * _h)
        self.styling.scale_x.set(start, end,
            lambda t, _sf=squash_factor, _sx0=sx0: _sx0 * (1 + (_sf - 1) * _bounce_progress(t)[1]),
            stay=False)
        def _scale_y(t, _sf=squash_factor, _sy0=sy0):
            peak = 1 + (_sf - 1) * _bounce_progress(t)[1]
            return _sy0 / peak if peak > 1e-9 else _sy0
        self.styling.scale_y.set(start, end, _scale_y, stay=False)
        return self

    def _apply_scale_envelope(self, start, end, envelope, easing, stay=True):
        """Shared helper: animate scale_x/scale_y via *envelope(progress) -> multiplier*."""
        dur = end - start
        if dur <= 0:
            return self
        sx0, sy0 = self._init_scale_anim(start)
        _d = max(dur, 1e-9)
        def _make(s0):
            return lambda t, _s=start, _d=_d, _s0=s0, _e=easing, _env=envelope: \
                _s0 * _env(_e((t - _s) / _d))
        self._set_scale_xy(start, end, _make(sx0), _make(sy0), stay=stay)
        return self

    def morph_scale(self, target_scale: float = 2.0, start: float = 0, end: float = 1,
                    overshoot: float = 0.3, oscillations: int = 2,
                    easing=easings.smooth):
        """Scale to *target_scale* with a spring-like overshoot that settles."""
        _ts = target_scale
        _damp = 3.0 / max(overshoot, 0.01)
        _freq = math.tau * (oscillations + 0.25)
        def _spring(p, _ts=_ts, _damp=_damp, _freq=_freq):
            if p >= 1.0: return _ts
            if p <= 0.0: return 1.0
            return _ts + (1.0 - _ts) * math.exp(-_damp * p) * math.cos(_freq * p)
        return self._apply_scale_envelope(start, end, _spring, easing, stay=True)

    def strobe(self, start: float = 0, end: float = 1, n_flashes: int = 5,
               duty: float = 0.5):
        """Rapid hard on/off blink effect like a strobe light."""
        dur = end - start
        if dur <= 0 or n_flashes <= 0:
            return self
        duty = _clamp01(duty)
        self.styling.opacity.set(start, end,
            lambda t, _s=start, _d=dur, _fl=n_flashes, _du=duty: (
                1.0 if ((t - _s) / _d * _fl) % 1.0 < _du else 0.0),
            stay=False)
        return self

    def zoom_to(self, canvas, start: float = 0, end: float = 1,
                padding: float = 100, easing=easings.smooth):
        """Animate the camera to zoom in and focus on this object."""
        dur = end - start
        if dur <= 0:
            return self
        bx, by, bw, bh = self.bbox(start)
        target_w = bw + 2 * padding
        target_h = bh + 2 * padding
        if target_w <= 0 or target_h <= 0:
            return self
        cx, cy = bx + bw / 2, by + bh / 2
        aspect = canvas.width / canvas.height
        if target_w / target_h > aspect:
            target_h = target_w / aspect
        else:
            target_w = target_h * aspect
        target_x = cx - target_w / 2
        target_y = cy - target_h / 2
        canvas.vb_x.move_to(start, end, target_x, easing=easing)
        canvas.vb_y.move_to(start, end, target_y, easing=easing)
        canvas.vb_w.move_to(start, end, target_w, easing=easing)
        canvas.vb_h.move_to(start, end, target_h, easing=easing)
        return self

    def typewriter_delete(self, start: float = 0, end: float = 1,
                          direction='right', easing=easings.smooth):
        """Clip-path sweep hide (reverse of typewriter_reveal)."""
        return self._typewriter_clip(start, end, direction, easing, reveal=False)

    def domino(self, start: float = 0, end: float = 1, direction='right',
               angle: float = 90, easing=easings.smooth):
        """Tip the object over like a falling domino, rotating around its bottom edge."""
        dur = end - start
        if dur <= 0:
            return self
        self._hide_from(end)
        bx, by, bw, bh = self.bbox(start)
        if direction == 'left':
            pivot_x, pivot_y, target_angle = bx, by + bh, -angle
        else:
            pivot_x, pivot_y, target_angle = bx + bw, by + bh, angle
        _d = max(dur, 1e-9)
        self.styling.rotation.set(start, end,
            lambda t, _s=start, _d=_d, _ta=target_angle, _px=pivot_x, _py=pivot_y, _e=easing: (
                _ta * _e((t - _s) / _d), _px, _py),
            stay=True)
        return self

    def stamp_trail(self, start: float = 0, end: float = 1, count=8,
                    fade_duration=0.5, opacity=0.4):
        """Leave ghostly fading copies along the path. Returns a list of ghost VObjects."""
        ghosts = []
        dur = end - start
        if dur <= 0 or count <= 0:
            return ghosts
        for i in range(count):
            t_appear = start + dur * (i + 1) / (count + 1)
            ghost = deepcopy(self)
            _apply_pos_offset(ghost, t_appear, 0, 0)
            ghost.show.set_onward(0, False)
            ghost.show.set_onward(t_appear, True)
            t_gone = t_appear + fade_duration
            ghost.show.set_onward(t_gone, False)
            fd = max(fade_duration, 1e-9)
            fade_fn = lambda t, _s=t_appear, _fd=fd, _o=opacity: _o * max(0, 1 - (t - _s) / _fd)
            ghost.styling.fill_opacity.set(t_appear, t_gone, fade_fn)
            ghost.styling.stroke_opacity.set(t_appear, t_gone, fade_fn)
            ghosts.append(ghost)
        return ghosts

    def unfold(self, start: float = 0, end: float = 1, direction='right',
               change_existence=True, easing=easings.smooth):
        """Animate the object unfolding from zero width to full size along one axis."""
        dur = end - start
        if dur <= 0:
            return self
        if change_existence:
            self._show_from(start)
        bx, by, bw, bh = self.bbox(start)
        cx, cy = bx + bw / 2, by + bh / 2
        horizontal = direction in ('left', 'right')
        if direction == 'right':
            self.styling._scale_origin = (bx, cy)
        elif direction == 'left':
            self.styling._scale_origin = (bx + bw, cy)
        elif direction == 'down':
            self.styling._scale_origin = (cx, by)
        else:
            self.styling._scale_origin = (cx, by + bh)
        scale_fn = _ramp(start, dur, 1, easing)
        if horizontal:
            self.styling.scale_x.set(start, end, scale_fn, stay=True)
        else:
            self.styling.scale_y.set(start, end, scale_fn, stay=True)
        return self

    def glitch_shift(self, start: float = 0, end: float = 1, intensity=20,
                     steps=8, seed=None):
        """Random discrete horizontal displacement jumps simulating a digital glitch."""
        import random
        dur = end - start
        if dur <= 0 or steps <= 0:
            return self
        rng = random.Random(seed)
        step_dur = dur / steps
        for i in range(steps):
            t0 = start + i * step_dur
            t1 = t0 + step_dur
            dx = rng.uniform(-intensity, intensity)
            for xa, _ in self._shift_reals():
                xa.add(t0, t1, lambda _t, _dx=dx: _dx, stay=False)
            for c in self._shift_coors():
                c.add(t0, t1, lambda _t, _dx=dx: (_dx, 0), stay=False)
        return self

    @staticmethod
    def _make_parabolic_wave(start, _d, amplitude, frequency, easing, wave_func=None):
        """Build a closure for parabolic-envelope sinusoidal displacement."""
        wf = wave_func or math.sin
        def _wave(t, _s=start, _d=_d, _a=amplitude, _freq=frequency, _e=easing, _wf=wf):
            p = (t - _s) / _d
            envelope = _e(p) * (1 - _e(p)) * 4
            return _a * _wf(math.tau * _freq * p) * envelope
        return _wave

    def wave_through(self, start: float = 0, end: float = 1, amplitude=20,
                     frequency=2, direction='y', easing=easings.smooth):
        """Sinusoidal oscillation along the given axis with a fading envelope."""
        dur = end - start
        if dur <= 0:
            return self
        _wave = self._make_parabolic_wave(start, max(dur, 1e-9), amplitude, frequency, easing)
        kw = {'dy_func': _wave} if direction == 'y' else {'dx_func': _wave}
        return self._apply_shift_effect(start, end, **kw)

    def countdown(self, start: float = 0, end: float = 1, from_val=3):
        """For Text objects: display a countdown from *from_val* to 1."""
        _ensure_text(self, 'countdown')
        dur = end - start
        if dur <= 0 or from_val < 1:
            return self
        step_dur = dur / from_val
        for i in range(from_val):
            self.text.set_onward(start + i * step_dur, str(from_val - i))
        return self

    def squeeze(self, start: float = 0, end: float = 1, axis='x',
                factor=0.5, easing=easings.smooth):
        """Squeeze the object along one axis, scaling up the other to preserve area."""
        dur = end - start
        if dur <= 0:
            return self
        sx0, sy0 = self._init_scale_anim(start)
        _d = max(dur, 1e-9)
        compensate = 1.0 / factor if factor > 1e-9 else 1.0

        def _sq(s0, f):
            return lambda t, _s=start, _d=_d, _s0=s0, _f=f, _e=easing: \
                _s0 * (1 + (_f - 1) * _e((t - _s) / _d))
        fx, fy = (factor, compensate) if axis == 'x' else (compensate, factor)
        self._set_scale_xy(start, end, _sq(sx0, fx), _sq(sy0, fy), stay=True)
        return self

    def bind_to(self, other, offset_x=0, offset_y=0, start: float = 0, end: float | None = None):
        """Keep this object at a fixed offset relative to another object's center."""
        def _bind(obj, time, _other=other, _ox=offset_x, _oy=offset_y):
            ocx, ocy = _other.center(time)
            scx, scy = obj.center(time)
            dx = ocx + _ox - scx
            dy = ocy + _oy - scy
            if abs(dx) > 0.01 or abs(dy) > 0.01:
                _apply_pos_offset(obj, time, dx, dy)
        self.add_updater(_bind, start, end)
        return self

    def pin_to(self, other, edge='center', offset_x=0, offset_y=0, start: float = 0, end: float | None = None):
        """Anchor this object to a specific edge/corner of *other* via an updater."""
        edge_fn = _EDGE_POINTS.get(edge, _EDGE_POINTS['center'])

        def _pin(obj, time, _other=other, _edge_fn=edge_fn,
                 _ox=offset_x, _oy=offset_y):
            bx, by, bw, bh = _other.bbox(time)
            ex, ey = _edge_fn(bx, by, bw, bh)
            target_x = ex + _ox
            target_y = ey + _oy
            sx, sy, sw, sh = obj.bbox(time)
            dx = target_x - (sx + sw / 2)
            dy = target_y - (sy + sh / 2)
            if abs(dx) > 0.01 or abs(dy) > 0.01:
                _apply_pos_offset(obj, time, dx, dy)

        self.add_updater(_pin, start, end)
        return self

    def duplicate(self, count=2, direction=RIGHT, buff=MED_SMALL_BUFF):
        """Create count copies of the object arranged in the given direction.
        Returns a VCollection containing the copies (not including self)."""
        from vectormation._collection import VCollection
        col = VCollection(*[deepcopy(self) for _ in range(count)])
        col.arrange(direction=direction, buff=buff)
        return col

    arc_to = lambda self, *a, **kw: self.path_arc(*a, **kw)
    arc_to.__doc__ = """Alias for :meth:`path_arc`."""

    def typewriter_cursor(self, start: float = 0, end: float = 1, blink_rate=0.5, cursor_char='|'):
        """For Text objects: append a blinking cursor character."""
        _ensure_text(self, 'typewriter_cursor')
        _base_text_func = self.text.time_func
        def _blink(t, _s=start, _rate=blink_rate, _char=cursor_char, _base=_base_text_func):
            base = _base(t)
            if int((t - _s) / _rate) % 2 == 0:
                return base + _char
            return base
        self.text.set(start, end, _blink, stay=False)
        return self

    def parallax(self, dx, dy, start: float = 0, end: float = 1, depth_factor=0.5, easing=easings.smooth):
        """Shift by a fraction of (dx, dy) to create a parallax depth illusion."""
        return self.shift(dx=dx * depth_factor, dy=dy * depth_factor,
                          start=start, end=end, easing=easing)

    _DASH_PRESETS = {
        'solid': '',
        'dashes': '10 5',
        'dots': '2 4',
        'dash_dot': '10 5 2 5',
    }

    def set_dash_pattern(self, pattern='dashes', start: float = 0):
        """Set the stroke-dasharray at a given time. Accepts preset names or a custom string."""
        self.styling.stroke_dasharray.set_onward(start, self._DASH_PRESETS.get(pattern, pattern))
        return self

    def show_if(self, condition_func, start: float = 0, end: float | None = None):
        """Show the object only when *condition_func(time)* returns True."""
        def _opacity(t):
            return 1 if condition_func(t) else 0
        self.styling.opacity.set_onward(start, _opacity)
        self.styling.fill_opacity.set_onward(start, _opacity)
        if end is not None:
            self.styling.opacity.set_onward(end, self.styling.opacity.at_time(end))
            self.styling.fill_opacity.set_onward(end, self.styling.fill_opacity.at_time(end))
        return self

    @staticmethod
    def surround(other, buff=SMALL_BUFF, rx=6, ry=6, start: float = 0, follow=True):
        """Create a rectangle surrounding another object. Returns a Rectangle."""
        return _make_brect(other.bbox, start, rx, ry, buff, follow)

    def fade_to_color(self, target_color, start: float = 0, end: float = 1, easing=easings.smooth):
        """Smoothly transition both fill and stroke to *target_color*."""
        return self.set_fill(color=target_color, start=start, end=end, easing=easing) \
            .set_stroke(color=target_color, start=start, end=end, easing=easing)

    def spin_and_fade(self, start: float = 0, end: float = 1, spins=1.5, direction=1, easing=easings.smooth):
        """Rotate and fade out simultaneously."""
        return self.rotate_by(start, end, spins * 360 * direction, easing=easing) \
            .set_opacity(0, start=start, end=end, easing=easing)

    def grow_to_size(self, target_width=None, target_height=None, start: float = 0, end: float = 1, easing=easings.smooth):
        """Animate the object to reach a specific width and/or height."""
        cur_w = self.get_width(start)
        cur_h = self.get_height(start)
        if target_width is not None and target_height is not None:
            if cur_w > 0 and cur_h > 0:
                self.stretch(target_width / cur_w, target_height / cur_h,
                             start=start, end=end, easing=easing)
        elif target_width is not None:
            if cur_w > 0:
                self.scale(target_width / cur_w, start=start, end=end, easing=easing)
        elif target_height is not None:
            if cur_h > 0:
                self.scale(target_height / cur_h, start=start, end=end, easing=easing)
        return self

    def tilt_towards(self, target_x, target_y, max_angle=15, start: float = 0, end: float = 1, easing=easings.smooth):  # noqa: ARG002
        """Rotate the object to tilt toward a target point by *max_angle* degrees.
        The vertical offset (target_y) determines tilt direction; target_x is accepted
        for API consistency (pass a point, not just a y-coordinate)."""
        _, cy = self.center(start)
        tilt = max_angle if target_y - cy >= 0 else -max_angle
        self.rotate_by(start, end, tilt, easing=easing)
        return self

    # -- Blend mode --

    _VALID_BLEND_MODES = frozenset({
        'normal', 'multiply', 'screen', 'overlay', 'darken', 'lighten',
        'color-dodge', 'color-burn',
    })

    def set_blend_mode(self, mode, start: float = 0):
        """Set the SVG mix-blend-mode on this object."""
        if mode not in self._VALID_BLEND_MODES:
            raise ValueError(
                f"Unsupported blend mode '{mode}'. "
                f"Must be one of: {', '.join(sorted(self._VALID_BLEND_MODES))}"
            )
        self.styling.mix_blend_mode.set_onward(start, mode)
        return self

    # -- Reveal clip --

    # Maps reveal_clip direction names to _CLIP_INSET keys.
    # 'left' (reveal left→right) clips the right side, etc.
    _REVEAL_DIR = {'left': 'right', 'right': 'left', 'top': 'down', 'bottom': 'up'}

    def reveal_clip(self, start: float = 0, end: float = 1, direction='left', easing=easings.smooth):
        """Progressive reveal using SVG clip-path in the given direction."""
        dur = end - start
        if dur <= 0:
            return self
        self._show_from(start)
        key = self._REVEAL_DIR.get(direction)
        if key is None:
            raise ValueError(
                f"Unsupported reveal direction '{direction}'. "
                f"Must be one of: {', '.join(sorted(self._REVEAL_DIR))}"
            )
        self.styling.clip_path.set(start, end,
            _clip_reveal(self._CLIP_INSET[key], start, max(dur, 1e-9), easing), stay=True)
        return self

    # -- Repeat animation --

    def repeat_animation(self, method_name, count=2, start: float = 0, end: float = 1, **kwargs):
        """Repeat an animation method *count* times within [start, end]."""
        if count <= 0 or end <= start:
            return self
        slice_dur = (end - start) / count
        method = getattr(self, method_name)
        for i in range(count):
            s = start + i * slice_dur
            method(start=s, end=s + slice_dur, **kwargs)
        return self

    # -- Elastic scale --

    def elastic_scale(self, start: float = 0, end: float = 1, factor=1.5, easing=easings.smooth):
        """Scale up elastically then bounce back to original size."""
        _f, _damp, _freq = factor, 6.0, math.tau * 2.5
        def _elastic(p, _f=_f, _damp=_damp, _freq=_freq):
            if p <= 0: return 1.0
            if p >= 1: return 1.0
            return 1 + (_f - 1) * math.cos(_freq * p) * math.exp(-_damp * p)
        return self._apply_scale_envelope(start, end, _elastic, easing, stay=True)

    def snap_to_grid(self, grid_size=50, start: float = 0, end: float = 1, easing=easings.smooth):
        """Animate the object's center to the nearest grid point."""
        cx, cy = self.center(start)
        target_x = round(cx / grid_size) * grid_size
        target_y = round(cy / grid_size) * grid_size
        dx, dy = target_x - cx, target_y - cy
        if dx != 0 or dy != 0:
            self.shift(dx=dx, dy=dy, start=start, end=end, easing=easing)
        return self

    def add_background(self, color='#000000', opacity=0.5, padding=20, creation=0, z=-1):
        """Create a semi-transparent Rectangle behind the object as a readability backdrop."""
        from vectormation._shapes import Rectangle
        x, y, w, h = self.bbox(creation)
        return Rectangle(
            width=w + 2 * padding,
            height=h + 2 * padding,
            x=x - padding,
            y=y - padding,
            creation=creation,
            z=z,
            fill=color,
            fill_opacity=opacity,
            stroke_width=0,
        )

    def cycle_colors(self, colors, start: float = 0, end: float = 1, easing=easings.linear):
        """Cycle the fill color through a list of colors over [start, end]."""
        dur = end - start
        if dur <= 0 or len(colors) < 2:
            return self
        n = len(colors)
        parsed = [attributes.Color(0, '#000').parse(c)[1] for c in colors]
        self.set_fill(color=colors[0], start=start)
        src = self.styling.fill
        def _make_interp(_cf, _ct, _ss, _dd, _easing):
            return lambda t: tuple(
                cf_v + (ct_v - cf_v) * _easing((t - _ss) / _dd)
                for cf_v, ct_v in zip(_cf, _ct))
        for i in range(n - 1):
            seg_s = start + dur * i / (n - 1)
            seg_e = start + dur * (i + 1) / (n - 1)
            _d = max(seg_e - seg_s, 1e-9)
            src.set(seg_s, seg_e, _make_interp(parsed[i], parsed[i + 1], seg_s, _d, easing),
                    stay=(i == n - 2))
        return self

    def freeze(self, start, end: float | None = None):
        """Freeze the object's appearance at time *start* until *end*."""
        _captured = {}

        def _capture(obj, t):
            if not _captured:
                for name, _, cls, _, _ in style._ATTR_SCHEMA:
                    _captured[name] = getattr(obj.styling, name).at_time(start)
                _captured['_z'] = obj.z.at_time(start)
            for name, _, cls, _, _ in style._ATTR_SCHEMA:
                val = _captured[name]
                attr = getattr(obj.styling, name)
                if cls is attributes.Color:
                    attr.set_onward(t, lambda _t, _v=val: _v)  # noqa: pyright
                else:
                    attr.set_onward(t, val)
            obj.z.set_onward(t, _captured['_z'])

        self.add_updater(_capture, start, end)
        return self

    def delay_animation(self, method_name, delay, *args, **kwargs):
        """Schedule an animation to start after a delay."""
        import inspect
        method = getattr(self, method_name)
        params = inspect.signature(method).parameters
        if 'start' in params:
            kwargs['start'] = kwargs.get('start', 0) + delay
        if 'end' in params:
            end_val = kwargs.get('end', params['end'].default)
            if end_val is not None and end_val is not inspect.Parameter.empty:
                kwargs['end'] = end_val + delay
        method(*args, **kwargs)
        return self

    def wobble(self, start: float = 0, end: float = 1, amplitude=5, frequency=3, easing=easings.smooth):
        """Organic wobbling motion combining small rotations and position shifts."""
        dur = end - start
        if dur <= 0:
            return self
        _d = max(dur, 1e-9)

        def _dx(t, _s=start, _d=_d, _a=amplitude, _freq=frequency, _easing=easing):
            p = (t - _s) / _d
            return _a * math.sin(math.tau * _freq * p) * (1 - _easing(p))

        def _dy(t, _s=start, _d=_d, _a=amplitude, _freq=frequency, _easing=easing):
            p = (t - _s) / _d
            return _a * 0.7 * math.sin(math.tau * _freq * 1.3 * p) * (1 - _easing(p))

        self._apply_shift_effect(start, end, dx_func=_dx, dy_func=_dy)
        cx, cy = self.center(start)
        def _rot(t, _s=start, _d=_d, _a=amplitude, _freq=frequency, _cx=cx, _cy=cy, _easing=easing):
            p = (t - _s) / _d
            return (_a * math.sin(math.tau * _freq * 0.7 * p) * (1 - _easing(p)), _cx, _cy)
        self.styling.rotation.set(start, end, _rot)
        return self

    def focus_zoom(self, start: float = 0, end: float = 1, zoom_factor=1.3, easing=easings.smooth):
        """Zoom in slightly on the object then back to normal, like a camera focus effect."""
        return self.flash_scale(factor=zoom_factor, start=start, end=end, easing=easing)

    def typewriter_effect(self, text, start: float = 0, end: float = 1, easing=easings.linear):
        """For Text objects only: gradually reveal text character by character."""
        _ensure_text(self, 'typewriter_effect')
        n = len(text)
        if n == 0 or end <= start:
            return self
        _d = max(end - start, 1e-9)
        def _reveal(t, _s=start, _d=_d, _txt=text, _n=n, _easing=easing):
            return _txt[:int(min(1.0, _easing((t - _s) / _d)) * _n)]
        self.text.set(start, end, _reveal, stay=True)
        self.text.set_onward(end, text)
        return self

    def look_at(self, target, start: float = 0, end: float | None = None, easing=None):
        """Rotate so this object points toward *target*."""
        easing = easing or easings.smooth
        tx, ty = target if isinstance(target, tuple) else target.get_center(start)
        cx, cy = self.get_center(start)
        angle_deg = math.degrees(math.atan2(ty - cy, tx - cx))
        return self.rotate_to(start, end or start, angle_deg, easing=easing)

    def animate_to(self, target_obj, start: float = 0, end: float = 1, easing=None):
        """Animate position, scale, and colors to match *target_obj*."""
        easing = easing or easings.smooth
        tx, ty = target_obj.get_center(start)
        self.center_to_pos(posx=tx, posy=ty, start=start, end=end, easing=easing)
        tw = target_obj.get_width(start)
        cur_w = self.get_width(start)
        if cur_w > 0 and tw > 0:
            self.scale(tw / cur_w, start=start, end=end, easing=easing)
        target_fill = target_obj.styling.fill.time_func(start)
        if target_fill:
            self.set_color(start, end, fill=self._rgb_to_hex(target_fill), easing=easing)
        target_stroke = target_obj.styling.stroke.time_func(start)
        if target_stroke:
            self.set_color(start, end, stroke=self._rgb_to_hex(target_stroke), easing=easing)
        return self

    def set_gradient_fill(self, colors, direction='horizontal', start: float = 0):
        """Apply an SVG gradient fill to this object."""
        gid = f'grad{id(self)}'
        n = len(colors)
        stops = ''.join(
            f"<stop offset='{i / max(n - 1, 1) * 100}%' stop-color='{c}'/>"
            for i, c in enumerate(colors)
        )
        if direction == 'radial':
            grad_def = f"<radialGradient id='{gid}'>{stops}</radialGradient>"
        else:
            x1, y1, x2, y2 = (0, 0, 0, 1) if direction == 'vertical' else (0, 0, 1, 0)
            grad_def = (
                f"<linearGradient id='{gid}' x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}'>"
                f"{stops}</linearGradient>"
            )
        _wrap_to_svg(self, lambda inner, _t, _g=gid, _d=grad_def:
                     f"<g><defs>{_d}</defs><g fill='url(#{_g})'>{inner}</g></g>", start)
        return self

    def set_clip(self, clip_obj, start: float = 0):
        """Apply an SVG clip-path from another VObject's outline."""
        cid = f'clip{id(self)}'
        _wrap_to_svg(self, lambda inner, t, _c=cid, _cl=clip_obj:
                     f"<g clip-path='url(#{_c})'><defs><clipPath id='{_c}'>"
                     f"{_cl.to_svg(t)}</clipPath></defs>{inner}</g>", start)
        return self

    def set_lifetime(self, start, end):
        """Set bounded visibility: visible only from *start* to *end*."""
        self.set_visible(False, 0); self.set_visible(True, start); self.set_visible(False, end)
        return self

    def get_style(self, time: float = 0):
        """Return the current styling as a dict at the given time."""
        return {
            'fill': self.styling.fill.at_time(time),
            'stroke': self.styling.stroke.at_time(time),
            'fill_opacity': self.styling.fill_opacity.at_time(time),
            'stroke_opacity': self.styling.stroke_opacity.at_time(time),
            'stroke_width': self.styling.stroke_width.at_time(time),
            'opacity': self.styling.opacity.at_time(time),
        }

    def move_towards(self, other, fraction=0.5, start: float = 0, end: float | None = None, easing=None):
        """Move a fraction of the way toward another object or point."""
        cx, cy = self.get_center(start)
        tx, ty = _coords_of(other, start)
        return self.center_to_pos(posx=cx + fraction * (tx - cx),
            posy=cy + fraction * (ty - cy), start=start, end=end, easing=easing or easings.smooth)

    def add_label(self, text, direction=UP, buff=20, font_size=None, follow=False, creation=0, **kwargs):
        """Attach a text label next to this object. Returns a VCollection(self, label)."""
        from vectormation._shapes import Text as _Text
        label_kwargs = dict(creation=creation)
        if font_size is not None:
            label_kwargs['font_size'] = font_size
        label_kwargs.update(kwargs)
        label = _Text(text, **label_kwargs)
        label.next_to(self, direction, buff, start=creation)
        if follow:
            def _follow_updater(lbl, t, _parent=self, _d=direction, _b=buff):
                lbl.next_to(_parent, _d, _b, start=t)
            label.add_updater(_follow_updater, start=creation)
        from vectormation._collection import VCollection
        return VCollection(self, label)

    def place_between(self, obj_a, obj_b, fraction=0.5, start: float = 0, end: float | None = None, easing=None):
        """Position this object between two other objects or points."""
        ax, ay = _coords_of(obj_a, start)
        bx, by = _coords_of(obj_b, start)
        return self.center_to_pos(
            posx=(1 - fraction) * ax + fraction * bx,
            posy=(1 - fraction) * ay + fraction * by,
            start=start, end=end, easing=easing or easings.smooth)

    def homotopy(self, func, start: float = 0, end: float = 1):
        """Apply a continuous point-wise transformation *func(x, y, t) -> (x', y')* over time."""
        dur = end - start
        if dur <= 0:
            return self
        for c in self._shift_coors():
            orig = c.at_time(start)
            ox, oy = float(orig[0]), float(orig[1])
            def _h(t, _s=start, _d=dur, _ox=ox, _oy=oy, _f=func):
                return _f(_ox, _oy, min(1.0, (t - _s) / _d))
            c.set(start, end, _h, stay=True)
            fx, fy = func(ox, oy, 1.0)
            c.set_onward(end, (fx, fy))
        for rx, ry in self._shift_reals():
            ox, oy = float(rx.at_time(start)), float(ry.at_time(start))
            def _hi(idx, _s=start, _d=dur, _ox=ox, _oy=oy, _f=func):
                return lambda t: _f(_ox, _oy, min(1.0, (t - _s) / _d))[idx]
            rx.set(start, end, _hi(0), stay=True)
            ry.set(start, end, _hi(1), stay=True)
            fx, fy = func(ox, oy, 1.0)
            rx.set_onward(end, fx); ry.set_onward(end, fy)
        return self

    def apply_wave(self, start: float = 0, end: float = 1, amplitude: float = 30,
                   wave_func=None, direction='y', easing=easings.smooth):
        """Apply a sinusoidal wave distortion that travels across the object.

        The wave sweeps from left to right (or top to bottom), displacing
        each point perpendicular to the sweep direction. At start and end
        the object returns to its original shape (there-and-back).

        *wave_func* can customize the wave shape; default is ``sin``.
        """
        dur = end - start
        if dur <= 0:
            return self
        _wave = self._make_parabolic_wave(start, max(dur, 1e-9), amplitude, 2, easing, wave_func)
        kw = {'dy_func': _wave} if direction == 'y' else {'dx_func': _wave}
        self._apply_shift_effect(start, end, **kw)
        return self

    def scale_in_place(self, factor, start: float = 0, end: float = 1, easing=easings.smooth):
        """Scale the object without moving its center (anchored at current center)."""
        self._ensure_scale_origin(start)
        return self.scale(factor, start=start, end=end, easing=easing)

    def passing_flash(self, start: float = 0, end: float = 1, width: float = 0.15,
                      color=None, easing=easings.linear):
        """Flash a bright swoosh along the object's stroke (ShowPassingFlash equivalent).

        A short glowing segment travels along the stroke path, creating a
        swoosh/sparkle effect. Uses animated stroke-dashoffset to sweep
        a bright dash along the outline.

        Parameters
        ----------
        start, end : float
            Time interval for the animation.
        width : float
            Fraction of the path that is illuminated (0 < width < 1).
        color : str or None
            Override stroke color during the flash.
        easing : callable
            Easing function.
        """
        dur = end - start
        if dur <= 0:
            return self
        _d = max(dur, 1e-9)
        _w = max(0.01, min(width, 0.99))
        # Approximate path length for dash array sizing
        _path_len = 4000  # generous upper bound for SVG viewbox
        _dash = _path_len * _w
        _gap = _path_len * (1 - _w)
        # Set dash array: one short visible dash + one long gap
        self.styling.stroke_dasharray.set_onward(start, f'{_dash:.0f} {_gap:.0f}')
        # Animate dash offset from +path_len to -path_len
        self.styling.stroke_dashoffset.set_onward(start,
            lambda t, _s=start, _d=_d, _e=easing, _pl=_path_len:
                _pl * (1 - 2 * _e((t - _s) / _d)) if _s <= t <= _s + _d else 0)
        # Flash visibility
        self._show_from(start)
        self._hide_from(end)
        if color:
            self.styling.stroke.set_onward(start, color)
        return self

# VCollection moved to _collection.py; re-export for backward compatibility.
