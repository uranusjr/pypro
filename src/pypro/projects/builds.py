__all__ = ["Build", "ProjectBuildManagementMixin"]

import dataclasses
import pathlib
import shutil
import typing

from pypro.venvs import VirtualEnvironment

from .runtimes import ProjectRuntimeManagementMixin
from ._envs import create_venv, get_interpreter_quintuplet


BuildEnv = VirtualEnvironment


@dataclasses.dataclass()
class Build:
    container: pathlib.Path

    @property
    def env(self) -> BuildEnv:
        return BuildEnv(self.container.joinpath("venv"))

    @property
    def root_for_build_ext(self) -> pathlib.Path:
        return self.container.joinpath("ext")


@dataclasses.dataclass()
class BuildExists(Exception):
    build: Build


class ProjectBuildManagementMixin(ProjectRuntimeManagementMixin):
    """Build management functionalities for project.

    The build directory is structured as follows::

        <project_root>/
            build/
                <quintuplet>/
                    ext/    # Build root for build tools.
                    venv/   # Build env.
                (more quintuplets)
            (other project files)
    """

    @property
    def _build_dir(self) -> pathlib.Path:
        return self.root.joinpath("build")

    def _get_build_container(self, quintuplet: str) -> pathlib.Path:
        return self._build_dir.joinpath(quintuplet)

    def get_build(self, quintuplet: str) -> typing.Optional[Build]:
        """Get of build of quintuplet.

        This ensures the build directory exists, but does not check whether it
        is actually in working condition or not.
        """
        container = self._get_build_container(quintuplet)
        if container.exists():
            return Build(container)
        return None

    def create_build(self, python: pathlib.Path) -> Build:
        """Create build environment.

        Raises `BuildExists` if the directory already exists, othereise creates
        a container directory and a venv for building.

        This function always raises an error if the build exists, even if it is
        not actually in working condition, and never attempts to fix the build.
        """
        quintuplet = get_interpreter_quintuplet(python)
        build_container = self._get_build_container(quintuplet)
        build = Build(build_container)

        if build_container.exists():
            raise BuildExists(build)
        build_container.mkdir(parents=True)

        # TODO: Make prompt configurable? Include quintuplet in prompt?
        create_venv(python=python, env_dir=build.env.root, prompt=self.name)

        return build

    def remove_build(self, build: Build):
        if build.container.exists():
            shutil.rmtree(str(build.container))
