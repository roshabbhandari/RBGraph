from backend.database import init_db, list_diagrams, save_diagram
from core.models import Diagram, DiagramType


def test_history_listing_supports_safe_limits(tmp_path, monkeypatch):
    monkeypatch.setattr("backend.database.DB_PATH", tmp_path / "history.db")
    init_db()

    for index in range(5):
        save_diagram(
            Diagram(
                name=f"Diagram {index}",
                diagram_type=DiagramType.ARCHITECTURE,
                nodes=[],
                edges=[],
            )
        )

    items = list_diagrams(limit=2, offset=1)

    assert len(items) == 2
    assert items[0]["name"] == "Diagram 3"
