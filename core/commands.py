import re
from copy import deepcopy
from typing import Tuple

from core.models import Diagram, Edge, Node
from core.parser import canonical_label, detect_category, normalize_id


def apply_command(diagram: Diagram, command: str) -> Tuple[Diagram, str]:
    text = " ".join(command.strip().split())
    if not text:
        raise ValueError("Command cannot be empty.")

    result = deepcopy(diagram)

    add_match = re.fullmatch(r"add\s+(.+?)(?:\s+to\s+(.+))?", text, re.I)
    if add_match:
        label = canonical_label(add_match.group(1))
        target_label = add_match.group(2)
        node_id = normalize_id(label)
        if any(node.id == node_id for node in result.nodes):
            return result, f"{label} is already in the diagram."

        _ensure_positions(result)
        node = Node(id=node_id, label=label, category=detect_category(label))

        if target_label:
            target_id = _find_node(result, target_label)
            if target_id:
                target = next(item for item in result.nodes if item.id == target_id)
                node.x = target.x + 260
                node.y = target.y
                result.nodes.append(node)
                result.edges.append(Edge(source=target_id, target=node_id, label="connects"))
                return result, f"Added {label} and connected it to {target.label}."

        last = result.nodes[-1] if result.nodes else None
        node.x = last.x + 260 if last and last.x is not None else 140
        node.y = last.y if last and last.y is not None else 120
        result.nodes.append(node)
        if last:
            result.edges.append(Edge(source=last.id, target=node_id, label="connects"))
        return result, f"Added {label}."

    remove_match = re.fullmatch(r"(?:remove|delete)\s+(.+)", text, re.I)
    if remove_match:
        node_id = _find_node(result, remove_match.group(1))
        if not node_id:
            raise ValueError("That node is not in the diagram.")
        label = next(node.label for node in result.nodes if node.id == node_id)
        result.nodes = [node for node in result.nodes if node.id != node_id]
        result.edges = [edge for edge in result.edges if edge.source != node_id and edge.target != node_id]
        return result, f"Removed {label}."

    move_match = re.fullmatch(r"move\s+(.+?)\s+(left|right|up|down)", text, re.I)
    if move_match:
        node_id = _find_node(result, move_match.group(1))
        if not node_id:
            raise ValueError("That node is not in the diagram.")
        _ensure_positions(result)
        node = next(item for item in result.nodes if item.id == node_id)
        offsets = {"left": (-220, 0), "right": (220, 0), "up": (0, -150), "down": (0, 150)}
        dx, dy = offsets[move_match.group(2).lower()]
        node.x += dx
        node.y += dy
        return result, f"Moved {node.label} {move_match.group(2).lower()}."

    if re.fullmatch(r"(?:clear|remove)\s+highlight(?:s)?", text, re.I):
        for edge in result.edges:
            edge.highlighted = False
        return result, "Cleared highlighted paths."

    highlight_match = re.fullmatch(r"highlight\s+(.+)", text, re.I)
    if highlight_match:
        phrase = highlight_match.group(1).lower()
        tokens = [token for token in re.findall(r"[a-z0-9_-]+", phrase) if token not in {"the", "path"}]
        for edge in result.edges:
            source = _node_label(result, edge.source).lower()
            target = _node_label(result, edge.target).lower()
            label = (edge.label or "").lower()
            haystack = f"{source} {target} {label}"
            edge.highlighted = any(token in haystack for token in tokens)

        if not any(edge.highlighted for edge in result.edges):
            for edge in result.edges:
                haystack = f"{_node_label(result, edge.source).lower()} {_node_label(result, edge.target).lower()} {(edge.label or '').lower()}"
                edge.highlighted = any(token in haystack for token in ("rollback", "failure", "error", "restore", "deploy"))

        if not any(edge.highlighted for edge in result.edges):
            for edge in result.edges:
                edge.highlighted = True
        return result, f"Highlighted {phrase}."

    raise ValueError("Use add, remove, move, or highlight commands.")


def _ensure_positions(diagram: Diagram) -> None:
    for index, node in enumerate(diagram.nodes):
        if node.x is None:
            node.x = 140 + index * 260
        if node.y is None:
            node.y = 120


def _find_node(diagram: Diagram, query: str) -> str | None:
    normalized = " ".join(query.strip().split()).lower()
    query_id = normalize_id(normalized)
    for node in diagram.nodes:
        if node.id == query_id or node.label.lower() == normalized or normalized in node.label.lower():
            return node.id
    return None


def _node_label(diagram: Diagram, node_id: str) -> str:
    node = next((item for item in diagram.nodes if item.id == node_id), None)
    return node.label if node else node_id
