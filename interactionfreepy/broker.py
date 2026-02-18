"""IFBroker as the center server of InteractionFree."""
__license__ = "GNU General Public License v3"
__author__ = 'Hwaipy'
__email__ = 'hwaipy@gmail.com'

import time
import logging
import traceback
import ssl
import zmq
from zmq.eventloop.zmqstream import ZMQStream
from tornado import websocket, web, httpserver
from tornado.ioloop import IOLoop
from interactionfreepy.core import IFDefinition, IFException, Invocation, Message, IFLoop, IFAddress


class IFBroker:
  """
  IFBroker is the center server of InteractionFree.
  
  :param binding: The address to bind. Default is ``'*'``. The full address is expected to be in the format of ``'tcp://ip:port'``, while ``tcp://`` can be omitted, and the default port is ``1061``.
  :type binding: str
  :param manager: The manager to use. If not given, a default manager will be created.
  :type manager: Manager
  
  """

  def __init__(self, binding='*', manager=None):

    self.address = IFAddress.parseAddress(binding)
    socket = zmq.Context().socket(zmq.ROUTER)
    socket.bind(f'{self.address[0]}://{self.address[1]}:{self.address[2]}')
    self.main_stream = ZMQStream(socket, IOLoop.current())
    self.main_stream.on_recv(self.__onMessage)
    if manager is None:
      self.manager = Manager(self)
    else:
      self.manager = manager
      self.manager.broker = self
    IFLoop.tryStart()

  def close(self):
    """Close the server. All the connections will be closed."""
    self.main_stream.on_recv(None)
    self.main_stream.socket.setsockopt(zmq.LINGER, 0)
    # self.main_stream.socket.close()
    self.main_stream.close()
    self.main_stream = None

  def startWebSocket(self, port, path, sslOptions=None):
    '''Start a WebSocket server on the given port, with the given path. If sslOptions is given, the WebSocket server will use SSL.

    :param port: The port to listen.
    :type port: int
    :param path: The path to listen.
    :type path: str
    :param sslOptions: The SSL options. If not given, the WebSocket server will not use SSL. sslOptions should be a dict with two keys: ``'certfile'`` and ``'keyfile'``.
    :type sslOptions: dict
    :return: None
    '''
    handlersArray = [
        (path, WebSocketZMQBridgeHandler, {'port': self.address[2]}),
        (r"/(.+)", web.StaticFileHandler, {'path': 'interactionfreepy'}),
    ]
    app = web.Application(handlersArray)
    if sslOptions:
      sslCtx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
      sslCtx.load_cert_chain(sslOptions['certfile'], sslOptions['keyfile'])
      httpserver.HTTPServer(app, ssl_options=sslCtx).listen(port)
    else:
      app.listen(port)

  def __onMessage(self, msg):
    try:
      sourcePoint, msg = msg[0], msg[1:]
      protocol = msg[1]
      self.manager.statistics(sourcePoint, True, msg)
      if protocol != IFDefinition.PROTOCOL:
        raise IFException(f'Protocol {protocol} not supported.')
      distributingMode = msg[3]
      distributingAddress = msg[4]
      if distributingMode == IFDefinition.DISTRIBUTING_MODE_BROKER:
        IOLoop.current().add_callback(self.__onMessageDistributeLocal, sourcePoint, msg)
      elif distributingMode == IFDefinition.DISTRIBUTING_MODE_DIRECT:
        self.__onMessageDistributeDirect(sourcePoint, distributingAddress, msg)
      elif distributingMode == IFDefinition.DISTRIBUTING_MODE_SERVICE:
        self.__onMessageDistributeService(sourcePoint, distributingAddress, msg)
      else:
        raise IFException(f'Distributing mode {distributingMode} not supported.')
    except BaseException as exception:
      logging.debug(exception)

  async def __onMessageDistributeLocal(self, sourcePoint, msg):
    try:
      message = None
      message = Message(msg)
      invocation = message.getInvocation()
      result = self.manager.heartbeat(sourcePoint)
      if invocation.getFunction() != 'heartbeat':
        result = await invocation.perform(self.manager, sourcePoint)
      responseMessage = Message.newFromBrokerMessage(b'', Invocation.newResponse(message.messageID, result))
      self.__sendMessage([sourcePoint] + responseMessage)
    except BaseException as exception:
      if message:
        errorMsg = Message.newFromBrokerMessage(b'', Invocation.newError(message.messageID, str(exception)))
        self.__sendMessage([sourcePoint] + errorMsg)

  def __onMessageDistributeService(self, sourcePoint, distributingAddress, msg):
    distributingAddress = str(distributingAddress, encoding='UTF-8')
    try:
      targetAddress = self.manager.getAddressOfService(sourcePoint, distributingAddress)
      if not targetAddress:
        raise IFException(f'Service {distributingAddress} not exist.')
      self.__sendMessage([targetAddress] + msg[:3] + [sourcePoint] + msg[5:])
    except BaseException as exception:
      errorMsg = Message.newFromBrokerMessage(b'', Invocation.newError(Message(msg).messageID, str(exception)))
      self.__sendMessage([sourcePoint] + errorMsg)

  def __onMessageDistributeDirect(self, sourcePoint, distributingAddress, msg):
    try:
      self.__sendMessage([distributingAddress] + msg[:3] + [sourcePoint] + msg[5:])
    except BaseException as exception:
      errorMsg = Message.newFromBrokerMessage(b'', Invocation.newError(Message(msg).messageID, str(exception)))
      self.__sendMessage([sourcePoint] + errorMsg)

  def __sendMessage(self, frames):
    self.manager.statistics(frames[0], False, frames)
    self.main_stream.send_multipart(frames)


class Manager:
  """
  A service to manager workers of IFBroker. It can register workers as services, and distribute messages to workers.
  The functions below are also the default functions provided by the IFBroker. You can override them to customize the behavior of the IFBroker.
  Note: when invoking the functions by ``worker.function(argv)``, the parameter ``sourcePoint`` will be passed automatically. You don't need to pass it manually.
  """

  def __init__(self, broker=None):
    self.broker = broker
    self.__workers = {}
    self.__services = {}
    self.__activities = {}
    self.__nonservice = {}
    self.__previousGCTime = time.time()
    IOLoop.current().call_later(2, self.__check)

  def registerAsService(self, sourcePoint, name, interfaces=None, force=False):
    """Register a worker as a service.

    Args:
        sourcePoint (str): The source point of the invoker.
        name (str): The name of the service.
        interfaces (list): The interfaces of the service.
        force (bool): If True, the service will be registered even if the name is occupied. The old service will be replaced.
    """
    if name in self.__services and not force:
      raise IFException(f'Service name [{name}] occupied.')
    if sourcePoint in self.__workers:
      raise IFException(f'The current worker has registered as [{name}].')
    if interfaces is None:
      interfaces = []
    self.__services[name] = [sourcePoint, interfaces, time.time(), [0] * 4]
    self.__workers[sourcePoint] = name
    if sourcePoint in self.__nonservice:
      self.__nonservice.pop(sourcePoint)
    loggingMsg = f'Service [{name}] registered as {interfaces}.' if interfaces else f'Service [{name}] registered.'
    logging.info(loggingMsg)

  def unregister(self, sourcePoint):
    """Unregister a worker.

    Args:
        sourcePoint (str): The source point of the invoker.
    """
    if sourcePoint in self.__workers:
      serviceName = self.__workers.pop(sourcePoint)
      if serviceName in self.__services and self.__services[serviceName][0] == sourcePoint:
        self.__services.pop(serviceName)
        loggingMsg = f'Service [{serviceName}] unregistered.'
        logging.info(loggingMsg)

  def protocol(self, sourcePoint):
    """Get the protocol of IFBroker.
    
    Args:
        sourcePoint (str): The source point of the invoker. Not used.

    Returns:
        str: The protocol of IFBroker. Default is ``b'IF1'``.
    """
    return str(IFDefinition.PROTOCOL, encoding='UTF-8')

  def heartbeat(self, sourcePoint):
    """Sending heartbeat package to the IFBroker.
    
    Args:
        sourcePoint (str): The source point of the invoker.
    
    Returns:
        bool: True if the worker is registered as a service.
    """
    self.__activities[sourcePoint] = time.time()
    return sourcePoint in self.__workers

  def getAddressOfService(self, sourcePoint, serviceName):
    """Get the address of a service.
    
    Args:
        sourcePoint (str): The source point of the invoker. Not used.
        serviceName (str): The name of the service.

    Returns:
        str: The address of the service.
    """
    if serviceName in self.__services:
      return self.__services.get(serviceName)[0]
    return None

  def listServiceNames(self, sourcePoint):
    """List all service names.
    
    Args:
        sourcePoint (str): The source point of the invoker. Not used.
    """
    return list(self.__services.keys())

  def listServiceMeta(self, sourcePoint):
    """List all service with meta informations.
    
    Args:
        sourcePoint (str): The source point of the invoker. Not used.
        
    Returns:
        list: A list of service meta informations.
    """
    results = []
    currentTime = time.time()

    for serviceName, meta in self.__services.items():
      results.append({
          "ServiceName": serviceName,
          "Address": meta[0],
          "Interfaces": meta[1],
          "OnTime": currentTime - meta[2],
          "Statistics": {
              "Received Message": meta[3][0],
              "Received Bytes": meta[3][1],
              "Sent Message": meta[3][2],
              "Sent Bytes": meta[3][3],
          }})
    for serviceName, meta in self.__nonservice.items():
      results.append({
          "ServiceName": '',
          "Address": serviceName,
          "Interfaces": '',
          "OnTime": currentTime - meta[0],
          "Statistics": {
              "Received Message": meta[2][0],
              "Received Bytes": meta[2][1],
              "Sent Message": meta[2][2],
              "Sent Bytes": meta[2][3],
          }})
    return results

  def time(self, sourcePoint):
    return time.time()

  def statistics(self, sourcePoint, isReceived, message):
    """Get the statistics information of the IFBroker.
    
    Args:
        sourcePoint (str): The source point of the invoker.
        isReceived (bool): If True, the message is received.  
        message (list): The message.
        
    Returns:
        list: A list of statistics information.
    """
    offset = 0 if isReceived else 2
    if sourcePoint in self.__workers:
      statItem = self.__services[self.__workers[sourcePoint]][3]
    else:
      if not sourcePoint in self.__nonservice:
        self.__nonservice[sourcePoint] = [time.time(), 0, [0] * 4]
      self.__nonservice[sourcePoint][1] = time.time()
      statItem = self.__nonservice[sourcePoint][2]
    statItem[offset] += 1
    statItem[offset + 1] += len(message[-1])

    if time.time() - self.__previousGCTime > 10:
      try:
        keys = []
        for key in self.__nonservice:
          keys.append(key)
        for key in keys:
          if self.__nonservice[key][1] < self.__previousGCTime:
            self.__nonservice.pop(key)
        self.__previousGCTime = time.time()
      except BaseException:
        exstr = traceback.format_exc()
        print(exstr)
    # print(self.__workers.__contains__(sourcePoint), statItem)

  # async def stopService(self, sourcePoint, serviceName):
  #     try:
  #         print(serviceName)
  #         # self.broker.main_stream.socket.disconnect(self.__services[serviceName][0])
  #         print('stoping')
  #         broker.
  #         # import asyncio
  #         # await asyncio.sleep(2)
  #         # print('stoped')
  #     except BaseException as e:
  #         print('exception')
  #         import traceback
  #         traceback.print_tb(e)

  def __check(self):
    # try:
    currentTime = time.time()
    tobeRemoved = []
    for key, lastActiviteTime in self.__activities.items():
      timeDiff = currentTime - lastActiviteTime
      if timeDiff > IFDefinition.HEARTBEAT_LIVETIME:
        tobeRemoved.append(key)
        print('unreg in check', key)
        self.unregister(key)
    for tbr in tobeRemoved:
      self.__activities.pop(tbr)
    # except BaseException as e:
    #     print('error in check', e)
    IOLoop.current().call_later(2, self.__check)


class WebSocketZMQBridgeHandler(websocket.WebSocketHandler):
  """The handler for WebSocket connection to the IFBroker."""

  def __init__(self, *args, **kwargs):
    super().__init__(*args)
    self.port = kwargs['port']
    self.currentMessage = []
    self.__endpoint = f'tcp://localhost:{self.port}'
    self.__stream = None

  def open(self, *args, **kwargs):
    """Open the WebSocket connection."""
    socket = zmq.Context().socket(zmq.DEALER)
    self.__stream = ZMQStream(socket, IOLoop.current())
    self.__stream.on_recv(self.__onReceive)
    self.__stream.socket.setsockopt(zmq.LINGER, 0)
    self.__stream.connect(self.__endpoint)

  def on_close(self, *_args, **_kwargs):
    self.__stream.close()

  def on_message(self, message):
    hasMore = message[0]
    self.currentMessage.append(message[1:])
    if not hasMore:
      sendingMessage = self.currentMessage
      self.currentMessage = []
      self.__stream.send_multipart(sendingMessage)

  def __onReceive(self, msg):
    for frame in msg[:-1]:
      self.write_message(b'\x01' + frame, binary=True)
    self.write_message(b'\x00' + msg[-1], binary=True)

  def check_origin(self, origin):
    return True

  def data_received(self, chunk: bytes):
    pass


if __name__ == '__main__':
  # broker = IFBroker(f"tcp://*:{IFDefinition.DEFAULT_PORT_TCP}")
  ifbroker = IFBroker()
  ifbroker.startWebSocket(IFDefinition.DEFAULT_PORT_WEBSOCKET_SSL, '/ws/',
  {
      "certfile": "/workspaces/InteractionFreePy/InteractionFreePy/.ssl/server.crt",
      "keyfile": "/workspaces/InteractionFreePy/InteractionFreePy/.ssl/server.key",
  }
  )
  print('started')

  from interactionfreepy import IFWorker
  print(IFWorker('tcp://127.0.0.1').listServiceNames())

  IFLoop.join()
