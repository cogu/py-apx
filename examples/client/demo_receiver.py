#!/bin/env python3
"""
Demo APX receiver
It simply prints all values it receives
Launch demo_receiver.py in parallel to see the values.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import apx
import time

@apx.DataListener.register
class MyDataListener(apx.DataListener):
    def on_data(self, port, value):
        print(f"{port.name}: {repr(value)}")

if __name__ == '__main__':

    node = apx.Node('DemoReceiver')
    node.append(apx.RequirePort('DemoSignal','C(0,15)', '=15'))

    with apx.Client(node) as client:
        client.set_listener(MyDataListener())
        if client.connect_tcp('localhost', 5000):
            while True:
                try:
                   time.sleep(1)
                except (KeyboardInterrupt, SystemExit):
                    break