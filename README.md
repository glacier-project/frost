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

### Prerequisites

To build and run this project, you will need the following prerequisites:

- **Lingua Franca:** This project is built using the Lingua Franca framework. You can find installation instructions on the [Lingua Franca website](https://www.lf-lang.org/docs/handbook/getting-started).

    You can install Lingua Franca using the following command:

    ```bash
    curl -Ls https://install.lf-lang.org | bash -s cli
    ```

    After installation, you may need to add the Lingua Franca binary to your PATH. Follow the instructions provided by the installer.


- **Python:** Python 3.12 or later is required. You can download it from the [Python website](https://www.python.org/).

- **Python Packages:** The project requires several Python packages. You can install them by running the following command in the root of the project:

  ```bash
  pip install -r requirements.txt
  ```

- **Make:** The `make` build automation tool is used to simplify the build and test process.

### Development

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

## Contributing

Contributions are welcome! If you have suggestions for improvements or features, please open an issue or submit a pull request.

### Development Setup

The development environment is managed with `pip`. To set up the development environment, follow these steps:

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd frost
   ```

2. **Create a virtual environment (recommended):**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3. **Install dependencies:**
   Execute the following command to install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

### Development

To ensure the stability and correctness of the codebase, it is important to run the test suite before committing any changes. The project provides a convenient `Makefile` target for this purpose.

To build and run all the tests, execute the following command from the root of the project:

```bash
make test
```

This command will:
1.  Find all the `.lf` test files in the `test/src` directory.
2.  Build each test using the Lingua Franca compiler.
3.  Run the compiled test binaries.
4.  Provide a summary of the test results, indicating which tests passed and which failed.

This process is managed by the `test/run_all.sh` script, which is invoked by the `Makefile`.

This project uses [act](https://github.com/nektos/act) to enable local execution of GitHub Actions workflows. This allows you to test CI/CD pipelines locally before pushing changes to the repository.

 
