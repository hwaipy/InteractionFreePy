import sys
sys.path.append('/workspaces/InteractionFreePy/InteractionFreePy')

from interactionfreepy import IFBroker
from interactionfreepy.broker import Manager

class CustomManager(Manager):
    def echo(self, sourcePoint, message):
        return f'ECHO: {message}'

    def whatIsMyID(self, sourcePoint):
        return f'Your ID is {sourcePoint}.'

    def registerAsService(self, sourcePoint, name, interfaces=None, force=False):
        if not name or not name[0].isalpha() or not name[0].isupper():
          raise Exception('The first letter of the service name should be uppercase.')
        return super().registerAsService(sourcePoint, name, interfaces, force)

broker = IFBroker(manager=CustomManager())

from interactionfreepy import IFWorker
worker = IFWorker('tcp://localhost:1061')
print(worker.listServiceNames())
echo = worker.echo('response to me!')
myID = worker.whatIsMyID()
print(echo)
print(myID)

worker = IFWorker('tcp://localhost:1061', 'Dlower', '')

import time
time.sleep(3)