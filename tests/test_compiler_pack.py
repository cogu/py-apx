"""
Unit tests for bytecode pack compiler
"""
# pylint: disable=missing-class-docstring, missing-function-docstring
import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
import apx
import apx.base as apx_base
import apx.vm.base
import apx.vm.compiler


class TestCompilerPackUint8(unittest.TestCase):

    def test_pack_uint8(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"C:=255
"""
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.provide_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.HEADER_FLAG_PACK_PROG | apx.vm.base.Variant.UINT8.value,
            apx.vm.base.UINT8_SIZE,
            apx.vm.base.Variant.UINT8.value | (apx.vm.base.OpCode.PACK.value << apx.vm.base.INSTR_OPCODE_SHIFT)
        ])
        self.assertEqual(program, expected)

    def test_pack_uint8_array(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"C[2]:={255, 255}
"""
        array_len = 2
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.provide_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.HEADER_FLAG_PACK_PROG | apx.vm.base.Variant.UINT8.value,
            apx.vm.base.UINT8_SIZE * array_len,
            apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_PACK,
            apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_DATA_SIZE,
            array_len
        ])
        self.assertEqual(program, expected)

    def test_pack_uint8_with_range_check(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"C(0,3):=3
"""
        lower_limit = 0
        upper_limit = 3
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.provide_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.HEADER_FLAG_PACK_PROG | apx.vm.base.Variant.UINT8.value,
            apx.vm.base.UINT8_SIZE,
            apx.vm.base.Variant.LIMIT_CHECK_UINT8.value | apx.vm.base.OPCODE_DATA_CTRL,
            lower_limit,
            upper_limit,
            apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_PACK
        ])
        self.assertEqual(program, expected)

    def test_pack_uint8_array_with_range_check(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"C(0,3)[2]:={3, 3}
"""
        array_len = 2
        lower_limit = 0
        upper_limit = 3
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.provide_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.HEADER_FLAG_PACK_PROG | apx.vm.base.Variant.UINT8.value,
            apx.vm.base.UINT8_SIZE * array_len,
            apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.LIMIT_CHECK_UINT8.value | apx.vm.base.OPCODE_DATA_CTRL,
            lower_limit,
            upper_limit,
            apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_PACK,
            apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_DATA_SIZE,
            array_len
        ])
        self.assertEqual(program, expected)

    def test_pack_queued_uint8(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"C:Q[10]
"""
        queue_len = 10
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.provide_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        header_flags = apx.vm.base.HEADER_FLAG_PACK_PROG | apx.vm.base.HEADER_FLAG_QUEUED_DATA
        header_flags |= apx.vm.base.Variant.UINT8.value
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            header_flags,
            apx.vm.base.UINT8_SIZE * (1 + queue_len),
            apx.vm.base.Variant.ELEMENT_SIZE_U8_QUEUE_SIZE_UINT8.value | apx.vm.base.OPCODE_DATA_SIZE,
            apx.vm.base.UINT8_SIZE,
            apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_PACK
        ])
        self.assertEqual(program, expected)

    def test_pack_dynamic_array_uint8(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"C[8*]
"""
        max_array_len = 8
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.provide_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        header_flags = apx.vm.base.HEADER_FLAG_DYNAMIC_DATA | apx.vm.base.HEADER_FLAG_PACK_PROG
        header_flags |= apx.vm.base.Variant.UINT8.value
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            header_flags,
            apx.vm.base.UINT8_SIZE * (1 + max_array_len),
            apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_PACK,
            apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.ARRAY_SIZE_UINT8.value | apx.vm.base.OPCODE_DATA_SIZE,
            max_array_len
        ])
        self.assertEqual(program, expected)


class TestCompilerPackUint16(unittest.TestCase):

    def test_pack_uint16(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"S:=0
"""
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.provide_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.HEADER_FLAG_PACK_PROG | apx.vm.base.Variant.UINT8.value,
            apx.vm.base.UINT16_SIZE,
            apx.vm.base.Variant.UINT16.value | apx.vm.base.OPCODE_PACK
        ])
        self.assertEqual(program, expected)

    def test_pack_uint16_array(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"S[2]:={65535, 65535}
"""
        array_len = 2
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.provide_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.HEADER_FLAG_PACK_PROG | apx.vm.base.Variant.UINT8.value,
            apx.vm.base.UINT16_SIZE * array_len,
            apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.UINT16.value | apx.vm.base.OPCODE_PACK,
            apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_DATA_SIZE,
            array_len
        ])
        self.assertEqual(program, expected)


class TestCompilerPackUint32(unittest.TestCase):

    def test_pack_uint32(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"L:=0xFFFFFFFF
"""
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.provide_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.HEADER_FLAG_PACK_PROG | apx.vm.base.Variant.UINT8.value,
            apx.vm.base.UINT32_SIZE,
            apx.vm.base.Variant.UINT32.value | apx.vm.base.OPCODE_PACK
        ])
        self.assertEqual(program, expected)

    def test_pack_uint32_array(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"L[2]:={0xFFFFFFFF, 0xFFFFFFFF}
"""
        array_len = 2
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.provide_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.HEADER_FLAG_PACK_PROG | apx.vm.base.Variant.UINT8.value,
            apx.vm.base.UINT32_SIZE * array_len,
            apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.UINT32.value | apx.vm.base.OPCODE_PACK,
            apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_DATA_SIZE,
            array_len
        ])
        self.assertEqual(program, expected)


class TestCompilerPackUint64(unittest.TestCase):

    def test_pack_uint64(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"Q:=0xFFFFFFFFFFFFFFFF
"""
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.provide_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.HEADER_FLAG_PACK_PROG | apx.vm.base.Variant.UINT8.value,
            apx.vm.base.UINT64_SIZE,
            apx.vm.base.Variant.UINT64.value | apx.vm.base.OPCODE_PACK
        ])
        self.assertEqual(program, expected)

    def test_pack_uint64_array(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"Q[2]:={0xFFFFFFFFFFFFFFFF, 0xFFFFFFFFFFFFFFFF}
"""
        array_len = 2
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.provide_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.HEADER_FLAG_PACK_PROG | apx.vm.base.Variant.UINT8.value,
            apx.vm.base.UINT64_SIZE * array_len,
            apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.UINT64.value | apx.vm.base.OPCODE_PACK,
            apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_DATA_SIZE,
            array_len
        ])
        self.assertEqual(program, expected)


class TestCompilerPackInt8(unittest.TestCase):

    def test_pack_int8(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"c:=0
"""
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.provide_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.HEADER_FLAG_PACK_PROG | apx.vm.base.Variant.UINT8.value,
            apx.vm.base.INT8_SIZE,
            apx.vm.base.Variant.INT8.value | apx.vm.base.OPCODE_PACK
        ])
        self.assertEqual(program, expected)

    def test_pack_int8_array(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"c[2]:={-1, -1}
"""
        array_len = 2
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.provide_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.HEADER_FLAG_PACK_PROG | apx.vm.base.Variant.UINT8.value,
            apx.vm.base.INT8_SIZE * array_len,
            apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.INT8.value | apx.vm.base.OPCODE_PACK,
            apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_DATA_SIZE,
            array_len
        ])
        self.assertEqual(program, expected)

    def test_pack_int8_with_limits(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"c(-10,10):=0
"""
        lower_limit = -10
        upper_limit = 10
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.provide_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.HEADER_FLAG_PACK_PROG | apx.vm.base.Variant.UINT8.value,
            apx.vm.base.INT8_SIZE,
            apx.vm.base.Variant.LIMIT_CHECK_INT8.value | apx.vm.base.OPCODE_DATA_CTRL,
            lower_limit & 0xFF,
            upper_limit & 0xFF,
            apx.vm.base.Variant.INT8.value | apx.vm.base.OPCODE_PACK,
        ])
        self.assertEqual(program, expected)

    def test_pack_int8_array_with_limits(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"c(-10,10)[2]:={0,0}
"""
        array_len = 2
        lower_limit = -10
        upper_limit = 10
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.provide_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.HEADER_FLAG_PACK_PROG | apx.vm.base.Variant.UINT8.value,
            apx.vm.base.INT8_SIZE * array_len,
            apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.LIMIT_CHECK_INT8.value | apx.vm.base.OPCODE_DATA_CTRL,
            lower_limit & 0xFF,
            upper_limit & 0xFF,
            apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.INT8.value | apx.vm.base.OPCODE_PACK,
            apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_DATA_SIZE,
            array_len
        ])
        self.assertEqual(program, expected)


class TestCompilerPackInt16(unittest.TestCase):

    def test_pack_int16(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"s:=-1
"""
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.provide_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.HEADER_FLAG_PACK_PROG | apx.vm.base.Variant.UINT8.value,
            apx.vm.base.INT16_SIZE,
            apx.vm.base.Variant.INT16.value | apx.vm.base.OPCODE_PACK
        ])
        self.assertEqual(program, expected)

    def test_pack_int16_array(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"s[2]:={-1, -1}
"""
        array_len = 2
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.provide_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.HEADER_FLAG_PACK_PROG | apx.vm.base.Variant.UINT8.value,
            apx.vm.base.INT16_SIZE * array_len,
            apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.INT16.value | apx.vm.base.OPCODE_PACK,
            apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_DATA_SIZE,
            array_len
        ])
        self.assertEqual(program, expected)


class TestCompilerPackInt32(unittest.TestCase):

    def test_pack_int32(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"l:=-1
"""
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.provide_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.HEADER_FLAG_PACK_PROG | apx.vm.base.Variant.UINT8.value,
            apx.vm.base.INT32_SIZE,
            apx.vm.base.Variant.INT32.value | apx.vm.base.OPCODE_PACK
        ])
        self.assertEqual(program, expected)

    def test_pack_int32_array(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"l[2]:={-1, -1}
"""
        array_len = 2
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.provide_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.HEADER_FLAG_PACK_PROG | apx.vm.base.Variant.UINT8.value,
            apx.vm.base.INT32_SIZE * array_len,
            apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.INT32.value | apx.vm.base.OPCODE_PACK,
            apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_DATA_SIZE,
            array_len
        ])
        self.assertEqual(program, expected)


class TestCompilerPackInt64(unittest.TestCase):

    def test_pack_int64(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"q:=-1
"""
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.provide_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.HEADER_FLAG_PACK_PROG | apx.vm.base.Variant.UINT8.value,
            apx.vm.base.INT64_SIZE,
            apx.vm.base.Variant.INT64.value | apx.vm.base.OPCODE_PACK
        ])
        self.assertEqual(program, expected)

    def test_pack_int64_array(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"q[2]:={-1, -1}
"""
        array_len = 2
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.provide_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.HEADER_FLAG_PACK_PROG | apx.vm.base.Variant.UINT8.value,
            apx.vm.base.INT64_SIZE * array_len,
            apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.INT64.value | apx.vm.base.OPCODE_PACK,
            apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_DATA_SIZE,
            array_len
        ])
        self.assertEqual(program, expected)


class TestCompilerPackChar(unittest.TestCase):

    def test_pack_char(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"a
"""
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.provide_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.HEADER_FLAG_PACK_PROG | apx.vm.base.Variant.UINT8.value,
            apx.vm.base.CHAR_SIZE,
            apx.vm.base.Variant.CHAR.value | apx.vm.base.OPCODE_PACK
        ])
        self.assertEqual(program, expected)

    def test_pack_char_array(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"a[10]
"""
        array_len = 10
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.provide_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.HEADER_FLAG_PACK_PROG | apx.vm.base.Variant.UINT8.value,
            apx.vm.base.CHAR_SIZE * array_len,
            apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.CHAR.value | apx.vm.base.OPCODE_PACK,
            apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_DATA_SIZE,
            array_len
        ])
        self.assertEqual(program, expected)


class TestCompilerPackChar8(unittest.TestCase):

    def test_pack_char8(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"A
"""
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.provide_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.HEADER_FLAG_PACK_PROG | apx.vm.base.Variant.UINT8.value,
            apx.vm.base.CHAR8_SIZE,
            apx.vm.base.Variant.CHAR8.value | apx.vm.base.OPCODE_PACK
        ])
        self.assertEqual(program, expected)

    def test_pack_char8_array(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"A[10]
"""
        array_len = 10
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.provide_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.HEADER_FLAG_PACK_PROG | apx.vm.base.Variant.UINT8.value,
            apx.vm.base.CHAR8_SIZE * array_len,
            apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.CHAR8.value | apx.vm.base.OPCODE_PACK,
            apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_DATA_SIZE,
            array_len
        ])
        self.assertEqual(program, expected)


class TestCompilerPackBool(unittest.TestCase):

    def test_pack_bool(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"b:=0
"""
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.provide_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.HEADER_FLAG_PACK_PROG | apx.vm.base.Variant.UINT8.value,
            apx.vm.base.UINT8_SIZE,
            apx.vm.base.Variant.BOOL.value | apx.vm.base.OPCODE_PACK
        ])
        self.assertEqual(program, expected)

    def test_pack_bool_array(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"b[2]
"""
        array_len = 2
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.provide_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.HEADER_FLAG_PACK_PROG | apx.vm.base.Variant.UINT8.value,
            apx.vm.base.UINT8_SIZE * array_len,
            apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.BOOL.value | apx.vm.base.OPCODE_PACK,
            apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_DATA_SIZE,
            array_len
        ])
        self.assertEqual(program, expected)


class TestCompilerPackByte(unittest.TestCase):

    def test_pack_byte(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"B:=255
"""
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.provide_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.HEADER_FLAG_PACK_PROG | apx.vm.base.Variant.UINT8.value,
            apx.vm.base.BYTE_SIZE,
            apx.vm.base.Variant.BYTE.value | apx.vm.base.OPCODE_PACK
        ])
        self.assertEqual(program, expected)

    def test_pack_byte_array(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"B[2]
"""
        array_len = 2
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.provide_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.HEADER_FLAG_PACK_PROG | apx.vm.base.Variant.UINT8.value,
            apx.vm.base.BYTE_SIZE * array_len,
            apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.BYTE.value | apx.vm.base.OPCODE_PACK,
            apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_DATA_SIZE,
            array_len
        ])
        self.assertEqual(program, expected)

    def test_pack_dynamic_byte_array(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"B[10*]
"""
        max_array_len = 10
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.provide_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        header_flags = apx.vm.base.HEADER_FLAG_DYNAMIC_DATA | apx.vm.base.HEADER_FLAG_PACK_PROG
        header_flags |= apx.vm.base.Variant.UINT8.value
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            header_flags,
            apx.vm.base.BYTE_SIZE * (1 + max_array_len),
            apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.BYTE.value | apx.vm.base.OPCODE_PACK,
            apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.ARRAY_SIZE_UINT8.value | apx.vm.base.OPCODE_DATA_SIZE,
            max_array_len
        ])
        self.assertEqual(program, expected)


class TestCompilerPackRecord(unittest.TestCase):

    def test_pack_record_uint8_uint16(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"{"First"C"Second"S}:={255, 65535}
"""
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.provide_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        parts = [
            bytes([
                apx.vm.base.MAJOR_VERSION,
                apx.vm.base.MINOR_VERSION,
                apx.vm.base.HEADER_FLAG_PACK_PROG | apx.vm.base.Variant.UINT8.value,
                apx.vm.base.UINT8_SIZE + apx.vm.base.UINT16_SIZE,
                apx.vm.base.Variant.RECORD.value | apx.vm.base.OPCODE_PACK,
                # First record element
                apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.RECORD_SELECT.value | apx.vm.base.OPCODE_DATA_CTRL
            ]),
            bytes('First', 'ascii') + bytes([0]),
            bytes([
                apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_PACK,
                # Second record element
                apx.vm.base.Variant.RECORD_SELECT.value | apx.vm.base.OPCODE_DATA_CTRL
            ]),
            bytes('Second', 'ascii') + bytes([0]),
            bytes([
                apx.vm.base.Variant.UINT16.value | apx.vm.base.OPCODE_PACK,
                apx.vm.base.Variant.RECORD_END.value | apx.vm.base.OPCODE_DATA_CTRL
            ])
        ]
        expected = b''.join(parts)
        self.assertEqual(program, expected)

    def test_pack_record_array(self):
        apx_text = """APX/1.3
N"TestNode"
P"Signal"{"Id"S"Value"C}[2]:={{65535, 255}, {65535, 255}}
"""
        array_len = 2
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.provide_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        parts = [
            bytes([
                apx.vm.base.MAJOR_VERSION,
                apx.vm.base.MINOR_VERSION,
                apx.vm.base.HEADER_FLAG_PACK_PROG | apx.vm.base.Variant.UINT8.value,
                (apx.vm.base.UINT16_SIZE + apx.vm.base.UINT8_SIZE) * array_len,
                apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.RECORD.value | apx.vm.base.OPCODE_PACK,
                apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_DATA_SIZE,
                array_len,
                # First record element
                apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.RECORD_SELECT.value | apx.vm.base.OPCODE_DATA_CTRL
            ]),
            bytes('Id', 'ascii') + bytes([0]),
            bytes([
                apx.vm.base.Variant.UINT16.value | apx.vm.base.OPCODE_PACK,
                # Second record element
                apx.vm.base.Variant.RECORD_SELECT.value | apx.vm.base.OPCODE_DATA_CTRL
            ]),
            bytes('Value', 'ascii') + bytes([0]),
            bytes([
                apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_PACK,
                apx.vm.base.Variant.RECORD_END.value | apx.vm.base.OPCODE_DATA_CTRL,
                apx.vm.base.Variant.ARRAY_NEXT.value | apx.vm.base.OPCODE_FLOW_CTRL
            ])
        ]
        expected = b''.join(parts)
        self.assertEqual(program, expected)

    def test_pack_uint8_reference(self):
        apx_text = """APX/1.3
N"TestNode"
T"Type_T"C(0,3):VT("Off","On","Error","NotAvailable")
R"UInt8Port"T[0]:=3
"""
        lower_limit = 0
        upper_limit = 3
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.require_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        expected = bytes([
            apx.vm.base.MAJOR_VERSION,
            apx.vm.base.MINOR_VERSION,
            apx.vm.base.HEADER_FLAG_PACK_PROG | apx.vm.base.Variant.UINT8.value,
            apx.vm.base.UINT8_SIZE,
            apx.vm.base.Variant.LIMIT_CHECK_UINT8.value | apx.vm.base.OPCODE_DATA_CTRL,
            lower_limit,
            upper_limit,
            apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_PACK,
        ])
        self.assertEqual(program, expected)

    def test_pack_record_reference_with_child_references(self):
        apx_text = """APX/1.3
N"TestNode"
T"FirstType_T"C(0,3)
T"SecondType_T"C(0,7)
T"RecordType_T"{"First"T[0]"Second"T[1]}
R"RecordPort"T[2]:={3,7}
"""
        first_lower_limit = 0
        first_upper_limit = 3
        second_lower_limit = 0
        second_upper_limit = 7
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.require_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        parts = [
            bytes([
                apx.vm.base.MAJOR_VERSION,
                apx.vm.base.MINOR_VERSION,
                apx.vm.base.HEADER_FLAG_PACK_PROG | apx.vm.base.Variant.UINT8.value,
                apx.vm.base.UINT8_SIZE + apx.vm.base.UINT8_SIZE,
                apx.vm.base.Variant.RECORD.value | apx.vm.base.OPCODE_PACK,
                # First record element
                apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.RECORD_SELECT.value | apx.vm.base.OPCODE_DATA_CTRL
            ]),
            bytes('First', 'ascii') + bytes([0]),
            bytes([
                apx.vm.base.Variant.LIMIT_CHECK_UINT8.value | apx.vm.base.OPCODE_DATA_CTRL,
                first_lower_limit,
                first_upper_limit,
                apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_PACK,
                # Second record element
                apx.vm.base.Variant.RECORD_SELECT.value | apx.vm.base.OPCODE_DATA_CTRL
            ]),
            bytes('Second', 'ascii') + bytes([0]),
            bytes([
                apx.vm.base.Variant.LIMIT_CHECK_UINT8.value | apx.vm.base.OPCODE_DATA_CTRL,
                second_lower_limit,
                second_upper_limit,
                apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_PACK,
                apx.vm.base.Variant.RECORD_END.value | apx.vm.base.OPCODE_DATA_CTRL
            ])
        ]
        expected = b''.join(parts)
        self.assertEqual(program, expected)

    def test_pack_dynamic_array_of_records(self):
        apx_text = """APX/1.3
N"TestNode"
R"RecordPort"{"Id"S"Value"C}[10*]:={}
"""
        array_len = 10
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.require_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        header_flags = apx.vm.base.HEADER_FLAG_PACK_PROG | apx.vm.base.HEADER_FLAG_DYNAMIC_DATA
        header_flags |= apx.vm.base.Variant.UINT8.value
        parts = [
            bytes([
                apx.vm.base.MAJOR_VERSION,
                apx.vm.base.MINOR_VERSION,
                header_flags,
                apx.vm.base.UINT8_SIZE + (apx.vm.base.UINT16_SIZE + apx.vm.base.UINT8_SIZE) * array_len,
                apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.RECORD.value | apx.vm.base.OPCODE_PACK,
                apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.ARRAY_SIZE_UINT8.value | apx.vm.base.OPCODE_DATA_SIZE,
                array_len,
                # First record element
                apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.RECORD_SELECT.value | apx.vm.base.OPCODE_DATA_CTRL
            ]),
            bytes('Id', 'ascii') + bytes([0]),
            bytes([
                apx.vm.base.Variant.UINT16.value | apx.vm.base.OPCODE_PACK,
                # Second record element
                apx.vm.base.Variant.RECORD_SELECT.value | apx.vm.base.OPCODE_DATA_CTRL
            ]),
            bytes('Value', 'ascii') + bytes([0]),
            bytes([
                apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_PACK,
                apx.vm.base.Variant.RECORD_END.value | apx.vm.base.OPCODE_DATA_CTRL,
                apx.vm.base.Variant.ARRAY_NEXT.value | apx.vm.base.OPCODE_FLOW_CTRL
            ])
        ]
        expected = b''.join(parts)
        self.assertEqual(program, expected)

    def test_pack_record_dynamic_uint8_uint16(self):
        apx_text = """APX/1.3
N"TestNode"
R"RecordPort"{"First"C[8*]"Second"S}:={{}, 0xFFFF}
"""
        array_len = 8
        parser = apx.parser.NodeParser()
        node = parser.loads(apx_text)
        self.assertEqual(parser.result, apx_base.NO_ERROR)
        port = node.require_ports[0]
        compiler = apx.vm.compiler.Compiler()
        result, program = compiler.compile_port(port, apx.vm.base.ProgramType.PACK)
        self.assertEqual(result, apx_base.NO_ERROR)
        header_flags = apx.vm.base.HEADER_FLAG_DYNAMIC_DATA | apx.vm.base.HEADER_FLAG_PACK_PROG
        header_flags |= apx.vm.base.Variant.UINT8.value
        parts = [
            bytes([
                apx.vm.base.MAJOR_VERSION,
                apx.vm.base.MINOR_VERSION,
                header_flags,
                apx.vm.base.UINT8_SIZE + apx.vm.base.UINT8_SIZE * array_len + apx.vm.base.UINT16_SIZE,
                apx.vm.base.Variant.RECORD.value | apx.vm.base.OPCODE_PACK,
                # First record element
                apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.RECORD_SELECT.value | apx.vm.base.OPCODE_DATA_CTRL
            ]),
            bytes('First', 'ascii') + bytes([0]),
            bytes([
                apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.UINT8.value | apx.vm.base.OPCODE_PACK,
                apx.vm.base.INSTR_FLAG | apx.vm.base.Variant.ARRAY_SIZE_UINT8.value | apx.vm.base.OPCODE_DATA_SIZE,
                array_len,
                # Second record element
                apx.vm.base.Variant.RECORD_SELECT.value | apx.vm.base.OPCODE_DATA_CTRL
            ]),
            bytes('Second', 'ascii') + bytes([0]),
            bytes([
                apx.vm.base.Variant.UINT16.value | apx.vm.base.OPCODE_PACK,
                apx.vm.base.Variant.RECORD_END.value | apx.vm.base.OPCODE_DATA_CTRL
            ])
        ]
        expected = b''.join(parts)
        self.assertEqual(program, expected)


if __name__ == '__main__':
    unittest.main()
