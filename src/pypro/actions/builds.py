import json
import os
import pathlib
import subprocess
import sys
import typing

from pypro.projects import Build, Project


_API_CODE = """
import json

try:
    input = raw_input
except NameError:
    pass

data = json.loads(input())

mod, _, fpath = data["spec"].split(":", 1)
kwargs = data["kwargs"]

obj = import_module(mod)
if fpath:
    for name in fpath.split("."):
        obj = getattr(obj, name)

try:
    result = {"r": obj(**kwargs)}
except Exception as e:
    result = {"e": str(e)}

print(json.dumps(result))
"""


def _call_api(python: os.PathLike, spec: str, kw: dict) -> typing.Any:
    inp = json.dumps({"spec": spec, "kwargs": kw}).encode(sys.stdin.encoding)

    p = subprocess.Popen(
        [str(python), "-c", _API_CODE],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    out, _ = p.communicate(inp)
    p.wait()

    result = json.loads(out.decode(sys.stdout.encoding))
    try:
        r = result["r"]
    except KeyError:
        raise RuntimeError(result.get("e"))
    return r


SETUPTOOLS_DEVAPI_PY = (
    pathlib.Path(__file__)
    .joinpath("..", "..", "..", "setuptools_devapi.py")
    .resolve()
)


def build_py(
    project: Project, build: Build
) -> typing.List[typing.Tuple[str, pathlib.Path]]:
    # HACK: Inject setuptools_devapi into the build environment. In the end
    # we should standardize this and make that module into a build-requires.
    src = SETUPTOOLS_DEVAPI_PY
    build.env.site_packages.joinpath(src.name).write_text(src.read_text())

    # TODO: Make these configurable.
    spec = "setuptools_devapi:collect_pure_for_dev"
    kwargs = {"config_settings": None}
    result = _call_api(build.env.python, spec, kwargs)
    return [
        (row[0], pathlib.Path(project.root, row[1]).resolve())
        for row in result
    ]
