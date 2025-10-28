import abc
from typing import List, Callable, Any
from simulation_message import Operation

class Stepper:
    def __init__(self, step: int, current_simulation_time: int):
        """
        Initializes the step.

        :param step: The time to simulate in this step (e.g., nanoseconds).
        :param current_simulation_time: The current simulation time.
        """
        self._step = step
        self._current_simulation_time = current_simulation_time

    @property
    def step(self) -> int:
        """
        Returns the time to simulate in this step.

        :return: The time to simulate.
        """
        return self._step
    
    @step.getter
    def step(self) -> int:
        """
        Returns the time to simulate in this step.

        :return: The time to simulate.
        """
        return self._step

    @step.setter
    def step(self, value: int) -> None:
        """
        Sets the time to simulate in this step.

        :param value: The new time to simulate.
        """
        self._step = value

    @property
    def current_simulation_time(self) -> int:
        """
        Returns the current simulation time.

        :return: The current simulation time.
        """
        return self._current_simulation_time

    @current_simulation_time.getter
    def current_simulation_time(self) -> int:
        """
        Returns the current simulation time.

        :return: The current simulation time.
        """
        return self._current_simulation_time

    @current_simulation_time.setter
    def current_simulation_time(self, value: int) -> None:
        """
        Sets the current simulation time.

        :param value: The new current simulation time.
        """
        self._current_simulation_time = value

    def __call__(self) -> None:
        return None
    

