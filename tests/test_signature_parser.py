import os, sys
sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import unittest
import apx

class TestSignatureParser(unittest.TestCase):

   def test_parse_uint8(self):
      parser = apx.parser.SignatureParser()
      (data_element, result) = parser.parse_signature('C')
      self.assertEqual(result, apx.base.NO_ERROR)
      self.assertIsInstance(data_element, apx.data_element.DataElement)
      self.assertEqual(data_element.type_code, apx.base.TYPE_CODE_UINT8)
      self.assertFalse(data_element.has_limits)
      self.assertFalse(data_element.is_array)

   def test_parse_uint8_with_limits(self):
      parser = apx.parser.SignatureParser()
      (data_element, result) = parser.parse_signature('C(0,3)')
      self.assertEqual(result, apx.base.NO_ERROR)
      self.assertIsInstance(data_element, apx.data_element.DataElement)
      self.assertEqual(data_element.type_code, apx.base.TYPE_CODE_UINT8)
      self.assertTrue(data_element.has_limits)
      self.assertFalse(data_element.is_array)
      lower_limit, upper_limit = data_element.get_limits()
      self.assertEqual(lower_limit, 0)
      self.assertEqual(upper_limit, 3)

   def test_parse_uint8_array(self):
      parser = apx.parser.SignatureParser()
      (data_element, result) = parser.parse_signature('C[8]')
      self.assertEqual(result, apx.base.NO_ERROR)
      self.assertIsInstance(data_element, apx.data_element.DataElement)
      self.assertEqual(data_element.type_code, apx.base.TYPE_CODE_UINT8)
      self.assertFalse(data_element.has_limits)
      self.assertTrue(data_element.is_array)
      self.assertEqual(data_element.array_len, 8)
