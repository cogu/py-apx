import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import apx
import unittest
import autosar

class TestParser(unittest.TestCase):
 
   def setUp(self):
      pass
 
   def test_parse_node(self):
      text="""APX/1.2
N"TestSWC"
T"Percent_T"C
T"CoolantTemp_T"C
T"InactiveActive_T"C(0,3):VT("InactiveActive_Inactive","InactiveActive_Active","InactiveActive_Error","InactiveActive_NotAvailable")
T"OnOff_T"C(0,3):VT("OnOff_Off","OnOff_On","OnOff_Error","OnOff_NotAvailable")
T"EngineSpeed_T"S
T"VehicleSpeed_T"S
R"FuelLevel"T[0]:=255
R"CoolantTemp"T[1]:=255
R"ParkBrakeState"T[2]:=3
R"MainBeamState"T[3]:=3
P"EngineSpeed"T[4]:=0xFFFF
P"VehicleSpeed"T[5]:=0xFFFF
"""

      apx_parser = apx.Parser()
      node = apx_parser.loads(text)
      self.assertIsInstance(node, apx.Node)
      self.assertEqual(node.name, "TestSWC")
      self.assertEqual(len(node.dataTypes), 6)
      self.assertEqual(len(node.requirePorts), 4)
      self.assertEqual(len(node.providePorts), 2)
      self.assertIs(node.requirePorts[0].dsg.dataElement.typeReference, node.dataTypes[0])
      self.assertIs(node.requirePorts[1].dsg.dataElement.typeReference, node.dataTypes[1])
      self.assertIs(node.requirePorts[2].dsg.dataElement.typeReference, node.dataTypes[2])
      self.assertIs(node.requirePorts[3].dsg.dataElement.typeReference, node.dataTypes[3])
      self.assertIs(node.providePorts[0].dsg.dataElement.typeReference, node.dataTypes[4])
      self.assertIs(node.providePorts[1].dsg.dataElement.typeReference, node.dataTypes[5])
      self.assertEqual(node.find('FuelLevel').id, 0)
      self.assertEqual(node.find('CoolantTemp').id, 1)
      self.assertEqual(node.find('ParkBrakeState').id, 2)
      self.assertEqual(node.find('MainBeamState').id, 3)
      self.assertEqual(node.find('EngineSpeed').id, 0)
      self.assertEqual(node.find('VehicleSpeed').id, 1)

   def test_parse_node2(self):
      apx_text = """APX/1.2
N"TestNode"
T"VehicleSpeed_T"S
T"EngineSpeed_T"S
T"InactiveActive_T"C(0,3):VT("InactiveActive_Inactive","InactiveActive_Active","InactiveActive_Error","InactiveActive_NotAvailable")
R"VehicleSpeed"T[0]:=0xFFFF
R"EngineSpeed"T[1]:=0xFFFF
R"ParkBrakeState"T["InactiveActive_T"]:=3
"""

      apx_parser = apx.Parser()
      node = apx_parser.loads(apx_text)
      self.assertIsInstance(node, apx.Node)
      self.assertEqual(node.name, "TestNode")

   def test_parse_comments(self):
      apx_text = """APX/1.2
N"TestNode"
T"VehicleSpeed_T"S
T"EngineSpeed_T"S
T"InactiveActive_T"C(0,3):VT("InactiveActive_Inactive","InactiveActive_Active","InactiveActive_Error","InactiveActive_NotAvailable")
#Line Comment1
#Line Comment2
R"VehicleSpeed"T[0]:=0xFFFF #A Comment
R"EngineSpeed"T[1]:=0xFFFF
R"ParkBrakeState"T["InactiveActive_T"]:=3 
"""

      apx_parser = apx.Parser()
      node = apx_parser.loads(apx_text)
      self.assertIsInstance(node, apx.Node)
      self.assertEqual(node.name, "TestNode")
      port = node.find('ParkBrakeState')
      self.assertIsInstance(port, apx.RequirePort)
      

class TestParserErrors(unittest.TestCase):
   
   def test_missing_end_brace(self):      
      node = apx.Node("TestSWC")
      with self.assertRaises(apx.ParseError) as context:
         port = apx.RequirePort('TestPort1', '{"name"a[6]"Rectangle"{"x"L"y"L"width"L"height"L}','={"",{0,0,0,0}}')
      self.assertEqual(str(context.exception), "Missing '}' in data signature")
   

if __name__ == '__main__':
    unittest.main()