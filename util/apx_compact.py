#!/usr/bin/env python3
import argparse
from pathlib import Path
import sys

# Ensure local src is on python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from apx.parser import NodeParser
from apx.writer import Writer


def main() -> None:
    arg_parser = argparse.ArgumentParser(description="Compact APX file by using index-based type references.")
    arg_parser.add_argument(
        'input_file',
        nargs='?',
        default='-',
        help="Path to input file (.apx) or '-' for stdin (default: '-')"
    )
    arg_parser.add_argument(
        '-o', '--output',
        dest='output_file',
        default=None,
        help="Output file path (default: stdout for stdin, or overwrite input file)"
    )
    args = arg_parser.parse_args()

    # 1. Read input
    if args.input_file == '-':
        if sys.stdin.isatty():
            arg_parser.print_help()
            sys.exit(1)
        text = sys.stdin.read()
    else:
        text = Path(args.input_file).read_text(encoding='utf-8')

    parser = NodeParser()
    writer = Writer(compact=True)
    node = parser.loads(text)

    # 2. Write output
    if args.output_file == '-' or (args.output_file is None and args.input_file == '-'):
        print(writer.write_str(node))
    else:
        out_path = args.output_file if args.output_file is not None else args.input_file
        writer.write_file(node, out_path)


if __name__ == '__main__':
    main()