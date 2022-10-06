__author__ = 'Hwaipy'

import unittest
import time
from interactionfreepy import IFBroker
from interactionfreepy import IFWorker
from interactionfreepy import Message, IFException
from tornado.ioloop import IOLoop
import threading
from asyncio import Queue
from random import Random
import string
import queue
from wrapt_timeout_decorator import timeout
from tests.defines import Defines


class MessageTransportTest(unittest.TestCase):
    testPort = 20111
    brokerAddress = 'tcp://127.0.0.1:{}'.format(testPort)

    @classmethod
    def setUpClass(cls):
        broker = IFBroker(MessageTransportTest.brokerAddress)

    def setUp(self):
        pass

    @timeout(Defines.timeout)
    def testConnectionOfSession(self):
        worker = IFWorker(MessageTransportTest.brokerAddress)

    @timeout(Defines.timeout)
    def testDynamicInvoker(self):
        worker = IFWorker(MessageTransportTest.brokerAddress)
        invoker = worker.toMessageInvoker()
        m1 = invoker.fun1(1, 2, "3", b=None, c=[1, 2, "3d"])
        self.assertTrue(m1.isProtocolValid())
        self.assertTrue(m1.isBrokerMessage())
        m1Invocation = m1.getInvocation()
        self.assertTrue(m1Invocation.isRequest())
        self.assertEqual(m1Invocation.getFunction(), 'fun1')
        self.assertEqual(m1Invocation.getArguments(), [1, 2, "3"])
        self.assertEqual(m1Invocation.getKeywordArguments(), {"b": None, "c": [1, 2, "3d"]})

        invoker2 = worker.toMessageInvoker("OnT")
        m2 = invoker2.fun2()
        m2Invocation = Message.getInvocation(m2)
        self.assertTrue(m2Invocation.isRequest())
        self.assertEqual(m2Invocation.getFunction(), 'fun2')
        self.assertEqual(m2Invocation.getArguments(), [])
        self.assertEqual(m2Invocation.getKeywordArguments(), {})
        self.assertTrue(m2.isServiceMessage())
        self.assertEqual(m2.distributingAddress, b'OnT')

    @timeout(Defines.timeout)
    def testRemoteInvokeAndAsync(self):
        worker1 = IFWorker(MessageTransportTest.brokerAddress)
        invoker1 = worker1.asynchronousInvoker()
        future1 = invoker1.co()
        latch1 = threading.Semaphore(0)
        future1.onComplete(lambda: latch1.release())
        latch1.acquire()
        self.assertTrue(future1.isDone())
        self.assertFalse(future1.isSuccess())
        self.assertEqual(future1.exception().description, "Function [co] not available.")

        future1 = invoker1.protocol(a=1, b=2)
        latch1 = threading.Semaphore(0)
        future1.onComplete(lambda: latch1.release())
        latch1.acquire()
        self.assertTrue(future1.isDone())
        self.assertFalse(future1.isSuccess())
        self.assertEqual(future1.exception().description, "Keyword Argument [a] not availabel for function [protocol].")
        future1 = invoker1.protocol(1, 2, 3)
        latch1 = threading.Semaphore(0)
        future1.onComplete(lambda: latch1.release())
        latch1.acquire()
        self.assertTrue(future1.isDone())
        self.assertFalse(future1.isSuccess())
        self.assertEqual(future1.exception().description, "Function [protocol] expects [0] arguments, but [3] were given.")

    @timeout(Defines.timeout)
    def testRemoteInvokeAndSync(self):
        worker = IFWorker(MessageTransportTest.brokerAddress)
        invoker = worker.blockingInvoker()
        self.assertRaises(IFException, lambda: invoker.co())
        self.assertEqual(invoker.protocol(), 'IF1')

    @timeout(Defines.timeout)
    def testSyncAndAsyncMode(self):
        worker = IFWorker(MessageTransportTest.brokerAddress)
        self.assertRaises(IFException, lambda: worker.co())
        self.assertEqual(worker.protocol(), 'IF1')
        worker.blocking = False
        future1 = worker.protocol(1, 2, 3)
        latch1 = threading.Semaphore(0)
        future1.onComplete(lambda: latch1.release())
        latch1.acquire()
        self.assertTrue(future1.isDone())
        self.assertFalse(future1.isSuccess())
        self.assertEqual(future1.exception().description, "Function [protocol] expects [0] arguments, but [3] were given.")

    @timeout(Defines.timeout)
    def testInvokeOtherClient(self):
        class Target:
            def __init__(self):
                self.notFunction = 100

            def v8(self): return "V8 great!"

            def v9(self): raise IFException("V9 not good.")

            def v10(self): raise IOError("V10 have problems.")

            def v(self, i, b): return "OK"

        worker1 = IFWorker(MessageTransportTest.brokerAddress, serviceObject=Target(), serviceName="T1-Benz")
        checker = IFWorker(MessageTransportTest.brokerAddress)
        benzChecker = checker.blockingInvoker("T1-Benz", 1)
        v8r = benzChecker.v8()
        self.assertEqual(v8r, "V8 great!")
        try:
            benzChecker.v9()
            self.assertTrue(False)
        except IFException as e:
            self.assertEqual(e.__str__(), "V9 not good.")
        try:
            benzChecker.v10()
            self.assertTrue(False)
        except Exception as e:
            self.assertEqual(e.__str__(), "V10 have problems.")
        self.assertEqual(benzChecker.v(1, False), "OK")
        try:
            benzChecker.v11()
            self.assertTrue(False)
        except IFException as e:
            self.assertEqual(e.__str__(), "Function [v11] not available.")
        try:
            benzChecker.notFunction()
            self.assertTrue(False)
        except IFException as e:
            self.assertEqual(e.__str__(), "Function [notFunction] not available.")

    @timeout(Defines.timeout)
    def testServiceDuplicated(self):
        worker1 = IFWorker(MessageTransportTest.brokerAddress, serviceName="T2-ClientDuplicated")
        try:
            worker2 = IFWorker(MessageTransportTest.brokerAddress, serviceName="T2-ClientDuplicated")
        except IFException as e:
            self.assertEqual(e.__str__(), "Service name [T2-ClientDuplicated] occupied.")

    @timeout(Defines.timeout)
    def testTimeCostInvocation(self):
        queue = Queue()

        class WorkerObject:
            async def popQueue(self):
                g = await queue.get()
                return g

            def returnImmediatly(self):
                return 'rim'

        worker = IFWorker(MessageTransportTest.brokerAddress, serviceName="TimeCostWorker", serviceObject=WorkerObject())
        client = IFWorker(MessageTransportTest.brokerAddress)
        client.asynchronousInvoker('TimeCostWorker').popQueue()
        IOLoop.current().call_at(IOLoop.current().time() + 2, queue.put, 'lock')
        startTime = time.time()
        self.assertEqual(client.TimeCostWorker.returnImmediatly(), 'rim')
        stopTime = time.time()
        self.assertLess(stopTime - startTime, 1)

    @timeout(Defines.timeout)
    def testInvokeLargeData(self):
        rnd = Random()
        letters = string.printable
        largeData = (''.join([letters[rnd.randint(0, len(letters) - 1)] for i in range(1000000)])).encode()

        class Target:
            def get(self):
                return largeData

            def compare(self, data, simple=False):
                if simple:
                    return len(data) == len(largeData) and data[0] == largeData[0] and data[-1] == largeData[-1]
                return data == largeData

        worker = IFWorker(MessageTransportTest.brokerAddress, serviceObject=Target(), serviceName="LDS")
        checker = IFWorker(MessageTransportTest.brokerAddress)
        self.assertTrue(checker.LDS.compare(largeData))
        retrived = checker.LDS.get()
        self.assertTrue(largeData, retrived)

        largeData = largeData * 100
        self.assertTrue(checker.LDS.compare(largeData, True))
        retrived = checker.LDS.get()
        self.assertTrue(len(retrived) == len(largeData) and retrived[0] == largeData[0] and retrived[-1] == largeData[-1])

        worker.close()
        checker.close()

    @timeout(Defines.timeout)
    def testDisconnectService(self):
        serviceName = 'DSWorker1'
        s1 = IFWorker(MessageTransportTest.brokerAddress, serviceName=serviceName, serviceObject="")
        client = IFWorker(MessageTransportTest.brokerAddress)
        self.assertTrue(client.listServiceNames().__contains__(serviceName))
        stopFuture = client.asyncInvoker(serviceName).stopService(serviceName)

        stopResultQueue = queue.Queue()
        async def test():
            stopped = await stopFuture
            stopResultQueue.put('')

        IOLoop.current().add_callback(test)
        stopResultQueue.get(timeout=10)
        self.assertFalse(client.listServiceNames().__contains__(serviceName))

    @timeout(Defines.timeout)
    def testForceRegisterService(self):
        serviceName = 'DSWorker1'
        s1 = IFWorker(MessageTransportTest.brokerAddress, serviceName=serviceName, serviceObject="1")
        client = IFWorker(MessageTransportTest.brokerAddress)
        self.assertTrue(client.listServiceNames().__contains__(serviceName))
        self.assertTrue(client.blockingInvoker(serviceName).strip() == '1')
        s2 = IFWorker(MessageTransportTest.brokerAddress, serviceName=serviceName, serviceObject='2', force=True)
        self.assertTrue(client.blockingInvoker(serviceName).strip() == '2')

    @timeout(Defines.timeout)
    def testInvokeOtherClientRemotely(self):
        class Target:
            def v8(self): return "V8 great!"

        class Relay:
            def __init__(self, invoker):
                self.invoker = invoker

            def local(self): return 'local'

            def trans(self): return self.invoker.v8()

        # print('Not Implemented')
        # worker1 = IFWorker(MessageTransportTest.brokerAddress, serviceObject=Target(), serviceName="T1")
        # worker2 = IFWorker(MessageTransportTest.brokerAddress, serviceObject=Relay(worker1.T1), serviceName='Relay') 
        # checker = IFWorker(MessageTransportTest.brokerAddress)
        # self.assertEqual(checker.Relay.local(), 'local')
        # checker.Relay.trans()
        # v8r = benzChecker.v8()
        # self.assertEqual(v8r, "V8 great!")
        # try:
        #     benzChecker.v9()
        #     self.assertTrue(False)
        # except IFException as e:
        #     self.assertEqual(e.__str__(), "V9 not good.")
        # try:
        #     benzChecker.v10()
        #     self.assertTrue(False)
        # except Exception as e:
        #     self.assertEqual(e.__str__(), "V10 have problems.")
        # self.assertEqual(benzChecker.v(1, False), "OK")
        # try:
        #     benzChecker.v11()
        #     self.assertTrue(False)
        # except IFException as e:
        #     self.assertEqual(e.__str__(), "Function [v11] not available.")
        # try:
        #     benzChecker.notFunction()
        #     self.assertTrue(False)
        # except IFException as e:
        #     self.assertEqual(e.__str__(), "Function [notFunction] not available.")

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        time.sleep(1)
        # IOLoop.current().stop()


if __name__ == '__main__':
    unittest.main()
