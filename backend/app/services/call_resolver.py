from pathlib import Path


BUILTIN_NAMES = {
    "abs",
    "all",
    "any",
    "bool",
    "bytes",
    "callable",
    "chr",
    "dict",
    "dir",
    "divmod",
    "enumerate",
    "eval",
    "filter",
    "float",
    "format",
    "frozenset",
    "getattr",
    "hasattr",
    "hash",
    "help",
    "id",
    "input",
    "int",
    "isinstance",
    "issubclass",
    "iter",
    "len",
    "list",
    "map",
    "max",
    "memoryview",
    "min",
    "next",
    "object",
    "open",
    "ord",
    "pow",
    "print",
    "property",
    "range",
    "repr",
    "reversed",
    "round",
    "set",
    "setattr",
    "slice",
    "sorted",
    "str",
    "sum",
    "super",
    "tuple",
    "type",
    "vars",
    "zip",
}


def build_symbol_index(
    repository_root: str,
) -> dict[str, list[dict]]:
    root = Path(repository_root)

    index: dict[str, list[dict]] = {}

    for path in root.rglob("*.py"):
        if ".git" in path.parts:
            continue

        relative = path.relative_to(root)
        file_path = relative.as_posix()

        source = path.read_text(
            encoding="utf-8",
            errors="replace",
        )

        lines = source.splitlines()

        current_class = None

        for line_number, line in enumerate(
            lines,
            start=1,
        ):
            stripped = line.strip()

            # Detect class
            if stripped.startswith("class "):
                name = (
                    stripped[6:]
                    .split("(", 1)[0]
                    .split(":", 1)[0]
                    .strip()
                )

                current_class = name

                index.setdefault(
                    name,
                    [],
                ).append(
                    {
                        "type": "class",
                        "name": name,
                        "file": file_path,
                        "line": line_number,
                    }
                )

                continue

            # Detect function
            if stripped.startswith("def "):
                name = (
                    stripped[4:]
                    .split("(", 1)[0]
                    .strip()
                )

                # Method inside a class
                if current_class:
                    index.setdefault(
                        name,
                        [],
                    ).append(
                        {
                            "type": "method",
                            "name": name,
                            "class": current_class,
                            "file": file_path,
                            "line": line_number,
                        }
                    )

                # Top-level function
                else:
                    index.setdefault(
                        name,
                        [],
                    ).append(
                        {
                            "type": "function",
                            "name": name,
                            "file": file_path,
                            "line": line_number,
                        }
                    )

    return index


def resolve_call_name(
    call_name: str,
    symbol_index: dict[str, list[dict]],
    current_class: str | None = None,
) -> list[dict]:

    # Ignore Python built-ins
    if call_name in BUILTIN_NAMES:
        return []

    # self.method()
    if call_name.startswith("self."):
        method_name = call_name.split(
            ".",
            1,
        )[1]

        if not current_class:
            return []

        candidates = symbol_index.get(
            method_name,
            [],
        )

        return [
            candidate
            for candidate in candidates
            if candidate["type"] == "method"
            and candidate.get("class") == current_class
        ]

    # Remove object prefixes for now
    if "." in call_name:
        final_name = call_name.split(".")[-1]
    else:
        final_name = call_name

    return symbol_index.get(
        final_name,
        [],
    )