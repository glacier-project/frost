from traitlets import Dict
from typing import Callable, Any, Optional, List
from simulation_message import SimulationMessage, SimulationMessageBuilder
from operation import Operation

class SimulationMessageHandler:
    """
    Handles SimulationMessage objects by dispatching them to registered callables
    based on the message's operation.
    """

    def __init__(self, name: str):
        """
        Initializes the SimulationMessageHandler.
        """
        self._name: str = name
        self._handlers: Dict[Operation, Callable[[List[Any]], Any]] = {}

    def register_handler(self, operation: Operation, handler: Callable[[SimulationMessage], Any]) -> bool:
        """
        Registers a callable function to handle a specific operation.

        Args:
            operation (Operation): The operation to associate with the handler.
            handler (Callable[[SimulationMessage], Any]): The function to be called
                when a message with the specified operation is received. It must
                accept a SimulationMessage object as its sole argument.
        """
        self._handlers[operation] = handler
        return True

    def handle_message(self, message: SimulationMessage) -> Optional[SimulationMessage]:
        """
        Processes an incoming SimulationMessage, calls the appropriate handler,
        and prepares a response message with the result.

        If a handler is registered for the message's operation, it is called with
        the message as an argument. The return value from the handler is then
        used as the payload for a new response SimulationMessage.

        Args:
            message (SimulationMessage): The message to be processed.

        Returns:
            Optional[SimulationMessage]: A new SimulationMessage containing the result
            from the handler, or None if no handler is found.
        """
        assert message.target == self._name

        handler = self._handlers.get(message.operation)
        if handler:
            
            if message.operation == Operation.get_enum().REGISTER:
                handler(message.sender)
                return f"{message.sender} registered"
            result = handler(message.args)
            # Prepare the answer message with the result
            response_builder = SimulationMessageBuilder()
            response_message = (
                response_builder.set_sender(self._name).set_target(message.sender)
                .set_operation(Operation.get_enum().RESPONSE)
                .set_args([result])
                .build()
            )
            return response_message
        return None

    def __call__(self, message: SimulationMessage) -> Optional[SimulationMessage]:
        """
        Allows the handler instance to be called directly, which in turn calls
        the handle_message method.

        Args:
            message (SimulationMessage): The message to be processed.

        Returns:
            Optional[SimulationMessage]: The response message or None.
        """
        return self.handle_message(message)
    