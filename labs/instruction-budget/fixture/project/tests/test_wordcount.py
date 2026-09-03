from textkit.wordcount import word_count


def test_basic():
    assert word_count("a b c") == 3


def test_empty():
    assert word_count("") == 0
