from core.commands import apply_command
from core.models import DiagramType
from core.parser import parse_description
from core.renderer import render_svg


def test_connect_command_links_existing_nodes():
    diagram = parse_description("User connects to API", "Connect", DiagramType.ARCHITECTURE)
    render_svg(diagram)

    updated, _ = apply_command(diagram, "connect API to Redis")

    assert any(node.label == "Redis" for node in updated.nodes)
    assert any(edge.source == "api" and edge.target == "redis" for edge in updated.edges)
