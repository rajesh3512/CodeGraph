from pathlib import Path

from app.models.graph import GraphEdge, GraphNode
from app.services.file_discovery import discover_source_files
from app.services.graph import CodeGraph
from app.services.symbol_extractor import extract_symbols
from app.services.import_resolver import (
    build_python_module_map,
    resolve_import,
)
from app.services.import_resolver import (
    build_python_module_map,
    resolve_import,
)
from app.services.call_extractor import extract_calls
from app.services.call_resolver import (
    build_symbol_index,
    resolve_call_name,
)
from app.services.call_resolver import (
    build_import_bindings,
    build_symbol_index,
    resolve_call_name,
)


def build_repository_graph(repository_root: str) -> CodeGraph:
    root = Path(repository_root)

    if not root.exists():
        raise FileNotFoundError(
            f"Repository not found: {repository_root}"
        )

    graph = CodeGraph()

    # Repository node
    repository_id = "repository:root"

    graph.add_node(
        GraphNode(
            id=repository_id,
            type="repository",
            name=root.name,
        )
    )

    files = discover_source_files(repository_root)
    module_map = build_python_module_map(repository_root)
    symbol_index = build_symbol_index(repository_root)


    for file_data in files:
        relative_path = Path(file_data["path"])
        full_path = root / relative_path

        file_id = f"file:{relative_path.as_posix()}"

        # File node
        graph.add_node(
            GraphNode(
                id=file_id,
                type="file",
                name=relative_path.name,
                file=relative_path.as_posix(),
            )
        )

        # Repository -> File
        graph.add_edge(
            GraphEdge(
                source=repository_id,
                target=file_id,
                type="contains",
            )
        )

        # Currently our symbol extractor supports Python.
        if relative_path.suffix.lower() != ".py":
            continue

        symbols = extract_symbols(str(full_path))

        # Imports
        # Imports
        for import_data in symbols["imports"]:
            resolved_file = resolve_import(
                import_data["name"],
                relative_path.as_posix(),
                module_map,
            )

            if resolved_file:
                target_file_id = f"file:{resolved_file}"

                graph.add_edge(
                    GraphEdge(
                        source=file_id,
                        target=target_file_id,
                        type="imports",
                        metadata={
                            "line": import_data["line"],
                            "statement": import_data["name"],
                        },
                    )
                )

            else:
                import_id = (
                    f"external:{relative_path.as_posix()}:"
                    f"{import_data['line']}"
                )

                graph.add_node(
                    GraphNode(
                        id=import_id,
                        type="external_module",
                        name=import_data["name"],
                        file=relative_path.as_posix(),
                        line=import_data["line"],
                    )
                )

                graph.add_edge(
                    GraphEdge(
                        source=file_id,
                        target=import_id,
                        type="imports",
                    )
                )

        # Functions
        for function in symbols["functions"]:
            function_id = (
                f"function:{relative_path.as_posix()}:"
                f"{function['name']}"
            )

            graph.add_node(
                GraphNode(
                    id=function_id,
                    type="function",
                    name=function["name"],
                    file=relative_path.as_posix(),
                    line=function["line"],
                )
            )

            graph.add_edge(
                GraphEdge(
                    source=file_id,
                    target=function_id,
                    type="defines",
                )
            )

        # Classes and methods
        for class_data in symbols["classes"]:
            class_id = (
                f"class:{relative_path.as_posix()}:"
                f"{class_data['name']}"
            )

            graph.add_node(
                GraphNode(
                    id=class_id,
                    type="class",
                    name=class_data["name"],
                    file=relative_path.as_posix(),
                    line=class_data["line"],
                )
            )

            graph.add_edge(
                GraphEdge(
                    source=file_id,
                    target=class_id,
                    type="defines",
                )
            )

            for method in class_data["methods"]:
                method_id = (
                    f"method:{relative_path.as_posix()}:"
                    f"{class_data['name']}:"
                    f"{method['name']}"
                )

                graph.add_node(
                    GraphNode(
                        id=method_id,
                        type="method",
                        name=method["name"],
                        file=relative_path.as_posix(),
                        line=method["line"],
                    )
                )

                graph.add_edge(
                    GraphEdge(
                        source=class_id,
                        target=method_id,
                        type="contains",
                    )
                )


    # Call relationships: process every Python file after all nodes exist.
    for file_data in files:
        relative_path = Path(file_data["path"])
        if relative_path.suffix.lower() != ".py":
            continue

        full_path = root / relative_path
        call_data = extract_calls(str(full_path))

        for call in call_data["calls"]:
            caller_name = call.get("scope")
            if not caller_name:
                continue

            caller_class = call.get("class")
            caller_candidates = [
                candidate
                for candidate in symbol_index.get(caller_name, [])
                if candidate["file"] == relative_path.as_posix()
                and candidate["type"] in ("function", "method")
                and candidate.get("class") == caller_class
            ]

            if not caller_candidates:
                continue

            caller = caller_candidates[0]

            if caller["type"] == "function":
                caller_id = (
                    f"function:{caller['file']}:{caller['name']}"
                )
            else:
                caller_id = (
                    f"method:{caller['file']}:"
                    f"{caller['class']}:{caller['name']}"
                )

            caller_symbols = extract_symbols(str(full_path))
            import_bindings = build_import_bindings(caller_symbols["imports"])

            targets = resolve_call_name(
                call["name"],
                symbol_index,
                current_class=caller_class,
                import_bindings=import_bindings,
                module_map=module_map,
            )
            for target in targets:
                if target["type"] == "function":
                    target_id = (
                        f"function:{target['file']}:{target['name']}"
                    )
                elif target["type"] == "method":
                    target_id = (
                        f"method:{target['file']}:"
                        f"{target['class']}:{target['name']}"
                    )
                else:
                    continue

                if not graph.graph.has_node(caller_id):
                    continue
                if not graph.graph.has_node(target_id):
                    continue

                graph.add_edge(
                    GraphEdge(
                        source=caller_id,
                        target=target_id,
                        type="calls",
                        metadata={
                            "line": call["line"],
                            "call": call["name"],
                        },
                    )
                )

    return graph
