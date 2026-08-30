from core.models import DiagramType
from core.parser import parse_description


def test_arrow_syntax_creates_a_chain():
    diagram = parse_description(
        "User -> API -> Redis -> PostgreSQL",
        "Chain",
        DiagramType.WORKFLOW,
    )

    assert [(edge.source, edge.target) for edge in diagram.edges] == [
        ("user", "api"),
        ("api", "redis"),
        ("redis", "postgresql"),
    ]
