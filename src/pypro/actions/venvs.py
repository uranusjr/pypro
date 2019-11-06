import collections
import contextlib
import os
import pathlib
import platform
import re
import shutil
import subprocess
import sys
import warnings

from . import _virtenv


_PY_VER_RE = re.compile(r"^(?P<major>\d+)(:?\.(?P<minor>\d+))?")


def _path_like(v):
    if isinstance(v, pathlib.Path):
        return True
    if os.sep in v:
        return True
    if os.altsep and os.altsep in v:
        return True
    return False


def _is_executable(path):
    return path.is_file() and os.access(str(path), os.X_OK)


def _find_in_env_path(cmd):
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


def _get_command_output(*args, **kwargs):
    out = subprocess.check_output(*args, **kwargs)
    out = out.decode(sys.stdout.encoding)
    out = out.strip()
    return out


def _find_python_with_py(python):
    py = _find_in_env_path("py")
    if not py:
        raise PyUnavailable()
    code = "import sys; print(sys.executable)"
    out = _get_command_output([str(py), "-{}".format(python), "-c", code])
    if not out:
        return None
    return pathlib.Path(out)


def _resolve_python(python):
    match = _PY_VER_RE.match(python)
    if match:
        return _find_python_with_py(python)
    if _path_like(python):
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


def _get_venv_name(python):
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


def _get_env_dirs_for_name(project, env_name):
    return (
        project.root.joinpath(".venvs", env_name),
        project.build_dir.joinpath(".venvs", env_name),
    )


@contextlib.contextmanager
def _redirect_stdout(f):
    # HACK: Used to silence virtenv.
    sys.stdout = f
    yield
    sys.stdout = sys.__stdout__


class InterpreterNotFound(Exception):
    pass


_VenvInfo = collections.namedtuple("_VenvInfo", "name run build")


def create(project, python, *, prompt, system=False):
    """(Re-)create clean slate venvs based on given base interpreter.

    This creates *two* venvs, one for running and one for building. The runtime
    one is in a directory named `.venv` in the project root. The build-time one
    is in a `.venvs` directory in the build directory.
    """
    python = _resolve_python(python)
    if not python:
        raise InterpreterNotFound(python)
    env_name = _get_venv_name(python)
    env_dirs = _get_env_dirs_for_name(project, env_name)
    for env_dir in env_dirs:
        with open(os.devnull, "w") as f, _redirect_stdout(f):
            _virtenv.create(
                python=python,
                env_dir=env_dir,
                system=system,
                prompt=prompt,
                bare=False,
            )
    return _VenvInfo(env_name, *env_dirs)


class _VenvMatcher:
    def __init__(self, parts, h=None):
        self._parts = [p.lower() for p in parts]
        self._hash = h.lower() if h else h

    @classmethod
    def _from_5(cls, v):
        return cls(v[:4], v[4])

    @classmethod
    def _from_4(cls, v):
        return cls(v)

    @classmethod
    def _from_3(cls, v):
        return cls(v[:2] + [platform.uname().system] + v[2:])

    @classmethod
    def _from_2(cls, v):
        uname = platform.uname()
        return cls(v + [uname.system, uname.machine])

    @classmethod
    def _from_1(cls, v):
        uname = platform.uname()
        impl = platform.python_implementation()
        return cls([impl] + v + [uname.system, uname.machine])

    @classmethod
    def from_alias(cls, alias):
        if _path_like(alias):
            alias = _get_venv_name(pathlib.Path(alias))
        parts = alias.split("-")
        try:
            ctor = {
                5: cls._from_5,
                4: cls._from_4,
                3: cls._from_3,
                2: cls._from_2,
                1: cls._from_1,
            }[len(parts)]
        except KeyError:
            raise ValueError(alias)
        return ctor(parts)

    def match(self, env_dir):
        parts = env_dir.name.split("-")
        if len(parts) != 5:
            return False
        hash_ = parts.pop()
        if self._hash and self._hash != hash_:
            return False
        return self._parts == parts


class NoVenvMatches(Exception):
    pass


class MultipleVenvMatches(Exception):
    pass


def _iter_venvs(container):
    if not container.is_dir():
        return
    for entry in container.iterdir():
        if not entry.is_dir():
            continue
        yield entry


def choose_venv(project, alias):
    """Choose exactly one matching venv from an alias.

    An alias can take one of the following forms:

    * Python version (``3.7``)
    * Python implementation + version (``cpython-3.7``)
    * Python implementation + version + bitness (`cpython-3.7-x86_64`)
    * Full identifier minus the hash (`cpython-3.7-darwin-x86_64`)
    * Full identifier including the hash (`cpython-3.7-darwin-x86_64-3d3725a6`)
    * Path to a Python interpreter
    """
    container = project.root.joinpath(".venvs")
    matcher = _VenvMatcher.from_alias(alias)

    matches = [
        env_dir for env_dir in _iter_venvs(container) if matcher.match(env_dir)
    ]

    if not matches:
        raise NoVenvMatches(alias, list(_iter_venvs(container)))
    if len(matches) > 1:
        raise MultipleVenvMatches(alias, matches)
    return matches[0].name


def activate(project, env_name):
    """Set venv with given name as active.

    This simply writes the runtime venv's path to a file named `.venv`. This
    is intentionally designed to be compatibile with Pipenv because why not.

    See: https://github.com/pypa/pipenv/issues/2680
    """
    marker = project.root.joinpath(".venv")
    marker.write_text(".venvs/{}".format(env_name))


def get_active(project):
    """Get the name of the activate venv.

    This returns the name of the active venv (not the path), or None if there
    is not a recognizable active venv.
    """
    path = project.root.joinpath(".venv")

    # Normal case: .venv is a file. It should contain a relative path pointing
    # to a venv in `{root}/.venvs`.
    if path.is_file():
        content = path.read_text().strip()
        prefix, name = content.split("/", 1)
        if prefix != ".venv":
            return None
        # TODO: Check the name is a valid quintuplet.
        if not project.joinpath(".venvs", name).is_dir():
            return None
        return name

    # Compatibility case: .venv is a link to a directory in `{root}/.venvs`.
    # Use that if it's managed.
    if path.is_symlink():
        path = path.resolve()
        if not path.is_dir():
            return None
        if project.root.joinpath(".venvs") not in path.parents:
            return None
        name = path.name
        # TODO: Check the name is a valid quintuplet.
        return name

    return None


def deactivate(project):
    active = get_active(project)
    if not active:
        return None
    marker = project.root.joinpath(".venv")
    marker.unlink()
    return active


class FailedToRemoveWarning(UserWarning):
    pass


def remove(project, env_name):
    # Deactivate env if it is going to be removed.
    if get_active(project) == env_name:
        deactivate(project)

    for env_dir in _get_env_dirs_for_name(project, env_name):
        try:
            shutil.rmtree(str(env_dir))
        except Exception as e:
            warnings.warn(FailedToRemoveWarning(env_dir, str(e)))


def iter_infos(project):
    root = project.root

    runs = {p.name: p for p in _iter_venvs(root.joinpath(".venvs"))}
    builds = {p.name: p for p in _iter_venvs(root.joinpath("build", ".venvs"))}
    for k in sorted(set(runs) | set(builds)):
        yield _VenvInfo(k, runs.get(k), builds.get(k))
