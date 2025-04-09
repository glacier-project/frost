from machine_data_model.builder.data_model_builder import DataModelBuilder
from machine_data_model.protocols.glacier_v1.glacier_protocol_mng import GlacierProtocolMng
from handle_recipe import get_messages
from machine_data_model.nodes.variable_node import VariableNode
path = "PingPong/models/PingPong.yml"
model = None
try:
    with open(path, 'r') as file:            
        model = DataModelBuilder().get_data_model(path)
        print(f"Successfully validated")
except Exception as e:
    print(f"Failed to validate {path}: {e}")
 
prot = GlacierProtocolMng(model)
mex = get_messages("PingPong/recipes/recipes/test.yaml")
pingsLeft:VariableNode = model.get_node("PingPong/pingsLeft")
pingsLeft.update(1)
print(pingsLeft.read())
print(prot.handle_message(mex[0]))
pingsLeft.update(10)
pingsLeft.update(0)
print(pingsLeft.read())