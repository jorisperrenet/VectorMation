"""Extended tests for _base_effects.py methods: connect, bind_to, homotopy, etc."""
import pytest
from vectormation.objects import Circle, Rectangle, Text, VCollection
from vectormation._constants import LEFT, RIGHT, UP, DOWN


class TestConnect:
    def test_line(self):
        a = Circle(r=30, cx=100, cy=100)
        b = Circle(r=30, cx=300, cy=100)
        line = a.connect(b, start=0)
        svg = line.to_svg(0)
        assert 'line' in svg.lower()

    def test_arrow(self):
        a = Circle(r=30, cx=100, cy=100)
        b = Circle(r=30, cx=300, cy=100)
        arrow = a.connect(b, arrow=True, start=0)
        assert arrow is not None

    def test_follow(self):
        a = Circle(r=30, cx=100, cy=100)
        b = Circle(r=30, cx=300, cy=100)
        line = a.connect(b, follow=True, start=0)
        assert line is not None


class TestMatchStyle:
    def test_basic(self):
        a = Circle(r=30, fill='#FF0000')
        b = Circle(r=30, fill='#0000FF')
        result = a.match_style(b)
        assert result is a


class TestMatchPosition:
    def test_basic(self):
        a = Circle(r=30, cx=100, cy=100)
        b = Circle(r=30, cx=500, cy=300)
        result = a.match_position(b)
        assert result is a


class TestScaleToFit:
    def test_width(self):
        r = Rectangle(200, 100, x=100, y=100)
        result = r.scale_to_fit(width=100)
        assert result is r

    def test_height(self):
        r = Rectangle(200, 100, x=100, y=100)
        result = r.scale_to_fit(height=50)
        assert result is r

    def test_both(self):
        r = Rectangle(200, 100, x=100, y=100)
        result = r.scale_to_fit(width=100, height=50)
        assert result is r


class TestTelegraph:
    def test_basic(self):
        c = Circle(r=50)
        result = c.telegraph(start=0, end=1)
        assert result is c

    def test_zero_duration(self):
        c = Circle(r=50)
        result = c.telegraph(start=1, end=1)
        assert result is c


class TestSkate:
    def test_basic(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.skate(500, 300, start=0, end=1)
        assert result is c


class TestFlicker:
    def test_basic(self):
        c = Circle(r=50)
        result = c.flicker(start=0, end=1)
        assert result is c


class TestSlingshot:
    def test_basic(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.slingshot(500, 300, start=0, end=1)
        assert result is c


class TestDomino:
    def test_left(self):
        r = Rectangle(50, 100, x=100, y=100)
        result = r.domino(start=0, end=1, direction='left')
        assert result is r

    def test_right(self):
        r = Rectangle(50, 100, x=100, y=100)
        result = r.domino(start=0, end=1, direction='right')
        assert result is r


class TestStampTrail:
    def test_basic(self):
        c = Circle(r=30, cx=100, cy=100)
        c.shift(dx=200, start=0, end=2)
        ghosts = c.stamp_trail(start=0, end=2, count=3)
        assert isinstance(ghosts, list)
        assert len(ghosts) == 3

    def test_zero_count(self):
        c = Circle(r=30)
        ghosts = c.stamp_trail(count=0)
        assert ghosts == []


class TestUnfold:
    def test_right(self):
        r = Rectangle(100, 50, x=100, y=100)
        result = r.unfold(start=0, end=1, direction='right')
        assert result is r

    def test_down(self):
        r = Rectangle(100, 50, x=100, y=100)
        result = r.unfold(start=0, end=1, direction='down')
        assert result is r


class TestGlitchShift:
    def test_basic(self):
        c = Circle(r=50)
        result = c.glitch_shift(start=0, end=1, steps=4)
        assert result is c


class TestWaveThrough:
    def test_y(self):
        c = Circle(r=50)
        result = c.wave_through(start=0, end=1, direction='y')
        assert result is c

    def test_x(self):
        c = Circle(r=50)
        result = c.wave_through(start=0, end=1, direction='x')
        assert result is c


class TestCountdown:
    def test_basic(self):
        t = Text(text='3', x=100, y=100)
        result = t.countdown(start=0, end=3, from_val=3)
        assert result is t

    def test_not_text_raises(self):
        c = Circle(r=50)
        with pytest.raises(TypeError, match="Text objects"):
            c.countdown()


class TestSqueeze:
    def test_x(self):
        c = Circle(r=50)
        result = c.squeeze(start=0, end=1, axis='x')
        assert result is c

    def test_y(self):
        c = Circle(r=50)
        result = c.squeeze(start=0, end=1, axis='y')
        assert result is c


class TestBindTo:
    def test_basic(self):
        a = Circle(r=30, cx=100, cy=100)
        b = Circle(r=30, cx=300, cy=300)
        result = a.bind_to(b)
        assert result is a


class TestPinTo:
    def test_center(self):
        a = Circle(r=30)
        b = Rectangle(100, 50, x=400, y=200)
        result = a.pin_to(b, edge='center')
        assert result is a


class TestDuplicate:
    def test_basic(self):
        c = Circle(r=30)
        copies = c.duplicate(count=3)
        assert isinstance(copies, VCollection)
        assert len(copies) == 3


class TestSetDashPattern:
    def test_presets(self):
        c = Circle(r=50)
        for p in ('dashes', 'dots', 'dash_dot', 'solid'):
            result = c.set_dash_pattern(p)
            assert result is c

    def test_custom(self):
        c = Circle(r=50)
        result = c.set_dash_pattern('15 10 5 10')
        assert result is c


class TestShowIf:
    def test_basic(self):
        c = Circle(r=50)
        result = c.show_if(lambda t: t > 1, start=0)
        assert result is c


class TestSetGradientFill:
    def test_horizontal(self):
        c = Circle(r=50)
        result = c.set_gradient_fill(['#FF0000', '#0000FF'])
        assert result is c

    def test_vertical(self):
        c = Circle(r=50)
        result = c.set_gradient_fill(['#FF0000', '#0000FF'], direction='vertical')
        assert result is c

    def test_radial(self):
        c = Circle(r=50)
        result = c.set_gradient_fill(['#FF0000', '#0000FF'], direction='radial')
        assert result is c


class TestSetLifetime:
    def test_basic(self):
        c = Circle(r=50)
        result = c.set_lifetime(1, 3)
        assert result is c


class TestGetStyle:
    def test_returns_dict(self):
        c = Circle(r=50, fill='#FF0000')
        s = c.get_style()
        assert isinstance(s, dict)
        assert 'fill' in s
        assert 'stroke' in s


class TestMoveTowards:
    def test_basic(self):
        a = Circle(r=30, cx=100, cy=100)
        b = Circle(r=30, cx=500, cy=500)
        result = a.move_towards(b, fraction=0.5)
        assert result is a


class TestAddLabel:
    def test_basic(self):
        c = Circle(r=50)
        result = c.add_label('hello')
        assert isinstance(result, VCollection)

    def test_follow(self):
        c = Circle(r=50)
        result = c.add_label('test', follow=True)
        assert isinstance(result, VCollection)


class TestPlaceBetween:
    def test_basic(self):
        a = Circle(r=30, cx=100, cy=100)
        b = Circle(r=30, cx=500, cy=500)
        c = Circle(r=30)
        result = c.place_between(a, b)
        assert result is c


class TestHomotopy:
    def test_basic(self):
        c = Circle(r=50, cx=500, cy=300)
        result = c.homotopy(lambda x, y, t: (x + 100 * t, y + 50 * t), start=0, end=1)
        assert result is c


class TestWobble:
    def test_basic(self):
        c = Circle(r=50)
        result = c.wobble(start=0, end=1)
        assert result is c


class TestTypewriterEffect:
    def test_basic(self):
        t = Text(text='', x=100, y=100)
        result = t.typewriter_effect('Hello World', start=0, end=1)
        assert result is t

    def test_renders(self):
        t = Text(text='', x=100, y=100)
        t.typewriter_effect('Hello', start=0, end=1)
        svg = t.to_svg(0.5)
        assert svg is not None


class TestTypewriterCursor:
    def test_basic(self):
        t = Text(text='Hello', x=100, y=100)
        result = t.typewriter_cursor(start=0, end=2)
        assert result is t


class TestLookAt:
    def test_point(self):
        c = Circle(r=50, cx=100, cy=100)
        result = c.look_at((500, 300))
        assert result is c

    def test_object(self):
        a = Circle(r=50, cx=100, cy=100)
        b = Circle(r=50, cx=500, cy=300)
        result = a.look_at(b)
        assert result is a


class TestAnimateTo:
    def test_basic(self):
        a = Circle(r=50, cx=100, cy=100, fill='#FF0000')
        b = Circle(r=100, cx=500, cy=300, fill='#0000FF')
        result = a.animate_to(b, start=0, end=1)
        assert result is a


class TestSetClip:
    def test_basic(self):
        c = Circle(r=50, cx=500, cy=300)
        mask = Rectangle(100, 100, x=450, y=250)
        result = c.set_clip(mask)
        assert result is c


class TestPassingFlash:
    def test_basic(self):
        c = Circle(r=50)
        result = c.passing_flash(start=0, end=1)
        assert result is c


class TestScaleInPlace:
    def test_basic(self):
        c = Circle(r=50, cx=500, cy=300)
        result = c.scale_in_place(2, start=0, end=1)
        assert result is c


class TestApplyWave:
    def test_basic(self):
        c = Circle(r=50)
        result = c.apply_wave(start=0, end=1)
        assert result is c


class TestFocusZoom:
    def test_basic(self):
        c = Circle(r=50)
        result = c.focus_zoom(start=0, end=1)
        assert result is c


class TestParallax:
    def test_basic(self):
        c = Circle(r=50)
        result = c.parallax(100, 50, start=0, end=1)
        assert result is c


class TestDirectionTupleNormalization:
    """Ensure methods accept tuple direction constants (UP, DOWN, LEFT, RIGHT)."""

    def test_domino_left_tuple(self):
        r = Rectangle(50, 100, x=100, y=100)
        assert r.domino(start=0, end=1, direction=LEFT) is r

    def test_domino_right_tuple(self):
        r = Rectangle(50, 100, x=100, y=100)
        assert r.domino(start=0, end=1, direction=RIGHT) is r

    def test_unfold_left_tuple(self):
        r = Rectangle(100, 50, x=100, y=100)
        assert r.unfold(start=0, end=1, direction=LEFT) is r

    def test_unfold_right_tuple(self):
        r = Rectangle(100, 50, x=100, y=100)
        assert r.unfold(start=0, end=1, direction=RIGHT) is r

    def test_unfold_up_tuple(self):
        r = Rectangle(100, 50, x=100, y=100)
        assert r.unfold(start=0, end=1, direction=UP) is r

    def test_unfold_down_tuple(self):
        r = Rectangle(100, 50, x=100, y=100)
        assert r.unfold(start=0, end=1, direction=DOWN) is r

    def test_wipe_left_tuple(self):
        r = Rectangle(100, 50, x=100, y=100)
        assert r.wipe(direction=LEFT, start=0, end=1) is r

    def test_wipe_right_tuple(self):
        r = Rectangle(100, 50, x=100, y=100)
        assert r.wipe(direction=RIGHT, start=0, end=1) is r

    def test_wipe_up_tuple(self):
        r = Rectangle(100, 50, x=100, y=100)
        assert r.wipe(direction=UP, start=0, end=1) is r

    def test_wipe_down_tuple(self):
        r = Rectangle(100, 50, x=100, y=100)
        assert r.wipe(direction=DOWN, start=0, end=1) is r

    def test_slide_in_left_tuple(self):
        r = Rectangle(100, 50, x=100, y=100)
        assert r.slide_in(direction=LEFT, start=0, end=1) is r

    def test_slide_in_right_tuple(self):
        r = Rectangle(100, 50, x=100, y=100)
        assert r.slide_in(direction=RIGHT, start=0, end=1) is r

    def test_slide_in_up_tuple(self):
        r = Rectangle(100, 50, x=100, y=100)
        assert r.slide_in(direction=UP, start=0, end=1) is r

    def test_slide_in_down_tuple(self):
        r = Rectangle(100, 50, x=100, y=100)
        assert r.slide_in(direction=DOWN, start=0, end=1) is r

    def test_slide_out_left_tuple(self):
        r = Rectangle(100, 50, x=100, y=100)
        assert r.slide_out(direction=LEFT, start=0, end=1) is r

    def test_slide_out_right_tuple(self):
        r = Rectangle(100, 50, x=100, y=100)
        assert r.slide_out(direction=RIGHT, start=0, end=1) is r



class TestPointFromProportion:
    def test_midpoint(self):
        from vectormation.objects import Line
        l = Line(x1=0, y1=0, x2=100, y2=0)
        pt = l.point_from_proportion(0.5)
        assert pt[0] == pytest.approx(50, abs=5)
