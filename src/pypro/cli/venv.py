import os
import sys
import typing
import warnings

from pypro.projects import Project, runtimes

from ._errors import VENV_NOT_FOUND


name = "venv"

options = {"usage": "Manage venvs for this project"}


def configure(parser):
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument("venv", nargs="?", help="activate venv")
    action_group.add_argument(
        "--add", help="create new venv with given base interpreter"
    )
    action_group.add_argument("--remove", help="remove the venv")


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


def run(options):
    project = Project.discover()

    if options.add:
        python = options.add
        try:
            runtime = project.create_runtime(python, prompt=project.name)
        except runtimes.InterpreterNotFound:
            message = "Error: {!r} is not a valid Python interpreter"
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
        return

    if options.remove:
        with warnings.catch_warnings(record=True) as recorder:
            warnings.simplefilter("always", runtimes.FailedToRemove)

            runtime = _find_runtime_match(project, options.venv)
            if not runtime:
                return VENV_NOT_FOUND

            project.remove_runtime(runtime)
            for w in recorder:
                env_dir, e = w.args
                env_dir = env_dir.relative_to(project.root)
                message = "Warning: Failed to remove {}\n{}".format(env_dir, e)
                print(message, file=sys.stderr)
        return

    if options.venv:
        runtime = _find_runtime_match(project, options.venv)
        if not runtime:
            return VENV_NOT_FOUND
        try:
            project.activate_runtime(runtime)
        except Exception as e:
            print("Error: Failed to activate {!r}\n{}".format(runtime.name, e))
        else:
            print("Switched to {!r}".format(runtime.name))
        return

    # No options provided: List available venvs.
    print("  Quintuplet")
    print("=" * 45)

    active_runtime = project.get_active_runtime()
    for runtime in project.iter_runtimes():
        line = "{} {}".format(
            "*" if runtime == active_runtime else " ", runtime.name
        )
        print(line)
