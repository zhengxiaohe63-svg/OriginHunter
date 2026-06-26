from modules.similarity import _ratio


def test_ratio_identical():
    assert _ratio("abc", "abc") == 1.0
