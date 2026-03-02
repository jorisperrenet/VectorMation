"""Tests for previously untested _base_effects methods."""
from vectormation.objects import Circle, Rectangle, Text


class TestTypewriterEffect:
    def test_full_text_at_end(self):
        t = Text(text='', x=100, y=100)
        t.typewriter_effect('Hello', start=0, end=1)
        svg = t.to_svg(1)
        assert 'Hello' in svg


class TestAddLabel:
    def test_basic(self):
        c = Circle(r=30, cx=200, cy=200)
        group = c.add_label('My Circle')
        svg = group.to_svg(0)
        assert 'My Circle' in svg

    def test_custom_direction(self):
        c = Circle(r=30, cx=200, cy=200)
        group = c.add_label('Test', direction=(1, 0))  # RIGHT
        svg = group.to_svg(0)
        assert 'Test' in svg

    def test_custom_font_size(self):
        c = Circle(r=30, cx=200, cy=200)
        group = c.add_label('Big', font_size=32)
        svg = group.to_svg(0)
        assert 'Big' in svg

    def test_follow(self):
        c = Circle(r=30, cx=200, cy=200)
        group = c.add_label('Follow', follow=True)
        svg = group.to_svg(0)
        assert 'Follow' in svg


class TestSetClip:
    def test_basic(self):
        rect = Rectangle(width=200, height=200, x=100, y=100, fill='#FF0000')
        clip = Circle(r=80, cx=200, cy=200)
        rect.set_clip(clip, start=0)
        svg = rect.to_svg(0)
        assert 'clipPath' in svg

    def test_with_rectangle_clip(self):
        c = Circle(r=100, cx=200, cy=200, fill='#00FF00')
        clip = Rectangle(width=100, height=100, x=150, y=150)
        c.set_clip(clip, start=0)
        svg = c.to_svg(0)
        assert 'clipPath' in svg
