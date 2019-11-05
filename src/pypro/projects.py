import dataclasses
import pathlib


class ProjectNotFound(Exception):
    pass


def _is_project_root(path):
    # TODO: We might need to check the content to make sure it's valid?
    # This would even be REQUIRED if pyproject.toml implements workspace mode.
    return path.joinpath("pyproject.toml").is_file()


@dataclasses.dataclass()
class Project:
    root: pathlib.Path

    @classmethod
    def discover(cls, start=None):
        if not start:
            start = pathlib.Path()
        else:
            start = pathlib.Path(start)
        for path in start.resolve().joinpath("pyproject.toml").parents:
            if _is_project_root(path):
                return cls(root=path)
        raise ProjectNotFound()

    @property
    def build_dir(self):
        # TODO: Make this configurable?
        path = self.root.joinpath("build")
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def name(self):
        # TODO: Make this configurable.
        return self.root.name
