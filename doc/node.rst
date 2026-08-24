Creating APX Nodes Programmatically
====================================

APX nodes can be created directly in Python using programmatic objects and data signatures.

An APX Node consists of the following components:

- **Node Name**: A unique identifier for the node within the APX network.
- **Data Types**: Zero or more custom data type definitions.
- **Provide Ports**: Zero or more output ports (data produced by this node).
- **Require Ports**: Zero or more input ports (data consumed by this node).

Creating the APX Node
---------------------

Use the ``apx.Node`` class to create a new node with your selected node name:

.. code-block:: python

    import apx

    node = apx.Node('MyNode')

Creating Ports
--------------

APX ports are created using the classes ``apx.RequirePort`` and ``apx.ProvidePort``:

.. code-block:: python

    r_port = apx.RequirePort(port_name, data_signature, attributes=None)
    p_port = apx.ProvidePort(port_name, data_signature, attributes=None)

Parameters:

- ``port_name`` (*str*): The name of the port.
- ``data_signature`` (*str*): The data signature defining its data type.
- ``attributes`` (*str | None*, optional): Attributes such as initial values, queue limits, or value tables.

Data Signatures
---------------

The data signature describes the type and structure of the data transmitted over a port.

Integer Data Types
~~~~~~~~~~~~~~~~~~

APX supports the following signed and unsigned integer types:

+-----------+-----------+------+-------------+----------------------+
| Type Code | Type Name | Bits | Min         | Max                  |
+===========+===========+======+=============+======================+
| ``c``     | sint8     | 8    | -128        | 127                  |
+-----------+-----------+------+-------------+----------------------+
| ``s``     | sint16    | 16   | -32768      | 32767                |
+-----------+-----------+------+-------------+----------------------+
| ``l``     | sint32    | 32   | -2147483648 | 2147483647           |
+-----------+-----------+------+-------------+----------------------+
| ``q``     | sint64    | 64   | -2^63       | 2^63 - 1             |
+-----------+-----------+------+-------------+----------------------+
| ``C``     | uint8     | 8    | 0           | 255                  |
+-----------+-----------+------+-------------+----------------------+
| ``S``     | uint16    | 16   | 0           | 65535                |
+-----------+-----------+------+-------------+----------------------+
| ``L``     | uint32    | 32   | 0           | 4294967295           |
+-----------+-----------+------+-------------+----------------------+
| ``Q``     | uint64    | 64   | 0           | 18446744073709551615 |
+-----------+-----------+------+-------------+----------------------+
| ``b``     | bool      | 8    | 0 (False)   | 1 (True)             |
+-----------+-----------+------+-------------+----------------------+

You can also specify explicit value limits within parentheses:

.. code-block:: python

    u8_limited = apx.RequirePort('EngineSpeed', 'S(0,8000)')
    s8_limited = apx.RequirePort('Temperature', 'c(-40,125)')

String and Character Data Types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Strings are represented as character arrays:

- ``a[N]``: ASCII string of maximum length *N*.
- ``A[N]``: UTF-8 string of maximum length *N*.

.. code-block:: python

    str_port = apx.RequirePort('VehicleIdent', 'a[17]')

Array Signatures
~~~~~~~~~~~~~~~~

Fixed-size arrays are defined by appending ``[N]`` to the type code:

.. code-block:: python

    u8_array = apx.RequirePort('SensorValues', 'C[8]')
    u16_array = apx.RequirePort('WheelSpeeds', 'S[4]')

Dynamic arrays (variable length with a size prefix) are defined with an asterisk ``*``:

.. code-block:: python

    dyn_data = apx.RequirePort('LogData', 'C[64*]')

Record Signatures
~~~~~~~~~~~~~~~~~

Records (structs) group multiple named fields inside curly braces ``{}``. Field names are enclosed in double quotes ``"..."`` followed immediately by their type:

.. code-block:: python

    user_port = apx.RequirePort('UserData', '{"Name"a[32]"Id"L}')
    rect_port = apx.RequirePort('Rectangle', '{"TopLeft"{"x"L"y"L}"BottomRight"{"x"L"y"L}}')

Custom Data Types and Type References
-------------------------------------

To avoid repeating complex type definitions across multiple ports, you can define named data types using ``apx.DataType`` and reference them in ports using ``T["TypeName"]`` or by index ``T[index]``:

.. code-block:: python

    # Define reusable data type
    node.append(apx.DataType('VehicleSpeed_T', 'S(0,300)'))

    # Reference data type by name
    node.append(apx.RequirePort('VehicleSpeed', 'T["VehicleSpeed_T"]', '=0'))

Port and Type Attributes
------------------------

Attributes provide metadata such as initial values, value tables (enumerations), and queue specifications.

Initial Values
~~~~~~~~~~~~~~

Initial values are prefixed with ``=``:

- **Scalars**: ``=0``, ``=255``, ``=-10``
- **Arrays**: ``={1, 2, 3, 4}``
- **Records**: ``={100, 200}`` or field mappings
- **Strings**: ``="default_string"``

.. code-block:: python

    port = apx.ProvidePort('Status', 'C', '=0')

Value Tables (Enumerations)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Value tables define textual enumeration labels for integer values using ``VT(...)``:

.. code-block:: python

    node.append(
        apx.DataType(
            'VehicleState_T',
            'C(0,3)',
            'VT("State_Off","State_Standby","State_Active","State_Error")'
        )
    )

Queued Ports
~~~~~~~~~~~~

For queued signal delivery, specify a queue size attribute with ``:Q[N]``:

.. code-block:: python

    queued_port = apx.ProvidePort('Events', 'C:Q[16]')

Adding Elements to the Node
---------------------------

Use the ``append()`` method (or specific helper methods) to add data types and ports to the node:

.. code-block:: python

    node = apx.Node('SensorNode')
    node.append(apx.DataType('Voltage_T', 'S'))
    node.append(apx.ProvidePort('Voltage', 'T["Voltage_T"]', '=0'))
    node.append(apx.RequirePort('Command', 'C', '=0'))

Complete Example
----------------

The following example demonstrates creating a complete automotive APX node with custom data types, type references, records, value tables, and initial values:

.. include:: examples/node_01.py
    :code: python

Parsing / Compiling to Model
----------------------------

To finalize and convert an ``apx.Node`` into an internal AST model ready for compilation or networking, pass it to ``NodeParser``:

.. code-block:: python

    from apx.parser import NodeParser

    parser = NodeParser()
    model_node = parser.from_base_node(node)
