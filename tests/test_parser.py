from core.models import DiagramType
from core.parser import canonical_label, detect_category, parse_description


def test_parser_detects_chained_services():
    diagram = parse_description(
        "User connects to FastAPI and FastAPI uses Redis and PostgreSQL",
        "Demo",
        DiagramType.ARCHITECTURE,
    )
    labels = {node.label for node in diagram.nodes}
    assert {"User", "FastAPI", "Redis", "PostgreSQL"}.issubset(labels)
    assert len(diagram.edges) >= 3


def test_parser_prefers_longer_technology_aliases():
    assert canonical_label("AWS Lambda") == "AWS Lambda"
    assert detect_category("AWS Lambda") == "serverless"


def test_parser_supports_arrow_notation():
    diagram = parse_description("Browser -> API -> PostgreSQL")
    assert len(diagram.nodes) == 3
    assert len(diagram.edges) == 2
