"""Tests for TexCountAnimation, add_label, add_background, match_width/height,
place_between, animate_to, move_towards, look_at, and other misc methods."""
from vectormation.objects import (
    Circle, Square, Rectangle, Dot, Text, VectorMathAnim,
    TexCountAnimation, CountAnimation, DynamicObject,
)


# ── TexCountAnimation ──────────────────────────────────────────

class TestTexCountAnimation:
    def test_creation(self):
        tca = TexCountAnimation(start_val=0, end_val=10, start=0, end=2)
        assert tca is not None

    def test_repr(self):
        tca = TexCountAnimation(start_val=0, end_val=100, start=0, end=1)
        assert 'TexCountAnimation' in repr(tca)

    def test_renders(self):
        tca = TexCountAnimation(start_val=0, end_val=10, start=0, end=2)
        v = VectorMathAnim('/tmp')
        v.add(tca)
        svg = v.generate_frame_svg(0)
        assert len(svg) > 100

    def test_custom_fmt(self):
        tca = TexCountAnimation(start_val=0, end_val=1, start=0, end=1, fmt='{:.2f}')
        assert tca is not None

    def test_is_dynamic_object(self):
        tca = TexCountAnimation(start_val=0, end_val=5, start=0, end=1)
        assert isinstance(tca, DynamicObject)

    def test_custom_position(self):
        tca = TexCountAnimation(start_val=0, end_val=5, start=0, end=1,
                                x=200, y=300)
        assert tca is not None

    def test_custom_font_size(self):
        tca = TexCountAnimation(start_val=0, end_val=5, start=0, end=1,
                                font_size=72)
        assert tca is not None

    def test_custom_style(self):
        tca = TexCountAnimation(start_val=0, end_val=5, start=0, end=1,
                                fill='#ff0000')
        assert tca is not None


# ── CountAnimation extras ──────────────────────────────────────

class TestCountAnimationExtras:
    def test_count_to(self):
        ca = CountAnimation(start_val=0, end_val=10, start=0, end=1)
        ca.count_to(50, start=1, end=2)
        assert ca._last_val == 50

    def test_count_to_returns_self(self):
        ca = CountAnimation(start_val=0, end_val=10, start=0, end=1)
        result = ca.count_to(20, start=1, end=2)
        assert result is ca

    def test_renders_at_different_times(self):
        ca = CountAnimation(start_val=0, end_val=100, start=0, end=2)
        v = VectorMathAnim('/tmp')
        v.add(ca)
        svg0 = v.generate_frame_svg(0)
        svg2 = v.generate_frame_svg(2)
        # At t=0 should show 0, at t=2 should show 100
        assert '0' in svg0
        assert '100' in svg2


# ── add_label ──────────────────────────────────────────────────

class TestAddLabel:
    def test_returns_vcollection(self):
        c = Circle(r=30, cx=500, cy=500)
        labeled = c.add_label('Test')
        assert len(labeled.objects) == 2  # circle + label

    def test_label_text_appears(self):
        c = Circle(r=30, cx=500, cy=500)
        labeled = c.add_label('Hello')
        v = VectorMathAnim('/tmp')
        v.add(labeled)
        svg = v.generate_frame_svg(0)
        assert 'Hello' in svg

    def test_label_with_direction(self):
        c = Circle(r=30, cx=500, cy=500)
        labeled = c.add_label('Up', direction='up')
        assert len(labeled.objects) == 2

    def test_label_with_follow(self):
        c = Circle(r=30, cx=500, cy=500)
        labeled = c.add_label('Follow', follow=True)
        assert len(labeled.objects) == 2

    def test_label_custom_font_size(self):
        c = Circle(r=30, cx=500, cy=500)
        labeled = c.add_label('Big', font_size=30)
        assert len(labeled.objects) == 2


# ── add_background ─────────────────────────────────────────────

class TestAddBackground:
    def test_returns_rectangle(self):
        c = Circle(r=30, cx=500, cy=500)
        bg = c.add_background()
        assert isinstance(bg, Rectangle)

    def test_custom_color(self):
        c = Circle(r=30, cx=500, cy=500)
        bg = c.add_background(color='#ff0000')
        v = VectorMathAnim('/tmp')
        v.add(bg)
        svg = v.generate_frame_svg(0)
        assert 'rgb(255,0,0)' in svg

    def test_custom_padding(self):
        c = Circle(r=30, cx=500, cy=500)
        bg1 = c.add_background(padding=10)
        bg2 = c.add_background(padding=50)
        assert bg2.get_width(0) > bg1.get_width(0)


# ── match_width / match_height ─────────────────────────────────

class TestMatchDimensions:
    def test_match_width(self):
        s1 = Square(50, x=100, y=100)
        s2 = Square(200, x=400, y=400)
        s1.match_width(s2)
        assert abs(s1.get_width(0) - s2.get_width(0)) < 2

    def test_match_height(self):
        s1 = Square(50, x=100, y=100)
        s2 = Square(200, x=400, y=400)
        s1.match_height(s2)
        assert abs(s1.get_height(0) - s2.get_height(0)) < 2

    def test_match_width_returns_self(self):
        s1 = Square(50)
        s2 = Square(100)
        assert s1.match_width(s2) is s1

    def test_match_height_returns_self(self):
        s1 = Square(50)
        s2 = Square(100)
        assert s1.match_height(s2) is s1


# ── place_between ──────────────────────────────────────────────

class TestPlaceBetween:
    def test_centers_between_objects(self):
        a = Dot(cx=100, cy=500)
        b = Dot(cx=900, cy=500)
        d = Dot(cx=0, cy=0)
        d.place_between(a, b, start=0)
        cx, cy = d.center(0)
        assert abs(cx - 500) < 10
        assert abs(cy - 500) < 10

    def test_custom_fraction(self):
        a = Dot(cx=100, cy=500)
        b = Dot(cx=500, cy=500)
        d = Dot(cx=0, cy=0)
        d.place_between(a, b, fraction=0.25, start=0)
        cx, _ = d.center(0)
        assert abs(cx - 200) < 10  # 25% of the way from a to b

    def test_returns_self(self):
        a = Dot(cx=0, cy=0)
        b = Dot(cx=100, cy=100)
        d = Dot(cx=50, cy=50)
        assert d.place_between(a, b, start=0) is d


# ── animate_to ─────────────────────────────────────────────────

class TestAnimateTo:
    def test_moves_to_target(self):
        c = Circle(r=30, cx=100, cy=100)
        target = Circle(r=30, cx=500, cy=500)
        c.animate_to(target, start=0, end=1)
        cx, cy = c.center(1)
        assert abs(cx - 500) < 10
        assert abs(cy - 500) < 10

    def test_returns_self(self):
        c = Circle(r=30, cx=100, cy=100)
        t = Circle(r=30, cx=500, cy=500)
        assert c.animate_to(t, start=0, end=1) is c


# ── move_towards ───────────────────────────────────────────────

class TestMoveTowards:
    def test_moves_fraction(self):
        a = Dot(cx=100, cy=100)
        b = Dot(cx=500, cy=100)
        a.move_towards(b, fraction=0.5, start=0)
        cx, _ = a.center(0)
        assert abs(cx - 300) < 10

    def test_returns_self(self):
        a = Dot(cx=100, cy=100)
        b = Dot(cx=500, cy=100)
        assert a.move_towards(b, start=0) is a


# ── look_at ────────────────────────────────────────────────────

class TestLookAt:
    def test_returns_self(self):
        c = Circle(r=30, cx=300, cy=300)
        target = Dot(cx=500, cy=500)
        assert c.look_at(target, start=0) is c


# ── snap_to_grid ───────────────────────────────────────────────

class TestSnapToGrid:
    def test_snaps_position(self):
        d = Dot(cx=115, cy=225)
        d.snap_to_grid(start=0, end=1, grid_size=100)
        # After animation completes at t=1, position should be snapped
        cx, cy = d.center(1)
        assert abs(cx - 100) < 5
        assert abs(cy - 200) < 5

    def test_returns_self(self):
        d = Dot(cx=50, cy=50)
        assert d.snap_to_grid(start=0) is d


# ── parallax ───────────────────────────────────────────────────

class TestParallax:
    def test_moves_by_depth_fraction(self):
        c = Circle(r=30, cx=100, cy=100)
        c.parallax(dx=200, dy=0, start=0, end=1, depth_factor=0.5)
        cx, _ = c.center(1)
        assert abs(cx - 200) < 10  # 100 + 200*0.5

    def test_returns_self(self):
        c = Circle(r=30, cx=100, cy=100)
        assert c.parallax(dx=100, dy=0, start=0, end=1) is c


# ── squish ─────────────────────────────────────────────────────

class TestSquish:
    def test_returns_self(self):
        c = Circle(r=30, cx=500, cy=500)
        assert c.squish(start=0, end=1) is c


# ── rotate_in ──────────────────────────────────────────────────

class TestRotateIn:
    def test_returns_self(self):
        c = Circle(r=30, cx=500, cy=500)
        assert c.rotate_in(start=0, end=1) is c

    def test_renders(self):
        c = Circle(r=30, cx=500, cy=500)
        c.rotate_in(start=0, end=1)
        v = VectorMathAnim('/tmp')
        v.add(c)
        svg = v.generate_frame_svg(0.5)
        assert len(svg) > 50


# ── visibility_toggle ─────────────────────────────────────────

class TestVisibilityToggle:
    def test_returns_self(self):
        c = Circle(r=30)
        assert c.visibility_toggle(0, 1, 2) is c

    def test_toggles(self):
        c = Circle(r=30, cx=500, cy=500)
        c.visibility_toggle(0, 1, 2)
        v = VectorMathAnim('/tmp')
        v.add(c)
        # Should be visible at t=0 and hidden at t=0.5
        svg_visible = v.generate_frame_svg(0)
        svg_hidden = v.generate_frame_svg(0.5)
        assert len(svg_visible) >= len(svg_hidden)


# ── dissolve_in / dissolve_out ─────────────────────────────────

class TestDissolveEffects:
    def test_dissolve_in_returns_self(self):
        c = Circle(r=30)
        assert c.dissolve_in(start=0, end=1) is c

    def test_dissolve_out_returns_self(self):
        c = Circle(r=30)
        assert c.dissolve_out(start=0, end=1) is c

    def test_dissolve_in_renders(self):
        c = Circle(r=30, cx=500, cy=500)
        c.dissolve_in(start=0, end=1)
        v = VectorMathAnim('/tmp')
        v.add(c)
        svg = v.generate_frame_svg(0.5)
        assert len(svg) > 50


# ── shimmer ────────────────────────────────────────────────────

class TestShimmer:
    def test_returns_self(self):
        c = Circle(r=30)
        assert c.shimmer(start=0, end=1) is c


# ── breathe ────────────────────────────────────────────────────

class TestBreathe:
    def test_returns_self(self):
        c = Circle(r=30)
        assert c.breathe(start=0, end=2) is c


# ── typewriter effects ─────────────────────────────────────────

class TestTypewriterEffects:
    def test_typewriter_reveal_returns_self(self):
        t = Text(text='Hello', x=400, y=400, font_size=30)
        assert t.typewriter_reveal(start=0, end=1) is t

    def test_typewriter_delete_returns_self(self):
        t = Text(text='Hello', x=400, y=400, font_size=30)
        assert t.typewriter_delete(start=0, end=1) is t


# ── follow_spline ──────────────────────────────────────────────

class TestFollowSpline:
    def test_returns_self(self):
        d = Dot(cx=100, cy=100)
        assert d.follow_spline([(100, 100), (500, 200), (900, 100)], start=0, end=2) is d

    def test_moves_to_end(self):
        d = Dot(cx=100, cy=100)
        d.follow_spline([(100, 100), (500, 500), (900, 100)], start=0, end=1)
        cx, cy = d.center(1)
        assert abs(cx - 900) < 20
        assert abs(cy - 100) < 20


# ── animate_along_object ──────────────────────────────────────

class TestAnimateAlongObject:
    def test_returns_self(self):
        d = Dot(cx=100, cy=100)
        target = Circle(r=100, cx=500, cy=500)
        assert d.animate_along_object(target, start=0, end=1) is d


# ── appear_from ────────────────────────────────────────────────

class TestAppearFrom:
    def test_returns_self(self):
        c = Circle(r=30, cx=500, cy=500)
        src = Dot(cx=100, cy=100)
        assert c.appear_from(src, start=0, end=1) is c

    def test_at_end_reaches_target(self):
        c = Circle(r=30, cx=500, cy=500)
        src = Dot(cx=100, cy=100)
        c.appear_from(src, start=0, end=1)
        cx, cy = c.center(1)
        assert abs(cx - 500) < 10
        assert abs(cy - 500) < 10


# ── animate_style ──────────────────────────────────────────────

class TestAnimateStyle:
    def test_returns_self(self):
        c = Circle(r=30)
        assert c.animate_style(0, 1, fill='#ff0000') is c

    def test_stroke_width_changes(self):
        c = Circle(r=30, cx=500, cy=500, stroke_width=2)
        c.animate_style(0, 1, stroke_width=10)
        v = VectorMathAnim('/tmp')
        v.add(c)
        svg_after = v.generate_frame_svg(1)
        assert '10' in svg_after


# ── set_backstroke ─────────────────────────────────────────────

class TestSetBackstroke:
    def test_returns_self(self):
        c = Circle(r=30)
        assert c.set_backstroke('#ffffff', width=8) is c

    def test_adds_paint_order(self):
        c = Circle(r=30, cx=500, cy=500)
        c.set_backstroke('#000000', width=10)
        v = VectorMathAnim('/tmp')
        v.add(c)
        svg = v.generate_frame_svg(0)
        assert 'paint-order' in svg


# ── bounce_in / bounce_out ─────────────────────────────────────

class TestBounceEffects:
    def test_bounce_in_returns_self(self):
        c = Circle(r=30)
        assert c.bounce_in(start=0, end=1) is c

    def test_bounce_out_returns_self(self):
        c = Circle(r=30)
        assert c.bounce_out(start=0, end=1) is c
