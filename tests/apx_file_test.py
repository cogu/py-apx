import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import apx
import unittest
import remotefile
import time
import re
from collections import namedtuple

FileWrite = namedtuple('FileWrite', "file offset length")

@apx.NodeDataHandler.register
class MockNodeDataHandler:
   def __init__(self):
      self.calls=[]
   def inPortDataWriteNotify(self, file, offset: int, length: int):
      """
      Called by FileManager when it receives a remote write in the node's inPortData file
      """
      self.calls.append(FileWrite(file, offset, length))

class MockFileManager:
   def __init__(self):
      self.calls=[]

   def outPortDataWriteNotify(self, file, offset : int, length : int):
      self.calls.append(FileWrite(file, offset, length))


class TestApxFile(unittest.TestCase):

   def test_input_file(self):
      mockDataHandler = MockNodeDataHandler()
      inFile = apx.InputFile('test1.in', 10)
      inFile.nodeDataHandler=mockDataHandler
      self.assertIsInstance(inFile.data, bytearray)
      self.assertEqual(len(inFile.data), 10)
      retval = inFile.write(5, b"\x01\x02\x03")
      self.assertEqual(retval, 3)
      self.assertEqual(len(mockDataHandler.calls), 1)
      self.assertEqual(mockDataHandler.calls[-1].offset,5)
      self.assertEqual(mockDataHandler.calls[-1].length,3)
      self.assertEqual(inFile.data[5:8], b"\x01\x02\x03")
      data = inFile.read(mockDataHandler.calls[-1].offset, mockDataHandler.calls[-1].length)
      self.assertIsInstance(data, bytes)
      self.assertEqual(len(data), 3)
      self.assertEqual(data, b"\x01\x02\x03")

   def test_output_file(self):
      outFile = apx.OutputFile('test1.out', 5)
      self.assertIsInstance(outFile.data, bytearray)
      self.assertEqual(len(outFile.data), 5)
      retval = outFile.write(2, b"\x01\x02\x03")
      self.assertEqual(retval, 3)
      self.assertEqual(outFile.data[2:5], b"\x01\x02\x03")



if __name__ == '__main__':
    unittest.main()

