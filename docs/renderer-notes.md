# RBGraph Rendering Pipeline

RBGraph treats the diagram model as the source of truth and derives visual output from that model.

## Pipeline

1. Parse or edit the diagram structure.
2. Validate the structure and relationships.
3. Render nodes and edges into SVG.
4. Apply the active theme and layout information.
5. Export or display the resulting SVG.

Keeping SVG generation downstream of the model makes chat edits and manual edits converge on the same renderer.

## Export considerations

Raster exports should be generated from the SVG source at the requested scale. Standalone HTML export should preserve the SVG so the exported file remains independent of the development server.

Renderer changes should be checked against both a simple diagram and a diagram containing multiple relationships and labels.