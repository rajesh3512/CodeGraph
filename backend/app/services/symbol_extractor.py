from pathlib import Path

from tree_sitter import Language, Parser
import tree_sitter_python


PYTHON_LANGUAGE = Language(tree_sitter_python.language())
parser = Parser(PYTHON_LANGUAGE)


def get_node_text(source_code: bytes, node) -> str:
    return source_code[node.start_byte:node.end_byte].decode(
        "utf-8",
        errors="replace",
    )


def extract_symbols(file_path: str) -> dict:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    source_code = path.read_bytes()
    tree = parser.parse(source_code)
    root = tree.root_node

    imports = []
    functions = []
    classes = []

    for node in root.children:

        # import requests
        if node.type == "import_statement":
            imports.append({
                "type": "import",
                "name": get_node_text(source_code, node),
                "line": node.start_point[0] + 1,
            })

        # from requests import Session
        elif node.type == "import_from_statement":
            imports.append({
                "type": "from_import",
                "name": get_node_text(source_code, node),
                "line": node.start_point[0] + 1,
            })

        # def function(...)
        elif node.type == "function_definition":
            name_node = node.child_by_field_name("name")

            if name_node:
                functions.append({
                    "name": get_node_text(source_code, name_node),
                    "line": node.start_point[0] + 1,
                })

        # class Example(...)
        elif node.type == "class_definition":
            name_node = node.child_by_field_name("name")

            methods = []

            if name_node:
                body = node.child_by_field_name("body")

                if body:
                    for child in body.children:
                        if child.type == "function_definition":
                            method_name = child.child_by_field_name("name")

                            if method_name:
                                methods.append({
                                    "name": get_node_text(
                                        source_code,
                                        method_name,
                                    ),
                                    "line": child.start_point[0] + 1,
                                })

                classes.append({
                    "name": get_node_text(source_code, name_node),
                    "line": node.start_point[0] + 1,
                    "methods": methods,
                })

    return {
        "file": str(path),
        "language": "python",
        "imports": imports,
        "functions": functions,
        "classes": classes,
    }