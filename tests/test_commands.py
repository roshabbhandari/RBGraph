import pytest

from core.commands import apply_command
from core.models import DiagramType
from core.parser import parse_description


def make_diagram():
    return parse_description(
        "User connects to API and API uses PostgreSQL",
        "Commands",
        DiagramType.ARCHITECTURE,
    )


def test_add_command_creates_node():
    diagram, message = apply_command(make_diagram(), "add Redis")
    assert any(node.label == "Redis" for node in diagram.nodes)
    assert "Added Redis" in message


def test_remove_command_removes_edges_with_node():
    diagram, _ = apply_command(make_diagram(), "remove PostgreSQL")
    assert all(node.label != "PostgreSQL" for node in diagram.nodes)
    assert all(edge.target != "postgresql" for edge in diagram.edges)


def test_move_command_changes_position():
    diagram, _ = apply_command(make_diagram(), "move API right")
    api = next(node for node in diagram.nodes if node.label == "API")
    assert api.x is not None and api.x > 140


def test_unknown_command_is_rejected():
    with pytest.raises(ValueError):
        apply_command(make_diagram(), "rename API")
