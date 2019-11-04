from . import clean, new, prep, ready, run, venv


_subcommands = [clean, new, prep, ready, run, venv]


def build_subcommands(subparsers):
    for command in _subcommands:
        parser = subparsers.add_parser(command.name, **command.options)
        command.configure(parser)
        parser.set_defaults(func=command.run)
