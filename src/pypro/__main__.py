import argparse
import sys

from . import cli


def _no_subcommand(options):
    options.parser.print_help()
    return 1


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.set_defaults(func=_no_subcommand)
    cli.build_subcommands(parser.add_subparsers())

    options = parser.parse_args(argv)
    options.parser = parser

    retcode = options.func(options)
    if retcode:
        sys.exit(retcode)


if __name__ == "__main__":
    main()
