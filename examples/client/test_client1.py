import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import apx
import time

@apx.DataListener.register
class MyDataListener(apx.DataListener):
    def on_data(self, port, data):
        print("%s: %s"%(port.name, str(data)))

if __name__ == '__main__':
    node = apx.Node('TestNode1')
    node.append(apx.ProvidePort('TestSignal1','S'))
    node.append(apx.RequirePort('TestSignal2','S'))
    value=1

    with apx.Client(node) as client:
        client.set_listener(MyDataListener())
        client.write_port('TestSignal1',value)
        if client.connect_tcp('localhost', 5000):
            while True:
                try:
                    time.sleep(1)
                    value = (value + 1) & 0x3FFF #wraparound to zero after 16383
                    client.write_port('TestSignal1', value)
                except (KeyboardInterrupt, SystemExit):
                    break
