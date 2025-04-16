# Frost 💠
Frost is an open source Digital Twin development Platform supporting early manufacturing software validation and testing.
It enables fast modeling of machineries and simple deployment on the infrastructure.

Frost is built on top of the Lingua Franca framework [(LF)](https://www.lf-lang.org/), which ensures deterministic execution, enhancing the reliability of soft-ware prototyping and testing. 


## Frost components
The platform pillars are Frost Machine and Frost Bus. The former implements an empty model that provides an interface between the Frost platform and the new model behavior. 
The latter implements the message broker that forwards messages to the target component.

### Frost Reactor

It is the brick of our platform. It instatiates the multiports for communication, the data model, message manager and so on.

It just has one reaction that is used for setting up the logger.

### Frost Bus

It serves as message broker and connects all the machine in the simulation.

It forwards any message to its target destination. At the start, it receives a series of registration messages from all the neighbours and stores their port in a map.
In this way, the map doesn't need to be implemented by hand and the you may change the link among ports without any worry.

### Frost Machine
Frost Machine is a Lingua Franca reactor that extends Frost Reactor and instantiates a set of procedures for variable update handling, message incoming, answering and connecting to the Bus.

This reactor creates a virtual environment where the new user can extend this reactor and set up its machine behavior without carying about communication and synchronization.

## How to develop new models?

The development is summarized in the following step:

1) Extend Frost Machine reactor.
```python
reactor TrafficLight extends GlacierMachine
```
2) initialize Lingua Franca states with the nodes you need in the simulation.
```python
state modality = {= self.data_model.get_node("TrafficLight/mode")=}
```
3) Implement and pass callbacks.
```python
method call(ins){=
    self.logger.info("Received: %s", ins)
    if ins == 0:
        self.error.value = 1      
    else:
        self.req.value = 0
    return ins
=}

reaction(startup){=
    self.c.callback = self.call
=}  
```
4) Implement timely behavior through timers, logical actions or by implementing specific reaction for MethodNodes.
```python
timer t(0 nsec, 1 nsec)
reaction(t) -> work{=
    if self.w.value == True:
        work.schedule(NSEC(self.num))
        self.w.value = False
=}
```
5) Add the new reactor to the Main one and prepare some message for testing its functionalities.

## Examples

In the repository `example/ICE` you can find a project representing the ICE laboratory of Verona, Italy [(ICE)](https://www.icelab.di.univr.it/).
In that project we developed the entire plant and a Scheduler that triggers each machine for performing operations. The Scheduler prepares a set of Frost Messages (see [Frost Messages](https://www.icelab.di.univr.it/)) that replicates an industrial recipe used in the real laboratory.