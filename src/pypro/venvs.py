import dataclasses
import pathlib

from .utils import find_in_paths


@dataclasses.dataclass()
class VirtualEnvironmentInvalid(Exception):
    root: pathlib.Path


@dataclasses.dataclass()
class VirtualEnvironment:
    root: pathlib.Path

    def exists(self) -> bool:
        return self.root.is_dir()

    @property
    def name(self) -> str:
        return self.root.name

    @property
    def python(self) -> pathlib.Path:
        python = find_in_paths(
            "python",
            prefixes=[
                self.root.joinpath("bin"),
                self.root.joinpath("Scripts"),
            ],
        )
        if python is None:
            raise VirtualEnvironmentInvalid(self.root)
        return python

    @property
    def site_packages(self) -> pathlib.Path:
        patterns = [
            "lib/python*.*/site-packages",  # POSIX.
            "Lib/site-packages",  # Windows.
        ]
        for pattern in patterns:
            for path in self.root.glob(pattern):
                if path.is_dir():
                    return path
        raise VirtualEnvironmentInvalid(self.root)
