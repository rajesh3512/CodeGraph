
from fastapi.testclient import TestClient

from app import main


def test_file_routes_reject_paths_outside_repository(
    tmp_path, monkeypatch
):
    repository = tmp_path / "repository"
    repository.mkdir()

    outside_file = tmp_path / "outside.py"
    outside_file.write_text(
        "def secret():\n    return True\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(main, "REPOSITORY_ROOT", repository)
    client = TestClient(main.app)

    routes = [
        "/repositories/parse",
        "/repositories/symbols",
        "/repositories/imports",
        "/repositories/calls",
    ]

    for route in routes:
        response = client.get(
            route,
            params={"file": "../outside.py"},
        )

        assert response.status_code == 400, (
            route,
            response.status_code,
            response.text,
        )
        assert "within the repository" in response.text
