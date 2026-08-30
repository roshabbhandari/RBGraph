from core.models import Diagram, DiagramType, Edge, Node
from core.renderer import render_svg
from core.validator import validate_diagram, validate_svg


def test_valid_diagram_has_no_errors():
    diagram = Diagram(
        name="Valid",
        diagram_type=DiagramType.ARCHITECTURE,
        nodes=[Node(id="api", label="API")],
    )
    assert validate_diagram(diagram) == []


def test_unknown_edge_target_is_reported():
    diagram = Diagram(
        name="Invalid",
        diagram_type=DiagramType.ARCHITECTURE,
        nodes=[Node(id="api", label="API")],
        edges=[Edge(source="api", target="missing")],
    )
    errors = validate_diagram(diagram)
    assert any("Edge target does not exist" in error for error in errors)


def test_rendered_svg_is_valid():
    diagram = Diagram(
        name="SVG",
        diagram_type=DiagramType.WORKFLOW,
        nodes=[Node(id="a", label="A"), Node(id="b", label="B")],
        edges=[Edge(source="a", target="b")],
    )
    svg = render_svg(diagram)
    assert validate_svg(svg) == []
