import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import apx
import time

timer_init = 10

@apx.DataListener.register
class MyDataListener(apx.DataListener):
   def on_data(self, port, data):
      global value
      global client
      if port.name=='StressSignal2' and value is not None:
         value = value + 1
         client.write_port('StressSignal1', value)

if __name__ == '__main__':
   node = apx.Node('TestNode3')
   node.append(apx.ProvidePort('StressSignal1','L'))
   node.append(apx.RequirePort('StressSignal2','L'))
   value=1
   with apx.Client(node) as client:
      client.set_listener(MyDataListener())
      client.write_port('StressSignal1',value)
      if client.connect_tcp('localhost', 5000):
         while True:
            try:
               time.sleep(timer_init)
               events = value*2 # two signal events per loop
               value = None
               print("events={}. events/s: {}".format(events, events/timer_init))
               break
            except (KeyboardInterrupt, SystemExit):
               value = None
               break
