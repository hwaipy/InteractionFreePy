from interactionfreepy import IFBroker
from interactionfreepy import IFLoop

broker = IFBroker('tcp://*:224')
broker.startWebSocket(81, '/ws/',
{
    "certfile": "/root/.config/OpenSSL/server.crt",
    "keyfile": "/root/.config/OpenSSL/server.key",
}
)
print('InteractionFree server start at port {}'.format(224))
IFLoop.join()