"""Tests for previously untested animation effects in _base_effects.py."""
import pytest
from vectormation.objects import (
    Circle, Rectangle, Text, Dot, VectorMathAnim,
)


class TestMatchPosition:
    def test_basic(self):
        c1 = Circle(r=50, cx=100, cy=100)
        c2 = Circle(r=50, cx=500, cy=400)
        c1.match_position(c2, time=0)
        svg = c1.to_svg(0)
        assert svg is not None

    def test_returns_self(self):
        c1 = Circle(r=50, cx=100, cy=100)
        c2 = Circle(r=50, cx=500, cy=400)
        result = c1.match_position(c2)
        assert result is c1


class TestPointFromProportion:
    def test_start(self):
        r = Rectangle(200, 100, x=100, y=100)
        pt = r.point_from_proportion(0)
        assert isinstance(pt, tuple)
        assert len(pt) == 2

    def test_mid(self):
        r = Rectangle(200, 100, x=100, y=100)
        pt = r.point_from_proportion(0.5)
        assert isinstance(pt, tuple)


class TestConnect:
    def test_line_connection(self):
        c1 = Circle(r=50, cx=200, cy=300)
        c2 = Circle(r=50, cx=600, cy=300)
        line = c1.connect(c2)
        svg = line.to_svg(0)
        assert 'line' in svg.lower() or 'path' in svg.lower()

    def test_arrow_connection(self):
        c1 = Circle(r=50, cx=200, cy=300)
        c2 = Circle(r=50, cx=600, cy=300)
        arrow = c1.connect(c2, arrow=True)
        svg = arrow.to_svg(0)
        assert svg is not None

    def test_follow_line(self):
        c1 = Circle(r=50, cx=200, cy=300)
        c2 = Circle(r=50, cx=600, cy=300)
        line = c1.connect(c2, follow=True)
        svg = line.to_svg(0)
        assert svg is not None

    def test_follow_arrow(self):
        c1 = Circle(r=50, cx=200, cy=300)
        c2 = Circle(r=50, cx=600, cy=300)
        arrow = c1.connect(c2, arrow=True, follow=True)
        svg = arrow.to_svg(0)
        assert svg is not None


class TestMatchStyle:
    def test_basic(self):
        c1 = Circle(r=50, fill='#FF0000')
        c2 = Circle(r=50, fill='#00FF00', stroke='#0000FF')
        c1.match_style(c2)
        svg = c1.to_svg(0)
        assert svg is not None

    def test_returns_self(self):
        c1 = Circle(r=50)
        c2 = Circle(r=50, fill='#FF0000')
        result = c1.match_style(c2)
        assert result is c1


class TestTelegraph:
    def test_basic(self):
        c = Circle(r=50)
        c.telegraph(start=0, end=0.4)
        svg = c.to_svg(0.2)
        assert svg is not None

    def test_returns_self(self):
        c = Circle(r=50)
        result = c.telegraph()
        assert result is c

    def test_zero_duration(self):
        c = Circle(r=50)
        result = c.telegraph(start=1, end=1)
        assert result is c


class TestSkate:
    def test_basic(self):
        c = Circle(r=50, cx=100, cy=100)
        c.skate(500, 400, start=0, end=1)
        svg = c.to_svg(0.5)
        assert svg is not None

    def test_returns_self(self):
        c = Circle(r=50)
        result = c.skate(500, 500)
        assert result is c


class TestFlicker:
    def test_basic(self):
        c = Circle(r=50)
        c.flicker(start=0, end=1)
        svg = c.to_svg(0.5)
        assert svg is not None

    def test_zero_duration(self):
        c = Circle(r=50)
        result = c.flicker(start=1, end=1)
        assert result is c


class TestSlingshot:
    def test_basic(self):
        c = Circle(r=50, cx=100, cy=300)
        c.slingshot(800, 300, start=0, end=1)
        svg = c.to_svg(0.5)
        assert svg is not None

    def test_returns_self(self):
        c = Circle(r=50)
        result = c.slingshot(500, 500)
        assert result is c


class TestElasticBounce:
    def test_basic(self):
        c = Circle(r=50)
        c.elastic_bounce(start=0, end=1)
        svg = c.to_svg(0.5)
        assert svg is not None

    def test_custom_params(self):
        c = Circle(r=50)
        c.elastic_bounce(start=0, end=2, height=200, n_bounces=5)
        svg = c.to_svg(1.0)
        assert svg is not None

    def test_zero_duration(self):
        c = Circle(r=50)
        result = c.elastic_bounce(start=1, end=1)
        assert result is c


class TestMorphScale:
    def test_basic(self):
        c = Circle(r=50)
        c.morph_scale(target_scale=2.0, start=0, end=1)
        svg = c.to_svg(0.5)
        assert svg is not None

    def test_returns_self(self):
        c = Circle(r=50)
        result = c.morph_scale()
        assert result is c


class TestStrobe:
    def test_basic(self):
        c = Circle(r=50)
        c.strobe(start=0, end=1, n_flashes=5)
        svg = c.to_svg(0.3)
        assert svg is not None

    def test_zero_flashes(self):
        c = Circle(r=50)
        result = c.strobe(n_flashes=0)
        assert result is c

    def test_zero_duration(self):
        c = Circle(r=50)
        result = c.strobe(start=1, end=1)
        assert result is c


class TestZoomTo:
    def test_basic(self):
        canvas = VectorMathAnim('/tmp')
        c = Circle(r=50)
        canvas.add(c)
        c.zoom_to(canvas, start=0, end=1)
        svg = canvas.generate_frame_svg(0.5)
        assert svg is not None

    def test_zero_duration(self):
        canvas = VectorMathAnim('/tmp')
        c = Circle(r=50)
        result = c.zoom_to(canvas, start=1, end=1)
        assert result is c


class TestTypewriterDelete:
    def test_basic(self):
        r = Rectangle(200, 100)
        r.typewriter_delete(start=0, end=1)
        svg = r.to_svg(0.5)
        assert svg is not None


class TestDomino:
    def test_right(self):
        r = Rectangle(100, 200)
        r.domino(start=0, end=1, direction='right')
        svg = r.to_svg(0.5)
        assert svg is not None

    def test_left(self):
        r = Rectangle(100, 200)
        r.domino(start=0, end=1, direction='left')
        svg = r.to_svg(0.5)
        assert svg is not None

    def test_zero_duration(self):
        r = Rectangle(100, 200)
        result = r.domino(start=1, end=1)
        assert result is r


class TestStampTrail:
    def test_basic(self):
        c = Circle(r=50)
        c.shift(dx=200, start=0, end=2)
        ghosts = c.stamp_trail(start=0, end=2, count=3)
        assert len(ghosts) == 3
        for g in ghosts:
            svg = g.to_svg(1.0)
            assert svg is not None

    def test_zero_count(self):
        c = Circle(r=50)
        ghosts = c.stamp_trail(count=0)
        assert ghosts == []

    def test_zero_duration(self):
        c = Circle(r=50)
        ghosts = c.stamp_trail(start=1, end=1)
        assert ghosts == []


class TestGlitchShift:
    def test_basic(self):
        c = Circle(r=50)
        c.glitch_shift(start=0, end=1, seed=42)
        svg = c.to_svg(0.5)
        assert svg is not None

    def test_deterministic(self):
        c1 = Circle(r=50)
        c2 = Circle(r=50)
        c1.glitch_shift(start=0, end=1, seed=42)
        c2.glitch_shift(start=0, end=1, seed=42)
        svg1 = c1.to_svg(0.5)
        svg2 = c2.to_svg(0.5)
        assert svg1 == svg2

    def test_zero_duration(self):
        c = Circle(r=50)
        result = c.glitch_shift(start=1, end=1)
        assert result is c


class TestWaveThrough:
    def test_basic(self):
        c = Circle(r=50)
        c.wave_through(start=0, end=1)
        svg = c.to_svg(0.5)
        assert svg is not None

    def test_x_direction(self):
        c = Circle(r=50)
        c.wave_through(start=0, end=1, direction='x')
        svg = c.to_svg(0.5)
        assert svg is not None


class TestRevealClip:
    def test_left(self):
        r = Rectangle(200, 100)
        r.reveal_clip(start=0, end=1, direction='left')
        svg = r.to_svg(0.5)
        assert svg is not None

    def test_right(self):
        r = Rectangle(200, 100)
        r.reveal_clip(start=0, end=1, direction='right')
        svg = r.to_svg(0.5)
        assert svg is not None

    def test_top(self):
        r = Rectangle(200, 100)
        r.reveal_clip(start=0, end=1, direction='top')
        svg = r.to_svg(0.5)
        assert svg is not None

    def test_bottom(self):
        r = Rectangle(200, 100)
        r.reveal_clip(start=0, end=1, direction='bottom')
        svg = r.to_svg(0.5)
        assert svg is not None

    def test_invalid_direction(self):
        r = Rectangle(200, 100)
        with pytest.raises(ValueError, match='Unsupported reveal direction'):
            r.reveal_clip(direction='diagonal')


class TestRepeatAnimation:
    def test_basic(self):
        c = Circle(r=50)
        c.repeat_animation('flash', count=3, start=0, end=3)
        svg = c.to_svg(1.5)
        assert svg is not None

    def test_zero_count(self):
        c = Circle(r=50)
        result = c.repeat_animation('flash', count=0)
        assert result is c


class TestElasticScale:
    def test_basic(self):
        c = Circle(r=50)
        c.elastic_scale(start=0, end=1)
        svg = c.to_svg(0.5)
        assert svg is not None

    def test_returns_self(self):
        c = Circle(r=50)
        result = c.elastic_scale()
        assert result is c


class TestSnapToGrid:
    def test_basic(self):
        c = Circle(r=50, cx=123, cy=267)
        c.snap_to_grid(grid_size=50, start=0, end=1)
        svg = c.to_svg(1.0)
        assert svg is not None

    def test_already_aligned(self):
        c = Circle(r=50, cx=100, cy=200)
        result = c.snap_to_grid(grid_size=100)
        assert result is c


class TestAddBackground:
    def test_basic(self):
        c = Circle(r=50)
        bg = c.add_background()
        svg = bg.to_svg(0)
        assert 'rect' in svg.lower()

    def test_custom_params(self):
        c = Circle(r=50)
        bg = c.add_background(color='#333333', opacity=0.8, padding=30)
        svg = bg.to_svg(0)
        assert svg is not None


class TestSetGradientFill:
    def test_horizontal(self):
        c = Circle(r=50)
        c.set_gradient_fill(['#FF0000', '#0000FF'])
        svg = c.to_svg(0)
        assert 'linearGradient' in svg

    def test_vertical(self):
        c = Circle(r=50)
        c.set_gradient_fill(['#FF0000', '#0000FF'], direction='vertical')
        svg = c.to_svg(0)
        assert 'linearGradient' in svg

    def test_radial(self):
        c = Circle(r=50)
        c.set_gradient_fill(['#FF0000', '#0000FF'], direction='radial')
        svg = c.to_svg(0)
        assert 'radialGradient' in svg


class TestSetLifetime:
    def test_basic(self):
        c = Circle(r=50)
        c.set_lifetime(start=1, end=3)
        assert not c.show.at_time(0)
        assert c.show.at_time(1)
        assert c.show.at_time(2)
        assert not c.show.at_time(3)

    def test_returns_self(self):
        c = Circle(r=50)
        result = c.set_lifetime(0, 5)
        assert result is c


class TestGetStyle:
    def test_basic(self):
        c = Circle(r=50, fill='#FF0000', stroke='#00FF00')
        style = c.get_style(time=0)
        assert 'fill' in style
        assert 'stroke' in style
        assert 'fill_opacity' in style
        assert 'stroke_opacity' in style
        assert 'stroke_width' in style
        assert 'opacity' in style

    def test_returns_dict(self):
        c = Circle(r=50)
        result = c.get_style()
        assert isinstance(result, dict)


class TestHomotopy:
    def test_basic(self):
        c = Circle(r=50)
        c.homotopy(lambda x, y, t: (x + 100 * t, y + 50 * t), start=0, end=1)
        svg = c.to_svg(0.5)
        assert svg is not None

    def test_zero_duration(self):
        c = Circle(r=50)
        result = c.homotopy(lambda x, y, t: (x, y), start=1, end=1)
        assert result is c


class TestScaleInPlace:
    def test_basic(self):
        c = Circle(r=50)
        c.scale_in_place(2.0, start=0, end=1)
        svg = c.to_svg(0.5)
        assert svg is not None

    def test_returns_self(self):
        c = Circle(r=50)
        result = c.scale_in_place(1.5)
        assert result is c


class TestPassingFlash:
    def test_basic(self):
        c = Circle(r=50, stroke='#FFFFFF')
        c.passing_flash(start=0, end=1)
        svg = c.to_svg(0.5)
        assert svg is not None

    def test_with_color(self):
        c = Circle(r=50)
        c.passing_flash(start=0, end=1, color='#FFD700')
        svg = c.to_svg(0.5)
        assert svg is not None


class TestFadeToColor:
    def test_basic(self):
        c = Circle(r=50, fill='#FF0000')
        c.fade_to_color('#0000FF', start=0, end=1)
        svg = c.to_svg(0.5)
        assert svg is not None

    def test_returns_self(self):
        c = Circle(r=50)
        result = c.fade_to_color('#FF0000')
        assert result is c


class TestSpinAndFade:
    def test_basic(self):
        c = Circle(r=50)
        c.spin_and_fade(start=0, end=1)
        svg = c.to_svg(0.5)
        assert svg is not None

    def test_returns_self(self):
        c = Circle(r=50)
        result = c.spin_and_fade()
        assert result is c


class TestGrowToSize:
    def test_width_only(self):
        c = Circle(r=50)
        c.grow_to_size(target_width=200, start=0, end=1)
        svg = c.to_svg(0.5)
        assert svg is not None

    def test_height_only(self):
        c = Circle(r=50)
        c.grow_to_size(target_height=200, start=0, end=1)
        svg = c.to_svg(0.5)
        assert svg is not None

    def test_both(self):
        c = Circle(r=50)
        c.grow_to_size(target_width=300, target_height=200, start=0, end=1)
        svg = c.to_svg(0.5)
        assert svg is not None

    def test_returns_self(self):
        c = Circle(r=50)
        result = c.grow_to_size(target_width=200)
        assert result is c


class TestSetBlendMode:
    def test_valid_mode(self):
        c = Circle(r=50)
        c.set_blend_mode('multiply')
        svg = c.to_svg(0)
        assert 'multiply' in svg

    def test_invalid_mode(self):
        c = Circle(r=50)
        with pytest.raises(ValueError, match='Unsupported blend mode'):
            c.set_blend_mode('invalid_mode')


class TestSurround:
    def test_basic(self):
        c = Circle(r=50)
        rect = Circle.surround(c)
        svg = rect.to_svg(0)
        assert 'rect' in svg.lower()


class TestSqueeze:
    def test_x_axis(self):
        c = Circle(r=50)
        c.squeeze(start=0, end=1, axis='x')
        svg = c.to_svg(0.5)
        assert svg is not None

    def test_y_axis(self):
        c = Circle(r=50)
        c.squeeze(start=0, end=1, axis='y')
        svg = c.to_svg(0.5)
        assert svg is not None


class TestBindTo:
    def test_basic(self):
        c1 = Circle(r=50, cx=100, cy=100)
        c2 = Circle(r=20)
        c2.bind_to(c1, offset_x=0, offset_y=80, start=0)
        svg = c2.to_svg(0)
        assert svg is not None

    def test_returns_self(self):
        c1 = Circle(r=50)
        c2 = Circle(r=20)
        result = c2.bind_to(c1)
        assert result is c2


class TestPinTo:
    def test_basic(self):
        c1 = Circle(r=50, cx=300, cy=300)
        c2 = Dot(cx=0, cy=0)
        c2.pin_to(c1, edge='center')
        svg = c2.to_svg(0)
        assert svg is not None


class TestDuplicate:
    def test_basic(self):
        c = Circle(r=50)
        copies = c.duplicate(count=3)
        assert len(copies.objects) == 3


class TestTypewriterCursor:
    def test_basic(self):
        t = Text(text='Hello')
        t.typewriter_cursor(start=0, end=2)
        svg = t.to_svg(0)
        assert svg is not None


class TestParallax:
    def test_basic(self):
        c = Circle(r=50)
        c.parallax(100, 50, start=0, end=1, depth_factor=0.3)
        svg = c.to_svg(0.5)
        assert svg is not None


class TestSetDashPattern:
    def test_dashes(self):
        c = Circle(r=50)
        c.set_dash_pattern('dashes')
        svg = c.to_svg(0)
        assert '10 5' in svg

    def test_dots(self):
        c = Circle(r=50)
        c.set_dash_pattern('dots')
        svg = c.to_svg(0)
        assert '2 4' in svg

    def test_custom(self):
        c = Circle(r=50)
        c.set_dash_pattern('15 3 5 3')
        svg = c.to_svg(0)
        assert '15 3 5 3' in svg


class TestShowIf:
    def test_basic(self):
        c = Circle(r=50)
        c.show_if(lambda t: t > 1, start=0)
        # Before t=1, should be hidden (opacity 0)
        svg_before = c.to_svg(0.5)
        # After t=1, should be visible
        svg_after = c.to_svg(1.5)
        assert svg_before is not None
        assert svg_after is not None

    def test_returns_self(self):
        c = Circle(r=50)
        result = c.show_if(lambda t: True)
        assert result is c


class TestCountdown:
    def test_basic(self):
        t = Text(text='3')
        t.countdown(start=0, end=3, from_val=3)
        # At time 0 should show "3"
        svg0 = t.to_svg(0)
        assert '3' in svg0
        # At time 2 should show "1"
        svg2 = t.to_svg(2)
        assert '1' in svg2


class TestFocusZoom:
    def test_basic(self):
        c = Circle(r=50)
        c.focus_zoom(start=0, end=1)
        svg = c.to_svg(0.5)
        assert svg is not None


class TestArcTo:
    def test_is_alias(self):
        c = Circle(r=50)
        assert hasattr(c, 'arc_to')
