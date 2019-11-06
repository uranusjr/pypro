import dataclasses
import pathlib


@dataclasses.dataclass()
class BaseProject:
    root: pathlib.Path

    @property
    def name(self):
        # TODO: Make this configurable.
        return self.root.name

    @property
    def build_dir(self):
        # TODO: Make this configurable?
        path = self.root.joinpath("build")
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def venv_root_for_build(self):
        return self.build_dir.joinpath(".venvs")
