import sys,os
import autosar
sys.path.insert(0,'../..')
import apx

def create_dir(dir_name):
   if not os.path.exists(dir_name):
      os.makedirs(dir_name)

def create_autosar_workspace():
   ws = autosar.workspace()
   dataTypes = ws.createPackage('DataType', role='DataType')
   dataTypes.createSubPackage('CompuMethod', role='CompuMethod')
   dataTypes.createSubPackage('Unit', role='Unit')
   dataTypes.createIntegerDataType('UInt8', min=0, max=255)
   dataTypes.createIntegerDataType('UInt16', min=0, max=65535)
   dataTypes.createIntegerDataType('UInt32', min=0, max=4294967295)   
   dataTypes.createArrayDataType('U16Array_T', '/DataType/UInt16', 4)
   dataTypes.createRecordDataType('MyRecord_T', elements=[
      ('First', 'UInt8'),
      ('Second', 'U16Array_T')
   ])
   constants = ws.createPackage('Constant', role='Constant')
   constants.createConstant('C_U16Array4_IV', 'U16Array_T', [0, 0, 0, 0])
   constants.createConstant('C_MyRecord_IV', 'MyRecord_T', {'First': 0, 'Second': [0, 0, 0, 0]})
   portInterfaces = ws.createPackage('PortInterface', role='PortInterface')
   portInterfaces.createSenderReceiverInterface('U16Array4_I',
                                                autosar.DataElement('Element', 'U16Array_T'))
   portInterfaces.createSenderReceiverInterface('MyRecord_I',
                                                autosar.DataElement('Data', 'MyRecord_T'))
   components = ws.createPackage('ComponentType', role='ComponentType')
   swc = components.createApplicationSoftwareComponent('Example4')
   swc.createProvidePort('U16ArraySender', 'U16Array4_I', initValueRef='/Constant/C_U16Array4_IV')
   swc.createRequirePort('U16ArrayReceiver', 'U16Array4_I', initValueRef='/Constant/C_U16Array4_IV')
   swc.createRequirePort('RecordReceiver', 'MyRecord_I', initValueRef='/Constant/C_MyRecord_IV')
   swc.behavior.createRunnable(swc.name+'_Init', portAccess=[x.name for x in swc.providePorts])
   swc.behavior.createRunnable(swc.name+'_Run', portAccess=[x.name for x in swc.requirePorts+swc.providePorts])
   return ws

def create_rte_partition(ws):
   partition = autosar.rte.Partition()
   for swc in ws.findall('/ComponentType/*'):
      if isinstance(swc, autosar.component.ApplicationSoftwareComponent):
         partition.addComponent(swc)
   return partition

def generate_rte_types(partition, derived_dir):
   type_generator = autosar.rte.TypeGenerator(partition)
   type_generator.generate(derived_dir)

def create_apx_context(ws):
   context = apx.Context()
   for swc in ws.findall('/ComponentType/*'):
      if isinstance(swc, autosar.component.AtomicSoftwareComponent):
         node = apx.Node().import_autosar_swc(swc)
         context.append(node)
   return context

def generate_apx_node(context, derived_dir):
   node_generator = apx.NodeGenerator()
   for node in context.nodes:
      node_generator.generate(derived_dir, node, includes=['Rte_Type.h'])

def save_apx_files(context, derived_dir):
   context.generateAPX(derived_dir)

if __name__ == '__main__':
   derived_dir = 'derived4'
   create_dir(derived_dir)
   ws = create_autosar_workspace()
   rte_partition = create_rte_partition(ws)
   generate_rte_types(rte_partition, derived_dir)
   context = create_apx_context(ws)
   generate_apx_node(context, derived_dir)
   save_apx_files(context, derived_dir)
