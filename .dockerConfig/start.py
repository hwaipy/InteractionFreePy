""" InteractionFree server start script for docker container. """
import os
# pylint: disable=import-error
from interactionfreepy import IFBroker, IFLoop, IFDefinition
# pylint: enable=import-error

broker = IFBroker()
print(f'InteractionFree server start at port {broker.address[2]}')

certFiles = {
    "certfile": "/root/.config/ssl/server.crt",
    "keyfile": "/root/.config/ssl/server.key",
}
if os.path.exists(certFiles['certfile']) and os.path.exists(certFiles['keyfile']):
  broker.startWebSocket(IFDefinition.DEFAULT_PORT_WEBSOCKET_SSL, '/ws/', certFiles)
  print(f'InteractionFree WebSocket server (SSL) start at port {IFDefinition.DEFAULT_PORT_WEBSOCKET_SSL}, /ws/')
broker.startWebSocket(IFDefinition.DEFAULT_PORT_WEBSOCKET, '/ws/')
print(f'InteractionFree WebSocket server (no SSL) start at port {IFDefinition.DEFAULT_PORT_WEBSOCKET}, /ws/')

IFLoop.join()
