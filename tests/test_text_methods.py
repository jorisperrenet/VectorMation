"""Tests for Text advanced methods: reveal_by_word, highlight, split, wrap, etc."""
import pytest
from vectormation.objects import Text, VCollection


class TestRevealByWord:
    def test_returns_self(self):
        t = Text(text='Hello World', x=100, y=100)
        result = t.reveal_by_word(start=0, end=1)
        assert result is t

    def test_multi_word(self):
        t = Text(text='one two three', x=100, y=100)
        t.reveal_by_word(start=0, end=2)
        svg = t.to_svg(0.5)
        assert svg is not None


class TestHighlight:
    def test_returns_vcollection_or_self(self):
        t = Text(text='Hello', x=100, y=100)
        result = t.highlight(start=0, end=1)
        # highlight returns a VCollection (containing the rect + text)
        assert result is not None

    def test_custom_color(self):
        t = Text(text='Hello', x=100, y=100)
        result = t.highlight(color='#FF0000')
        assert result is not None


class TestHighlightSubstring:
    def test_basic(self):
        t = Text(text='Hello World', x=100, y=100)
        result = t.highlight_substring('World')
        assert result is not None

    def test_no_match(self):
        t = Text(text='Hello World', x=100, y=100)
        result = t.highlight_substring('xyz')
        assert result is not None  # Should not crash


class TestSetText:
    def test_changes_text(self):
        t = Text(text='Hello', x=100, y=100)
        t.set_text(start=0, end=1, new_text='World')
        svg = t.to_svg(1.5)
        assert 'World' in svg

    def test_returns_self(self):
        t = Text(text='Hello', x=100, y=100)
        result = t.set_text(start=0, end=1, new_text='World')
        assert result is t


class TestSplitChars:
    def test_basic(self):
        t = Text(text='ABC', x=100, y=100)
        result = t.split_chars()
        assert isinstance(result, VCollection)
        assert len(result) == 3

    def test_single_char(self):
        t = Text(text='X', x=100, y=100)
        result = t.split_chars()
        assert isinstance(result, VCollection)
        assert len(result) == 1


class TestSplitLines:
    def test_multiline(self):
        t = Text(text='Line1\nLine2\nLine3', x=100, y=100)
        result = t.split_lines()
        assert isinstance(result, VCollection)
        assert len(result) == 3

    def test_single_line(self):
        t = Text(text='Hello', x=100, y=100)
        result = t.split_lines()
        assert isinstance(result, VCollection)
        assert len(result) == 1


class TestFitToBox:
    def test_basic(self):
        t = Text(text='Hello World', x=100, y=100, font_size=48)
        result = t.fit_to_box(max_width=200)
        assert result is t

    def test_with_max_height(self):
        t = Text(text='Hello', x=100, y=100, font_size=48)
        result = t.fit_to_box(max_width=200, max_height=50)
        assert result is t


class TestToUpperToLower:
    def test_to_upper(self):
        t = Text(text='hello', x=100, y=100)
        result = t.to_upper()
        assert result is t
        svg = t.to_svg(0)
        assert 'HELLO' in svg

    def test_to_lower(self):
        t = Text(text='HELLO', x=100, y=100)
        result = t.to_lower()
        assert result is t
        svg = t.to_svg(0)
        assert 'hello' in svg


class TestTruncate:
    def test_basic(self):
        t = Text(text='Hello World', x=100, y=100)
        result = t.truncate(8)
        assert result is t
        svg = t.to_svg(0)
        assert 'Hello...' in svg

    def test_no_truncation_needed(self):
        t = Text(text='Hi', x=100, y=100)
        result = t.truncate(10)
        assert result is t
        svg = t.to_svg(0)
        assert 'Hi' in svg

    def test_custom_ellipsis(self):
        t = Text(text='Hello World', x=100, y=100)
        t.truncate(7, ellipsis='..')
        svg = t.to_svg(0)
        assert 'Hello..' in svg


class TestWrap:
    def test_basic_wrap(self):
        t = Text(text='This is a long text that should be wrapped', x=100, y=100)
        result = t.wrap(max_width=200)
        assert result is not None

    def test_short_text_no_wrap(self):
        t = Text(text='Hi', x=100, y=100, font_size=20)
        result = t.wrap(max_width=500)
        assert result is not None


class TestAddBackgroundRectangle:
    def test_basic(self):
        t = Text(text='Hello', x=100, y=100)
        result = t.add_background_rectangle()
        assert isinstance(result, VCollection)

    def test_custom_color(self):
        t = Text(text='Hello', x=100, y=100)
        result = t.add_background_rectangle(color='#FF0000', opacity=0.8)
        assert isinstance(result, VCollection)
