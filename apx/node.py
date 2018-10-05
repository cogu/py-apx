import autosar
import apx
import math
from copy import deepcopy
from apx.parser import apx_split_line, Parser




class Node:
   """
   Represents an APX node

   Example:
   >>> import sys
   >>> import apx
   >>> node = apx.Node()
   >>> node.append(apx.ProvidePort('TestSignal1','C'))
   0
   >>> node.append(apx.RequirePort('TestSignal2','S'))
   0
   >>> node.write(sys.stdout)
   N"None"
   P"TestSignal1"C
   R"TestSignal2"S
   """
   def __init__(self,name=None):
      self.name=name
      self.isFinalized = False
      self.dataTypes = []
      self.requirePorts=[]
      self.providePorts=[]
      self.dataTypeMap = {}


   @classmethod
   def from_autosar_swc(cls, swc, name=None, reverse=False):
      assert(isinstance(swc, autosar.component.AtomicSoftwareComponent))
      node = cls()
      node.import_autosar_swc(swc, name=name)
      return node

   @classmethod
   def from_text(cls, text):
      return Parser().loads(text)

   def _updateDataType(self, ws, port):
      portInterface = ws.find(port.portInterfaceRef)
      if isinstance(portInterface,autosar.portinterface.SenderReceiverInterface):
         if len(portInterface.dataElements)==1:
            dataType = ws.find(portInterface.dataElements[0].typeRef)
            assert(dataType is not None)
            if dataType.name not in self.dataTypeMap:
               item = apx.AutosarDataType(ws,dataType, self)
               item.id=len(self.dataTypes)
               self.dataTypeMap[dataType.name]=item
               self.dataTypes.append(item)
               assert (item is not None)
               return item
            else:
               item = self.dataTypeMap[dataType.name]
               assert (item is not None)
               return item
         elif len(portInterface.dataElements)>1:
            raise NotImplementedError('SenderReceiverInterface with more than 1 element not supported')
      return None

   def _calcAttributeFromAutosarPort(self,ws,port):
      """
      returns string
      """
      if (len(port.comspec)==1) and isinstance(port.comspec[0],autosar.component.DataElementComSpec):
         if port.comspec[0].initValueRef is not None:
            initValue = ws.find(port.comspec[0].initValueRef)
            if initValue is None:
               raise ValueError('invalid init value reference: '+port.comspec[0].initValueRef)
            if isinstance(initValue, autosar.constant.Constant):
               initValue=initValue.value
            return "="+self._deriveInitValueFromAutosarConstant(initValue)
      return None

   def _deriveInitValueFromAutosarConstant(self,item):
      if isinstance(item,autosar.constant.IntegerValue):
         if (item.value>255):
            return "0x%02X"%item.value
         else:
            return "%d"%item.value
      elif isinstance(item,autosar.constant.StringValue):
            return '"%s"'%item.value
      elif isinstance(item,autosar.constant.RecordValue):
         tmp = [self._deriveInitValueFromAutosarConstant(x) for x in item.elements]
         return "{"+','.join(tmp)+"}"
      elif isinstance(item,autosar.constant.ArrayValue):
         tmp = [self._deriveInitValueFromAutosarConstant(x) for x in item.elements]
         return "{"+','.join(tmp)+"}"
      else:
         raise NotImplementedError(str(type(item)))


   def import_autosar_swc(self, swc, ws=None, name=None):
      assert(isinstance(swc, autosar.component.AtomicSoftwareComponent))
      if name is None:
         self.name=swc.name
      else:
         self.name = name
      if ws is None:
         ws=swc.rootWS()
      for port in swc.providePorts:
         self.add_autosar_port(port, ws)
      for port in swc.requirePorts:
         self.add_autosar_port(port, ws)
      self.resolve_types()
      return self



   def add_autosar_port(self, port, ws=None):
      """
      adds an autosar port to the node
      returns the port ID of the newly added port
      """
      if ws is None:
         ws=port.rootWS()
      assert(ws is not None)
      dataType=self._updateDataType(ws, port)
      if dataType is not None:
         if isinstance(port, autosar.component.RequirePort):
            apx_port = apx.RequirePort(port.name, "T[%s]"%dataType.id, self._calcAttributeFromAutosarPort(ws, port))
            return self.add_require_port(apx_port)
         elif isinstance(port, autosar.component.ProvidePort):
            apx_port = apx.ProvidePort(port.name, "T[%s]"%dataType.id, self._calcAttributeFromAutosarPort(ws, port))
            return self.add_provide_port(apx_port)
         else:
            raise ValueError('invalid type '+str(type(port)))

   def append(self, item):
      """
      Adds the item to the node.
      Item can be of type DataType, RequirePort and ProvidePort
      returns the object (port or datatype)
      """
      if isinstance(item, apx.DataType):
         return self.add_type(item)
      if isinstance(item, apx.RequirePort):
         return self.add_require_port(item)
      elif isinstance(item, apx.ProvidePort):
         return self.add_provide_port(item)
      elif isinstance(item, autosar.component.Port):
         return self.add_autosar_port(item)
      elif isinstance(item, str):
         parts = apx_split_line(item)
         if len(parts) != 4:
            raise ValueError("invalid APX string: '%s'"%item)
         if parts[0]=='R':
            newPort = apx.RequirePort(parts[1],parts[2],parts[3])
            if newPort is not None:
               return self.add_require_port(newPort)
            else:
               raise ValueError('apx.RequirePort() returned None')
         elif parts[0]=='P':
            newPort = apx.ProvidePort(parts[1],parts[2],parts[3])
            if newPort is not None:
               return self.add_provide_port(newPort)
            else:
               raise ValueError('apx.ProvidePort() returned None')
         else:
            raise ValueError(parts[0])
      else:
         raise ValueError(type(port))


   def add_type(self, dataType):
      if dataType.name not in self.dataTypeMap:
         dataType.id=len(self.dataTypes)
         dataType.dsg.resolve_data_element(self.dataTypes)
         self.dataTypeMap[dataType.name]=dataType
         self.dataTypes.append(dataType)
         return dataType
      else:
         raise ValueError('Data type with name {} already exists'.format(dataType.name))

   def add_require_port(self, port):
      port.id = len(self.requirePorts)
      if port.dsg.dataElement.isReference:
         port.resolve_type(self.dataTypes)
      self.requirePorts.append(port)
      return port

   def add_provide_port(self, port):
      port.id = len(self.providePorts)
      if port.dsg.dataElement.isReference:
         port.resolve_type(self.dataTypes)
      self.providePorts.append(port)
      return port

   def write(self, fp):
      """
      writes node as text in fp
      """
      print('N"%s"'%self.name, file=fp)
      for dataType in self.dataTypes:
         print(str(dataType), file=fp)
      for port in self.providePorts:
         print(str(port), file=fp)
      for port in self.requirePorts:
         print(str(port), file=fp)

   def lines(self, normalized=None):
      """
      returns context as list of strings (one line at a time)
      """
      lines = ['N"%s"'%self.name]
      for dataType in self.dataTypes:
         lines.append(str(dataType))
      for port in self.providePorts:
         lines.append(str(port))
      for port in self.requirePorts:
         lines.append(str(port))
      return lines

   def mirror(self, name=None):
      """
      clones the node in a version where all provide and require ports are reversed
      """
      if name is None:
         name = self.name
      mirror = Node(name)
      mirror.dataTypes = deepcopy(self.dataTypes)
      mirror.requirePorts = [port.mirror() for port in self.providePorts]
      mirror.providePorts = [port.mirror() for port in self.requirePorts]
      for dataType in mirror.dataTypes:
         mirror.dataTypeMap[dataType.name]=dataType
      mirror.resolve_types()
      return mirror

   def add_port_from_node(self, from_node, from_port):
      """
      Attempts to clone the port from the other node, including all its data types
      """

      if not isinstance(from_node, apx.Node):
         raise ValueError('from_node argument must be of type apx.Node')
      if not isinstance(from_port, apx.Port):
         raise ValueError('from_node argument must derive from type apx.Port')

      to_port = from_port.clone()
      from_data_element = from_port.dsg.dataElement
      if from_data_element.typeCode == apx.REFERENCE_TYPE_CODE:
         from_data_type = from_data_element.typeReference
         if not isinstance(from_data_type, apx.base.DataType):
            raise RunTimeError('Node.finalize() method must be called before this method can be used')
         to_data_type  = self.find(from_data_type.name)
         if to_data_type is None:
            self.add_data_type_from_node(from_node, from_data_type)
      self.append(to_port)
      return to_port


   def add_data_type_from_node(self, from_node, from_data_type):
      """
      Attempts to clone the data type from other node to this node
      """
      if not isinstance(from_node, apx.Node):
         raise ValueError('from_node argument must be of type apx.Node')

      if not isinstance(from_data_type, apx.DataType):
         raise ValueError('from_data_type argument must be of type apx.DataType')
      from_data_element = from_data_type.dsg.dataElement
      if (from_data_element.typeCode >= apx.UINT8_TYPE_CODE) and (from_data_element.typeCode < apx.RECORD_TYPE_CODE):
         pass #no further action needed
      elif (from_data_element.typeCode == apx.RECORD_TYPE_CODE):
         for elem in from_data_element.elements:
            if elem.typeCode == apx.REFERENCE_TYPE_CODE:
               self.add_data_type_from_node(from_node, elem.typeReference)
      else:
         raise NotImplementedError(from_data_element.typeCode)

      to_data_type = from_data_type.clone()
      self.append(to_data_type)
      return to_data_type


   def find(self, name):
      """
      Finds type or port by name.
      If the variable name is a list, it finds multiple items
      """
      if isinstance(name, list):
         result = []
         for inner_name in name:
            result.append(self._inner_find(inner_name))
         return result
      else:
         return self._inner_find(name)

   def _inner_find(self, name):
      """
      finds type or port by name (internal implementation)
      """
      for elem in self.dataTypes+self.requirePorts+self.providePorts:
         if elem.name == name:
            return elem

   def resolve_types(self):
      """
      Resolves all integer and string type references with their actual object counter-parts
      """
      for port in self.requirePorts+self.providePorts:
         if port.dsg.dataElement.isReference:
            port.resolve_type(self.dataTypes)

   def finalize(self):
      if not self.isFinalized:
         self.resolve_types()
         self.isFinalized = True

