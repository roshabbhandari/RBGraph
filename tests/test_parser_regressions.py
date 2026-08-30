from core.models import DiagramType
from core.parser import parse_description


def test_parser_understands_storage_language():
    diagram = parse_description(
        "API stores data in PostgreSQL",
        "Storage",
        DiagramType.DATA_FLOW,
    )

    labels = {node.label for node in diagram.nodes}

    assert {"API", "PostgreSQL"}.issubset(labels)
    assert any(edge.source == "api" and edge.target == "postgresql" for edge in diagram.edges)
