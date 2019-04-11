import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import apx
import unittest
import time
import shutil

class TestApxGenerator(unittest.TestCase):

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

    def test_code_generator(self):
        node = apx.Node("Test")
        node.append(apx.DataType('SoundRequest_T','{"SoundId"S"Volume"C}'))
        node.append(apx.RequirePort('RU8FirstPort','C','=12'))
        node.append(apx.RequirePort('RS16ARPort','s[3]','={32767, 1, 0}'))
        node.append(apx.RequirePort('RS32Port','l','=1'))
        node.append(apx.RequirePort('RU8Port','C','=255'))
        node.append(apx.RequirePort('RU8ARPort','C[3]','={255, 255, 255}'))
        node.append(apx.RequirePort('SoundRequest','T["SoundRequest_T"]', '={65535,255}'))
        node.append(apx.RequirePort('RU8LastPort','C','=210'))
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
        node.finalize(sort=False)
        apx.NodeGenerator().generate(output_dir_full, node, callbacks=callback_map)
        with open (os.path.join(os.path.dirname(__file__), output_dir, 'ApxNode_{0.name}.h'.format(node)), "r") as fp:
            generated=fp.read()
        with open (os.path.join(os.path.dirname(__file__), 'expected_gen', 'ApxNode_{0.name}.h'.format(node)), "r") as fp:
            expected=fp.read()
        self.assertEqual(expected, generated)
        with open (os.path.join(os.path.dirname(__file__), output_dir, 'ApxNode_{0.name}.c'.format(node)), "r") as fp:
            generated=fp.read()
        with open (os.path.join(os.path.dirname(__file__), 'expected_gen', 'ApxNode_{0.name}.c'.format(node)), "r") as fp:
            expected=fp.read()
        self.assertEqual(expected, generated)
        with open (os.path.join(os.path.dirname(__file__), output_dir, 'ApxNode_{0.name}_Cbk.h'.format(node)), "r") as fp:
            generated=fp.read()
        with open (os.path.join(os.path.dirname(__file__), 'expected_gen', 'ApxNode_{0.name}_Cbk.h'.format(node)), "r") as fp:
            expected=fp.read()
        self.assertEqual(expected, generated)
        shutil.rmtree(output_dir_full)

if __name__ == '__main__':
    unittest.main()
