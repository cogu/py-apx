import remotefile
import threading
import abc
import sys

class NodeDataHandler(metaclass=abc.ABCMeta):
   @abc.abstractmethod
   def inPortDataWriteNotify(self, file, write_offset : int, write_len : int):
      """
      Notification called when inPortDataFile has been written to (from ApxFileManager)
      """
   @abc.abstractmethod
   def inPortDataOpen(self, file):
      """
      Called when APX server has requested to open the nodes input file
      """


class File(remotefile.File):
   """
   This is the apx.File class. It inherits from remotefile.File.
   
   In the C implementation this type is called apx_file_t.
   """
   def __init__(self, name, length, init_data=None):
      super().__init__(name, length)
      self.data = bytearray(length)
      self.dataLock = threading.Lock()
      self.fileManager = None
      if init_data is not None:
         if len(init_data) != length:
            raise ValueError('Length of init_data must be equal to length argument')         
         self.data[0:length]=init_data

   def read(self, offset: int, length: int):
      """
      reads data from the given offset, returns bytes array or None in case of error
      """
      if(offset < 0) or (offset+length>len(self.data) ):
         print('file read outside file boundary detected, file=%s, off=%d, len=%d'%(self.name, offset, len(self.data)),file=sys.stderr)
         return None
      self.dataLock.acquire()
      retval = bytes(self.data[offset:offset+length])
      self.dataLock.release()
      return retval
      
   
   def write(self, offset: int, data: bytes):
      """
      writes data at the given offset in the file
      returns number of bytes written or -1 on error
      """
      if(offset < 0) or (offset+len(data)>len(self.data) ):
         print('file write outside file boundary detected, file=%s, off=%d, len=%d'%(self.name, offset, len(data)),file=sys.stderr)
         return -1
      self.dataLock.acquire()
      self.data[offset:offset+len(data)]=data
      self.dataLock.release()
      return len(data)
      

class InputFile(File):
   """
   An APX input file. when written to, it notifies the upper layer (NodeDataHandler) about the change
   """
   def __init__(self, name, length, init_data=None):
      super().__init__(name, length, init_data)
      self.nodeDataHandler=None
   
   def write(self, offset: int, data: bytes, more_bit : bool = False):
      retval = super().write(offset, data)      
      if (retval>=0) and (more_bit == False):
         if self.nodeDataHandler is not None:
            self.nodeDataHandler.inPortDataWriteNotify(self, offset, len(data))
      return retval
         

class OutputFile(File):
   """
   An APX output file. when written to, it notifies the lower layer (FileManager) about the change
   """
   def __init__(self, name, length, init_data=None):
      super().__init__(name, length, init_data)
            
   def write(self, offset: int, data: bytes):
      retval = super().write(offset, data)
      if (retval >=0) and (self.fileManager is not None) and (self.isOpen==True):
         self.fileManager.outPortDataWriteNotify(self, offset, len(data))
      return retval
      