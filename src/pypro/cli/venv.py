name = "venv"

options = {"usage": "Manage venvs for this project"}


def configure(parser):
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument("venv", nargs="?", help="activate venv")
    action_group.add_argument(
        "--add", help="create new venv with given base interpreter"
    )
    action_group.add_argument("--remove", help="remove the venv")


def run(options):
    print(options)
