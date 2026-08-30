from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from backend.database import delete_diagram, get_saved_diagram, init_db, list_diagrams, save_diagram
from backend.lifespan import app_lifespan
from core.commands import apply_command
from core.models import Diagram, DiagramType
from core.parser import parse_description
from core.renderer import render_svg
from core.validator import validate_diagram, validate_svg


ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"

app = FastAPI(
    title="RBGraph",
    description="Plain-English technical diagram generator",
    version="1.0.0",
    lifespan=app_lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/assets", StaticFiles(directory=FRONTEND_DIR), name="assets")


class GenerateRequest(BaseModel):
    description: str = Field(min_length=1, max_length=5000)
    name: str = Field(default="Untitled Diagram", min_length=1, max_length=120)
    diagram_type: DiagramType = DiagramType.ARCHITECTURE


class CommandRequest(BaseModel):
    diagram: Diagram
    command: str = Field(min_length=1, max_length=500)


@app.get("/")
def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health")
def health() -> dict:
    return {"status": "healthy", "service": "RBGraph"}


@app.post("/api/diagrams/generate")
def generate_diagram(request: GenerateRequest) -> dict:
    try:
        diagram = parse_description(request.description, request.name, request.diagram_type)
        errors = validate_diagram(diagram)
        if errors:
            raise HTTPException(status_code=422, detail=errors)
        svg = render_svg(diagram)
        svg_errors = validate_svg(svg)
        if svg_errors:
            raise HTTPException(status_code=422, detail=svg_errors)
        return {"success": True, "diagram": diagram.model_dump(mode="json"), "svg": svg}
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/diagrams/command")
def command_diagram(request: CommandRequest) -> dict:
    try:
        diagram, message = apply_command(request.diagram, request.command)
        errors = validate_diagram(diagram)
        if errors:
            raise HTTPException(status_code=422, detail=errors)
        svg = render_svg(diagram)
        svg_errors = validate_svg(svg)
        if svg_errors:
            raise HTTPException(status_code=422, detail=svg_errors)
        return {
            "success": True,
            "message": message,
            "diagram": diagram.model_dump(mode="json"),
            "svg": svg,
        }
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/validate")
def validate_route(diagram: Diagram) -> dict:
    errors = validate_diagram(diagram)
    return {"valid": not errors, "errors": errors}


@app.post("/api/diagrams")
def save_diagram_route(diagram: Diagram) -> dict:
    errors = validate_diagram(diagram)
    if errors:
        raise HTTPException(status_code=422, detail=errors)
    diagram_id = save_diagram(diagram)
    return {"success": True, "id": diagram_id}


@app.get("/api/diagrams")
def history(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> dict:
    try:
        return {"items": list_diagrams(limit=limit, offset=offset)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.get("/api/diagrams/{diagram_id}")
def load_diagram(diagram_id: int) -> dict:
    diagram = get_saved_diagram(diagram_id)
    if diagram is None:
        raise HTTPException(status_code=404, detail="Diagram not found.")
    svg = render_svg(diagram)
    return {"success": True, "diagram": diagram.model_dump(mode="json"), "svg": svg}


@app.delete("/api/diagrams/{diagram_id}")
def remove_diagram(diagram_id: int) -> dict:
    if not delete_diagram(diagram_id):
        raise HTTPException(status_code=404, detail="Diagram not found.")
    return {"success": True}
