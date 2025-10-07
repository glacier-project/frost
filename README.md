# 💠 Frost

Frost is an open-source framework for the development, testing, and deployment of software applications for controlling and supervising industrial machines. The focus of the framework is on implementing a unified and extensible interface for the development of machine control software, which can be used in different industrial contexts.

Frost enables the development and testing of software applications in a virtual environment (i.e., a Digital Twin) before deploying them on the actual machine. Once the software is validated in the virtual environment, it can be deployed on the real system with minimal/no changes.

Frost is built on top of the [Lingua Franca framework (LF)](https://www.lf-lang.org/), which ensures deterministic execution, enhancing the reliability of soft-ware prototyping and testing.
Frost is part of the [Glacier project](https://glacier-project.github.io/glacier-website/). 

## Frost components

*FrostMachine* and *FrostBus* are the main components of the Frost framework. 
The former implements a ready-to-use reactor that can be extended to implement the machine behavior, while the latter implements a message broker that connects all the components of the system being represented.
Both components extend the base class *FrostReactor*, which implements some basic functionalities such as logging and message handling.
The *FrostReactor* relies on the [data model library](https://github.com/glacier-project/machine-data-model) to implement the component interfaces.
Custom components can be developed by extending the *FrostReactor* class and implementing the desired behavior.

## How to develop new machine interfaces?

The development is summarized in the following step:

1) Extend *Frost Machine* reactor.
2) Definite the state variables of the machine and link them to the data model nodes.
3) Define the logic implementing the machine behavior.
4) Instantiate the reactor in the main file and run it.

```python
# Extend the FrostMachine reactor
reactor TrafficLight extends FrostMachine{

    # State variables of the machine 
    state mode

    # Method for implementing the machine behavior
    method m(ins){=
        self.logger.info("Received: %s", ins)
        if ins == 0:
            self.error.value = 1      
        else:
            self.req.value = 0
        return ins
    =}

    # Link the state variables to the data model nodes
    # and set the method as callback  
    reaction(startup){=
        self.mode = self.data_model.get_node("TrafficLight/Mode")
        method_node = self.data_model.get_node("TrafficLight/")
        method_node.callback = self.m
    =}  

    # Custom logic updating the state variables
    timer t(0 s, 1 s)
    reaction(t) -> work{=
        if self.mode.value == LIGHT_GREEN:
            self.mode.value = LIGHT_RED
        else:
            self.mode.value = LIGHT_GREEN
    =}
}
```

Then instantiate the following reactor with:

```python
import TrafficLight from "TrafficLight.lf"

main reactor{
    tl = TrafficLight(model_path="path/to/model.yaml")
    ...
}
```

## Examples

- [ICE Laboratory](examples/ICE): The directory contains an implementation of the production line of the [ICE Laboratory](https://www.icelab.di.univr.it/) of Verona, Italy. A Scheduler controls the production by sending requests to the different machines of the plant The example is still under development and will be updated soon.
