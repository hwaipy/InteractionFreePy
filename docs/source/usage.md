# Usage

## Install

To install the package, you can use pip.

```{code-block} shell
pip install interactionfreepy
```

## Host a Broker

It is simple to host a *Broker*.
One may start with the {py:class}`IFBroker <interactionfreepy.broker.IFBroker>` class.

```{code-block} python
:lineno-start: 1

from interactionfreepy import IFBroker, IFLoop

broker = IFBroker()
IFLoop.join()
```

Here, `IFBroker()` creates the *Broker* instance and listens on the default port `1061`.
You can also change the port by explicitly passing the port number to the constructor, for example, `8061`.

```{code-block} python
:lineno-start: 1

from interactionfreepy import IFBroker, IFLoop

broker = IFBroker('*:8061')
IFLoop.join()
```

The address can also be specified (by replacing `*` with the IP address of the machine) to allow only local connections.
The `IFLoop.join()` is a blocking call that will keep the program running until terminated.

You can also host the *Broker* in a Docker container.
The Docker image is available as [hwaipy/ifbroker](https://hub.docker.com/r/hwaipy/ifbroker).
To run the broker in a Docker container, you can use the following command:

```{code-block} shell
  docker run -d -p 1061:1061 --name IFBroker hwaipy/ifbroker:latest
```

## Connect to a Broker

Use the {py:class}`IFWorker <interactionfreepy.worker.IFWorker>` class to connect to a *Broker*.
For the purpose of giving an example, we will use the public *Broker* hosted by `interactionfree.cn:1061`.
You could change the address to your own *Broker* if you have already hosted one.

```{code-block} python
:lineno-start: 1

from interactionfreepy import IFWorker

worker = IFWorker('interactionfree.cn:1061')
```

After connecting to the *Broker*, you can check the protocol version to ensure the connectivity.

```{code-block} python
:lineno-start: 1

print(worker.protocol())
```

The output should be `IF1` by default.

## Registrate a Service

After connecting to the *Broker*, you can register the *Worker* as a *Server* by invoking {py:meth}`bindService <interactionfreepy.worker.IFWorker.bindService>`.
We can still use the dragon cipher as an example.
If you have a class named `DragonCipher` that provides a function `encrypt_to_dragon_speech`, as defined below, 

```{code-block} python
:lineno-start: 1

class DragonCipher:
  def encrypt_to_dragon_speech(self, text: str) -> str:
    result = []
    for char in text:
      lower_char = char.lower()
      if lower_char in {'a', 'e', 'i', 'o', 'u'}:
        new_char = '*'
      elif char.isalpha():
        new_char = f"{char}-ar" if char.isupper() else f"{char}-ar"
      else:
        new_char = char
      result.append(new_char)
    return ''.join(result)
```

You can simply publish it as a service by calling the `bindService` method of the `IFWorker` instance.

```{code-block} python
:lineno-start: 1

dragon_cipher = DragonCipher()
worker.registerAsService('DragonCipher', dragon_cipher)
```

You can even combine the creation of `IFWorker` instance and binding the service together, as follows,

```{code-block} python
:lineno-start: 1

worker = IFWorker('tcp://interactionfree.cn:1061', 'DragonCipher_Aelice', DragonCipher())
```

## Invoking a remote Service

An `IFWorker`, whether named or anonymous, can invoke a remote service by calling the function directly.
As a client, you do not need to provide the service address or the instance of the service.
With the broker address provided, you can list all the services available by calling `listServiceNames()`.
Then, you can call the service directly by using the service name as an attribute of the worker instance, `worker.DragonCipher_Alice.encrypt_to_dragon_speech(human_speech)`.
The most interesting part is that you can run the code on a completely different machine, and never need to know the implementation details of the service.
You do not even need to import anything related to the server.

For example, if you have a *Server* named `DragonCipher` that provides a function `encrypt_to_dragon_speech`, you can call it from a completely machine by:

```{code-block} python
:lineno-start: 1

from interactionfreepy import IFWorker

worker = IFWorker('interactionfree.cn:1061')

humam_speech = 'To be or not to be'
dragon_speech = worker.DragonCipher_Alice.encrypt_to_dragon_speech(humam_speech)
print(f'{humam_speech} -> {dragon_speech}')
```

The parameters can be numbers, strings, lists, maps, or any data type that is supported by the standard MessagePack protocol, see [here]( https://github.com/msgpack/msgpack/blob/master/spec.md).

With this code running, you might get the output like this:

```{code-block} shell

['DragonCipher_Alice']
To be or not to be -> T-ar* b-ar* *r-ar n-ar*t-ar t-ar* b-ar*
```

(costomize-manager)=
## Customizing the Manager

As mentioned above, any function invoked on `IFWorker` without specifying a `ServiceName` will be routed to the *Broker*'s `Manager`.
By default, the `IFBroker` uses an instance of {py:class}`Manager <interactionfreepy.broker.Manager>` as its manager.
You can customize the manager by inheriting the `Manager` class and overriding the methods you want to customize, or adding new methods.

For example, if you want to add two new methods, one is `echo` and the other is `whatIsMyID`, to the manager, you can do it when creating the `IFBroker` instance, as follows,

```{code-block} python
:lineno-start: 1

from interactionfreepy import IFBroker
from interactionfreepy.broker import Manager

class CustomManager(Manager):
    def echo(self, sourcePoint, message):
        return f'ECHO: {message}'

    def whatIsMyID(self, sourcePoint):
        return f'Your ID is {sourcePoint}.'

broker = IFBroker(manager=CustomManager())
IFLoop.join()
```

Here, the `echo` method simply returns the message passed to it, and the `whatIsMyID` method returns the unique ID of the caller.
Please note that the first parameter for a method of the manager must be `sourcePoint`, which is a special parameter that will be automatically passed by the protocol, indicating the unique ID of the caller.

Then, any `IFWorker` connected to the new `IFBroker` can invoke these methods.

```{code-block} python
:lineno-start: 1

echo = worker.echo('response to me!')
myID = worker.whatIsMyID()
print(echo)
print(myID)
```

and get results like

```{code-block} shell
ECHO: response to me!
Your ID is b'\x00k\x8bEg'.
```

Of course, the specific ID will be different in your case, and maybe at each run.
You can also add a filter for the `ServiceName` by overloading the method {py:meth}`bindService <interactionfreepy.broker.Manager.registerAsService>`, requiring that `ServiceName` must begin with a capital letter.

```{code-block} python
:lineno-start: 1

from interactionfreepy import IFBroker
from interactionfreepy.broker import Manager

class CustomManager(Manager):
    def registerAsService(self, sourcePoint, name, interfaces=None, force=False):
        if not name or not name[0].isalpha() or not name[0].isupper():
          raise Exception('The first letter of the service name should be uppercase.')
        return super().registerAsService(sourcePoint, name, interfaces, force)

broker = IFBroker(manager=CustomManager())
IFLoop.join()
```

Then if you register a *Server* with an invalid `ServiceName`, you should get the exception,

```{code-block} shell
interactionfreepy.core.IFException: The first letter of the service name should be uppercase.
```

