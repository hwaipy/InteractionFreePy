
# InteractionFree for Python

[![](https://img.shields.io/pypi/v/interactionfreepy)](https://pypi.org/project/interactionfreepy/)
[![Gitpod ready-to-code](https://img.shields.io/badge/Gitpod-ready--to--code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/hwaipy/InteractionFreePy)

[InteractionFree]() is a remote procedure call (RPC) protocol based on [ZeroMQ](https://zeromq.org). It allows the developers to build their own distributed and cross-languige program easily. The protocol is config-less and extremly easy to use. Currently, [Msgpack](https://msgpack.org) is used for binary serialization. InteractionFree implementation is already available in various languages (including Scala, Javascript, Arduino). More infomation will be available soon.

- InteractionFree specification: to be drafted.



## Quick Start

 **Install**

```shell
$ pip install interactionfreepy
```

**Start the server**

```python
from interactionfreepy import IFBroker

broker = IFBroker('tcp://*:port')
IFLoop.join()
```

replace `port` to any port number that is available.

`IFLoop.join()` is a utility function to prevent the program from finishing.

**Start a worker**

```python
from interactionfreepy import IFWorker

class Target():
    def tick(self, message):
        return "tack %s" % message

worker = IFWorker('tcp://address:port', 'TargetService', Target())
IFLoop.join()
```

replace `address` and `port` to the server's net address and port.

**Start a client**

```python
from interactionfreepy import IFWorker

client = IFWorker('tcp://address:port')
print(client.TargetService.tick('now'))
```

