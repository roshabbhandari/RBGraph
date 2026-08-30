# Development

Use Python 3.11 or newer for the backend.

Install dependencies with:

```bash
pip install -r requirements.txt
```

Run the API with:

```bash
python -m uvicorn backend.main:app --reload
```

Run tests with:

```bash
pytest
```

The frontend is served by FastAPI from the `frontend` directory. The core package is kept independent from browser concerns so parser, commands, renderer, and validation can be tested directly.
