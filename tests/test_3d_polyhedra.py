"""Tests for 3D polyhedra factory functions and 3D primitives."""
import math
from vectormation.objects import (
    ThreeDAxes, Surface, Sphere3D, Cube, Cylinder3D, Cone3D, Torus3D, Prism3D,
    Tetrahedron, Octahedron, Icosahedron, Dodecahedron,
    Line3D, Dot3D, Arrow3D, ParametricCurve3D, Text3D,
    VectorMathAnim,
)


# ── Polyhedra ─────────────────────────────────────────────────────────

class TestTetrahedron:
    def test_returns_list_of_surfaces(self):
        faces = Tetrahedron()
        assert isinstance(faces, list)
        assert len(faces) == 4

    def test_all_faces_are_surfaces(self):
        for f in Tetrahedron():
            assert isinstance(f, Surface)

    def test_custom_position(self):
        faces = Tetrahedron(cx=1, cy=2, cz=3)
        assert len(faces) == 4

    def test_custom_size(self):
        faces = Tetrahedron(size=2.0)
        assert len(faces) == 4

    def test_custom_color(self):
        faces = Tetrahedron(fill_color='#ff0000')
        assert len(faces) == 4

    def test_renders_in_axes(self):
        ax = ThreeDAxes()
        for f in Tetrahedron():
            ax.add_surface(f)
        v = VectorMathAnim('/tmp')
        v.add(ax)
        svg = v.generate_frame_svg(0)
        assert len(svg) > 200


class TestOctahedron:
    def test_returns_8_faces(self):
        faces = Octahedron()
        assert len(faces) == 8

    def test_all_surfaces(self):
        for f in Octahedron():
            assert isinstance(f, Surface)

    def test_custom_position(self):
        faces = Octahedron(cx=1, cy=2, cz=3)
        assert len(faces) == 8

    def test_custom_size(self):
        faces = Octahedron(size=0.5)
        assert len(faces) == 8

    def test_renders_in_axes(self):
        ax = ThreeDAxes()
        for f in Octahedron():
            ax.add_surface(f)
        v = VectorMathAnim('/tmp')
        v.add(ax)
        svg = v.generate_frame_svg(0)
        assert len(svg) > 200


class TestIcosahedron:
    def test_returns_20_faces(self):
        faces = Icosahedron()
        assert len(faces) == 20

    def test_all_surfaces(self):
        for f in Icosahedron():
            assert isinstance(f, Surface)

    def test_custom_position(self):
        faces = Icosahedron(cx=0.5, cy=0.5, cz=0.5)
        assert len(faces) == 20

    def test_custom_size(self):
        faces = Icosahedron(size=1.5)
        assert len(faces) == 20

    def test_custom_style(self):
        faces = Icosahedron(fill_color='#00ff00', stroke_color='#000',
                            stroke_width=2, fill_opacity=0.5)
        assert len(faces) == 20

    def test_renders_in_axes(self):
        ax = ThreeDAxes()
        for f in Icosahedron():
            ax.add_surface(f)
        v = VectorMathAnim('/tmp')
        v.add(ax)
        svg = v.generate_frame_svg(0)
        assert len(svg) > 200


class TestDodecahedron:
    def test_returns_12_faces(self):
        faces = Dodecahedron()
        assert len(faces) == 12

    def test_all_surfaces(self):
        for f in Dodecahedron():
            assert isinstance(f, Surface)

    def test_custom_position(self):
        faces = Dodecahedron(cx=-1, cy=-1, cz=-1)
        assert len(faces) == 12

    def test_custom_size(self):
        faces = Dodecahedron(size=3.0)
        assert len(faces) == 12

    def test_custom_creation_time(self):
        faces = Dodecahedron(creation=5)
        assert len(faces) == 12

    def test_renders_in_axes(self):
        ax = ThreeDAxes()
        for f in Dodecahedron():
            ax.add_surface(f)
        v = VectorMathAnim('/tmp')
        v.add(ax)
        svg = v.generate_frame_svg(0)
        assert len(svg) > 200


# ── 3D Primitives ────────────────────────────────────────────────────

class TestLine3D:
    def test_creation(self):
        l = Line3D((0, 0, 0), (1, 1, 1))
        assert l is not None

    def test_renders_in_axes(self):
        ax = ThreeDAxes()
        l = Line3D((0, 0, 0), (1, 1, 1))
        ax.add_3d(l)
        v = VectorMathAnim('/tmp')
        v.add(ax)
        svg = v.generate_frame_svg(0)
        assert len(svg) > 100

    def test_custom_style(self):
        l = Line3D((0, 0, 0), (2, 2, 2), stroke='#ff0000', stroke_width=3)
        assert l is not None


class TestDot3D:
    def test_creation(self):
        d = Dot3D((1, 2, 3))
        assert d is not None

    def test_renders(self):
        ax = ThreeDAxes()
        d = Dot3D((0, 0, 0))
        ax.add_3d(d)
        v = VectorMathAnim('/tmp')
        v.add(ax)
        svg = v.generate_frame_svg(0)
        assert '<circle' in svg or '<ellipse' in svg

    def test_custom_style(self):
        d = Dot3D((0, 0, 0), fill='#ff0000', radius=10)
        assert d is not None


class TestArrow3D:
    def test_creation(self):
        a = Arrow3D((0, 0, 0), (1, 1, 1))
        assert a is not None

    def test_renders(self):
        ax = ThreeDAxes()
        a = Arrow3D((0, 0, 0), (1, 0, 0))
        ax.add_3d(a)
        v = VectorMathAnim('/tmp')
        v.add(ax)
        svg = v.generate_frame_svg(0)
        assert len(svg) > 100

    def test_custom_style(self):
        a = Arrow3D((0, 0, 0), (1, 1, 1), stroke='#00ff00')
        assert a is not None


class TestParametricCurve3D:
    def test_creation(self):
        c = ParametricCurve3D(
            lambda t: (math.cos(t), math.sin(t), t / (2 * math.pi)),
            t_range=(0, 2 * math.pi),
        )
        assert c is not None

    def test_renders(self):
        ax = ThreeDAxes()
        c = ParametricCurve3D(
            lambda t: (math.cos(t), math.sin(t), 0),
            t_range=(0, 2 * math.pi),
        )
        ax.add_3d(c)
        v = VectorMathAnim('/tmp')
        v.add(ax)
        svg = v.generate_frame_svg(0)
        assert len(svg) > 100

    def test_custom_resolution(self):
        c = ParametricCurve3D(
            lambda t: (t, t * t, 0),
            t_range=(0, 1),
            num_points=50,
        )
        assert c is not None


class TestText3D:
    def test_creation(self):
        t = Text3D('Hello', (0, 0, 0))
        assert t is not None

    def test_renders(self):
        ax = ThreeDAxes()
        t = Text3D('Test', (1, 0, 0))
        ax.add_3d(t)
        v = VectorMathAnim('/tmp')
        v.add(ax)
        svg = v.generate_frame_svg(0)
        assert 'Test' in svg


# ── 3D Shape Factories ──────────────────────────────────────────────

class TestSphere3DExtended:
    def test_creates_surface(self):
        s = Sphere3D()
        assert isinstance(s, Surface)

    def test_custom_radius(self):
        s = Sphere3D(radius=2.0)
        assert s is not None

    def test_custom_position(self):
        s = Sphere3D(center=(1, 2, 3))
        assert s is not None

    def test_renders(self):
        ax = ThreeDAxes()
        ax.add_surface(Sphere3D())
        v = VectorMathAnim('/tmp')
        v.add(ax)
        svg = v.generate_frame_svg(0)
        assert len(svg) > 200


class TestCubeExtended:
    def test_creates_surfaces(self):
        faces = Cube()
        assert isinstance(faces, list)
        assert len(faces) == 6

    def test_custom_size(self):
        faces = Cube(side_length=2.0)
        assert len(faces) == 6

    def test_renders(self):
        ax = ThreeDAxes()
        for f in Cube():
            ax.add_surface(f)
        v = VectorMathAnim('/tmp')
        v.add(ax)
        svg = v.generate_frame_svg(0)
        assert len(svg) > 200


class TestCylinder3DExtended:
    def test_creates_surface(self):
        c = Cylinder3D()
        assert isinstance(c, Surface)

    def test_custom_params(self):
        c = Cylinder3D(radius=0.5, height=3.0)
        assert c is not None

    def test_renders(self):
        ax = ThreeDAxes()
        ax.add_surface(Cylinder3D())
        v = VectorMathAnim('/tmp')
        v.add(ax)
        svg = v.generate_frame_svg(0)
        assert len(svg) > 100


class TestCone3DExtended:
    def test_creates_surface(self):
        c = Cone3D()
        assert isinstance(c, Surface)

    def test_custom_params(self):
        c = Cone3D(radius=0.5, height=2.0)
        assert c is not None

    def test_renders(self):
        ax = ThreeDAxes()
        ax.add_surface(Cone3D())
        v = VectorMathAnim('/tmp')
        v.add(ax)
        svg = v.generate_frame_svg(0)
        assert len(svg) > 100


class TestTorus3DExtended:
    def test_creates_surface(self):
        t = Torus3D()
        assert isinstance(t, Surface)

    def test_custom_radii(self):
        t = Torus3D(major_radius=2.0, minor_radius=0.3)
        assert t is not None

    def test_renders(self):
        ax = ThreeDAxes()
        ax.add_surface(Torus3D())
        v = VectorMathAnim('/tmp')
        v.add(ax)
        svg = v.generate_frame_svg(0)
        assert len(svg) > 100


class TestPrism3DExtended:
    def test_creates_surfaces(self):
        faces = Prism3D()
        assert isinstance(faces, list)
        assert len(faces) > 0

    def test_custom_params(self):
        faces = Prism3D(n_sides=6, radius=1.0, height=2.0)
        assert len(faces) > 0

    def test_renders(self):
        ax = ThreeDAxes()
        for f in Prism3D():
            ax.add_surface(f)
        v = VectorMathAnim('/tmp')
        v.add(ax)
        svg = v.generate_frame_svg(0)
        assert len(svg) > 100
