from core.renderer import _wrap_label


def test_long_labels_are_wrapped_without_overflow():
    lines = _wrap_label("SupercalifragilisticComponent", 20)

    assert lines
    assert all(len(line) <= 20 for line in lines)
