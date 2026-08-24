"""
Collection of user-defined exceptions
"""


class ParseError(RuntimeError):
    """
    Raised by APX parser when parsing or validation fails
    """

    def __init__(self, message: str, line_number: int | None = None) -> None:
        self.line_number = line_number
        if line_number is not None:
            super().__init__(f"Line {line_number}: {message}")
        else:
            super().__init__(message)


class DuplicateElement(ValueError):
    """
    Element with this name already exists in current context
    """


class DataTypeAlreadyExists(DuplicateElement):
    """
    Exception raised when a data type already exists in the node.
    """


class PortAlreadyExists(DuplicateElement):
    """
    Exception raised when a port already exists in the node.
    """


class VersionError(ValueError):
    """
    Invalid or unsupported APX version
    """


class ValueTypeError(ValueError):
    """
    Exception raised when an invalid value type is encountered.
    """


class ValueRangeError(ValueError):
    """
    Exception raised when a value falls outside the valid range.
    """


class InvalidReferenceError(ValueError):
    """
    Reference is invalid
    """
