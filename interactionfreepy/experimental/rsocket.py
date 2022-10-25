"""A reconnectable socket with asyncio."""

import asyncio
from curses.ascii import RS
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
  __loop = None

  def __init__(self, host: str, port: int) -> None:
    # reader: asyncio.streams.StreamReader, write: asyncio.streams.StreamWriter
    self.host = host
    self.port = port
    self.reader = None
    self.writer = None
    self.__running = False
    self.__connectionActive = asyncio.Event()
    self.__writeQueue = asyncio.Queue()
    self.__waterline = 30
    self.__closeEvents = [asyncio.Event(), asyncio.Event(), asyncio.Event()]

  async def start(self) -> None:
    if self.__running:
      raise RuntimeError('The RSocdSocis already running.')
    self.__running = True
    asyncio.create_task(self.__loopConnect())
    asyncio.create_task(self.__loopRead())
    asyncio.create_task(self.__loopWrite())

  async def close(self) -> None:
    RSocket.__logger.info('RSocket closing.')
    self.__running = False
    for event in self.__closeEvents:
      await event.wait()
    RSocket.__logger.info('RSocket closed.')

  def writeLater(self, data) -> None:
    asyncio.create_task(self.write(data))

  async def write(self, data) -> None:
    if self.__writeQueue.qsize() > self.__waterline:
      RSocket.__logger.warning('The writing queue of RSocket reaches the waterline. New appended data will be discarded.')
    else:
      await self.__writeQueue.put(['WRITE', data])

  async def flush(self) -> None:
    event = asyncio.Event()
    await self.__writeQueue.put(['FLUSH', event])
    await event.wait()

  def setWaterline(self, waterline: int) -> None:
    self.__waterline = waterline

  def getWaterline(self) -> int:
    return self.__waterline

  async def __loopConnect(self):
    while self.__running:
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
    self.__closeEvents[0].set()

  async def __loopRead(self):
    while self.__running:
      await self.__connectionActive.wait()
      data = await self.reader.read(1000000)
      if len(data) == 0:
        RSocket.__logger.warning('Connection broken.')
        self.__connectionActive.clear()
      else:
        print(f'{len(data)} data read.')
    self.__closeEvents[1].set()

  async def __loopWrite(self):
    while self.__running:
      cmd, data = await self.__writeQueue.get()
      await self.__connectionActive.wait()
      if cmd == 'WRITE':
        self.writer.write(data)
      elif cmd == 'FLUSH':
        await self.writer.drain()
        data.set()
      else:
        msg = f'Invalid write command: {cmd}'
        RSocket.__logger.warning(msg)
    if self.writer:
      self.writer.close()
    self.__closeEvents[2].set()


class RSocketServer:
  """RSocketServer is a wrap of asyncio Server.
  After an RSocket client connects to an RSocket server, they will try to keep the connection alive even in a unstable network.
  """

  def __init__(self, host: str, port: int) -> None:
    self.host = host
    self.port = port

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
  logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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
