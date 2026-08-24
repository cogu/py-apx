"""
APX node writer module
"""
# pylint: disable=consider-using-with
from io import StringIO
from typing import TextIO, Any
import apx.base as apx_base
import apx.model as apx_model
from apx.parser.node import NodeParser

TYPE_CODE_TO_CHAR: dict[apx_base.TypeCode, str] = {
    apx_base.TypeCode.UINT8: 'C',
    apx_base.TypeCode.UINT16: 'S',
    apx_base.TypeCode.UINT32: 'L',
    apx_base.TypeCode.UINT64: 'Q',
    apx_base.TypeCode.INT8: 'c',
    apx_base.TypeCode.INT16: 's',
    apx_base.TypeCode.INT32: 'l',
    apx_base.TypeCode.INT64: 'q',
    apx_base.TypeCode.CHAR: 'a',
    apx_base.TypeCode.CHAR8: 'A',
    apx_base.TypeCode.CHAR16: 'u',
    apx_base.TypeCode.CHAR32: 'U',
    apx_base.TypeCode.BOOL: 'b',
    apx_base.TypeCode.BYTE: 'B',
}


class Writer:
    """
    APX node writer class
    """

    def __init__(self, version: str = "APX/1.3") -> None:
        self.file_path: str | None = None
        self.fh: TextIO | None = None
        self.line_number: int = 0
        self.version: str = version
        self.major_version: int = 1
        self.minor_version: int = 3
        self.node: apx_model.Node | None = None
        self._set_version(version)

    def _str_open(self) -> None:
        self.fh = StringIO()
        self.line_number = 1

    def _open(self, file_path: str) -> None:
        self.fh = open(file_path, 'w', encoding='utf-8', newline='\n')
        self.file_path = file_path
        self.line_number = 1

    def _close(self) -> None:
        if self.fh is not None:
            self.fh.close()
            self.fh = None

    def _add_line(self, text: str) -> None:
        assert self.fh is not None
        if self.line_number > 1:
            self.fh.write('\n')
        self.line_number += 1
        self.fh.write(text)

    def _prepare_node(self, node: apx_model.Node | apx_base.Node) -> apx_model.Node:
        if isinstance(node, apx_base.Node):
            parser = NodeParser()
            model_node = parser.from_base_node(node)
            return model_node
        elif isinstance(node, apx_model.Node):
            if not node.is_finalized:
                result = node.finalize()
                if result != apx_base.NO_ERROR:
                    raise ValueError(f"Failed to finalize model node '{node.name}': {result.name}")
            return node
        else:
            raise TypeError(f"Expected apx.model.Node or apx.base.Node, got {type(node).__name__}")

    def _set_version(self, version: str | tuple[int, int] | None) -> None:
        if version is None:
            version = self.version
        if isinstance(version, tuple):
            self.major_version, self.minor_version = version
        elif isinstance(version, str):
            v_str = version
            if v_str.startswith("APX/"):
                v_str = v_str[4:]
            parts = v_str.split(".")
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                self.major_version = int(parts[0])
                self.minor_version = int(parts[1])
            else:
                raise ValueError(f"Invalid APX version string: '{version}'")
        else:
            raise ValueError(f"Invalid APX version type: {type(version)}")

        if self.major_version != 1 or self.minor_version not in (2, 3):
            raise ValueError(f"Unsupported APX version: {self.major_version}.{self.minor_version}")

    def write_str(self, node: apx_model.Node | apx_base.Node, version: str | None = None) -> str:
        """
        Serializes the APX node to string.
        """
        self._set_version(version)
        model_node = self._prepare_node(node)
        self.node = model_node
        self._str_open()
        self._write_apx_node(model_node)
        assert self.fh is not None
        return self.fh.getvalue()

    def write_file(self, node: apx_model.Node | apx_base.Node, file_path: str, version: str | None = None) -> None:
        """
        Serializes the APX node to file.
        """
        self._set_version(version)
        model_node = self._prepare_node(node)
        self.node = model_node
        self._open(file_path)
        try:
            self._write_apx_node(model_node)
        finally:
            self._close()

    def write_header_str(self, node: apx_model.Node | apx_base.Node, version: str | None = None) -> str:
        """
        Serializes the APX node header to string.
        """
        self._set_version(version)
        model_node = self._prepare_node(node)
        self.node = model_node
        self._str_open()
        self._write_header(model_node)
        assert self.fh is not None
        return self.fh.getvalue()

    def write_body_str(self, node: apx_model.Node | apx_base.Node, version: str | None = None) -> str:
        """
        Serializes the APX node body to string (skipping header lines).
        """
        self._set_version(version)
        model_node = self._prepare_node(node)
        self.node = model_node
        self._str_open()
        self._write_body(model_node)
        assert self.fh is not None
        return self.fh.getvalue()

    def _write_apx_node(self, node: apx_model.Node) -> None:
        self._write_header(node)
        self._write_body(node)

    def _write_header(self, node: apx_model.Node) -> None:
        self._add_line(f"APX/{self.major_version}.{self.minor_version}")
        self._add_line(f'N"{node.name}"')

    def _write_body(self, node: apx_model.Node) -> None:
        for data_type in node.data_types:
            self._write_data_type(data_type)
        for port in node.provide_ports:
            self._write_provide_port(port)
        for port in node.require_ports:
            self._write_require_port(port)

    def _write_data_type(self, data_type: apx_model.DataType) -> None:
        sig_str = self._write_data_signature(data_type.dsg)
        line = f'T"{data_type.name}"{sig_str}'
        if data_type.has_attributes and data_type.attributes is not None:
            attr_str = self._write_type_attributes(data_type.attributes)
            if attr_str:
                line += f':{attr_str}'
        self._add_line(line)

    def _write_provide_port(self, port: apx_model.ProvidePort) -> None:
        sig_str = self._write_data_signature(port.dsg)
        line = f'P"{port.name}"{sig_str}'
        if port.has_attributes and port.attributes is not None:
            attr_str = self._write_port_attributes(port.attributes)
            if attr_str:
                line += f':{attr_str}'
        self._add_line(line)

    def _write_require_port(self, port: apx_model.RequirePort) -> None:
        sig_str = self._write_data_signature(port.dsg)
        line = f'R"{port.name}"{sig_str}'
        if port.has_attributes and port.attributes is not None:
            attr_str = self._write_port_attributes(port.attributes)
            if attr_str:
                line += f':{attr_str}'
        self._add_line(line)

    def _write_data_signature(self, dsg: apx_model.DataSignature) -> str:
        if dsg.element is None:
            return ""
        return self._write_data_element(dsg.element)

    def _write_data_element(self, elem: apx_model.DataElement) -> str:
        res = ""
        if elem.type_code == apx_base.TypeCode.RECORD:
            assert elem.elements is not None
            parts = [f'"{child.name}"{self._write_data_element(child)}' for child in elem.elements]
            res = "{" + "".join(parts) + "}"
        elif elem.type_code in (apx_base.TypeCode.TYPE_REF_PTR,
                                apx_base.TypeCode.TYPE_REF_NAME,
                                apx_base.TypeCode.TYPE_REF_ID):
            res = self._format_type_reference(elem)
        else:
            type_char = TYPE_CODE_TO_CHAR.get(elem.type_code)
            if type_char is None:
                raise ValueError(f"Unknown or unsupported type code: {elem.type_code}")
            res = type_char

        if elem.has_limits:
            res += f"({elem.lower_limit},{elem.upper_limit})"

        if elem.is_dynamic_array:
            res += f"[{elem.array_len}*]"
        elif elem.is_array:
            res += f"[{elem.array_len}]"

        return res

    def _format_type_reference(self, elem: apx_model.DataElement) -> str:
        if elem.type_code == apx_base.TypeCode.TYPE_REF_PTR:
            data_type = elem.typeref
            assert isinstance(data_type, apx_model.DataType)
            if self.minor_version == 2:
                index = self._get_data_type_index(data_type)
                return f"T[{index}]"
            else:
                return f'T["{data_type.name}"]'
        elif elem.type_code == apx_base.TypeCode.TYPE_REF_NAME:
            name = elem.typeref
            assert isinstance(name, str)
            if self.minor_version == 2:
                index = self._find_data_type_index_by_name(name)
                return f"T[{index}]"
            else:
                return f'T["{name}"]'
        elif elem.type_code == apx_base.TypeCode.TYPE_REF_ID:
            idx = elem.typeref
            assert isinstance(idx, int)
            if self.minor_version == 3 and self.node is not None and idx < len(self.node.data_types):
                return f'T["{self.node.data_types[idx].name}"]'
            else:
                return f"T[{idx}]"
        else:
            raise ValueError(f"Invalid type reference type code: {elem.type_code}")

    def _get_data_type_index(self, data_type: apx_model.DataType) -> int:
        if self.node is not None:
            try:
                return self.node.data_types.index(data_type)
            except ValueError:
                pass
        if data_type.type_id != apx_base.INVALID_ID:
            return data_type.type_id
        raise ValueError(f"DataType '{data_type.name}' not found in node data types")

    def _find_data_type_index_by_name(self, name: str) -> int:
        if self.node is not None:
            for idx, dt in enumerate(self.node.data_types):
                if dt.name == name:
                    return idx
        raise ValueError(f"DataType with name '{name}' not found in node data types")

    def _write_port_attributes(self, attr: apx_model.PortAttributes) -> str:
        parts: list[str] = []
        if attr.has_init_value:
            parts.append(self._format_init_value(attr.init_value))
        if attr.is_parameter:
            parts.append("P")
        if attr.is_queued:
            parts.append(f"Q[{attr.queue_length}]")
        return ", ".join(parts)

    def _format_init_value(self, value: Any) -> str:
        return "=" + self._format_init_value_element(value)

    def _format_init_value_element(self, value: Any) -> str:
        if isinstance(value, bool):
            return "1" if value else "0"
        elif isinstance(value, int):
            return str(value)
        elif isinstance(value, str):
            return f'"{value}"'
        elif isinstance(value, list):
            items = [self._format_init_value_element(elem) for elem in value]
            return "{" + ", ".join(items) + "}"
        elif isinstance(value, dict):
            items = [self._format_init_value_element(elem) for elem in value.values()]
            return "{" + ", ".join(items) + "}"
        else:
            raise ValueError(f"Unsupported init value type: {type(value)}")

    def _write_type_attributes(self, attr: apx_model.TypeAttributes) -> str:
        parts: list[str] = []
        for comp in attr.computations:
            if isinstance(comp, apx_model.ValueTable):
                parts.append(self._format_value_table(comp))
            elif isinstance(comp, apx_model.RationalScaling):
                parts.append(self._format_rational_scaling(comp))
            else:
                raise NotImplementedError(f"Unsupported computation type: {type(comp).__name__}")
        return ", ".join(parts)

    def _format_value_table(self, comp: apx_model.ValueTable) -> str:
        if comp.lower_limit is None or comp.lower_limit == 0:
            vt_items = ", ".join(f'"{v}"' for v in comp.values)
            return f"VT({vt_items})"
        elif len(comp.values) > 1 and comp.upper_limit == comp.lower_limit + len(comp.values) - 1:
            vt_items = ", ".join(f'"{v}"' for v in comp.values)
            return f"VT({comp.lower_limit}, {vt_items})"
        elif len(comp.values) == 1 and comp.lower_limit == comp.upper_limit:
            return f'VT({comp.lower_limit}, "{comp.values[0]}")'
        elif comp.lower_limit is not None and comp.upper_limit is not None:
            vt_items = ", ".join(f'"{v}"' for v in comp.values)
            return f"VT({comp.lower_limit}, {comp.upper_limit}, {vt_items})"
        else:
            vt_items = ", ".join(f'"{v}"' for v in comp.values)
            return f"VT({vt_items})"

    def _format_rational_scaling(self, comp: apx_model.RationalScaling) -> str:
        unit_str = f'"{comp.unit}"' if comp.unit is not None else '""'
        offset_val = int(comp.offset) if comp.offset.is_integer() else comp.offset
        return (
            f"RS({comp.lower_limit}, {comp.upper_limit}, {offset_val}, "
            f"{comp.numerator}, {comp.denominator}, {unit_str})"
        )
