__all__ = ["BuildEnv", "ProjectBuildEnvManagementMixin"]


from pypro.venvs import VirtualEnvironment

from .base import BaseProject


BuildEnv = VirtualEnvironment


class ProjectBuildEnvManagementMixin(BaseProject):
    pass
