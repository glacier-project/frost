import abc
from typing import List, Callable, Any
from simulation_message import Operation

class Stepper:
    def __init__(self, step: int, current_simulation_time: int):
        """
        Inizializza lo step.

        :param step: Il tempo da simulare in questo step (es. nanosecondi).
        :param current_simulation_time: Il tempo di simulazione corrente.
        """
        self._step = step
        self._current_simulation_time = current_simulation_time

    @property
    def step(self) -> int:
        """
        Restituisce il tempo da simulare in questo step.

        :return: Il tempo da simulare.
        """
        return self._step
    
    @step.getter
    def step(self) -> int:
        """
        Restituisce il tempo da simulare in questo step.

        :return: Il tempo da simulare.
        """
        return self._step

    @step.setter
    def step(self, value: int) -> None:
        """
        Imposta il tempo da simulare in questo step.

        :param value: Il nuovo tempo da simulare.
        """
        self._step = value

    @property
    def current_simulation_time(self) -> int:
        """
        Restituisce il tempo di simulazione corrente.

        :return: Il tempo di simulazione corrente.
        """
        return self._current_simulation_time

    @current_simulation_time.getter
    def current_simulation_time(self) -> int:
        """
        Restituisce il tempo di simulazione corrente.

        :return: Il tempo di simulazione corrente.
        """
        return self._current_simulation_time

    @current_simulation_time.setter
    def current_simulation_time(self, value: int) -> None:
        """
        Imposta il tempo di simulazione corrente.

        :param value: Il nuovo tempo di simulazione corrente.
        """
        self._current_simulation_time = value

    def __call__(self) -> None:
        return None
    
