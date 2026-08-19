# 💠 Frost

Frost is an open-source framework for the development, testing, and deployment of software applications for controlling and supervising industrial machines. The focus of the framework is on implementing a unified and extensible interface for the development of machine control software, which can be used in different industrial contexts.

Frost enables the development and testing of software applications in a virtual environment (i.e., a Digital Twin) before deploying them on the actual machine. Once the software is validated in the virtual environment, it can be deployed on the real system with minimal/no changes.

Frost is built on top of the [Lingua Franca framework (LF)](https://www.lf-lang.org/), which ensures deterministic execution, enhancing the reliability of soft-ware prototyping and testing.
Frost is part of the [Glacier project](https://glacier-project.github.io/glacier-website/). 

## Frost components

*FrostReactor* is the main building block of the Frost framework: a ready-to-use reactor that can be extended to implement a component's behavior. It bundles logging, message handling, and a data-model–backed interface so that custom components only need to define their domain logic.
*FrostLink* is the message router of the Frost network: it registers the components connected to it and forwards messages between them based on their target.
Both reactors descend from *FrostBase* and rely on the [data model library](https://github.com/glacier-project/machine-data-model) to expose their interfaces.
Custom components are developed by extending *FrostReactor* and implementing the desired behavior.

## Using Frost as a Lingua Franca package

Frost follows the [Lingua Franca package convention](https://github.com/lf-lang/pkgs):
reusable reactors live in `src/lib/` and are imported with angle brackets.

Clone Frost into the `lf-packages` directory at the root of your project:

```bash
git clone https://github.com/glacier-project/frost.git lf-packages/frost
```

Or, if your project is a git repository, add it as a submodule:

```bash
git submodule add https://github.com/glacier-project/frost.git lf-packages/frost
```

Alternatively, point the `LF_PACKAGES` environment variable at a directory
containing the clone.

Then import the reactors in your `.lf` files:

```
import FrostReactor from <frost/FrostReactor.lf>
import FrostLink from <frost/FrostLink.lf>
import FrostScheduler from <frost/scheduler/FrostScheduler.lf>
```

The Python helper modules are referenced through the `files` target property:

```
target Python{
    files: [
        "../lf-packages/frost/src/python_lib/frost.py",
        "../lf-packages/frost/src/python_lib/l_formatter.py",
        "../lf-packages/frost/src/python_lib/time_utils.py",
    ],
}
```

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

1) Extend the *FrostReactor* reactor.
2) Define the state variables of the component and link them to the data model nodes.
3) Define the logic implementing the component behavior.
4) Instantiate the reactor in the main file and run it.

```python
# Extend the FrostReactor reactor
reactor TrafficLight extends FrostReactor{

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
 
## Citation ##

If you use **Frost**, please consider citing the papers listed below:

```
@inproceedings{frost:indin:2026,
  author    = {Turco, Pietro and Gaiardelli, Sebastiano and Fraccaroli, Enrico and Cheng, Dong Seon and Lora, Michele and Fummi, Franco},
  booktitle = {2026 IEEE 24rd International Conference on Industrial Informatics (INDIN)},
  title     = {{Distributed Control Logic Validation through Lingua Franca}},
  year      = {2026}
}
@inproceedings{frost:indin:2025,
  author    = {Turco, Pietro and Gaiardelli, Sebastiano and Fraccaroli, Enrico and Lora, Michele and Chakraborty, Samarjit and Fummi, Franco},
  booktitle = {2025 IEEE 23rd International Conference on Industrial Informatics (INDIN)},
  title     = {{Frost: A Simulation Platform for Early Validation and Testing of Manufacturing Software}},
  year      = {2025}
}
```