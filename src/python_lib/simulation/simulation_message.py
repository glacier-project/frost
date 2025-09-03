from enum import Enum
from typing import List, Any
from abc import ABC
from typing import Callable, Dict, Any
from operation import Operation


class SimulationMessage:
    """
    Represents a simulation message between two components.
    """
    def __init__(self, sender: str, target: str, operation: Operation, args: List[Any]):
        """
        Initializes a SimMessage instance.
        It is recommended to use the SimulationMessageBuilder to create instances.
        """
        self._sender = sender
        self._target = target
        self._operation = operation
        self._args = args

    @property
    def sender(self) -> str:
        """Gets the sender of the message."""
        return self._sender

    @sender.getter
    def sender(self) -> str:
        """Gets the sender of the message."""
        return self._sender

    @sender.setter
    def sender(self, value: str):
        """Sets the sender of the message."""
        self._sender = value

    @property
    def target(self) -> str:
        """Gets the target of the message."""
        return self._target

    @target.getter
    def target(self) -> str:
        """Gets the target of the message."""
        return self._target

    @target.setter
    def target(self, value: str):
        """Sets the target of the message."""
        self._target = value

    @property
    def operation(self) -> Operation:
        """Gets the operation of the message."""
        return self._operation

    @operation.getter
    def operation(self) -> Operation:
        """Gets the operation of the message."""
        return self._operation

    @operation.setter
    def operation(self, value: Operation):
        """Sets the operation of the message."""
        self._operation = value

    @property
    def args(self) -> List[Any]:
        """Gets the arguments of the message."""
        return self._args
    
    @args.getter
    def args(self) -> List[Any]:
        """Gets the arguments of the message."""
        return self._args

    @args.setter
    def args(self, value: List[Any]):
        """Sets the arguments of the message."""
        self._args = value

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

    def set_sender(self, sender: str) -> "SimulationMessageBuilder":
        """Sets the sender of the message."""
        self._sender = sender
        return self

    def set_target(self, target: str) -> "SimulationMessageBuilder":
        """Sets the target of the message."""
        self._target = target
        return self

    def set_operation(self, operation: Operation) -> "SimulationMessageBuilder":
        """Sets the operation for the message."""
        self._operation = operation
        return self

    def set_args(self, args: List[Any]) -> "SimulationMessageBuilder":
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

