import os
import sys
import typing

from pypro.projects import Project, runtimes

from ._errors import VENV_NOT_FOUND


def _find_runtime_match(
    project: Project, alias: str
) -> typing.Optional[runtimes.Runtime]:
    try:
        return project.find_runtime(alias)
    except runtimes.NoRuntimes as e:
        message = "Error: no matching venv for {!r}, tried: {}".format(
            alias, ", ".join(r.name for r in e.tried)
        )
        print(message, file=sys.stderr)
    except runtimes.MultipleRuntimes as e:
        message = "Error: name {!r} is ambiguous; choose from: {}".format(
            alias, ", ".join(p.name for p in e.matches)
        )
        print(message, file=sys.stderr)
    return None


def add(project: Project, python: str) -> int:
    try:
        runtime = project.create_runtime(python)
    except runtimes.RuntimeExists as e:
        message = "Error: a runtime already exists at {!r}".format(
            e.runtime.root
        )
        print(message, file=sys.stderr)
        return VENV_NOT_FOUND
    except runtimes.InterpreterNotFound as e:
        message = "Error: {!r} is not a valid interpreter".format(e.spec)
        print(message, file=sys.stderr)
        return VENV_NOT_FOUND
    except runtimes.PyUnavailable:
        if os.name == "nt":
            url = "https://docs.python.org/3/using/windows.html"
        else:
            url = "https://github.com/brettcannon/python-launcher"
        message = (
            "Error: Specifying Python with version requires the Python "
            "Launcher. More information:\n{url}"
        ).format(url=url)
        print(message, file=sys.stderr)
        return VENV_NOT_FOUND
    print("Created runtime {!r}".format(runtime.name))
    return 0


def remove(project: Project, alias: str) -> int:
    runtime = _find_runtime_match(project, alias)
    if not runtime:
        return VENV_NOT_FOUND
    try:
        project.remove_runtime(runtime)
    except Exception as e:
        env_dir = runtime.root.relative_to(project.root)
        message = "Warning: Failed to remove {}\n{}".format(env_dir, e)
        print(message, file=sys.stderr)
    return 0


def activate(project: Project, alias: str) -> int:
    runtime = _find_runtime_match(project, alias)
    if not runtime:
        return VENV_NOT_FOUND
    try:
        project.activate_runtime(runtime)
    except Exception as e:
        print("Error: Failed to activate {!r}\n{}".format(runtime.name, e))
    else:
        print("Switched to {!r}".format(runtime.name))
    return 0


def show_all(project: Project) -> int:
    print("  Quintuplet")
    print("=" * 45)

    active_runtime = project.get_active_runtime()
    for runtime in project.iter_runtimes():
        line = "{} {}".format(
            "*" if runtime == active_runtime else " ", runtime.name
        )
        print(line)

    return 0
