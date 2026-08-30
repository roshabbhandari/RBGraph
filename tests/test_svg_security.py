from core.validator import validate_svg


def test_unsafe_svg_href_is_rejected():
    svg = '<svg xmlns="http://www.w3.org/2000/svg"><a href="javascript:alert(1)"><text>x</text></a></svg>'

    errors = validate_svg(svg)

    assert any("unsafe" in error.lower() for error in errors)
