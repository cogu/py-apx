import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import apx
import autosar
import unittest
import time
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from tests.generator_test_support import GeneratorTestCase

class TestApxGenerator(GeneratorTestCase):

    def test_ctypename(self):
        dsg = apx.DataSignature('C')
        self.assertEqual(dsg.ctypename(),'uint8')
        dsg = apx.DataSignature('c')
        self.assertEqual(dsg.ctypename(),'sint8')
        dsg = apx.DataSignature('S')
        self.assertEqual(dsg.ctypename(),'uint16')
        dsg = apx.DataSignature('s')
        self.assertEqual(dsg.ctypename(),'sint16')
        dsg = apx.DataSignature('L')
        self.assertEqual(dsg.ctypename(),'uint32')
        dsg = apx.DataSignature('l')
        self.assertEqual(dsg.ctypename(),'sint32')

    def test_empty_callback_map_matches_no_callbacks(self):
        node = apx.Node("EmptyCallbacks")
        node.append(apx.RequirePort('Speed', 'C'))

        with TemporaryDirectory() as expected_dir, TemporaryDirectory() as output_dir:
            apx.NodeGenerator().generate(expected_dir, node)
            apx.NodeGenerator().generate(output_dir, node, callbacks={})

            filenames = ['ApxNode_EmptyCallbacks.c', 'ApxNode_EmptyCallbacks.h']
            self.assertCountEqual(os.listdir(output_dir), filenames)
            for filename in filenames:
                self.assertEqual(
                    (Path(expected_dir) / filename).read_bytes(),
                    (Path(output_dir) / filename).read_bytes(),
                )

    def test_autosar_array_and_record_port_types(self):
        ws = autosar.workspace()
        types = ws.createPackage('DataType', role='DataType')
        types.createIntegerDataType('UInt8', min=0, max=255)
        element = types.createIntegerDataType('UInt16', min=0, max=65535)
        types.createArrayDataType('U16Array_T', element.ref, 4)
        types.createRecordDataType('MyRecord_T', elements=[
            ('First', 'UInt8'),
            ('Second', 'U16Array_T'),
        ])
        interfaces = ws.createPackage('PortInterface', role='PortInterface')
        interfaces.createSenderReceiverInterface('Array_I', autosar.DataElement('Value', 'U16Array_T'))
        interfaces.createSenderReceiverInterface('Record_I', autosar.DataElement('Value', 'MyRecord_T'))
        components = ws.createPackage('ComponentType', role='ComponentType')
        swc = components.createApplicationSoftwareComponent('ArrayNode')
        swc.createRequirePort('Receiver', 'Array_I')
        swc.createProvidePort('Sender', 'Array_I')
        swc.createRequirePort('RecordReceiver', 'Record_I')
        node = apx.Node().import_autosar_swc(swc)

        with TemporaryDirectory() as output_dir:
            apx.NodeGenerator().generate(output_dir, node, callbacks={'Receiver': 'OnArrayReceived'})
            for suffix in ('.h', '.c'):
                with self.subTest(suffix=suffix):
                    generated = (Path(output_dir) / ('ApxNode_ArrayNode' + suffix)).read_text()
                    self.assertIn('ApxNode_Read_ArrayNode_Receiver(uint16 *val)', generated)
                    self.assertIn('ApxNode_Write_ArrayNode_Sender(uint16 *val)', generated)
                    self.assertIn('ApxNode_Read_ArrayNode_RecordReceiver(MyRecord_T *val)', generated)
                    if suffix == '.c':
                        self.assertIn('val->First = (uint8_t) *p;', generated)
                        self.assertIn('val->Second[i] = (uint16_t) unpackLE(', generated)
            callback_header = (Path(output_dir) / 'ApxNode_ArrayNode_Cbk.h').read_text()
            self.assertIn('void OnArrayReceived(uint16 *value);', callback_header)

    def test_code_generator(self):
        node = apx.Node("Test")
        node.append(apx.DataType('SoundRequest_T','{"SoundId"S"Volume"C}'))
        node.append(apx.DataType('LightRequest_T','{"LightId"S"Intensity"C}'))
        node.append(apx.DataType('HapticRequest_T','{"HapticId"S"Intensity"C}'))
        node.append(apx.RequirePort('RU8FirstPort','C','=12'))
        node.append(apx.RequirePort('RS16ARPort','s[3]','={32767, 1, 0}'))
        node.append(apx.RequirePort('RS32Port','l','=1'))
        node.append(apx.RequirePort('RU8Port','C','=255'))
        node.append(apx.RequirePort('RU8ARPort','C[3]','={255, 255, 255}'))
        node.append(apx.RequirePort('LightRequest','T["LightRequest_T"]', '={65535,255}'))
        node.append(apx.RequirePort('SoundRequest','T["SoundRequest_T"]', '={65535,255}'))
        node.append(apx.RequirePort('RU8LastPort','C','=210'))
        node.append(apx.ProvidePort('SoundRequestAck','T["SoundRequest_T"]', '={65535,255}'))
        node.append(apx.ProvidePort('HapticRequest','T["HapticRequest_T"]', '={65535,255}'))
        node.append(apx.ProvidePort('PS8ARPort','c[1]','={1}'))
        node.append(apx.ProvidePort('PS8Port','c','=0'))
        node.append(apx.ProvidePort('PU16ARPort','S[4]','={65535, 65535, 65535, 65535}'))
        node.append(apx.ProvidePort('PU32Port','L','=4294967295'))

        callback_map = { 'RU8Port': 'RU8Port_cb_func',
                         'RS16ARPort': 'RS16ARPort_cb_func',
                         'SoundRequest': 'SoundRequest_cb_func' }

        output_dir = 'derived'
        output_dir_full = os.path.join(os.path.dirname(__file__),output_dir)
        if not os.path.exists(output_dir_full):
            os.makedirs(output_dir_full)
        time.sleep(0.1)
        # If we want ports in the order appended; explicitly finalize the node before generator
        node.finalize(sort=False, compact=True)
        apx.NodeGenerator().generate(output_dir_full, node, callbacks=callback_map)
        self.assert_generated_files(output_dir_full, node.name, '.h', '.c', '_Cbk.h')

        node.name = "Test_compact"
        apx.NodeGenerator().generate(output_dir_full, node, callbacks=callback_map, compact=True)
        self.assert_generated_files(output_dir_full, node.name, '.h', '.c', '_Cbk.h')
        shutil.rmtree(output_dir_full)

if __name__ == '__main__':
    unittest.main()
