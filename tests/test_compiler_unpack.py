import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import apx
import apx.base as apx_base
import apx.vm.base
import apx.vm.compiler


class TestCompilerUnpackUint8(unittest.TestCase):

    def test_unpack_uint8(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal"C:=255
"""
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.require_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.UNPACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.Variant.UINT8.value,
            apx.vm.base.UINT8_SIZE,
            apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_UNPACK
        ])
        self.assertEqual(program, expected)

    def test_unpack_uint8_array(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal"C[2]:={255, 255}
"""
        array_len = 2
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.require_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.UNPACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.Variant.UINT8.value,
            apx.vm.base.UINT8_SIZE * array_len,
            apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_UNPACK | apx.vm.base.INSTR_FLAG,
            apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_DATA_SIZE,
            array_len
        ])
        self.assertEqual(program, expected)

    def test_unpack_uint8_with_range_check(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal"C(0,3):=3
"""
        lower_limit = 0
        upper_limit = 3
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.require_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.UNPACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.Variant.UINT8.value,
            apx.vm.base.UINT8_SIZE,
            apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_UNPACK,
            apx.vm.base.Variant.LIMIT_CHECK_UINT8.value | apx.vm.base.OPCODE_DATA_CTRL,
            lower_limit,
            upper_limit,
        ])
        self.assertEqual(program, expected)

    def test_unpack_uint8_array_with_range_check(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal"C(0,3)[2]:={3, 3}
"""
        array_len = 2
        lower_limit = 0
        upper_limit = 3
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.require_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.UNPACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.Variant.UINT8.value,
            apx.vm.base.UINT8_SIZE * array_len,
            apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_UNPACK | apx.vm.base.INSTR_FLAG,
            apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_DATA_SIZE,
            array_len,
            apx.vm.base.Variant.LIMIT_CHECK_UINT8.value | apx.vm.base.OPCODE_DATA_CTRL | apx.vm.base.INSTR_FLAG,
            lower_limit,
            upper_limit,
        ])
        self.assertEqual(program, expected)

    def test_unpack_queued_uint8(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal"C:Q[10]
"""
        queue_len = 10
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.require_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.UNPACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        header_flag = apx.vm.base.HEADER_FLAG_QUEUED_DATA
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            header_flag | apx.vm.base.Variant.UINT8.value,
            apx.vm.base.UINT8_SIZE * (1 + queue_len),
            apx.vm.base.Variant.ELEMENT_SIZE_U8_QUEUE_SIZE_UINT8.value | apx.vm.base.OPCODE_DATA_SIZE,
            apx.vm.base.UINT8_SIZE,
            apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_UNPACK
        ])
        self.assertEqual(program, expected)

    def test_unpack_dynamic_array_uint8(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal"C[8*]
"""
        max_array_len = 8
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.require_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.UNPACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        header_flag = apx.vm.base.HEADER_FLAG_DYNAMIC_DATA
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            header_flag | apx.vm.base.Variant.UINT8.value,
            apx.vm.base.UINT8_SIZE * (1 + max_array_len),
            apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_UNPACK,
            apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_DATA_SIZE,
            max_array_len
        ])
        self.assertEqual(program, expected)

    def test_unpack_large_dynamic_array_uint8_with_range_check(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal"C(0,7)[300*]
"""
        max_array_len = 300
        lower_limit = 0
        upper_limit = 7
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.require_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.UNPACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        header_flag = apx.vm.base.HEADER_FLAG_DYNAMIC_DATA
        total_data_size = apx.vm.base.UINT8_SIZE * max_array_len + apx.vm.base.UINT16_SIZE
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            header_flag | apx.vm.base.Variant.UINT16.value,
            total_data_size & 0xFF,
            (total_data_size >> 8) & 0xFF,
            apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_UNPACK,
            apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.UINT16.value | apx.vm.base.OPCODE_DATA_SIZE,
            max_array_len & 0xFF,
            (max_array_len >> 8) & 0xFF,
            apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.LIMIT_CHECK_UINT8.value | apx.vm.base.OPCODE_DATA_CTRL,
            lower_limit,
            upper_limit,
        ])
        self.assertEqual(program, expected)


class TestCompilerUnpackUint16(unittest.TestCase):

    def test_unpack_uint16(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal"S:=0
"""
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.require_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.UNPACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.Variant.UINT8.value,
            apx.vm.base.UINT16_SIZE,
            apx.vm.base.Variant.UINT16.value | apx.vm.base.OPCODE_UNPACK
        ])
        self.assertEqual(program, expected)

    def test_unpack_uint16_array(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal"S[2]:={65535, 65535}
"""
        array_len = 2
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.require_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.UNPACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.Variant.UINT8.value,
            apx.vm.base.UINT16_SIZE * array_len,
            apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.UINT16.value | apx.vm.base.OPCODE_UNPACK,
            apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_DATA_SIZE,
            array_len
        ])
        self.assertEqual(program, expected)


class TestCompilerUnpackUint32(unittest.TestCase):

    def test_unpack_uint32(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal"L:=0xFFFFFFFF
"""
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.require_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.UNPACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.Variant.UINT8.value,
            apx.vm.base.UINT32_SIZE,
            apx.vm.base.Variant.UINT32.value | apx.vm.base.OPCODE_UNPACK
        ])
        self.assertEqual(program, expected)

    def test_unpack_uint32_array(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal"L[2]:={0xFFFFFFFF, 0xFFFFFFFF}
"""
        array_len = 2
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.require_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.UNPACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.Variant.UINT8.value,
            apx.vm.base.UINT32_SIZE * array_len,
            apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.UINT32.value | apx.vm.base.OPCODE_UNPACK,
            apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_DATA_SIZE,
            array_len
        ])
        self.assertEqual(program, expected)


class TestCompilerUnpackUint64(unittest.TestCase):

    def test_unpack_uint64(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal"Q:=0xFFFFFFFFFFFFFFFF
"""
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.require_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.UNPACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.Variant.UINT8.value,
            apx.vm.base.UINT64_SIZE,
            apx.vm.base.Variant.UINT64.value | apx.vm.base.OPCODE_UNPACK
        ])
        self.assertEqual(program, expected)

    def test_unpack_uint64_array(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal"Q[2]:={0xFFFFFFFFFFFFFFFF, 0xFFFFFFFFFFFFFFFF}
"""
        array_len = 2
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.require_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.UNPACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.Variant.UINT8.value,
            apx.vm.base.UINT64_SIZE * array_len,
            apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.UINT64.value | apx.vm.base.OPCODE_UNPACK,
            apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_DATA_SIZE,
            array_len
        ])
        self.assertEqual(program, expected)


class TestCompilerUnpackInt8(unittest.TestCase):

    def test_unpack_int8(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal"c:=0
"""
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.require_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.UNPACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.Variant.UINT8.value,
            apx.vm.base.INT8_SIZE,
            apx.vm.base.Variant.INT8.value | apx.vm.base.OPCODE_UNPACK
        ])
        self.assertEqual(program, expected)

    def test_unpack_int8_array(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal"c[2]:={-1, -1}
"""
        array_len = 2
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.require_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.UNPACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.Variant.UINT8.value,
            apx.vm.base.INT8_SIZE * array_len,
            apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.INT8.value | apx.vm.base.OPCODE_UNPACK,
            apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_DATA_SIZE,
            array_len
        ])
        self.assertEqual(program, expected)

    def test_unpack_int8_with_limits(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal"c(-10,10):=0
"""
        lower_limit = -10
        upper_limit = 10
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.require_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.UNPACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.Variant.UINT8.value,
            apx.vm.base.INT8_SIZE,
            apx.vm.base.Variant.INT8.value | apx.vm.base.OPCODE_UNPACK,
            apx.vm.base.Variant.LIMIT_CHECK_INT8.value | apx.vm.base.OPCODE_DATA_CTRL,
            lower_limit & 0xFF,
            upper_limit & 0xFF,
        ])
        self.assertEqual(program, expected)

    def test_unpack_int8_array_with_limits(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal"c(-10,10)[2]:={0,0}
"""
        array_len = 2
        lower_limit = -10
        upper_limit = 10
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.require_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.UNPACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.Variant.UINT8.value,
            apx.vm.base.INT8_SIZE * array_len,
            apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.INT8.value | apx.vm.base.OPCODE_UNPACK,
            apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_DATA_SIZE,
            array_len,
            apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.LIMIT_CHECK_INT8.value | apx.vm.base.OPCODE_DATA_CTRL,
            lower_limit & 0xFF,
            upper_limit & 0xFF,
        ])
        self.assertEqual(program, expected)


class TestCompilerUnpackInt16(unittest.TestCase):

    def test_unpack_int16(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal"s:=-1
"""
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.require_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.UNPACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.Variant.UINT8.value,
            apx.vm.base.INT16_SIZE,
            apx.vm.base.Variant.INT16.value | apx.vm.base.OPCODE_UNPACK
        ])
        self.assertEqual(program, expected)

    def test_unpack_int16_array(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal"s[2]:={-1, -1}
"""
        array_len = 2
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.require_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.UNPACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.Variant.UINT8.value,
            apx.vm.base.INT16_SIZE * array_len,
            apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.INT16.value | apx.vm.base.OPCODE_UNPACK,
            apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_DATA_SIZE,
            array_len
        ])
        self.assertEqual(program, expected)


class TestCompilerUnpackInt32(unittest.TestCase):

    def test_unpack_int32(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal"l:=-1
"""
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.require_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.UNPACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.Variant.UINT8.value,
            apx.vm.base.INT32_SIZE,
            apx.vm.base.Variant.INT32.value | apx.vm.base.OPCODE_UNPACK
        ])
        self.assertEqual(program, expected)

    def test_unpack_int32_array(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal"l[2]:={-1, -1}
"""
        array_len = 2
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.require_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.UNPACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.Variant.UINT8.value,
            apx.vm.base.INT32_SIZE * array_len,
            apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.INT32.value | apx.vm.base.OPCODE_UNPACK,
            apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_DATA_SIZE,
            array_len
        ])
        self.assertEqual(program, expected)


class TestCompilerUnpackInt64(unittest.TestCase):

    def test_unpack_int64(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal"q:=-1
"""
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.require_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.UNPACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.Variant.UINT8.value,
            apx.vm.base.INT64_SIZE,
            apx.vm.base.Variant.INT64.value | apx.vm.base.OPCODE_UNPACK
        ])
        self.assertEqual(program, expected)

    def test_unpack_int64_array(self):
        apx_text = """APX/1.3
N"TestNode"
R"Signal"q[2]:={-1, -1}
"""
        array_len = 2
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.require_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.UNPACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.Variant.UINT8.value,
            apx.vm.base.INT64_SIZE * array_len,
            apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.INT64.value | apx.vm.base.OPCODE_UNPACK,
            apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_DATA_SIZE,
            array_len
        ])
        self.assertEqual(program, expected)


if __name__ == '__main__':
    unittest.main()
