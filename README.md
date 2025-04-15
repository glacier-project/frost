# Frost
Forst is an open source Digital Twin development Platform supporting early manufacturing software validation and testing.
It enables fast modeling of machineries and simple deployment on the infrastructure.

Frost is built on top of the Lingua Franca framework [(LF)](https://www.lf-lang.org/), which ensures deterministic execution, enhancing the reliability of soft-ware prototyping and testing. 


## Frost components
The platform pillars are Frost Machine and Frost Bus. The former implements an empty model that provides an interface between the Frost platform and the new model behavior. 
The latter implements the message broker that forwards messages to the target component.

### Frost Machine
Frost Machine is a Lingua Franca reactor that extends Frost Reactor and instantiates a set of procedures for variable update handling, message incoming, answering and connecting to the Bus.

The Frost Reactor is far more simple as it just imports the data model and the Frost Protocol Manager.

The combination of these 2 reactor connects the new machine to the rest of the system.

## How to develop new models?

The development is summarized in the following step:

1) Extend Frost Machine reactor.
2) initialize Lingua Franca states with the nodes you need in the simulation.
3) Implement and pass callbacks.
4) Implement timely behavior through timers, logical actions or by implementing specific reaction for MethodNodes.
5) Add the new reactor to the Main one and prepare some message for testing its functionalities.

## Examples

In the repository `example/ICE` you can find a project representing the ICE laboratory of Verona, Italy [(ICE)](https://www.icelab.di.univr.it/).
In that project we developed the entire plant and a Scheduler that triggers each machine for performing operations. The Scheduler prepares a set of Frost Messages (see [Frost Messages](https://www.icelab.di.univr.it/)) that replicates an industrial recipe used in the real laboratory.

## Benchmark

In the folder `benchmark/INDIN` there are 6 projects used for measuring the overhead introduced by Frost Platform that we developed for the INDIN conference. We developed for each project the Lingua Franca baseline model of the system and its Frost version.

A pyhton script is available for testing your own project performance.