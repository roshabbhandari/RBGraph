
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from core.models import DiagramType
from core.parser import parse_description


app = FastAPI(
    title="RBGraph",
    description="Plain-English technical diagram generator",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DiagramRequest(BaseModel):
    description: str = Field(min_length=1)
    name: str = "Untitled Diagram"
    diagram_type: DiagramType = DiagramType.ARCHITECTURE


@app.get("/")
def root():
    return {
        "name": "RBGraph",
        "version": "0.1.0",
        "status": "running",
        "message": "RBGraph API is running",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/api/diagrams/generate")
def generate_diagram(request: DiagramRequest):
    try:
        diagram = parse_description(
            description=request.description,
            name=request.name,
            diagram_type=request.diagram_type,
        )

        return {
            "success": True,
            "diagram": diagram.model_dump(),
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

