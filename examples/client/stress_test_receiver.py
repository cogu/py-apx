#!/bin/env python3
"""
This script counts the number of APX events seen during
a 10 second interval.

Launch stress_test_sender.py first, then launch this script.
It will report the result after 10 seconds then shut down.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import apx
import time

timer_init = 10

@apx.DataListener.register
class MyDataListener(apx.DataListener):
   def on_data(self, port, value):
      global value1
      global client
      if port.name=='StressSignal2' and value is not None:
         value1 = value + 1
         client.write_port('StressSignal1', value1)

if __name__ == '__main__':
   node = apx.Node('StressTestReceiver')
   node.append(apx.ProvidePort('StressSignal1','L'))
   node.append(apx.RequirePort('StressSignal2','L'))
   value1=1
   with apx.Client(node) as client:
      client.set_listener(MyDataListener())
      client.write_port('StressSignal1',value1)
      if client.connect_tcp('localhost', 5000):
         while True:
            try:
               print("Collecting events...")
               time.sleep(timer_init)
               events = value1*2 # two signal events per loop
               value1 = None
               print("events={}. events/s: {}".format(events, events/timer_init))
               break
            except (KeyboardInterrupt, SystemExit):
               value1 = None
               break
