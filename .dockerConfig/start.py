from interactionfreepy import IFBroker
from interactionfreepy import IFLoop
from interactionfreepy import IFDefinition
import os

broker = IFBroker()
print('InteractionFree server start at port {}'.format(broker.address[2]))

certFiles = {
    "certfile": "/root/.config/ssl/server.crt",
    "keyfile": "/root/.config/ssl/server.key",
}
useSSL = os.path.exists(certFiles['certfile']) and os.path.exists(certFiles['keyfile'])
if useSSL:
    broker.startWebSocket(IFDefinition.DEFAULT_PORT_WEBSOCKET_SSL, '/wss/', certFiles)
    print('InteractionFree WebSocket server (SSL) start at port {}, /wss/'.format(IFDefinition.DEFAULT_PORT_WEBSOCKET_SSL))
else:
    broker.startWebSocket(IFDefinition.DEFAULT_PORT_WEBSOCKET, '/ws/')
    print('InteractionFree WebSocket server (no SSL) start at port {}, /ws/'.format(IFDefinition.DEFAULT_PORT_WEBSOCKET))

IFLoop.join()