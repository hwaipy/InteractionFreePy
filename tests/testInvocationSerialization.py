__author__ = 'Hwaipy'

import sys
import unittest
import msgpack
from random import Random
from interactionfreepy import Invocation
import timeout_decorator


class InvocationSerializationTest(unittest.TestCase):
    mapIn = {
        "keyString": "value1",
        "keyInt": 123,
        "keyLong": (sys.maxsize + 100),
        "keyBigInteger": 2 ** 64 - 1,
        "keyBooleanFalse": False,
        "KeyBooleanTrue": True,
        "keyByteArray": b"\x01\x02\x02\x02\x02\x01\x01\x02\x02\x01\x01\x04\x05\x00\x04\x04\xFF",
        "keyIntArray": [3, 526255, 1321, 4, -1],
        "keyNull": None,
        "keyDouble": 1.242,
        "keyDouble2": -12.2323e-100}
    map = {"keyMap": mapIn}

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        pass

    @timeout_decorator.timeout(seconds=10)
    def testFeedOverflow(self):
        unpacker = msgpack.Unpacker(raw=False)
        bytes = Invocation(InvocationSerializationTest.map).serialize()
        for i in range(100000):
            unpacker.feed(bytes)

    @timeout_decorator.timeout(seconds=10)
    def testOverDeepth(self):
        map = {"a": "b"}
        for i in range(200):
            map = {'a': map}
        Invocation(map).serialize()

    @timeout_decorator.timeout(seconds=10)
    def testMapPackAndUnpack(self):
        bytes = Invocation(InvocationSerializationTest.map).serialize()
        unpacker = msgpack.Unpacker(raw=False)
        unpacker.feed(bytes)
        m1 = unpacker.__next__()
        self.assertRaises(StopIteration, unpacker.__next__)
        self.assertEqual(m1, InvocationSerializationTest.map)

    @timeout_decorator.timeout(seconds=10)
    def testMapPackAndClassUnpack(self):
        bytes = Invocation(InvocationSerializationTest.map).serialize()
        m1 = Invocation.deserialize(bytes, contentOnly=True)
        self.assertEqual(m1, InvocationSerializationTest.map)

    @timeout_decorator.timeout(seconds=10)
    def testMultiUnpack(self):
        multi = 100
        bytes = b''
        for i in range(multi):
            bytes += Invocation(InvocationSerializationTest.map).serialize()
        unpacker = msgpack.Unpacker(raw=False)
        unpacker.feed(bytes)
        for i in range(multi):
            self.assertEqual(unpacker.__next__(), InvocationSerializationTest.map)
        self.assertRaises(StopIteration, unpacker.__next__)

    @timeout_decorator.timeout(seconds=10)
    def testPartialUnpackByteByByte(self):
        multi = 10
        bytes = Invocation(InvocationSerializationTest.map).serialize()
        unpacker = msgpack.Unpacker(raw=False)
        for j in range(multi):
            for i in range(len(bytes) - 1):
                unpacker.feed(bytes[i:i + 1])
                self.assertRaises(StopIteration, unpacker.__next__)
            unpacker.feed(bytes[-1:])
            self.assertEqual(unpacker.__next__(), InvocationSerializationTest.map)

    @timeout_decorator.timeout(seconds=10)
    def testPartialUnpackBlockByBlock(self):
        unitSize = len(Invocation(InvocationSerializationTest.map).serialize())
        limit = unitSize * 3
        random = Random()
        multi = 10
        blockSizesA = [0] * (multi - 1)
        for i in range(len(blockSizesA)):
            blockSizesA[i] = random.randint(0, limit)
        sumA = sum(blockSizesA)
        lastSize = unitSize - (sumA % unitSize)
        blockSizes = blockSizesA + [lastSize]
        totalSize = sumA + lastSize
        self.assertEqual(totalSize % unitSize, 0)
        bytes = b''
        for i in range(totalSize // unitSize):
            bytes += Invocation(InvocationSerializationTest.map).serialize()
        self.assertEqual(len(bytes), totalSize)
        unpacker = msgpack.Unpacker(raw=False)
        generated = 0
        sumD = 0
        for size in blockSizes:
            unpacker.feed(bytes[sumD:sumD + size])
            sumD += size
            newGenerated = sumD // unitSize
            while newGenerated > generated:
                self.assertEqual(unpacker.__next__(), InvocationSerializationTest.map)
                generated += 1
            self.assertRaises(StopIteration, unpacker.__next__)
        self.assertEqual(generated, totalSize // unitSize)

    @timeout_decorator.timeout(seconds=10)
    def testException(self):
        unpacker = msgpack.Unpacker(raw=False)
        bytes = Invocation(InvocationSerializationTest.map).serialize()
        unpacker.feed(bytes)
        unpacker.feed(bytes[1:-1])
        unpacker.feed(bytes)
        self.assertEqual(unpacker.__next__(), InvocationSerializationTest.map)
        self.assertNotEqual(unpacker.__next__(), InvocationSerializationTest.map)

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        pass


if __name__ == '__main__':
    unittest.main()
