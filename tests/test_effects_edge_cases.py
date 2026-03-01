"""Edge case tests for animation effects in _base_effects.py."""
from vectormation._shapes import Circle, Rectangle, Dot


# ── wobble ────────────────────────────────────────────────────────────────

class TestWobbleEffect:
    def test_basic(self):
        c = Circle(r=50, cx=500, cy=500)
        c.wobble(start=0, end=1, amplitude=5, frequency=3)
        svg = c.to_svg(0.5)
        assert svg is not None

    def test_zero_duration(self):
        c = Circle(r=50, cx=500, cy=500)
        c.wobble(start=1, end=1)
        svg = c.to_svg(1)
        assert svg is not None

    def test_zero_amplitude(self):
        c = Circle(r=50, cx=500, cy=500)
        c.wobble(start=0, end=1, amplitude=0)
        svg = c.to_svg(0.5)
        assert svg is not None


# ── focus_zoom ────────────────────────────────────────────────────────────

class TestFocusZoom:
    def test_basic(self):
        c = Circle(r=50, cx=500, cy=500)
        c.focus_zoom(start=0, end=1, zoom_factor=1.3)
        svg = c.to_svg(0.5)
        assert svg is not None

    def test_zoom_factor_one(self):
        """Zoom factor 1 = no zoom."""
        c = Circle(r=50, cx=500, cy=500)
        c.focus_zoom(start=0, end=1, zoom_factor=1)
        svg = c.to_svg(0.5)
        assert svg is not None


# ── look_at ───────────────────────────────────────────────────────────────

class TestLookAt:
    def test_look_at_point(self):
        c = Circle(r=50, cx=500, cy=500)
        c.look_at((800, 500), start=0)
        svg = c.to_svg(0.5)
        assert svg is not None

    def test_look_at_object(self):
        c = Circle(r=50, cx=500, cy=500)
        target = Dot(cx=800, cy=800)
        c.look_at(target, start=0)
        svg = c.to_svg(0.5)
        assert svg is not None

    def test_look_at_with_end(self):
        c = Circle(r=50, cx=500, cy=500)
        c.look_at((800, 200), start=0, end=1)
        svg = c.to_svg(0.5)
        assert svg is not None


# ── animate_to ────────────────────────────────────────────────────────────

class TestAnimateTo:
    def test_basic(self):
        c = Circle(r=50, cx=500, cy=500)
        target = Circle(r=100, cx=800, cy=800)
        c.animate_to(target, start=0, end=1)
        svg = c.to_svg(0.5)
        assert svg is not None

    def test_same_object(self):
        c = Circle(r=50, cx=500, cy=500)
        c.animate_to(c, start=0, end=1)
        svg = c.to_svg(0.5)
        assert svg is not None


# ── set_lifetime ──────────────────────────────────────────────────────────

class TestSetLifetime:
    def test_basic(self):
        c = Circle(r=50, cx=500, cy=500)
        c.set_lifetime(1, 3)
        # Before start: hidden
        assert not c.show.at_time(0.5)
        # During: visible
        assert c.show.at_time(2)
        # After end: hidden
        assert not c.show.at_time(4)

    def test_returns_self(self):
        c = Circle(r=50, cx=500, cy=500)
        result = c.set_lifetime(0, 1)
        assert result is c


# ── move_towards ──────────────────────────────────────────────────────────

class TestMoveTowards:
    def test_halfway(self):
        c = Circle(r=50, cx=0, cy=0)
        target = Dot(cx=200, cy=200)
        c.move_towards(target, fraction=0.5, start=0)

    def test_point_target(self):
        c = Circle(r=50, cx=0, cy=0)
        c.move_towards((200, 200), fraction=0.5, start=0)

    def test_zero_fraction(self):
        c = Circle(r=50, cx=100, cy=100)
        c.move_towards((500, 500), fraction=0, start=0)


# ── place_between ─────────────────────────────────────────────────────────

class TestPlaceBetween:
    def test_between_points(self):
        c = Circle(r=50, cx=500, cy=500)
        c.place_between((100, 100), (300, 300), fraction=0.5, start=0)

    def test_between_objects(self):
        c = Circle(r=50, cx=500, cy=500)
        a = Dot(cx=100, cy=100)
        b = Dot(cx=300, cy=300)
        c.place_between(a, b, fraction=0.5, start=0)

    def test_fraction_zero(self):
        c = Circle(r=50, cx=500, cy=500)
        c.place_between((100, 100), (300, 300), fraction=0, start=0)

    def test_fraction_one(self):
        c = Circle(r=50, cx=500, cy=500)
        c.place_between((100, 100), (300, 300), fraction=1, start=0)


# ── homotopy ──────────────────────────────────────────────────────────────

class TestHomotopy:
    def test_identity(self):
        r = Rectangle(100, 50, x=500, y=500)
        r.homotopy(lambda x, y, t: (x, y), start=0, end=1)
        svg = r.to_svg(0.5)
        assert svg is not None

    def test_zero_duration(self):
        r = Rectangle(100, 50, x=500, y=500)
        r.homotopy(lambda x, y, t: (x + 10, y + 10), start=1, end=1)
        svg = r.to_svg(1)
        assert svg is not None

    def test_translation(self):
        r = Rectangle(100, 50, x=500, y=500)
        r.homotopy(lambda x, y, t: (x + 100 * t, y), start=0, end=1)
        svg = r.to_svg(0.5)
        assert svg is not None


# ── apply_wave ────────────────────────────────────────────────────────────

class TestApplyWave:
    def test_basic(self):
        r = Rectangle(200, 50, x=500, y=500)
        r.apply_wave(start=0, end=1, amplitude=30)
        svg = r.to_svg(0.5)
        assert svg is not None

    def test_x_direction(self):
        r = Rectangle(200, 50, x=500, y=500)
        r.apply_wave(start=0, end=1, amplitude=20, direction='x')
        svg = r.to_svg(0.5)
        assert svg is not None

    def test_zero_amplitude(self):
        r = Rectangle(200, 50, x=500, y=500)
        r.apply_wave(start=0, end=1, amplitude=0)
        svg = r.to_svg(0.5)
        assert svg is not None


# ── scale_in_place ────────────────────────────────────────────────────────

class TestScaleInPlace:
    def test_basic(self):
        c = Circle(r=50, cx=500, cy=500)
        c.scale_in_place(2, start=0, end=1)
        svg = c.to_svg(0.5)
        assert svg is not None

    def test_scale_down(self):
        c = Circle(r=50, cx=500, cy=500)
        c.scale_in_place(0.5, start=0, end=1)
        svg = c.to_svg(0.5)
        assert svg is not None

    def test_scale_one(self):
        c = Circle(r=50, cx=500, cy=500)
        c.scale_in_place(1, start=0, end=1)
        svg = c.to_svg(0.5)
        assert svg is not None


# ── passing_flash ─────────────────────────────────────────────────────────

class TestPassingFlash:
    def test_basic(self):
        c = Circle(r=100, cx=500, cy=500)
        c.passing_flash(start=0, end=1)
        svg = c.to_svg(0.5)
        assert svg is not None

    def test_with_color(self):
        c = Circle(r=100, cx=500, cy=500)
        c.passing_flash(start=0, end=1, color='#FF0000')
        svg = c.to_svg(0.5)
        assert svg is not None

    def test_narrow_width(self):
        c = Circle(r=100, cx=500, cy=500)
        c.passing_flash(start=0, end=1, width=0.05)
        svg = c.to_svg(0.5)
        assert svg is not None


# ── get_style ─────────────────────────────────────────────────────────────

class TestGetStyle:
    def test_returns_dict(self):
        c = Circle(r=50, cx=500, cy=500, fill='#FF0000')
        s = c.get_style(0)
        assert isinstance(s, dict)
        assert 'fill' in s

    def test_at_different_times(self):
        c = Circle(r=50, cx=500, cy=500)
        c.set_color(start=0, end=1, fill='#FF0000')
        s0 = c.get_style(0)
        s1 = c.get_style(1)
        assert isinstance(s0, dict)
        assert isinstance(s1, dict)


# ── chaining effects ─────────────────────────────────────────────────────

class TestEffectChaining:
    def test_multiple_effects(self):
        c = Circle(r=50, cx=500, cy=500)
        c.wobble(start=0, end=1)
        c.focus_zoom(start=1, end=2)
        c.scale_in_place(1.5, start=2, end=3)
        svg = c.to_svg(0.5)
        assert svg is not None

    def test_overlapping_effects(self):
        c = Circle(r=50, cx=500, cy=500)
        c.wobble(start=0, end=2)
        c.focus_zoom(start=1, end=3)
        svg = c.to_svg(1.5)
        assert svg is not None
