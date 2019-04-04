import apx.base
import apx.context
import cfile as C
import sys
import autosar
import autosar.constant
import os
from collections import namedtuple

TypeInfo = namedtuple('TypeInfo', ['variable_name', 'type_name', 'array_len'])


def _genCommentHeader(comment):
    lines = []
    lines.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
    lines.append(C.line('// %s'%comment))
    lines.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
    return lines


# def autosar_constant_to_initializer(constant):
#    if constant is None:
#       return ''
#    elif isinstance(constant, autosar.constant.IntegerValue):
#       return '%d'%(int(constant.value))
#    else:
#       raise NotImplementedError(str(type(constant)))

class SignalInfo:
    def __init__(self, name,offset, pack_len, func, dsg, dataElement, operation, init_value=None):
        self.name=name
        self.offset=offset
        self.pack_len=pack_len
        self.init_value=init_value
        self.func=func
        self.dsg=dsg
        self.dataElement=dataElement
        self.arrayLen=dataElement.arrayLen

        if init_value is not None:
            self.init_data = dsg.createInitData(init_value)
        else:
            self.init_data = bytearray()
            self.init_data.extend([0 for x in range(self.pack_len)])

        assert(len(self.init_data)==self.pack_len)

        if operation == 'pack' or operation == 'unpack':
            self.operation=operation
        else:
            raise ValueError("operation: invalid parameter value '%s', expected 'pack' or 'unpack'"%operation)


class CallbackInfo:
    """
    A class that represents everything we need to know about user-defined callbacks
    """
    def __init__(self, indent=3):
        self.local_vars = []
        self.defines = {'offset':{}, 'length':{}}
        self.code_fragments = {}
        self.data_vars = None
        self.isFinalized = False
        self.pending = []
        self.indent = indent
        self.functions = []

    def create(self, port_info, callback_name=None):
        """
        Creates a new callback mapping. port info must be of type SignalInfo.
        When callback_name is None, no user-defined callback is generated
        """
        type_name = port_info.func.args[0].typename
        if callback_name is not None:
            type_info = TypeInfo(port_info.name, type_name, port_info.arrayLen)
            self.local_vars.append(type_info)
        port_offset_define = C.define("APX_RX_OFFSET_%s"%(port_info.name.upper()), port_info.offset)
        port_length_define = C.define("APX_RX_LEN_%s"%(port_info.name.upper()), port_info.pack_len)
        self.defines['offset'][port_info.name] = port_offset_define
        self.defines['length'][port_info.name] = port_length_define
        self.pending.append((port_info, callback_name, type_name, port_offset_define, port_length_define))


    def finalize(self):
        self.data_vars = []
        for type_info in sorted(self.local_vars, key=lambda type_info: type_info.variable_name):
            c_var = C.variable(type_info.variable_name, type_info.type_name, array=type_info.array_len)
            self.data_vars.append(c_var)
        for elem in self.pending:
            self._generate_code_fragment(*elem)
        self.pending=[]
        self.isFinalized = True


    def _generate_code_fragment(self, port_info, callback_name, type_name, port_offset_define, port_length_define):
        code = C.sequence()
        code.append(C.line('case %s:'%port_offset_define.left))
        if callback_name is not None:
            idx0_str = '' if port_info.arrayLen is None else '[0]'
            code.append(C.statement('(void) %s(&data.%s%s)' % (port_info.func.name, port_info.name, idx0_str), indent=self.indent))
            modifier='&' if port_info.dsg.isComplexType() else ''
            code.append(C.statement(C.fcall(callback_name, [modifier + 'data.' + port_info.name + idx0_str]), indent=self.indent))
        code.append(C.statement('offset += %s'%port_length_define.left, indent=self.indent))
        code.append(C.statement('break', indent=self.indent))
        self.code_fragments[port_info.offset]=code
        if callback_name is not None:
            self.functions.append(C.function(callback_name, 'void', args=[C.variable('value', type_name, pointer=port_info.dsg.isComplexType())]))

class NodeGenerator:
    """
    APX Node generator for c-apx and apx-es
    """

    def __init__(self, record_elem_suffix=None):
        self.includes=None
        self.InPortDataNotifyFunc=None
        self.callbacks=CallbackInfo()
        self.record_elem_suffix = record_elem_suffix if record_elem_suffix is not None else ''

    def generate(self, output_dir, node, name=None, includes=None, callbacks=None, header_dir=None):
        """
        generates APX node layer for single APX node

        parameters:

           node: APX node object

           output_dir: directory where to generate header and source files

           name: Can be used to override the name of the APX node. Default is

           includes: optional list of additional include files,

           callbacks: optional dict of require port callbacks (key: port name, value: name of C callback function)

           header_dir: optional directory where to redirect header generation (instead of output_dir)

        """
        signalInfoList=[]
        signalInfoMap={'require':{}, 'provide':{}}
        inPortDataLen=0
        outPortDataLen=0
        offset=0
        if name is None:
            prefixed_name='ApxNode_'+node.name
            name = node.name
        else:
            prefixed_name='ApxNode_'+name
        self.node = node
        self.name=name
        self.prefixed_name = prefixed_name
        self.includes=includes
        self.callback_list = []
        self.has_callbacks = True if (callbacks is not None) else False

        if not node.isFinalized:
            node.finalize_sorted()

        source_dir = output_dir
        if header_dir is None:
            header_dir=source_dir
        #require ports (in ports)
        for port in node.requirePorts:
            is_pointer=False
            func = C.function("ApxNode_Read_%s_%s"%(name,port.name),"Std_ReturnType")
            is_pointer=True
            type_name = port.dsg.ctypename(node.dataTypes)
            func.add_arg(C.variable('val',type_name,pointer=is_pointer))
            packLen=port.dsg.packLen()
            port.dsg.typeList=node.dataTypes
            initValue=None
            if port.attr is not None:
                initValue = port.attr.initValue
            info = SignalInfo(port.name,offset,packLen,func,port.dsg,port.resolve_type(node.dataTypes), 'unpack', initValue)
            if self.has_callbacks:
                if port.name in callbacks:
                    self.callbacks.create(info, callbacks[port.name])
                else:
                    self.callbacks.create(info, None)
            signalInfoList.append(info)
            signalInfoMap['require'][port.name]=info
            inPortDataLen+=packLen
            offset+=packLen
        #provide ports (out ports)
        offset=0
        for port in node.providePorts:
            is_pointer=False
            func = C.function("ApxNode_Write_%s_%s"%(name,port.name),"Std_ReturnType")
            if port.dsg.isComplexType(node.dataTypes):
                is_pointer=True
            func.add_arg(C.variable('val',port.dsg.ctypename(node.dataTypes),pointer=is_pointer))
            packLen=port.dsg.packLen()
            port.dsg.typeList= node.dataTypes
            initValue=None
            if port.attr is not None:
                initValue = port.attr.initValue
            tmp = SignalInfo(port.name,offset,packLen,func,port.dsg, port.resolve_type(node.dataTypes),'pack',initValue)
            signalInfoList.append(tmp)
            signalInfoMap['provide'][port.name]=tmp
            outPortDataLen+=packLen
            offset+=packLen
        self.callbacks.finalize()
        self.inPortDataLen=inPortDataLen
        self.outPortDataLen=outPortDataLen
        header_filename = os.path.normpath(os.path.join(header_dir, self.prefixed_name+'.h'))
        source_filename = os.path.normpath(os.path.join(source_dir, self.prefixed_name+'.c'))
        callback_path,callback_file=None,None
        if len(self.callbacks.functions)>0:
            callback_file = self.prefixed_name+'_Cbk.h'
            callback_path = os.path.normpath(os.path.join(header_dir, callback_file))
            with open(callback_path, "w") as fp:
                self._writeCallbackPrototypes(fp, prefixed_name.upper()+'_CBK_H')
        with open(header_filename, "w") as fp:
            (initFunc,nodeDataFunc) = self._writeHeaderFile(fp, signalInfoList, signalInfoMap, prefixed_name.upper()+'_H', node)
        with open(source_filename, "w") as fp:
            self._writeSourceFile(fp,signalInfoMap,initFunc,nodeDataFunc, node, inPortDataLen, outPortDataLen, callback_file)

    def genPackUnpackInteger(self, code, buf, operation, valname, dataElement, localvar, offset, indent):
        dataLen=0
        resolvedElement = dataElement.resolve_data_element()
        if resolvedElement.typeCode==apx.SINT8_TYPE_CODE or resolvedElement.typeCode==apx.UINT8_TYPE_CODE:
            dataLen=1
            basetype='sint8' if resolvedElement.typeCode==apx.SINT8_TYPE_CODE else 'uint8'
        elif resolvedElement.typeCode==apx.SINT16_TYPE_CODE or resolvedElement.typeCode==apx.UINT16_TYPE_CODE:
            dataLen=2
            basetype='sint16' if resolvedElement.typeCode==apx.SINT16_TYPE_CODE else 'uint16'
        elif resolvedElement.typeCode==apx.SINT32_TYPE_CODE or resolvedElement.typeCode==apx.UINT32_TYPE_CODE:
            dataLen=4
            basetype='sint32' if resolvedElement.typeCode==apx.SINT32_TYPE_CODE else 'uint32'
        else:
            raise NotImplementedError(resolvedElement.typeCode)
        if 'bufptr' in localvar:
            # relative addressing
            if dataLen == 1:
                if operation == 'pack':
                    code.append(C.statement('*%s=(uint8) %s' % (localvar['bufptr'].name, valname), indent=indent))
                else:  # unpack
                    code.append(C.statement('%s = (%s) *%s' % (valname, basetype, localvar['bufptr'].name), indent=indent))
                code.append(C.statement('%s++' % (localvar['bufptr'].name), indent=indent))
            else:
                if operation == 'pack':
                    code.append(C.statement('packLE(%s,(uint32) %s,(uint8) sizeof(%s))' % (localvar['bufptr'].name, valname, basetype), indent=indent))
                else:
                    code.append(C.statement('%s = (%s) unpackLE(%s,(uint8) sizeof(%s))' % (valname, basetype, localvar['bufptr'].name, basetype), indent=indent))
                code.append(C.statement('%s+=sizeof(%s)' % (localvar['bufptr'].name, basetype), indent=indent))
        else:
            # absolute addressing
            if dataLen == 1:
                if operation == 'pack':
                    code.append(C.statement("%s[%d]=(uint8) %s" % (buf.name, offset, valname), indent=indent))
                else:  # unpack
                    code.append(C.statement("*%s = (%s) %s[%d]" % (valname, basetype, buf.name, offset), indent=indent))
            else:
                if operation == 'pack':
                    code.append(C.statement('packLE(&%s[%d],(uint32) %s,(uint8) sizeof(%s))' % (buf.name, offset, valname, basetype), indent=indent))
                else:
                    code.append(C.statement('*%s = (%s) unpackLE(&%s[%d],(uint8) sizeof(%s))' % (valname, basetype, buf.name, offset, basetype), indent=indent))
        return dataLen

    def genPackUnpackItem(self, code, buf, operation, val, elem, localvar, offset, indent, indentStep):
        if isinstance(elem, apx.DataSignature):
            dataElement = elem.resolve_data_element(self.node.dataTypes)
        elif isinstance(elem, apx.DataElement):
            dataElement = elem
        else:
            raise NotImplementedError(type(elem))
        packLen=0
        if isinstance(val,C.variable):
            valname=val.name
        elif isinstance(val,str):
            valname=val
        else:
            raise ValueError(val)
        if (dataElement.isComplexType()):
            #raise NotImplemented('complex types not yet fully supported')
            if dataElement.typeCode == apx.STRING_TYPE_CODE:
                if dataElement.strNullTerminator:
                    strDataLen = dataElement.arrayLen-1 #reserve one byte for null-terminator
                else:
                    strDataLen = dataElement.arrayLen #Allow entire array for data
                if 'bufptr' in localvar:
                    #use relative addressing using 'p' pointer
                    if operation == 'pack':
                        code.append(C.statement('memcpy(%s,%s,%d)'%(localvar['bufptr'].name,valname, strDataLen),indent=indent))
                        if dataElement.strNullTerminator:
                            code.append(C.statement("%s[%d]='\\0'"%(localvar['bufptr'].name, strDataLen),indent=indent))
                    else:
                        code.append(C.statement('memcpy(%s,%s,%d)'%(valname, localvar['bufptr'].name, strDataLen), indent=indent))
                        #TODO: add support for disabling/enabling usage of null-terminator in NodeGenerator data unpacking
#                        if dataElement.strNullTerminator:
#                            code.append(C.statement("%s[%d]='\\0'"%(localvar['bufptr'].name, strDataLen), indent=indent))
                    code.append(C.statement('%s+=%d'%(localvar['bufptr'].name, dataElement.arrayLen),indent=indent))
                else:
                    #use absolute addressing using buf variable and offset
                    if operation == 'pack':
                        code.append(C.statement('memcpy(&%s[%d],%s,%d)'%(buf.name,offset,valname, strDataLen),indent=indent))
                        if dataElement.strNullTerminator:
                            code.append(C.statement("%s[%d]='\\0'"%(buf.name,offset+strDataLen),indent=indent))
                    else:
                        code.append(C.statement('memcpy(%s,&%s[%d],%d)'%(valname,buf.name,offset, strDataLen),indent=indent))
                        #TODO: add support for disabling/enabling usage of null-terminator in NodeGenerator data unpacking
#                        if dataElement.strNullTerminator:
#                            code.append(C.statement("%s[%d]='\\0'"%(buf.name, offset+strDataLen),indent=indent))
                packLen=dataElement.arrayLen

            elif dataElement.typeCode==apx.RECORD_TYPE_CODE:
                if 'bufptr' not in localvar:
                    localvar['bufptr']=C.variable('p','uint8',pointer=True)
                for childElement in dataElement.elements:
                    if isinstance(val,C.variable):
                        if val.pointer:
                            childName="%s->%s%s"%(valname, childElement.name, self.record_elem_suffix)
                        else:
                            childName="%s.%s%s"%(valname, childElement.name, self.record_elem_suffix)
                    elif isinstance(val,str):
                        childName="%s.%s"%(valname, childElement.name)
                    assert(childName is not None)
                    itemLen=self.genPackUnpackItem(code, buf, operation, childName, childElement, localvar, offset, indent, indentStep)
                    offset+=itemLen
                    packLen+=itemLen
            elif dataElement.isArray():
                if dataElement.arrayLen<256:
                    typename='uint8'
                elif dataElement.arrayLen<65536:
                    typename='uint16'
                else:
                    typename='uint32'
                if 'loopVar' not in localvar:
                    localvar['loopVar']=C.variable('i',typename)
                else:
                    if localvar['loopVar'].typename=='uint8' and (typename=='uint16' or typename=='uint32'):
                        localvar['loopVar'].typename=typename
                    elif localvar['loopVar'].typename=='uint16' and typename=='uint32':
                        localvar['loopVar'].typename=typename
                if 'bufptr' not in localvar:
                    localvar['bufptr']=C.variable('p','uint8',pointer=True)
                code.append(C.line('for({0}=0;{0}<{1};{0}++)'.format(localvar['loopVar'].name,dataElement.arrayLen),indent=indent))
                block=C.block(indent=indent)
                indent+=indentStep
                packLen=self.genPackUnpackInteger(block, buf, operation, valname+'[%s]'%localvar['loopVar'].name, dataElement, localvar, offset, indent)
                packLen*=dataElement.arrayLen
                indent-=indentStep
                code.append(block)
        else:
            packLen=self.genPackUnpackInteger(code, buf, operation, valname, elem, localvar, offset, indent)
        return packLen

    def genPackUnpackFunc(self, func, buf, offset, operation, dsg, indent, indentStep):
        indent+=indentStep
        code=C.block()
        localvar={'buf':'m_outPortdata'}
        val=func.args[0]

        codeBlock=C.sequence()
        packLen=self.genPackUnpackItem(codeBlock, buf, operation, val, dsg, localvar, offset, indent, indentStep)
        #initializer=C.initializer(None,['(uint16)%du'%offset,'(uint16)%du'%packLen])
        if 'p' in localvar:
            code.append(C.statement(localvar['p'],indent=indent))
        for k in sorted(localvar.keys()):
            if k=='p' or k=='buf':
                continue
            else:
                v = localvar[k]
                code.append(C.statement(v,indent=indent))
        if operation=='pack':
            code.append(C.statement('apx_nodeData_lockOutPortData(&m_nodeData)', indent=indent))
        else:
            if packLen > 1:
                code.append(C.statement('apx_nodeData_lockInPortData(&m_nodeData)', indent=indent))
        if 'bufptr' in localvar:
            code.append(C.statement('%s=&%s[%d]'%(localvar['bufptr'].name,buf.name,offset),indent=indent))
        code.extend(codeBlock)
        if operation=='pack':
            code.append(C.statement(C.fcall('outPortData_writeCmd', params=[offset, packLen]),indent=indent))
        else:
            if packLen > 1:
                code.append(C.statement('apx_nodeData_unlockInPortData(&m_nodeData)', indent=indent))
        code.append(C.statement('return E_OK',indent=indent))
        indent-=indentStep
        return code,packLen



    def _writeHeaderFile(self, fp, signalInfoList, signalInfoMap, guard, node):

        headerFile=C.hfile(None,guard=guard)
        headerFile.code.append(C.blank(1))
        headerFile.code.append(C.include('apx_nodeData.h'))
        #headerFile.code.append(C.include('Std_Types.h'))
        #headerFile.code.append(C.include('Rte_Type.h'))
        if self.includes is not None:
            for filename in self.includes:
                headerFile.code.append(C.include(filename))

        headerFile.code.append(C.blank(1))
        headerFile.code.extend(_genCommentHeader('CONSTANTS'))

        headerFile.code.append(C.blank(1))
        headerFile.code.extend(_genCommentHeader('FUNCTION PROTOTYPES'))
        initFunc = C.function('ApxNode_Init_%s'%self.name,'void')
        nodeDataFunc = C.function('ApxNode_GetNodeData_%s'%self.name,'apx_nodeData_t',pointer=True)
        headerFile.code.append(C.statement(initFunc))
        headerFile.code.append(C.statement(nodeDataFunc))
        headerFile.code.append(C.blank(1))
        for elem in signalInfoList:
            headerFile.code.append(C.statement(elem.func))

        if self.inPortDataLen>0:
            #void (*inPortDataWritten)(void *arg, struct apx_nodeData_tag *nodeData, uint32_t offset, uint32_t len)
            self.InPortDataNotifyFunc=C.function(self.name+'_inPortDataWritten','void')
            self.InPortDataNotifyFunc.add_arg(C.variable('arg','void',pointer=True))
            self.InPortDataNotifyFunc.add_arg(C.variable('nodeData','apx_nodeData_t',pointer=True))
            self.InPortDataNotifyFunc.add_arg(C.variable('offset','uint32_t'))
            self.InPortDataNotifyFunc.add_arg(C.variable('len','uint32_t'))
            headerFile.code.append(C.statement(self.InPortDataNotifyFunc))

        fp.write(str(headerFile))
        return (initFunc,nodeDataFunc)

    def _writeSourceFile(self, fp, signalInfoMap, initFunc, nodeDataFunc, node, inPortDataLen, outPortDataLen, callbackHeader):
        indent=0
        indentStep=3

        ctx = apx.Context()
        ctx.append(node)
        nodeText = ctx.dumps()
        sourceFile=C.cfile(None)
        code = sourceFile.code
        code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
        code.append(C.line('// INCLUDES'))
        code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
        code.append(C.sysinclude('string.h'))
        code.append(C.sysinclude('stdio.h')) #TEMPORARY, REMOVE LATER
        code.append(C.include('%s.h'%self.prefixed_name))
        if callbackHeader is not None:
            code.append(C.include(callbackHeader))
        code.append(C.include('pack.h'))
        code.append(C.blank(1))
        code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
        code.append(C.line('// CONSTANTS AND DATA TYPES'))
        code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
        code.append(C.define('APX_DEFINITON_LEN', str(len(nodeText)+1)+'u')) #add 1 for empty newline
        code.append(C.define('APX_IN_PORT_DATA_LEN', str(inPortDataLen)+'u'))
        code.append(C.define('APX_OUT_PORT_DATA_LEN', str(outPortDataLen)+'u'))
        if len(self.callbacks.defines['length'])>0:
            for define in sorted(self.callbacks.defines['length'].values(), key=lambda x: x.right):
                code.append(str(define))
        if len(self.callbacks.defines['offset'])>0:
            for define in sorted(self.callbacks.defines['offset'].values(), key=lambda x: x.right):
                code.append(str(define))

        code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
        code.append(C.line('// LOCAL FUNCTIONS'))
        code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
        if outPortDataLen>0:
            code.append(C.statement('static void outPortData_writeCmd(apx_offset_t offset, apx_size_t len )'))

        code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
        code.append(C.line('// LOCAL VARIABLES'))
        code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))

        if (outPortDataLen) > 0:
            outDatabuf=C.variable('m_outPortdata','uint8', static=True, array='APX_OUT_PORT_DATA_LEN')
            outInitData=C.variable('m_outPortInitData','uint8_t', static=True, const=True, array='APX_OUT_PORT_DATA_LEN')
            code.append(str(outInitData)+'= {')
            initBytes=[]
            for port in node.providePorts:
                signalInfo = signalInfoMap['provide'][port.name]
                initBytes.extend([str(x) for x in signalInfo.init_data])
            assert(len(initBytes) == outPortDataLen)
            maxItemsPerLine=32
            remain=len(initBytes)
            while(remain>0):
                if remain>maxItemsPerLine:
                    numItems,last=maxItemsPerLine,False
                else:
                    numItems,last=remain,True
                if last:
                    code.append(' '*indentStep+', '.join(initBytes[0:numItems]))
                else:
                    code.append(' '*indentStep+', '.join(initBytes[0:numItems])+',')
                del initBytes[0:numItems]
                remain=len(initBytes)

            code.append('};')
            code.append(C.blank(1))
            code.append(C.statement(outDatabuf))
            code.append(C.statement(C.variable('m_outPortDirtyFlags','uint8_t', static=True, array='APX_OUT_PORT_DATA_LEN')))
        else:
            outDatabuf,outInitData = None,None

        if (inPortDataLen) > 0:
            inDatabuf=C.variable('m_inPortdata','uint8', static=True, array='APX_IN_PORT_DATA_LEN')
            inInitData=C.variable('m_inPortInitData','uint8_t', static=True, const=True, array='APX_IN_PORT_DATA_LEN')
            code.append(str(inInitData)+'= {')
            initBytes=[]
            for port in node.requirePorts:
                signalInfo = signalInfoMap['require'][port.name]
                initBytes.extend([str(x) for x in signalInfo.init_data])
            assert(len(initBytes) == inPortDataLen)
            maxItemsPerLine=32
            remain=len(initBytes)
            while(remain>0):
                if remain>maxItemsPerLine:
                    numItems,last=maxItemsPerLine,False
                else:
                    numItems,last=remain,True
                if last:
                    code.append(' '*indentStep+', '.join(initBytes[0:numItems]))
                else:
                    code.append(' '*indentStep+', '.join(initBytes[0:numItems])+',')
                del initBytes[0:numItems]
                remain=len(initBytes)
            code.append('};')
            code.append(C.blank(1))
            code.append(C.statement(inDatabuf))
            code.append(C.statement(C.variable('m_inPortDirtyFlags','uint8_t', static=True, array='APX_IN_PORT_DATA_LEN')))
        else:
            inDatabuf,inInitData = None,None

        code.append(C.statement(C.variable('m_nodeData','apx_nodeData_t',static=True)))
        code.append(C.line('static const char *m_apxDefinitionData='))
        for line in nodeText.split('\n'):
            line=line.replace('"','\\"')
            code.append(C.line('"%s\\n"'%line))
        code.elements[-1].val+=';'
        code.append(C.blank(1))



        code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
        code.append(C.line('// GLOBAL FUNCTIONS'))
        code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))

        sourceFile.code.append(initFunc)
        body=C.block(innerIndent=indentStep)
        if inPortDataLen>0:
            body.append(C.statement('memcpy(&m_inPortdata[0], &m_inPortInitData[0], APX_IN_PORT_DATA_LEN)'))
            body.append(C.statement('memset(&m_inPortDirtyFlags[0], 0, sizeof(m_inPortDirtyFlags))'))
        if outPortDataLen>0:
            body.append(C.statement('memcpy(&m_outPortdata[0], &m_outPortInitData[0], APX_OUT_PORT_DATA_LEN)'))
            body.append(C.statement('memset(&m_outPortDirtyFlags[0], 0, sizeof(m_outPortDirtyFlags))'))
        args = ['&m_nodeData', '"%s"'%(node.name), '(uint8_t*) &m_apxDefinitionData[0]', 'APX_DEFINITON_LEN']
        if inPortDataLen>0:
            args.extend(['&m_inPortdata[0]', '&m_inPortDirtyFlags[0]', 'APX_IN_PORT_DATA_LEN'])
        else:
            args.extend(['0','0','0'])
        if outPortDataLen>0:
            args.extend(['&m_outPortdata[0]', '&m_outPortDirtyFlags[0]', 'APX_OUT_PORT_DATA_LEN'])
        else:
            args.extend(['0','0','0'])
        body.append(C.statement('apx_nodeData_create(%s)'%(', '.join(args))))
        body.append(C.line('#ifdef APX_POLLED_DATA_MODE', indent=0))
        body.append(C.statement('rbfs_create(&m_outPortDataCmdQueue, &m_outPortDataCmdBuf[0], APX_NUM_OUT_PORTS, APX_DATA_WRITE_CMD_SIZE)'))
        body.append(C.line('#endif', indent=0))

        sourceFile.code.append(body)
        sourceFile.code.append(C.blank(1))

        sourceFile.code.append(nodeDataFunc)
        body=C.block(innerIndent=indentStep)

        body.append(C.statement('return &m_nodeData'))
        sourceFile.code.append(body)
        sourceFile.code.append(C.blank(1))

        for port in node.requirePorts:
            signalInfo = signalInfoMap['require'][port.name]
            sourceFile.code.append(signalInfo.func)
            body,packLen=self.genPackUnpackFunc(signalInfo.func, inDatabuf, signalInfo.offset, signalInfo.operation, signalInfo.dsg, indent, indentStep)
            code.append(body)
            code.append(C.blank())
        for port in node.providePorts:
            signalInfo = signalInfoMap['provide'][port.name]
            sourceFile.code.append(signalInfo.func)
            body,packLen=self.genPackUnpackFunc(signalInfo.func, outDatabuf, signalInfo.offset, signalInfo.operation, signalInfo.dsg, indent, indentStep)
            code.append(body)
            code.append(C.blank())

        if self.InPortDataNotifyFunc is not None:
            code.append(self.InPortDataNotifyFunc)
            indent+=indentStep
            body=C.block(innerIndent=indent)

            body.append(C.statement('(void)arg'))
            body.append(C.statement('(void)nodeData'))

            if len(self.callbacks.code_fragments)>0:
                body.append('')
                body.append(C.line('union data_tag'))
                body.append(C.line('{'))
                indent+=indentStep
                for c_var in self.callbacks.data_vars:
                    body.append(C.statement(c_var, indent=indent))
                indent-=indentStep
                body.append(C.statement('} data'))
                end_offset_var = C.variable('endOffset', 'uint32_t')
                init_expression = '%s + %s'%(self.InPortDataNotifyFunc.args[2].name,self.InPortDataNotifyFunc.args[3].name)
                body.append(C.statement(str(end_offset_var)+' = '+ init_expression ))
                body.append('')
                body.append(C.line('while (offset < endOffset)'))
                body.append(C.line('{'))
                indent+=indentStep
                body.append(C.line('switch(offset)', indent=indent))
                switch_body = C.block(indent=indent)
                for key in sorted(self.callbacks.code_fragments.keys()):
                    lines = [indent*C.indentChar+x for x in self.callbacks.code_fragments[key].lines()]
                    switch_body.extend(lines)
                switch_body.append(C.line('default:', indent=indent))
                indent+=indentStep
                switch_body.append(C.statement('offset = endOffset', indent=indent))
                indent-=indentStep
                body.append(switch_body)
                body.append(C.line('}'))
                indent-=indentStep
            else:
                body.append(C.statement('(void)offset'))
                body.append(C.statement('(void)len'))

            code.append(body)
            indent-=indentStep

        code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
        code.append(C.line('// LOCAL FUNCTIONS'))
        code.append(C.line('//////////////////////////////////////////////////////////////////////////////'))
        if outPortDataLen>0:
            code.append('''static void outPortData_writeCmd(apx_offset_t offset, apx_size_t len )
{
   if ( (m_outPortDirtyFlags[offset] == 0) && (true == apx_nodeData_isOutPortDataOpen(&m_nodeData) ) )
   {
      m_outPortDirtyFlags[offset] = (uint8_t) 1u;
      apx_nodeData_unlockOutPortData(&m_nodeData);
      apx_nodeData_outPortDataNotify(&m_nodeData, (uint32_t) offset, (uint32_t) len);
      return;
   }
   apx_nodeData_unlockOutPortData(&m_nodeData);
}''')
        fp.write(str(sourceFile))

    def _writeCallbackPrototypes(self, fp, guard):

        headerFile=C.hfile(None, guard=guard)
        code = headerFile.code
        code.append(C.blank(1))
        code.extend(_genCommentHeader('INCLUDES'))
        code.append(C.include('Rte_Type.h'))

        code.append(C.blank(1))
        code.extend(_genCommentHeader('FUNCTION PROTOTYPES'))
        for func in self.callbacks.functions:
            code.append(C.statement(func))
        fp.write(str(headerFile))


class ComVariable:
    def __init__(self, name, data_type, init_value):
        self.initializer = autosar.constant.initializer_string(init_value)
        self.inner = C.variable(name, data_type.name, static=True)

    def declaration(self):
        return C.statement('%s = %s'%(str(self.inner), self.initializer))


class ComGenerator:
    def __init__(self, com_component):
        assert isinstance(com_component, autosar.bsw.com.ComComponent)
        self.component = com_component
        self.apx_node = apx.Node().import_autosar_swc(com_component).mirror()
        self.local_vars = {}
        self.inner_indent=3
        self.header_includes = [('Rte_Type.h', False)]
        self.header_file = None
        # self.ar_port_map = {}
        # self.apx_port_map = {}
        #
        # for port in com_component.requirePorts+com_component.providePorts:
        #    self.ar_port_map[port.name]=port
        # for port in apx_node.requirePorts+com_component.providePorts:
        #    self.apx_port_map[port.name]=port
        self.createAPI()


    def createAPI(self):
        for func in self.component.upperLayerAPI.send:
            self.createSendBody(func)
        for func in self.component.upperLayerAPI.receive:
            self.createReceiveBody(func)

    def createSendBody(self, com_func):
        body = C.block(innerIndent=self.inner_indent)
        local_var = self._local_var(com_func)
        if com_func.data_element.dataType.isComplexType:
            var_modifier = '&'
            body.append(C.line('if (memcmp(%s, %s, sizeof(%s)) != 0)'%(com_func.proto.args[0].name, var_modifier+local_var.inner.name, local_var.inner.name)))
        else:
            var_modifier = ''
            body.append(C.line('if (%s != %s)'%(com_func.proto.args[0].name, local_var.inner.name)))
        inner_body = C.block(innerIndent=self.inner_indent)
        if com_func.data_element.dataType.isComplexType:
            inner_body.append(C.statement('memcpy(%s, %s, sizeof(%s))'%(var_modifier+local_var.inner.name, com_func.proto.args[0].name, local_var.inner.name)))
        else:
            inner_body.append(C.statement('%s = %s'%(local_var.inner.name, com_func.proto.args[0].name)))
        apx_call = C.statement(C.fcall('ApxNode_Write_%s_%s'%(self.apx_node.name,com_func.port.name), params=[var_modifier+local_var.inner.name]))
        inner_body.append(apx_call)
        body.append(inner_body)
        body.append(C.statement('return E_OK'))
        com_func.body = body

    def createReceiveBody(self, com_func):
        body = C.block(innerIndent=self.inner_indent)
        apx_call = C.statement(C.fcall('ApxNode_Read_%s_%s'%(self.apx_node.name,com_func.port.name), params=[com_func.proto.args[0].name]))
        body.append(apx_call)
        body.append(C.statement('return E_OK'))
        com_func.body = body

    def _local_var(self, com_func):
        var_name = 'm_%s_%s'%(com_func.port.name,com_func.data_element.name)
        if var_name not in self.local_vars:
            local_var = ComVariable(var_name, com_func.data_element.dataType, com_func.data_element.initValue)
            self.local_vars[var_name]=local_var
        else:
            local_var = self.local_vars[var_name]
        return local_var

    # def createSendFunction(self, signal_name, dataType):
    #    upperLayerFunc = C.function('ApxCom_Send_'+signal_name, 'Std_ReturnType')
    #    isPointer = True if dataType.isComplexType else False
    #    upperLayerFunc.add_arg(C.variable('value', dataType.name, pointer=isPointer))
    #    lowerLayerFunc = None
    #    for node in self.apx_context.nodes:
    #       for apx_port in node.requirePorts + node.providePorts:
    #          if apx_port.name == signal_name:
    #             name = 'ApxNode_Write_%s_%s'%(node.name,apx_port.name)
    #             lowerLayerFunc = C.function(name, 'Std_ReturnType')
    #             lowerLayerFunc.add_arg(C.variable('val', dataType.name, pointer=isPointer))
    #             include_file = 'ApxNode_%s.h'%node.name
    #             if include_file not in self.includes:
    #                self.includes.append(include_file)
    #             break
    #    if lowerLayerFunc is None:
    #       raise ValueError('unable to find apx node with port '+signal_name)
    #    info = ComSendFunction(signal_name, dataType, upperLayerFunc, lowerLayerFunc)
    #    self.upperLayerAPI['send'].append(info)
    #    self.localVars.append(info.var)
    #
    # def createReceiveFunction(self, signal_name, dataType):
    #    upperLayerFunc = C.function('ApxCom_Receive_'+signal_name, 'Std_ReturnType')
    #    isPointer = True
    #    upperLayerFunc.add_arg(C.variable('value', dataType.name, pointer=isPointer))
    #    lowerLayerFunc = None
    #    for node in self.apx_context.nodes:
    #       for apx_port in node.requirePorts + node.providePorts:
    #          if apx_port.name == signal_name:
    #             name = 'ApxNode_Read_%s_%s'%(node.name,apx_port.name)
    #             lowerLayerFunc = C.function(name, 'Std_ReturnType')
    #             lowerLayerFunc.add_arg(C.variable('val', dataType.name, pointer=isPointer))
    #             include_file = 'ApxNode_%s.h'%node.name
    #             if include_file not in self.includes:
    #                self.includes.append(include_file)
    #             break
    #    if lowerLayerFunc is None:
    #       raise ValueError('unable to find apx node with port '+signal_name)
    #    info = ComReceiveFunction(signal_name, dataType, upperLayerFunc, lowerLayerFunc)
    #    self.upperLayerAPI['receive'].append(info)
    #    self.localVars.append(info.var)


    def generateHeader(self, dest_dir = '.', file_name='ApxCom.h'):
        self.header_file = file_name
        file_path = os.path.join(dest_dir, file_name)
        hfile = C.hfile(file_path)
        code = hfile.code
        code.extend(_genCommentHeader('INCLUDES'))
        for elem in self.header_includes:
            if isinstance(elem, tuple):
                code.append(C.include(elem[0], sys=elem[1]))
        code.append(C.blank(1))
        code.extend(_genCommentHeader('CONSTANTS AND DATA TYPES'))
        code.append(C.blank(1))
        code.extend(_genCommentHeader('GLOBAL FUNCTIONS'))
        for com_func in self.component.upperLayerAPI.send+self.component.upperLayerAPI.receive:
            code.append(C.statement(com_func.proto))
        with open(file_path, "w") as fp:
            fp.write(str(hfile))

    def generateSource(self, dest_dir = '.', file_name='ApxCom.c'):
        file_path = os.path.join(dest_dir, file_name)
        file = C.cfile(file_path)
        code = file.code
        code.extend(self._writeIncludes())
        code.append(C.blank(1))
        code.extend(_genCommentHeader('CONSTANTS AND DATA TYPES'))
        code.append(C.blank(1))
        code.extend(_genCommentHeader('LOCAL FUNCTION PROTOTYPES'))
        code.extend(self._writeLocalVars())
        code.extend(self._generateGlobalFunctionsSource())
        with open(file_path, "w") as fp:
            fp.write(str(file))

    def _writeIncludes(self):
        code = C.sequence()
        code.extend(_genCommentHeader('INCLUDES'))
        code.append(C.include("string.h", sys=True))
        code.append(C.include(self.header_file))
        code.append(C.include('ApxNode_%s.h'%self.apx_node.name))
        return code

    def _writeLocalVars(self):
        code = C.sequence()
        code.append(C.blank(1))
        code.extend(_genCommentHeader('LOCAL VARIABLES'))
        for local_var in sorted(self.local_vars.values(), key=lambda x: x.inner.name):
            code.append(local_var.declaration())
        return code

    def _generateGlobalFunctionsSource(self):
        code = C.sequence()
        code.append(C.blank(1))
        code.extend(_genCommentHeader('GLOBAL FUNCTIONS'))
        for com_func in self.component.upperLayerAPI.send+self.component.upperLayerAPI.receive:
            code.append(C.blank(1))
            code.append(com_func.proto)
            code.append(com_func.body)
        return code
