import csv
import functools
import os
import sys

import setuptools

from setuptools import build_meta
from setuptools.command.build_py import build_py


class _CollectPureCommand(build_py):
    def run(self):
        rows = [
            (
                path,
                os.path.join(self.get_package_dir(pkg), os.path.basename(path))
            )
            for pkg, _, path in self.find_all_modules()
        ] + [
            (
                os.path.join(src_dir, filename),
                os.path.join(self.get_package_dir(package), filename),
            )
            for package, src_dir, _, filenames in self.data_files
            for filename in filenames
        ]

        # _build_directory is set in `collect_pure_for_dev`.
        output = os.path.join(self._build_directory, "PURE")
        with open(output, "w") as f:
            # Same options as RECORD in wheels.
            writer = csv.writer(
                f, delimiter=",", quotechar='"', lineterminator="\n"
            )
            writer.writerows(rows)


def collect_pure_for_dev(build_directory, config_settings=None):
    """Collect Python files for a develop install.

    This should generate a file at ``{build_directory}/PURE`` that holds a
    list of Python files this project would install. The format is similar to
    ``RECORD`` in a wheel, but each line has two elements:

    * The path where the file would be installed to, relative to the base
      location (similar to RECORD's first element).
    * The path where the file is located, relative to the project root.

    The hook MAY NOT modify any files except the aforementioned ``.PURE`` file.
    """
    global_options = []
    if config_settings and "--global-option" in config_settings:
        global_options = config_settings["--global-option"]

    class CollectPureCommand(_CollectPureCommand):
        _build_directory = build_directory

    setuptools_setup = setuptools.setup

    @functools.wraps(setuptools_setup)
    def _patched_setup(**kwargs):
        commands = kwargs.pop("cmdclass", {})
        commands["build_py"] = CollectPureCommand
        return setuptools_setup(cmdclass=commands, **kwargs)

    setuptools.setup = _patched_setup
    sys.argv = sys.argv[:1] + ["build_py"] + global_options
    build_meta._BACKEND.run_setup()  # HACK.


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
