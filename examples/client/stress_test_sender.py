#!/bin/env python3
"""
This script attempts to send as many APX events as possible.
It's limited by the response time of the receiver.

Launch this script first, then launch stress_test_receiver.py.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import apx
import time

@apx.DataListener.register
class MyDataListener(apx.DataListener):
    global client
    def on_data(self, port, value):
        if port.name=='StressSignal1':
            client.write_port('StressSignal2', value)

if __name__ == '__main__':

    node = apx.Node('StressTestSender')
    node.append(apx.RequirePort('StressSignal1','L'))
    node.append(apx.ProvidePort('StressSignal2','L'))

    with apx.Client(node) as client:
        client.set_listener(MyDataListener())
        if client.connect_tcp('localhost', 5000):
            while True:
                try:
                   time.sleep(1)
                except (KeyboardInterrupt, SystemExit):
                    break