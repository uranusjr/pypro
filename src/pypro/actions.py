def clean():
    """Clean built artifacts and venvs.
    """
    print("clean")


def create_venv():
    """(Re-)create a clean slate venv.
    """
    print("create venv")


def sync_dependencies():
    """Ready the venv to receive the project.
    """
    print("sync dependencies")


def build_py():
    """Collect Python files in the project.
    """
    print("build py")


def build_clib():
    """Build accompanying libraries (not extension modules) in the project.
    """
    print("build clib")


def build_ext():
    """Build extensions in the project.
    """
    print("build ext")


def install_project():
    """Install project files into the venv for execution.

    This should produce a result similar to bdist_wheel + install the wheel,
    but without actually producing the wheel. Note that this assumes the
    project is built.
    """
    print("install project")


def run_script():
    """Run a script defined in the project (inside the venv).
    """
    print("run script")
