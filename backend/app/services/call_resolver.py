from pathlib import Path
from app.services.symbol_extractor import extract_symbols


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


def build_symbol_index(repository_root: str) -> dict[str, list[dict]]:
    root = Path(repository_root)
    index: dict[str, list[dict]] = {}

    for path in root.rglob("*.py"):
        if ".git" in path.parts or ".venv" in path.parts:
            continue

        relative_path = path.relative_to(root).as_posix()
        symbols = extract_symbols(str(path))

        for function in symbols["functions"]:
            index.setdefault(function["name"], []).append({
                "type": "function",
                "name": function["name"],
                "file": relative_path,
                "line": function["line"],
            })

        for class_data in symbols["classes"]:
            class_name = class_data["name"]

            index.setdefault(class_name, []).append({
                "type": "class",
                "name": class_name,
                "file": relative_path,
                "line": class_data["line"],
            })

            for method in class_data["methods"]:
                index.setdefault(method["name"], []).append({
                    "type": "method",
                    "name": method["name"],
                    "class": class_name,
                    "file": relative_path,
                    "line": method["line"],
                })

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


    # Resolve explicitly imported names before global name-based matching.
    if "." not in call_name and call_name in bindings:
        qualified_name = bindings[call_name]
        module_name, _, symbol_name = qualified_name.rpartition(".")
        target_file = modules.get(module_name)

        # Do not fall back to unrelated symbols if the import cannot resolve.
        if not target_file:
            return []

        return [
            candidate
            for candidate in symbol_index.get(symbol_name, [])
            if candidate["file"] == target_file
            and candidate["type"] in ("function", "method")
        ]

    # Resolve module-qualified calls only when the prefix is imported.
    if "." in call_name:
        prefix, _, suffix = call_name.partition(".")
        imported_module = bindings.get(prefix)

        if not imported_module:
            # Unknown receivers and unsupported attribute chains stay unresolved.
            return []

        module_name = None
        symbol_name = None

        # Handle `import services.users` followed by
        # `services.users.get_user()`.
        if call_name.startswith(imported_module + "."):
            module_name = imported_module
            symbol_name = call_name[len(imported_module) + 1:]

        # Handle `import alpha as a` followed by `a.process()`.
        elif suffix and "." not in suffix:
            module_name = imported_module
            symbol_name = suffix

        # Resolve only direct function calls in the imported module.
        if (
            module_name
            and symbol_name
            and "." not in symbol_name
        ):
            target_file = modules.get(module_name)

            if not target_file:
                return []

            return [
                candidate
                for candidate in symbol_index.get(symbol_name, [])
                if candidate["file"] == target_file
                and candidate["type"] == "function"
            ]

        return []


    # Preserve name-based resolution for simple, unqualified calls
    # that do not have an explicit import binding.
    return [
        candidate
        for candidate in symbol_index.get(call_name, [])
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
