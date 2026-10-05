# Examples

Two minimal programs on `Feedthrough.fmu` (FMI 3.0, copies its input to its output, can roll back).
Both change the input at 250 ms, between two 100 ms steps, and print the committed output at every tag.

| Example | Reactor | Shows |
|---|---|---|
| `src/FmuStandalone.lf` | `FrostFmu` | LF time drives the FMU; `_commit()` publishes, `fmu_inputs` + `_apply_input_now()` change an input at the current tag. |
| `src/FmuOnDataModel.lf` | `FrostFmuReactor` | The FMU on a data model whose node names differ from the FMU ones: `_bind_inputs()` maps a node to an input, `_commit()` writes an output on a node. |

Run from this folder:

```sh
lfc src/FmuStandalone.lf  && bin/FmuStandalone
lfc src/FmuOnDataModel.lf && bin/FmuOnDataModel
```

Without `FROST_CONFIG`, a program loads `config/<program name in snake_case>.yml` from the current folder;
set `FROST_CONFIG` to use another file.

Both print the output still at `0.0` up to 200 ms and `5.0` from 250 ms on: the input written at 250 ms
takes effect at that tag, not at the next step.

`step_size` comes from the YAML in `config/`, since `Feedthrough.fmu` declares no step size.
The main file must `from frost import *` in a preamble: Frost reactors read `FROST_CONFIG` from it.
