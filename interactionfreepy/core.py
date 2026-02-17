"""Core definitions and classes."""
__license__ = "GNU General Public License v3"
__author__ = 'Hwaipy'
__email__ = 'hwaipy@gmail.com'

import threading
import re
import types
from threading import Thread
from tornado.ioloop import IOLoop
import msgpack
# import nest_asyncio


class IFDefinition:
  """Some definitions of Interaction Free."""

  PROTOCOL = b'IF1'
  DISTRIBUTING_MODE_BROKER = b'Broker'
  DISTRIBUTING_MODE_DIRECT = b'Direct'
  DISTRIBUTING_MODE_SERVICE = b'Service'
  HEARTBEAT_LIVETIME = 10
  DEFAULT_PORT_TCP = 1061
  DEFAULT_PORT_WEBSOCKET_SSL = 1062
  DEFAULT_PORT_WEBSOCKET = 1063


class IFException(Exception):
  """Exception of Interaction Free."""

  def __init__(self, description):
    Exception.__init__(self)
    self.description = description

  def __str__(self):
    return self.description

class IFRemoteException(Exception):
  """Remote Exception of Interaction Free."""

  def __init__(self, remoteTraceback):
    Exception.__init__(self)
    self.remoteTraceback = remoteTraceback

  def __str__(self):
      return f'[Remote Exception]\n{"-" * 20 + " Remote Traceback below " + "-" * 20}\n{self.remoteTraceback}\n{"-" * 20 + " Remote Traceback above " + "-" * 20}\n'

class IFLoop:
  """A tool class to start the loop of Interaction Free."""

  __loopLock = threading.Lock()
  __running = False
  __loopingThread = None
  # nest_asyncio.apply()
  __INSTANCE = None

  @classmethod
  def start(cls, background=True):
    """Start the loop of Interaction Free."""
    if not IFLoop.__runIfNot():
      raise IFException('IFLoop is already running.')
    if background:
      thread = Thread(target=IFLoop.getInstance().start)
      thread.daemon = True
      thread.start()
      IFLoop.__loopingThread = thread
    else:
      IFLoop.__loopingThread = threading.current_thread()
      IFLoop.getInstance().start()

  @classmethod
  def tryStart(cls):
    """Start the loop of Interaction Free if not running."""
    if IFLoop.__runIfNot():
      thread = Thread(target=IFLoop.getInstance().start, daemon=True)
      thread.start()
      IFLoop.__loopingThread = thread

  @classmethod
  def __runIfNot(cls):
    IFLoop.__loopLock.acquire()
    if IFLoop.__running:
      IFLoop.__loopLock.release()
      return False
    IFLoop.__running = True
    IFLoop.__loopLock.release()
    return True

  @classmethod
  def join(cls):
    """Join the thread of Interaction Free loop."""
    IFLoop.__loopingThread.join()

  @classmethod
  def getInstance(cls):
    """Get the instance of Interaction Free loop."""
    if not IFLoop.__INSTANCE:
      IFLoop.__INSTANCE = IOLoop.current()
    return IFLoop.__INSTANCE


class Message:
  """A Message represent the content of Remote Procedure Call."""

  MessageIDs = 0
  __mutex__ = threading.Lock()

  @classmethod
  def newBrokerMessage(cls, invocation, serialization='Msgpack'):
    """Create a new message to send to broker.

    Args:
      invocation: The Invocation object to send.
      serialization: The serialization method of the message. Can be 'Msgpack', 'Plain' or 'Default'. 'Msgpack' is the default.

    Returns:
      A Message object.
    """
    return Message.newMessage(IFDefinition.DISTRIBUTING_MODE_BROKER, b'', invocation, serialization)

  @classmethod
  def newServiceMessage(cls, serviceName, invocation, serialization='Msgpack'):
    """Create a new message to send to a service.

    Args:
      serviceName: The name of the service.
      invocation: The Invocation object to send.
      serialization: The serialization method of the message. Can be 'Msgpack', 'Plain' or 'Default'. 'Msgpack' is the default.

    Returns:
      A Message object.

    Raises:
      IFException: If the service name is not a valid service name.
    """

    return Message.newMessage(IFDefinition.DISTRIBUTING_MODE_SERVICE, serviceName, invocation, serialization)

  @classmethod
  def newDirectMessage(cls, address, invocation, serialization='Msgpack'):
    """Create a new message to send to a direct address.

    Args:
      address: The address of the target.
      invocation: The Invocation object to send.
      serialization: The serialization method of the message. Can be 'Msgpack', 'Plain' or 'Default'. 'Msgpack' is the default.

    Returns:
      A Message object.

    Raises:
      IFException: If the address is not a valid address.
    """

    return Message.newMessage(IFDefinition.DISTRIBUTING_MODE_DIRECT, address, invocation, serialization)

  @classmethod
  def newMessage(cls, distributingMode, distributingAddress, invocation, serialization='Msgpack'):
    """Create a new message object.

    Args:
      distributingMode: The distributing mode of the message. Can be 'Broker', 'Direct' or 'Service'.
      distributingAddress: The address of the target. If the distributing mode is 'Broker', this should be empty. If the distributing mode is 'Direct', this should be the address of the target. If the distributing mode is 'Service', this should be the name of the service.
      invocation: The Invocation object to send.
      serialization: The serialization method of the message. Can be 'Msgpack', 'Plain' or 'Default'. 'Msgpack' is the default.

    Returns:
      A Message object.
    """
    if distributingMode not in [IFDefinition.DISTRIBUTING_MODE_BROKER, IFDefinition.DISTRIBUTING_MODE_DIRECT, IFDefinition.DISTRIBUTING_MODE_SERVICE]:
      raise IFException(f'Bad DistributingMode: {distributingMode}')
    if distributingMode == IFDefinition.DISTRIBUTING_MODE_BROKER:
      distributingAddress = b''
    # if serialization == 'Plain' or serialization == 'Default' or serialization == 'ZMQ': serialization = b''
    msg = [b'', IFDefinition.PROTOCOL, str(Message.__getAndIncrementID()), distributingMode, distributingAddress, serialization, invocation.serialize(serialization)]
    return Message([Message.__messagePartToBytes(m) for m in msg])

  @classmethod
  def newFromBrokerMessage(cls, fromAddress, invocation, serialization='Msgpack'):
    """Create a new message that is from broker, i.e., from another worker."""
    msg = [b'', IFDefinition.PROTOCOL, str(Message.__getAndIncrementID()), fromAddress, serialization, invocation.serialize(serialization)]
    return [Message.__messagePartToBytes(m) for m in msg]

  @classmethod
  def __getAndIncrementID(cls):
    Message.__mutex__.acquire()
    mid = Message.MessageIDs
    Message.MessageIDs += 1
    Message.__mutex__.release()
    return mid

  @classmethod
  def __messagePartToBytes(cls, part):
    if isinstance(part, bytes):
      return part
    if isinstance(part, str):
      return bytes(part, 'UTF-8')
    if part is None:
      return b''
    raise IFException(f'Data type not transportable: {type(part)}')

  def __init__(self, msgc):
    self.__content = msgc
    self.__protocol = msgc[1]
    self.messageID = msgc[2].decode('UTF-8')
    if self.isOutgoingMessage():
      self.__distributingMode = msgc[3]
      self.distributingAddress = msgc[4]
      self.serialization = msgc[5]
      self.__invocationContent = msgc[6]
    else:
      self.__distributingMode = b'Received'
      self.fromAddress = msgc[3]
      self.serialization = msgc[4]
      self.__invocationContent = msgc[5]
    self.__invocation = None

  def isProtocolValid(self):
    """Check if the protocol of the message is valid."""
    return self.__protocol == IFDefinition.PROTOCOL

  def isOutgoingMessage(self):
    """Check if the message is an outgoing message.
    
    Returns:
      True if the message is an outgoing message, False otherwise.
    """
    return len(self.__content) == 7

  def isBrokerMessage(self):
    """Check if the message is a broker message.
    
    Returns:
      True if the message is a broker message, False otherwise.
    """
    return self.isOutgoingMessage() and self.__distributingMode == IFDefinition.DISTRIBUTING_MODE_BROKER

  def isServiceMessage(self):
    """Check if the message is a service message.
    
    Returns:
      True if the message is a service message, False otherwise.
    """
    return self.isOutgoingMessage() and self.__distributingMode == IFDefinition.DISTRIBUTING_MODE_SERVICE

  def isDirectMessage(self):
    """Check if the message is a direct message.
    
    Returns:
      True if the message is a direct message, False otherwise.
    """
    return self.isOutgoingMessage() and self.__distributingMode == IFDefinition.DISTRIBUTING_MODE_DIRECT

  def getInvocation(self, decoded=True):
    """Get the invocation of the message.
    
    Args:
      decoded: If True, the invocation object will be deserialized as an Invocation object. If False, the raw content will be returned.
      
    Returns:
      The invocation object or the raw content of the invocation.
    """
    if not decoded:
      return self.__invocationContent
    if not self.__invocation:
      self.__invocation = Invocation.deserialize(self.__invocationContent, self.serialization)
    return self.__invocation

  def getContent(self):
    """Get the raw content of the message.
    
    Returns:
      The raw content of the message.
    """
    return self.__content

  def __str__(self):
    if self.isBrokerMessage():
      return f'Broker: [id={self.messageID}] {self.getInvocation()}'
    if self.isServiceMessage():
      return f'Service [{self.distributingAddress}]: [id={self.messageID}] {self.getInvocation()}'
    if self.isDirectMessage():
      return f'Direct [{self.distributingAddress}]: [id={self.messageID}] {self.getInvocation()}'
    return f'Receive from [{"Broker" if self.fromAddress == b"" else self.fromAddress}]: [id={self.messageID}] {self.getInvocation()}'


class Invocation:
  """The Invocation class represents an invocation of a function."""

  KeyType = 'Type'
  KeyFunciton = 'Function'
  KeyArguments = 'Arguments'
  KeyKeyworkArguments = 'KeyworkArguments'
  KeyRespopnseID = 'ResponseID'
  KeyResult = 'Result'
  KeyError = 'Error'
  KeyWarning = 'Warning'
  ValueTypeRequest = 'Request'
  ValueTypeResponse = 'Response'
  Preserved = [KeyType, KeyFunciton, KeyArguments, KeyKeyworkArguments, KeyRespopnseID, KeyResult, KeyError,
               KeyWarning]

  def __init__(self, content=None):
    self.__content = content if content is not None else {}

  def get(self, key, nilValid=True, nonKeyValid=True):
    """Get the value of the key.
    
    Args:
      key: The key of the value.
      nilValid: If True, the value can be None.
      nonKeyValid: If True, the key does not need to exist.
      
    Returns:
      The value of the key.
    """
    if key in self.__content:
      value = self.__content[key]
      if value is None:
        if nilValid:
          return None
        raise IFException(f"Nil value invalid with key {key}.")
      return value
    if nonKeyValid:
      return None
    raise IFException(f"Invocation does not contains key {key}.")

  def isRequest(self):
    """Check if the invocation is a request.
    
    Returns:
      True if the invocation is a request.
    """
    return self.get(Invocation.KeyType) == Invocation.ValueTypeRequest

  def isResponse(self):
    """Check if the invocation is a response.
    
    Returns:
      True if the invocation is a response.
    """
    return self.get(Invocation.KeyType) == Invocation.ValueTypeResponse

  def isError(self):
    """Check if the invocation is an error.
    
    Returns:
      True if the invocation is an error.
    """
    return self.isResponse() and Invocation.KeyError in self.__content

  def hasWarning(self):
    """Check if the invocation has a warning.
    
    Returns:
      True if the invocation has a warning.
    """
    return self.isResponse() and Invocation.KeyWarning in self.__content

  def getResponseID(self):
    """Get the response ID of the invocation. Only valid for response.
    
    Returns:
      The response ID of the invocation.
    """
    if self.isResponse():
      return self.get(Invocation.KeyRespopnseID)
    return None

  def getResult(self):
    """Get the result of the invocation. Only valid for response. If the invocation is an error, None will be returned.
    
    Returns:
      The result of the invocation. If the invocation is an error, None will be returned.
    """
    if self.isResponse() and not self.isError():
      return self.get(Invocation.KeyResult)
    return None

  def getError(self):
    """Get the error of the invocation. Only valid for response. If the invocation is not an error, None will be returned.
    
    Returns:
      The error of the invocation. If the invocation is not an error, None will be returned.
    """
    if self.isError():
      return self.get(Invocation.KeyError)
    return None

  def getWarning(self):
    """Get the warning of the invocation. Only valid for response. If the invocation has no warning, None will be returned.
    
    Returns:
      The warning of the invocation. If the invocation has no warning, None will be returned.
    """
    if self.isResponse():
      return self.get(Invocation.KeyWarning)
    return None

  def getFunction(self):
    """Get the function name of the invocation. Only valid for request.
    
    Returns:
      The function name of the invocation. If the invocation is not a request, None will be returned.
    """
    if self.isRequest():
      return self.get(Invocation.KeyFunciton)
    return None

  def getArguments(self):
    """Get the arguments of the invocation. Only valid for request.
    
    Returns:
      The list of arguments of the invocation. If the invocation is not a request, None will be returned. If the invocation has no arguments, an empty list will be returned.
    """
    if self.isRequest():
      args = self.get(Invocation.KeyArguments)
      if args:
        return args if isinstance(args, list) else [args]
      return []
    return None

  def getKeywordArguments(self):
    """Get the keyword arguments of the invocation. Only valid for request.
    
    Returns:
      The dictionary of keyword arguments of the invocation. If the invocation is not a request, None will be returned. If the invocation has no keyword arguments, an empty dictionary will be returned.
    """
    if self.isRequest():
      kwargs = self.get(Invocation.KeyKeyworkArguments)
      return kwargs if kwargs else {}
    return None

  @classmethod
  def newRequest(cls, functionName, args, kwargs):
    """Create a new request invocation.
    
    Args:
      functionName: The name of the function.
      args: The list of arguments.
      kwargs: The dictionary of keyword arguments.
      
    Returns:
      The new request invocation.
    """
    return Invocation({
        Invocation.KeyType: Invocation.ValueTypeRequest,
        Invocation.KeyFunciton: functionName,
        Invocation.KeyArguments: args,
        Invocation.KeyKeyworkArguments: kwargs
    })

  @classmethod
  def newResponse(cls, messageID, result):
    """Create a new response invocation corresponding to the request message with specified messageID.

    Args:
      messageID: The ID of the request.
      result: The result of the request.

    Returns:
      The new response invocation.
    """
    return Invocation({
        Invocation.KeyType: Invocation.ValueTypeResponse,
        Invocation.KeyRespopnseID: messageID,
        Invocation.KeyResult: result
    })

  @classmethod
  def newError(cls, messageID, description):
    """Create a new error response invocation corresponding to the request message with specified messageID.
    
    Args:
      messageID: The ID of the request.
      description: The description of the error.
      
    Returns:
      The new error response invocation.
    """
    return Invocation({
        Invocation.KeyType: Invocation.ValueTypeResponse,
        Invocation.KeyRespopnseID: messageID,
        Invocation.KeyError: description
    })

  def serialize(self, serialization='Msgpack'):
    """Serialize the invocation.
    
    Args:
      serialization: The serialization method. Currently only 'Msgpack' is supported.
    
    Returns:
      The serialized binary data.
    """
    if serialization == 'Msgpack':
      return msgpack.packb(self.__content, use_bin_type=True)
    raise IFException(f'Bad serialization: {serialization}')

  def __str__(self):
    content = ', '.join([f'{k}: {self.__content[k]}' for k in self.__content.keys()])
    return f"Invocation [{content}]"

  @classmethod
  def deserialize(cls, data, serialization='Msgpack', contentOnly=False):
    """Deserialize the invocation.
    
    Args:
      data: The serialized binary data.
      serialization: The serialization method. Currently only 'Msgpack' is supported.
      contentOnly: If True, only the content will be returned. Otherwise, an Invocation object will be returned.
      
    Returns:
      The content of the invocation. If contentOnly is False, an Invocation object will be returned.
    """
    if isinstance(serialization, bytes):
      serialization = str(serialization, encoding='UTF-8')
    if serialization == 'Msgpack':
      unpacker = msgpack.Unpacker(raw=False)
      unpacker.feed(data)
      content = unpacker.unpack()
      return content if contentOnly else Invocation(content)
    raise IFException(f'Bad serialization: {serialization}')

  async def perform(self, target, sourcePoint=None):
    """Perform the invocation on the target object. The target object must have a function with the same name as the invocation function. The arguments of the invocation will be passed to the function.
    
    Args:
      target: The target object.
      sourcePoint: The source point of the invocation. Only available for Broker.
      
    Returns:
      The result of the invocation."""
    try:
      method = getattr(target, self.getFunction())
    except BaseException as exception:
      raise IFException(f'Function [{self.getFunction()}] not available.') from exception
    if not callable(method):
      raise IFException(f'Function [{self.getFunction()}] not available.')
    args = self.getArguments()
    kwargs = self.getKeywordArguments()
    if sourcePoint:
      args = [sourcePoint] + args
    try:
      result = method(*args, **kwargs)
      if isinstance(result, types.CoroutineType):
        return await result
      return result
    except BaseException as exception:
      matchEargs = re.search("takes ([0-9]+) positional arguments but ([0-9]+) were given", str(exception))
      if matchEargs:
        minus = 2 if sourcePoint else 1
        raise IFException(f'Function [{self.getFunction()}] expects [{int(matchEargs.group(1)) - minus}] arguments, but [{int(matchEargs.group(2)) - minus}] were given.') from exception
      matchEkwargs = re.search("got an unexpected keyword argument '(.+)'", str(exception))
      if matchEkwargs:
        raise IFException(f'Keyword Argument [{matchEkwargs.group(1)}] not availabel for function [{self.getFunction()}].') from exception
      raise exception


class IFAddress:
  """A utility class for parsing address."""

  @classmethod
  def parseAddress(cls, address):
    """Parse the address.
    
    Args:
      address: The address to be parsed.
      
    Returns:
      A list of [protocol, ip, port]. If the address is invalid, an exception will be raised.
    """
    sp1 = address.split('://')
    if len(sp1) > 2:
      raise ValueError(f'Invalid address: {address}')
    protocol = sp1[0] if len(sp1) == 2 else 'tcp'
    if protocol != 'tcp':
      raise ValueError(f'Invalid protocol "{protocol}" of address "{address}"')
    sp2 = sp1[-1].split(':')
    port = IFDefinition().DEFAULT_PORT_TCP if len(sp2) == 1 else sp2[1]
    return [protocol, sp2[0], port]


if __name__ == '__main__':
  print('test Core')
  # inv = Invocation.newRequest('set', args=[i for i in range(100)] * 150000, kwargs={})
  # bs = inv.serialize()
  # print(len(bs))

  # import random
  # random.Random().randint(100000, 999999)

  # import sys
  # print(sys.path)
  