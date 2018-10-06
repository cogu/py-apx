import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import apx
import unittest
import remotefile
import time
import re


class TestApxContext(unittest.TestCase):


   def test_dumps_from_raw(self):
      node = apx.Node('Simulator')
      node.dataTypes.append(apx.DataType('InactiveActive_T','C(0,3)'))
      node.providePorts.append(apx.ProvidePort('VehicleSpeed','S','=65535'))
      node.providePorts.append(apx.ProvidePort('MainBeam','T[0]','=3'))
      node.providePorts.append(apx.ProvidePort('FuelLevel','C'))
      node.providePorts.append(apx.ProvidePort('ParkBrakeActive','T[0]','=3'))
      node.requirePorts.append(apx.RequirePort('RheostatLevelRqst','C','=255'))
      node.finalize()
      context = apx.Context()
      context.append(node)
      text=context.dumps()
      lines=re.compile(r'\r\n|\n').split(text)
      self.assertEqual(len(lines),9)
      self.assertEqual(lines[0],'APX/1.2')
      self.assertEqual(lines[1],'N"Simulator"')
      self.assertEqual(lines[2],'T"InactiveActive_T"C(0,3)')
      self.assertEqual(lines[3],'P"VehicleSpeed"S:=65535')
      self.assertEqual(lines[4],'P"MainBeam"T[0]:=3')
      self.assertEqual(lines[5],'P"FuelLevel"C')
      self.assertEqual(lines[6],'P"ParkBrakeActive"T[0]:=3')
      self.assertEqual(lines[7],'R"RheostatLevelRqst"C:=255')
      self.assertEqual(lines[8],'')

   def test_load_dumped_apx_text(self):
      node1 = apx.Node('Simulator')
      node1.dataTypes.append(apx.DataType('InactiveActive_T','C(0,3)'))
      node1.providePorts.append(apx.ProvidePort('VehicleSpeed','S','=65535'))
      node1.providePorts.append(apx.ProvidePort('MainBeam','T[0]','=3'))
      node1.providePorts.append(apx.ProvidePort('FuelLevel','C'))
      node1.providePorts.append(apx.ProvidePort('ParkBrakeActive','T[0]','=3'))
      node1.requirePorts.append(apx.RequirePort('RheostatLevelRqst','C','=255'))
      self.assertFalse(node1.providePorts[0].dsg.isComplexType())

      node1.finalize()
      context = apx.Context()
      context.append(node1)
      text=context.dumps()

      apx_parser = apx.Parser()
      node2 = apx_parser.loads(text)
      self.assertFalse(node2.providePorts[0].dsg.isComplexType())



if __name__ == '__main__':
    unittest.main()

