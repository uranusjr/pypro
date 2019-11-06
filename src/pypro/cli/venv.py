import os
import sys
import warnings

from ..actions import venvs
from ..projects import Project

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


def run(options):
    project = Project.discover()

    if options.add:
        python = options.add
        try:
            info = venvs.create(project, python, prompt=project.name)
        except venvs.InterpreterNotFound:
            message = "Error: {!r} is not a valid Python interpreter"
            print(message, file=sys.stderr)
            return VENV_NOT_FOUND
        except venvs.PyUnavailable:
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
        print("Switching to newly created {!r}".format(info.name))
        venvs.activate(project, info.name)
        return

    if options.remove:
        with warnings.catch_warnings(record=True) as recorder:
            warnings.simplefilter("always", venvs.FailedToRemoveWarning)
            venvs.remove(project, options.remove)
            for w in recorder:
                env_dir, e = w.args
                env_dir = env_dir.relative_to(project.root)
                message = "Warning: Failed to remove {}: {}".format(env_dir, e)
                print(message, file=sys.stderr)
        return

    if options.venv:
        try:
            env_name = venvs.choose_venv(project, options.venv)
        except venvs.NoVenvMatches as e:
            alias, tried = e.args
            tried = ", ".join(p.name for p in tried)
            message = "Error: no matching venv for {!r}, tried: {}".format(
                alias, tried
            )
            print(message, file=sys.stderr)
            return VENV_NOT_FOUND
        except venvs.MultipleVenvMatches as e:
            alias, matches = e.args
            matches = ", ".join(p.name for p in matches)
            message = "Error: name {!r} is ambiguous; choose from: {}".format(
                alias, matches
            )
            print(message, file=sys.stderr)
            return VENV_NOT_FOUND
        print("Switching to {!r}".format(env_name))
        venvs.activate(project, env_name)
        return

    # No options provided: List available venvs.

    active_name = venvs.get_active(project)
    venv_infos = list(venvs.iter_infos(project))
    if venv_infos:
        let_len = max(len(info.name) for info in venv_infos)
    else:
        let_len = 10

    form = "{0: <2}{1: {let_agn}{let_len}} {2: ^5} {3: ^5}"

    title = form.format(
        "", "Quintuplet", "Run", "Build", let_len=let_len, let_agn="^"
    )
    print(title)
    print("=" * (len(title) + 1))

    for info in venv_infos:
        line = form.format(
            "*" if info.name == active_name else "",
            info.name,
            "v" if info.run else "",
            "v" if info.build else "",
            let_len=let_len,
            let_agn="<",
        )
        print(line)
