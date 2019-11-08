import csv
import functools
import io
import os
import sys
import tokenize
import tempfile

import setuptools

from setuptools import build_meta
from setuptools.command.build_py import build_py


# Copied from Setuptools.
def _open_setup_script(setup_script):
    if not os.path.exists(setup_script):
        return io.StringIO("from setuptools import setup; setup()")
    return getattr(tokenize, "open", open)(setup_script)


# Copied from Setuptools.
def _run_setup(self, setup_script="setup.py"):
    __file__ = setup_script
    __name__ = "__main__"
    with _open_setup_script(__file__) as f:
        code = f.read().replace(r"\r\n", r"\n")
    exec(compile(code, __file__, "exec"), locals())


# Same options as RECORD in wheels.
_CSV_KWARGS = {"delimiter": ",", "quotechar": '"', "lineterminator": "\n"}


def _write_csv(f, rows):
    f.seek(0)
    csv.writer(f, **_CSV_KWARGS).writerows(rows)


def _read_csv(f):
    f.seek(0)
    return list(csv.reader(f, **_CSV_KWARGS))


class _CollectPureCommand(build_py):
    def run(self):
        rows = [
            (
                mod_path,
                os.path.join(
                    self.get_package_dir(package), os.path.basename(mod_path)
                ),
            )
            for package, _, mod_path in self.find_all_modules()
        ] + [
            (
                os.path.join(src_dir, filename),
                os.path.join(self.get_package_dir(package), filename),
            )
            for package, src_dir, _, filenames in self.data_files
            for filename in filenames
        ]
        _write_csv(self._temp_file, rows)


def collect_pure_for_dev(config_settings=None):
    """Collect Python files for a develop install.

    Returns a list of 2-tuples representing Python files this project would
    install. Each 2-tuple is specified as:

    * The path where the file would be installed to, relative to the base
      location (similar to RECORD's first element).
    * The path where the file is located, relative to the project root.
    """
    global_options = []
    if config_settings and "--global-option" in config_settings:
        global_options = config_settings["--global-option"]

    with tempfile.TemporaryFile(mode="w+") as tf:

        class CollectPureCommand(_CollectPureCommand):
            _temp_file = tf

        setuptools_setup = setuptools.setup

        @functools.wraps(setuptools_setup)
        def _patched_setup(**kwargs):
            commands = kwargs.pop("cmdclass", {})
            commands["build_py"] = CollectPureCommand
            return setuptools_setup(cmdclass=commands, **kwargs)

        setuptools.setup = _patched_setup
        sys.argv = sys.argv[:1] + ["build_py"] + global_options
        try:
            _run_setup()
        except SystemExit as e:
            if e.args[0]:
                raise

        return _read_csv(tf)


def get_paths_triggering_build(config_settings=None):
    """Get a list of paths that should trigger a rebuild if changed.

    This should return a list of strings specifying items on the filesystem,
    relative to the project root. Frontend is expected to call
    ``build_for_dev`` if any of them is modified later than the last build.
    """


def build_for_dev(build_directory, config_settings=None):
    """Build files for a develop install.

    This should generate a file at ``{build_directory}/BUILT`` that holds a
    list of files it generates for this project to install. The format is
    similar to ``RECORD`` in a wheel, but each line has two elements:

    * The path where the file would be installed to, relative to the base
      location (similar to RECORD's first element).
    * The path where the file is located, relative to ``build_directory``.

    The hook is expected to write files into ``build_directory``, and refer
    them in ``BUILT``. The frontend is expected to pass a consistent value of
    ``build_directory`` across each ``build_for_dev`` call. The hook should
    expect the directory already containing previously-built files, and may
    choose to reuse them if it determines they do not need to be rebuilt.
    """
    # Basically should do `setup.py build_clib build_ext`.


# Reuse PEP 517 for now. We can always change our mind and decide they need to
# be separate hooks.
get_requires_for_dev = build_meta.get_requires_for_build_wheel
prepare_metadata_for_dev = build_meta.prepare_metadata_for_build_wheel
