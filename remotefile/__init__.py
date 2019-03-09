import sys
import struct
import abc
import queue
import threading


# constants

RMF_CMD_START_ADDR = 0x3FFFFC00

RMF_FILE_TYPE_FIXED     = 0
RMF_FILE_TYPE_DYNAMIC   = 1
RMF_FILE_TYPE_STREAM    = 2

RMF_CMD_ACK             = 0  # reserved for future use
RMF_CMD_NACK            = 1  # reserved for future use
RMF_CMD_EOT             = 2  # reserved for future use
RMF_CMD_FILE_INFO       = 3
RMF_CMD_FILE_OPEN       = 10
RMF_CMD_FILE_CLOSE      = 11

RMF_DIGEST_TYPE_NONE    = 0

RMF_MSG_CONNECT         = 0
RMF_MSG_FILEINFO        = 1
RMF_MSG_FILEOPEN        = 2
RMF_MSG_FILECLOSE       = 3
RMF_MSG_WRITE_DATA      = 4

RMF_FILEINFO_BASE_LEN   = 48

RMF_MORE_BIT_MASK       = 0x40
RMF_HIGH_BIT_MASK       = 0x80
RMF_ADDR_BIT_MASK       = 0x3F


def unpackHeader(data):
    """
    Returns tuple (bytes_parsed, address, more_bit)
    """
    i = 0
    bytes_parsed = 0
    more_bit = False
    address = None
    if((i+1) < len(data)):  # parse 16-bits
        b1, b2 = data[i:i+2]
        i += 2
        if b1 & RMF_MORE_BIT_MASK:
            more_bit = True
        if b1 & RMF_HIGH_BIT_MASK:
            # Parse next 16 bits to form a full 30-bit address
            b1 &= RMF_ADDR_BIT_MASK
            if (i+2) < len(data):
                b3, b4 = data[i:i+2]
                i += 2
                address = (b1 << 24) | (b2 << 16) | (b3 << 8) | b4
        else:
            # parse 2 or 3 bytes as header depending on mode
            b1 &= RMF_ADDR_BIT_MASK
            address = (b1 << 8) | (b2)
        if address is not None:
            bytes_parsed = i
    return (bytes_parsed, address, more_bit)


def packHeader(address, more_bit=False):
    """
    packs address and more_bit into bytearray

    returns bytes
    """
    if address < 16384:
        # address will fit into 16 bits
        b1, b2 = (address >> 8) & RMF_ADDR_BIT_MASK, address & 0xFF
        if more_bit:
            b1 |= RMF_MORE_BIT_MASK
        return bytes([b1, b2])
    elif address < 1073741824:
        b1, b2 = (address >> 24) & RMF_ADDR_BIT_MASK, (address >> 16) & 0xFF
        b3, b4 = (address >> 8) & 0xFF, address & 0xFF
        if more_bit:
            b1 |= RMF_MORE_BIT_MASK
        return bytes([b1 | RMF_HIGH_BIT_MASK, b2, b3, b4])
    else:
        raise ValueError('address must be less than 1073741824')


def packFileInfo(file, byte_order='<'):
    """
    packs FileInfo object into bytearray b
    """
    if file.address is None:
        raise ValueError('FileInfo object does not have an address')
    if (byte_order != '<') and (byte_order != '>'):
        raise ValueError('unknown byte_order: '+str(byte_order))
    fmt = '%s3I2H32s%ds' % (byte_order, len(file.name))
    return struct.pack(fmt, RMF_CMD_FILE_INFO, file.address,
                       file.length, file.fileType, file.digestType,
                       file.digestData, bytes(file.name, encoding='ascii'))


def unpackFileInfo(data, byte_order='<'):
    """
    unpacks FileInfo object from bytearray b
    """
    if (byte_order != '<') and (byte_order != '>'):
        raise ValueError('unknown byte_order: '+str(byte_order))
    fmt = '%s3I2H32s' % (byte_order)
    assert(RMF_FILEINFO_BASE_LEN == RMF_FILEINFO_BASE_LEN)
    if len(data) >= RMF_FILEINFO_BASE_LEN:
        part1 = data[0:RMF_FILEINFO_BASE_LEN]
        part2 = data[RMF_FILEINFO_BASE_LEN:]
        (cmdType, address, length, fileType,
         digestType, digestData) = struct.unpack(fmt, part1)
        endOffset = None
        for i in range(0, len(part2)):
            if part2[i] == 0:
                endOffset = i
                break
        if endOffset is not None:
            name = str(part2[0:endOffset], encoding='utf-8')
        else:
            name = str(part2[0:], encoding='utf-8')
        file = File(name, length, fileType, address)
        file.digestType = digestType
        file.digestData = digestData
        return file
    else:
        return None


def packFileOpen(address, byte_order='<'):
    if (byte_order != '<') and (byte_order != '>'):
        raise ValueError('unknown byte_order: '+str(byte_order))
    fmt = '%s2I' % (byte_order)
    return struct.pack(fmt, RMF_CMD_FILE_OPEN, address)


def unpackFileOpen(data, byte_order='<'):
    if (byte_order != '<') and (byte_order != '>'):
        raise ValueError('unknown byte_order: '+str(byte_order))
    fmt = '%s2I' % (byte_order)
    cmdType, address = struct.unpack(fmt, data)
    if cmdType != RMF_CMD_FILE_OPEN:
        raise ValueError('expected RMF_CMD_FILE_OPEN')
    return address


def packFileClose(address, byte_order='<'):
    if (byte_order != '<') and (byte_order != '>'):
        raise ValueError('unknown byte_order: '+str(byte_order))
    fmt = '%s2I' % (byte_order)
    return struct.pack(fmt, RMF_CMD_FILE_CLOSE, address)


def unpackFileClose(data, byte_order='<'):
    if (byte_order != '<') and (byte_order != '>'):
        raise ValueError('unknown byte_order: '+str(byte_order))
    fmt = '%s2I' % (byte_order)
    cmdType, address = struct.unpack(fmt, data)
    if cmdType != RMF_CMD_FILE_ClOSE:
        raise ValueError('expected RMF_CMD_FILE_ClOSE')
    return address


class TransmitHandler(metaclass=abc.ABCMeta):

    def getSendAvail(self):
        return None

    @abc.abstractmethod
    def send(self, data: bytes):
        """
        send data bytes
        """


class ReceiveHandler(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def onMsgReceived(self, msg):
        """
        called by socket adapter when a message has been received
        """
    @abc.abstractmethod
    def onConnected(self, transmitHandler):
        """
        called by socket adapter on a new connection, a reference to self
        (the socket adapter) is given as the argument
        """


class File:
    """
    Base class for File.
    This can be inherited from in case you need more properties (e.g. APX).
    Note: in C implemenation this class is called FileInfo_t
    """
    def __init__(self, name, length,
                 fileType=RMF_FILE_TYPE_FIXED, address=None):
        self.name = str(name)                   # part of FILEINFO struct
        self.length = int(length)               # part of FILEINFO struct
        self.fileType = int(fileType)           # part of FILEINFO struct
        self.address = address                  # part of FILEINFO struct
        self.digestType = RMF_DIGEST_TYPE_NONE  # part of FILEINFO struct
        self.digestData = bytes([0]*32)         # part of FILEINFO struct
        self.isRemoteFile = False               # not part of FILEINFO struct
        self.isOpen = False                     # not part of FILEINFO struct

    def open(self):
        self.isOpen = True

    def close(self):
        self.isOpen = False


class FileMap(metaclass=abc.ABCMeta):
    """
    abstract baseclass of FileMap

    FileMaps are used by the FileManager class.

    It is expected that files in the FileMap are sorted by address (ascending)
    """

    @abc.abstractmethod
    def insert(self, file):
        """
        inserts file into the FileMap.
        The FileMap must assign an address to the file when inserted
        """

    @abc.abstractmethod
    def remove(self, file):
        """
        removes file from FileMap.
        """


@ReceiveHandler.register
class FileManager:
    """
    The FileManager manages local and remote files
    mapped to a point-to-point connection
    """
    def __init__(self, localFileMap, remoteFileMap):
        assert(isinstance(localFileMap, FileMap))
        assert(isinstance(remoteFileMap, FileMap))
        self.localFileMap = localFileMap
        self.remoteFileMap = remoteFileMap
        self.requestedFiles = {}
        self.byteOrder = '<'  # use '<' for little endian, '>' for big endian

        def worker():
            """
            this is the worker thread.

            It awaits commands in the message queue q.
            When the special message None arrives it quits
            """
            transmitHandler = None
            while True:
                msg = self.msgQueue.get()
                if msg is None:
                    break
                msgType = msg[0]
                if msgType == RMF_MSG_CONNECT:
                    transmitHandler = msg[1]
                elif msgType == RMF_MSG_FILEINFO:
                    fileInfo = msg[1]
                    header = packHeader(RMF_CMD_START_ADDR)
                    if transmitHandler is not None:
                        transmitHandler.send(header+fileInfo)
                elif msgType == RMF_MSG_WRITE_DATA:
                    (address, data) = msg[1:3]
                    header = packHeader(address)
                    if transmitHandler is not None:
                        transmitHandler.send(header+data)
                elif msgType == RMF_MSG_FILEOPEN:
                    data = packFileOpen(msg[1])
                    header = packHeader(RMF_CMD_START_ADDR)
                    if transmitHandler is not None:
                        transmitHandler.send(header+data)
                else:
                    raise NotImplementedError(msgType)

        self.msgQueue = queue.Queue()
        self.worker_active = False
        self.worker = threading.Thread(target=worker)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()

    def start(self):
        self.worker_active = True
        self.worker.start()

    def stop(self):
        if self.worker_active:
            # send special message None to stop the worker thread
            self.msgQueue.put(None)
            self.worker.join()
            self.worker = None
            self.worker_active = False

    def _FileInfo_handler(self, msg):
        print("_FileInfo_handler")

    def attachLocalFile(self, file):
        self.localFileMap.insert(file)
        file.fileManager = self

    def requestRemoteFile(self, file):
        self.requestedFiles[file.name] = file

    # ReceiveHandler API
    def onMsgReceived(self, msg):
        bytes_parsed, address, more_bit = unpackHeader(msg)
        if bytes_parsed > 0:
            if address == RMF_CMD_START_ADDR:
                self._processCmd(msg[bytes_parsed:])
            elif address < RMF_CMD_START_ADDR:
                self._processFileWrite(address, more_bit, msg[bytes_parsed:])
            else:
                raise ValueError("invalid address %d" % address)

    def onConnected(self, transmitHandler):
        """
        called on new connection
        """
        print("FileManager.onConnected")
        self.msgQueue.put((RMF_MSG_CONNECT, transmitHandler))
        for file in self.localFileMap:
            self.msgQueue.put((RMF_MSG_FILEINFO, packFileInfo(file)))

    def _processCmd(self, data):
        fmt = self.byteOrder+'I'
        size = struct.calcsize(fmt)
        if len(data) >= size:
            (cmd,) = struct.unpack(fmt, data[0:size])
            if cmd == RMF_CMD_FILE_INFO:
                remoteFile = unpackFileInfo(data, self.byteOrder)
                # check if this is a requested file
                if remoteFile.name in self.requestedFiles:
                    requestedFile = self.requestedFiles[remoteFile.name]
                    if requestedFile.length == remoteFile.length:
                        del self.requestedFiles[requestedFile.name]
                        requestedFile.address = remoteFile.address
                        requestedFile.fileType = remoteFile.fileType
                        requestedFile.digestType = remoteFile.digestType
                        requestedFile.digestData = remoteFile.digestData
                        requestedFile.open()
                        self.remoteFileMap.insert(requestedFile)
                        print("sending request to open file %s" %
                              requestedFile.name)
                        msg = (RMF_MSG_FILEOPEN, requestedFile.address)
                        self.msgQueue.put(msg)
                    else:
                        print("[remoteFile.FileManager] FileInfo received for %s but with length=%d, expected length=%d" % (requstedFile.name, remoteFile.length, requstedFile.length))
                else:
                    self.remoteFileMap.insert(remoteFile)
            elif cmd == RMF_CMD_FILE_OPEN:
                address = unpackFileOpen(data, self.byteOrder)
                file = self.localFileMap.findByAddress(address)
                if file is not None:
                    print("FileManager.open(%s)" % file.name)
                    file.open()
                    fileContent = file.read(0, file.length)
                    if fileContent is not None:
                        msg = (RMF_MSG_WRITE_DATA, file.address, fileContent)
                        self.msgQueue.put(msg)
            elif cmd == RMF_CMD_FILE_CLOSE:
                address = unpackFileClose(data, self.byteOrder)
                file = self.localFileMap.findByAddress(address)
                if file is not None:
                    print("FileManager.close(%s)" % file.name)
                    file.close()
            else:
                print("[remotefile] unknown command %d" % cmd, file=sys.stderr)

    def _processFileWrite(self, address, more_bit, data):
        remoteFile = self.remoteFileMap.findByAddress(address)
        if remoteFile is not None and remoteFile.isOpen:
            offset = address-remoteFile.address
            if (offset >= 0) and ((offset+len(data)) <= remoteFile.length):
                remoteFile.write(offset, data, more_bit)

    def outPortDataWriteNotify(self, file: File, offset: int, length: int):
        assert(file.address is not None)
        fileContent = file.read(offset, length)
        if fileContent is not None:
            msg = (RMF_MSG_WRITE_DATA, file.address+offset, fileContent)
            self.msgQueue.put(msg)

from remotefile.socket_adapter import TcpSocketAdapter
from remotefile.proto import readLine
