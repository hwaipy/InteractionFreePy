import os
from interactionfreepy import IFBroker, IFLoop, IFDefinition

broker = IFBroker()
print(f'InteractionFree server start at port {broker.address[2]}')

certFiles = {
    "certfile": "/root/.config/ssl/server.crt",
    "keyfile": "/root/.config/ssl/server.key",
}
if os.path.exists(certFiles['certfile']) and os.path.exists(certFiles['keyfile']):
  broker.startWebSocket(IFDefinition.DEFAULT_PORT_WEBSOCKET_SSL, '/wss/', certFiles)
  print('InteractionFree WebSocket server (SSL) start at port {IFDefinition.DEFAULT_PORT_WEBSOCKET_SSL}, /wss/')
else:
  broker.startWebSocket(IFDefinition.DEFAULT_PORT_WEBSOCKET, '/ws/')
  print('InteractionFree WebSocket server (no SSL) start at port {IFDefinition.DEFAULT_PORT_WEBSOCKET}, /ws/')

IFLoop.join()
