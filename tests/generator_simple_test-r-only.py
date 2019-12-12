import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import apx
import unittest
import time
import shutil

class TestApxGenerator(unittest.TestCase):

    def test_code_generator(self):
        node = apx.Node("TestSimpleOnlyR")
        node.append(apx.RequirePort('RU16Port','S','=0xffFF'))

        output_dir = 'derived'
        output_dir_full = os.path.join(os.path.dirname(__file__),output_dir)
        if not os.path.exists(output_dir_full):
            os.makedirs(output_dir_full)
        time.sleep(0.1)
        apx.NodeGenerator().generate(output_dir_full, node, thread_safe_require_ports=False)
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
        shutil.rmtree(output_dir_full)

if __name__ == '__main__':
    unittest.main()
