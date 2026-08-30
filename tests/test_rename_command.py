from core.commands import apply_command
from core.models import DiagramType
from core.parser import parse_description
from core.renderer import render_svg


def test_rename_command_updates_label_and_id():
    diagram = parse_description("User connects to API", "Rename", DiagramType.ARCHITECTURE)
    render_svg(diagram)

    updated, _ = apply_command(diagram, "rename API to Gateway")

    assert any(node.label == "Gateway" and node.id == "gateway" for node in updated.nodes)
    assert all(edge.source != "api" and edge.target != "api" for edge in updated.edges)
    assert any(edge.source == "user" and edge.target == "gateway" for edge in updated.edges)
