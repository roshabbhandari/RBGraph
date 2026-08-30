from core.models import Diagram, DiagramType, Edge, Node
from core.validator import validate_diagram, validate_svg


def test_self_referencing_edge_is_rejected():
    diagram = Diagram(
        name="Self Edge",
        diagram_type=DiagramType.ARCHITECTURE,
        nodes=[Node(id="api", label="API")],
        edges=[Edge(source="api", target="api")],
    )

    errors = validate_diagram(diagram)

    assert any("self" in error.lower() for error in errors)


def test_duplicate_connections_are_rejected_even_with_labels():
    diagram = Diagram(
        name="Duplicate Edges",
        diagram_type=DiagramType.ARCHITECTURE,
        nodes=[Node(id="api", label="API"), Node(id="db", label="PostgreSQL")],
        edges=[
            Edge(source="api", target="db", label="reads"),
            Edge(source="api", target="db", label="writes"),
        ],
    )

    errors = validate_diagram(diagram)

    assert any("duplicate" in error.lower() for error in errors)


def test_invalid_svg_viewbox_is_rejected():
    svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 nope 900 500"><rect width="900" height="500"/></svg>'

    errors = validate_svg(svg)

    assert any("viewbox" in error.lower() for error in errors)
