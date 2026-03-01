"""Tests for SVG utility classes: ArrowVectorField, StreamLines, Image,
LinearGradient, RadialGradient, DynamicObject."""
import math
from vectormation.objects import (
    ArrowVectorField, StreamLines, Image, LinearGradient, RadialGradient,
    DynamicObject, Circle, Square, VectorMathAnim,
)


class TestArrowVectorField:
    def test_creation(self):
        avf = ArrowVectorField(lambda x, y: (-y, x),
                               x_range=(100, 500, 100), y_range=(100, 500, 100))
        assert avf is not None

    def test_has_arrows(self):
        avf = ArrowVectorField(lambda x, y: (1, 0),
                               x_range=(100, 400, 100), y_range=(100, 400, 100))
        assert len(avf.objects) > 0

    def test_renders(self):
        avf = ArrowVectorField(lambda x, y: (x, -y),
                               x_range=(200, 600, 200), y_range=(200, 600, 200))
        v = VectorMathAnim('/tmp')
        v.add(avf)
        svg = v.generate_frame_svg(0)
        assert len(svg) > 200

    def test_custom_max_length(self):
        avf = ArrowVectorField(lambda x, y: (100, 100),
                               x_range=(100, 300, 100), y_range=(100, 300, 100),
                               max_length=40)
        assert avf is not None

    def test_custom_style(self):
        avf = ArrowVectorField(lambda x, y: (1, 1),
                               x_range=(100, 300, 100), y_range=(100, 300, 100),
                               stroke='#ff0000')
        assert len(avf.objects) > 0

    def test_circular_field(self):
        avf = ArrowVectorField(lambda x, y: (-y + 500, x - 500),
                               x_range=(300, 700, 100), y_range=(300, 700, 100))
        assert len(avf.objects) >= 9

    def test_zero_vector_field(self):
        avf = ArrowVectorField(lambda x, y: (0, 0),
                               x_range=(100, 300, 100), y_range=(100, 300, 100))
        # Should handle zero vectors gracefully
        assert avf is not None


class TestStreamLines:
    def test_creation(self):
        sl = StreamLines(lambda x, y: (-y + 500, x - 500),
                         x_range=(100, 900, 200), y_range=(100, 900, 200))
        assert sl is not None

    def test_has_lines(self):
        sl = StreamLines(lambda x, y: (1, 0),
                         x_range=(100, 500, 200), y_range=(100, 500, 200))
        assert len(sl.objects) > 0

    def test_renders(self):
        sl = StreamLines(lambda x, y: (x - 500, y - 500),
                         x_range=(200, 800, 300), y_range=(200, 800, 300))
        v = VectorMathAnim('/tmp')
        v.add(sl)
        svg = v.generate_frame_svg(0)
        assert len(svg) > 200

    def test_custom_steps(self):
        sl = StreamLines(lambda x, y: (1, 0),
                         x_range=(100, 300, 200), y_range=(100, 300, 200),
                         n_steps=20, step_size=10)
        assert sl is not None


class TestImage:
    def test_creation(self):
        img = Image('test.png', x=100, y=100, width=200, height=150)
        assert img is not None

    def test_default_params(self):
        img = Image('file.svg')
        assert img.width.at_time(0) == 1
        assert img.height.at_time(0) == 1

    def test_renders_svg(self):
        img = Image('http://example.com/img.png', x=50, y=50,
                     width=300, height=200)
        v = VectorMathAnim('/tmp')
        v.add(img)
        svg = v.generate_frame_svg(0)
        assert '<image' in svg
        assert 'http://example.com/img.png' in svg

    def test_position_and_size(self):
        img = Image('test.png', x=100, y=200, width=400, height=300)
        assert img.x.at_time(0) == 100
        assert img.y.at_time(0) == 200
        assert img.width.at_time(0) == 400
        assert img.height.at_time(0) == 300

    def test_repr(self):
        img = Image('myfile.png')
        r = repr(img)
        assert 'Image' in r or 'VObject' in r


class TestLinearGradient:
    def test_creation(self):
        lg = LinearGradient([(0, '#ff0000'), (1, '#0000ff')])
        assert lg is not None

    def test_with_direction(self):
        lg = LinearGradient([(0, '#ff0000'), (0.5, '#00ff00'), (1, '#0000ff')],
                            x1='0%', y1='0%', x2='100%', y2='0%')
        assert lg is not None

    def test_renders_def(self):
        lg = LinearGradient([(0, '#ff0000'), (1, '#0000ff')])
        svg = lg.to_svg_def()
        assert '<linearGradient' in svg
        assert 'stop' in svg.lower()

    def test_has_auto_id(self):
        lg = LinearGradient([(0, '#000'), (1, '#fff')])
        assert lg.id.startswith('lg')

    def test_three_stops(self):
        lg = LinearGradient([(0, '#ff0000'), (0.5, '#00ff00'), (1, '#0000ff')])
        svg = lg.to_svg_def()
        assert svg.count('<stop') == 3


class TestRadialGradient:
    def test_creation(self):
        rg = RadialGradient([(0, '#ff0000'), (1, '#0000ff')])
        assert rg is not None

    def test_renders_def(self):
        rg = RadialGradient([(0, '#ff0000'), (1, '#0000ff')])
        svg = rg.to_svg_def()
        assert '<radialGradient' in svg
        assert 'stop' in svg.lower()

    def test_custom_center(self):
        rg = RadialGradient([(0, '#fff'), (1, '#000')],
                            cx='30%', cy='30%', r='70%')
        assert rg is not None

    def test_has_auto_id(self):
        rg = RadialGradient([(0, '#000'), (1, '#fff')])
        assert rg.id.startswith('rg')


class TestDynamicObject:
    def test_creation(self):
        do = DynamicObject(lambda t: Circle(r=30 + t * 10, cx=500, cy=500))
        assert do is not None

    def test_renders(self):
        do = DynamicObject(lambda t: Circle(r=30, cx=500, cy=500))
        v = VectorMathAnim('/tmp')
        v.add(do)
        svg = v.generate_frame_svg(0)
        assert '<circle' in svg or '<ellipse' in svg

    def test_changes_over_time(self):
        do = DynamicObject(lambda t: Square(30 + t * 50))
        v = VectorMathAnim('/tmp')
        v.add(do)
        svg0 = v.generate_frame_svg(0)
        svg2 = v.generate_frame_svg(2)
        # The SVG should differ because the square size changes
        assert svg0 != svg2
