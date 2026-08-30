from core.models import Diagram, DiagramType, Edge, Node
from core.validator import validate_diagram


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
