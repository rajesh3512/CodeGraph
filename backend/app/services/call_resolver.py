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
    import_bindings: dict[str, str] | None = None,
    module_map: dict[str, str] | None = None,
) -> list[dict]:
    if call_name in BUILTIN_NAMES:
        return []

    # Resolve self.method() within the current class.
    if call_name.startswith("self."):
        if not current_class:
            return []

        method_name = call_name.split(".", 1)[1]
        return [
            candidate
            for candidate in symbol_index.get(method_name, [])
            if candidate["type"] == "method"
            and candidate.get("class") == current_class
        ]

    bindings = import_bindings or {}
    modules = module_map or {}

    # Explicit imports must resolve to their actual source module.
    if "." not in call_name and call_name in bindings:
        qualified_name = bindings[call_name]
        module_name, _, symbol_name = qualified_name.rpartition(".")
        target_file = modules.get(module_name)

        # Do not fall back to unrelated functions if the import is unresolved.
        if not target_file:
            return []

        return [
            candidate
            for candidate in symbol_index.get(symbol_name, [])
            if candidate["file"] == target_file
            and candidate["type"] in ("function", "method")
        ]

    # Preserve name-based resolution for calls without an explicit import binding.
    final_name = call_name.split(".")[-1]
    return [
        candidate
        for candidate in symbol_index.get(final_name, [])
        if candidate["type"] in ("function", "method")
    ]

def build_import_bindings(
    import_statements: list[dict],
) -> dict[str, str]:
    """Map local imported names and aliases to their source modules."""
    bindings = {}

    for import_data in import_statements:
        statement = import_data.get("name", "").strip()

        if statement.startswith("from "):
            parts = statement.split(" import ", 1)
            if len(parts) != 2:
                continue

            module_name = parts[0][5:].strip()
            imported_names = parts[1].strip().strip("()")

            for item in imported_names.split(","):
                item = item.strip()
                if not item or item == "*":
                    continue

                original_name, separator, alias = item.partition(" as ")
                original_name = original_name.strip()
                local_name = alias.strip() if separator else original_name

                bindings[local_name] = (
                    f"{module_name}.{original_name}".strip(".")
                )

        elif statement.startswith("import "):
            imported_modules = statement[7:].split(",")

            for item in imported_modules:
                item = item.strip()
                if not item:
                    continue

                module_name, separator, alias = item.partition(" as ")
                module_name = module_name.strip()
                local_name = (
                    alias.strip()
                    if separator
                    else module_name.split(".")[0]
                )
                bindings[local_name] = module_name

    return bindings
