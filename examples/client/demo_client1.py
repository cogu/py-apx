#!/bin/env python3
import os, sys
import time
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import apx

@apx.DataListener.register
class MyApxWorker(apx.DataListener):
    def __init__(self, client):
        self.client = client
        client.set_listener(self) #register on_data method to be called when new data arrives
        self.DemoSignal3 = 0

    def on_data(self, port, value):
        print("%s: %s"%(port.name, str(value)))

    def connect(self):
        success = self.client.connect_tcp('localhost', 5000, False)
        if success:
            self.client.write_port('DemoSignal3', self.DemoSignal3)
        return success

    def run(self):
        if self.DemoSignal3 < 15:
            self.DemoSignal3 += 1
            self.client.write_port('DemoSignal3', self.DemoSignal3)

    def stop(self):
        self.client.stop()


if __name__ == '__main__':
    node = apx.Node('PythonDemo1')
    node.append(apx.ProvidePort('DemoSignal3','C(0,15)', '=15'))
    node.append(apx.RequirePort('DemoSignal1','C(0,3)', '=3'))

    with apx.Client(node) as client:
        worker = MyApxWorker(client)
        if worker.connect():
            while True:
                try:
                    time.sleep(0.01)
                    worker.run()
                except (KeyboardInterrupt, SystemExit):
                    break
