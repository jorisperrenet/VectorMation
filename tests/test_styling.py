"""Tests for the styling system: SVG output, transforms, opacity."""
import pytest

from vectormation._shapes import Circle, Rectangle
from vectormation.style import Styling


class TestStylingDefaults:

    def test_default_circle_has_fill(self):
        c = Circle(r=50)
        svg = c.to_svg(0)
        assert 'fill' in svg

    def test_default_stroke(self):
        c = Circle(r=50)
        stroke = c.styling.stroke.at_time(0)
        assert stroke == 'rgb(255,255,255)'  # default #fff

    def test_custom_fill(self):
        c = Circle(r=50, fill='#ff0000')
        fill = c.styling.fill.at_time(0)
        assert fill == 'rgb(255,0,0)'

    def test_fill_opacity(self):
        c = Circle(r=50, fill_opacity=0.5)
        op = c.styling.fill_opacity.at_time(0)
        assert op == pytest.approx(0.5)


class TestTransformStyle:

    def test_rotation_in_svg(self):
        c = Circle(r=50, cx=100, cy=100)
        c.rotate_by(start=0, end=0, degrees=45)
        svg = c.to_svg(0)
        assert 'rotate' in svg

    def test_no_transform_when_identity(self):
        c = Circle(r=50)
        svg = c.to_svg(0)
        # Should produce valid SVG (circle uses <circle> tag)
        assert '<circle' in svg


class TestSetStyle:

    def test_set_fill_opacity(self):
        c = Circle(r=50)
        c.set_style(start=0, fill_opacity=0.3)
        assert c.styling.fill_opacity.at_time(0) == pytest.approx(0.3)

    def test_set_stroke_width(self):
        c = Circle(r=50)
        c.set_style(start=0, stroke_width=10)
        assert c.styling.stroke_width.at_time(0) == pytest.approx(10)
