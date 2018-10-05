import apx
import autosar
import os

def createContextfromPartition(autosar_partition):
   context = Context()
   for component in autosar_partition.components:
      if (component.swc is not None) and (isinstance(component.swc, autosar.component.ApplicationSoftwareComponent)):
         swc = component.swc
         ws = swc.rootWS()
         apx_node = apx.Node(swc.name)
         for port in swc.requirePorts + swc.providePorts:
            portInterface = ws.find(port.portInterfaceRef)
            if portInterface is None:
               print('Warning (port=%s): PortInterface with ref %s not found in ECU extract'%(port.name, port.portInterfaceRef))
            else:
               if (type(portInterface) is autosar.portinterface.SenderReceiverInterface) and (len(portInterface.dataElements)>0):
                  apx_node.append(port)
         context.append(apx_node)
   return context

class Context:
   def __init__(self):
      self.nodes = []

   def append(self, node):
      assert(isinstance(node, apx.Node))
      self.nodes.append(node)
      return self

   def generateAPX(self, output_dir='.', normalized=False):
      """
      generates a new APX Text file for each node in context

      path argument is expected to be a output directory.

      Returns:
      A list containing the names of the generated files
      """
      file_list = []
      if not os.path.isdir(output_dir):
         raise ValueError('path variable not a directory')
      for node in self.nodes:
         file_name = os.path.normpath(os.path.join(output_dir, node.name+'.apx'))
         with open(file_name, "w", newline='\n') as fp:
            fp.write("APX/1.2\n") #APX Text header
            node.write(fp)
            fp.write("\n") #Add extra newline at end of file
         file_list.append(file_name)
      return file_list


   def dumps(self, normalized=False):
      """
      returns context as a string
      """
      lines = []
      lines.append("APX/1.2")
      for node in self.nodes:
         lines.extend(node.lines(normalized))
      text = '\n'.join(lines)+'\n'
      return text

