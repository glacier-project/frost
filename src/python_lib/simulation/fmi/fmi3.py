"""FMI 3.0 Co-Simulation slave for FrostFmuBase.

fmi2.FMU2Frost exposes the same methods, so FrostFmuBase never branches on the
FMI version.
"""

from typing import Any

from fmpy.fmi3 import FMU3Slave, fmi3FMUState
from fmpy.model_description import ModelDescription, ModelVariable
import numpy as np


# fmpy picks the C functions to load from the class name, which must start
# with "FMU3".
class FMU3Frost(FMU3Slave):
    """fmpy FMI 3.0 slave plus the version-specific steps of FrostFmuBase.

    Attributes:
        event_mode_used (bool):
            Whether the FMU was instantiated with Event Mode.
        in_event (bool):
            Whether the FMU sits in Event Mode, waiting for settle().

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
        self.event_mode_used = co_simulation.hasEventMode
        self.in_event = False
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
        """Leave Initialization Mode.

        With Event Mode the FMU enters Event Mode first, so settle() must run
        before the first step.
        """
        super().exitInitializationMode()
        self.in_event = self.event_mode_used

    def setFMUState(self, state: fmi3FMUState) -> None:  # noqa: N802
        """Restore a state; FrostFmuBase saves states only in Step Mode.

        Args:
            state (fmi3FMUState):
                State returned by getFMUState().

        """
        super().setFMUState(state)
        self.in_event = False

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
                True when the FMU requests termination.

        """
        if not self.in_event:
            return False
        while True:
            needs_update, terminate, *_ = self.updateDiscreteStates()
            if terminate:
                return True
            if not needs_update:
                break
        self.enterStepMode()
        self.in_event = False
        return False

    def step(
        self,
        time: float,
        size: float,
        may_restore: bool,
    ) -> tuple[bool, float | None]:
        """Perform fmi3DoStep.

        On an event with Event Mode, enter Event Mode and leave it pending for
        settle().

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
        return terminate, last if early else None
