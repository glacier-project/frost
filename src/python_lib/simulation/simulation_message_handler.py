from typing import Callable, Any
from simulation_message import SimulationMessage, ParticipantFailure
from operation import Operation

class SimulationMessageHandler:
    """Dispatch simulation messages to registered handlers."""

    def __init__(self, name: str):
        """
        Initialize a dispatcher with no handlers for the named participant.

        Args:
            name (str): Participant name that incoming messages must target.
        """
        self._name: str = name
        self._handlers: dict[Operation, Callable[[Any], Any]] = {}

    def register_handler(self, operation: Operation, handler: Callable[[Any], Any]) -> bool:
        """
        Register an operation handler.

        Args:
            operation (Operation): Operation to handle.
            handler (Callable): Receives the sender for REGISTER, otherwise the argument list.
        """
        self._handlers[operation] = handler
        return True

    def handle_message(self, message: SimulationMessage) -> SimulationMessage:
        """
        Dispatch a request to its handler and build the response; unsupported operations return ERROR.

        Handler exceptions propagate to the reactor for logging and error reporting.

        Args:
            message (SimulationMessage): Request addressed to this participant.
        """
        assert message.target == self._name

        handler = self._handlers.get(message.operation)
        if handler is None:
            return self.error_response(
                message,
                f"{self._name} has no handler for operation {message.operation.value!r}",
            )

        if message.operation == Operation.REGISTER:
            handler(message.sender)
            result = f"{message.sender} registered"
        else:
            result = handler(message.payload if message.payload is not None else message.args)

        if message.payload is not None:
            return message.reply(result)
        return message.reply(args=[result])

    def error_response(self, message: SimulationMessage, reason: str) -> SimulationMessage:
        """
        Build an ERROR response addressed to the request sender, so every request gets an answer.

        Args:
            message (SimulationMessage): Request that failed.
            reason (str): Failure description sent as ParticipantFailure and legacy arg.
        """
        return message.reply(ParticipantFailure("operation_failed", reason),
                             operation=Operation.ERROR, args=[reason])

    def __call__(self, message: SimulationMessage) -> SimulationMessage:
        """
        Dispatch a simulation message, making the handler usable as a callable.

        Args:
            message (SimulationMessage): Request addressed to this participant.
        """
        return self.handle_message(message)
