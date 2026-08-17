"""
Unit tests for manual node creation
"""
# pylint: disable=missing-class-docstring, missing-function-docstring
import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import apx  # noqa E402
import apx.base as apx_base  # noqa E402


class TestNodeCreation(unittest.TestCase):

    def test_create_empty_node(self):
        node = apx.Node('TestNode')
        self.assertIsInstance(node, apx_base.Node)
        self.assertEqual(node.name, 'TestNode')
        self.assertEqual(len(node.require_ports), 0)
        self.assertEqual(len(node.provide_ports), 0)

    def test_create_require_port_uint8(self):
        node = apx.Node('TestNode')
        port = node.append(apx.RequirePort('U8Signal', 'C', '=255'))
        self.assertIsInstance(port, apx_base.RequirePort)
        self.assertEqual(len(node.require_ports), 1)


if __name__ == '__main__':
    unittest.main()
