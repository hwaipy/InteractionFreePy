# Quick Start

**InteractionFreePy** is extremely easy to use.
Follow the steps below as a quick start.

1. Install

```{code-block} shell
  pip install interactionfreepy
```

2. Run a service

We assume Alice wants to publish a service that provides a dragon-language encryption for everyone.
She defines the service as follows:

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

As an example, the details of the implementation are not important.
It can be any function that does anything you want.
With the function defined, she can publish the service as follows:

```{code-block} python
:lineno-start: 1

from interactionfreepy import IFWorker, IFLoop

worker = IFWorker('tcp://interactionfree.cn:1061', 'DragonCipher_Alice', DragonCipher())
IFLoop.join()
```

Here, `tcp://interactionfree.cn:1061` is the address of the broker.
It is provided by the InteractionFreePy project for testing.
Due to the limitations of the server, visiting our public broker may be slow.
You can also host your own broker to ensure the performance, latency time, and privacy of your service.
See [Hosting a broker](host_a_broker) for more details.
`'DragonCipher_Alice'` is the name of the service, which can be any string that you want.
`DragonCipher()` provided the instance of the service.
Finally, `IFLoop.join()` prevents the main thread from exiting, keeping the service running.

3. Run a client

Now, Bob has some text that he wants to encrypt into dragon speech.

```{code-block} python
:lineno-start: 1

from interactionfreepy import IFWorker

worker = IFWorker('tcp://interactionfree.cn:1061')
print(worker.listServiceNames())
humam_speech = 'To be or not to be'
dragon_speech = worker.DragonCipher_Alice.encrypt_to_dragon_speech(humam_speech)
print(f'{humam_speech} -> {dragon_speech}')
```

As a client, he does not need to provide the service address or the instance of the service.
With the broker address provided, he can list all the services available by calling `listServiceNames()`.
Then, he can call the service directly by using the service name as an attribute of the worker instance, `worker.DragonCipher_Alice.encrypt_to_dragon_speech(human_speech)`.
The most interesting part is that Bob can run the code on a completely different machine and never needs to know the implementation details of the service.
He does not even need to import anything related to Alice.
With this code running, he might get the output like this:

```{code-block} shell

['DragonCipher_Alice']
To be or not to be -> T-ar* b-ar* *r-ar n-ar*t-ar t-ar* b-ar*
```

```{note}

The result of `listServiceNames()` may be different from the one shown above. 
It is the list of all the services that are currently running on the broker.
More importantly, as the service name is expected to be unique, you might get an error if you try to run the service with the same name as the one already running on the broker.
Therefore, when using my public testing broker located at `interactionfree.cn:1061`, it is recommended to use a unique name for your service, such as your GitHub username or any other unique identifier.
For example, as my GitHub username is `hwaipy`, I can use `DragonCipher_hwaipy` as the service name.
```

(host_a_broker)=
4. Host a broker

You can host your own broker by running the following code:

```{code-block} python
:lineno-start: 1

from interactionfreepy import IFBroker, IFLoop

broker = IFBroker()
IFLoop.join()
```

It will start a broker on the default port ``1061``.
You can also specify the port by passing the port number to the constructor:

```{code-block} python
:lineno-start: 1

from interactionfreepy import IFBroker, IFLoop

broker = IFBroker('tcp://*:999')
IFLoop.join()
```

You can also host the broker in a Docker container.
The Docker image is available as [hwaipy/ifbroker](https://hub.docker.com/r/hwaipy/ifbroker).
To run the broker in a Docker container, you can use the following command:

```{code-block} shell
docker run -d -p 1061:1061 --name IFBroker hwaipy/ifbroker:latest
```

