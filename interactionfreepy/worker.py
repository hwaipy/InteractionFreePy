""" InteractionFreePy Worker """
__license__ = "GNU General Public License v3"
__author__ = 'Hwaipy'
__email__ = 'hwaipy@gmail.com'

import time
import threading
import asyncio
import logging
import traceback
import zmq
from zmq.eventloop.zmqstream import ZMQStream
from interactionfreepy.core import IFException, Message, Invocation, IFLoop, IFDefinition, IFAddress


class IFWorker:
  """InteractionFreePy Worker class. """

  def __init__(self, endpoint, serviceName=None, serviceObject=None, interfaces=None, blocking=True, timeout=None, force=False):
    self.address = IFAddress.parseAddress(endpoint)
    self.socket = zmq.Context().socket(zmq.DEALER)
    self.__stream = ZMQStream(self.socket, IFLoop.getInstance())
    self.__stream.on_recv(self.__onMessage)
    self.__stream.socket.setsockopt(zmq.LINGER, 0)
    self.__stream.connect(f'{self.address[0]}://{self.address[1]}:{self.address[2]}')
    self.__waitingMap = {}
    self.__waitingMapLock = threading.Lock()
    self.blocking = blocking
    self.timeout = timeout
    self.__isService = False
    if serviceName is not None:
      self.bindService(serviceName, serviceObject, [] if interfaces is None else interfaces)
    threading.Thread(target=self.__hbLoop, daemon=True).start()
    IFLoop.tryStart()
    if self.__isService:
      self.registerAsService(self.__serviceName, self.__interfaces, force)

  def __hbLoop(self):
    while True:
      time.sleep(IFDefinition.HEARTBEAT_LIVETIME / 5)
      try:
        if not self.blockingInvoker(timeout=IFDefinition.HEARTBEAT_LIVETIME / 5).heartbeat() and self.__isService:
          self.registerAsService(self.__serviceName, self.__interfaces)
      except BaseException as exception:
        logging.warning('Heartbeat: %s', exception)

  def __onMessage(self, msg):
    try:
      message = Message(msg)
      invocation = message.getInvocation()
      if invocation.isRequest():
        IFLoop.getInstance().add_callback(self.__onRequest, message)
      elif invocation.isResponse():
        self.__onResponse(message)
    except BaseException:
      exstr = traceback.format_exc()
      logging.debug(exstr)

  async def __onRequest(self, message):
    sourcePoint = message.fromAddress
    invocation = message.getInvocation()
    try:
      if 'stopService' == invocation.getFunction():
        self.__isService = False
        result = await self.asyncInvoker().unregister()
      else:
        result = await invocation.perform(self.__serviceObject)
      responseMessage = Message.newDirectMessage(sourcePoint, Invocation.newResponse(message.messageID, result))
      self.__stream.send_multipart(responseMessage.getContent())
    except BaseException as exception:
      errorMsg = Message.newDirectMessage(sourcePoint, Invocation.newError(message.messageID, str(exception)))
      self.__stream.send_multipart(errorMsg.getContent())

  def __onResponse(self, message):
    invocation = message.getInvocation()
    correspondingID = invocation.getResponseID()
    self.__waitingMapLock.acquire()
    if correspondingID in self.__waitingMap:
      (futureEntry, runnable) = self.__waitingMap.pop(correspondingID)
      if invocation.isError():
        futureEntry['error'] = invocation.getError()
      else:
        futureEntry['result'] = invocation.getResult()
      if invocation.hasWarning():
        futureEntry['warning'] = invocation.getWarning()
      runnable()
    else:
      logging.debug('ResponseID not recognized: %s', message)
    self.__waitingMapLock.release()

  def send(self, msg):
    """Send a message by the worker.
    
    Args:
        msg (Message): The message to send.

    Returns:
        InvokeFuture: The future of the sending.
    """
    self.__stream.send_multipart(msg.getContent())
    mid = msg.messageID
    (future, onFinish, resultMap) = InvokeFuture.newFuture()
    self.__waitingMapLock.acquire()
    if mid in self.__waitingMap:
      raise IFException("MessageID have been used.")
    self.__waitingMap[mid] = (resultMap, onFinish)
    self.__waitingMapLock.release()
    return future

  def toMessageInvoker(self, target=None):
    """Create a invoker that generate Message objects only, without sending.
    
    Args:
        target (str): The target of the invoker.
        
    Returns:
        DynamicRemoteObject: The invoker.
    """
    return DynamicRemoteObject(None, toMessage=True, blocking=False, target=target, timeout=None)

  def asynchronousInvoker(self, target=None):
    """Create a non-blocking invoker.

    Args:
        target (str): The target of the invoker.
    
    Returns:
        AsyncRemoteObject: The invoker.

    Deprecated:
        This method is deprecated. Remove it in the future. Use asyncInvoker instead.
    """
    return DynamicRemoteObject(self, toMessage=False, blocking=False, target=target, timeout=None)

  def asyncInvoker(self, target=None):
    """Create an async invoker.
    
    Args:
        target (str): The target of the invoker.
        
    Returns:
        AsyncRemoteObject: The invoker.
    """
    return AsyncRemoteObject(self, target=target, timeout=30)

  def blockingInvoker(self, target=None, timeout=None):
    """Create a blocking invoker.
    
    Args:
        target (str): The target of the invoker.
        
    Returns:
        DynamicRemoteObject: The invoker.
    """
    return DynamicRemoteObject(self, toMessage=False, blocking=True, target=target, timeout=timeout)

  @classmethod
  def start(cls):
    IFLoop.getInstance().start()

  def __getattr__(self, item):
    return InvokeTarget(self, item)

  def close(self):
    """Close the worker. If the worker is a service, it will be unregistered.
    
    Returns:
        None
    """
    self.unregister()

  def bindService(self, serviceName, serviceObject, interfaces=None):
    """Bind the worker as a service.
    
    Args:
        serviceName (str): The name of the service.
        serviceObject (object): The object to be bind.
        interfaces (list): The interfaces of the service.
    
    Returns:
        None
    """
    if self.__isService:
      raise IFException('Service already bind.')
    self.__isService = serviceName is not None
    self.__serviceName = serviceName
    self.__serviceObject = serviceObject
    self.__interfaces = [] if interfaces is None else interfaces


class InvokeTarget:
  def __init__(self, worker, item):
    self.__worker = worker
    self.__name = item

  def __getattr__(self, item):
    item = '{}'.format(item)
    return self.__defaultInvoker(self.__name).__getattr__(item)

  def __call__(self, *args, **kwargs):
    invoker = self.__defaultInvoker('')
    func = invoker.__getattr__(self.__name)
    return func(*args, **kwargs)

  def __defaultInvoker(self, target):
    if self.__worker.blocking:
      return self.__worker.blockingInvoker(target, self.__worker.timeout)
    else:
      return self.__worker.asynchronousInvoker(target)


class RemoteObject(object):
  def __init__(self, name):
    self.name = name

  def __str__(self):
    return "RemoteObject[{}]".format(self.name)


class DynamicRemoteObject(RemoteObject):
  def __init__(self, worker, toMessage, blocking, target, timeout):
    super(DynamicRemoteObject, self).__init__(target)
    self.__worker = worker
    self.__target = target
    self.__toMessage = toMessage
    self.__blocking = blocking
    self.__timeout = timeout
    self.name = target

  def __getattr__(self, item):
    item = f'{item}'

    def invoke(*args, **kwargs):
      invocation = Invocation.newRequest(item, args, kwargs)
      if self.__target == '' or self.__target is None:
        message = Message.newBrokerMessage(invocation)
      else:
        message = Message.newServiceMessage(self.__target, invocation)
      if self.__toMessage:
        return message
      elif self.__blocking:
        return self.__worker.send(message).sync(self.__timeout)
      else:
        return self.__worker.send(message)

    return invoke

  def __str__(self):
    return f"DynamicRemoteObject[{self.name}]"


class AsyncRemoteObject(RemoteObject):
  def __init__(self, worker, target, timeout):
    super(AsyncRemoteObject, self).__init__(target)
    self.__worker = worker
    self.__target = target
    self._timeout = timeout
    self.name = target

  def __getattr__(self, item):
    item = f'{item}'

    async def invoke(*args, **kwargs):
      invocation = Invocation.newRequest(item, args, kwargs)
      if self.__target == '' or self.__target is None:
        message = Message.newBrokerMessage(invocation)
      else:
        message = Message.newServiceMessage(self.__target, invocation)
      invokeFuture = self.__worker.send(message)
      queue = asyncio.Queue()
      tobeAwait = queue.get()

      def onComplete():
        queue.put_nowait(invokeFuture)

      invokeFuture.onComplete(onComplete)
      invokeFuture = await tobeAwait
      if invokeFuture.isSuccess():
        return invokeFuture.result()
      else:
        raise invokeFuture.exception()

    return invoke

  def __str__(self):
    return f"AsyncRemoteObject[{self.name}]"


class InvokeFuture:
  @classmethod
  def newFuture(cls):
    future = InvokeFuture()
    return (future, future._onFinish, future.__resultMap)

  def __init__(self):
    self.__done = False
    self.__result = None
    self.__exception = None
    self.__warning = None
    self.__onComplete = None
    self.__metux = threading.Lock()
    self.__resultMap = {}
    self.__awaitSemaphore = threading.Semaphore(0)

  def isDone(self):
    return self.__done

  def isSuccess(self):
    return self.__exception is None

  def result(self):
    return self.__result

  def exception(self):
    return self.__exception

  def warning(self):
    return self.__warning

  def onComplete(self, func):
    self.__metux.acquire()
    self.__onComplete = func
    if self.__done:
      self.__onComplete()
    self.__metux.release()

  def waitFor(self, timeout=None):
    # For Python 3 only.
    if self.__awaitSemaphore.acquire(True, timeout):
      self.__awaitSemaphore.release()
      return True
    else:
      return False

  def sync(self, timeout=None):
    if self.waitFor(timeout):
      if self.isSuccess():
        return self.__result
      if isinstance(self.__exception, BaseException):
        raise self.__exception
      raise IFException('Error state in InvokeFuture.')
    raise IFException('Time out!')

  def _onFinish(self):
    self.__done = True
    if self.__resultMap.__contains__('result'):
      self.__result = self.__resultMap['result']
    if self.__resultMap.__contains__('warning'):
      self.__warning = self.__resultMap['warning']
    if self.__resultMap.__contains__('error'):
      self.__exception = IFException(self.__resultMap['error'])
    if self.__onComplete is not None:
      self.__onComplete()
    self.__awaitSemaphore.release()


if __name__ == '__main__':
  ifworker = IFWorker('127.0.0.1', 'TimeoutTest2', 'TimeoutTest2')
  print('TimeoutTest started')
  print(ifworker.listServiceNames())
  IFLoop().join()

  # class Target:
  #     def test(self, arg):
  #         print(arg)
  #         return 1.1

  # worker = IFWorker('tcp://172.16.60.200:81', 'TS', Target())
  # print(worker.listServiceMeta())
  # # print(worker.HMC7044EvalAlice.checkChannel(1))
  # IFLoop.join()
