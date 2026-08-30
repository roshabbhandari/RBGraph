# Data Model

RBGraph represents a diagram with a name, diagram type, nodes, and edges.

Each node has:

- a stable identifier
- a display label
- a technology or visual category
- optional x and y coordinates

Each edge stores a source node, target node, optional label, and highlight state.

Supported diagram types are `architecture`, `workflow`, `sequence`, `data_flow`, and `lifecycle`.

Pydantic validation keeps the API and core engine aligned on the same shape.
