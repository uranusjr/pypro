import dataclasses
import pathlib


@dataclasses.dataclass()
class VirtualEnvironment:
    root: pathlib.Path

    def exists(self) -> bool:
        return self.root.is_dir()

    @property
    def name(self) -> str:
        return self.root.name
