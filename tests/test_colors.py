"""Tests for vectormation.colors: color_from_name, gradients, color harmony."""
import pytest
from vectormation.colors import (
    color_from_name, LinearGradient, RadialGradient, color_gradient,
    interpolate_color, triadic, analogous, split_complementary,
    _hex_to_hsl,
)


class TestColorFromName:
    def test_known_colors(self):
        assert color_from_name('WHITE') == '#FFFFFF'
        assert color_from_name('RED') == '#FC6255'
        assert color_from_name('BLUE') == '#58C4DD'
        assert color_from_name('GREEN') == '#83C167'
        assert color_from_name('YELLOW') == '#FFFF00'

    def test_unknown_color_raises(self):
        with pytest.raises(ValueError):
            color_from_name('NONEXISTENT')

    def test_grey_aliases(self):
        assert color_from_name('GRAY') == color_from_name('GREY')
        assert color_from_name('GRAY_A') == color_from_name('GREY_A')


class TestLinearGradient:
    def test_to_svg_def(self):
        lg = LinearGradient([('0%', '#f00'), ('100%', '#00f')])
        svg = lg.to_svg_def()
        assert '<linearGradient' in svg
        assert '</linearGradient>' in svg
        assert "stop-color='#f00'" in svg
        assert "stop-color='#00f'" in svg

    def test_fill_ref(self):
        lg = LinearGradient([('0%', '#f00'), ('100%', '#00f')])
        ref = lg.fill_ref()
        assert ref.startswith('url(#')
        assert ref.endswith(')')


class TestRadialGradient:
    def test_to_svg_def(self):
        rg = RadialGradient([('0%', '#fff'), ('100%', '#000')])
        svg = rg.to_svg_def()
        assert '<radialGradient' in svg
        assert '</radialGradient>' in svg
        assert "stop-color='#fff'" in svg

    def test_fill_ref(self):
        rg = RadialGradient([('0%', '#fff'), ('100%', '#000')])
        ref = rg.fill_ref()
        assert ref.startswith('url(#')


class TestColorGradient:
    def test_basic_gradient(self):
        result = color_gradient('#000000', '#ffffff', 3)
        assert len(result) == 3
        assert result[0] == '#000000'
        assert result[2] == '#ffffff'

    def test_midpoint(self):
        result = color_gradient('#000000', '#ffffff', 3)
        # Midpoint should be gray
        assert result[1] in ('#7f7f7f', '#808080', '#7f7f7f')

    def test_named_colors(self):
        result = color_gradient('RED', 'BLUE', 5)
        assert len(result) == 5


class TestInterpolateColor:
    def test_start(self):
        assert interpolate_color('#000000', '#ffffff', 0) == '#000000'

    def test_end(self):
        result = interpolate_color('#000000', '#ffffff', 1)
        assert result in ('#ffffff', '#fefefe', '#ffffff')

    def test_named(self):
        result = interpolate_color('RED', 'BLUE', 0.5)
        assert isinstance(result, str)
        assert result.startswith('#')


class TestTriadic:
    def test_returns_two_colors(self):
        result = triadic('#ff0000')
        assert len(result) == 2
        assert all(c.startswith('#') for c in result)

    def test_hue_offsets(self):
        # Pure red hue=0, triadic should give hue=120 and hue=240
        colors = triadic('#ff0000')
        h1 = _hex_to_hsl(colors[0])[0]
        h2 = _hex_to_hsl(colors[1])[0]
        assert h1 == pytest.approx(120, abs=2)
        assert h2 == pytest.approx(240, abs=2)


class TestAnalogous:
    def test_returns_two_colors(self):
        result = analogous('#ff0000')
        assert len(result) == 2
        assert all(c.startswith('#') for c in result)

    def test_custom_angle(self):
        result = analogous('#ff0000', angle=45)
        assert len(result) == 2
        h1 = _hex_to_hsl(result[0])[0]
        h2 = _hex_to_hsl(result[1])[0]
        # hue 0 - 45 = 315, hue 0 + 45 = 45
        assert h1 == pytest.approx(315, abs=2)
        assert h2 == pytest.approx(45, abs=2)

    def test_default_angle(self):
        result = analogous('#ff0000')
        h1 = _hex_to_hsl(result[0])[0]
        h2 = _hex_to_hsl(result[1])[0]
        assert h1 == pytest.approx(330, abs=2)
        assert h2 == pytest.approx(30, abs=2)


class TestSplitComplementary:
    def test_returns_two_colors(self):
        result = split_complementary('#ff0000')
        assert len(result) == 2
        assert all(c.startswith('#') for c in result)

    def test_hue_offsets(self):
        # Pure red hue=0, split complementary = hue+150 and hue+210
        colors = split_complementary('#ff0000')
        h1 = _hex_to_hsl(colors[0])[0]
        h2 = _hex_to_hsl(colors[1])[0]
        assert h1 == pytest.approx(150, abs=2)
        assert h2 == pytest.approx(210, abs=2)
