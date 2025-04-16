# ICE
This project shapes the ICE laboratory [(ICE)](https://www.icelab.di.univr.it/) through **Frost** platform.

We developed each machine by extending the **Frost Machine** and we connected them through the **Frost Bus**.

We developed a **Scheduler** reactor that reads a recipe from an yml file and parses it into **Frost Messages**. The recipe is composition of two files: the recipe containing the commands to be sent and the conditions that are the responses we would like to have before advancing with the next task.

The Scheduler acts as an OPC UA client which sends messages to the bus and wait for answers.
