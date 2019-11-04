from .. import actions


# This command is intentionally named like this to avoid ambiguity whether the
# "build" step would include syncing artifacts into the venv. We always do, so
# there's no doubt whether the venv is up to date.
name = "ready"

options = {"usage": "Ready the project for execution"}


def configure(parser):
    parser.add_argument(
        "--no-build",
        help="assume extensions are up-to-date and do not rebuild",
        dest="builds_ext",
        action="store_false",
    )


def run(options):
    actions.sync_dependencies()
    if options.builds_ext:
        actions.build_clib()
        actions.builds_ext()
    actions.build_py()
    actions.install_project()
