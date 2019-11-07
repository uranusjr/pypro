import os
import sys
import typing

from pypro.projects import Project, ProjectNotFound

from ._errors import PROJECT_NOT_FOUND


def find() -> typing.Tuple[typing.Optional[Project], int]:
    try:
        project = Project.discover()
    except ProjectNotFound:
        message = "Error: Project not found at {!r}".format(os.getcwd())
        print(message, file=sys.stderr)
        return None, PROJECT_NOT_FOUND

    return project, 0
