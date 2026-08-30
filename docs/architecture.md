# RBGraph Architecture

RBGraph is split into a browser frontend, a FastAPI application layer, a core diagram engine, and a SQLite persistence layer.

```text
Browser
  |
  v
FastAPI
  |
  +--> Parser ------> Diagram Model
  |
  +--> Commands ----> Diagram Model
  |
  +--> Validator
  |
  +--> Renderer ----> SVG
  |
  +--> SQLite
```

The diagram model is the contract between text parsing, chat edits, validation, rendering, persistence, and browser export.

The browser handles interaction, theme state, zoom, rasterization, clipboard operations, and standalone HTML creation.
