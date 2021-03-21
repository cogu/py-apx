import os, sys
sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import unittest
import apx

class TestSignatureParser(unittest.TestCase):

   def test_parse_uint8(self):
      parser = apx.parser.SignatureParser()
      (data_element, remain) = parser.parse_signature('C')
      self.assertEqual(len(remain), 0)
      self.assertIsInstance(data_element, apx.data_element.DataElement)
      self.assertEqual(data_element.type_code, apx.base.TYPE_CODE_UINT8)
      self.assertFalse(data_element.has_limits)
      self.assertFalse(data_element.is_array)
