# InteractionFree

*v1.0.20200320*

------

InteractionFree is a remote procedure call (RPC) framework that is initially designed for device control and data processing in quantum optics lab. Nevertheless, is can be used in any scene of distributed computing.



### Topology

InteractionFree frame currently support star structure. There is a server (called Broker) that take TCP connections from all clients (called Worker). Thus, the IP address of the server should be reachable for all clients.



### Protocol

##### Transport

The framework is basically build on [ZeroMQ](https://zeromq.org/), thus remains a high flexibility of update in the future. A Broker is a ROUTER, while a Worker is a DEALER. When a Worker connects to the Broker, an identical address is assigned to the connection. Workers communicate to each other and to the Broker by sending Messages. A Message is a standard ZeroMQ multi-part message.

Message send to the Broker is organized as follows:


| &nbsp;Frame | &nbsp;Value | Explain |
| :-: | :-: | :-: |
| 0 | empty | Defined in ZeroMQ |
| 1 | 'IF1' | The version of InteractionFree |
|       2       | bytes |         Identity Message ID         |
|       3       |      string      | The distributing mode of the Message |
|       4       |     address | The target that the Message is expected to send to |
| 5 | string | The method of serialization for the content of invocation |
| 6 | Bytes | The content of the invocation |

Frame 0 to 4 are all information that the Broker needs to know. Frame 5 to $\infin$ are normally meaningless bytes for the Broker and will be transported to the expected target intactly. When transporting large amount of data, Zero-Copy could be employed for better performance.

The target of a message is specified by Frame 3 and 4. InteractionFree version 1.0 now support the following mode:

| Distributing-Mode |                           Address                            |
| :---------------: | :----------------------------------------------------------: |
|      Broker       | The Message is sending to the Broker, the address is undefined. Better to be empty. |
|      Direct       | The Message is sending to the Worker that has the corresponding address |
|      Service      |                 Explained in Service section                 |

Message send from the Broker is organized as follows:

| &nbsp;Frame | &nbsp;Value |                          Explain                          |
| :---------: | :---------: | :-------------------------------------------------------: |
|      0      |    empty    |                     Defined in ZeroMQ                     |
|      1      |    'IF1'    |              The version of InteractionFree               |
|      2      |    string    |                    Identity Message ID                    |
|      3      |   address   | The address that the Message is send from. b'' for Broker |
|      4      |   string    | The method of serialization for the content of invocation |
|      5      |    bytes    |               The content of the invocation               |



##### Remote Function Invoke

With InteractionFree, one can invoke a function on a remote program by sending Messages. Their are 2 types of invocation, named Request and Response. A Response contains the Message ID of the corresponding Request to indicate that which request is it replying. Thus, the invocation process can be run in complete asynchronous. The invocation is a serialized Map that contains the following content:

|       Key        | Value  |                           Explain                            |
| :--------------: | :----: | :----------------------------------------------------------: |
|       Type       | string |                      Request, Response                       |
|     Function     | string |                     On exists in Request                     |
|    Arguments     |  list  |                     On exists in Request                     |
| KeyworkArguments |  map   |                     On exists in Request                     |
|    ResponseID    | bytes  |                    Only exist in Response                    |
|      Result      |  any   |                    Only exist in Response                    |
|      Error       | string | Error message. When non emply, the Result value should be ignored |
|     Warning      | string |                       Warning message                        |

The serialization of invocation could be Messagepack or JSON for the current version. It is the Worker's responsibility to guarantee that the Response have the same serialization method with the corresponding Request.



##### Life-circle of Worker

After connected to the Broker, a Worker can register it self as a Service for the visibility to other workers. Just simply invoke the registerAsService function in Broker:

```
registerAsService: None (serviceName: String, interfaces: List[String])
```



##### Service







# Problems to be solved

1. what if the address is used up for connections.