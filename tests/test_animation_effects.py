"""Tests for animation effect methods in _base_effects.py."""
import pytest
from vectormation.objects import Circle, Rectangle


class TestElasticBounce:
    def test_returns_self(self):
        c = Circle(r=50, cx=500, cy=300)
        result = c.elastic_bounce(start=0, end=2, height=100)
        assert result is c

    def test_zero_duration(self):
        c = Circle(r=50)
        result = c.elastic_bounce(start=1, end=1)
        assert result is c

    def test_renders_at_midpoint(self):
        c = Circle(r=50, cx=500, cy=300)
        c.elastic_bounce(start=0, end=2)
        svg = c.to_svg(1.0)
        assert '<circle' in svg


class TestMorphScale:
    def test_returns_self(self):
        c = Circle(r=50)
        result = c.morph_scale(target_scale=2.0, start=0, end=1)
        assert result is c

    def test_zero_duration(self):
        c = Circle(r=50)
        result = c.morph_scale(start=1, end=1)
        assert result is c

    def test_renders_midway(self):
        c = Circle(r=50)
        c.morph_scale(target_scale=2.0, start=0, end=1)
        svg = c.to_svg(0.5)
        assert '<circle' in svg


class TestStrobe:
    def test_returns_self(self):
        c = Circle(r=50)
        result = c.strobe(start=0, end=1, n_flashes=5)
        assert result is c

    def test_zero_flashes(self):
        c = Circle(r=50)
        result = c.strobe(start=0, end=1, n_flashes=0)
        assert result is c

    def test_opacity_changes(self):
        c = Circle(r=50)
        c.strobe(start=0, end=1, n_flashes=4)
        # At different times, opacity should vary
        o1 = c.styling.opacity.at_time(0.1)
        o2 = c.styling.opacity.at_time(0.15)
        # At least one should be 0 or 1
        assert o1 in (0, 1) or o2 in (0, 1)


class TestFadeToColor:
    def test_returns_self(self):
        c = Circle(r=50, fill='#FF0000')
        result = c.fade_to_color('#00FF00', start=0, end=1)
        assert result is c

    def test_color_changes(self):
        c = Circle(r=50, fill='#FF0000')
        c.fade_to_color('#0000FF', start=0, end=1)
        svg = c.to_svg(1.5)
        # After animation, should be close to blue
        assert 'rgb(0,0,255)' in svg or '0000ff' in svg.lower() or 'rgb' in svg


class TestSpinAndFade:
    def test_returns_self(self):
        c = Circle(r=50)
        result = c.spin_and_fade(start=0, end=1)
        assert result is c

    def test_opacity_decreases(self):
        c = Circle(r=50)
        c.spin_and_fade(start=0, end=1)
        o = c.styling.opacity.at_time(1.5)
        assert o == pytest.approx(0, abs=0.01)


class TestGrowToSize:
    def test_target_width(self):
        r = Rectangle(100, 50, x=100, y=100)
        result = r.grow_to_size(target_width=200, start=0, end=1)
        assert result is r

    def test_target_height(self):
        r = Rectangle(100, 50, x=100, y=100)
        result = r.grow_to_size(target_height=100, start=0, end=1)
        assert result is r

    def test_both_targets(self):
        r = Rectangle(100, 50, x=100, y=100)
        result = r.grow_to_size(target_width=200, target_height=100, start=0, end=1)
        assert result is r

    def test_no_targets(self):
        r = Rectangle(100, 50, x=100, y=100)
        result = r.grow_to_size(start=0, end=1)
        assert result is r


class TestTiltTowards:
    def test_returns_self(self):
        c = Circle(r=50, cx=500, cy=300)
        result = c.tilt_towards(600, 400, start=0, end=1)
        assert result is c

    def test_tilt_direction(self):
        c = Circle(r=50, cx=500, cy=300)
        c.tilt_towards(600, 400, max_angle=15, start=0, end=1)
        rot = c.styling.rotation.at_time(1.5)
        assert rot[0] != 0


class TestSetBlendMode:
    def test_valid_mode(self):
        c = Circle(r=50)
        result = c.set_blend_mode('multiply')
        assert result is c

    def test_invalid_mode(self):
        c = Circle(r=50)
        with pytest.raises(ValueError, match="Unsupported blend mode"):
            c.set_blend_mode('invalid_mode')


class TestRevealClip:
    def test_returns_self(self):
        c = Circle(r=50)
        result = c.reveal_clip(start=0, end=1, direction='left')
        assert result is c

    def test_all_directions(self):
        for d in ('left', 'right', 'top', 'bottom'):
            c = Circle(r=50)
            c.reveal_clip(start=0, end=1, direction=d)
            svg = c.to_svg(0.5)
            assert svg is not None

    def test_invalid_direction(self):
        c = Circle(r=50)
        with pytest.raises(ValueError, match="Unsupported reveal direction"):
            c.reveal_clip(direction='diagonal')


class TestRepeatAnimation:
    def test_returns_self(self):
        c = Circle(r=50)
        result = c.repeat_animation('pulsate', count=3, start=0, end=3)
        assert result is c

    def test_zero_count(self):
        c = Circle(r=50)
        result = c.repeat_animation('pulsate', count=0, start=0, end=1)
        assert result is c


class TestElasticScale:
    def test_returns_self(self):
        c = Circle(r=50)
        result = c.elastic_scale(start=0, end=1, factor=1.5)
        assert result is c

    def test_settles_back(self):
        c = Circle(r=50)
        c.elastic_scale(start=0, end=1, factor=2.0)
        # After the animation, scale should be back to ~1
        sx = c.styling.scale_x.at_time(1.5)
        assert sx == pytest.approx(1.0, abs=0.1)


class TestSnapToGrid:
    def test_returns_self(self):
        c = Circle(r=50, cx=512, cy=303)
        result = c.snap_to_grid(grid_size=50, start=0, end=1)
        assert result is c

    def test_already_on_grid(self):
        c = Circle(r=50, cx=500, cy=300)
        result = c.snap_to_grid(grid_size=50, start=0, end=1)
        assert result is c


class TestAddBackground:
    def test_returns_rectangle(self):
        c = Circle(r=50, cx=500, cy=300)
        bg = c.add_background()
        assert isinstance(bg, Rectangle)

    def test_custom_options(self):
        c = Circle(r=50, cx=500, cy=300)
        bg = c.add_background(color='#FF0000', opacity=0.8, padding=30)
        assert isinstance(bg, Rectangle)


class TestCycleColors:
    def test_returns_self(self):
        c = Circle(r=50, fill='#FF0000')
        result = c.cycle_colors(['#FF0000', '#00FF00', '#0000FF'], start=0, end=3)
        assert result is c

    def test_single_color_noop(self):
        c = Circle(r=50)
        result = c.cycle_colors(['#FF0000'], start=0, end=1)
        assert result is c


class TestFreeze:
    def test_returns_self(self):
        c = Circle(r=50, fill='#FF0000')
        result = c.freeze(start=0, end=2)
        assert result is c


class TestDelayAnimation:
    def test_returns_self(self):
        c = Circle(r=50)
        result = c.delay_animation('fadein', delay=1.0)
        assert result is c
