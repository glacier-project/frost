from dataclasses import dataclass


@dataclass
class Stepper:
    """
    Holds the time to simulate in a step and the current simulation time.
    """
    step: int
    current_simulation_time: int

    def __call__(self) -> None:
        return None
