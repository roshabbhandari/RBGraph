from core.commands import apply_command
from core.models import DiagramType
from core.parser import parse_description
from core.renderer import render_svg
from core.validator import validate_diagram, validate_svg


def test_architecture_generation():
    diagram = parse_description(
        "User connects to FastAPI and FastAPI uses Redis and PostgreSQL",
        "Demo",
        DiagramType.ARCHITECTURE,
    )
    assert {node.label for node in diagram.nodes} >= {"User", "FastAPI", "Redis", "PostgreSQL"}
    assert not validate_diagram(diagram)
    svg = render_svg(diagram)
    assert svg.startswith("<svg")
    assert not validate_svg(svg)


def test_technology_categories():
    diagram = parse_description(
        "GitHub Actions deploys to AWS Lambda and AWS Lambda uses OpenAI",
        "Deploy",
        DiagramType.WORKFLOW,
    )
    categories = {node.category for node in diagram.nodes}
    assert {"automation", "serverless", "ai"}.issubset(categories)


def test_chat_command_add_move_and_highlight():
    diagram = parse_description("User connects to API and API uses Redis", "Commands", DiagramType.ARCHITECTURE)
    diagram = render_ready(diagram)
    updated, message = apply_command(diagram, "add PostgreSQL to API")
    assert "PostgreSQL" in message
    assert any(node.label == "PostgreSQL" for node in updated.nodes)
    moved, _ = apply_command(updated, "move API left")
    api_before = next(node for node in updated.nodes if node.label == "API")
    api_after = next(node for node in moved.nodes if node.label == "API")
    assert api_after.x < api_before.x
    highlighted, _ = apply_command(moved, "highlight rollback path")
    assert any(edge.highlighted for edge in highlighted.edges)


def render_ready(diagram):
    render_svg(diagram)
    return diagram
