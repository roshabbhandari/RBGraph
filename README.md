# RBGraph

RBGraph is a local-first technical diagram builder. Describe a software system in plain English, generate a structured diagram, then edit it through short chat commands and export the result.

## What it supports

- Architecture diagrams
- Workflow diagrams
- Sequence diagrams
- Data-flow diagrams
- Lifecycle diagrams
- Plain-English generation
- Chat editing with commands such as `add Redis`, `move auth left`, and `highlight rollback path`
- Technology-aware visual categories for common services
- Dark and light themes with a remembered preference
- SVG, PNG, JPEG, WebP, and standalone HTML export
- 1×, 2×, and 4× raster exports
- 4× PNG clipboard copy
- SQLite history
- Diagram and SVG validation
- GitHub Actions test automation

## Local setup

```text
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn backend.main:app --reload
```

Open `http://127.0.0.1:8000`.

## Example prompt

```text
A user connects to React frontend and React connects to FastAPI. FastAPI uses Redis and PostgreSQL. GitHub Actions deploys to AWS Lambda.
```

## Chat commands

```text
add Redis
add OpenAI to API
remove PostgreSQL
move authentication left
move API down
highlight rollback path
clear highlight
```

## Testing

```text
pytest
```

## Project structure

```text
backend/
  database.py
  main.py
core/
  __init__.py
  commands.py
  models.py
  parser.py
  renderer.py
  validator.py
frontend/
  app.js
  index.html
  style.css
tests/
  test_basic.py
.github/
  workflows/
    ci.yml
```

## Export design

The browser generates raster exports from the SVG source at the selected scale, with 4× available for crisp output. Standalone HTML export embeds the SVG and viewer styles directly so the file can be opened without RBGraph or a server. PNG clipboard copy uses the browser Clipboard API when the current browser context permits image clipboard writes.

## License

MIT
