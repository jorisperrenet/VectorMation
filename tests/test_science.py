"""Tests for science/electronics classes from _science.py."""
from vectormation.objects import (
    Resistor, Capacitor, Inductor, Diode, LED,
    Molecule2D, NeuralNetwork, Pendulum, StandingWave,
    Charge, ElectricField, Lens, Ray, VectorMathAnim,
)


class TestResistor:
    def test_creates(self):
        r = Resistor(creation=0)
        assert len(r.objects) > 0

    def test_repr(self):
        r = Resistor(creation=0)
        assert 'Resistor' in repr(r)

    def test_renders(self):
        r = Resistor(creation=0)
        v = VectorMathAnim(save_dir='/tmp/test_sci')
        v.add(r)
        svg = v.generate_frame_svg(time=0)
        assert svg

    def test_custom_position(self):
        r = Resistor(x1=200, y1=200, x2=500, y2=200, creation=0)
        assert len(r.objects) > 0

    def test_no_label(self):
        r = Resistor(label='', creation=0)
        assert len(r.objects) >= 1


class TestCapacitor:
    def test_creates(self):
        c = Capacitor(creation=0)
        assert len(c.objects) > 0

    def test_repr(self):
        c = Capacitor(creation=0)
        assert 'Capacitor' in repr(c)


class TestInductor:
    def test_creates(self):
        i = Inductor(creation=0)
        assert len(i.objects) > 0

    def test_repr(self):
        i = Inductor(creation=0)
        assert 'Inductor' in repr(i)


class TestDiode:
    def test_creates(self):
        d = Diode(creation=0)
        assert len(d.objects) > 0

    def test_repr(self):
        d = Diode(creation=0)
        assert 'Diode' in repr(d)


class TestLED:
    def test_creates(self):
        led = LED(creation=0)
        assert len(led.objects) > 0

    def test_repr(self):
        led = LED(creation=0)
        assert 'LED' in repr(led)


class TestMolecule2D:
    def test_creates(self):
        atoms = [('C', 0, 0), ('O', 1, 0), ('H', -1, 0)]
        bonds = [(0, 1, 2), (0, 2, 1)]
        m = Molecule2D(atoms, bonds, creation=0)
        assert len(m.objects) > 0

    def test_repr(self):
        atoms = [('C', 0, 0), ('H', 1, 0)]
        m = Molecule2D(atoms, creation=0)
        assert '2 atoms' in repr(m)

    def test_no_bonds(self):
        atoms = [('O', 0, 0)]
        m = Molecule2D(atoms, creation=0)
        assert len(m._atom_objects) == 1

    def test_renders(self):
        atoms = [('C', 0, 0), ('O', 1, 0)]
        bonds = [(0, 1, 1)]
        m = Molecule2D(atoms, bonds, creation=0)
        v = VectorMathAnim(save_dir='/tmp/test_sci')
        v.add(m)
        svg = v.generate_frame_svg(time=0)
        assert svg


class TestNeuralNetwork:
    def test_creates(self):
        nn = NeuralNetwork([3, 5, 2], creation=0)
        assert len(nn.objects) > 0

    def test_repr(self):
        nn = NeuralNetwork([2, 3], creation=0)
        r = repr(nn)
        assert 'NeuralNetwork' in r or 'Neural' in r

    def test_renders(self):
        nn = NeuralNetwork([2, 3, 1], creation=0)
        v = VectorMathAnim(save_dir='/tmp/test_sci')
        v.add(nn)
        svg = v.generate_frame_svg(time=0)
        assert svg

    def test_two_layers(self):
        nn = NeuralNetwork([3, 2], creation=0)
        assert len(nn.objects) > 0


class TestPendulum:
    def test_creates(self):
        p = Pendulum(creation=0)
        assert len(p.objects) > 0

    def test_repr(self):
        p = Pendulum(creation=0)
        assert 'Pendulum' in repr(p)

    def test_renders(self):
        p = Pendulum(creation=0)
        v = VectorMathAnim(save_dir='/tmp/test_sci')
        v.add(p)
        svg = v.generate_frame_svg(time=0)
        assert svg


class TestStandingWave:
    def test_creates(self):
        sw = StandingWave(creation=0)
        assert len(sw.objects) > 0

    def test_repr(self):
        sw = StandingWave(creation=0)
        assert 'StandingWave' in repr(sw)


class TestCharge:
    def test_creates_positive(self):
        c = Charge(cx=500, cy=500, sign=1, creation=0)
        assert len(c.objects) > 0

    def test_creates_negative(self):
        c = Charge(cx=500, cy=500, sign=-1, creation=0)
        assert len(c.objects) > 0

    def test_repr(self):
        c = Charge(creation=0)
        assert 'Charge' in repr(c)


class TestElectricField:
    def test_creates(self):
        c1 = Charge(cx=500, cy=400, sign=1, creation=0)
        c2 = Charge(cx=500, cy=600, sign=-1, creation=0)
        ef = ElectricField(c1, c2, creation=0)
        assert len(ef.objects) > 0

    def test_repr(self):
        c = Charge(cx=500, cy=500, sign=1, creation=0)
        ef = ElectricField(c, creation=0)
        assert 'ElectricField' in repr(ef)


class TestLens:
    def test_creates_converging(self):
        lens = Lens(cx=500, cy=500, lens_type='converging', creation=0)
        assert len(lens.objects) > 0

    def test_creates_diverging(self):
        lens = Lens(cx=500, cy=500, lens_type='diverging', creation=0)
        assert len(lens.objects) > 0

    def test_repr(self):
        lens = Lens(creation=0)
        assert 'Lens' in repr(lens)


class TestRay:
    def test_creates(self):
        ray = Ray(x1=100, y1=500, angle=0, length=400, creation=0)
        assert len(ray.objects) > 0

    def test_repr(self):
        ray = Ray(creation=0)
        assert 'Ray' in repr(ray)

    def test_with_lens(self):
        lens = Lens(cx=500, cy=500, creation=0)
        ray = Ray(x1=100, y1=500, angle=0, lenses=[lens], creation=0)
        assert len(ray.objects) > 0
