name = "clean"

options = {"usage": "Remove all built artifacts and reset all venvs"}


def configure(parser):
    parser.add_argument("--no-venv", help="do not recreate venvs")


def run(options):
    print(options)
