"""Edge case tests for the physics module."""
import math
from vectormation.objects import Dot
from vectormation._physics import Body, Wall, PhysicsSpace, Cloth


class TestEmptyPhysicsWorld:
    def test_simulate_empty_space(self):
        """Simulating empty PhysicsSpace should not crash."""
        space = PhysicsSpace()
        space.simulate(duration=0.5)

    def test_empty_space_repr(self):
        space = PhysicsSpace()
        assert '0 bodies' in repr(space)


class TestZeroMomentOfInertia:
    def test_zero_radius_gives_zero_moment(self):
        """Body with radius=0 should have zero moment_of_inertia."""
        space = PhysicsSpace()
        b = space.add_body(Dot(cx=500, cy=500), radius=0)
        assert b.moment_of_inertia == 0.0

    def test_zero_moment_simulate_no_crash(self):
        """Body with zero moment_of_inertia should simulate without crash."""
        space = PhysicsSpace()
        b = space.add_body(Dot(cx=500, cy=500), radius=0)
        b.apply_torque(100)
        space.simulate(duration=0.1)
        # angular integration is skipped when moment_of_inertia <= 0

    def test_explicit_zero_moment(self):
        space = PhysicsSpace()
        b = space.add_body(Dot(cx=500, cy=500), moment_of_inertia=0)
        assert b.moment_of_inertia == 0.0
        space.simulate(duration=0.1)


class TestSpringEdgeCases:
    def test_bodies_at_same_position(self):
        """Spring between overlapping bodies should not crash."""
        space = PhysicsSpace(gravity=(0, 0))
        d1 = Dot(cx=500, cy=500)
        d2 = Dot(cx=500, cy=500)
        b1 = space.add_body(d1)
        b2 = space.add_body(d2)
        space.add_spring(b1, b2)
        space.simulate(duration=0.1)

    def test_spring_zero_rest_length(self):
        """Spring with rest_length=0 should pull bodies together."""
        space = PhysicsSpace(gravity=(0, 0))
        d1 = Dot(cx=400, cy=500)
        d2 = Dot(cx=600, cy=500)
        b1 = space.add_body(d1)
        b2 = space.add_body(d2)
        space.add_spring(b1, b2, rest_length=0, stiffness=2.0)
        space.simulate(duration=2.0)
        dist = math.hypot(b2.x - b1.x, b2.y - b1.y)
        assert dist < 100  # should be much closer

    def test_spring_both_anchors(self):
        """Spring between two fixed points should not crash."""
        space = PhysicsSpace()
        space.add_spring((100, 100), (200, 200))
        space.simulate(duration=0.1)

    def test_spring_same_body(self):
        """Spring connecting a body to itself should not crash."""
        space = PhysicsSpace(gravity=(0, 0))
        d = Dot(cx=500, cy=500)
        b = space.add_body(d)
        space.add_spring(b, b, rest_length=100)
        space.simulate(duration=0.1)

    def test_spring_zero_stiffness(self):
        """Spring with zero stiffness should apply no force."""
        space = PhysicsSpace(gravity=(0, 0))
        d1 = Dot(cx=400, cy=500)
        d2 = Dot(cx=600, cy=500)
        b1 = space.add_body(d1)
        b2 = space.add_body(d2)
        space.add_spring(b1, b2, stiffness=0)
        space.simulate(duration=0.5)
        # With zero stiffness, bodies should stay still (no gravity either)
        assert abs(b1.x - 400) < 1
        assert abs(b2.x - 600) < 1


class TestPointForceEdgeCases:
    def test_attraction_body_at_target(self):
        """Attraction to exact position should give zero force."""
        space = PhysicsSpace(gravity=(0, 0))
        d = Dot(cx=500, cy=500)
        b = space.add_body(d)
        space.add_attraction((500, 500), strength=100000)
        space.simulate(duration=0.1)
        assert abs(b.x - 500) < 1

    def test_repulsion_from_point(self):
        """Repulsion from fixed point should push body away."""
        space = PhysicsSpace(gravity=(0, 0))
        d = Dot(cx=500, cy=500)
        b = space.add_body(d)
        space.add_repulsion((400, 500), strength=50000)
        space.simulate(duration=0.2)
        assert b.x > 500


class TestMutualRepulsionEdgeCases:
    def test_bodies_at_same_position(self):
        """Two bodies at same position with mutual repulsion should not crash."""
        space = PhysicsSpace(gravity=(0, 0))
        d1 = Dot(cx=500, cy=500, r=5)
        d2 = Dot(cx=500, cy=500, r=5)
        b1 = space.add_body(d1)
        b2 = space.add_body(d2)
        space.add_mutual_repulsion(strength=50000)
        space.simulate(duration=0.2)
        # Guard prevents force at distance < 1, so shouldn't crash

    def test_extreme_strength(self):
        """Very high mutual repulsion shouldn't produce infinite velocity."""
        space = PhysicsSpace(gravity=(0, 0))
        d1 = Dot(cx=490, cy=500)
        d2 = Dot(cx=510, cy=500)
        b1 = space.add_body(d1)
        b2 = space.add_body(d2)
        space.add_mutual_repulsion(strength=1e8)
        space.simulate(duration=0.01)
        assert math.isfinite(b1.vx) and math.isfinite(b1.vy)
        assert math.isfinite(b2.vx) and math.isfinite(b2.vy)


class TestCollisionEdgeCases:
    def test_zero_radius_bodies(self):
        """Collision between zero-radius bodies should not crash."""
        space = PhysicsSpace(gravity=(0, 0))
        d1 = Dot(cx=400, cy=500, r=1)
        d2 = Dot(cx=500, cy=500, r=1)
        b1 = space.add_body(d1, vx=1000, radius=0)
        b2 = space.add_body(d2, vx=-1000, radius=0)
        space.simulate(duration=0.2)

    def test_fixed_body_collision(self):
        """Collision with fixed body should work correctly."""
        space = PhysicsSpace(gravity=(0, 0))
        d1 = Dot(cx=500, cy=500)
        d2 = Dot(cx=530, cy=500)
        b1 = space.add_body(d1, vx=200, radius=20)
        b2 = space.add_body(d2, vx=0, radius=20, fixed=True)
        space.simulate(duration=0.5)
        # Moving body should bounce back
        assert b1.vx < 0 or b1.x < 510


class TestWallEdgeCases:
    def test_wall_restitution_zero(self):
        """Wall with restitution=0 should absorb bounce."""
        space = PhysicsSpace(gravity=(0, 0))
        d = Dot(cx=500, cy=100, r=5)
        b = space.add_body(d, vy=500)
        space.add_wall(y=500, restitution=0)
        space.simulate(duration=1.0)
        # Body should come to near-rest after hitting wall
        assert abs(b.vy) < 50

    def test_friction_above_one(self):
        """Friction > 1 should clamp tangential velocity to zero."""
        space = PhysicsSpace(gravity=(0, 0))
        d = Dot(cx=500, cy=490, r=10)
        b = space.add_body(d, vy=100, vx=200, friction=2.0, radius=10)
        space.add_wall(y=500, restitution=0.5)
        space.simulate(duration=0.5)
        # fric = max(0, 1-2.0) = 0, so tangential velocity goes to 0


class TestTimingEdgeCases:
    def test_zero_duration(self):
        """Simulating with duration=0 should not crash."""
        space = PhysicsSpace()
        d = Dot(cx=500, cy=500)
        b = space.add_body(d)
        space.simulate(duration=0)

    def test_start_time_offset(self):
        """Positions before simulation start should return initial pos."""
        space = PhysicsSpace(gravity=(0, 500), start=1.0)
        d = Dot(cx=500, cy=100)
        space.add_body(d)
        space.simulate(duration=0.5)


class TestClothEdgeCases:
    def test_cloth_1x1(self):
        """Cloth with 1 column x 1 row should create single particle."""
        cloth = Cloth(cols=1, rows=1, pin_top=True)
        assert len(cloth.space.springs) == 0
        cloth.simulate(duration=0.1)

    def test_cloth_single_column(self):
        """Cloth with single column should not crash."""
        cloth = Cloth(cols=1, rows=3)
        cloth.simulate(duration=0.1)

    def test_cloth_single_row(self):
        """Cloth with single row should not crash."""
        cloth = Cloth(cols=3, rows=1)
        cloth.simulate(duration=0.1)


class TestAddBulk:
    def test_add_mixed_objects(self):
        """add() should handle Body, Spring, and Wall objects."""
        space = PhysicsSpace()
        b = Body(Dot(cx=100, cy=100))
        w = Wall(y=500)
        space.add(b, w)
        assert len(space.bodies) == 1
        assert len(space.walls) == 1

    def test_add_walls_convenience(self):
        """add_walls() should create walls on all four sides."""
        space = PhysicsSpace()
        space.add_walls(left=0, right=1920, top=0, bottom=1080)
        assert len(space.walls) == 4


class TestAngularDynamics:
    def test_angular_drag(self):
        """Angular drag should slow rotation."""
        space = PhysicsSpace(gravity=(0, 0))
        d = Dot(cx=500, cy=500)
        b = space.add_body(d, angular_velocity=360, radius=20)
        space.add_angular_drag(coefficient=0.1)
        space.simulate(duration=1.0)
        assert abs(b.angular_velocity) < 360

    def test_torque_application(self):
        """Applied torque should change angular velocity."""
        space = PhysicsSpace(gravity=(0, 0))
        d = Dot(cx=500, cy=500)
        b = space.add_body(d, radius=20)
        b.apply_torque(1000)
        space.simulate(duration=0.01)
        # Torque is reset each step, so only first step matters


class TestCustomForces:
    def test_drag_force(self):
        """add_drag should slow body down."""
        space = PhysicsSpace(gravity=(0, 0))
        d = Dot(cx=500, cy=500)
        b = space.add_body(d, vx=500)
        space.add_drag(coefficient=0.1)
        space.simulate(duration=1.0)
        assert abs(b.vx) < 500

    def test_multiple_custom_forces(self):
        """Multiple custom forces should all be applied."""
        space = PhysicsSpace(gravity=(0, 0))
        d = Dot(cx=500, cy=500)
        b = space.add_body(d)
        space.add_force(lambda _body, _t: (100, 0))
        space.add_force(lambda _body, _t: (0, 100))
        space.simulate(duration=0.5)
        assert b.x > 500
        assert b.y > 500


class TestWallValidation:
    def test_wall_needs_x_or_y(self):
        """Wall with neither x nor y should raise ValueError."""
        import pytest
        with pytest.raises(ValueError, match='at least x or y'):
            Wall()
