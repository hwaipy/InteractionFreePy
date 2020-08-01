__author__ = 'Hwaipy'

import unittest
import time
from IFBroker import IFBroker
from IFWorker import IFWorker
from IFCore import Message, IFException
from tornado.ioloop import IOLoop
import threading
from asyncio import Queue


class AsyncIFWorkerTest(unittest.TestCase):
    testPort = 20111
    brokerAddress = 'tcp://127.0.0.1:{}'.format(testPort)

    @classmethod
    def setUpClass(cls):
        broker = IFBroker(AsyncIFWorkerTest.brokerAddress)

    def setUp(self):
        pass

    def testRemoteInvokeAndAsync(self):
        worker1 = IFWorker(AsyncIFWorkerTest.brokerAddress)
        invoker1 = worker1.asyncInvoker()

        async def test():
            self.assertEqual(await invoker1.protocol(), 'IF1')
            try:
                await invoker1.protocol2()
                self.fail('No exception raised.')
            except IFException as e:
                self.assertEqual(e.__str__(), 'Function [protocol2] not available.')

        IOLoop.current().add_callback(test)

    #     future1 = invoker1.co()
    #     latch1 = threading.Semaphore(0)
    #     future1.onComplete(lambda: latch1.release())
    #     latch1.acquire()
    #     self.assertTrue(future1.isDone())
    #     self.assertFalse(future1.isSuccess())
    #     self.assertEqual(future1.exception().description, "Function [co] not available.")
    #
    #     future1 = invoker1.protocol(a=1, b=2)
    #     latch1 = threading.Semaphore(0)
    #     future1.onComplete(lambda: latch1.release())
    #     latch1.acquire()
    #     self.assertTrue(future1.isDone())
    #     self.assertFalse(future1.isSuccess())
    #     self.assertEqual(future1.exception().description, "Keyword Argument [a] not availabel for function [protocol].")
    #     future1 = invoker1.protocol(1, 2, 3)
    #     latch1 = threading.Semaphore(0)
    #     future1.onComplete(lambda: latch1.release())
    #     latch1.acquire()
    #     self.assertTrue(future1.isDone())
    #     self.assertFalse(future1.isSuccess())
    #     self.assertEqual(future1.exception().description, "Function [protocol] expects [0] arguments, but [3] were given.")
    #
    # def testRemoteInvokeAndSync(self):
    #     worker = IFWorker(MessageTransportTest.brokerAddress)
    #     invoker = worker.blockingInvoker()
    #     self.assertRaises(IFException, lambda: invoker.co())
    #     self.assertEqual(invoker.protocol(), 'IF1')
    #
    # def testSyncAndAsyncMode(self):
    #     worker = IFWorker(MessageTransportTest.brokerAddress)
    #     self.assertRaises(IFException, lambda: worker.co())
    #     self.assertEqual(worker.protocol(), 'IF1')
    #     worker.blocking = False
    #     future1 = worker.protocol(1, 2, 3)
    #     latch1 = threading.Semaphore(0)
    #     future1.onComplete(lambda: latch1.release())
    #     latch1.acquire()
    #     self.assertTrue(future1.isDone())
    #     self.assertFalse(future1.isSuccess())
    #     self.assertEqual(future1.exception().description, "Function [protocol] expects [0] arguments, but [3] were given.")
    #
    # def testInvokeOtherClient(self):
    #     class Target:
    #         def __init__(self):
    #             self.notFunction = 100
    #
    #         def v8(self): return "V8 great!"
    #
    #         def v9(self): raise IFException("V9 not good.")
    #
    #         def v10(self): raise IOError("V10 have problems.")
    #
    #         def v(self, i, b): return "OK"
    #
    #     worker1 = IFWorker(MessageTransportTest.brokerAddress, serviceObject=Target(), serviceName="T1-Benz")
    #     checker = IFWorker(MessageTransportTest.brokerAddress)
    #     benzChecker = checker.blockingInvoker("T1-Benz", 1)
    #     v8r = benzChecker.v8()
    #     self.assertEqual(v8r, "V8 great!")
    #     try:
    #         benzChecker.v9()
    #         self.assertTrue(False)
    #     except IFException as e:
    #         self.assertEqual(e.__str__(), "V9 not good.")
    #     try:
    #         benzChecker.v10()
    #         self.assertTrue(False)
    #     except Exception as e:
    #         self.assertEqual(e.__str__(), "V10 have problems.")
    #     self.assertEqual(benzChecker.v(1, False), "OK")
    #     try:
    #         benzChecker.v11()
    #         self.assertTrue(False)
    #     except IFException as e:
    #         self.assertEqual(e.__str__(), "Function [v11] not available.")
    #     try:
    #         benzChecker.notFunction()
    #         self.assertTrue(False)
    #     except IFException as e:
    #         self.assertEqual(e.__str__(), "Function [notFunction] not available.")
    #
    # def testServiceDuplicated(self):
    #     worker1 = IFWorker(MessageTransportTest.brokerAddress, serviceName="T2-ClientDuplicated")
    #     try:
    #         worker2 = IFWorker(MessageTransportTest.brokerAddress, serviceName="T2-ClientDuplicated")
    #     except IFException as e:
    #         self.assertEqual(e.__str__(), "Service name [T2-ClientDuplicated] occupied.")
    #
    # def testTimeCostInvocation(self):
    #     queue = Queue()
    #
    #     class WorkerObject:
    #         async def popQueue(self):
    #             g = await queue.get()
    #             return g
    #
    #         def returnImmediatly(self):
    #             return 'rim'
    #
    #     worker = IFWorker(MessageTransportTest.brokerAddress, serviceName="TimeCostWorker", serviceObject=WorkerObject())
    #     client = IFWorker(MessageTransportTest.brokerAddress)
    #     client.asynchronousInvoker('TimeCostWorker').popQueue()
    #     IOLoop.current().call_at(IOLoop.current().time() + 2, queue.put, 'lock')
    #     startTime = time.time()
    #     self.assertEqual(client.TimeCostWorker.returnImmediatly(), 'rim')
    #     stopTime = time.time()
    #     self.assertLess(stopTime - startTime, 1)

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        time.sleep(1)
        IOLoop.current().stop()


if __name__ == '__main__':
    unittest.main()
