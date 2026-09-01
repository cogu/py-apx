Parsers (``apx.parser``)
=========================

The ``apx.parser`` package provides parsing facilities for APX node definitions, type signatures, and port attributes.

Node Parser
-----------

.. autoclass:: apx.parser.node.NodeParser
   :members:
   :show-inheritance:

Signature Parser
----------------

.. autoclass:: apx.parser.signature.SignatureParser
   :members:
   :show-inheritance:

Attribute Parser
----------------

.. autoclass:: apx.parser.attribute.AttributeParser
   :members:
   :show-inheritance:

Base Parser & Helpers
---------------------

.. autoclass:: apx.parser.base.BaseParser
   :members:
   :show-inheritance:

.. autofunction:: apx.parser.base.split_port_declaration

.. autofunction:: apx.parser.base.split_type_declaration

.. autofunction:: apx.parser.base.strip_comment
