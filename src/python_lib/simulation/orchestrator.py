from stepper import Stepper
from typing import List
from typing_extensions import override


class OrchestratorStepper(Stepper):
    """
    Classe di utilità per orchestrare gli step.
    """
    def __init__(self, step: int, current_simulation_time: int):
        """
        Inizializza l'OrchestratorStep.

        :param step: Il tempo da simulare in questo step.
        :param current_simulation_time: Il tempo di simulazione corrente.
        """
        super().__init__(step, current_simulation_time)
        self._steps: List[int] = []

    def add_step(self, step: int) -> None:
        """
        Aggiunge un nuovo valore alla lista degli step
        """
        self._steps.append(step)

    def compute_next_step(self, values: List[int]) -> int:
        """
        Calcola il valore minimo da una lista di interi.

        :param values: Una lista di valori interi.
        :return: Il valore minimo nella lista.
        """
        if not values:
            raise ValueError("La lista dei valori non può essere vuota.")
        return min(values)
    
    @override
    def __call__(self) -> int:
        """
        Restituisce il prossimo step da eseguire.

        :return: Il prossimo step come intero.
        """
        if not self._steps:
            raise ValueError("Nessuno step è stato aggiunto.")
        next_step = self.compute_next_step(self._steps)
        self._steps.clear()
        return next_step

    

    
    

