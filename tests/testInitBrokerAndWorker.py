__author__ = 'Hwaipy'

import unittest
import time
from interactionfreepy import IFBroker
from interactionfreepy import IFWorker

class InitBrokerAndWorkerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    def testFormatOfAddress(self):
        broker1 = IFBroker('tcp://*:1001')
        broker2 = IFBroker('tcp://127.0.0.1:1002')
        broker3 = IFBroker('127.0.0.1:1003')
        broker4 = IFBroker('127.0.0.1')
        self.assertRaises(ValueError, lambda: IFBroker('udp://127.0.0.1'))
        self.assertRaises(ValueError, lambda: IFBroker('udp://127.0.0.1:123'))

        worker1 = IFWorker('127.0.0.1:1001', 'W1', '')
        self.assertEqual(worker1.listServiceNames(), ['W1'])
        worker1.unregister()
        worker2 = IFWorker('127.0.0.1:1002', 'W2', '')
        self.assertEqual(worker2.listServiceNames(), ['W2'])
        worker2.unregister()
        worker3 = IFWorker('tcp://127.0.0.1:1003', 'W3', '')
        self.assertEqual(worker3.listServiceNames(), ['W3'])
        worker3.unregister()
        worker4 = IFWorker('127.0.0.1', 'W4', '')
        self.assertEqual(worker4.listServiceNames(), ['W4'])
        worker4.unregister()
        self.assertRaises(ValueError, lambda: IFBroker('udp://127.0.0.1'))
        self.assertRaises(ValueError, lambda: IFBroker('udp://127.0.0.1:456'))

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        time.sleep(1)

if __name__ == '__main__':
    unittest.main()