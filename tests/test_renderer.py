from core.models import Diagram, DiagramType, Edge, Node
from core.renderer import render_svg


def test_renderer_outputs_svg_root():
    diagram = Diagram(
        name="Render",
        diagram_type=DiagramType.ARCHITECTURE,
        nodes=[Node(id="api", label="FastAPI", category="backend")],
    )
    svg = render_svg(diagram)
    assert svg.startswith("<svg")
    assert "FastAPI" in svg


def test_renderer_includes_arrow_marker_and_edge():
    diagram = Diagram(
        name="Connections",
        diagram_type=DiagramType.ARCHITECTURE,
        nodes=[Node(id="api", label="API"), Node(id="db", label="PostgreSQL", category="database")],
        edges=[Edge(source="api", target="db", label="queries")],
    )
    svg = render_svg(diagram)
    assert 'id="arrow"' in svg
    assert "queries" in svg
