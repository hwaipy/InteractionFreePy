__license__ = "GNU General Public License v3"
__author__ = 'Hwaipy'
__email__ = 'hwaipy@gmail.com'

import zmq
from zmq.eventloop.zmqstream import ZMQStream
from interactionfreepy.core import IFDefinition, IFException, Invocation, Message, IFLoop
from tornado.ioloop import IOLoop
import time
import logging


class IFBroker(object):
    def __init__(self, binding, manager=None):
        socket = zmq.Context().socket(zmq.ROUTER)
        socket.bind(binding)
        self.main_stream = ZMQStream(socket, IOLoop.current())
        self.main_stream.on_recv(self.__onMessage)
        if manager == None:
            self.manager = Manager(self)
        else:
            self.manager = manager
        IFLoop.tryStart()

    def close(self):
        self.main_stream.on_recv(None)
        self.main_stream.socket.setsockopt(zmq.LINGER, 0)
        self.main_stream.socket.close()
        self.main_stream.close()
        self.main_stream = None

    def __onMessage(self, msg):
        try:
            sourcePoint, msg = msg[0], msg[1:]
            protocol = msg[1]
            if protocol != IFDefinition.PROTOCOL: raise IFException('Protocol {} not supported.'.format(protocol))
            distributingMode = msg[3]
            distributingAddress = msg[4]
            if distributingMode == IFDefinition.DISTRIBUTING_MODE_BROKER:
                IOLoop.current().add_callback(self.__onMessageDistributeLocal, sourcePoint, msg)
            elif distributingMode == IFDefinition.DISTRIBUTING_MODE_DIRECT:
                self.__onMessageDistributeDirect(sourcePoint, distributingAddress, msg)
            elif distributingMode == IFDefinition.DISTRIBUTING_MODE_SERVICE:
                self.__onMessageDistributeService(sourcePoint, distributingAddress, msg)
            else:
                raise IFException('Distributing mode {} not supported.'.format(distributingMode))
        except BaseException as e:
            logging.debug(e)

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
        except BaseException as e:
            if message:
                errorMsg = Message.newFromBrokerMessage(b'', Invocation.newError(message.messageID, str(e)))
                self.__sendMessage([sourcePoint] + errorMsg)

    def __onMessageDistributeService(self, sourcePoint, distributingAddress, msg):
        distributingAddress = str(distributingAddress, encoding='UTF-8')
        try:
            targetAddress = self.manager.getAddressOfService(sourcePoint, distributingAddress)
            if not targetAddress: raise IFException('Service {} not exist.'.format(distributingAddress))
            self.__sendMessage([targetAddress] + msg[:3] + [sourcePoint] + msg[5:])
        except BaseException as e:
            errorMsg = Message.newFromBrokerMessage(b'', Invocation.newError(Message(msg).messageID, str(e)))
            self.__sendMessage([sourcePoint] + errorMsg)

    def __onMessageDistributeDirect(self, sourcePoint, distributingAddress, msg):
        try:
            self.__sendMessage([distributingAddress] + msg[:3] + [sourcePoint] + msg[5:])
        except BaseException as e:
            errorMsg = Message.newFromBrokerMessage(b'', Invocation.newError(Message(msg).messageID, str(e)))
            self.__sendMessage([sourcePoint] + errorMsg)

    def __sendMessage(self, frames):
        self.main_stream.send_multipart(frames)


class Manager:
    def __init__(self, broker):
        self.broker = broker
        self.__workers = {}
        self.__services = {}
        self.__activities = {}
        IOLoop.current().call_later(2, self.__check)

    def registerAsService(self, sourcePoint, name, interfaces=[]):
        if self.__services.__contains__(name):
            raise IFException('Service name [{}] occupied.'.format(name))
        if self.__workers.__contains__(sourcePoint):
            raise IFException('The current worker has registered as [{}].'.format(name))
        self.__services[name] = [sourcePoint, interfaces, time.time()]
        self.__workers[sourcePoint] = name
        logging.info('Service [{}] registered as {}.'.format(name, interfaces))

    def unregister(self, sourcePoint):
        if self.__workers.__contains__(sourcePoint):
            serviceName = self.__workers.pop(sourcePoint)
            self.__services.pop(serviceName)
            logging.info('Service [{}] unregistered.'.format(serviceName))

    def protocol(self, sourcePoint):
        return str(IFDefinition.PROTOCOL, encoding='UTF-8')

    def heartbeat(self, sourcePoint):
        self.__activities[sourcePoint] = time.time()
        return self.__workers.__contains__(sourcePoint)

    def getAddressOfService(self, sourcePoint, serviceName):
        if self.__services.__contains__(serviceName):
            return self.__services.get(serviceName)[0]
        return None

    def listServiceNames(self, sourcePoint):
        return list(self.__services.keys())

    def listServiceMeta(self, sourcePoint):
        results = []
        currentTime = time.time()
        for s in self.__services:
            meta = self.__services[s]
            results.append([s, meta[0], meta[1], currentTime - meta[2]])
        return results

    def __check(self):
        currentTime = time.time()
        for key in self.__activities.keys():
            lastActiviteTime = self.__activities[key]
            timeDiff = currentTime - lastActiviteTime
            if timeDiff > IFDefinition.HEARTBEAT_LIVETIME:
                self.unregister(key)
        IOLoop.current().call_later(2, self.__check)


if __name__ == '__main__':
    broker = IFBroker("tcp://*:2224")
    IFLoop.join()