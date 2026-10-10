from pathlib import Path


def build_python_module_map(repository_root: str) -> dict[str, str]:
    root = Path(repository_root)
    module_map = {}

    for path in root.rglob("*.py"):
        if ".git" in path.parts:
            continue

        relative = path.relative_to(root)
        parts = list(relative.parts)

        # Handle src/ layout
        if parts and parts[0] == "src":
            parts = parts[1:]

        if not parts:
            continue

        if parts[-1] == "__init__.py":
            parts = parts[:-1]
        else:
            parts[-1] = Path(parts[-1]).stem

        if not parts:
            continue

        module_name = ".".join(parts)
        module_map[module_name] = relative.as_posix()

    return module_map


def resolve_import(
    import_statement: str,
    current_file: str,
    module_map: dict[str, str],
) -> str | None:

    statement = import_statement.strip()
    current_path = Path(current_file)

    # ---------------------------------------------------------
    # Relative import
    #
    # Example:
    # from .utils import something
    # ---------------------------------------------------------

    if statement.startswith("from ."):

        module_part = statement.split(" import ", 1)[0]

        # Remove "from "
        relative_module = module_part[5:]

        # Number of dots
        dot_count = len(relative_module) - len(
            relative_module.lstrip(".")
        )

        module_name = relative_module[dot_count:]

        # Find the current module's package
        current_parts = list(current_path.parts)

        if current_parts and current_parts[-1].endswith(".py"):
            current_parts[-1] = Path(
                current_parts[-1]
            ).stem

        # Remove file itself
        current_package = current_parts[:-1]

        # Remove src from package path
        if current_package and current_package[0] == "src":
            current_package = current_package[1:]

        # Move upward according to relative import level
        if dot_count > 1:
            levels_up = dot_count - 1

            if levels_up <= len(current_package):
                current_package = current_package[
                    :-levels_up
                ]
            else:
                current_package = []

        # Handle:
        # from . import _types as _t
        # from . import auth
        if not module_name:
            imported_part = statement.split(" import ", 1)[1]

            # There may be multiple imports:
            # from . import foo, bar
            imported_names = imported_part.split(",")

            for imported_name in imported_names:
                imported_name = imported_name.strip()

                # Remove alias:
                # _types as _t -> _types
                imported_name = imported_name.split(
                    " as ",
                    1
                )[0].strip()

                candidate_parts = (
                    current_package + [imported_name]
                )

                candidate = ".".join(candidate_parts)

                if candidate in module_map:
                    return module_map[candidate]

            # If the imported name isn't a module,
            # fall back to the package itself.
            package = ".".join(current_package)

            if package in module_map:
                return module_map[package]

            return None


        # Normal relative import:
        # from .auth import HTTPBasicAuth
        if module_name:
            candidate_parts = (
                current_package + module_name.split(".")
            )

            candidate = ".".join(candidate_parts)

            if candidate in module_map:
                return module_map[candidate]

            return None

    # ---------------------------------------------------------
    # Absolute import
    # ---------------------------------------------------------

    if statement.startswith("from "):

        parts = statement.split()

        if len(parts) >= 2:
            module_name = parts[1]

            if module_name in module_map:
                return module_map[module_name]

            components = module_name.split(".")

            for index in range(
                len(components) - 1,
                0,
                -1,
            ):
                candidate = ".".join(
                    components[:index]
                )

                if candidate in module_map:
                    return module_map[candidate]

    # ---------------------------------------------------------
    # import requests.utils
    # ---------------------------------------------------------

    elif statement.startswith("import "):

        module_name = (
            statement[7:]
            .split(",")[0]
            .strip()
        )

        if module_name in module_map:
            return module_map[module_name]

    return None