import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import apx
import unittest
import remotefile
import autosar

class TestApxDataType(unittest.TestCase):

    def setUp(self):
        pass

    def test_create_uint8_type(self):
        dt = apx.DataType('MyU8_T','C')
        self.assertIsInstance(dt, apx.DataType)
        self.assertEqual(dt.dataElement.typeCode, apx.UINT8_TYPE_CODE)
        self.assertEqual(str(dt), 'T"MyU8_T"C')

    def test_create_uint8_range_type(self):
        dt = apx.DataType('MyU8_T','C(0,3)')
        self.assertIsInstance(dt, apx.DataType)
        self.assertEqual(dt.dataElement.typeCode, apx.UINT8_TYPE_CODE)
        self.assertEqual(str(dt), 'T"MyU8_T"C(0,3)')

    def test_create_uint8_array_type(self):
        dt = apx.DataType('MyU8_T','C[8]')
        self.assertIsInstance(dt, apx.DataType)
        self.assertEqual(dt.dataElement.typeCode, apx.UINT8_TYPE_CODE)
        self.assertEqual(str(dt), 'T"MyU8_T"C[8]')

    def test_clone_uint8_type(self):
        dt1 = apx.DataType('MyU8_T','C')
        dt2 = dt1.clone()
        self.assertIsInstance(dt2, apx.DataType)
        self.assertEqual(dt2.dataElement.typeCode, apx.UINT8_TYPE_CODE)
        self.assertEqual(str(dt2), 'T"MyU8_T"C')

    def test_create_uint16_type(self):
        dt = apx.DataType('MyU16_T','S')
        self.assertIsInstance(dt, apx.DataType)
        self.assertEqual(dt.dataElement.typeCode, apx.UINT16_TYPE_CODE)

    def test_clone_uint16_type(self):
        dt1 = apx.DataType('MyU16_T','S')
        dt2 = dt1.clone()
        self.assertIsInstance(dt2, apx.DataType)
        self.assertEqual(dt2.dataElement.typeCode, apx.UINT16_TYPE_CODE)
        self.assertEqual(str(dt2), 'T"MyU16_T"S')

    def test_create_uint32_type(self):
        dt = apx.DataType('MyU32_T','L')
        self.assertIsInstance(dt, apx.DataType)
        self.assertEqual(dt.dataElement.typeCode, apx.UINT32_TYPE_CODE)

    def test_clone_uint32_type(self):
        dt1 = apx.DataType('MyU32_T','L')
        dt2 = dt1.clone()
        self.assertIsInstance(dt2, apx.DataType)
        self.assertEqual(dt2.dataElement.typeCode, apx.UINT32_TYPE_CODE)
        self.assertEqual(str(dt2), 'T"MyU32_T"L')

    def test_create_ref_type(self):
        dt = apx.DataType('MyRef_T','T["MyU8_T"]')
        self.assertIsInstance(dt, apx.DataType)
        self.assertEqual(dt.dataElement.typeCode, apx.REFERENCE_TYPE_CODE)
        self.assertEqual(dt.dataElement.typeReference, 'MyU8_T')
        self.assertEqual(str(dt), 'T"MyRef_T"T["MyU8_T"]')

    def test_clone_ref_type(self):
        dt1 = apx.DataType('MyRef_T','T["MyU8_T"]')
        dt2 = dt1.clone()
        self.assertIsInstance(dt2, apx.DataType)
        self.assertEqual(dt2.dataElement.typeCode, apx.REFERENCE_TYPE_CODE)
        self.assertEqual(dt2.dataElement.typeReference, 'MyU8_T')
        self.assertEqual(str(dt2), 'T"MyRef_T"T["MyU8_T"]')

    def test_record_type(self):
        dt = apx.DataType('MyRecord_T','{"Name"a[8]"Id"L"Data"S[3]}')
        self.assertIsInstance(dt, apx.DataType)
        self.assertEqual(dt.dataElement.typeCode, apx.RECORD_TYPE_CODE)
        self.assertEqual(str(dt), 'T"MyRecord_T"{"Name"a[8]"Id"L"Data"S[3]}')

if __name__ == '__main__':
    unittest.main()