"""Tests for vectormation.style.Styling."""
import pytest
from vectormation.style import Styling


class TestStyling:
    def test_default_svg_style(self):
        s = Styling({}, creation=0)
        style = s.svg_style(0)
        # Attributes matching their SVG spec default are omitted.
        # stroke is always emitted (SVG default is 'none').
        # stroke_width=4 is always emitted (SVG default is 1).
        assert 'opacity' not in style or "opacity='1'" not in style
        assert "stroke='rgb(0,0,0)'" in style
        assert "stroke-width='4'" in style

    def test_custom_fill(self):
        s = Styling({'fill': '#ff0000'}, creation=0)
        style = s.svg_style(0)
        assert "fill='rgb(255,0,0)'" in style

    def test_custom_stroke_width(self):
        s = Styling({'stroke_width': 7}, creation=0)
        style = s.svg_style(0)
        assert "stroke-width='7'" in style

    def test_transform_rotation(self):
        s = Styling({'rotation': (45, 100, 100)}, creation=0)
        transform = s.transform_style(0)
        assert 'rotate(315' in transform  # 45° CCW → -45 mod 360 = 315° in SVG

    def test_transform_scale(self):
        s = Styling({'scale_x': 2, 'scale_y': 2}, creation=0)
        transform = s.transform_style(0)
        assert 'scale(2,2)' in transform

    def test_no_transform_default(self):
        s = Styling({}, creation=0)
        transform = s.transform_style(0)
        assert transform == ''

    def test_last_change(self):
        s = Styling({}, creation=0)
        assert s.last_change == 0
        s.opacity.move_to(0, 5, 0)
        assert s.last_change == 5

    def test_kwargs_roundtrip(self):
        s = Styling({'fill': '#ff0000', 'stroke_width': 3}, creation=0)
        kw = s.kwargs()
        assert 'fill' in kw
        assert 'stroke_width' in kw

    def test_transform_translate(self):
        s = Styling({'dx': 100, 'dy': 50}, creation=0)
        transform = s.transform_style(0)
        assert 'translate(100,50)' in transform

    def test_transform_skew(self):
        s = Styling({'skew_x': 30}, creation=0)
        transform = s.transform_style(0)
        assert 'skewX(30)' in transform

    def test_transform_skew_y(self):
        s = Styling({'skew_y': 20}, creation=0)
        transform = s.transform_style(0)
        assert 'skewY(20)' in transform

    def test_transform_matrix(self):
        s = Styling({'matrix': (1, 0, 0, 1, 50, 50)}, creation=0)
        transform = s.transform_style(0)
        assert 'matrix(1,0,0,1,50,50)' in transform

    def test_svg_style_with_gradient_fill(self):
        from vectormation.colors import LinearGradient
        lg = LinearGradient([('0%', '#f00'), ('100%', '#00f')])
        s = Styling({'fill': lg}, creation=0)
        svg = s.svg_style(0)
        assert 'url(#' in svg

    def test_svg_style_with_opacity(self):
        s = Styling({'opacity': 0.5}, creation=0)
        svg = s.svg_style(0)
        assert "opacity='0.5'" in svg

    def test_svg_style_with_fill_opacity(self):
        s = Styling({'fill_opacity': 0.3}, creation=0)
        svg = s.svg_style(0)
        assert "fill-opacity='0.3'" in svg

    def test_svg_style_with_stroke_dasharray(self):
        s = Styling({'stroke_dasharray': '5,10'}, creation=0)
        svg = s.svg_style(0)
        assert "stroke-dasharray='5,10'" in svg
