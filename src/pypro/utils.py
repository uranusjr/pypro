__all__ = ["find_in_paths"]

import os
import pathlib
import typing


_EnvPaths = typing.List[os.PathLike]


def _get_env_paths() -> _EnvPaths:
    v = os.environ.get("PATH", "")
    if not v:
        return []
    return typing.cast(_EnvPaths, v.split(os.pathsep))


def _is_executable(path: pathlib.Path) -> bool:
    return path.is_file() and os.access(str(path), os.X_OK)


def find_in_paths(
    cmd: str, *, prefixes: typing.Optional[_EnvPaths] = None
) -> typing.Optional[pathlib.Path]:
    if prefixes is None:
        prefixes = _get_env_paths()

    exts = [s for s in os.environ.get("PATHEXT", "").split(os.pathsep) if s]

    for prefix in prefixes:
        if not prefix:
            continue
        path = pathlib.Path(prefix, cmd)
        if _is_executable(path):
            return path
        for ext in exts:
            p = path.with_suffix(ext)
            if _is_executable(p):
                return p
    return None
