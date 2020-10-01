from interactionfreepy import IFBroker
from interactionfreepy import IFLoop

broker = IFBroker('tcp://*:224')
print('InteractionFree server start at port {}'.format(224))
IFLoop.join()
