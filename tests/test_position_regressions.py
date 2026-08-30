from core.commands import apply_command
from core.models import DiagramType
from core.parser import parse_description
from core.renderer import render_svg


def test_move_command_keeps_nodes_inside_the_canvas():
    diagram = parse_description("User connects to API", "Bounds", DiagramType.ARCHITECTURE)
    render_svg(diagram)
    user = next(node for node in diagram.nodes if node.id == "user")
    user.x = 40
    user.y = 40

    updated, _ = apply_command(diagram, "move User left")

    assert updated.nodes[0].x >= 96
    assert updated.nodes[0].y >= 48
