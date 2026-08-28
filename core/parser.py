
import re

from core.models import Diagram, DiagramType, Edge, Node


def clean_name(value: str) -> str:
    """Clean a component name."""
    value = value.strip()
    value = re.sub(r"\s+", " ", value)
    return value


def parse_description(
    description: str,
    name: str = "Untitled Diagram",
    diagram_type: DiagramType = DiagramType.ARCHITECTURE,
) -> Diagram:
    """
    Convert a simple plain-English description
    into an RBGraph diagram model.
    """

    description = clean_name(description)

    if not description:
        raise ValueError("Description cannot be empty.")

    nodes = {}
    edges = []

    # Detect simple relationships such as:
    # "User connects to API"
    # "API connects to PostgreSQL"
    pattern = re.compile(
        r"([A-Za-z0-9_.-]+(?:\s+[A-Za-z0-9_.-]+)*)"
        r"\s+(?:connects?\s+to|sends?\s+to|calls?|uses?)\s+"
        r"([A-Za-z0-9_.-]+(?:\s+[A-Za-z0-9_.-]+)*)",
        re.IGNORECASE,
    )

    matches = pattern.findall(description)

    for source, target in matches:
        source = clean_name(source)
        target = clean_name(target)

        source_id = source.lower().replace(" ", "-")
        target_id = target.lower().replace(" ", "-")

        if source_id not in nodes:
            nodes[source_id] = Node(
                id=source_id,
                label=source,
                category=detect_category(source),
            )

        if target_id not in nodes:
            nodes[target_id] = Node(
                id=target_id,
                label=target,
                category=detect_category(target),
            )

        edges.append(
            Edge(
                source=source_id,
                target=target_id,
            )
        )

    return Diagram(
        name=name,
        diagram_type=diagram_type,
        nodes=list(nodes.values()),
        edges=edges,
    )


def detect_category(label: str) -> str:
    """
    Detect a basic visual category from a technology/component name.
    """

    value = label.lower()

    categories = {
        "postgres": "database",
        "postgresql": "database",
        "mysql": "database",
        "sqlite": "database",
        "mongodb": "database",
        "redis": "cache",
        "api": "backend",
        "fastapi": "backend",
        "backend": "backend",
        "frontend": "frontend",
        "react": "frontend",
        "user": "user",
        "client": "user",
        "github": "service",
        "github-actions": "automation",
        "openai": "ai",
        "lambda": "serverless",
        "aws": "cloud",
    }

    for keyword, category in categories.items():
        if keyword in value:
            return category

    return "default"

