```python
from html import escape

from core.models import Diagram


CATEGORY_STYLES = {
    "user": {
        "fill": "#2563eb",
        "stroke": "#1d4ed8",
        "text": "#ffffff",
    },
    "frontend": {
        "fill": "#7c3aed",
        "stroke": "#6d28d9",
        "text": "#ffffff",
    },
    "backend": {
        "fill": "#0891b2",
        "stroke": "#0e7490",
        "text": "#ffffff",
    },
    "database": {
        "fill": "#059669",
        "stroke": "#047857",
        "text": "#ffffff",
    },
    "cache": {
        "fill": "#d97706",
        "stroke": "#b45309",
        "text": "#ffffff",
    },
    "automation": {
        "fill": "#db2777",
        "stroke": "#be185d",
        "text": "#ffffff",
    },
    "ai": {
        "fill": "#9333ea",
        "stroke": "#7e22ce",
        "text": "#ffffff",
    },
    "cloud": {
        "fill": "#0284c7",
        "stroke": "#0369a1",
        "text": "#ffffff",
    },
    "serverless": {
        "fill": "#ea580c",
        "stroke": "#c2410c",
        "text": "#ffffff",
    },
    "service": {
        "fill": "#475569",
        "stroke": "#334155",
        "text": "#ffffff",
    },
    "default": {
        "fill": "#64748b",
        "stroke": "#475569",
        "text": "#ffffff",
    },
}


def render_svg(diagram: Diagram) -> str:
    """
    Render an RBGraph diagram as a self-contained SVG document.
    """

    nodes = diagram.nodes
    edges = diagram.edges

    if not nodes:
        return _empty_svg()

    positions = _calculate_positions(len(nodes))

    node_positions = {}

    for index, node in enumerate(nodes):
        x, y = positions[index]
        node_positions[node.id] = (x, y)

    width = max(900, len(nodes) * 220)
    height = 500

    svg_parts = [
        f'''<svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 {width} {height}"
            width="{width}"
            height="{height}"
            role="img"
            aria-label="{escape(diagram.name)}"
        >''',
        _svg_definitions(),
        _svg_background(width, height),
    ]

    # Draw connections first so nodes appear above them.
    for edge in edges:
        if edge.source not in node_positions:
            continue

        if edge.target not in node_positions:
            continue

        source_x, source_y = node_positions[edge.source]
        target_x, target_y = node_positions[edge.target]

        svg_parts.append(
            _render_edge(
                source_x,
                source_y,
                target_x,
                target_y,
                edge.label,
            )
        )

    # Draw nodes.
    for node in nodes:
        x, y = node_positions[node.id]

        svg_parts.append(
            _render_node(
                x=x,
                y=y,
                label=node.label,
                category=node.category,
            )
        )

    svg_parts.append("</svg>")

    return "\n".join(svg_parts)


def _calculate_positions(node_count: int):
    """
    Create a simple horizontal layout.

    A more advanced automatic layout engine
    will replace this later.
    """

    positions = []

    start_x = 130
    spacing = 200
    y = 250

    for index in range(node_count):
        positions.append(
            (
                start_x + index * spacing,
                y,
            )
        )

    return positions


def _render_node(
    x: float,
    y: float,
    label: str,
    category: str,
) -> str:

    style = CATEGORY_STYLES.get(
        category,
        CATEGORY_STYLES["default"],
    )

    safe_label = escape(label)

    return f'''
    <g class="rbgraph-node">
        <rect
            x="{x - 75}"
            y="{y - 40}"
            width="150"
            height="80"
            rx="12"
            fill="{style["fill"]}"
            stroke="{style["stroke"]}"
            stroke-width="2"
        />

        <text
            x="{x}"
            y="{y + 5}"
            text-anchor="middle"
            font-family="Arial, sans-serif"
            font-size="16"
            font-weight="600"
            fill="{style["text"]}"
        >
            {safe_label}
        </text>

        <text
            x="{x}"
            y="{y + 25}"
            text-anchor="middle"
            font-family="Arial, sans-serif"
            font-size="11"
            fill="{style["text"]}"
            opacity="0.8"
        >
            {escape(category)}
        </text>
    </g>
    '''


def _render_edge(
    source_x: float,
    source_y: float,
    target_x: float,
    target_y: float,
    label: str | None,
) -> str:

    start_x = source_x + 75
    end_x = target_x - 75

    center_x = (start_x + end_x) / 2

    label_svg = ""

    if label:
        label_svg = f'''
        <text
            x="{center_x}"
            y="{source_y - 12}"
            text-anchor="middle"
            font-family="Arial, sans-serif"
            font-size="12"
            fill="currentColor"
        >
            {escape(label)}
        </text>
        '''

    return f'''
    <g class="rbgraph-edge">

        <line
            x1="{start_x}"
            y1="{source_y}"
            x2="{end_x}"
            y2="{target_y}"
            stroke="#94a3b8"
            stroke-width="2"
            marker-end="url(#arrow)"
        />

        {label_svg}

    </g>
    '''


def _svg_definitions() -> str:
    return '''
    <defs>

        <marker
            id="arrow"
            markerWidth="10"
            markerHeight="10"
            refX="9"
            refY="3"
            orient="auto"
            markerUnits="strokeWidth"
        >
            <path
                d="M0,0 L0,6 L9,3 z"
                fill="#94a3b8"
            />
        </marker>

    </defs>
    '''


def _svg_background(
    width: int,
    height: int,
) -> str:

    return f'''
    <rect
        width="{width}"
        height="{height}"
        fill="#ffffff"
    />
    '''


def _empty_svg() -> str:
    return '''
    <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 900 500"
        width="900"
        height="500"
    >
        <rect
            width="900"
            height="500"
            fill="#ffffff"
        />

        <text
            x="450"
            y="250"
            text-anchor="middle"
            font-family="Arial, sans-serif"
            font-size="18"
            fill="#64748b"
        >
            No diagram nodes available
        </text>
    </svg>
    '''
```
