from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from app.services.repository import clone_repository
from app.services.file_discovery import discover_source_files
from app.services.parser import parse_python_file
from app.services.symbol_extractor import extract_symbols
from app.services.graph_builder import build_repository_graph
from app.services.import_resolver import (
    build_python_module_map,
    resolve_import,
)
from app.services.call_extractor import extract_calls
from pathlib import Path

REPOSITORY_ROOT = (
    Path(__file__).resolve().parent.parent
    / "workspace"
    / "repository"
)

app = FastAPI(
    title="CodeGraph API",
    description="Repository intelligence and software engineering platform",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RepositoryRequest(BaseModel):
    repository_url: str


@app.get("/")
def root():
    return {
        "name": "CodeGraph",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


@app.post("/repositories/clone")
def clone_repository_endpoint(request: RepositoryRequest):
    try:
        result = clone_repository(
            request.repository_url,
            str(REPOSITORY_ROOT),
        )

        return result

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@app.get("/repositories/files")
def get_repository_files():
    try:
        files = discover_source_files(
            str(REPOSITORY_ROOT)
        )

        return {
            "repository": str(REPOSITORY_ROOT),
            "file_count": len(files),
            "files": files,
        }

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@app.get("/repositories/parse")
def parse_repository_file(
    file: str = "src/requests/models.py"
):
    try:
        result = parse_python_file(
            str(REPOSITORY_ROOT / file)
        )

        return result

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@app.get("/repositories/symbols")
def get_repository_symbols(
    file: str = "src/requests/models.py"
):
    try:
        result = extract_symbols(
            str(REPOSITORY_ROOT / file)
        )

        return result

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@app.get("/repositories/graph")
def get_repository_graph():
    try:
        graph = build_repository_graph(
            str(REPOSITORY_ROOT)
        )

        return {
            "repository": "workspace/repository",
            "node_count": graph.node_count(),
            "edge_count": graph.edge_count(),
            "graph": graph.to_dict(),
        }

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@app.get("/repositories/imports")
def get_repository_imports(
    file: str = "src/requests/models.py"
):
    try:
        repository_root = str(REPOSITORY_ROOT)

        module_map = build_python_module_map(
            repository_root
        )

        symbols = extract_symbols(
            f"{repository_root}/{file}"
        )

        imports = []

        for import_data in symbols["imports"]:
            resolved_file = resolve_import(
                import_data["name"],
                file,
                module_map,
            )

            imports.append({
                "statement": import_data["name"],
                "line": import_data["line"],
                "resolved_file": resolved_file,
                "internal": resolved_file is not None,
            })

        return {
            "file": file,
            "imports": imports,
        }

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

@app.get("/repositories/calls")
def get_repository_calls(
    file: str = "src/requests/models.py"
):
    try:
        repository_root = str(REPOSITORY_ROOT)
        result = extract_calls(
            f"{repository_root}/{file}"
        )

        return result

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )