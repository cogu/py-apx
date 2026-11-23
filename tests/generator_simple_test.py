import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import apx
import unittest
import time
import shutil

from tests.generator_test_support import GeneratorTestCase

class TestApxGenerator(GeneratorTestCase):

    def test_code_generator(self):
        node = apx.Node("TestSimple")
        node.append(apx.RequirePort('RS32Port','l','=-2147483648'))
        node.append(apx.RequirePort('RU8Port','C','=255'))
        node.append(apx.RequirePort('PS16ARPort256','s[256]'))
        node.append(apx.ProvidePort('PS16ARPort256','s[256]'))
        node.append(apx.ProvidePort('PS8Port','c','=-1'))
        node.append(apx.ProvidePort('PU32Port','L','=4294967295'))

        output_dir = 'derived'
        output_dir_full = os.path.join(os.path.dirname(__file__),output_dir)
        if not os.path.exists(output_dir_full):
            os.makedirs(output_dir_full)
        time.sleep(0.1)
        apx.NodeGenerator().generate(output_dir_full, node)
        self.assert_generated_files(output_dir_full, node.name, '.h', '.c')
        shutil.rmtree(output_dir_full)

if __name__ == '__main__':
    unittest.main()
