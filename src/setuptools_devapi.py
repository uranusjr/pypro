from setuptools import build_meta


def get_paths_triggering_build(config_settings=None):
    """Get a list of paths that should trigger a rebuild if changed.

    This should return a list of strings specifying items on the filesystem,
    relative to the project root. Frontend is expected to call ``build_dev`` if
    any of them is modified later than the last build.
    """


def collect_pure_for_dev(build_directory, config_settings=None):
    """Collect Python files for a develop install.

    This should generate a file at ``{build_directory}/{name}-{version}.PURE``
    that holds a list of Python files this project would install. The format is
    similar to ``RECORD`` in a wheel, but each line has two elements:

    * The path where the file would be installed to, relative to the base
      location (similar to RECORD's first element).
    * The path where the file is located, relative to the project root.

    The hook MAY NOT modify any files except the aforementioned ``.PURE`` file.
    """
    # Basically should use logic in `build_py` but collect paths instead.


def build_for_dev(build_directory, config_settings=None):
    """Build files for a develop install.

    This should generate a file at ``{build_directory}/{name}-{version}.BUILT``
    that holds a list of files it generates for this project to install. The
    format is similar to that of ``build_pure``, but the second element should
    be relative to ``build_directory`` instead.

    The hook is expected to write files into ``build_directory``, and refer
    them in the ``.BUILT`` file. The frontend is expected to pass a consistent
    value of ``build_directory`` across each ``build_dev`` call. The hook
    should expect the directory already containing previously-built files, and
    may choose to reuse them if it determines they do not need to be rebuilt.
    """
    # Basically should do `setup.py build_clib build_ext`.


# Reuse PEP 517 for now. We can always change our mind and decide they need to
# be separate hooks.
get_requires_for_dev = build_meta.get_requires_for_build_wheel
prepare_metadata_for_dev = build_meta.prepare_metadata_for_build_wheel
