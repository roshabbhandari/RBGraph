from pydantic import ValidationError
import pytest

from core.models import Diagram, DiagramType, Edge, Node


def test_diagram_model_defaults_are_empty():
    diagram = Diagram(name="Demo", diagram_type=DiagramType.ARCHITECTURE)
    assert diagram.nodes == []
    assert diagram.edges == []


def test_edge_supports_highlight_state():
    edge = Edge(source="api", target="db", highlighted=True)
    assert edge.highlighted is True


def test_node_rejects_empty_label():
    with pytest.raises(ValidationError):
        Node(id="api", label="")
