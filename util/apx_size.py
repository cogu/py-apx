#!/usr/bin/env python3
import argparse
from pathlib import Path
import sys

# Ensure local src is on python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import apx.base as apx_base
import apx.model as apx_model
from apx.parser import NodeParser
import apx.vm.base as apx_vm_base
from apx.vm.compiler import Compiler
import apx.vm.program as apx_vm_program


def get_port_data_size(port: apx_model.Port, program_type: apx_vm_base.ProgramType) -> int:
    compiler = Compiler()
    if port.effective_element is None:
        raise ValueError(f"Port '{port.name}' has no effective element")
    rc, elem_size = compiler.compile_data_element(program_type, port.effective_element)
    if rc != apx_base.NO_ERROR:
        raise ValueError(f"Error calculating size for port '{port.name}': {rc.name}")
    if port.queue_len > 0:
        queue_variant = apx_vm_program.calc_data_variant(port.queue_len)
        queue_size_bytes = apx_vm_program.get_size_by_variant(queue_variant)
        return queue_size_bytes + elem_size * port.queue_len
    return elem_size


def calculate_node_sizes(node: apx_model.Node) -> tuple[int, int]:
    in_data_size = sum(get_port_data_size(port, apx_vm_base.ProgramType.UNPACK) for port in node.require_ports)
    out_data_size = sum(get_port_data_size(port, apx_vm_base.ProgramType.PACK) for port in node.provide_ports)
    return in_data_size, out_data_size


def main() -> None:
    arg_parser = argparse.ArgumentParser(description="Calculate and print serialized data size of an APX node.")
    arg_parser.add_argument(
        'input_file',
        nargs='?',
        default='-',
        help="Path to input file (.apx) or '-' for stdin (default: '-')"
    )
    args = arg_parser.parse_args()

    if args.input_file == '-':
        if sys.stdin.isatty():
            arg_parser.print_help()
            sys.exit(1)
        text = sys.stdin.read()
    else:
        text = Path(args.input_file).read_text(encoding='utf-8')

    parser = NodeParser()
    node = parser.loads(text)

    in_size, out_size = calculate_node_sizes(node)
    print(f"in:\t{in_size:d}\tout:\t{out_size:d}")


if __name__ == "__main__":
    main()