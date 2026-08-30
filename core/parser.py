import re
from typing import Dict, Iterable, List, Tuple

from core.models import Diagram, DiagramType, Edge, Node


ALIASES = {
    "postgresql": ("PostgreSQL", "database"),
    "postgres": ("PostgreSQL", "database"),
    "mysql": ("MySQL", "database"),
    "sqlite": ("SQLite", "database"),
    "mongodb": ("MongoDB", "database"),
    "redis": ("Redis", "cache"),
    "github actions": ("GitHub Actions", "automation"),
    "github": ("GitHub", "service"),
    "openai": ("OpenAI", "ai"),
    "aws lambda": ("AWS Lambda", "serverless"),
    "lambda": ("AWS Lambda", "serverless"),
    "aws": ("AWS", "cloud"),
    "fastapi": ("FastAPI", "backend"),
    "react": ("React", "frontend"),
    "next.js": ("Next.js", "frontend"),
    "nextjs": ("Next.js", "frontend"),
    "frontend": ("Frontend", "frontend"),
    "backend": ("Backend", "backend"),
    "api": ("API", "backend"),
    "authentication": ("Authentication", "security"),
    "auth": ("Authentication", "security"),
    "user": ("User", "user"),
    "client": ("Client", "user"),
    "browser": ("Browser", "user"),
    "queue": ("Queue", "service"),
    "worker": ("Worker", "service"),
}

RELATION_PATTERNS = [
    (re.compile(r"(.+?)\s+(?:connects?|talks?|communicates?)\s+(?:to|with)\s+(.+)", re.I), "connects"),
    (re.compile(r"(.+?)\s+(?:sends?|passes?|pushes?)\s+(?:data\s+|code\s+)?(?:to|into)\s+(.+)", re.I), "sends"),
    (re.compile(r"(.+?)\s+(?:stores?|persists?)\s+(?:data\s+)?(?:in|into|to)\s+(.+)", re.I), "stores"),
    (re.compile(r"(.+?)\s+(?:loads?|reads?|retrieves?)\s+(?:data\s+)?(?:from)\s+(.+)", re.I), "reads"),
    (re.compile(r"(.+?)\s+(?:calls?|requests?)\s+(.+)", re.I), "calls"),
    (re.compile(r"(.+?)\s+(?:uses?|reads?\s+from|reads?|writes?\s+to|depends?\s+on|checks?)\s+(.+)", re.I), "uses"),
    (re.compile(r"(.+?)\s+(?:deploys?|ships?)\s+(?:to|into)\s+(.+)", re.I), "deploys"),
    (re.compile(r"(.+?)\s+(?:triggers?|starts?|runs?)\s+(.+)", re.I), "triggers"),
    (re.compile(r"(.+?)\s+(?:transitions?|moves?)\s+(?:to|into)\s+(.+)", re.I), "transitions"),
]


def clean_name(value: str) -> str:
    value = re.sub(r"^\s*(?:a|an|the|then)\s+", "", value.strip(), flags=re.I)
    value = re.sub(r"\s+", " ", value)
    return value.strip(" ,.;:")


def normalize_id(label: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", label.lower()).strip("-")
    return value or "node"


def detect_category(label: str) -> str:
    value = label.lower()
    for keyword in sorted(ALIASES, key=len, reverse=True):
        if keyword in value:
            return ALIASES[keyword][1]
    return "default"


def canonical_label(label: str) -> str:
    cleaned = clean_name(label)
    value = cleaned.lower()
    for keyword in sorted(ALIASES, key=len, reverse=True):
        if value == keyword or keyword in value:
            return ALIASES[keyword][0]
    return cleaned


def _split_clauses(description: str) -> List[str]:
    text = description.replace("→", "->").replace("➜", "->").replace("⇒", "->")
    text = re.sub(r"\s*->\s*", " -> ", text)
    text = re.sub(r"\s+and\s+(?=[^.;\n]+?\s+(?:connects?|talks?|communicates?|sends?|passes?|pushes?|stores?|persists?|loads?|reads?|retrieves?|calls?|requests?|uses?|writes?|depends?|checks?|deploys?|ships?|triggers?|starts?|runs?|transitions?|moves?)\b)", " | ", text, flags=re.I)
    text = re.sub(r"[.;\n]+", " | ", text)
    return [clean_name(item) for item in text.split("|") if clean_name(item)]


def _add_node(nodes: Dict[str, Node], label: str) -> str:
    label = canonical_label(label)
    node_id = normalize_id(label)
    if node_id not in nodes:
        nodes[node_id] = Node(id=node_id, label=label, category=detect_category(label))
    return node_id


def _parse_relation(clause: str) -> Tuple[str, List[str], str] | None:
    for pattern, label in RELATION_PATTERNS:
        match = pattern.fullmatch(clause)
        if match:
            targets = [clean_name(item) for item in re.split(r"\s+and\s+|\s*,\s*", match.group(2), flags=re.I) if clean_name(item)]
            return clean_name(match.group(1)), targets, label

    return None


def _extract_mentions(text: str) -> Iterable[str]:
    lower = text.lower()
    found: List[Tuple[int, int, str]] = []

    for keyword in sorted(ALIASES, key=len, reverse=True):
        pattern = re.compile(r"(?<!\w)" + re.escape(keyword) + r"(?!\w)", re.I)
        for match in pattern.finditer(lower):
            if any(start < match.end() and match.start() < end for start, end, _ in found):
                continue
            found.append((match.start(), match.end(), ALIASES[keyword][0]))

    for _, _, label in sorted(found):
        yield label


def parse_description(
    description: str,
    name: str = "Untitled Diagram",
    diagram_type: DiagramType = DiagramType.ARCHITECTURE,
) -> Diagram:
    description = clean_name(description)
    if not description:
        raise ValueError("Description cannot be empty.")

    nodes: Dict[str, Node] = {}
    edges: List[Edge] = []

    for clause in _split_clauses(description):
        if "->" in clause:
            pieces = [clean_name(piece) for piece in clause.split("->") if clean_name(piece)]
            if len(pieces) >= 2:
                previous_id = _add_node(nodes, pieces[0])
                for piece in pieces[1:]:
                    target_id = _add_node(nodes, piece)
                    if previous_id != target_id:
                        edges.append(Edge(source=previous_id, target=target_id, label="flows"))
                    previous_id = target_id
                continue

        relation = _parse_relation(clause)
        if relation:
            source, targets, relation_label = relation
            source_id = _add_node(nodes, source)
            for target in targets:
                target_id = _add_node(nodes, target)
                if source_id != target_id:
                    edges.append(Edge(source=source_id, target=target_id, label=relation_label))
            continue

        for mention in _extract_mentions(clause):
            _add_node(nodes, mention)

    if not nodes:
        chunks = [clean_name(part) for part in re.split(r"\s+to\s+|\s+and\s+|,", description, flags=re.I) if clean_name(part)]
        for chunk in chunks[:8]:
            if len(chunk.split()) <= 5:
                _add_node(nodes, chunk)

    node_ids = list(nodes)
    if not edges and len(node_ids) > 1:
        edges.extend(Edge(source=source_id, target=target_id, label="flows") for source_id, target_id in zip(node_ids, node_ids[1:]))

    seen = set()
    unique_edges = []
    for edge in edges:
        key = (edge.source, edge.target, edge.label)
        if key not in seen:
            seen.add(key)
            unique_edges.append(edge)

    return Diagram(
        name=clean_name(name) or "Untitled Diagram",
        diagram_type=diagram_type,
        nodes=list(nodes.values()),
        edges=unique_edges,
    )
