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


def extract_calls(file_path: str) -> dict:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    source_code = path.read_bytes()

    tree = parser.parse(source_code)
    root = tree.root_node

    calls = []

    def walk(
        node,
        current_class=None,
        current_function=None,
    ):
        # Track classes
        if node.type == "class_definition":
            name_node = node.child_by_field_name("name")

            if name_node:
                current_class = get_node_text(
                    source_code,
                    name_node,
                )

        # Track functions / methods
        if node.type == "function_definition":
            name_node = node.child_by_field_name("name")

            if name_node:
                current_function = get_node_text(
                    source_code,
                    name_node,
                )

        # Track function calls
        if node.type == "call":
            function_node = node.child_by_field_name(
                "function"
            )

            if function_node:
                calls.append(
                    {
                        "name": get_node_text(
                            source_code,
                            function_node,
                        ),
                        "line": node.start_point[0] + 1,
                        "class": current_class,
                        "scope": current_function,
                    }
                )

        for child in node.children:
            walk(
                child,
                current_class,
                current_function,
            )

    walk(root)

    return {
        "file": str(path),
        "language": "python",
        "calls": calls,
    }