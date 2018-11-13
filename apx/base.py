import autosar
import math
import re
import sys
import copy

INVALID_TYPE_CODE = -1
UINT8_TYPE_CODE = 0
UINT16_TYPE_CODE = 1
UINT32_TYPE_CODE = 2
UINT64_TYPE_CODE = 3
SINT8_TYPE_CODE = 4
SINT16_TYPE_CODE = 5
SINT32_TYPE_CODE = 6
SINT64_TYPE_CODE = 7
STRING_TYPE_CODE = 8
RECORD_TYPE_CODE = 9
REFERENCE_TYPE_CODE = 10

VTYPE_INVALID = -1
VTYPE_SCALAR = 0
VTYPE_LIST = 1
VTYPE_MAP = 2

MAX_RECURSE_DEPTH = 10

def match_pair(s,left,right):
   if (len(s)>0) and (s[0]==left):
      count=1
      for i in range(1,len(s)):
         if s[i]==right:
            count-=1
            if count==0:
               return (s[1:i],s[i+1:])
         elif s[i]==left:
            count+=1 #nested pair
      return (None,"")
   return (None,s)

def parse_str(s):
   return match_pair(s,'"','"')

def _getIntegerTypeCode(dataType):
   """
   using an autosar integer datatype, calculate how many bits are required
   to store its value and based on that, calculate what APX type code to use.
   """
   global args
   if dataType.minVal >= 0:
      bits = _calcUIntTypeLen(dataType)
      if bits <=8:
         if (dataType.minVal>0) or (dataType.maxVal<255):
            return 'C(%d,%d)'%(dataType.minVal,dataType.maxVal)
         else:
            return 'C'
      elif bits <=16:
         return 'S'
      elif bits <=32:
         return 'L'
      elif bits <=64:
         return 'U'
   elif dataType.minVal<0:
      bits = _calcIntTypeLen(dataType)
      if bits <=8:
         if (dataType.minval>-128) or dataType.maxVal<127:
            return 'c(%d,%d)'%(dataType.minval,dataType.maxVal)
         else:
            return 'c'
      elif bits <=16:
         return 's'
      elif bits <=32:
         return 'l'
      elif bits <=64:
         return 'u'
   else:
      print("not implemented (min=%s)"%dataType.minval)

def _calcUIntTypeLen(dataType):
   """
   returs number of bits needed to represent the autosar integer
   type value.
   """
   if isinstance(dataType,autosar.datatype.IntegerDataType):
      return int(math.ceil(math.log(dataType.maxVal,2)))
   return None

def _calcIntTypeLen(dataType):
   """
   same as _calcUIntTypeLen but for signed integers
   """
   if isinstance(dataType,autosar.datatype.IntegerDataType):
      return int(math.ceil(math.log(abs(dataType.maxVal),2)))+1
   return None

def _derive_c_typename(dataElement):
   """
   returns the C typename for simple data types
   """
   if   dataElement.typeCode == UINT8_TYPE_CODE: retval = 'uint8'
   elif dataElement.typeCode == UINT16_TYPE_CODE: retval = 'uint16'
   elif dataElement.typeCode == UINT32_TYPE_CODE: retval = 'uint32'
   elif dataElement.typeCode == SINT8_TYPE_CODE: retval = 'sint8'
   elif dataElement.typeCode == SINT16_TYPE_CODE: retval = 'sint16'
   elif dataElement.typeCode == SINT32_TYPE_CODE: retval = 'sint32'
   elif dataElement.typeCode == STRING_TYPE_CODE: retval = 'uint8'
   else:
      raise NotImplementedError('typeCode={:d}'.format(dataElement.typeCode))
   return retval

def _typeCodeToStr(typeCode):
   mapping = ['C', 'S', 'L', 'U', 'c', 's', 'l', 'u', 'a']
   if (typeCode>=0) and (typeCode <= STRING_TYPE_CODE ):
      return mapping[typeCode]
   else:
      raise ValueError('Invalid typeCode: {:d}'.format(typeCode))

class Port:
   """
   APX port base type
   """
   def __init__(self, portType, name, dataSignature, attributes=None):
      self.portType = portType    #string containing 'P' for provide port or 'R' for require port
      self.name = name            #name of the port
      self.dsg = DataSignature(dataSignature)
      self.attr = PortAttribute(attributes) if attributes is not None else None
      self.id = None

   def __str__(self):
      return self.to_string(False)

   def to_string(self, normalized):
      if self.attr is not None:
         return '%s"%s"%s:%s'%(self.portType, self.name, self.dsg.to_string(normalized), str(self.attr))
      else:
         return '%s"%s"%s'%(self.portType, self.name, self.dsg.to_string(normalized))


   def resolve_type(self, typeList):
      return self.dsg.resolve_data_element(typeList)

   @property
   def data_element(self):
      data_element = self.dsg.dataElement
      if data_element.isReference:
         if isinstance(data_element.typeReference, DataType):
            return data_element.typeReference.dsg.dataElement
         else:
            raise ApxTypeError('Unresolved type reference: {}'.format(str(data_element.typeReference)))
      else:
         return data_element

   @property
   def init_value(self):
      if self.attr is None:
         return None
      else:
         return self.attr.initValue

class RequirePort(Port):
   """
   APX require port
   """
   def __init__(self, name, dataSignature, attributes=None):
      super().__init__('R',name, dataSignature, attributes)

   def mirror(self):
      return ProvidePort(self.name, self.dsg.to_string(normalized=True), str(self.attr) if self.attr is not None else None)

   def clone(self):
      return RequirePort(self.name, self.dsg.to_string(normalized=True), str(self.attr) if self.attr is not None else None)

class ProvidePort(Port):
   """
   APX provide port
   """
   def __init__(self, name, dataSignature, attributes=None):
      super().__init__('P',name, dataSignature, attributes)

   def mirror(self):
      return RequirePort(self.name, str(self.dsg), str(self.attr) if self.attr is not None else None)

   def clone(self):
      return ProvidePort(self.name, str(self.dsg), str(self.attr) if self.attr is not None else None)


class DataType:
   """
   APX datatype
   """
   def __init__(self, name, dataSignature, attributes=None):
      self.name = name
      self.dsg = DataSignature(dataSignature, None, self)
      self.attr = TypeAttribute(attributes) if attributes is not None else None
      self.id = None

   def __str__(self):
      return self.to_string()

   def to_string(self, normalized=False):
      if self.attr is not None:
         return 'T"%s"%s:%s'%(self.name, self.dsg.to_string(normalized), str(self.attr))
      else:
         return 'T"%s"%s'%(self.name, self.dsg.to_string(normalized))

   def clone(self):
      if self.attr is not None:
         return DataType(self.name, self.dsg.to_string(normalized=True), str(self.attr) )
      else:
         return DataType(self.name, self.dsg.to_string(normalized=True) )

   @property
   def dataElement(self):
      return self.dsg.dataElement

class DataSignature:
   """
   APX Datasignature
   """
   def __init__(self, dsg, typeList=None, parent=None):
      if isinstance(dsg, str):
         (dataElement,remain)=DataSignature.parseDataSignature(dsg, typeList)
         if len(remain)>0:
            raise ParseError("string '%s' not fully parsed"%dsg)
         assert(isinstance(dataElement, DataElement))
         self.dataElement=dataElement
      elif isinstance(dsg, DataElement):
         self.dataElement=copy.deepcopy(DataElement)
      else:
         raise NotImplementedError(type(dsg))
      self.parent=parent

   def __str__(self):
      return self.dataElement.to_string()

   def to_string(self, normalized=False):
      return self.dataElement.to_string(normalized)

   def packLen(self):
      result=0
      stack = []
      i = iter([self.dataElement])

      while True:
         try:
            dataElement = next(i)
         except StopIteration:
            try:
               i = stack.pop()
               continue
            except IndexError:
               break
         if dataElement.typeCode == RECORD_TYPE_CODE:
            stack.append(i)
            i=iter(dataElement.elements)
         else:
            elemSize=self._calcElemSize(dataElement)
            result+=elemSize
      return result

   def _calcElemSize(self, dataElement):
      typeCodes = [UINT8_TYPE_CODE, UINT16_TYPE_CODE, UINT32_TYPE_CODE, UINT64_TYPE_CODE,
                     SINT8_TYPE_CODE, SINT16_TYPE_CODE, SINT32_TYPE_CODE, SINT64_TYPE_CODE,
                     STRING_TYPE_CODE]
      typeSizes = [1, 2, 4, 8, 1, 2, 4, 8, 1]
      if dataElement.typeCode == REFERENCE_TYPE_CODE:
         dataType = dataElement.typeReference
         assert(isinstance(dataType, DataType))
         return self._calcElemSize(dataType.dsg.dataElement)
      elif dataElement.typeCode == RECORD_TYPE_CODE:
         elemSize = 0
         for childElement in dataElement.elements:
            elemSize+=self._calcElemSize(childElement)
      else:
         try:
               i = typeCodes.index(dataElement.typeCode)
         except ValueError:
               raise NotImplementedError(dataElement.typeCode)
         elemSize =  typeSizes[i]

      if dataElement.isArray():
         return elemSize*dataElement.arrayLen
      else:
         return elemSize


   def ctypename(self,typeList=None):
      """
      Returns the C type name of the data signature as a string. This return value can be used for code generation in C/C++ code.
      """
      if self.dataElement.isReference:
         data_type = self.dataElement.typeReference
         assert(isinstance(data_type, DataType))
         return data_type.name
      else:
         return _derive_c_typename(self.dataElement)

   def isComplexType(self, typeList = None):
      return self.dataElement.isComplexType(typeList)

   def isArray(self, typeList = None):
      return self.dataElement.isArray(typeList)

   def createInitData(self, initValue):
      return self.dataElement.createInitData(initValue)

   def resolve_data_element(self, typeList = None):
      return self.dataElement.resolve_type(typeList)

   @staticmethod
   def _parseRecordSignature(remain, typeList):
      recordElement = DataElement.Record()
      while len(remain)>0:
         (name,remain)=match_pair(remain,'"','"')
         if len(remain)>0:
            (childElement,remain)=DataSignature.parseDataSignature(remain, typeList)
            if childElement is None:
               if remain[0] == '}':
                  return (recordElement,remain[1:])
               else:
                  raise ParseError('syntax error while parsing record')
            else:
               assert(isinstance(childElement, DataElement))
               childElement.name = name
               recordElement.elements.append(childElement)
      raise ParseError("Missing '}' in data signature")

   @staticmethod
   def _parseExtendedTypeCode(text):
      values=re.split(r'\s*,\s*',text)
      if len(values)<2:
         raise Exception("min,max missing from %s"%text)
      minVal = int(values[0])
      maxVal = int(values[1])
      return (minVal, maxVal)


   @staticmethod
   def parseDataSignature(s, typeList=None):
      remain=s
      c=remain[0]
      if c=='{': #start of record
         remain = remain[1:]
         return DataSignature._parseRecordSignature(remain,typeList)
      if c=='T': #typeRef
         (data,remain2)=match_pair(remain[1:],'[',']')
         if data is not None:
            (data2,remain3)=match_pair(data,r'"',r'"')
            if data2 is not None:
               assert(len(remain3)==0)
               dataType = DataSignature._get_type_by_name(typeList, data2)
               return DataElement.TypeReference(dataType), remain2
            else:
               dataType = DataSignature._get_type_by_id(typeList, int(data))
               return DataElement.TypeReference(dataType), remain2
         else:
               raise ParseError("Parse failure near '%s', unmatched '[]' pair "%remain[1:])
      else:
         typeCodesChar=['C','S','L','U','c','s','l','u','a']
         typeCodeInt = [UINT8_TYPE_CODE, UINT16_TYPE_CODE, UINT32_TYPE_CODE, UINT64_TYPE_CODE,
                     SINT8_TYPE_CODE, SINT16_TYPE_CODE, SINT32_TYPE_CODE, SINT64_TYPE_CODE,
                     STRING_TYPE_CODE]
         
         try:
            i = typeCodesChar.index(c)
         except ValueError:
            return (None,remain)
         remain=remain[1:]
         if (len(remain)>0) and (remain[0]=='('):
               (data,remain)=match_pair(remain[0:],'(',')')
               if data is None:
                  raise ParseError("Expecting ')' near: "+remain)
               (minVal,maxVal) = DataSignature._parseExtendedTypeCode(data)
         else:
            (minVal,maxVal) = (None, None)            
         if (len(remain)>0) and (remain[0]=='['):
               (value,remain)=match_pair(remain[0:],'[',']')
               if value is None:
                  raise ParseError("Expecting ']' near: "+remain)
               arrayLen=int(value)
         else:
            arrayLen = None
         dataElement = DataElement(None, typeCodeInt[i], minVal, maxVal, arrayLen)
         return (dataElement, remain)

   @staticmethod
   def _get_type_by_id(typeList, i):
      if typeList is None:
         return i
      if i<len(typeList):
         return typeList[i]
      else:
         raise ValueError('Invalid type id: {:d}'.format(i))

   @staticmethod
   def _get_type_by_name(typeList, name):
      if typeList is None:
         return name
      for dataType in typeList:
         if dataType.name == name:
            return dataType
      else:
         raise ValueError('No data type found with name {}'.format(name))




class DataElement:
   """
   This class describes the type of data that is contained in a data signature. A data signature contains one data element.
   """
   def __init__(self, name=None, typeCode = INVALID_TYPE_CODE, minVal = None, maxVal = None, arrayLen = None, elements = None, reference=None):
      self.name = name
      self.typeMinVal = None
      self.typeMaxVal = None

      self.strNullTerminator = True #TODO: make this configurable in the future
      typeCodeInt = [UINT8_TYPE_CODE, UINT16_TYPE_CODE, UINT32_TYPE_CODE, UINT64_TYPE_CODE,
                     SINT8_TYPE_CODE, SINT16_TYPE_CODE, SINT32_TYPE_CODE, SINT64_TYPE_CODE,
                     STRING_TYPE_CODE]
      typeMinVal = [0, 0, 0, 0,
                     -128, -32768, -2147483648, None, #python has issues with 64-bit integer literals, ignore for now
                     0]
      typeMaxVal = [255, 65535, 0xFFFFFFFF, None, #python has issues with 64-bit integer literals, ignore for now
                     127, 32767, 2147483647, None,                     
                     255]
      if reference is not None:
         self.typeCode = REFERENCE_TYPE_CODE
         assert(isinstance(reference, (int, str, DataType)))
         self.typeReference = reference
         self.minVal = None
         self.maxVal = None
         self.arrayLen = None
      else:
         self.typeCode = typeCode
         self.minVal = minVal
         self.maxVal = maxVal
         if typeCode < RECORD_TYPE_CODE:         
            self.typeMinVal = typeMinVal[typeCode] #this can be used in case user hasn't specifically set self.minVal
            self.typeMaxVal = typeMaxVal[typeCode] #this can be used in case user hasn't specifically set self.maxVal         
         self.arrayLen = arrayLen
         self.typeReference = None


      if elements is not None:
         self.elements = list(elements)
      else:
         self.elements = None

   @property
   def arrayLen(self):
      return self._arrayLen

   @arrayLen.setter
   def arrayLen(self, value):
      if value is not None:
         if value < 0:
            raise ValueError('invalid length: %s'%value)
         self._arrayLen = value
      else:
          self._arrayLen = None

   def isArray(self, typeList = None):
      dataElement = self.resolve_data_element()
      return dataElement.arrayLen is not None

   def isRecord(self, typeList = None):
      dataElement = self.resolve_data_element()
      return dataElement.typeCode == RECORD_TYPE_CODE

   def isComplexType(self, typeList = None):
      return self.isArray() or self.isRecord()

   @property
   def isReference(self):
      return self.typeCode == REFERENCE_TYPE_CODE
   
   @property
   def minValWithDefault(self):
      if self.minVal is not None:
         return self.minVal
      return self.typeMinVal

   @property
   def maxValWithDefault(self):
      if self.maxVal is not None:
         return self.maxVal
      return self.typeMaxVal

   def to_string(self, normalized = False):
      retval = None
      if (self.typeCode >= UINT8_TYPE_CODE) and (self.typeCode <= STRING_TYPE_CODE):
         retval = _typeCodeToStr(self.typeCode)
      elif self.typeCode == RECORD_TYPE_CODE:
         retval = '{'
         for elem in self.elements:
            retval+='"{}"{}'.format(elem.name, elem.to_string(normalized))
         retval += '}'
      elif (self.typeCode == REFERENCE_TYPE_CODE):
         if isinstance(self.typeReference, DataType):
            referencedType = self.typeReference
            if not normalized and referencedType.id is not None:
               return 'T[{:d}]'.format(referencedType.id)
            return 'T["{}"]'.format(referencedType.name)
         elif isinstance(self.typeReference, str):
            return 'T["{}"]'.format(self.typeReference)
         else:
            raise RuntimeError('to_string called on non-final object, try calling finalize() on the apx.Node object')
      else:
         raise NotImplementedError(self.typeCode)
      if (self.minVal is not None) and (self.maxVal is not None):
         retval += "({:d},{:d})".format(self.minVal, self.maxVal)
      if self.arrayLen is not None:
         retval += "[{:d}]".format(self.arrayLen)
      return retval


   @classmethod
   def UInt8(cls, name=None, minVal = None, maxVal = None, arrayLen = None):
      return cls(name, UINT8_TYPE_CODE, minVal, maxVal, arrayLen)

   @classmethod
   def UInt16(cls, name=None, minVal = None, maxVal = None, arrayLen = None):
      return cls(name, UINT16_TYPE_CODE, minVal, maxVal, arrayLen)

   @classmethod
   def UInt32(cls, name=None, minVal = None, maxVal = None, arrayLen = None):
      return cls(name, UINT32_TYPE_CODE, minVal, maxVal, arrayLen)

   @classmethod
   def String(cls, name=None, arrayLen = None):
      return cls(name, STRING_TYPE_CODE, None, None, arrayLen)

   @classmethod
   def SInt8(cls, name=None, minVal = None, maxVal = None, arrayLen = None):
      return cls(name, SINT8_TYPE_CODE, minVal, maxVal, arrayLen)

   @classmethod
   def SInt16(cls, name=None, minVal = None, maxVal = None, arrayLen = None):
      return cls(name, SINT16_TYPE_CODE, minVal, maxVal, arrayLen)

   @classmethod
   def SInt32(cls, name=None, minVal = None, maxVal = None, arrayLen = None):
      return cls(name, SINT32_TYPE_CODE, minVal, maxVal, arrayLen)

   @classmethod
   def Record(cls, name=None, elements = None):
      self = cls(name, RECORD_TYPE_CODE)
      if elements is not None:
         self.elements = list(elements)
      else:
         self.elements = []
      return self

   @classmethod
   def TypeReference(cls, reference, name=None):
      self = cls(name, reference = reference)
      return self

   def append(self, elem):
      if self.typeCode == RECORD_TYPE_CODE:
         self.elements.append(elem)
      else:
         raise ParseError('DataElement is not a record element')

   def resolve_type(self, typeList):
      """
      Updates internal type references to type objects
      """
      if self.typeCode == REFERENCE_TYPE_CODE:
         if typeList is not None:
            if isinstance(self.typeReference, int):
               obj=typeList[self.typeReference]
            elif isinstance(self.typeReference, str):
               for dataType in typeList:
                  if dataType.name == self.typeReference:
                     obj = dataType
                     break
               else:
                  raise ApxTypeError('No data type found with name "{}"'.format(self.typeReference))
            elif isinstance(self.typeReference, DataType):
               return self.typeReference.dsg.resolve_data_element(typeList)
            else:
               raise NotImplementedError(type(self.typeReference))
            self.typeReference = obj
            return obj
         else:
            raise ValueError('typeList argument must not be None')
      elif self.typeCode == RECORD_TYPE_CODE:
         #TODO: detect circular loops in type-reference lookups to prevent infinite loop
         for element in self.elements:
            element.resolve_type(typeList)
      return self

   def resolve_data_element(self):
      dataElement, count = self,0
      while(count < MAX_RECURSE_DEPTH):
         count+=1
         if dataElement.typeCode == REFERENCE_TYPE_CODE:
            if isinstance(dataElement.typeReference, DataType):
               dataType = dataElement.typeReference
               dataElement = dataType.dsg.dataElement
            else:
               raise ApxTypeError('Unresolved data type: {}'.format(type(dataElement.typeReference)))
         else:
            break
      if (count >= MAX_RECURSE_DEPTH) and dataElement.typeCode == REFERENCE_TYPE_CODE:
         raise RuntimeError('Max recurse depth reached')
      return dataElement

   def createInitData(self, initValue):
      data = bytearray()
      if (self.typeCode == RECORD_TYPE_CODE):
         if (initValue.valueType != VTYPE_LIST):
            raise ValueError('invalid init value type: list expected')
         if len(initValue.elements) != len(self.elements):
            raise ValueError('Incorrect number of record elements in init_value: got %d, expected %s'%(len(initValue.elements), len(self.dataElement.elements)))
         for i,dataElement in enumerate(self.elements):
            data.extend(DataElement._createInitDataInner(dataElement, initValue.elements[i]))
      else:
         data.extend(DataElement._createInitDataInner(self, initValue))
      return data

   @staticmethod
   def _createInitDataInner(dataElement, initValue, is_array_elem=False):
      data = bytearray()
      if (dataElement.typeCode == RECORD_TYPE_CODE):
         if (initValue.valueType != VTYPE_LIST):
            raise ValueError('invalid init value type: list expected')
         if len(initValue.elements) != len(dataElement.elements):
            raise ValueError('Incorrect number of record elements in init_value: got %d, expected %s'%(len(initValue.elements), len(self.dataElement.elements)))
         for i,childElement in enumerate(dataElement.elements):
            data.extend(DataElement._createInitDataInner(childElement, initValue.elements[i]))
      elif (dataElement.typeCode == STRING_TYPE_CODE):
            if not initValue.isString:
               raise ValueError('invalid init value type: expected string')
            if len(initValue.value) > dataElement.arrayLen:
               print('Warning: init value "%s" will be truncated to %d bytes'%(initValue.value, dataElement.arrayLen), file=sys.stderr)
            for i in range(dataElement.arrayLen):
               if i<len(initValue.value):
                  data.append(ord(initValue.value[i]))
               else:
                  data.append(0)
      elif (dataElement.typeCode in [UINT8_TYPE_CODE, UINT16_TYPE_CODE, UINT32_TYPE_CODE, SINT8_TYPE_CODE, SINT16_TYPE_CODE, SINT32_TYPE_CODE]):
         if (dataElement.isArray()) and (not is_array_elem):
            if (initValue.valueType != VTYPE_LIST):
               raise ValueError('invalid init value type: expected list')
            for initElem in initValue.elements:
               data.extend(DataElement._createInitDataInner(dataElement, initElem, True))
         else:
            if initValue.valueType != VTYPE_SCALAR:
               raise ValueError('invalid init value type: got %s, expected integer'%(initValue.value))
            if dataElement.typeCode==UINT8_TYPE_CODE or dataElement.typeCode==SINT8_TYPE_CODE:
               data.append(int(initValue.value) & 0xFF)
            elif dataElement.typeCode==UINT16_TYPE_CODE or dataElement.typeCode==SINT16_TYPE_CODE:
               #TODO: implement big endian support
               data.append(int(initValue.value) & 0xFF)
               data.append(int(initValue.value)>>8 & 0xFF)
            elif dataElement.typeCode==UINT32_TYPE_CODE or dataElement.typeCode==SINT32_TYPE_CODE:
               #TODO: implement big endian support
               data.append(int(initValue.value) & 0xFF)
               data.append(int(initValue.value)>>8 & 0xFF)
               data.append(int(initValue.value)>>16 & 0xFF)
               data.append(int(initValue.value)>>24 & 0xFF)
            else:
               raise NotImplementedError(dataElement.typeCode)
      elif dataElement.typeCode == REFERENCE_TYPE_CODE:
         dataType = dataElement.typeReference
         assert(isinstance(dataType, DataType))
         return DataElement._createInitDataInner(dataType.dsg.dataElement, initValue, is_array_elem)
      else:
         raise NotImplementedError(dataElement.typeCode)
      return data

class InitValue:
   def __init__(self, valueType, value = None):
      self.valueType = valueType
      self.value = value
      if valueType == VTYPE_LIST:
         self.elements = []
      else:
         self.elements = None
   @property
   def isString(self):
      return isinstance(self.value, str)

   @classmethod
   def Int(cls, value):
      return cls(VTYPE_SCALAR, int(value))

   @classmethod
   def String(cls, value):
      return cls(VTYPE_SCALAR, str(value))

   @classmethod
   def List(cls):
      return cls(VTYPE_LIST)


class PortAttribute:
   """
   Port attributes are attributes declared on a line starting with either 'R' or 'P'
   """
   _p2=re.compile(r'0x([0-9A-Fa-f]+)|(-?\d+)|"([^"]*)"')
   _p3=re.compile(r'\[(\d+)\]')

   def __init__(self,text):
      self.isQueued=False
      self.isParameter=False
      self.queueLength=None
      self.initValue=None
      self.str = str(text)
      if text==None or len(text)==0:
         return
      remain=text
      while len(remain)>0:
         remain=remain.lstrip()
         if remain.startswith('='):
            remain=remain[1:]
            (initValue,remain)=self._parseInitValue(remain)
            self.initValue=initValue
         elif remain.startswith('Q'):
            self.isQueued=True
            remain=remain[1:]
            m=PortAttribute._p3.match(remain)
            if m:
               self.queueLength=m.group(1)
               remain=remain[m.end():]
            break
         elif remain.startswith('P'):
            self.isParameter=True
            remain=remain[1:]
         else:
            raise ParseError(text)

   def __str__(self):
      return self.str

   def _parseInitValue(self,remain):
      remain=remain.lstrip()
      if remain.startswith('{'):
         (match,remain2)=match_pair(remain,'{','}')
         initValue = InitValue.List()
         while len(match)>0:
            match=match.lstrip()
            (elem,match)=self._parseInitValue(match)
            initValue.elements.append(elem)
            match=match.lstrip()
            if match.startswith(','):
               match=match[1:]
               match=match.lstrip()
            elif len(match)==0:
               return (initValue,remain2)
            else:
               raise ParseError
      else:
         m=PortAttribute._p2.match(remain)
         if m:
            remain=remain[m.end():]
            if m.group(1) is not None:
               return (InitValue.Int(int(m.group(1),16)),remain)
            elif m.group(2) is not None:
               return (InitValue.Int(int(m.group(2),10)),remain)
            elif m.group(3) is not None:
               return (InitValue.String(m.group(3)),remain)
      return (None,remain)

class TypeAttribute:
   """
   Type attributes are attributes declared on a line starting with letter 'T'
   """
   def __init__(self,text):
      self.valueTable = None
      self.str=str(text)
      if text==None or len(text)==0:
         return
      remain = text
      while len(remain)>0:
         if remain.startswith('VT('):
            (result,remain) = match_pair(remain[2:],'(',')')
            if result == None:
               raise ParseError
            else:
               self.valueTable = []
               strings = result.split(',')
               for string in strings:
                  (name,remain2)=parse_str(string)
                  self.valueTable.append(name)
         else:
            raise ParseError
    
   def __str__(self):
      return self.str


class AutosarPort:
   """
   An AUTOSAR port (base type)
   """
   def __init__(self,name,typeId):
      self.name = name
      self.typeId = typeId

class AutosarRequirePort(AutosarPort):
   def __init__(self, name, typeId, ws=None, port=None):
      super().__init__(name,typeId)
      if (ws is not None) and (port is not None):
         self.attr = self._calcAttribute(ws,port)

   def __str__(self):
      if self.attr is not None:
         return 'R"%s"T[%d]:%s'%(self.name,self.typeId,self.attr)
      else:
         return 'R"%s"T[%d]'%(self.name,self.typeId)

   def mirror(self):
      other = AutosarProvidePort(self.name, self.typeId)
      other.attr = self.attr
      return other

class AutosarProvidePort(AutosarPort):
   def __init__(self, name, typeId, ws=None, port=None):
      super().__init__(name,typeId)
      if (ws is not None) and (port is not None):
         self.attr = self._calcAttribute(ws,port)

   def __str__(self):
      if self.attr is not None:
         return 'P"%s"T[%d]:%s'%(self.name,self.typeId,self.attr)
      else:
         return 'P"%s"T[%d]'%(self.name,self.typeId)

   def mirror(self):
      other = AutosarRequirePort(self.name, self.typeId)
      other.attr = self.attr
      return other

class AutosarDataType(DataType):
   def __init__(self, ws, dataType, parent = None):
      self.name=dataType.name
      self.dsg=DataSignature(self._calcDataSignature(ws,dataType), parent)
      typeSemantics = ws.find('/DataType/DataTypeSemantics/%s'%dataType.name)
      if typeSemantics is not None:
         self.attr = self._calcAttribute(dataType,typeSemantics)
      else:
         self.attr=None

   def __str__(self):
      if self.attr is not None:
         return 'T"%s"%s:%s'%(self.name,self.dsg,self.attr)
      else:
         return 'T"%s"%s'%(self.name,self.dsg)

   def _calcAttribute(self,dataType,typeSemantics):
      if isinstance(typeSemantics,autosar.datatype.CompuMethodConst):
         values=[]
         for elem in typeSemantics.elements:
            assert(isinstance(elem,autosar.datatype.CompuConstElement))
            if elem.lowerLimit==elem.upperLimit:
               values.append(elem.textValue)
            else:
               num_items = (elem.upperLimit+1)-elem.lowerLimit               
               values.extend([elem.textValue+str(i) for i in range(1, num_items+1)])
         v=','.join(['"%s"'%x for x in values])
         return "VT(%s)"%v
      return None

   def _calcDataSignature(self,ws,dataType):
      if isinstance(dataType,autosar.datatype.BooleanDataType):
         return 'C(0,1)'
      if isinstance(dataType,autosar.datatype.IntegerDataType):
         return _getIntegerTypeCode(dataType)
      elif isinstance(dataType,autosar.datatype.ArrayDataType):
         typeCode = _getIntegerTypeCode(typeData.find(dataType['typeRef']))
         if typeCode != None:
            return "%s[%d]"%(typeCode,int(dataType.length))
         else:
            raise Exception("unsupported type: %s"%typeData.find(dataType['typeRef']))
      elif isinstance(dataType,autosar.datatype.StringDataType):
         typeCode = 'a'
         if typeCode != None:
            return "%s[%d]"%(typeCode,int(dataType.length)+1)
      elif isinstance(dataType,autosar.datatype.RecordDataType):
         result="{"
         for elem in dataType.elements:
            #remove _RE from end of element names
            if elem.name.endswith('_RE'):
               elem.name=elem.name[:-3]
            childType = ws.find(elem.typeRef, role="DataType")
            if childType is None:
               raise ValueError("invalid type reference: %s"%elem.typeRef)
            result+='"%s"%s'%(elem.name, self._calcDataSignature(ws, childType))
         result+="}"
         return result
      else: raise Exception('unhandled data type: %s'%type(dataType))
      return ""

class ParseError(RuntimeError):
   pass

class ApxTypeError(RuntimeError):
   pass

