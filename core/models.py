
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class DiagramType(str, Enum):
    ARCHITECTURE = "architecture"
    WORKFLOW = "workflow"
    SEQUENCE = "sequence"
    DATA_FLOW = "data_flow"
    LIFECYCLE = "lifecycle"


class Node(BaseModel):
    id: str = Field(min_length=1)
    label: str = Field(min_length=1)
    category: str = "default"
    x: Optional[float] = None
    y: Optional[float] = None


class Edge(BaseModel):
    source: str = Field(min_length=1)
    target: str = Field(min_length=1)
    label: Optional[str] = None


class Diagram(BaseModel):
    name: str = Field(min_length=1)
    diagram_type: DiagramType
    nodes: List[Node] = []
    edges: List[Edge] = []
