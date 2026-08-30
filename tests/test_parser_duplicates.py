from core.models import DiagramType
from core.parser import parse_description


def test_parser_deduplicates_same_connection_with_different_verbs():
    diagram = parse_description(
        "API stores data in PostgreSQL and API uses PostgreSQL",
        "Duplicate Relations",
        DiagramType.DATA_FLOW,
    )

    matches = [edge for edge in diagram.edges if edge.source == "api" and edge.target == "postgresql"]

    assert len(matches) == 1
