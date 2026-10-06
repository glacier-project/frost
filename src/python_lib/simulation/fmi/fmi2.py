"""FMI 2.0 Co-Simulation slave for FrostFmu.

fmi3.FMU3Frost exposes the same methods, so FrostFmu never branches on the
FMI version.
"""

import shutil
from typing import Any

from fmpy.fmi2 import FMU2Slave
from fmpy.model_description import ModelDescription, ModelVariable
from fmpy.simulation import (
    apply_start_values,
    settable_in_initialization_mode,
)


# fmpy picks the C functions to load from the class name, which must start
# with "FMU2".
class FMU2Frost(FMU2Slave):
    """fmpy FMI 2.0 slave plus the version-specific steps of FrostFmu.

    Attributes:
        description (ModelDescription):
            Parsed model description.
        next_event_time (None):
            Always None: FMI 2.0 Co-Simulation reports no time events.

    """

    next_event_time = None

    def __init__(
        self,
        unzipdir: str,
        description: ModelDescription,
        instance_name: str,
    ) -> None:
        """Load the library and instantiate.

        Args:
            unzipdir (str):
                Extracted archive directory.
            description (ModelDescription):
                Parsed fmpy model description.
            instance_name (str):
                Name the FMU logs under.

        """
        super().__init__(
            guid=description.guid,
            modelIdentifier=description.coSimulation.modelIdentifier,
            unzipDirectory=unzipdir,
            instanceName=instance_name,
        )
        self.description = description
        self.instantiate()

    def enter_initialization(
        self,
        tolerance: float | None,
        start_time: float,
        stop_time: float | None,
    ) -> None:
        """Communicate the experiment, then enter Initialization Mode.

        Args:
            tolerance (float | None):
                Relative tolerance; None leaves the FMU default.
            start_time (float):
                Model time the simulation starts at.
            stop_time (float | None):
                Model time the simulation stops at; None for no limit.

        """
        self.setupExperiment(
            tolerance=tolerance,
            startTime=start_time,
            stopTime=stop_time,
        )
        self.enterInitializationMode()

    def initialize(
        self,
        start_values: dict[str, Any],
        tolerance: float | None,
        start_time: float,
        stop_time: float | None,
    ) -> None:
        """Write the start values in Initialization Mode and enter Step Mode.

        Args:
            start_values (dict[str, Any]):
                Values keyed by variable name.
            tolerance (float | None):
                Relative tolerance; None leaves the FMU default.
            start_time (float):
                Model time the simulation starts at.
            stop_time (float | None):
                Model time the simulation stops at; None for no limit.

        """
        self.enter_initialization(tolerance, start_time, stop_time)
        if rejected := apply_start_values(
            self,
            self.description,
            start_values,
            settable_in_initialization_mode,
        ):
            raise KeyError(
                f"{self.instanceName} cannot set {sorted(rejected)} in "
                "Initialization Mode"
            )
        self.exitInitializationMode()

    def close(self, terminate: bool) -> None:
        """Free the FMU and remove its extracted archive.

        Args:
            terminate (bool):
                Whether to terminate it first; only after initialize().

        """
        try:
            if terminate:
                self.terminate()
        finally:
            self.freeInstance()
            shutil.rmtree(self.unzipDirectory, ignore_errors=True)

    def read(self, variable: ModelVariable) -> Any:
        """Read one variable as a Python value.

        Args:
            variable (ModelVariable):
                fmpy variable to read.

        Returns:
            Any:
                The value; Boolean as bool and String as str.

        """
        type_name = (
            "Integer" if variable.type == "Enumeration" else variable.type
        )
        value = getattr(self, f"get{type_name}")([variable.valueReference])[0]
        if type_name == "Boolean":
            return bool(value)
        if type_name == "String":
            return value.decode("utf-8")
        return value

    def write(self, variable: ModelVariable, value: Any) -> None:
        """Write one variable.

        Args:
            variable (ModelVariable):
                fmpy variable to write.
            value (Any):
                Value to write.

        """
        type_name = (
            "Integer" if variable.type == "Enumeration" else variable.type
        )
        getattr(self, f"set{type_name}")([variable.valueReference], [value])

    def step(
        self,
        time: float,
        size: float,
        may_restore: bool,
    ) -> tuple[bool, float | None]:
        """Perform fmi2DoStep.

        Args:
            time (float):
                Current communication point.
            size (float):
                Communication step size.
            may_restore (bool):
                Whether a state saved before this step may still be restored.

        Returns:
            tuple[bool, float | None]:
                False, since an FMI 2.0 step cannot request termination
                without a Discard, and None, since FMI 2.0 has no early
                return.

        """
        self.doStep(
            time,
            size,
            noSetFMUStatePriorToCurrentPoint=not may_restore,
        )
        return False, None
