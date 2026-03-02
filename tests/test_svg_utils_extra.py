"""Tests for SVG utility classes: Image, LinearGradient, DynamicObject."""
from vectormation.objects import (
    Image, LinearGradient,
    DynamicObject, Square, Text, VectorMathAnim,
)


class TestImage:
    def test_position_and_size(self):
        img = Image('test.png', x=100, y=200, width=400, height=300)
        assert img.x.at_time(0) == 100
        assert img.y.at_time(0) == 200
        assert img.width.at_time(0) == 400
        assert img.height.at_time(0) == 300

    def test_href_xml_escape(self):
        """Image href with special chars should be properly escaped."""
        img = Image("file.png?a=1&b=2", x=0, y=0, width=100, height=100)
        svg = img.to_svg(0)
        assert '&amp;' in svg
        assert '&b=2' not in svg  # raw & should be escaped

    def test_font_family_escape(self):
        """Text with special chars in font-family should be escaped."""
        t = Text(text='hi', font_family="O'Reilly")
        svg = t.to_svg(0)
        assert '&apos;' in svg


class TestLinearGradient:
    def test_three_stops(self):
        lg = LinearGradient([(0, '#ff0000'), (0.5, '#00ff00'), (1, '#0000ff')])
        svg = lg.to_svg_def()
        assert svg.count('<stop') == 3


class TestDynamicObject:
    def test_changes_over_time(self):
        do = DynamicObject(lambda t: Square(30 + t * 50))
        v = VectorMathAnim('/tmp')
        v.add(do)
        svg0 = v.generate_frame_svg(0)
        svg2 = v.generate_frame_svg(2)
        # The SVG should differ because the square size changes
        assert svg0 != svg2
