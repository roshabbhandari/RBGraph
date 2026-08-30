import json
import sys

from core.models import DiagramType
from core.parser import parse_description
from core.renderer import render_svg
from core.validator import validate_diagram, validate_svg


def main() -> int:
    description = " ".join(sys.argv[1:]).strip()
    if not description:
        print("Usage: python -m core <description>")
        return 1

    diagram = parse_description(description, "RBGraph CLI", DiagramType.ARCHITECTURE)
    diagram_errors = validate_diagram(diagram)
    if diagram_errors:
        print(json.dumps({"errors": diagram_errors}, indent=2))
        return 2

    svg = render_svg(diagram)
    svg_errors = validate_svg(svg)
    if svg_errors:
        print(json.dumps({"errors": svg_errors}, indent=2))
        return 3

    print(json.dumps({"diagram": diagram.model_dump(mode="json"), "svg": svg}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
