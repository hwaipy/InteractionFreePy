# InteractionFree for Python

**InteractionFree** is a remote procedure call (RPC) protocol.
It allows developers to build their own distributed and cross-language programs easily.
The protocol is config-less and extremely easy to use.
Currently, [`MessagePack`](https://msgpack.org) is used for binary serialization, and [`ZeroMQ`](https://zeromq.org) is used for communication.
This project, **InteractionFreePy**, is the Python implementation of the protocol.

PRC is a protocol that allows a computer program to execute a procedure or function on another computer, as if it were a local call.
This abstraction simplifies distributed system development by hiding the complexities of network communication.
The *InteractionFree* protocol is designed to be simple and efficient, allowing developers to focus on building their applications without worrying about the underlying communication details.

```{hint}

The name *InteractionFree* originates from the concept of **interaction-free measurement** in quantum physics.
In physics, interaction-free measurement is a type of measurement in quantum mechanics that detects the position, presence, or state of an object without an interaction occurring between it and the measuring device [^note1].
Essentially, in interaction-free measurement, although no probe particles (such as photons) reach the measured object (with intensity being zero), the phase of the probe particles is still affected by the measured object in reality, which reflects the object's properties.
The name of the RPC protocol *InteractionFree* is a metaphor for this physical phenomenon: developers appear not to have written code that transmits function calls to the other side, yet RPC genuinely occurs.
   
[^note1]: [https://en.wikipedia.org/wiki/Interaction-free_measurement](https://en.wikipedia.org/wiki/Interaction-free_measurement)

```

See this project in GitHub [hwaipy/InteractionFreePy](https://github.com/hwaipy/InteractionFreePy).

```{toctree}
:maxdepth: 2
:caption: Table of Contents

quickstart
concept
usage
spec
api
```