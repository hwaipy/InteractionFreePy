"""A reconnectable socket with asyncio."""

import asyncio
import threading
import socket
import random
import logging


class RSocket:
  """RSocket is a reconnectable socket wrap with asyncio.
  After an RSocket client connects to an RSocket server, they will try to keep the connection alive even in a unstable network.
  This object is a wrap of `asyncio.open_connection(host, port)`, but reconnectable.
  The parameters, `host` and `port`, are the same for `asyncio.open_connection()`.
  """
  __logger = logging.getLogger('RSocket')

  def __init__(self, host: str, port: int) -> None:
    # reader: asyncio.streams.StreamReader, write: asyncio.streams.StreamWriter
    self.host = host
    self.port = port
    self.reader = None
    self.writer = None
    self.__connectionActive = asyncio.Event()
    self.__writeQueue = asyncio.Queue()
    self.__waterline = 30
    asyncio.create_task(self.__loopConnect())
    asyncio.create_task(self.__loopRead())
    asyncio.create_task(self.__loopWrite())

  def writeLater(self, data) -> None:
    asyncio.create_task(self.write(data))

  async def write(self, data) -> None:
    event = asyncio.Event()
    await self.__writeQueue.put(data)
    await event.wait()
  # need a limit of queue size 
  # async def flush():

  def setWaterline(self, waterline: int) -> None:
    self.__waterline = waterline

  def getWaterline(self) -> int:
    return self.__waterline

  async def __loopConnect(self):
    while True:
      if self.__connectionActive.is_set():
        await asyncio.sleep(1)
      else:
        try:
          connection = await asyncio.open_connection(self.host, self.port)
          self.reader = connection[0]
          self.writer = connection[1]
          RSocket.__logger.info('RSocket connected')
          self.__connectionActive.set()
        except ConnectionError as exc:
          msg = f'RSocket connection failed: {exc}. Retring in 5 s...'
          RSocket.__logger.warning(msg)
          await asyncio.sleep(5 - random.random() / 10)

  async def __loopRead(self):
    while True:
      await self.__connectionActive.wait()
      data = await self.reader.read(1000000)
      if len(data) == 0:
        RSocket.__logger.warning('Connection broken.')
        self.__connectionActive.clear()
      else:
        print(f'{len(data)} data read.')

  async def __loopWrite(self):
    while True:
      data = await self.__writeQueue.get()
      await self.__connectionActive.wait()
      self.writer.write(data)

class RSocketServer:
  """RSocketServer is a wrap of asyncio Server.
  After an RSocket client connects to an RSocket server, they will try to keep the connection alive even in a unstable network.
  """

  def __init__(self, server: asyncio.base_events.Server) -> None:
    self.server = server

  @classmethod
  async def startServer(cls, host: str | None, port: int | str | None):
    """A coroutine which creates a TCP server bound to host and port.
    The return value is a wrap of `loop.create_server()`.
    The parameters, `host` and `port`, are the same for `loop.create_server()`.
    """

    async def handleConnection(server: socket) -> None:
      while True:
        client, _ = await asyncio.get_event_loop().sock_accept(server)
        print(client)

    # server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server.bind((host, port))
    # server.setblocking(False)
    # print(1)
    # server.accept()
    # print(2)
    # # asyncio.get_event_loop().create_task(handleConnection(server))
    # print('started')

    async def handle_echo(reader, writer: asyncio.streams.StreamWriter):
      data = await reader.read(100)
      message = data.decode()
      addr = writer.get_extra_info('peername')

      print(f"Received {message!r} from {addr!r}")
      print(type(writer.transport))

      print(f"Send: {message!r}")
      writer.write(data)
      await writer.drain()

    server = await asyncio.start_server(handle_echo, '127.0.0.1', 8888)

    async with server:
      await server.serve_forever()


if __name__ == "__main__":
  logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
  async def test(cmd):
    if cmd == 'server':
      server = await RSocketServer.startServer('127.0.0.1', 8888)
      await asyncio.sleep(100)
    elif cmd == 'client':
      client = RSocket('127.0.0.1', 8888)
      await client.write(b'009988')
      print('writed')
      await asyncio.sleep(100)
    else:
      raise BaseException('Bad CMD.')

  import sys
  import time
  t1 = threading.Thread(target=asyncio.get_event_loop_policy().new_event_loop().run_until_complete, args=[test(sys.argv[1])])
  t1.start()
  t1.join()
