from enum import Enum
from typing import List


class Operation:
    """
    Defines the base operations for a simulation message.
    This class dynamically creates an Enum based on a list of strings.
    """
    _operations: List[str] = ["register", "simulate", "response"]
    _OpEnum: Enum = Enum("OpEnum", {op.upper(): op for op in _operations})

    def __init_subclass__(cls, **kwargs):
        """Dynamically creates the Enum for subclasses."""
        super().__init_subclass__(**kwargs)
        # Combine operations from parent classes with the subclass's own
        all_ops = []
        for base in reversed(cls.__mro__):
            if hasattr(base, '_operations'):
                all_ops.extend(op for op in base._operations if op not in all_ops)
        
        cls._OpEnum = Enum(f"{cls.__name__}OpEnum", {op.upper(): op for op in all_ops})
        for member in cls._OpEnum:
            setattr(cls, member.name, member.value)

    @classmethod
    def __contains__(cls, item):
        """Check if an item is a valid operation value."""
        return item in {member.value for member in cls._OpEnum}
    
    @classmethod
    def get_enum(cls):
        """Return the Enum class."""
        return cls._OpEnum
    
class DryRunOperation(Operation):
    """
    Extends Operation with simulation-specific commands.
    """
    _operations = ["dry_run"]

if __name__ == '__main__':
    # Ottiene il valore dell'operazione REGISTER
    register_value = Operation.get_enum().REGISTER.value

    # Verifica se il valore è un'operazione valida
    if register_value in Operation.get_enum():
        print(f"'{register_value}' è un'operazione valida.")
        # Stampa il valore
        print(f"Il valore di REGISTER è: {register_value}")

    # Esempio con la sottoclasse
    print("\n--- Esempio con DryRunOperation ---")
    
    # DryRunOperation eredita le operazioni da Operation
    if Operation.get_enum().REGISTER in DryRunOperation.get_enum():
        print(f"'{Operation.get_enum().REGISTER}' è un'operazione valida anche in DryRunOperation.")

    # E ha anche le sue operazioni specifiche
    dry_run_value = DryRunOperation.get_enum().DRY_RUN
    if dry_run_value in DryRunOperation.get_enum():
        print(f"'{dry_run_value.value}' è una nuova operazione in DryRunOperation.")

    # L'operazione della sottoclasse non è nella classe base
    if dry_run_value not in Operation.get_enum():
        print(f"'{dry_run_value.value}' non è un'operazione valida nella classe base Operation.")

