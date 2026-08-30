import backend.database as database
from core.models import Diagram, DiagramType, Node


def test_database_round_trip(tmp_path):
    database.DB_PATH = tmp_path / "rbgraph.db"
    database.init_db()

    diagram = Diagram(
        name="Stored",
        diagram_type=DiagramType.ARCHITECTURE,
        nodes=[Node(id="api", label="API")],
    )

    diagram_id = database.save_diagram(diagram)
    assert diagram_id > 0

    items = database.list_diagrams()
    assert items[0]["name"] == "Stored"

    loaded = database.get_saved_diagram(diagram_id)
    assert loaded is not None
    assert loaded.name == "Stored"
    assert loaded.nodes[0].label == "API"

    assert database.delete_diagram(diagram_id) is True
    assert database.get_saved_diagram(diagram_id) is None
