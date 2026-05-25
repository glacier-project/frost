from dataclasses import dataclass, field
from typing import List, Any
from operation import Operation


@dataclass
class SimulationMessage:
    """
    Represents a simulation message between two components.
    It is recommended to use the SimulationMessageBuilder to create instances.
    """
    sender: str
    target: str
    operation: Operation
    args: List[Any] = field(default_factory=list)

    def __repr__(self) -> str:
        return (f"SimMessage(sender='{self.sender}', target='{self.target}', "
                f"operation={self.operation.name}, args={self.args})")

    @staticmethod
    def get_builder() -> "SimulationMessageBuilder":
        """Returns a new builder for creating SimMessage instances."""
        return SimulationMessageBuilder()


class SimulationMessageBuilder:
    """
    Builder class for constructing SimMessage objects.
    """

    def __init__(self):
        self._sender: str | None = None
        self._target: str | None = None
        self._operation: Operation | None = None
        self._args: List[Any] = []

    def with_sender(self, sender: str) -> "SimulationMessageBuilder":
        """Sets the sender of the message."""
        self._sender = sender
        return self

    def with_target(self, target: str) -> "SimulationMessageBuilder":
        """Sets the target of the message."""
        self._target = target
        return self

    def with_operation(self, operation: Operation) -> "SimulationMessageBuilder":
        """Sets the operation for the message."""
        self._operation = operation
        return self

    def with_args(self, args: List[Any]) -> "SimulationMessageBuilder":
        """Sets the arguments for the message."""
        self._args = args
        return self

    def add_arg(self, arg: Any) -> "SimulationMessageBuilder":
        """Adds a single argument to the message's argument list."""
        self._args.append(arg)
        return self

    def build(self) -> SimulationMessage:
        """
        Constructs and returns the SimMessage object.

        Raises:
            ValueError: If sender, target, or operation are not set.
        """
        if self._sender is None:
            raise ValueError("Sender must be set before building.")
        if self._target is None:
            raise ValueError("target must be set before building.")
        if self._operation is None:
            raise ValueError("Operation must be set before building.")

        return SimulationMessage(
            sender=self._sender,
            target=self._target,
            operation=self._operation,
            args=self._args
        )
