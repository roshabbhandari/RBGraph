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
