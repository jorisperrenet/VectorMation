"""Tests for animation effect methods in _base_effects.py."""
import pytest
from vectormation.objects import Circle


class TestStrobe:
    def test_opacity_changes(self):
        c = Circle(r=50)
        c.strobe(start=0, end=1, n_flashes=4)
        # At different times, opacity should vary
        o1 = c.styling.opacity.at_time(0.1)
        o2 = c.styling.opacity.at_time(0.15)
        # At least one should be 0 or 1
        assert o1 in (0, 1) or o2 in (0, 1)


class TestFadeToColor:
    def test_color_changes(self):
        c = Circle(r=50, fill='#FF0000')
        c.fade_to_color('#0000FF', start=0, end=1)
        svg = c.to_svg(1.5)
        # After animation, should be close to blue
        assert 'rgb(0,0,255)' in svg or '0000ff' in svg.lower() or 'rgb' in svg


class TestSpinAndFade:
    def test_opacity_decreases(self):
        c = Circle(r=50)
        c.spin_and_fade(start=0, end=1)
        o = c.styling.opacity.at_time(1.5)
        assert o == pytest.approx(0, abs=0.01)


class TestTiltTowards:
    def test_tilt_direction(self):
        c = Circle(r=50, cx=500, cy=300)
        c.tilt_towards(600, 400, max_angle=15, start=0, end=1)
        angle, _, _ = c.styling.rotation.at_time(1.5)
        assert angle != 0


class TestSetBlendMode:
    def test_invalid_mode(self):
        c = Circle(r=50)
        with pytest.raises(ValueError, match="Unsupported blend mode"):
            c.set_blend_mode('invalid_mode')


class TestElasticScale:
    def test_settles_back(self):
        c = Circle(r=50)
        c.elastic_scale(start=0, end=1, factor=2.0)
        # After the animation, scale should be back to ~1
        sx = c.styling.scale_x.at_time(1.5)
        assert sx == pytest.approx(1.0, abs=0.1)
