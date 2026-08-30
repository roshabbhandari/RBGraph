import re
import xml.etree.ElementTree as ET
from math import isfinite
from typing import List

from core.models import Diagram


def validate_diagram(diagram: Diagram) -> List[str]:
    errors = []

    if not diagram.name.strip():
        errors.append("Diagram name cannot be empty.")
    if not diagram.nodes:
        errors.append("Diagram must contain at least one node.")

    node_ids = [node.id for node in diagram.nodes]
    if len(node_ids) != len(set(node_ids)):
        errors.append("Diagram contains duplicate node IDs.")

    for node in diagram.nodes:
        if not re.fullmatch(r"[a-zA-Z0-9_-]+", node.id):
            errors.append(f"Invalid node ID: {node.id}.")
        if node.x is not None and (not isfinite(node.x) or node.x < -10000 or node.x > 100000):
            errors.append(f"Invalid x position for {node.id}.")
        if node.y is not None and (not isfinite(node.y) or node.y < -10000 or node.y > 100000):
            errors.append(f"Invalid y position for {node.id}.")

    known_ids = set(node_ids)
    edge_pairs = set()
    for edge in diagram.edges:
        if edge.source not in known_ids:
            errors.append(f"Edge source does not exist: {edge.source}.")
        if edge.target not in known_ids:
            errors.append(f"Edge target does not exist: {edge.target}.")
        if edge.source == edge.target:
            errors.append(f"Self-referencing edge is not allowed: {edge.source}.")
        pair = (edge.source, edge.target)
        if pair in edge_pairs:
            errors.append(f"Duplicate edge is not allowed: {edge.source} -> {edge.target}.")
        edge_pairs.add(pair)

    return errors


def validate_svg(svg: str) -> List[str]:
    errors = []
    try:
        root = ET.fromstring(svg)
    except ET.ParseError as exc:
        return [f"SVG parsing failed: {exc}"]

    if root.tag.split("}")[-1] != "svg":
        errors.append("SVG root element is invalid.")

    view_box = root.attrib.get("viewBox", "").split()
    if len(view_box) != 4:
        errors.append("SVG viewBox must contain four numbers.")
    else:
        try:
            values = [float(value) for value in view_box]
            if any(not isfinite(value) for value in values):
                errors.append("SVG viewBox contains a non-finite value.")
            elif values[2] <= 0 or values[3] <= 0:
                errors.append("SVG viewBox width and height must be positive.")
        except ValueError:
            errors.append("SVG viewBox must contain numeric values.")

    lowered = svg.lower()
    if "<script" in lowered or "<foreignobject" in lowered:
        errors.append("SVG contains an unsafe element.")
    if re.search(r"(?:xlink:)?href\s*=\s*['\"]\s*(?:javascript:|data:text/html)", svg, re.I):
        errors.append("SVG contains an unsafe link.")
    if re.search(r"\bon(?:load|error|click|mouseover|focus)\s*=", svg, re.I):
        errors.append("SVG contains an unsafe event handler.")
    if len(list(root)) < 2:
        errors.append("SVG does not contain enough visual structure.")

    return errors
