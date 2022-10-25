__license__ = "GNU General Public License v3"
__author__ = 'Hwaipy'
__email__ = 'hwaipy@gmail.com'

import threading
import msgpack
import re
from tornado.ioloop import IOLoop
from threading import Thread
import types
# import nest_asyncio


class IFDefinition:
    PROTOCOL = b'IF1'
    DISTRIBUTING_MODE_BROKER = b'Broker'
    DISTRIBUTING_MODE_DIRECT = b'Direct'
    DISTRIBUTING_MODE_SERVICE = b'Service'
    HEARTBEAT_LIVETIME = 10
    DEFAULT_PORT_TCP = 1061
    DEFAULT_PORT_WEBSOCKET_SSL = 1062
    DEFAULT_PORT_WEBSOCKET = 1063


class IFException(Exception):
    def __init__(self, description):
        Exception.__init__(self)
        self.description = description

    def __str__(self):
        return self.description


class IFLoop:
    __loopLock = threading.Lock()
    __running = False
    __loopingThread = None
    # nest_asyncio.apply()
    __INSTANCE = None

    @classmethod
    def start(cls, background=True):
        if not IFLoop.__runIfNot(): raise IFException('IFLoop is already running.')
        if background:
            thread = Thread(target=IFLoop.getInstance().start)
            thread.setDaemon(True)
            thread.start()
            IFLoop.__loopingThread = thread
        else:
            IFLoop.__loopingThread = threading.current_thread()
            IFLoop.getInstance().start()

    @classmethod
    def tryStart(cls):
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
        IFLoop.__loopingThread.join()

    @classmethod
    def getInstance(cls):
        if not IFLoop.__INSTANCE:
            IFLoop.__INSTANCE = IOLoop.current()
        return IFLoop.__INSTANCE

class Message:
    MessageIDs = 0
    __mutex__ = threading.Lock()

    @classmethod
    def newBrokerMessage(cls, invocation, serialization='Msgpack'):
        return Message.newMessage(IFDefinition.DISTRIBUTING_MODE_BROKER, b'', invocation, serialization)

    @classmethod
    def newServiceMessage(cls, serviceName, invocation, serialization='Msgpack'):
        return Message.newMessage(IFDefinition.DISTRIBUTING_MODE_SERVICE, serviceName, invocation, serialization)

    @classmethod
    def newDirectMessage(cls, address, invocation, serialization='Msgpack'):
        return Message.newMessage(IFDefinition.DISTRIBUTING_MODE_DIRECT, address, invocation, serialization)

    @classmethod
    def newMessage(cls, distributingMode, distributingAddress, invocation, serialization='Msgpack'):
        if (distributingMode != IFDefinition.DISTRIBUTING_MODE_BROKER) and (
                distributingMode != IFDefinition.DISTRIBUTING_MODE_DIRECT) and (
                distributingMode != IFDefinition.DISTRIBUTING_MODE_SERVICE): raise IFException(
            'Bad DistributingMode: {}'.format(distributingMode))
        if distributingMode == IFDefinition.DISTRIBUTING_MODE_BROKER: distributingAddress = b''
        # if serialization == 'Plain' or serialization == 'Default' or serialization == 'ZMQ': serialization = b''
        id = Message.__getAndIncrementID()
        id = str(id)
        msg = [b'', IFDefinition.PROTOCOL, id, distributingMode, distributingAddress,
               serialization, invocation.serialize(serialization)]
        return Message([Message.__messagePartToBytes(m) for m in msg])

    @classmethod
    def newFromBrokerMessage(cls, fromAddress, invocation, serialization='Msgpack'):
        id = Message.__getAndIncrementID()
        id = str(id)
        msg = [b'', IFDefinition.PROTOCOL, id, fromAddress, serialization, invocation.serialize(serialization)]
        return [Message.__messagePartToBytes(m) for m in msg]

    @classmethod
    def __getAndIncrementID(cls):
        Message.__mutex__.acquire()
        id = Message.MessageIDs
        Message.MessageIDs += 1
        Message.__mutex__.release()
        return id

    @classmethod
    def __messagePartToBytes(self, p):
        if isinstance(p, bytes): return p
        if isinstance(p, str): return bytes(p, 'UTF-8')
        if p == None: return b''
        raise IFException('Data type not transportable: {}'.format(type(p)))

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
        return self.__protocol == IFDefinition.PROTOCOL

    def isOutgoingMessage(self):
        return len(self.__content) == 7

    def isBrokerMessage(self):
        return self.isOutgoingMessage() and self.__distributingMode == IFDefinition.DISTRIBUTING_MODE_BROKER

    def isServiceMessage(self):
        return self.isOutgoingMessage() and self.__distributingMode == IFDefinition.DISTRIBUTING_MODE_SERVICE

    def isDirectMessage(self):
        return self.isOutgoingMessage() and self.__distributingMode == IFDefinition.DISTRIBUTING_MODE_DIRECT

    def getInvocation(self, decoded=True):
        if not decoded:
            return self.__invocationContent
        if not self.__invocation:
            self.__invocation = Invocation.deserialize(self.__invocationContent, self.serialization)
        return self.__invocation

    def getContent(self):
        return self.__content

    def __str__(self):
        if self.isBrokerMessage():
            return 'Broker: [id={}] {}'.format(self.messageID, self.getInvocation())
        if self.isServiceMessage():
            return 'Service [{}]: [id={}] {}'.format(self.distributingAddress, self.messageID, self.getInvocation())
        if self.isDirectMessage():
            return 'Direct [{}]: [id={}] {}'.format(self.distributingAddress, self.messageID, self.getInvocation())
        else:
            return 'Receive from [{}]: [id={}] {}'.format('Broker' if self.fromAddress == b'' else self.fromAddress,
                                                          self.messageID, self.getInvocation())


class Invocation:
    KeyType = u'Type'
    KeyFunciton = u'Function'
    KeyArguments = u'Arguments'
    KeyKeyworkArguments = u'KeyworkArguments'
    KeyRespopnseID = u'ResponseID'
    KeyResult = u'Result'
    KeyError = u'Error'
    KeyWarning = u'Warning'
    ValueTypeRequest = u'Request'
    ValueTypeResponse = u'Response'
    Preserved = [KeyType, KeyFunciton, KeyArguments, KeyKeyworkArguments, KeyRespopnseID, KeyResult, KeyError,
                 KeyWarning]

    def __init__(self, content={}):
        self.__content = content

    def get(self, key, nilValid=True, nonKeyValid=True):
        if self.__content.__contains__(key):
            value = self.__content[key]
            if value == None:
                if nilValid:
                    return None
                else:
                    raise IFException("Nil value invalid with key {}.".format(key))
            else:
                return value
        elif (nonKeyValid):
            return None
        else:
            raise IFException("Invocation does not contains key {}.".format(key))

    def isRequest(self):
        return self.get(Invocation.KeyType) == Invocation.ValueTypeRequest

    def isResponse(self):
        return self.get(Invocation.KeyType) == Invocation.ValueTypeResponse

    def isError(self):
        return self.isResponse() and self.__content.__contains__(Invocation.KeyError)

    def hasWarning(self):
        return self.isResponse() and self.__content.__contains__(Invocation.KeyWarning)

    def getResponseID(self):
        if self.isResponse(): return self.get(Invocation.KeyRespopnseID)
        return None

    def getResult(self):
        if self.isResponse() and not self.isError():
            return self.get(Invocation.KeyResult)
        return None

    def getError(self):
        if self.isError(): return self.get(Invocation.KeyError)
        return None

    def getWarning(self):
        if self.isResponse(): return self.get(Invocation.KeyWarning)
        return None

    def getFunction(self):
        if self.isRequest():
            return self.get(Invocation.KeyFunciton)
        return None

    def getArguments(self):
        if self.isRequest():
            args = self.get(Invocation.KeyArguments)
            if args: return args if isinstance(args, list) else [args]
            return []
        return None

    def getKeywordArguments(self):
        if self.isRequest():
            kwargs = self.get(Invocation.KeyKeyworkArguments)
            return kwargs if kwargs else {}
        return None

    @classmethod
    def newRequest(cls, functionName, args, kwargs):
        return Invocation({
            Invocation.KeyType: Invocation.ValueTypeRequest,
            Invocation.KeyFunciton: functionName,
            Invocation.KeyArguments: args,
            Invocation.KeyKeyworkArguments: kwargs
        })

    @classmethod
    def newResponse(cls, messageID, result):
        return Invocation({
            Invocation.KeyType: Invocation.ValueTypeResponse,
            Invocation.KeyRespopnseID: messageID,
            Invocation.KeyResult: result
        })

    @classmethod
    def newError(cls, messageID, description):
        return Invocation({
            Invocation.KeyType: Invocation.ValueTypeResponse,
            Invocation.KeyRespopnseID: messageID,
            Invocation.KeyError: description
        })

    def serialize(self, serialization='Msgpack'):
        if serialization == 'Msgpack':
            return msgpack.packb(self.__content, use_bin_type=True)
        else:
            raise IFException('Bad serialization: {}'.format(serialization))

    def __str__(self):
        content = ', '.join(['{}: {}'.format(k, self.__content[k]) for k in self.__content.keys()])
        return "Invocation [{}]".format(content)

    @classmethod
    def deserialize(cls, data, serialization='Msgpack', contentOnly=False):
        if isinstance(serialization, bytes): serialization = str(serialization, encoding='UTF-8')
        if serialization == 'Msgpack':
            unpacker = msgpack.Unpacker(raw=False)
            unpacker.feed(data)
            content = unpacker.__next__()
            return content if contentOnly else Invocation(content)
        else:
            raise IFException('Bad serialization: {}'.format(serialization))

    # sourcePoint only available for Broker.
    async def perform(self, target, sourcePoint=None):
        try:
            method = getattr(target, self.getFunction())
        except BaseException as e:
            raise IFException('Function [{}] not available.'.format(self.getFunction()))
        if not callable(method):
            raise IFException('Function [{}] not available.'.format(self.getFunction()))
        args = self.getArguments()
        kwargs = self.getKeywordArguments()
        if sourcePoint:
            args = [sourcePoint] + args
        try:
            result = method(*args, **kwargs)
            if (isinstance(result, types.CoroutineType)):
                return await result
            else:
                return result
        except BaseException as e:
            matchEargs = re.search("takes ([0-9]+) positional arguments but ([0-9]+) were given", str(e))
            if matchEargs:
                minus = 2 if sourcePoint else 1
                raise IFException('Function [{}] expects [{}] arguments, but [{}] were given.'
                                  .format(self.getFunction(),
                                          int(matchEargs.group(1)) - minus,
                                          int(matchEargs.group(2)) - minus))
            matchEkwargs = re.search("got an unexpected keyword argument '(.+)'", str(e))
            if matchEkwargs:
                raise IFException(
                    'Keyword Argument [{}] not availabel for function [{}].'.format(matchEkwargs.group(1),
                                                                                    self.getFunction()))
            raise e

        # noResponse = message.get(Message.KeyNoResponse)
        # if callable(method):
        #     try:
        #         result = method(*args, **kwargs)
        #         response = message.response(result)
        #         if noResponse is not True:
        #             self.communicator.sendLater(response)
        #     except BaseException as e:
        #         error = message.error(e.__str__())
        #         self.communicator.sendLater(error)
        #     return

class IFAddress:
    @classmethod
    def parseAddress(clz, address):
        sp1 = address.split('://')
        if len(sp1) > 2:
            raise ValueError(f'Invalid address: {address}')
        else:
            protocol = sp1[0] if len(sp1) == 2 else 'tcp'
            if protocol != 'tcp':
                raise ValueError(f'Invalid protocol "{protocol}" of address "{address}"')
            sp2 = sp1[-1].split(':')
            ip = sp2[0]
            port = IFDefinition().DEFAULT_PORT_TCP if len(sp2) == 1 else sp2[1]
            return [protocol, ip, port]

if __name__ == '__main__':
    print('test Core')
    inv = Invocation.newRequest('set', args=[i for i in range(100)] * 150000, kwargs={})
    bs = inv.serialize()
    print(len(bs))

    import random
    random.Random().randint(100000, 999999)

    import sys
    print(sys.path)