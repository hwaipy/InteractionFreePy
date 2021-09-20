__license__ = "GNU General Public License v3"
__author__ = 'Hwaipy'
__email__ = 'hwaipy@gmail.com'

import zmq
from zmq.eventloop.zmqstream import ZMQStream
from interactionfreepy.core import IFDefinition, IFException, Invocation, Message, IFLoop
from tornado import websocket, web, httpserver
from tornado.ioloop import IOLoop
import time
import logging
import os
import ssl

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

    def startWebSocket(self, port, path, ssl_options=None):
        handlers_array = [
            (path, WebSocketZMQBridgeHandler),
            (r"/(.+)", web.StaticFileHandler, {'path': 'interactionfreepy'}),
        ]
        app = web.Application(handlers_array)
        if ssl_options:
            ssl_ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            ssl_ctx.load_cert_chain(ssl_options['certfile'], ssl_options['keyfile'])
            httpserver.HTTPServer(app, ssl_options=ssl_ctx).listen(port)
        else:
            app.listen(port)

    def __onMessage(self, msg):
        try:
            sourcePoint, msg = msg[0], msg[1:]
            protocol = msg[1]
            self.manager.statistics(sourcePoint, True, msg)
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
        self.manager.statistics(frames[0], False, frames)
        self.main_stream.send_multipart(frames)


class Manager:
    def __init__(self, broker):
        self.broker = broker
        self.__workers = {}
        self.__services = {}
        self.__activities = {}
        self.__nonserviceStatistics = [0] * 4
        self.__nonservice = {}
        self.__previousGCTime = time.time()
        IOLoop.current().call_later(2, self.__check)

    def registerAsService(self, sourcePoint, name, interfaces=[], force=False):
        if self.__services.__contains__(name) and not force:
            raise IFException('Service name [{}] occupied.'.format(name))
        if self.__workers.__contains__(sourcePoint):
            raise IFException('The current worker has registered as [{}].'.format(name))
        self.__services[name] = [sourcePoint, interfaces, time.time(), [0] * 4]
        self.__workers[sourcePoint] = name
        if self.__nonservice.__contains__(sourcePoint): self.__nonservice.pop(sourcePoint)
        logging.info('Service [{}] registered as {}.'.format(name, interfaces))

    def unregister(self, sourcePoint):
        if self.__workers.__contains__(sourcePoint):
            serviceName = self.__workers.pop(sourcePoint)
            if self.__services.__contains__(serviceName) and self.__services[serviceName][0] == sourcePoint:
                self.__services.pop(serviceName)
                print('Service [{}] unregistered.'.format(serviceName))
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

        def metaItem(sn, meta):
            return {
                "ServiceName": sn, 
                "Address": meta[0], 
                "Interfaces": meta[1], 
                "OnTime": currentTime - meta[2],
                "Statistics": {
                    "Received Message": meta[3][0],
                    "Received Bytes": meta[3][1],
                    "Sent Message": meta[3][2],
                    "Sent Bytes": meta[3][3],
                }
            }

        for s in self.__services:
            meta = self.__services[s]
            results.append({
                "ServiceName": s, 
                "Address": meta[0], 
                "Interfaces": meta[1], 
                "OnTime": currentTime - meta[2],
                "Statistics": {
                    "Received Message": meta[3][0],
                    "Received Bytes": meta[3][1],
                    "Sent Message": meta[3][2],
                    "Sent Bytes": meta[3][3],
                }})
        for s in self.__nonservice:
            meta = self.__nonservice[s]
            results.append({
                "ServiceName": '', 
                "Address": s, 
                "Interfaces": '', 
                "OnTime": currentTime - meta[0],
                "Statistics": {
                    "Received Message": meta[2][0],
                    "Received Bytes": meta[2][1],
                    "Sent Message": meta[2][2],
                    "Sent Bytes": meta[2][3],
                }})
        # results.append(metaItem("", ["", "", 0, self.__nonserviceStatistics]))
        return results

    def statistics(self, sourcePoint, isReceived, message):
        offset = 0 if isReceived else 2
        if self.__workers.__contains__(sourcePoint):
            statItem = self.__services[self.__workers[sourcePoint]][3]
        else:
            if not self.__nonservice.__contains__(sourcePoint):
                self.__nonservice[sourcePoint] = [time.time(), 0, [0] * 4] 
            self.__nonservice[sourcePoint][1] = time.time()
            statItem = self.__nonservice[sourcePoint][2]
        statItem[offset] += 1
        statItem[offset + 1] += len(message[-1])

        if (time.time() - self.__previousGCTime > 10):
            try:
                keys = []
                for key in self.__nonservice:
                    keys.append(key)
                for key in keys:
                    if self.__nonservice[key][1] < self.__previousGCTime:
                        self.__nonservice.pop(key)
                self.__previousGCTime = time.time()
            except BaseException as e:
                import traceback
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
        for key in self.__activities.keys():
            lastActiviteTime = self.__activities[key]
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
    def open(self, *args, **kwargs):
        self.currentMessage = []
        self.__endpoint = 'tcp://localhost:224'
        socket = zmq.Context().socket(zmq.DEALER)
        self.__stream = ZMQStream(socket, IOLoop.current())
        self.__stream.on_recv(self.__onReceive)
        self.__stream.socket.setsockopt(zmq.LINGER, 0)
        self.__stream.connect(self.__endpoint)

    def on_close(self, *args, **kwargs):
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

if __name__ == '__main__':
    broker = IFBroker("tcp://*:224")
    # broker.startWebSocket(81, '/ws/',
    # {
    #     "certfile": "/root/.config/OpenSSL/server.crt",
    #     "keyfile": "/root/.config/OpenSSL/server.key",
    # }
    # )
    print('started')
    IFLoop.join()
