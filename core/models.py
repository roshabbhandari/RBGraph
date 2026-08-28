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
    id: str = Field(min_length=1, max_length=80)
    label: str = Field(min_length=1, max_length=120)
    category: str = "default"
    x: Optional[float] = None
    y: Optional[float] = None


class Edge(BaseModel):
    source: str = Field(min_length=1, max_length=80)
    target: str = Field(min_length=1, max_length=80)
    label: Optional[str] = Field(default=None, max_length=120)
    highlighted: bool = False


class Diagram(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    diagram_type: DiagramType
    nodes: List[Node] = Field(default_factory=list)
    edges: List[Edge] = Field(default_factory=list)
