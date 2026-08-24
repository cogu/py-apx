"""
Node parser for APX definition files
"""
from dataclasses import dataclass
from enum import Enum
import re
import apx.base as apx_base
import apx.model as apx_model
from apx.exception import ParseError
from apx.parser.base import strip_comment, split_type_declaration, split_port_declaration
from apx.parser.signature import SignatureParser
from apx.parser.attribute import AttributeParser


class FileSection(Enum):
    """
    Parser section in APX file
    """
    VERSION = 0
    NODE = 1
    TYPE = 2
    PORT = 3


@dataclass
class NodeParseState:
    """
    Internal parse state for NodeParser.
    """
    line_number: int = 0
    major_version: int = 0
    minor_version: int = 0
    accept_next: FileSection = FileSection.VERSION
    node: apx_model.Node | None = None
    data_element: apx_model.DataElement | None = None
    type_attributes: apx_model.TypeAttributes | None = None
    port_attributes: apx_model.PortAttributes | None = None


class NodeParser:
    """
    Parser for full APX node text definitions
    """

    def __init__(self) -> None:
        self.state: NodeParseState | None = None
        self.version_statement_re = re.compile(r'APX/(\d+)\.(\d+)')
        self.node_statement_re = re.compile(r'N"(\w+)"')
        self.signature_parser = SignatureParser()
        self.attribute_parser = AttributeParser()
        self.result: apx_base.Result | None = None

    def loads(self, apx_text: str) -> apx_model.Node:
        """
        Parses an APX document from text string.
        Returns a finalized Node on success, or raises ParseError on failure.
        """
        self.state = NodeParseState()
        result = apx_base.Result.NO_ERROR
        for line in apx_text.splitlines():
            self.state.line_number += 1
            result = self._parse_line(strip_comment(line))
            if result != apx_base.Result.NO_ERROR:
                self.result = result
                raise ParseError(
                    f"Error parsing line: {result.name}",
                    line_number=self.state.line_number
                )
        if self.state.node is None:
            self.result = apx_base.Result.PARSE_ERROR
            raise ParseError("No APX node found in text", line_number=self.state.line_number)
        self.result = self.state.node.finalize()
        if self.result != apx_base.Result.NO_ERROR:
            err_line = self.state.node.last_error_line or self.state.line_number
            raise ParseError(
                f"Error finalizing node '{self.state.node.name}': {self.result.name}",
                line_number=err_line
            )
        return self.state.node

    def from_base_node(self, base_node: apx_base.Node) -> apx_model.Node:
        """
        Creates and finalizes a model Node from a base (pseudo) Node.
        Returns a finalized Node on success, or raises ParseError on failure.
        """
        if not isinstance(base_node, apx_base.Node):
            raise TypeError(f"Expected apx.base.Node, got {type(base_node).__name__}")
        self.state = NodeParseState()
        self.state.node = apx_model.Node(base_node.name)

        # 1. Add Data Types
        for base_type in base_node.data_types:
            result = self._accept_type_declaration_parts(
                base_type.name,
                base_type.dsg,
                base_type.attributes
            )
            if result != apx_base.Result.NO_ERROR:
                self.result = result
                raise ParseError(
                    f"Error parsing data type '{base_type.name}' signature '{base_type.dsg}': {result.name}"
                )

        # 2. Add Require Ports
        for base_port in base_node.require_ports:
            result = self._accept_port_declaration_parts(
                'R',
                base_port.name,
                base_port.dsg,
                base_port.attributes
            )
            if result != apx_base.Result.NO_ERROR:
                self.result = result
                raise ParseError(
                    f"Error parsing require port '{base_port.name}' signature '{base_port.dsg}': {result.name}"
                )

        # 3. Add Provide Ports
        for base_port in base_node.provide_ports:
            result = self._accept_port_declaration_parts(
                'P',
                base_port.name,
                base_port.dsg,
                base_port.attributes
            )
            if result != apx_base.Result.NO_ERROR:
                self.result = result
                raise ParseError(
                    f"Error parsing provide port '{base_port.name}' signature '{base_port.dsg}': {result.name}"
                )

        # 4. Finalize
        self.result = self.state.node.finalize()
        if self.result != apx_base.Result.NO_ERROR:
            raise ParseError(
                f"Error finalizing node '{base_node.name}': {self.result.name}"
            )
        return self.state.node

    def _finalize(self) -> None:
        self.result = apx_base.Result.NO_ERROR

    def _parse_line(self, line: str) -> apx_base.Result:
        assert self.state is not None
        if self.state.accept_next == FileSection.VERSION:
            result = self._accept_version_line(line)
        elif self.state.accept_next == FileSection.NODE:
            result = self._accept_node_declaration(line)
        elif self.state.accept_next == FileSection.TYPE:
            result = self._accept_type_or_port_declaration(line)
        else:
            result = self._accept_port_declaration(line)
        return result

    def _accept_version_line(self, line: str) -> apx_base.Result:
        assert self.state is not None
        match = self.version_statement_re.match(line)
        if match is not None:
            self.state.major_version = int(match.group(1))
            self.state.minor_version = int(match.group(2))
            return self._accecpt_apx_version(self.state.major_version, self.state.minor_version)
        return apx_base.Result.PARSE_ERROR

    def _accecpt_apx_version(self, major_version: int, minor_version: int) -> apx_base.Result:
        assert self.state is not None
        if major_version == 1 and 2 <= minor_version <= 3:
            self.state.accept_next = FileSection.NODE
            return apx_base.Result.NO_ERROR
        return apx_base.Result.VERSION_ERROR

    def _accept_node_declaration(self, line: str) -> apx_base.Result:
        assert self.state is not None
        match = self.node_statement_re.match(line)
        if match is not None:
            node_name = match.group(1)
            self.state.node = apx_model.Node(node_name, self.state.line_number)
            self.state.accept_next = FileSection.TYPE
            return apx_base.Result.NO_ERROR
        return apx_base.Result.PARSE_ERROR

    def _accept_type_or_port_declaration(self, line: str) -> apx_base.Result:
        assert self.state is not None
        parts1 = split_type_declaration(line)
        if isinstance(parts1, tuple):
            return self._accept_type_declaration_parts(*parts1)
        else:
            parts2 = split_port_declaration(line)
            if isinstance(parts2, tuple):
                self.state.accept_next = FileSection.PORT
                return self._accept_port_declaration_parts(*parts2)
        return apx_base.Result.PARSE_ERROR

    def _accept_port_declaration(self, line: str) -> apx_base.Result:
        parts = split_port_declaration(line)
        if isinstance(parts, tuple):
            return self._accept_port_declaration_parts(*parts)
        return apx_base.Result.PARSE_ERROR

    def _accept_type_declaration_parts(
        self,
        name: str,
        signature_string: str,
        attribute_string: str | None
    ) -> apx_base.Result:
        assert self.state is not None and self.state.node is not None
        result = self._parse_data_signature(signature_string)
        has_attributes = False
        if result == apx_base.Result.NO_ERROR and attribute_string is not None:
            has_attributes = True
            result = self._parse_type_attributes(attribute_string)
        if result == apx_base.Result.NO_ERROR:
            data_type = apx_model.DataType(name, self.state.line_number)
            data_type.data_element = self.state.data_element
            if has_attributes:
                data_type.attributes = self.state.type_attributes
            self.state.node.append(data_type)
        return result

    def _accept_port_declaration_parts(
        self,
        port_type_string: str,
        name: str,
        signature_string: str,
        attribute_string: str | None
    ) -> apx_base.Result:
        assert self.state is not None and self.state.node is not None
        result = self._parse_data_signature(signature_string)
        has_attributes = False
        if result == apx_base.Result.NO_ERROR and attribute_string is not None:
            has_attributes = True
            result = self._parse_port_attributes(attribute_string)
        if result == apx_base.Result.NO_ERROR:
            if port_type_string == 'R':
                port: apx_model.Port = apx_model.RequirePort(name, self.state.line_number)
            elif port_type_string == 'P':
                port = apx_model.ProvidePort(name, self.state.line_number)
            else:
                return apx_base.Result.PARSE_ERROR
            port.data_element = self.state.data_element
            if has_attributes:
                port.attributes = self.state.port_attributes
            self.state.node.append(port)
        return result

    def _parse_data_signature(self, signature: str) -> apx_base.Result:
        assert self.state is not None
        result = self.signature_parser.parse_signature(signature)
        if result == apx_base.Result.NO_ERROR:
            self.state.data_element = self.signature_parser.take_data_element()
        return result

    def _parse_type_attributes(self, attribute_string: str) -> apx_base.Result:
        assert self.state is not None
        result, attributes_object = self.attribute_parser.parse_type_attributes(attribute_string)
        if result == apx_base.Result.NO_ERROR:
            self.state.type_attributes = attributes_object
        return result

    def _parse_port_attributes(self, attribute_string: str) -> apx_base.Result:
        assert self.state is not None
        result, attributes_object = self.attribute_parser.parse_port_attributes(attribute_string)
        if result == apx_base.Result.NO_ERROR:
            self.state.port_attributes = attributes_object
        return result
