name = "new"

options = {"usage": "Create a new project"}


def configure(parser):
    parser.add_argument(
        "--python",
        help="Python interpreter to use for this project",
        required=True,
    )
    parser.add_argument(
        "--vcs",
        help="Initialize for given version control system",
        choices=["", "git", "hg"],
        action="store",
        nargs="*",
        default=["git"],
    )


def run(options):
    print(options)
