Quick start
=====

**InteractionFreePy** is extremely easy to use.
Follow the steps below as a quick start.

Install
------------

.. code-block:: shell

    pip install interactionfreepy





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
``` -->