from html import escape
from math import isfinite
from typing import Dict, List, Tuple

from core.models import Diagram, DiagramType, Node


CATEGORY_MARKS = {
    "user": "U",
    "frontend": "UI",
    "backend": "API",
    "database": "DB",
    "cache": "R",
    "automation": "CI",
    "ai": "AI",
    "cloud": "C",
    "serverless": "L",
    "service": "S",
    "security": "AUTH",
    "default": "N",
}

NODE_WIDTH = 176
NODE_HEIGHT = 88
H_GAP = 88
V_GAP = 72


def render_svg(diagram: Diagram) -> str:
    if not diagram.nodes:
        raise ValueError("A diagram must contain at least one node.")

    if all(node.x is not None and node.y is not None for node in diagram.nodes):
        positions = {node.id: (float(node.x), float(node.y)) for node in diagram.nodes}
    else:
        positions = _layout_nodes(diagram)
        for node in diagram.nodes:
            node.x, node.y = positions[node.id]

    width = max(920, max(x for x, _ in positions.values()) + NODE_WIDTH / 2 + 80)
    height = max(560, max(y for _, y in positions.values()) + NODE_HEIGHT / 2 + 100)

    parts = [
        f'<svg class="rbgraph-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:g} {height:g}" role="img" aria-label="{escape(diagram.name)}">',
        _svg_style(),
        _grid(width, height),
        _arrow_defs(),
    ]

    if diagram.diagram_type == DiagramType.SEQUENCE:
        parts.extend(_sequence_guides(diagram, positions, height))

    for edge in diagram.edges:
        if edge.source in positions and edge.target in positions:
            parts.append(_render_edge(diagram, edge, positions))

    for node in diagram.nodes:
        parts.append(_render_node(node, positions[node.id]))

    parts.append("</svg>")
    svg = "\n".join(parts)

    if not _finite_positions(diagram):
        raise ValueError("The layout produced an invalid coordinate.")

    return svg


def _layout_nodes(diagram: Diagram) -> Dict[str, Tuple[float, float]]:
    if diagram.diagram_type == DiagramType.SEQUENCE:
        return _layout_sequence(diagram)
    if diagram.diagram_type == DiagramType.LIFECYCLE:
        return _layout_lifecycle(diagram)
    return _layout_graph(diagram)


def _layout_graph(diagram: Diagram) -> Dict[str, Tuple[float, float]]:
    ids = [node.id for node in diagram.nodes]
    incoming = {node_id: 0 for node_id in ids}
    outgoing: Dict[str, List[str]] = {node_id: [] for node_id in ids}

    for edge in diagram.edges:
        if edge.source in outgoing and edge.target in incoming:
            outgoing[edge.source].append(edge.target)
            incoming[edge.target] += 1

    levels = {node_id: 0 for node_id in ids}
    queue = [node_id for node_id in ids if incoming[node_id] == 0]
    visited = set()

    while queue:
        current = queue.pop(0)
        visited.add(current)
        for target in outgoing[current]:
            levels[target] = max(levels[target], levels[current] + 1)
            incoming[target] -= 1
            if incoming[target] == 0:
                queue.append(target)

    for index, node_id in enumerate(ids):
        if node_id not in visited:
            levels[node_id] = max(levels[node_id], index // 4)

    grouped: Dict[int, List[str]] = {}
    for node_id in ids:
        grouped.setdefault(levels[node_id], []).append(node_id)

    positions = {}
    for level, group in sorted(grouped.items()):
        columns = min(4, max(1, len(group)))
        for index, node_id in enumerate(group):
            row = index // columns
            column = index % columns
            positions[node_id] = (
                140 + column * (NODE_WIDTH + H_GAP),
                120 + row * (NODE_HEIGHT + V_GAP) + level * 34,
            )
    return positions


def _layout_sequence(diagram: Diagram) -> Dict[str, Tuple[float, float]]:
    return {node.id: (150 + index * (NODE_WIDTH + H_GAP), 120) for index, node in enumerate(diagram.nodes)}


def _layout_lifecycle(diagram: Diagram) -> Dict[str, Tuple[float, float]]:
    return {node.id: (150 + index * (NODE_WIDTH + H_GAP), 290) for index, node in enumerate(diagram.nodes)}


def _render_node(node: Node, position: Tuple[float, float]) -> str:
    x, y = position
    mark = CATEGORY_MARKS.get(node.category, CATEGORY_MARKS["default"])
    label_lines = _wrap_label(node.label, 20)
    label_start = y - 2 - (len(label_lines) - 1) * 9
    text = []
    for index, line in enumerate(label_lines):
        text.append(f'<tspan x="{x:g}" dy="{0 if index == 0 else 18}">{escape(line)}</tspan>')

    return f'''<g class="rbgraph-node" data-id="{escape(node.id)}" data-category="{escape(node.category)}">
  <rect x="{x - NODE_WIDTH / 2:g}" y="{y - NODE_HEIGHT / 2:g}" width="{NODE_WIDTH}" height="{NODE_HEIGHT}" rx="18" />
  <circle cx="{x - 58:g}" cy="{y - 22:g}" r="16" class="rbgraph-mark" />
  <text x="{x - 58:g}" y="{y - 17:g}" text-anchor="middle" class="rbgraph-mark-text">{escape(mark)}</text>
  <text x="{x:g}" y="{label_start:g}" text-anchor="middle" class="rbgraph-label">{''.join(text)}</text>
  <text x="{x:g}" y="{y + 30:g}" text-anchor="middle" class="rbgraph-category">{escape(node.category)}</text>
</g>'''.strip()


def _render_edge(diagram: Diagram, edge, positions: Dict[str, Tuple[float, float]]) -> str:
    source_x, source_y = positions[edge.source]
    target_x, target_y = positions[edge.target]
    highlighted = " highlighted" if edge.highlighted else ""

    if diagram.diagram_type == DiagramType.SEQUENCE:
        x1, y1 = source_x, source_y + NODE_HEIGHT / 2
        x2, y2 = target_x, y1 + 82
    else:
        x1, y1 = _anchor(source_x, source_y, target_x, target_y)
        x2, y2 = _anchor(target_x, target_y, source_x, source_y)

    if abs(target_x - source_x) < 4:
        curve = f"M {x1:g} {y1:g} C {x1 + 70:g} {y1 + 22:g}, {x2 + 70:g} {y2 - 22:g}, {x2:g} {y2:g}"
    else:
        mid_x = (x1 + x2) / 2
        curve = f"M {x1:g} {y1:g} C {mid_x:g} {y1:g}, {mid_x:g} {y2:g}, {x2:g} {y2:g}"

    label = ""
    if edge.label:
        label = f'<text x="{(x1 + x2) / 2:g}" y="{(y1 + y2) / 2 - 10:g}" text-anchor="middle" class="rbgraph-edge-label">{escape(edge.label)}</text>'

    return f'''<g class="rbgraph-edge{highlighted}">
  <path d="{curve}" class="rbgraph-edge-line" marker-end="url(#rbgraph-arrow)" />
  {label}
</g>'''.strip()


def _sequence_guides(diagram: Diagram, positions: Dict[str, Tuple[float, float]], height: float) -> List[str]:
    return [
        f'<line x1="{positions[node.id][0]:g}" y1="{positions[node.id][1] + NODE_HEIGHT / 2:g}" x2="{positions[node.id][0]:g}" y2="{height - 50:g}" class="rbgraph-lifeline" />'
        for node in diagram.nodes
    ]


def _anchor(x1: float, y1: float, x2: float, y2: float) -> Tuple[float, float]:
    dx = x2 - x1
    dy = y2 - y1
    if abs(dx) >= abs(dy):
        return x1 + (NODE_WIDTH / 2 if dx >= 0 else -NODE_WIDTH / 2), y1
    return x1, y1 + (NODE_HEIGHT / 2 if dy >= 0 else -NODE_HEIGHT / 2)


def _wrap_label(label: str, limit: int) -> List[str]:
    words = label.split()
    if not words:
        return [""]
    lines = []
    current = words[0]
    for word in words[1:]:
        if len(current) + len(word) + 1 <= limit:
            current = f"{current} {word}"
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines[:3]


def _finite_positions(diagram: Diagram) -> bool:
    return all(
        node.x is not None and node.y is not None and isfinite(node.x) and isfinite(node.y)
        for node in diagram.nodes
    )


def _svg_style() -> str:
    return '''<style>
svg{--rb-bg:#f8fafc;--rb-grid:#e2e8f0;--rb-text:#0f172a;--rb-muted:#64748b;--rb-edge:#64748b;--rb-card:#ffffff;--rb-border:#dbe3ee;--rb-user:#2563eb;--rb-frontend:#7c3aed;--rb-backend:#0891b2;--rb-database:#059669;--rb-cache:#d97706;--rb-automation:#db2777;--rb-ai:#9333ea;--rb-cloud:#0284c7;--rb-serverless:#ea580c;--rb-service:#475569;--rb-security:#be123c;--rb-default:#64748b;background:var(--rb-bg);color:var(--rb-text);font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
@media(prefers-color-scheme:dark){svg{--rb-bg:#0b1220;--rb-grid:#1c2838;--rb-text:#e5edf8;--rb-muted:#8da2bc;--rb-edge:#8091aa;--rb-card:#111b2b;--rb-border:#253348}}
.rbgraph-grid{fill:url(#rbgraph-pattern)}
.rbgraph-node rect{fill:var(--rb-card);stroke:var(--rb-border);stroke-width:2;filter:drop-shadow(0 8px 20px rgba(15,23,42,.1))}
.rbgraph-node[data-category="user"] .rbgraph-mark{fill:var(--rb-user)}
.rbgraph-node[data-category="frontend"] .rbgraph-mark{fill:var(--rb-frontend)}
.rbgraph-node[data-category="backend"] .rbgraph-mark{fill:var(--rb-backend)}
.rbgraph-node[data-category="database"] .rbgraph-mark{fill:var(--rb-database)}
.rbgraph-node[data-category="cache"] .rbgraph-mark{fill:var(--rb-cache)}
.rbgraph-node[data-category="automation"] .rbgraph-mark{fill:var(--rb-automation)}
.rbgraph-node[data-category="ai"] .rbgraph-mark{fill:var(--rb-ai)}
.rbgraph-node[data-category="cloud"] .rbgraph-mark{fill:var(--rb-cloud)}
.rbgraph-node[data-category="serverless"] .rbgraph-mark{fill:var(--rb-serverless)}
.rbgraph-node[data-category="service"] .rbgraph-mark{fill:var(--rb-service)}
.rbgraph-node[data-category="security"] .rbgraph-mark{fill:var(--rb-security)}
.rbgraph-node[data-category="default"] .rbgraph-mark{fill:var(--rb-default)}
.rbgraph-mark-text{fill:#fff;font-size:9px;font-weight:800}
.rbgraph-label{fill:var(--rb-text);font-size:16px;font-weight:700}
.rbgraph-category{fill:var(--rb-muted);font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase}
.rbgraph-edge-line{fill:none;stroke:var(--rb-edge);stroke-width:2.5}
.rbgraph-edge-label{fill:var(--rb-muted);font-size:11px;font-weight:600;paint-order:stroke;stroke:var(--rb-bg);stroke-width:6;stroke-linejoin:round}
.rbgraph-edge.highlighted .rbgraph-edge-line{stroke:#ef4444;stroke-width:4}
.rbgraph-edge.highlighted .rbgraph-edge-label{fill:#ef4444}
.rbgraph-lifeline{stroke:var(--rb-grid);stroke-width:2;stroke-dasharray:5 8}
</style>'''.strip()


def _grid(width: float, height: float) -> str:
    return f'''<defs><pattern id="rbgraph-pattern" width="32" height="32" patternUnits="userSpaceOnUse"><path d="M32 0H0V32" fill="none" stroke="var(--rb-grid)" stroke-width="1" opacity=".55" /></pattern></defs><rect width="{width:g}" height="{height:g}" class="rbgraph-grid" />'''.strip()


def _arrow_defs() -> str:
    return '<defs><marker id="rbgraph-arrow" markerWidth="11" markerHeight="11" refX="9" refY="4" orient="auto" markerUnits="strokeWidth"><path d="M0 0 L0 8 L10 4 z" fill="var(--rb-edge)" /></marker></defs>'
