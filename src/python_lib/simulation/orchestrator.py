from stepper import Stepper
from typing import List
from typing_extensions import override


class OrchestratorStepper(Stepper):
    """
    Utility class for orchestrating steps.
    """
    def __init__(self, step: int, current_simulation_time: int):
        """
        Initializes the OrchestratorStep.

        :param step: The time to simulate in this step.
        :param current_simulation_time: The current simulation time.
        """
        super().__init__(step, current_simulation_time)
        self._steps: List[int] = []

    def add_step(self, step: int) -> None:
        """
        Adds a new value to the list of steps.
        """
        self._steps.append(step)

    def compute_next_step(self, values: List[int]) -> int:
        """
        Calculates the minimum value from a list of integers.

        :param values: A list of integer values.
        :return: The minimum value in the list.
        """
        if not values:
            raise ValueError("The list of values cannot be empty.")
        return min(values)
    
    @override
    def __call__(self) -> int:
        """
        Returns the next step to be executed.

        :return: The next step as an integer.
        """
        if not self._steps:
            raise ValueError("No steps have been added.")
        next_step = self.compute_next_step(self._steps)
        self._steps.clear()
        return next_step
