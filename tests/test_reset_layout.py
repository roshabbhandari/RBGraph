from core.commands import apply_command
from core.models import DiagramType
from core.parser import parse_description
from core.renderer import render_svg


def test_reset_layout_clears_manual_positions():
    diagram = parse_description("User connects to API and API uses Redis", "Reset", DiagramType.ARCHITECTURE)
    render_svg(diagram)
    diagram.nodes[0].x = 900
    diagram.nodes[0].y = 700

    updated, _ = apply_command(diagram, "reset layout")

    assert all(node.x is None and node.y is None for node in updated.nodes)
