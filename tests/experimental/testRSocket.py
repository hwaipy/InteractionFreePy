__author__ = 'Hwaipy'

import unittest
import asyncio
from wrapt_timeout_decorator import timeout
from tests.defines import Defines
from interactionfreepy.experimental.rsocket import RSocket, RSocketServer


class RSocketTest(unittest.TestCase):
  port = 8901

  @classmethod
  def setUpClass(cls):
    pass

  def setUp(self):
    pass

  @timeout(Defines.timeout)
  def testRSocketStartAndClose(self):
    async def test():
      rsocket = RSocket('localhost', 110)
      await rsocket.start()
      try:
        await rsocket.start()
        raise AssertionError('This code should not be runned.')
      except RuntimeError as exc:
        self.assertEqual(str(exc), 'The RSocdSocis already running.')
      await rsocket.close()

    asyncio.new_event_loop().run_until_complete(test())

  def tearDown(self):
    pass

  @classmethod
  def tearDownClass(cls):
    pass
    # time.sleep(1)
    # IOLoop.current().stop()


if __name__ == '__main__':
  unittest.main()
