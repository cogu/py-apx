import apx
import abc
import struct
from collections import namedtuple
import threading

PortMapRange = namedtuple('PortMapRange', "data_offset data_len port")

class NodeDataClient(metaclass=abc.ABCMeta):
   @abc.abstractmethod
   def on_require_port_data(self, port, value):
      """
      called by apx.NodeData when a require port has updated its data
      """


@apx.NodeDataHandler.register
class NodeData():
   """
   APX NodeData class
   """

   def __init__(self,node):
      if isinstance(node, apx.Node):
          self.node=node
          context=apx.Context()
          context.append(node)
          apx_text=context.dumps()
      elif isinstance(node, str):
         parser = apx.Parser()
         apx_text=node
         self.node = parser.loads(apx_text)
      else:
         raise NotImplementedError(type(node))

      compiler = apx.compiler.Compiler()
      self.name=self.node.name
      self.inPortByteMap = [] #length: length of self.inPortDataFile
      self.inPortDataMap = [] #length: number of require ports
      self.outPortDataMap = [] #length: number of provide ports
      self.inPortPrograms = [] #length: number of require ports
      self.outPortPrograms = [] #length: number of provide ports
      self.outPortValues = [] #length: number of provide ports
      self.inPortDataFile = self._createInPortDataFile(self.node, compiler) if len(self.node.requirePorts)>0 else None
      self.outPortDataFile = self._createOutPortDataFile(self.node, compiler) if len(self.node.providePorts)>0 else None
      self.definitionFile = self._createDefinitionFile(node.name,apx_text)
      self.vm = apx.VM()
      self.lock=threading.Lock() #the virtual machine is not thread-safe, use this lock to protect it in case users try to read/write ports from multiple threads
      if self.inPortDataFile is not None:
         self.inPortDataFile.nodeDataHandler=self
      self.nodeDataClient=None

   def _createInPortDataFile(self, node, compiler):
      offset=0
      init_data = bytearray()
      for port in node.requirePorts:
         assert(port.id is not None)
         dataElement = port.dsg.resolve_data_element(node.dataTypes)
         packLen = port.dsg.packLen()
         self.mapInPort(port, offset, packLen)
         self.createUnpackProg(port, dataElement, compiler)
         offset+=packLen
         if port.attr is not None and port.attr.initValue is not None:
            init_data.extend(dataElement.createInitData(port.attr.initValue))
         else:
            init_data.extend(bytes(packLen)) #initialize with zeros if no init value has been selected
      file_len=offset
      assert(len(init_data)==file_len)
      if file_len > 0:
         file = apx.InputFile(node.name+'.in', file_len, init_data)
         return file
      return None

   def _createOutPortDataFile(self, node, compiler):
      offset=0
      init_data = bytearray()
      for port in node.providePorts:
         dataElement = port.dsg.resolve_data_element(node.dataTypes)
         packLen = port.dsg.packLen()
         self.mapOutPort(port, offset, packLen)
         self.createPackProg(port, dataElement, compiler)
         self.createOutPortValue(port)
         offset+=packLen
         if port.attr is not None and port.attr.initValue is not None:
            init_data.extend(dataElement.createInitData(port.attr.initValue))
         else:
            init_data.extend(bytes(packLen)) #initialize with zeros if no init value has been selected
      file_len=offset
      assert(len(init_data)==file_len)
      if file_len > 0:
         file = apx.OutputFile(node.name+'.out', file_len, init_data)
         return file
      return None


   def _createDefinitionFile(self, node_name, apx_text):
      apx_text_size = len(apx_text.encode('utf-8'))
      file = apx.OutputFile(node_name+'.apx', length=apx_text_size)
      file.write(0,bytes(apx_text, encoding='utf-8'))
      return file

   def inPortDataWriteNotify(self, file, write_offset: int, write_len : int):
      """
      Called by FileManager when it receives a remote write in the node's inPortData file
      """
      if self.nodeDataClient is not None:
         for (port, data_offset, data_len) in self.byte_to_port(write_offset, write_len):
            value = self._unpackRequirePort(port.id, data_offset, data_len)
            self.nodeDataClient.on_require_port_data(port, value)

   def notify_all_require_port_data(self):
      if self.nodeDataClient is not None and self.inPortDataFile is not None:
         file_len = len(self.inPortByteMap)
         if file_len > 0:
            for (port, data_offset, data_len) in self.byte_to_port(0, file_len - 1):
               value = self._unpackRequirePort(port.id, data_offset, data_len)
               self.nodeDataClient.on_require_port_data(port, value)

   def byte_to_port(self, start_offset, data_len):
      """
      Returns an iterator which yields a sequence of ports triggered by the data update
      """
      data_offset = start_offset
      end_offset = start_offset+data_len
      file_len = len(self.inPortByteMap)
      if start_offset > file_len:
         raise ValueError('start_offset ({:d}) is beyond length of file ({:d})'.format(start_offset, file_len))
      if end_offset > file_len:
         raise ValueError('end_offset ({:d}) is beyond length of file ({:d})'.format(end_offset, file_len))
      while data_offset < end_offset:
         port = self.inPortByteMap[data_offset]
         mapping = self.inPortDataMap[port.id]
         assert(mapping.port is port)
         next_offset = mapping.data_offset+mapping.data_len
         yield port,mapping.data_offset,mapping.data_len
         data_offset=next_offset


   def write_provide_port(self, port_id, value):
      if isinstance(port_id, apx.Port):
         port_id = port_id.id
      if not isinstance(port_id, int):
         raise ValueError('port_id must be integer')
      port_map = self.outPortDataMap[port_id]
      assert(port_id == port_map.port.id)
      return self._packProvidePort(port_id, port_map.data_offset, port_map.data_len, value)

   def read_provide_port(self, port_id):
      if isinstance(port_id, apx.Port):
         port_id = port_id.id
      if not isinstance(port_id, int):
         raise ValueError('port_id must be integer')
      port_map = self.outPortDataMap[port_id]
      assert(port_id == port_map.port.id)
      return self.outPortValues[port_id]

   def _packProvidePort(self, port_id, data_offset, data_len, value):
      program = self.outPortPrograms[port_id]
      data = bytearray(data_len)
      self.lock.acquire()
      try:
         self.vm.exec_pack_prog(program, data, 0, value)
         self.outPortValues[port_id]=value
      finally:
         self.lock.release()
      self.outPortDataFile.write(data_offset, data)

   def read_require_port(self, port_id):
      if isinstance(port_id, apx.Port):
         port_id = port_id.id
      if not isinstance(port_id, int):
         raise ValueError('port_id must be integer')
      port_map = self.inPortDataMap[port_id]
      assert(port_id == port_map.port.id)
      return self._unpackRequirePort(port_id, port_map.data_offset, port_map.data_len)

   def _unpackRequirePort(self, port_id, data_offset, data_len):
      program = self.inPortPrograms[port_id]
      data=self.inPortDataFile.read(data_offset, data_len)
      if data is None:
         raise RuntimeError('Failed to read data at offset={:d}, len={:d}'.format(data_offset, data_len))
      self.lock.acquire()
      try:
         self.vm.exec_unpack_prog(program, data, 0)
         value = self.vm.value
      finally:
         self.lock.release()
      return value

   def mapInPort(self, port, start_offset, data_len):
      elem = PortMapRange(start_offset, data_len, port)
      self.inPortDataMap.append(elem)
      for i in range(data_len):
         self.inPortByteMap.append(port)

   def mapOutPort(self, port, start_offset, data_len):
      elem = PortMapRange(start_offset, data_len, port)
      self.outPortDataMap.append(elem)

   def createPackProg(self, port, dataElement, compiler):
      assert(isinstance(dataElement, apx.DataElement))
      program = compiler.compilePackProg(dataElement)
      if len(self.outPortPrograms) != port.id:
         raise RuntimeError('port id {:d} of port {} is out of sync'.format(port.id, port.name))
      self.outPortPrograms.append(program)

   def createUnpackProg(self, port, dataElement, compiler):
      program = compiler.compileUnpackProg(dataElement)
      if len(self.inPortPrograms) != port.id:
         raise RuntimeError('port id {:d} of port {} is out of sync'.format(port.id, port.name))
      self.inPortPrograms.append(program)

   def createOutPortValue(self, port):
      #TODO: add implementation for record types
      if port.attr is not None and port.attr.initValue is not None:
         self.outPortValues.append(port.attr.initValue)
      else:
         self.outPortValues.append(0)
