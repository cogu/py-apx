![Python package](https://github.com/cogu/py-apx/actions/workflows/python-package.yml/badge.svg)

# Python APX v0.5

The official Python 3 implementation of [APX](https://cogu.github.io/apx/) (AUTOSAR Port eXchange).

APX is an open framework and protocol designed to exchange AUTOSAR signal data with non-AUTOSAR applications. It enables external applications running on POSIX, Windows, or microcontrollers to seamlessly communicate with AUTOSAR runtime environments (RTE).

**Important notes:**

1. Python APX v0.5+ uses a modernized API and is incompatible with the v0.4 API.
2. For Python APX v0.4, see the [v0.4 maintenance branch](https://github.com/cogu/py-apx/tree/maintenance/0.4).
3. Documentation is currently being updated for v0.5.

## Compatibility & Versioning with `autosar`

`py-apx` versions align directly with the [python-autosar](https://github.com/cogu/autosar) package:

| `py-apx` Version | `autosar` Version | Status | Notes |
| :--- | :--- | :--- | :--- |
| **v0.4.x** | **v0.4.x** | Maintenance | Legacy API compatibility maintained on the respective `maintenance/0.4` branches. |
| **v0.5.x** | **v0.5.x** | In Development | Modernized API redesign & architecture refactoring. |
| **v0.6.x** | **v0.6.x** | Planned | Stable modernized release with full `autosar` v0.6.x compatibility, published to PyPI. |

## Major design changes

APX v0.5 has been rewritten and modernized.

**Key features:**

* **Modular Architecture**: Decoupled subsystem design separating parsing, semantic models, data encoding, and virtual machine execution.
* **Snake-case naming**: Method and variable naming strictly follows PEP 8 standards.
* **Modern type hinting**: Full type annotations across the codebase (requires Python 3.10 or later).
* **Python Enum classes**: Enumerations replace legacy integer constants.
* **New APX version**: Support for APX IDL v1.3 with APX VM v2.1.
* **Newer AUTOSAR version support**: No longer dependent on the old AUTOSAR3 type system.
* **Linting & Code Quality**: Checked with flake8 and Pylint.
* **Comprehensive Test Suite**: Fast, modern unit tests verifying parser, model, serializer, and VM components.

## Usage

```python
import apx
from apx.parser import NodeParser

# 1. Create a new Node
node = apx.Node('Example')

# 2. Add custom Data Types
node.append(apx.DataType('BatteryVoltage_T', 'S'))
node.append(apx.DataType('Date_T', '{"Year"C"Month"C(1,13)"Day"C(1,32)}'))
node.append(apx.DataType(
    'InactiveActive_T',
    'C(0,3)',
    'VT("InactiveActive_Inactive", "InactiveActive_Active", "InactiveActive_Error", "InactiveActive_NotAvailable")'
))

# 3. Add Provide and Require Ports with Type References and Init Values
node.append(apx.ProvidePort('BatteryVoltage', 'T["BatteryVoltage_T"]', '=65535'))
node.append(apx.RequirePort('CurrentDate', 'T["Date_T"]', '={255, 13, 32}'))
node.append(apx.RequirePort('ExteriorLightsActive', 'T["InactiveActive_T"]', '=3'))

# 4. Parse base node into semantic model
parser = NodeParser()
model_node = parser.from_base_node(node)
print(f"Created node '{model_node.name}' with {len(model_node.data_types)} types, "
      f"{len(model_node.provide_ports)} provide ports, {len(model_node.require_ports)} require ports.")
```

## Requirements

* Python 3.10+
* [cfile](https://github.com/cogu/cfile) v0.4.0+


## Python Module Hierarchy

### `apx.base`

Base declarations, type codes, port types, constants, and basic AST node/port/data type representations.

### `apx.model`

Semantic data model representing parsed APX nodes, ports, data elements, computation rules, and type definitions.

### `apx.parser`

Parser subsystem for APX type signatures, port attributes, and complete APX text specifications.

### `apx.data`

Direct binary serialization and deserialization engine for packing and unpacking APX data packets.

### `apx.vm`

Virtual machine bytecode compiler and execution engine for fast data packing/unpacking programs.

### `apx.numheader`

Low-level APX message length and numeric header encoding/decoding utilities.


## Installation

Manual install required as this version is not yet available on PyPI.

### Preparation

Download a compressed source package from GitHub or clone this repo to a local directory.

### Installation steps for virtual environment

Start bash (Linux) or PowerShell (Windows).

#### Create virtual environment

```bash
python -m venv .venv
```

#### Activate virtual environment

On Windows run:

```powershell
.\.venv\Scripts\activate
```

On Linux run:

```bash
source .venv/bin/activate
```

#### Upgrade toolchain

Once virtual environment is active run:

```bash
python -m pip install --upgrade pip setuptools
```

#### Installing the Python module

Your current directory must be either where you unzipped the source package or where you cloned the git repo.

For standard install (users):

```bash
pip install .
```

For editable install (developers):

```bash
python -m pip install --editable ".[dev]"
```

For editable install with documentation tools:

```bash
python -m pip install --editable ".[dev,docs]"
```

The `docs` extra installs Sphinx, the Furo theme, MyST Markdown support, Mermaid
diagram support, and automatic rebuilding for HTML documentation.

## Building the Documentation

Build the HTML documentation once:

```bash
python -m sphinx -b html doc doc/_build/html
```

To rebuild automatically when documentation files change and preview the site
with live reload, run:

```bash
sphinx-autobuild doc doc/_build/html
```

The preview server is available at <http://127.0.0.1:8000> by default. Stop it
with `Ctrl+C`.

## Running Unit Tests

On Windows:

```powershell
.\run_tests.cmd
```

On Linux:

```bash
./run_tests.sh
```

Or run directly with unittest:

```bash
python -m unittest discover -v -s ./tests -p "test_*.py"
```

## Running Flake8

On Windows:

```powershell
.\run_flake.cmd
```

On Linux:

```bash
./run_flake.sh
```

## Validating Examples

Validate all documentation and example scripts:

On Windows:

```powershell
.\validate_examples.cmd
```

On Linux:

```bash
./validate_examples.sh
```

## Building a distribution package

```bash
python -m build
twine check dist/*
```
