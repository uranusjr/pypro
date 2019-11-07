from pypro.actions import projects, venvs

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
    project, error = projects.find()
    if project is None:
        return error

    if options.add:
        return venvs.add(project, options.add)
    if options.remove:
        return venvs.remove(project, options.remove)
    if options.venv:
        return venvs.activate(project, options.venv)

    # No options provided: List available venvs.
    return venvs.show_all(project)
