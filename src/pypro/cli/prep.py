from .. import actions

name = "prep"

options = {"usage": "Prepare the venv for project to run"}


def configure(parser):
    pass


def run(options):
    actions.sync_dependencies()
