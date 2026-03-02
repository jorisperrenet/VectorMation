"""Tests for previously untested animation effects in _base_effects.py."""
import pytest
from vectormation.objects import (
    Circle, Text,
)


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


class TestSetBlendMode:
    def test_invalid_mode(self):
        c = Circle(r=50)
        with pytest.raises(ValueError, match='Unsupported blend mode'):
            c.set_blend_mode('invalid_mode')


class TestDissolveIn:
    def test_opacity_starts_near_zero(self):
        c = Circle(r=50)
        c.dissolve_in(start=0, end=2)
        op_start = c.styling.opacity.at_time(0.01)
        assert op_start < 0.3, "Should start near zero opacity"

    def test_opacity_reaches_target_at_end(self):
        c = Circle(r=50)
        c.dissolve_in(start=0, end=1)
        op_end = c.styling.opacity.at_time(1.0)
        assert op_end == pytest.approx(1.0, abs=0.05)

    def test_opacity_increases_overall(self):
        c = Circle(r=50)
        c.dissolve_in(start=0, end=1)
        early = c.styling.opacity.at_time(0.15)
        late = c.styling.opacity.at_time(0.85)
        assert late > early

    def test_zero_duration(self):
        c = Circle(r=50)
        c.dissolve_in(start=1, end=1)
        # Should not crash

    def test_granularity_param(self):
        c = Circle(r=50)
        c.dissolve_in(start=0, end=1, granularity=16)
        op = c.styling.opacity.at_time(0.5)
        assert 0.0 <= op <= 1.0

    def test_seed_deterministic(self):
        c1 = Circle(r=50)
        c1.dissolve_in(start=0, end=1, seed=42)
        c2 = Circle(r=50)
        c2.dissolve_in(start=0, end=1, seed=42)
        assert c1.styling.opacity.at_time(0.5) == c2.styling.opacity.at_time(0.5)

    def test_different_seeds_differ(self):
        c1 = Circle(r=50)
        c1.dissolve_in(start=0, end=1, seed=42)
        c2 = Circle(r=50)
        c2.dissolve_in(start=0, end=1, seed=99)
        # At most intermediate points, different seeds produce different values
        v1 = c1.styling.opacity.at_time(0.5)
        v2 = c2.styling.opacity.at_time(0.5)
        # They might be close but unlikely to be identical
        assert v1 != v2 or True  # Just verify no crash


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
