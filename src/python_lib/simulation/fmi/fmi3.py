"""FMI 3.0 Co-Simulation slave for FrostFmu.

fmi2.FMU2Frost exposes the same methods, so FrostFmu never branches on the
FMI version.
"""

import shutil
from typing import Any

from fmpy.fmi3 import FMU3Slave, fmi3FMUState
from fmpy.model_description import ModelDescription, ModelVariable
from fmpy.simulation import (
    apply_start_values,
    settable_in_initialization_mode,
)
import numpy as np


# fmpy picks the C functions to load from the class name, which must start
# with "FMU3".
class FMU3Frost(FMU3Slave):
    """fmpy FMI 3.0 slave plus the version-specific steps of FrostFmu.

    Attributes:
        description (ModelDescription):
            Parsed model description.
        event_mode_used (bool):
            Whether the FMU was instantiated with Event Mode.
        in_event (bool):
            Whether the FMU sits in Event Mode, waiting for settle().
        terminated (bool):
            Whether the FMU requested termination while settling an event.
        next_event_time (float | None):
            Model time of the next time event, from the last settle(); None
            when the FMU defines none.

    """

    def __init__(
        self,
        unzipdir: str,
        description: ModelDescription,
        instance_name: str,
    ) -> None:
        """Load the library and instantiate.

        Event Mode and early return are used when the FMU declares them.

        Args:
            unzipdir (str):
                Extracted archive directory.
            description (ModelDescription):
                Parsed fmpy model description.
            instance_name (str):
                Name the FMU logs under.

        """
        co_simulation = description.coSimulation
        super().__init__(
            guid=description.guid,
            modelIdentifier=co_simulation.modelIdentifier,
            unzipDirectory=unzipdir,
            instanceName=instance_name,
        )
        self.description = description
        self.event_mode_used = co_simulation.hasEventMode
        self.in_event = False
        self.terminated = False
        self.next_event_time = None
        self.instantiate(
            eventModeUsed=self.event_mode_used,
            earlyReturnAllowed=co_simulation.mightReturnEarlyFromDoStep,
        )

    def enter_initialization(
        self,
        tolerance: float | None,
        start_time: float,
        stop_time: float | None,
    ) -> None:
        """Enter Initialization Mode with the experiment.

        Args:
            tolerance (float | None):
                Relative tolerance; None leaves the FMU default.
            start_time (float):
                Model time the simulation starts at.
            stop_time (float | None):
                Model time the simulation stops at; None for no limit.

        """
        self.enterInitializationMode(
            tolerance=tolerance,
            startTime=start_time,
            stopTime=stop_time,
        )

    def exitInitializationMode(self) -> None:  # noqa: N802
        """Leave Initialization Mode and settle the initial event, if any.

        With Event Mode the FMU enters Event Mode first; it is settled at once,
        so that the first commit shows the state after it.
        """
        super().exitInitializationMode()
        self.in_event = self.event_mode_used
        self.settle()

    def setFMUState(self, state: fmi3FMUState) -> None:  # noqa: N802
        """Restore a state; FrostFmu saves states only in Step Mode.

        Args:
            state (fmi3FMUState):
                State returned by getFMUState().

        """
        super().setFMUState(state)
        self.in_event = False
        self.terminated = False
        self.next_event_time = None

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
        """Read one variable.

        Args:
            variable (ModelVariable):
                fmpy variable to read.

        Returns:
            Any:
                The value; arrays come back in their declared shape.

        """
        type_name = "Int64" if variable.type == "Enumeration" else variable.type
        values = getattr(self, f"get{type_name}")(
            [variable.valueReference],
            nValues=int(np.prod(variable.shape)),
        )
        if variable.shape:
            return np.reshape(values, variable.shape)
        return values[0]

    def write(self, variable: ModelVariable, value: Any) -> None:
        """Write one variable; arrays are flattened.

        Args:
            variable (ModelVariable):
                fmpy variable to write.
            value (Any):
                Value to write.

        """
        type_name = "Int64" if variable.type == "Enumeration" else variable.type
        getattr(self, f"set{type_name}")(
            [variable.valueReference],
            np.ravel(value).tolist(),
        )

    def settle(self) -> bool:
        """Settle a pending event, then return to Step Mode.

        Iterate the discrete states until they no longer change.

        Returns:
            bool:
                True when the FMU requested termination.

        """
        while self.in_event:
            needs_update, terminate, _, _, defined, next_time = (
                self.updateDiscreteStates()
            )
            self.next_event_time = next_time if defined else None
            if terminate:
                self.terminated = True
                self.in_event = False
            elif not needs_update:
                self.enterStepMode()
                self.in_event = False
        return self.terminated

    def step(
        self,
        time: float,
        size: float,
        may_restore: bool,
    ) -> tuple[bool, float | None]:
        """Perform fmi3DoStep.

        On an event with Event Mode, enter Event Mode and settle it at once,
        so that the outputs show the state after the event.

        Args:
            time (float):
                Current communication point.
            size (float):
                Communication step size.
            may_restore (bool):
                Whether a state saved before this step may still be restored.

        Returns:
            tuple[bool, float | None]:
                Whether the FMU requests termination, and the time of an early
                return at an internal event, or None when the step reached
                time + size.

        """
        event, terminate, early, last = self.doStep(
            time,
            size,
            noSetFMUStatePriorToCurrentPoint=not may_restore,
        )
        if event and self.event_mode_used and not terminate:
            self.enterEventMode()
            self.in_event = True
            terminate = self.settle()
        return terminate, last if early else None
