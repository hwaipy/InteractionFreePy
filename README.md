
# InteractionFree for Python

[![](https://img.shields.io/github/actions/workflow/status/hwaipy/InteractionFreePy/tests.yml?branch=master)](https://github.com/hwaipy/InteractionFreePy/actions?query=workflow%3ATests)
[![Documentation Status](https://readthedocs.org/projects/interactionfreepy/badge/?version=latest)](https://interactionfreepy.readthedocs.io/en/latest/?badge=latest)
[![](https://img.shields.io/pypi/v/interactionfreepy)](https://pypi.org/project/interactionfreepy/)
[![](https://img.shields.io/pypi/pyversions/interactionfreepy)](https://pypi.org/project/interactionfreepy/)
[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/hwaipy/InteractionFreePy/python-coverage-comment-action-data/endpoint.json)](https://github.com/hwaipy/InteractionFreePy/tree/python-coverage-comment-action-data)

[InteractionFree]() is a remote procedure call (RPC) protocol based on [ZeroMQ](https://zeromq.org). It allows the developers to build their own distributed and cross-languige program easily. The protocol is config-less and extremly easy to use. Currently, [MessagePack](https://msgpack.org) is used for binary serialization. 

Please refer to [here](https://interactionfreepy.readthedocs.io/en/latest/index.html) for the full doc.


## Quick Start

 **Install**

```shell
$ pip install interactionfreepy
```

**Start the broker**

```python
from interactionfreepy import IFBroker

broker = IFBroker('tcp://*:port')
IFLoop.join()
```

replace `port` to any port number that is available.

`IFLoop.join()` is a utility function to prevent the program from finishing.

**Start a server**

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

