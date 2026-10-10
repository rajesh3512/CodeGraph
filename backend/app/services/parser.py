from pathlib import Path

from tree_sitter import Language, Parser
import tree_sitter_python


PYTHON_LANGUAGE = Language(tree_sitter_python.language())
parser = Parser(PYTHON_LANGUAGE)


def parse_python_file(file_path: str) -> dict:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    source_code = path.read_bytes()

    tree = parser.parse(source_code)

    root = tree.root_node

    return {
        "file": str(path),
        "language": "python",
        "root_type": root.type,
        "has_error": root.has_error,
        "node_count": count_nodes(root),
    }


def count_nodes(node) -> int:
    count = 1

    for child in node.children:
        count += count_nodes(child)

    return count