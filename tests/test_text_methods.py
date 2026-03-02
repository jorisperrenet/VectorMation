"""Tests for Text advanced methods: reveal_by_word, highlight, split, wrap, etc."""
from vectormation.objects import Text


class TestSetText:
    def test_changes_text(self):
        t = Text(text='Hello', x=100, y=100)
        t.set_text(start=0, end=1, new_text='World')
        svg = t.to_svg(1.5)
        assert 'World' in svg


class TestSplitChars:
    def test_basic(self):
        t = Text(text='ABC', x=100, y=100)
        result = t.split_chars()
        assert len(result) == 3

    def test_single_char(self):
        t = Text(text='X', x=100, y=100)
        result = t.split_chars()
        assert len(result) == 1


class TestSplitLines:
    def test_multiline(self):
        t = Text(text='Line1\nLine2\nLine3', x=100, y=100)
        result = t.split_lines()
        assert len(result) == 3

    def test_single_line(self):
        t = Text(text='Hello', x=100, y=100)
        result = t.split_lines()
        assert len(result) == 1


class TestToUpperToLower:
    def test_to_upper(self):
        t = Text(text='hello', x=100, y=100)
        t.to_upper()
        svg = t.to_svg(0)
        assert 'HELLO' in svg

    def test_to_lower(self):
        t = Text(text='HELLO', x=100, y=100)
        t.to_lower()
        svg = t.to_svg(0)
        assert 'hello' in svg


class TestTruncate:
    def test_basic(self):
        t = Text(text='Hello World', x=100, y=100)
        t.truncate(8)
        svg = t.to_svg(0)
        assert 'Hello...' in svg

    def test_no_truncation_needed(self):
        t = Text(text='Hi', x=100, y=100)
        t.truncate(10)
        svg = t.to_svg(0)
        assert 'Hi' in svg

    def test_custom_ellipsis(self):
        t = Text(text='Hello World', x=100, y=100)
        t.truncate(7, ellipsis='..')
        svg = t.to_svg(0)
        assert 'Hello..' in svg
