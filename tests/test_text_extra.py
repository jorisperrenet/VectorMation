"""Tests for Text methods with zero or minimal test coverage."""
from vectormation.objects import Text, VectorMathAnim


class TestGetText:
    def test_returns_initial(self):
        t = Text(text='hello', x=100, y=100, creation=0)
        assert t.get_text() == 'hello'

    def test_after_update(self):
        t = Text(text='hello', x=100, y=100, creation=0)
        t.update_text('world', start=1)
        assert t.get_text(time=1) == 'world'
        assert t.get_text(time=0) == 'hello'


class TestGetFontSize:
    def test_returns_initial(self):
        t = Text(text='hi', x=100, y=100, font_size=30, creation=0)
        assert t.get_font_size() == 30

    def test_default_size(self):
        t = Text(text='hi', x=100, y=100, creation=0)
        assert t.get_font_size() == 48


class TestStartsEndsWith:
    def test_starts_with_true(self):
        t = Text(text='hello world', x=100, y=100, creation=0)
        assert t.starts_with('hello')

    def test_starts_with_false(self):
        t = Text(text='hello world', x=100, y=100, creation=0)
        assert not t.starts_with('world')

    def test_ends_with_true(self):
        t = Text(text='hello world', x=100, y=100, creation=0)
        assert t.ends_with('world')

    def test_ends_with_false(self):
        t = Text(text='hello world', x=100, y=100, creation=0)
        assert not t.ends_with('hello')


class TestBoldItalic:
    def test_bold_sets_weight(self):
        t = Text(text='hi', x=100, y=100, creation=0)
        t.bold()
        assert t._font_weight == 'bold'

    def test_bold_custom_weight(self):
        t = Text(text='hi', x=100, y=100, creation=0)
        t.bold('600')
        assert t._font_weight == '600'

    def test_bold_normal_clears(self):
        t = Text(text='hi', x=100, y=100, creation=0)
        t.bold()
        t.bold('normal')
        assert t._font_weight is None

    def test_italic_sets_style(self):
        t = Text(text='hi', x=100, y=100, creation=0)
        t.italic()
        assert t._font_style == 'italic'

    def test_italic_normal_clears(self):
        t = Text(text='hi', x=100, y=100, creation=0)
        t.italic()
        t.italic('normal')
        assert t._font_style is None

    def test_bold_in_svg(self):
        t = Text(text='hi', x=100, y=100, creation=0)
        t.bold()
        v = VectorMathAnim(save_dir='/tmp/test_text_extra')
        v.add(t)
        svg = v.generate_frame_svg(time=0)
        assert 'font-weight' in svg

    def test_italic_in_svg(self):
        t = Text(text='hi', x=100, y=100, creation=0)
        t.italic()
        v = VectorMathAnim(save_dir='/tmp/test_text_extra')
        v.add(t)
        svg = v.generate_frame_svg(time=0)
        assert 'font-style' in svg


class TestSetFontFamily:
    def test_sets_family(self):
        t = Text(text='hi', x=100, y=100, creation=0)
        t.set_font_family('Courier')
        assert t._font_family == 'Courier'


class TestSetFontSize:
    def test_changes_size(self):
        t = Text(text='hi', x=100, y=100, font_size=20, creation=0)
        t.set_font_size(40, start=0, end=1)
        assert t.get_font_size(time=1) == 40


class TestTypewrite:
    def test_progressive_reveal(self):
        t = Text(text='hello', x=100, y=100, creation=0)
        t.typewrite(0, 1)
        mid = t.get_text(time=0.5)
        assert len(mid) > 0
        assert len(mid) < len('hello') + 2  # text + possible cursor

    def test_full_text_at_end(self):
        t = Text(text='hello', x=100, y=100, creation=0)
        t.typewrite(0, 1)
        assert t.get_text(time=1) == 'hello'

    def test_cursor_character(self):
        t = Text(text='hello', x=100, y=100, creation=0)
        t.typewrite(0, 1, cursor='_')
        mid = t.get_text(time=0.3)
        if len(mid) > 0 and mid != 'hello':
            assert mid.endswith('_')


class TestUntype:
    def test_empty_at_end(self):
        t = Text(text='hello', x=100, y=100, creation=0)
        t.untype(0, 1)
        assert t.get_text(time=1) == ''

    def test_progressive_removal(self):
        t = Text(text='hello', x=100, y=100, creation=0)
        t.untype(0, 1)
        mid = t.get_text(time=0.5)
        assert len(mid) < 5

    def test_hides_with_change_existence(self):
        t = Text(text='hello', x=100, y=100, creation=0)
        t.untype(0, 1, change_existence=True)
        assert not t.show.at_time(1.5)


class TestScramble:
    def test_settled_at_end(self):
        t = Text(text='hello', x=100, y=100, creation=0)
        t.scramble(0, 1)
        assert t.get_text(time=1) == 'hello'

    def test_scrambled_midway(self):
        t = Text(text='hello', x=100, y=100, creation=0)
        t.scramble(0, 1)
        mid = t.get_text(time=0.3)
        assert len(mid) == 5  # same length as original

    def test_custom_charset(self):
        t = Text(text='abc', x=100, y=100, creation=0)
        t.scramble(0, 1, charset='XYZ')
        mid = t.get_text(time=0.1)
        assert len(mid) == 3

    def test_preserves_spaces(self):
        t = Text(text='a b', x=100, y=100, creation=0)
        t.scramble(0, 1)
        mid = t.get_text(time=0.1)
        assert mid[1] == ' '


class TestUpdateText:
    def test_changes_text(self):
        t = Text(text='hello', x=100, y=100, creation=0)
        t.update_text('world', start=1)
        assert t.get_text(time=0) == 'hello'
        assert t.get_text(time=1) == 'world'


class TestReverseText:
    def test_reverses_in_place(self):
        t = Text(text='hello', x=100, y=100, creation=0)
        t.reverse_text()
        assert t.get_text(time=0) == 'olleh'

    def test_reverse_read_only(self):
        t = Text(text='hello', x=100, y=100, creation=0)
        result = t.reverse(time=0)
        assert result == 'olleh'
        # Original should be unchanged
        assert t.get_text(time=0) == 'hello'


class TestCharAt:
    def test_first_char(self):
        t = Text(text='hello', x=100, y=100, creation=0)
        assert t.char_at(0) == 'h'

    def test_last_char(self):
        t = Text(text='hello', x=100, y=100, creation=0)
        assert t.char_at(4) == 'o'

    def test_out_of_range_returns_empty(self):
        t = Text(text='hello', x=100, y=100, creation=0)
        assert t.char_at(99) == ''


class TestCharCount:
    def test_counts_chars(self):
        t = Text(text='hello', x=100, y=100, creation=0)
        assert t.char_count() == 5

    def test_empty(self):
        t = Text(text='', x=100, y=100, creation=0)
        assert t.char_count() == 0


class TestWordAt:
    def test_first_word(self):
        t = Text(text='hello world', x=100, y=100, creation=0)
        assert t.word_at(0) == 'hello'

    def test_second_word(self):
        t = Text(text='hello world', x=100, y=100, creation=0)
        assert t.word_at(1) == 'world'


class TestWordCount:
    def test_counts_words(self):
        t = Text(text='hello world foo', x=100, y=100, creation=0)
        assert t.word_count() == 3

    def test_single_word(self):
        t = Text(text='hello', x=100, y=100, creation=0)
        assert t.word_count() == 1

    def test_empty(self):
        t = Text(text='', x=100, y=100, creation=0)
        assert t.word_count() == 0


class TestSplitIntoWords:
    def test_returns_vcollection(self):
        t = Text(text='hello world', x=100, y=100, creation=0)
        words = t.split_into_words()
        assert len(words.objects) == 2

    def test_single_word(self):
        t = Text(text='hello', x=100, y=100, creation=0)
        words = t.split_into_words()
        assert len(words.objects) == 1
