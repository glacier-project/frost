import yaml
import uuid
import sys
from machine_data_model.protocols.glacier_v1.glacier_message import GlacierMessage
from machine_data_model.protocols.glacier_v1.glacier_header import *
from machine_data_model.protocols.glacier_v1.glacier_payload import VariablePayload, MethodPayload

def get_conditions(path: str)->list:
    '''
    This function reads a YAML file and returns a list of dictionaries containing the conditions
    specified in the YAML file.
    Args:
        path (str): The path to the YAML file
    Returns:
        list: A list of dictionaries containing the conditions specified in the YAML file
    '''
    
    list_of_conditions = []
    with open(path, 'r') as file:
        recipe = yaml.safe_load(file)
        if not isinstance(recipe, list) or not all(isinstance(item, dict) for item in recipe):
            raise ValueError("YAML file must contain a list of dictionaries")
        for item in recipe:
            condition = {
            "node": item["node"],
            "value": item["value"]
            }
            list_of_conditions.append(condition)
        return list_of_conditions

def get_messages(path: str) -> list:
    '''
    This function reads a YAML file and returns a list of GlacierMessage objects
    Args:
        path (str): The path to the YAML file
    Returns:
        list: A list of GlacierMessage messages
    '''
    list_of_messages = []
    with open(path, 'r') as file:
        recipe = yaml.safe_load(file)
        if not isinstance(recipe, list) or not all(isinstance(item, dict) for item in recipe):
            raise ValueError("YAML file must contain a list of dictionaries")
        for item in recipe:
            sender = item["sender"]
            target = item["target"]
            identifier = uuid.uuid4()
            header = GlacierHeader(
                type=MsgType[item["header"]["type"]],
                version=tuple(item["header"]["version"]),
                namespace=MsgNamespace[item["header"]["namespace"]],
                msg_name=(
                    VariableMsgName[item["header"]["msg_name"]]
                    if item["header"]["namespace"] == "VARIABLE"
                    else MethodMsgName[item["header"]["msg_name"]]
                    if item["header"]["namespace"] == "METHOD"
                    else None
                )
            )
            payload=None
            if header.namespace is None:
                raise ValueError(f"Unsupported namespace: {item['header']['namespace']}")
            if "payload" in item:
                if header.namespace == MsgNamespace.VARIABLE:
                    payload = VariablePayload(
                        node=item["payload"]["node"],
                        value=item["payload"]["value"]
                    )
                elif header.namespace == MsgNamespace.METHOD:
                    payload = MethodPayload(
                        node=item["payload"]["node"],
                        args=item["payload"]["args"]
                    )
            else:
                payload = None
            message = GlacierMessage(
                sender=sender,
                target=target,
                identifier=identifier,
                header=header,
                payload=payload
            )
            list_of_messages.append(message)

    return list_of_messages