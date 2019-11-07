__all__ = [
    "PyUnavailable",
    "create_venv",
    "format_venv_name",
    "looks_like_path",
    "resolve_python",
]

import os
import pathlib
import re
import subprocess
import sys
import typing

from pypro import _virtenv


def _is_executable(path: pathlib.Path) -> bool:
    return path.is_file() and os.access(str(path), os.X_OK)


def _find_in_env_path(cmd: str) -> typing.Optional[pathlib.Path]:
    exts = [s for s in os.environ.get("PATHEXT", "").split(os.pathsep) if s]
    for prefix in os.environ.get("PATH", "").split(os.pathsep):
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


class PyUnavailable(Exception):
    pass


def _get_command_output(*args, **kwargs) -> str:
    out = subprocess.check_output(*args, **kwargs)
    out = out.decode(sys.stdout.encoding)
    out = out.strip()
    return out


_PY_VER_RE = re.compile(r"^(?P<major>\d+)(:?\.(?P<minor>\d+))?")


def _find_python_with_py(python: str) -> typing.Optional[pathlib.Path]:
    py = _find_in_env_path("py")
    if not py:
        raise PyUnavailable()
    code = "import sys; print(sys.executable)"
    out = _get_command_output([str(py), "-{}".format(python), "-c", code])
    if not out:
        return None
    return pathlib.Path(out)


def looks_like_path(v: typing.Union[pathlib.Path, str]) -> bool:
    if isinstance(v, pathlib.Path):
        return True
    if os.sep in v:
        return True
    if os.altsep and os.altsep in v:
        return True
    return False


def resolve_python(python: str) -> typing.Optional[pathlib.Path]:
    match = _PY_VER_RE.match(python)
    if match:
        return _find_python_with_py(python)
    if looks_like_path(python):
        return pathlib.Path(python)
    return _find_in_env_path(python)


_VENV_NAME_CODE = """
from __future__ import print_function
import hashlib
import sys
import platform
exe = sys.executable.encode(sys.getfilesystemencoding(), "ignore")
print("{0}-{1[0]}.{1[1]}-{2.system}-{2.machine}-{3}".format(
    platform.python_implementation(),
    sys.version_info,
    platform.uname(),
    hashlib.sha256(exe).hexdigest()[:8],
).lower())
"""


def format_venv_name(python: os.PathLike) -> str:
    """Build a unique identifier for the interpreter to place the venv.

    This is done by asking the interpreter to format a string containing:

    * Python inplementation.
    * Python version (major.minor).
    * Plarform name.
    * Processor type.
    * A 8-char hash of the interpreter path for disambiguation.

    These parts are lowercased and joined by `-` (dash).

    Example: `cpython-3.7-darwin-x86_64-3d3725a6`.
    """
    return _get_command_output([str(python), "-c", _VENV_NAME_CODE])


def create_venv(python, env_dir, prompt):
    _virtenv.create(
        python=python, env_dir=env_dir, system=False, prompt=prompt, bare=False
    )
