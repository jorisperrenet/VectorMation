"""Tests for vectormation.colors: color_from_name, gradients."""
import pytest
from vectormation.colors import color_from_name, LinearGradient, RadialGradient, color_gradient, interpolate_color


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
