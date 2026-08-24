import apx
from apx.parser import NodeParser

# 1. Create a new Node
node = apx.Node('Example')

# 2. Add custom Data Types
node.append(apx.DataType('BatteryVoltage_T', 'S'))
node.append(apx.DataType('Date_T', '{"Year"C"Month"C(1,13)"Day"C(1,32)}'))
node.append(apx.DataType(
    'InactiveActive_T',
    'C(0,3)',
    'VT("InactiveActive_Inactive", "InactiveActive_Active", "InactiveActive_Error", "InactiveActive_NotAvailable")'
))

# 3. Add Provide and Require Ports with Type References and Init Values
node.append(apx.ProvidePort('BatteryVoltage', 'T["BatteryVoltage_T"]', '=65535'))
node.append(apx.RequirePort('CurrentDate', 'T["Date_T"]', '={255, 13, 32}'))
node.append(apx.RequirePort('ExteriorLightsActive', 'T["InactiveActive_T"]', '=3'))

# 4. Finalize / Parse model
parser = NodeParser()
model_node = parser.from_base_node(node)
print(f"Created node '{model_node.name}' with {len(model_node.data_types)} types, "
      f"{len(model_node.provide_ports)} provide ports, {len(model_node.require_ports)} require ports.")
