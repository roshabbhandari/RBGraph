from backend import main
from core.models import Diagram, DiagramType, Node


def test_validate_route_returns_structured_errors():
    diagram = Diagram(
        name="Invalid",
        diagram_type=DiagramType.ARCHITECTURE,
        nodes=[Node(id="api", label="API")],
    )

    result = main.validate_route(diagram)

    assert result == {"valid": True, "errors": []}


def test_history_route_passes_pagination_to_storage(monkeypatch):
    captured = {}

    def fake_list_diagrams(limit, offset):
        captured["limit"] = limit
        captured["offset"] = offset
        return []

    monkeypatch.setattr(main, "list_diagrams", fake_list_diagrams)

    result = main.history(limit=12, offset=4)

    assert result == {"items": []}
    assert captured == {"limit": 12, "offset": 4}
