"""Tests for UI component classes from _ui.py."""
from vectormation.objects import (
    Title, Variable, Underline, Code, Label, LabeledLine, LabeledArrow,
    Callout, DimensionLine, Tooltip, TextBox, Bracket, IconGrid,
    SpeechBubble, Badge, Divider, Text, Circle, VectorMathAnim,
)


class TestTitle:
    def test_creates(self):
        t = Title('Hello', creation=0)
        assert len(t.objects) == 2

    def test_repr(self):
        t = Title('Hello', creation=0)
        assert 'Title' in repr(t)

    def test_renders(self):
        t = Title('Hello', creation=0)
        v = VectorMathAnim(save_dir='/tmp/test_ui')
        v.add(t)
        svg = v.generate_frame_svg(time=0)
        assert 'Hello' in svg


class TestVariable:
    def test_creates(self):
        var = Variable(label='x', value=3.14, creation=0)
        assert len(var.objects) == 2

    def test_repr(self):
        var = Variable(label='x', value=0, creation=0)
        assert 'Variable' in repr(var)

    def test_set_value(self):
        var = Variable(label='x', value=0, creation=0)
        result = var.set_value(5.0, start=1)
        assert result is var

    def test_animate_value(self):
        var = Variable(label='x', value=0, creation=0)
        result = var.animate_value(10, start=0, end=1)
        assert result is var

    def test_tracker(self):
        var = Variable(label='x', value=0, creation=0)
        assert var.tracker is not None


class TestUnderline:
    def test_creates(self):
        txt = Text('Hello', creation=0)
        ul = Underline(txt, creation=0)
        assert len(ul.objects) == 1

    def test_repr(self):
        txt = Text('Hello', creation=0)
        ul = Underline(txt, creation=0)
        assert 'Underline' in repr(ul)

    def test_no_follow(self):
        txt = Text('Hello', creation=0)
        ul = Underline(txt, follow=False, creation=0)
        assert len(ul.objects) == 1


class TestCode:
    def test_creates(self):
        c = Code('x = 1\ny = 2', creation=0)
        assert len(c.objects) > 0

    def test_repr(self):
        c = Code('x = 1\ny = 2', creation=0)
        assert '2 lines' in repr(c)

    def test_highlight_lines(self):
        c = Code('a = 1\nb = 2\nc = 3', creation=0)
        hl = c.highlight_lines([1, 2], start=0, end=1)
        assert len(hl.objects) == 2

    def test_highlight_single_line(self):
        c = Code('a = 1\nb = 2', creation=0)
        hl = c.highlight_lines(1, start=0, end=1)
        assert len(hl.objects) == 1

    def test_highlight_out_of_range(self):
        c = Code('a = 1', creation=0)
        hl = c.highlight_lines([99], start=0, end=1)
        assert len(hl.objects) == 0

    def test_reveal_lines(self):
        c = Code('a = 1\nb = 2', creation=0)
        result = c.reveal_lines(start=0, end=1)
        assert result is c

    def test_javascript_language(self):
        c = Code('const x = 1;', language='javascript', creation=0)
        assert 'javascript' in repr(c)

    def test_renders(self):
        c = Code('x = 1', creation=0)
        v = VectorMathAnim(save_dir='/tmp/test_ui')
        v.add(c)
        svg = v.generate_frame_svg(time=0)
        assert svg


class TestLabel:
    def test_creates(self):
        lbl = Label('Test', creation=0)
        assert len(lbl.objects) == 2

    def test_repr(self):
        lbl = Label('Test', creation=0)
        assert 'Label' in repr(lbl)


class TestLabeledLine:
    def test_creates(self):
        ll = LabeledLine(x1=100, y1=100, x2=300, y2=100, label='AB', creation=0)
        assert len(ll.objects) >= 2

    def test_repr(self):
        ll = LabeledLine(label='AB', creation=0)
        assert 'LabeledLine' in repr(ll)


class TestLabeledArrow:
    def test_creates(self):
        la = LabeledArrow(x1=100, y1=100, x2=300, y2=100, label='AB', creation=0)
        assert len(la.objects) >= 2

    def test_repr(self):
        la = LabeledArrow(label='AB', creation=0)
        assert 'LabeledArrow' in repr(la)

    def test_has_arrow_attr(self):
        la = LabeledArrow(label='AB', creation=0)
        assert la.arrow is not None


class TestCallout:
    def test_creates_up(self):
        target = Circle(r=30, cx=500, cy=500, creation=0)
        co = Callout('Note', target, direction='up', creation=0)
        assert len(co.objects) == 3

    def test_creates_down(self):
        co = Callout('Note', (500, 500), direction='down', creation=0)
        assert len(co.objects) == 3

    def test_creates_left(self):
        co = Callout('Note', (500, 500), direction='left', creation=0)
        assert len(co.objects) == 3

    def test_repr(self):
        co = Callout('Note', (500, 500), creation=0)
        assert 'Callout' in repr(co)


class TestDimensionLine:
    def test_creates(self):
        dl = DimensionLine((100, 100), (400, 100), creation=0)
        assert len(dl.objects) >= 5

    def test_auto_label(self):
        dl = DimensionLine((100, 100), (400, 100), creation=0)
        assert 'DimensionLine' in repr(dl)

    def test_custom_label(self):
        dl = DimensionLine((100, 100), (400, 100), label='3m', creation=0)
        assert len(dl.objects) >= 5


class TestTooltip:
    def test_creates(self):
        target = Circle(r=30, cx=500, cy=500, creation=0)
        tt = Tooltip('Tip!', target, start=0, duration=1, creation=0)
        assert len(tt.objects) == 2

    def test_from_tuple(self):
        tt = Tooltip('Tip!', (500, 500), start=0, creation=0)
        assert len(tt.objects) == 2

    def test_repr(self):
        tt = Tooltip('Tip!', (500, 500), creation=0)
        assert 'Tooltip' in repr(tt)


class TestTextBox:
    def test_creates(self):
        tb = TextBox('Hello', creation=0)
        assert len(tb.objects) == 2

    def test_repr(self):
        tb = TextBox('Hello', creation=0)
        assert 'TextBox' in repr(tb)

    def test_custom_size(self):
        tb = TextBox('Hello', width=200, height=50, creation=0)
        assert tb.box is not None
        assert tb.label is not None


class TestBracket:
    def test_creates_down(self):
        b = Bracket(direction='down', creation=0)
        assert len(b.objects) >= 1

    def test_creates_up(self):
        b = Bracket(direction='up', creation=0)
        assert len(b.objects) >= 1

    def test_creates_right(self):
        b = Bracket(direction='right', creation=0)
        assert len(b.objects) >= 1

    def test_creates_left(self):
        b = Bracket(direction='left', creation=0)
        assert len(b.objects) >= 1

    def test_with_label(self):
        b = Bracket(text='label', creation=0)
        assert len(b.objects) == 2

    def test_repr(self):
        b = Bracket(creation=0)
        assert 'Bracket' in repr(b)


class TestIconGrid:
    def test_creates(self):
        ig = IconGrid([(5, '#FF0000'), (3, '#00FF00')], creation=0)
        assert len(ig.objects) == 8

    def test_square_shape(self):
        ig = IconGrid([(2, '#FF0000')], shape='square', creation=0)
        assert len(ig.objects) == 2

    def test_repr(self):
        ig = IconGrid([(3, '#FF0000')], creation=0)
        assert 'IconGrid' in repr(ig)


class TestSpeechBubble:
    def test_creates_down(self):
        sb = SpeechBubble('Hi!', tail_direction='down', creation=0)
        assert len(sb.objects) == 3

    def test_creates_up(self):
        sb = SpeechBubble('Hi!', tail_direction='up', creation=0)
        assert len(sb.objects) == 3

    def test_creates_left(self):
        sb = SpeechBubble('Hi!', tail_direction='left', creation=0)
        assert len(sb.objects) == 3

    def test_creates_right(self):
        sb = SpeechBubble('Hi!', tail_direction='right', creation=0)
        assert len(sb.objects) == 3

    def test_repr(self):
        sb = SpeechBubble('Hi!', creation=0)
        assert 'SpeechBubble' in repr(sb)

    def test_has_box_and_label(self):
        sb = SpeechBubble('Hi!', creation=0)
        assert sb.box is not None
        assert sb.label is not None


class TestBadge:
    def test_creates(self):
        b = Badge('v1.0', creation=0)
        assert len(b.objects) == 2

    def test_repr(self):
        b = Badge('v1.0', creation=0)
        assert 'Badge' in repr(b)

    def test_has_box_and_label(self):
        b = Badge('v1.0', creation=0)
        assert b.box is not None
        assert b.label is not None


class TestDivider:
    def test_creates_horizontal(self):
        d = Divider(direction='horizontal', creation=0)
        assert len(d.objects) >= 1

    def test_creates_vertical(self):
        d = Divider(direction='vertical', creation=0)
        assert len(d.objects) >= 1

    def test_with_label(self):
        d = Divider(label='Section', creation=0)
        assert len(d.objects) >= 2

    def test_repr(self):
        d = Divider(creation=0)
        assert 'Divider' in repr(d)
