"""Advanced animation methods for VObject (mixed in as a base class)."""
import math
from copy import deepcopy

import vectormation.easings as easings
import vectormation.attributes as attributes
import vectormation.style as style
from vectormation._base_helpers import (
    _lerp, _ramp, _ramp_down, _lerp_point, _clip_reveal,
    _norm_dir, _norm_edge, _coords_of, _set_attr, _parse_path,
    _make_brect, _EDGE_POINTS,
)
from vectormation._constants import (
    UP, DOWN, LEFT, RIGHT, UL, UR, DL, DR,
    SMALL_BUFF, MED_SMALL_BUFF,
)

class _VObjectEffectsMixin:
    """Advanced animation and effect methods, mixed into VObject."""
    def scale_to_fit(self, width=None, height=None, start=0, end=None, easing=easings.smooth):
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
        factor = min(factors)
        return self.scale(factor, start=start, end=end, easing=easing)

    def match_position(self, other, time: float = 0):
        """Move this object so its center matches *other*'s center at *time*."""
        ox, oy = _coords_of(other, time)
        return self.move_to(ox, oy, start=time)

    def point_from_proportion(self, t, time=0):
        """Return the (x, y) point at proportion *t* (0-1) along this object's SVG path outline."""
        path_d = self.path(time)
        if not path_d:
            return self.center(time)
        parsed, total_length = _parse_path(path_d)
        if total_length <= 0:
            pt = parsed.point(0)
            return (pt.real, pt.imag)
        t = max(0.0, min(1.0, t))
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

    def match_style(self, other, time=0):
        """Copy fill, stroke, opacity, and stroke_width from *other* at *time*."""
        # Copy fill and stroke colors using set_onward to preserve earlier animations
        self.styling.fill.set_onward(time, other.styling.fill.time_func(time))
        self.styling.stroke.set_onward(time, other.styling.stroke.time_func(time))
        # Copy numeric styling attributes
        self.styling.fill_opacity.set_onward(time, other.styling.fill_opacity.at_time(time))
        self.styling.stroke_opacity.set_onward(time, other.styling.stroke_opacity.at_time(time))
        self.styling.stroke_width.set_onward(time, other.styling.stroke_width.at_time(time))
        return self

    def telegraph(self, start: float = 0, duration: float = 0.4,
                  scale_factor: float = 1.4, shake_amplitude: float = 8,
                  easing=easings.there_and_back):
        """Quick attention-grabbing burst: scale spike + shake + opacity dip."""
        if duration <= 0:
            return self
        end = start + duration
        self._ensure_scale_origin(start)
        _s, _d = start, max(duration, 1e-9)
        # Scale spike
        scale_fn = _lerp(_s, _d, 1, scale_factor, easing)
        self.styling.scale_x.set(_s, end, scale_fn)
        self.styling.scale_y.set(_s, end, scale_fn)
        # Opacity dip (brief dim at peak)
        self.styling.opacity.set(_s, end, _lerp(_s, _d, 1, 0.7, easing))
        # Rapid horizontal shake
        shake_freq = 12
        def _dx(t, _s=_s, _d=_d, _a=shake_amplitude, _freq=shake_freq, _e=easing):
            p = (t - _s) / _d
            return _a * math.sin(_freq * math.tau * p) * _e(p)
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
        _s, _d, _freq, _mo = start, max(end - start, 1e-9), frequency, min_opacity
        def _opacity(t, _s=_s, _d=_d, _freq=_freq, _mo=_mo, _e=easing):
            p = (t - _s) / _d
            # Layered sine waves for pseudo-random flicker
            flicker = (math.sin(_freq * math.tau * p) *
                       math.sin(_freq * 3.7 * math.pi * p) *
                       math.sin(_freq * 5.3 * math.pi * p))
            # flicker is in [-1, 1]; map to [min_opacity, 1]
            # Envelope decays toward end so object returns to full opacity
            envelope = 1 - _e(p)
            depth = (1 - _mo) * max(0, -flicker) * envelope
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
        _s, _d = start, max(end - start, 1e-9)
        _pb, _os = pullback, overshoot
        _tdx, _tdy = total_dx, total_dy
        def _progress(t, _s=_s, _d=_d, _pb=_pb, _os=_os, _e=easing):
            p = _e((t - _s) / _d)
            # Three phases: pullback (0-0.2), launch (0.2-0.8), settle (0.8-1.0)
            if p < 0.2:
                # Pull back: go from 0 to -pullback
                return -_pb * math.sin(p / 0.2 * math.pi / 2)
            elif p < 0.8:
                # Launch: go from -pullback to (1 + overshoot)
                phase = (p - 0.2) / 0.6
                return -_pb + (-_pb - (1 + _os)) * (math.cos(phase * math.pi) - 1) / 2
            else:
                # Settle: go from (1 + overshoot) to 1
                phase = (p - 0.8) / 0.2
                return (1 + _os) - _os * math.sin(phase * math.pi / 2)
        def _dx(t, _f=_progress, _tdx=_tdx):
            return _f(t) * _tdx
        def _dy(t, _f=_progress, _tdy=_tdy):
            return _f(t) * _tdy
        self._apply_shift_effect(start, end, dx_func=_dx, dy_func=_dy, stay=True)
        return self

    def elastic_bounce(self, start: float = 0, end: float = 1, height=100,
                       bounces=3, squash_factor=1.4, easing=easings.smooth):
        """Bounce the object with squash-and-stretch deformation at each impact."""
        dur = end - start
        if dur <= 0:
            return self
        sx0, sy0 = self._init_scale_anim(start)
        _s, _d = start, max(dur, 1e-9)
        _h, _b, _sf = height, bounces, squash_factor
        _sx0, _sy0 = sx0, sy0

        def _bounce_progress(t, _s=_s, _d=_d, _b=_b, _easing=easing):
            """Return (vertical_offset, squash_envelope) at time t.
            vertical_offset: 0 at ground, negative upward.
            squash_envelope: 0 normally, peaks at 1.0 at impact moments."""
            p = _easing((t - _s) / _d)
            if p >= 1.0:
                return (0.0, 0.0)
            # Each bounce occupies a segment; amplitude decays
            phase = p * _b
            bounce_idx = min(int(phase), _b - 1)
            frac = phase - bounce_idx  # 0..1 within each bounce
            # Parabolic arc within each bounce: y = 4*frac*(1-frac) gives 0→1→0
            arc = 4 * frac * (1 - frac)
            # Decay: each bounce is smaller; also fade out near end
            decay = (1.0 - p) / (1 + bounce_idx)
            vert = -arc * decay
            # Squash peaks at impact (frac near 0 or 1)
            # Use a narrow bell curve at frac=0 and frac=1
            impact = max(math.exp(-((frac * 4) ** 2)),
                         math.exp(-(((1 - frac) * 4) ** 2)))
            squash = impact * decay
            return (vert, squash)

        def _dy(t, _h=_h):
            vert, _ = _bounce_progress(t)
            return vert * _h

        def _ssx(t, _sf=_sf, _sx0=_sx0):
            _, squash = _bounce_progress(t)
            return _sx0 * (1 + (_sf - 1) * squash)

        def _ssy(t, _sf=_sf, _sy0=_sy0):
            _, squash = _bounce_progress(t)
            peak = 1 + (_sf - 1) * squash
            return _sy0 / peak if peak > 1e-9 else _sy0

        self._apply_shift_effect(start, end, dy_func=_dy)
        self.styling.scale_x.set(start, end, _ssx, stay=False)
        self.styling.scale_y.set(start, end, _ssy, stay=False)
        return self

    def morph_scale(self, target_scale: float = 2.0, start: float = 0, end: float = 1,
                    overshoot: float = 0.3, oscillations: int = 2,
                    easing=easings.smooth):
        """Scale to *target_scale* with a spring-like overshoot that settles."""
        dur = end - start
        if dur <= 0:
            return self
        sx0, sy0 = self._init_scale_anim(start)
        _s, _d = start, max(dur, 1e-9)
        _ts, _os, _osc = target_scale, overshoot, oscillations
        _sx0, _sy0 = sx0, sy0

        # Map overshoot to damping: higher overshoot -> lower damping -> more ring
        _damp = 3.0 / max(_os, 0.01)
        _freq = math.tau * (_osc + 0.25)

        def _spring_curve(p, _ts=_ts, _damp=_damp, _freq=_freq):
            """Map progress p in [0,1] to a scale multiplier that overshoots
            *_ts* and settles at *_ts*.
            Uses a classic damped oscillation: target + (1-target)*exp(-d*p)*cos(f*p).
            At p=0 this equals 1.0 (original); it decays toward target."""
            if p >= 1.0:
                return _ts
            if p <= 0.0:
                return 1.0
            return _ts + (1.0 - _ts) * math.exp(-_damp * p) * math.cos(_freq * p)

        def _msx(t, _s=_s, _d=_d, _sx0=_sx0, _easing=easing, _sc=_spring_curve):
            p = _easing((t - _s) / _d)
            return _sx0 * _sc(p)

        def _msy(t, _s=_s, _d=_d, _sy0=_sy0, _easing=easing, _sc=_spring_curve):
            p = _easing((t - _s) / _d)
            return _sy0 * _sc(p)

        self.styling.scale_x.set(start, end, _msx, stay=True)
        self.styling.scale_y.set(start, end, _msy, stay=True)
        return self

    def strobe(self, start: float = 0, end: float = 1, flashes: int = 5,
               duty: float = 0.5):
        """Rapid hard on/off blink effect like a strobe light."""
        dur = end - start
        if dur <= 0 or flashes <= 0:
            return self
        duty = max(0.0, min(1.0, duty))
        _s, _d, _fl, _du = start, dur, flashes, duty

        def _opacity(t, _s=_s, _d=_d, _fl=_fl, _du=_du):
            p = (t - _s) / _d
            cycle_pos = (p * _fl) % 1.0
            return 1.0 if cycle_pos < _du else 0.0

        self.styling.opacity.set(start, end, _opacity, stay=False)
        return self

    def zoom_to(self, canvas, start: float = 0, end: float = 1,
                padding: float = 100, easing=easings.smooth):
        """Animate the camera to zoom in and focus on this object."""
        dur = end - start
        if dur <= 0:
            return self
        bx, by, bw, bh = self.bbox(start)
        target_x = bx - padding
        target_y = by - padding
        target_w = bw + 2 * padding
        target_h = bh + 2 * padding
        if target_w <= 0 or target_h <= 0:
            return self
        # Maintain canvas aspect ratio
        cx, cy = bx + bw / 2, by + bh / 2
        aspect = canvas.width / canvas.height
        if target_w / target_h > aspect:
            target_h = target_w / aspect
            target_y = cy - target_h / 2
        else:
            target_w = target_h * aspect
            target_x = cx - target_w / 2
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
            pivot_x = bx
            pivot_y = by + bh
            target_angle = -angle
        else:
            pivot_x = bx + bw
            pivot_y = by + bh
            target_angle = angle
        _s, _d = start, max(dur, 1e-9)
        _px, _py, _ta = pivot_x, pivot_y, target_angle

        def _rot(t, _s=_s, _d=_d, _ta=_ta, _px=_px, _py=_py, _e=easing):
            p = _e((t - _s) / _d)
            return (_ta * p, _px, _py)

        self.styling.rotation.set(start, end, _rot, stay=True)
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
            # Freeze at position at t_appear
            for xa, ya in ghost._shift_reals():
                xa.set_onward(t_appear, xa.at_time(t_appear))
                ya.set_onward(t_appear, ya.at_time(t_appear))
            for c in ghost._shift_coors():
                c.set_onward(t_appear, c.at_time(t_appear))
            # Hidden before appearance
            ghost.show.set_onward(0, False)
            ghost.show.set_onward(t_appear, True)
            # Fade out over fade_duration
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
        # Determine anchor point and which axis to scale
        horizontal = direction in ('left', 'right')
        if direction == 'right':
            self.styling._scale_origin = (bx, cy)
        elif direction == 'left':
            self.styling._scale_origin = (bx + bw, cy)
        elif direction == 'down':
            self.styling._scale_origin = (cx, by)
        else:  # up
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
                xa.add(t0, t1, lambda t, _dx=dx: _dx, stay=False)
            for c in self._shift_coors():
                c.add(t0, t1, lambda t, _dx=dx: (_dx, 0), stay=False)
        return self

    def wave_through(self, start: float = 0, end: float = 1, amplitude=20,
                     frequency=2, direction='y', easing=easings.smooth):
        """Sinusoidal oscillation along the given axis with a fading envelope."""
        dur = end - start
        if dur <= 0:
            return self
        _s, _d, _a, _freq = start, max(dur, 1e-9), amplitude, frequency

        def _wave(t, _s=_s, _d=_d, _a=_a, _freq=_freq, _easing=easing):
            progress = (t - _s) / _d
            envelope = _easing(progress) * (1 - _easing(progress)) * 4
            return _a * math.sin(math.tau * _freq * progress) * envelope

        if direction == 'y':
            return self._apply_shift_effect(start, end, dy_func=_wave)
        else:
            return self._apply_shift_effect(start, end, dx_func=_wave)

    def countdown(self, start: float = 0, end: float = 1, from_val=3):
        """For Text objects: display a countdown from *from_val* to 1."""
        from vectormation._shapes import Text as _Text
        if not isinstance(self, _Text):
            raise TypeError("countdown() can only be called on Text objects")
        dur = end - start
        if dur <= 0 or from_val < 1:
            return self
        step_dur = dur / from_val
        for i in range(from_val):
            t = start + i * step_dur
            val = from_val - i
            self.text.set_onward(t, str(val))
        return self

    def squeeze(self, start: float = 0, end: float = 1, axis='x',
                factor=0.5, easing=easings.smooth):
        """Squeeze the object along one axis, scaling up the other to preserve area."""
        dur = end - start
        if dur <= 0:
            return self
        sx0, sy0 = self._init_scale_anim(start)
        _s, _d, _f = start, max(dur, 1e-9), factor
        compensate = 1.0 / _f if _f > 1e-9 else 1.0

        def _primary(t, _s=_s, _d=_d, _f=_f, _easing=easing):
            progress = _easing((t - _s) / _d)
            return 1 + (_f - 1) * progress

        def _compensate(t, _s=_s, _d=_d, _c=compensate, _easing=easing):
            progress = _easing((t - _s) / _d)
            return 1 + (_c - 1) * progress

        if axis == 'x':
            self.styling.scale_x.set(start, end,
                lambda t, _b=sx0: _b * _primary(t), stay=True)
            self.styling.scale_y.set(start, end,
                lambda t, _b=sy0: _b * _compensate(t), stay=True)
        else:
            self.styling.scale_y.set(start, end,
                lambda t, _b=sy0: _b * _primary(t), stay=True)
            self.styling.scale_x.set(start, end,
                lambda t, _b=sx0: _b * _compensate(t), stay=True)
        return self

    def bind_to(self, other, offset_x=0, offset_y=0, start=0, end=None):
        """Keep this object at a fixed offset relative to another object's center.
        Uses an updater to track other's center and reposition self each frame.
        Returns self."""
        def _bind(obj, time, _other=other, _ox=offset_x, _oy=offset_y):
            ocx, ocy = _other.center(time)
            target_x = ocx + _ox
            target_y = ocy + _oy
            scx, scy = obj.center(time)
            dx = target_x - scx
            dy = target_y - scy
            if abs(dx) > 0.01 or abs(dy) > 0.01:
                for xa, ya in obj._shift_reals():
                    xa.set_onward(time, xa.at_time(time) + dx)
                    ya.set_onward(time, ya.at_time(time) + dy)
                for c in obj._shift_coors():
                    val = c.at_time(time)
                    c.set_onward(time, (val[0] + dx, val[1] + dy))
        self.add_updater(_bind, start, end)
        return self

    def pin_to(self, other, edge='center', offset_x=0, offset_y=0, start=0, end=None):
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
                for xa, ya in obj._shift_reals():
                    xa.set_onward(time, xa.at_time(time) + dx)
                    ya.set_onward(time, ya.at_time(time) + dy)
                for c in obj._shift_coors():
                    val = c.at_time(time)
                    c.set_onward(time, (val[0] + dx, val[1] + dy))

        self.add_updater(_pin, start, end)
        return self

    def duplicate(self, count=2, direction=RIGHT, buff=MED_SMALL_BUFF):
        """Create count copies of the object arranged in the given direction.
        Returns a VCollection containing the copies (not including self)."""
        from vectormation._collection import VCollection
        col = VCollection(*[deepcopy(self) for _ in range(count)])
        col.arrange(direction=direction, buff=buff)
        return col

    def arc_to(self, x, y, start, end, angle=math.pi / 4, easing=easings.smooth):
        """Animated curved movement to (x, y) following a circular arc.
        angle controls the arc curvature (default PI/4). Uses parametric interpolation."""
        return self.path_arc(x, y, start=start, end=end, angle=angle, easing=easing)

    def typewriter_cursor(self, start, end, blink_rate=0.5, cursor_char='|'):
        """For Text objects: append a blinking cursor character.
        The cursor blinks on/off at blink_rate (seconds per blink cycle).
        Returns self."""
        from vectormation._shapes import Text as _Text
        if not isinstance(self, _Text):
            raise TypeError("typewriter_cursor() can only be called on Text objects")
        _base_text_func = self.text.time_func
        def _blink(t, _s=start, _rate=blink_rate, _char=cursor_char, _base=_base_text_func):
            base = _base(t)
            if int((t - _s) / _rate) % 2 == 0:
                return base + _char
            return base
        self.text.set(start, end, _blink, stay=False)
        return self

    def parallax(self, dx, dy, start=0, end=1, depth_factor=0.5, easing=easings.smooth):
        """Shift by a fraction of (dx, dy) to create a parallax depth illusion."""
        return self.shift(dx=dx * depth_factor, dy=dy * depth_factor,
                          start=start, end=end, easing=easing)

    _DASH_PRESETS = {
        'solid': '',
        'dashes': '10 5',
        'dots': '2 4',
        'dash_dot': '10 5 2 5',
    }

    def set_dash_pattern(self, pattern='dashes', start=0):
        """Set the stroke-dasharray at a given time. Accepts preset names or a custom string."""
        pattern_str = self._DASH_PRESETS.get(pattern, pattern)
        self.styling.stroke_dasharray.set_onward(start, pattern_str)
        return self

    def show_if(self, condition_func, start=0, end=None):
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

    def fade_to_color(self, target_color, start=0, end=1, easing=easings.smooth):
        """Smoothly transition both fill and stroke to target_color over [start, end].
        Returns self."""
        self.set_fill(color=target_color, start=start, end=end, easing=easing)
        self.set_stroke(color=target_color, start=start, end=end, easing=easing)
        return self

    def spin_and_fade(self, start=0, end=1, spins=1.5, direction=1, easing=easings.smooth):
        """Rotate and fade out simultaneously over [start, end]."""
        degrees = spins * 360 * direction
        self.rotate_by(start, end, degrees, easing=easing)
        self.set_opacity(0, start=start, end=end, easing=easing)
        return self

    def grow_to_size(self, target_width=None, target_height=None, start=0, end=1, easing=easings.smooth):
        """Animate the object to reach a specific width and/or height."""
        cur_w = self.get_width(start)
        cur_h = self.get_height(start)
        if cur_w <= 0 or cur_h <= 0:
            return self
        if target_width is not None and target_height is not None:
            sx = target_width / cur_w
            sy = target_height / cur_h
            self.stretch(sx, sy, start=start, end=end, easing=easing)
        elif target_width is not None:
            factor = target_width / cur_w
            self.scale(factor, start=start, end=end, easing=easing)
        elif target_height is not None:
            factor = target_height / cur_h
            self.scale(factor, start=start, end=end, easing=easing)
        return self

    def tilt_towards(self, target_x, target_y, max_angle=15, start=0, end=1, easing=easings.smooth):
        """Rotate the object to tilt toward a target point by *max_angle* degrees."""
        _, cy = self.center(start)
        dy = target_y - cy
        # In SVG coordinates (y-down), positive dy means target is below,
        # so tilt clockwise (positive degrees); negative dy means above.
        tilt = max_angle if dy >= 0 else -max_angle
        self.rotate_by(start, end, tilt, easing=easing)
        return self

    # -- Blend mode --

    _VALID_BLEND_MODES = frozenset({
        'normal', 'multiply', 'screen', 'overlay', 'darken', 'lighten',
        'color-dodge', 'color-burn',
    })

    def set_blend_mode(self, mode, start=0):
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

    def reveal_clip(self, start=0, end=1, direction='left', easing=easings.smooth):
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

    def repeat_animation(self, method_name, count=2, start=0, end=1, **kwargs):
        """Repeat an animation method *count* times within [start, end]."""
        if count <= 0:
            return self
        dur = end - start
        if dur <= 0:
            return self
        slice_dur = dur / count
        method = getattr(self, method_name)
        for i in range(count):
            s = start + i * slice_dur
            e = s + slice_dur
            method(start=s, end=e, **kwargs)
        return self

    # -- Elastic scale --

    def elastic_scale(self, start=0, end=1, factor=1.5, easing=easings.smooth):
        """Scale up elastically then bounce back to original size."""
        dur = end - start
        if dur <= 0:
            return self
        sx0, sy0 = self._init_scale_anim(start)
        _s, _d, _f = start, max(dur, 1e-9), factor
        _damp = 6.0
        _freq = math.tau * 2.5

        def _elastic_envelope(p):
            """Damped cosine: 1 at p=0, oscillates toward 0 at p=1."""
            if p <= 0:
                return 1.0
            if p >= 1:
                return 0.0
            return math.cos(_freq * p) * math.exp(-_damp * p)

        def _make_elastic(s0):
            def _es(t, _s=_s, _d=_d, _f=_f, _s0=s0, _easing=easing):
                p = _easing((t - _s) / _d)
                return _s0 * (1 + (_f - 1) * _elastic_envelope(p))
            return _es

        self.styling.scale_x.set(start, end, _make_elastic(sx0), stay=True)
        self.styling.scale_y.set(start, end, _make_elastic(sy0), stay=True)
        return self

    def snap_to_grid(self, grid_size=50, start=0, end=1, easing=easings.smooth):
        """Animate the object's center to the nearest grid point."""
        cx, cy = self.center(start)
        target_x = round(cx / grid_size) * grid_size
        target_y = round(cy / grid_size) * grid_size
        dx = target_x - cx
        dy = target_y - cy
        if dx != 0 or dy != 0:
            self.shift(dx=dx, dy=dy, start=start, end=end, easing=easing)
        return self

    def add_background(self, color='#000000', opacity=0.5, padding=20, creation=0, z=-1):
        """Create a semi-transparent Rectangle behind the object as a readability backdrop."""
        from vectormation._shapes import Rectangle  # lazy to avoid circular import
        x, y, w, h = self.bbox(creation)
        rect = Rectangle(
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
        return rect

    def cycle_colors(self, colors, start=0, end=1, easing=easings.linear):
        """Cycle the fill color through a list of colors over [start, end]."""
        dur = end - start
        if dur <= 0 or len(colors) < 2:
            return self
        n = len(colors)
        # Parse all colors to RGB tuples
        parsed = []
        for c in colors:
            _, rgb = attributes.Color(0, '#000').parse(c)
            parsed.append(rgb)
        # Set initial color at start
        self.set_fill(color=colors[0], start=start)
        # Use Color.set to define each interpolation segment
        src = self.styling.fill
        def _make_interp(_cf, _ct, _ss, _dd, _easing):
            def _interp(t):
                p = _easing((t - _ss) / _dd)
                return tuple(_cf[j] + (_ct[j] - _cf[j]) * p for j in range(len(_cf)))
            return _interp
        for i in range(n - 1):
            seg_s = start + dur * i / (n - 1)
            seg_e = start + dur * (i + 1) / (n - 1)
            c_from = parsed[i]
            c_to = parsed[i + 1]
            _d = max(seg_e - seg_s, 1e-9)
            src.set(seg_s, seg_e, _make_interp(c_from, c_to, seg_s, _d, easing), stay=(i == n - 2))
        return self

    def freeze(self, start, end=None):
        """Freeze the object's appearance at time *start* until *end*."""
        _captured = {}

        def _capture(obj, t):
            if not _captured:
                # Snapshot every styling attribute at the freeze time
                for name, _, cls, _, _ in style._ATTR_SCHEMA:
                    attr = getattr(obj.styling, name)
                    _captured[name] = attr.at_time(start)
                _captured['_z'] = obj.z.at_time(start)
            # Restore all attributes to their frozen values
            for name, _, cls, _, _ in style._ATTR_SCHEMA:
                val = _captured[name]
                attr = getattr(obj.styling, name)
                if cls is attributes.Color:
                    attr.set_onward(t, lambda _t, _v=val: _v)
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
        if 'end' in params and 'end' in kwargs:
            kwargs['end'] = kwargs['end'] + delay
        method(*args, **kwargs)
        return self

    def wobble(self, start=0, end=1, intensity=5, frequency=3, easing=easings.smooth):
        """Organic wobbling motion combining small rotations and position shifts."""
        dur = end - start
        if dur <= 0:
            return self
        _s, _d, _a, _freq = start, max(dur, 1e-9), intensity, frequency

        # Shift component: two different sine frequencies for organic feel
        def _dx(t, _s=_s, _d=_d, _a=_a, _freq=_freq, _easing=easing):
            p = (t - _s) / _d
            envelope = 1 - _easing(p)
            return _a * math.sin(math.tau * _freq * p) * envelope

        def _dy(t, _s=_s, _d=_d, _a=_a, _freq=_freq, _easing=easing):
            p = (t - _s) / _d
            envelope = 1 - _easing(p)
            return _a * 0.7 * math.sin(math.tau * _freq * 1.3 * p) * envelope

        self._apply_shift_effect(start, end, _dx, _dy)

        # Rotation component: slight wobbling rotation
        cx, cy = self.center(start)
        self.styling.rotation.set(start, end,
            lambda t, _s=_s, _d=_d, _a=_a, _freq=_freq, _cx=cx, _cy=cy, _easing=easing: (
                _a * math.sin(math.tau * _freq * 0.7 * ((t - _s) / _d)) * (1 - _easing((t - _s) / _d)),
                _cx, _cy))
        return self

    def focus_zoom(self, start=0, end=1, zoom_factor=1.3, easing=easings.smooth):
        """Zoom in slightly on the object then back to normal, like a camera focus effect."""
        dur = end - start
        if dur <= 0:
            return self
        self._ensure_scale_origin(start)
        _s, _d, _zf = start, max(dur, 1e-9), zoom_factor
        def _make_zoom(s0):
            return lambda t, _s=_s, _d=_d, _zf=_zf, _s0=s0, _easing=easing: \
                _s0 * (1 + (_zf - 1) * math.sin(math.pi * _easing((t - _s) / _d)))
        self.styling.scale_x.set(start, end, _make_zoom(self.styling.scale_x.at_time(start)))
        self.styling.scale_y.set(start, end, _make_zoom(self.styling.scale_y.at_time(start)))
        return self

    def typewriter_effect(self, text, start=0, end=1, easing=easings.linear):
        """For Text objects only: gradually reveal text character by character."""
        from vectormation._shapes import Text as _Text
        if not isinstance(self, _Text):
            raise TypeError("typewriter_effect() can only be called on Text objects")
        n = len(text)
        if n == 0:
            return self
        dur = end - start
        if dur <= 0:
            return self
        _s, _d, _txt = start, max(dur, 1e-9), text
        def _reveal(t, _s=_s, _d=_d, _txt=_txt, _n=n, _easing=easing):
            p = min(1.0, _easing((t - _s) / _d))
            chars = int(p * _n)
            return _txt[:chars]
        self.text.set(start, end, _reveal, stay=True)
        self.text.set_onward(end, text)
        return self

    def look_at(self, target, start=0, end=None, easing=None):
        """Rotate so this object points toward *target*."""
        if easing is None:
            easing = easings.smooth
        # Resolve target coordinates
        if isinstance(target, tuple):
            tx, ty = target
        else:
            tx, ty = target.get_center(start)
        cx, cy = self.get_center(start)
        angle_rad = math.atan2(ty - cy, tx - cx)
        angle_deg = math.degrees(angle_rad)
        if end is None:
            return self.rotate_to(start, start, angle_deg, easing=easing)
        return self.rotate_to(start, end, angle_deg, easing=easing)

    def animate_to(self, target_obj, start=0, end=1, easing=None):
        """Animate position, scale, and colors to match *target_obj*."""
        if easing is None:
            easing = easings.smooth
        # Move to target center
        tx, ty = target_obj.get_center(start)
        self.center_to_pos(posx=tx, posy=ty, start=start, end=end, easing=easing)
        # Scale to match target width
        tw = target_obj.get_width(start)
        cur_w = self.get_width(start)
        if cur_w > 0 and tw > 0:
            factor = tw / cur_w
            self.scale(factor, start=start, end=end, easing=easing)
        # Transition fill color — use raw tuple from time_func to avoid
        # round-tripping through at_time()'s "rgb(...)" string format.
        target_fill = target_obj.styling.fill.time_func(start)
        if target_fill:
            self.set_color(start, end, fill=self._rgb_to_hex(target_fill), easing=easing)
        # Transition stroke color
        target_stroke = target_obj.styling.stroke.time_func(start)
        if target_stroke:
            self.set_color(start, end, stroke=self._rgb_to_hex(target_stroke), easing=easing)
        return self

    def set_gradient_fill(self, colors, direction='horizontal', start=0):
        """Apply an SVG gradient fill to this object."""
        gid = f'grad{id(self)}'
        n = len(colors)
        stops = ''.join(
            f"<stop offset='{i / max(n - 1, 1) * 100}%' stop-color='{c}'/>"
            for i, c in enumerate(colors)
        )
        if direction == 'radial':
            grad_def = (
                f"<radialGradient id='{gid}'>"
                f"{stops}</radialGradient>"
            )
        else:
            if direction == 'vertical':
                x1, y1, x2, y2 = 0, 0, 0, 1
            else:  # horizontal
                x1, y1, x2, y2 = 0, 0, 1, 0
            grad_def = (
                f"<linearGradient id='{gid}' x1='{x1}' y1='{y1}' x2='{x2}' y2='{y2}'>"
                f"{stops}</linearGradient>"
            )
        _orig_to_svg = self.to_svg

        def _gradient_to_svg(time, _orig=_orig_to_svg, _gid=gid,
                             _def=grad_def, _start=start):
            inner = _orig(time)
            if time >= _start:
                return (f"<g><defs>{_def}</defs>"
                        f"<g fill='url(#{_gid})'>{inner}</g></g>")
            return inner

        self.to_svg = _gradient_to_svg  # type: ignore[assignment]
        return self

    def set_clip(self, clip_obj, start=0):
        """Apply an SVG clip-path from another VObject's outline."""
        cid = f'clip{id(self)}'
        _orig_to_svg = self.to_svg

        def _clipped_to_svg(time, _orig=_orig_to_svg, _cid=cid,
                            _clip=clip_obj, _start=start):
            inner = _orig(time)
            if time >= _start:
                clip_svg = _clip.to_svg(time)
                return (f"<g clip-path='url(#{_cid})'>"
                        f"<defs><clipPath id='{_cid}'>"
                        f"{clip_svg}</clipPath></defs>"
                        f"{inner}</g>")
            return inner

        self.to_svg = _clipped_to_svg  # type: ignore[assignment]
        return self

    def set_lifetime(self, start, end):
        """Set bounded visibility: visible only from *start* to *end*."""
        self.set_visible(False, 0)
        self.set_visible(True, start)
        self.set_visible(False, end)
        return self

    def get_style(self, time=0):
        """Return the current styling as a dict at the given time."""
        return {
            'fill': self.styling.fill.at_time(time),
            'stroke': self.styling.stroke.at_time(time),
            'fill_opacity': self.styling.fill_opacity.at_time(time),
            'stroke_opacity': self.styling.stroke_opacity.at_time(time),
            'stroke_width': self.styling.stroke_width.at_time(time),
            'opacity': self.styling.opacity.at_time(time),
        }

    def move_towards(self, other, fraction=0.5, start=0, end=None, easing=None):
        """Move a fraction of the way toward another object or point.

        Parameters
        ----------
        other:
            A VObject (uses its center) or an (x, y) tuple.
        fraction:
            How far to move (0 = stay, 1 = reach other's center).
        start:
            Start time for the animation.
        end:
            End time (None = instant move).
        easing:
            Easing function for the animation.
        """
        cx, cy = self.get_center(start)
        tx, ty = _coords_of(other, start)
        nx = cx + fraction * (tx - cx)
        ny = cy + fraction * (ty - cy)
        return self.center_to_pos(posx=nx, posy=ny, start=start,
                                  end=end, easing=easing or easings.smooth)

    def add_label(self, text, direction=UP, buff=20, font_size=None, follow=False, creation=0, **kwargs):
        """Attach a text label next to this object.

        Creates a :class:`Text` object positioned via :meth:`next_to` and
        returns a :class:`VCollection` containing both *self* and the label.

        Parameters
        ----------
        text:
            The label string.
        direction:
            Direction constant for placement (e.g. ``UP``, ``DOWN``).
        buff:
            Pixel buffer between the object and the label.
        font_size:
            Optional font size for the label.  Defaults to ``None``
            which uses the Text default.
        follow:
            If ``True``, add an updater so the label tracks this
            object's position continuously.
        creation:
            Creation time for the label.
        **kwargs:
            Extra keyword arguments forwarded to the ``Text`` constructor.

        Returns a VCollection(self, label).
        """
        from vectormation._shapes import Text as _Text  # lazy import
        label_kwargs = dict(creation=creation)
        if font_size is not None:
            label_kwargs['font_size'] = font_size
        label_kwargs.update(kwargs)
        label = _Text(text, **label_kwargs)
        label.next_to(self, direction, buff, start=creation)
        if follow:
            _dir = direction
            _buff = buff
            def _follow_updater(lbl, t, _parent=self, _d=_dir, _b=_buff):
                lbl.next_to(_parent, _d, _b, start=t)
            label.add_updater(_follow_updater, start=creation)
        from vectormation._collection import VCollection
        return VCollection(self, label)

    def place_between(self, obj_a, obj_b, fraction=0.5, start=0, end=None, easing=None):
        """Position this object between two other objects or points.

        Computes the target as ``(1 - fraction) * center_a + fraction * center_b``
        and moves there using :meth:`center_to_pos`.

        Parameters
        ----------
        obj_a:
            First reference — a VObject (uses ``get_center``) or an ``(x, y)`` tuple.
        obj_b:
            Second reference — a VObject or tuple.
        fraction:
            Interpolation factor (0.0 = at *obj_a*, 1.0 = at *obj_b*).
        start:
            Start time for the movement.
        end:
            End time (``None`` = instant).
        easing:
            Easing function for animation.

        Returns self.
        """
        ax, ay = _coords_of(obj_a, start)
        bx, by = _coords_of(obj_b, start)
        tx = (1 - fraction) * ax + fraction * bx
        ty = (1 - fraction) * ay + fraction * by
        return self.center_to_pos(posx=tx, posy=ty, start=start,
                                  end=end, easing=easing or easings.smooth)

    def homotopy(self, func, start: float = 0, end: float = 1):
        """Apply a continuous point-wise transformation over time.

        *func(x, y, t)* → *(x', y')* is called for each coordinate attribute,
        where *t* progresses linearly from 0 to 1 over [start, end].
        Works on Polygon vertices, Line endpoints, and (x, y) Real pairs.
        """
        dur = end - start
        if dur <= 0:
            return self
        coors = self._shift_coors()
        reals = self._shift_reals()
        for c in coors:
            orig = c.at_time(start)
            ox, oy = float(orig[0]), float(orig[1])
            def _h(t, _s=start, _d=dur, _ox=ox, _oy=oy, _f=func):
                alpha = min(1.0, (t - _s) / _d)
                return _f(_ox, _oy, alpha)
            c.set(start, end, _h, stay=True)
            fx, fy = func(ox, oy, 1.0)
            c.set_onward(end, (fx, fy))
        for rx, ry in reals:
            ox = float(rx.at_time(start))
            oy = float(ry.at_time(start))
            def _hx(t, _s=start, _d=dur, _ox=ox, _oy=oy, _f=func):
                alpha = min(1.0, (t - _s) / _d)
                return _f(_ox, _oy, alpha)[0]
            def _hy(t, _s=start, _d=dur, _ox=ox, _oy=oy, _f=func):
                alpha = min(1.0, (t - _s) / _d)
                return _f(_ox, _oy, alpha)[1]
            rx.set(start, end, _hx, stay=True)
            ry.set(start, end, _hy, stay=True)
            fx, fy = func(ox, oy, 1.0)
            rx.set_onward(end, fx)
            ry.set_onward(end, fy)
        return self

# VCollection moved to _collection.py; re-export for backward compatibility.
