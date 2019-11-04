from .. import actions


_epilog = """
All the arguments following the two dashes (`--`) are passed to the script to
run. If you need to pass flags to the script, put them after `--` so they don't
get picked up by the `run` command.
"""

name = "run"

options = {"usage": "Run a project-defined script", "epilog": _epilog}


def configure(parser):
    parser.add_argument(
        "--no-build",
        help="assume extensions are up-to-date and do not rebuild",
        dest="builds_ext",
        action="store_false",
    )
    parser.add_argument("name")
    parser.add_argument("args", metavar="arg", nargs="*")


def run(options):
    actions.sync_dependencies()
    if options.builds_ext:
        actions.build_clib()
        actions.builds_ext()
    actions.build_py()
    actions.install_project()
    actions.run_script()
