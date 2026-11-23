import sys,os
import autosar
sys.path.insert(0,'../..')
import apx

TYPE_HEADER = 'CustomTypes.h'

def create_dir(dir_name):
   if not os.path.exists(dir_name):
      os.makedirs(dir_name)

def create_autosar_workspace():
   ws = autosar.workspace()
   dataTypes = ws.createPackage('DataType', role='DataType')
   dataTypes.createSubPackage('CompuMethod', role='CompuMethod')
   dataTypes.createSubPackage('Unit', role='Unit')
   dataTypes.createIntegerDataType('OffOn_T', valueTable=[
          "OffOn_Off",
          "OffOn_On",
          "OffOn_Error",
          "OffOn_NotAvailable"])
   dataTypes.createIntegerDataType('Percent_T', min=0, max=255, offset=0, scaling=0.4, unit='Percent')
   dataTypes.createIntegerDataType('VehicleSpeed_T', min=0, max=65535, offset=0, scaling=1/64, unit='km/h')
   dataTypes.createIntegerDataType('EngineSpeed_T', min=0, max=65535, offset=0, scaling=1/8, unit='rpm')
   dataTypes.createIntegerDataType('Seconds_T', min=0, max=63, offset=0, scaling=1, unit='Seconds')
   constants = ws.createPackage('Constant', role='Constant')
   constants.createConstant('C_EngineRunningStatus_IV', 'OffOn_T', 3)
   constants.createConstant('C_FuelLevelPercent_IV', 'Percent_T', 255)
   constants.createConstant('C_VehicleSpeed_IV', 'VehicleSpeed_T', 65535)
   constants.createConstant('C_EngineSpeed_IV', 'EngineSpeed_T', 0)
   constants.createConstant('C_Rtc_Seconds_IV', 'Seconds_T', 63)
   portInterfaces = ws.createPackage('PortInterface', role='PortInterface')
   portInterfaces.createSenderReceiverInterface('EngineRunningStatus_I', autosar.DataElement('EngineRunningStatus', 'OffOn_T'))
   portInterfaces.createSenderReceiverInterface('FuelLevelPercent_I', autosar.DataElement('FuelLevelPercent', 'Percent_T'))
   portInterfaces.createSenderReceiverInterface('VehicleSpeed_I', autosar.DataElement('VehicleSpeed', 'VehicleSpeed_T'))
   portInterfaces.createSenderReceiverInterface('EngineSpeed_I', autosar.DataElement('EngineSpeed','EngineSpeed_T'))
   portInterfaces.createSenderReceiverInterface('Rtc_Seconds_I', autosar.DataElement('Rtc_Seconds','Seconds_T'))
   components = ws.createPackage('ComponentType', role='ComponentType')
   swc = components.createApplicationSoftwareComponent('Example3')
   swc.createProvidePort('EngineRunningStatus', 'EngineRunningStatus_I', initValueRef=constants['C_EngineRunningStatus_IV'].ref)
   swc.createProvidePort('VehicleSpeed', 'VehicleSpeed_I', initValueRef=constants['C_VehicleSpeed_IV'].ref)
   swc.createRequirePort('Rtc_Seconds', 'Rtc_Seconds_I', initValueRef=constants['C_Rtc_Seconds_IV'].ref)
   swc.createRequirePort('FuelLevelPercent', 'FuelLevelPercent_I', initValueRef=constants['C_FuelLevelPercent_IV'].ref)
   swc.createRequirePort('EngineSpeed', 'EngineSpeed_I', initValueRef=constants['C_EngineSpeed_IV'].ref)
   swc.behavior.createRunnable(swc.name+'_Init', portAccess=[x.name for x in swc.providePorts])
   swc.behavior.createRunnable(swc.name+'_Run', portAccess=[x.name for x in swc.requirePorts+swc.providePorts])
   return ws

def create_rte_partition(ws):
   partition = autosar.rte.Partition()
   for swc in ws.findall('/ComponentType/*'):
      if isinstance(swc, autosar.component.AtomicSoftwareComponent):
         partition.addComponent(swc)
   return partition

def generate_rte_types(partition, derived_dir):
   type_generator = autosar.rte.TypeGenerator(partition)
   type_generator.generate(derived_dir, file_name=TYPE_HEADER)

def create_apx_context(ws):
   context = apx.Context()
   for swc in ws.findall('/ComponentType/*'):
      if isinstance(swc, autosar.component.AtomicSoftwareComponent):
         node = apx.Node().import_autosar_swc(swc)
         context.append(node)
   return context

def generate_apx_node(context, derived_dir):
   node_generator = apx.NodeGenerator()
   node = context.nodes[0]
   callback_map = {'FuelLevelPercent': node.name+'_FuelLevelPercent_Cbk',
                   'EngineSpeed': node.name+'_EngineSpeed_Cbk'}
   node_generator.generate(derived_dir, node, includes=[TYPE_HEADER], callbacks = callback_map)

def save_apx_files(context, derived_dir):
   context.generateAPX(derived_dir)

if __name__ == '__main__':
   derived_dir = 'derived3'
   create_dir(derived_dir)
   ws = create_autosar_workspace()
   partition = create_rte_partition(ws)
   generate_rte_types(partition, derived_dir)
   context = create_apx_context(ws)
   generate_apx_node(context, derived_dir)
   save_apx_files(context, derived_dir)
