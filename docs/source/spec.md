# Spec

*v1.0.20251009*

------

**InteractionFree** is a remote procedure call (RPC) framework that is initially designed for device control and data processing in a quantum optics lab. Nevertheless, it can be used in any scene of distributed computing.

## Topology

**InteractionFree** frame currently supports star structure. There is one and only one center node called Broker that takes TCP connections from all clients (called Worker). Thus, the net address of the service should be reachable for all clients.

## Transport

The framework is basically built on [ZeroMQ](https://zeromq.org/), thus it remains highly flexible for updates in the future. A Broker is a ROUTER, while a Worker is a DEALER. When a Worker connects to the Broker, an identical address is assigned to the connection. Workers communicate with each other and with the Broker by sending Messages. A Message is a standard ZeroMQ multi-part message.

The Messages sent to the Broker is organized as follows:

| &nbsp;Frame | &nbsp;Value | Explain |
| :-: | :-: | :-: |
| 0 | empty | Defined in ZeroMQ |
| 1 | 'IF1' | The version of InteractionFree |
|       2       | string |         Identity Message ID         |
|       3       |      string      | The distributing mode of the Message |
|       4       |     address | The target that the Message is expected to send to |
| 5 | string | The method of serialization for the content of invocation |
| 6 | bytes | The content of the invocation |

Frames 0 to 4 contain information that the Broker needs to know. Frame 5 and subsequent frames are normally meaningless bytes for the Broker and will be transported to the expected target intact. When transporting a large amount of data, Zero-Copy is recommended for better performance.

The target of a message is specified by Frames 3 and 4. **InteractionFree** now supports the following mode:

| Distributing-Mode |                           Address                            |
| :---------------: | :----------------------------------------------------------: |
|      Broker       | The Message is sent to the Broker. The address is undefined. Better to be empty. |
|      Direct       | The Message is sent to the Worker that has the corresponding address |
|      Service      |                 Explained in Service section                 |

Messages sent from the Broker are organized as follows:

| &nbsp;Frame | &nbsp;Value |                          Explain                          |
| :---------: | :---------: | :-------------------------------------------------------: |
|      0      |    empty    |                     Defined in ZeroMQ                     |
|      1      |    'IF1'    |              The version of InteractionFree               |
|      2      |    string    |                    Identity Message ID                    |
|      3      |   address   | The address that the Message is sent from. b'' for Broker |
|      4      |   string    | The method of serialization for the content of invocation |
|      5      |    bytes    |               The content of the invocation               |


## Remote Function Invoke

With **InteractionFree**, one can invoke a function on a remote program by sending Messages. There are 2 types of invocation, named Request and Response. A Response contains the Message ID of the corresponding Request to indicate which request it is replying to. Thus, the invocation process can be run completely asynchronously. The invocation is a serialized Map that contains the following content:

|       Key        | Value  |                           Explain                            |
| :--------------: | :----: | :----------------------------------------------------------: |
|       Type       | string |                      Request, Response                       |
|     Function     | string |                     Only exists in Request                     |
|    Arguments     |  list<any>  |                     Only exists in Request                     |
| KeywordArguments |  map<string, any>   |                     Only exists in Request                     |
|    ResponseID    | bytes  |                    Only exist in Response                    |
|      Result      |  any   |                    Only exist in Response                    |
|      Error       | string | Error message. When non-empty, the Result value should be ignored |
|     Warning      | string |                       Warning message                        |

The serialization of invocation is [MessagePack](https://msgpack.org/index.html) for the current version. It is the Worker's responsibility to guarantee that the Response has the same serialization method as the corresponding Request. Any data type that is supported by the standard **MessagePack** protocol is supported for `Result`, the elements of `Arguments`, and the values of `KeywordArguments`.

There is several functions defined for the broker as follows,

1. `registerAsService(serviceName, interfaces, force)`

Register a worker as a service.

`serviceName`: (string) The name of the service.

`interfaces`: (list\<string>, optinal) The interfaces of the service.

`force`: (bool, optinal) If True, the service will be registered even if the name is occupied. The old service will be replaced.

return: none

2. `getAddressOfService(serviceName)`

Get the address of a service.

`serviceName`: (string) The name of the service.

return: (string) The address of the service.

3. `unregister()`

Unregister a worker.

return: none

<!-- ## Life-circle of Worker

After connecting to the Broker, a Worker can register itself as a Service for the visibility to other workers. Just simply invoke the registerAsService function in Broker:

```
registerAsService: None (serviceName: String, interfaces: List[String])
```


## Service

Service
 -->
