# Examples

Minimal programs, from the bare FMU to an FMU on a Frost network: two on `Feedthrough.fmu` (FMI 3.0, copies its
input to its output, can roll back), two on the traffic intersection of `test/resources/fmu/` (one controller,
four lights). Each logs what is committed at every tag and changes an input between two steps.

| Example | Reactor | Shows |
|---|---|---|
| `src/SingleFmu.lf` | `FrostFmu` with `path` | One FMU, no data model, no ports. LF time drives the FMU; `_commit()` publishes, `fmu_inputs` + `_set_trigger()`, `_set_inputs()`, `_commit()`, `_resume(tick)` change an input at the current tag. |
| `src/FmuGroup.lf` | `FrostFmu` with `fmus` | The controller drives the four lights inside one reactor: `fmus` and `connections` in `config/fmu_group.yml`, dotted names `"<member>.<variable>"`; phase changes become tags; `emergency_stop` at 21 s, released at 28 s. |
| `src/NodeWithFmuGroup.lf` | `FrostFmuNode` with `fmus` | The same intersection on the data model of a `FrostNode` (`data_model/intersection.yml`), no network: `_bind_inputs()` maps a node to a dotted input, `_commit()` writes the outputs on their nodes, a local write is applied by `_external_trigger(tick)`. |
| `src/ReactorWithFmu.lf` | `FrostReactor` + `FrostFmuNode` with `path` | `Feedthrough.fmu` on a Frost network (`data_model/feedthrough_machine.yml`, node names other than the FMU ones): an operator node writes the setpoint and reads the measure through a `FrostLink`; `reaction(request_messages)` calls `_external_trigger(tick)`. |

Run from this folder:

```sh
lfc src/SingleFmu.lf && bin/SingleFmu
lfc src/FmuGroup.lf && bin/FmuGroup
lfc src/NodeWithFmuGroup.lf && bin/NodeWithFmuGroup
lfc src/ReactorWithFmu.lf && bin/ReactorWithFmu
```

Without `FROST_CONFIG`, a program loads `config/<program name in snake_case>.yml` from the current folder;
set `FROST_CONFIG` to use another file.

`SingleFmu` logs the output still at `0.0` up to 200 ms and `5.0` from 250 ms on: the input written at 250 ms
takes effect at that tag, not at the next step. `ReactorWithFmu` does the same at 2250 ms, after the link has
connected the nodes, and the read at 2300 ms answers `5.0`. The intersection examples log the lights at 2, 12,
15, 17 s (phase changes, off the 5 s grid); the emergency set at 21 s turns everything red from the next tag,
and after the release at 28 s the cycle restarts with 2 s of all red.

The FMU paths (`path`, or `fmus` and `connections`) and `step_size` come from the YAML in `config/`
(`Feedthrough.fmu` declares no step size); the reactors log at `INFO`, set there too.
The main file must `from frost import *` in a preamble: Frost reactors read `FROST_CONFIG` from it.
