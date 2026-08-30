from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_generate_endpoint_returns_svg():
    response = client.post(
        "/api/diagrams/generate",
        json={
            "description": "User connects to API and API uses PostgreSQL",
            "name": "API Demo",
            "diagram_type": "architecture",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["diagram"]["name"] == "API Demo"
    assert body["svg"].startswith("<svg")


def test_command_endpoint_updates_diagram():
    generated = client.post(
        "/api/diagrams/generate",
        json={
            "description": "User connects to API",
            "name": "Command Demo",
            "diagram_type": "architecture",
        },
    ).json()["diagram"]

    response = client.post(
        "/api/diagrams/command",
        json={"diagram": generated, "command": "add Redis to API"},
    )
    assert response.status_code == 200
    labels = {node["label"] for node in response.json()["diagram"]["nodes"]}
    assert "Redis" in labels
