#!/bin/env python3
"""
Demo APX sender
It updates the demo signal value every second.
Launch demo_receiver.py in parallel to see the values.
"""
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import time
import apx

@apx.DataListener.register
class MyApxWorker(apx.DataListener):
    def __init__(self, client):
        self.client = client
        client.set_listener(self)
        self.DemoSignal = 0

    def on_data(self, port, value):
        pass

    def connect(self):
        success = self.client.connect_tcp('localhost', 5000, False)
        return success

    def run(self):
        if self.DemoSignal < 15:
            self.DemoSignal += 1
        else:
            self.DemoSignal = 0
        self.client.write_port('DemoSignal', self.DemoSignal)

    def stop(self):
        self.client.stop()


if __name__ == '__main__':
    node = apx.Node('DemoSender')
    node.append(apx.ProvidePort('DemoSignal','C(0,15)', '=15'))

    with apx.Client(node) as client:
        worker = MyApxWorker(client)
        client.write_port('DemoSignal', 0)
        if worker.connect():
            while True:
                try:
                    time.sleep(1)
                    worker.run()
                except (KeyboardInterrupt, SystemExit):
                    break
