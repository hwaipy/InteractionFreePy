__author__ = 'Hwaipy'

import sys
import unittest
from interactionfreepy import Invocation, IFException
from wrapt_timeout_decorator import timeout


class InvocationTest(unittest.TestCase):
    sampleRequestContent = {
        Invocation.KeyType: Invocation.ValueTypeRequest,
        Invocation.KeyFunciton: "FunctionName",
        Invocation.KeyArguments: [1, "ARG2", None],
        Invocation.KeyKeyworkArguments: {'A': 'a', 'B': 2, 'D': None, 'C': -0.4},
        "keyString": "value1",
        "keyInt": 123,
        "keyLong": (sys.maxsize + 100),
        "keyBigInteger": 2 ** 100,
        "keyBooleanFalse": False,
        "KeyBooleanTrue": True,
        "keyByteArray": bytearray([1, 2, 2, 2, 2, 1, 1, 2, 2, 1, 1, 4, 5, 4, 4, 255]),
        "keyIntArray": [3, 526255, 1321, 4, -1],
        "keyNull": None,
        "keyDouble": 1.242,
        "keyDouble2": -12.2323e-100
    }
    sampleResponseContent = {
        Invocation.KeyType: Invocation.ValueTypeResponse,
        Invocation.KeyRespopnseID: 'ID1',
        Invocation.KeyResult: [1, 'Res'],
        Invocation.KeyWarning: 'Something not good'
    }
    sampleErrorContent = {
        Invocation.KeyType: Invocation.ValueTypeResponse,
        Invocation.KeyRespopnseID: b'0x01',
        Invocation.KeyResult: [1, 'Res'],
        Invocation.KeyWarning: 'Something not good',
        Invocation.KeyError: 'Fatal Error!'
    }

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    @timeout(10)
    def testGetInformation(self):
        m = Invocation(InvocationTest.sampleRequestContent)
        self.assertEqual(m.get("keyString"), "value1")
        self.assertRaises(TypeError, lambda: m.get("keyString") + 1)
        self.assertRaises(IFException, lambda: m.get("keyNull", False))
        self.assertIsNone(m.get("keyNull", True))

    @timeout(10)
    def testTypeAndContent(self):
        m1 = Invocation(InvocationTest.sampleRequestContent)
        self.assertTrue(m1.isRequest())
        self.assertEqual(m1.getFunction(), 'FunctionName')
        self.assertEqual(m1.getArguments(), [1, 'ARG2', None])
        self.assertEqual(m1.getKeywordArguments(), {'A': 'a', 'B': 2, 'C': -0.4, 'D': None})

        m2 = Invocation(InvocationTest.sampleResponseContent)
        self.assertTrue(m2.isResponse())
        self.assertFalse(m2.isError())
        self.assertTrue(m2.hasWarning())
        self.assertEqual(m2.getResult(), [1, 'Res'])
        self.assertEqual(m2.getWarning(), 'Something not good')
        self.assertEqual(m2.getResponseID(), 'ID1')

        m3 = Invocation(InvocationTest.sampleErrorContent)
        self.assertTrue(m3.isResponse())
        self.assertTrue(m3.isError())
        self.assertTrue(m3.hasWarning())
        self.assertEqual(m3.getWarning(), 'Something not good')
        self.assertEqual(m3.getError(), 'Fatal Error!')
        self.assertEqual(m3.getResult(), None)
        self.assertEqual(m3.getResponseID(), b'0x01')

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        pass


if __name__ == '__main__':
    unittest.main()
