"""Tests for previously untested _base_effects methods."""
import math
from vectormation.objects import Circle, Rectangle, Text, Dot


class TestUnfold:
    def test_basic(self):
        r = Rectangle(width=100, height=50, x=100, y=100)
        r.unfold(start=0, end=1)
        svg = r.to_svg(0.5)
        assert svg is not None

    def test_directions(self):
        for d in ('right', 'left', 'down', 'up'):
            r = Rectangle(width=80, height=60, x=200, y=200)
            r.unfold(start=0, end=1, direction=d)
            svg = r.to_svg(0.5)
            assert svg is not None

    def test_zero_duration(self):
        r = Rectangle(width=80, height=60, x=200, y=200)
        result = r.unfold(start=1, end=1)
        assert result is r  # returns self on zero duration

    def test_no_change_existence(self):
        r = Rectangle(width=80, height=60, x=200, y=200)
        r.unfold(start=0, end=1, change_existence=False)
        svg = r.to_svg(0.5)
        assert svg is not None


class TestTiltTowards:
    def test_basic(self):
        c = Circle(r=30, cx=100, cy=100)
        c.tilt_towards(200, 200, start=0, end=1)
        svg = c.to_svg(0.5)
        assert svg is not None

    def test_negative_tilt(self):
        c = Circle(r=30, cx=100, cy=200)
        c.tilt_towards(200, 100, start=0, end=1)  # target above
        svg = c.to_svg(0.5)
        assert svg is not None

    def test_custom_max_angle(self):
        c = Circle(r=30, cx=100, cy=100)
        c.tilt_towards(200, 300, max_angle=45, start=0, end=1)
        svg = c.to_svg(0.5)
        assert svg is not None


class TestCycleColors:
    def test_basic(self):
        c = Circle(r=30, cx=100, cy=100, fill='#FF0000')
        c.cycle_colors(['#FF0000', '#00FF00', '#0000FF'], start=0, end=2)
        svg = c.to_svg(1)
        assert svg is not None

    def test_two_colors(self):
        c = Circle(r=30, cx=100, cy=100)
        c.cycle_colors(['#FF0000', '#0000FF'], start=0, end=1)
        svg = c.to_svg(0.5)
        assert svg is not None

    def test_single_color_noop(self):
        c = Circle(r=30, cx=100, cy=100)
        result = c.cycle_colors(['#FF0000'], start=0, end=1)
        assert result is c  # < 2 colors, returns self


class TestFreeze:
    def test_basic(self):
        c = Circle(r=30, cx=100, cy=100, fill='#FF0000')
        c.freeze(start=0.5, end=2)
        svg = c.to_svg(1)
        assert svg is not None

    def test_no_end(self):
        c = Circle(r=30, cx=100, cy=100)
        c.freeze(start=1)
        svg = c.to_svg(2)
        assert svg is not None


class TestDelayAnimation:
    def test_basic(self):
        c = Circle(r=30, cx=100, cy=100)
        c.delay_animation('fadein', delay=2, start=0, end=1)
        svg = c.to_svg(2.5)
        assert svg is not None

    def test_shift(self):
        c = Circle(r=30, cx=100, cy=100)
        c.delay_animation('shift', delay=1, dx=50, start=0, end=1)
        svg = c.to_svg(1.5)
        assert svg is not None


class TestWobble:
    def test_basic(self):
        c = Circle(r=30, cx=100, cy=100)
        c.wobble(start=0, end=2)
        svg = c.to_svg(1)
        assert svg is not None

    def test_custom_params(self):
        c = Circle(r=30, cx=100, cy=100)
        c.wobble(start=0, end=1, amplitude=10, frequency=5)
        svg = c.to_svg(0.5)
        assert svg is not None

    def test_zero_duration(self):
        c = Circle(r=30, cx=100, cy=100)
        result = c.wobble(start=1, end=1)
        assert result is c


class TestTypewriterEffect:
    def test_basic(self):
        t = Text(text='', x=100, y=100)
        t.typewriter_effect('Hello World', start=0, end=2)
        svg = t.to_svg(1)
        assert svg is not None

    def test_partial_reveal(self):
        t = Text(text='', x=100, y=100)
        t.typewriter_effect('ABCDE', start=0, end=1)
        # At midpoint should show partial text
        svg = t.to_svg(0.5)
        assert svg is not None

    def test_empty_text(self):
        t = Text(text='', x=100, y=100)
        result = t.typewriter_effect('', start=0, end=1)
        assert result is t  # empty text returns self

    def test_full_text_at_end(self):
        t = Text(text='', x=100, y=100)
        t.typewriter_effect('Hello', start=0, end=1)
        svg = t.to_svg(1)
        assert 'Hello' in svg


class TestLookAt:
    def test_basic(self):
        c = Circle(r=30, cx=100, cy=100)
        c.look_at((500, 500), start=0)
        svg = c.to_svg(0)
        assert svg is not None

    def test_look_at_object(self):
        c = Circle(r=30, cx=100, cy=100)
        target = Dot(cx=500, cy=500)
        c.look_at(target, start=0)
        svg = c.to_svg(0)
        assert svg is not None

    def test_with_end(self):
        c = Circle(r=30, cx=100, cy=100)
        c.look_at((500, 500), start=0, end=1)
        svg = c.to_svg(0.5)
        assert svg is not None


class TestAnimateTo:
    def test_basic(self):
        src = Circle(r=30, cx=100, cy=100, fill='#FF0000')
        target = Circle(r=60, cx=500, cy=500, fill='#0000FF')
        src.animate_to(target, start=0, end=2)
        svg = src.to_svg(1)
        assert svg is not None

    def test_same_size(self):
        src = Rectangle(width=100, height=50, x=100, y=100)
        target = Rectangle(width=100, height=50, x=500, y=500)
        src.animate_to(target, start=0, end=1)
        svg = src.to_svg(0.5)
        assert svg is not None


class TestMoveTowards:
    def test_basic(self):
        c = Circle(r=30, cx=100, cy=100)
        target = Dot(cx=500, cy=500)
        c.move_towards(target, fraction=0.5, start=0)
        svg = c.to_svg(0)
        assert svg is not None

    def test_with_tuple(self):
        c = Circle(r=30, cx=100, cy=100)
        c.move_towards((500, 500), fraction=0.3, start=0)
        svg = c.to_svg(0)
        assert svg is not None

    def test_full_move(self):
        c = Circle(r=30, cx=100, cy=100)
        c.move_towards((500, 500), fraction=1.0, start=0, end=1)
        svg = c.to_svg(0.5)
        assert svg is not None


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


class TestPlaceBetween:
    def test_basic(self):
        a = Dot(cx=100, cy=100)
        b = Dot(cx=500, cy=500)
        c = Circle(r=20, cx=0, cy=0)
        c.place_between(a, b, start=0)
        svg = c.to_svg(0)
        assert svg is not None

    def test_with_tuples(self):
        c = Circle(r=20, cx=0, cy=0)
        c.place_between((100, 100), (500, 500), fraction=0.25, start=0)
        svg = c.to_svg(0)
        assert svg is not None

    def test_animated(self):
        c = Circle(r=20, cx=0, cy=0)
        c.place_between((100, 100), (500, 500), start=0, end=1)
        svg = c.to_svg(0.5)
        assert svg is not None


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


class TestApplyWave:
    def test_basic(self):
        r = Rectangle(width=200, height=100, x=100, y=100)
        r.apply_wave(start=0, end=2)
        svg = r.to_svg(1)
        assert svg is not None

    def test_custom_amplitude(self):
        r = Rectangle(width=200, height=100, x=100, y=100)
        r.apply_wave(start=0, end=1, amplitude=50)
        svg = r.to_svg(0.5)
        assert svg is not None

    def test_x_direction(self):
        r = Rectangle(width=200, height=100, x=100, y=100)
        r.apply_wave(start=0, end=1, direction='x')
        svg = r.to_svg(0.5)
        assert svg is not None

    def test_zero_duration(self):
        r = Rectangle(width=200, height=100, x=100, y=100)
        result = r.apply_wave(start=1, end=1)
        assert result is r

    def test_custom_wave_func(self):
        r = Rectangle(width=200, height=100, x=100, y=100)
        r.apply_wave(start=0, end=1, wave_func=math.cos)
        svg = r.to_svg(0.5)
        assert svg is not None
