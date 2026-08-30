# Getting Started

RBGraph turns a plain-language description of a software system into a structured technical diagram.

## Run locally

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn backend.main:app --reload
```

Open `http://127.0.0.1:8000`.

## First diagram

Enter a description such as:

```text
A user connects to React. React calls FastAPI. FastAPI uses Redis and PostgreSQL.
```

Choose a diagram type and generate the result.

## Chat editing

Use commands such as:

```text
add OpenAI to FastAPI
move Redis right
remove PostgreSQL
highlight rollback path
clear highlight
```

## Save and export

Saved diagrams are stored in SQLite. Export options are available in the browser for SVG, PNG, JPEG, WebP, and standalone HTML.
