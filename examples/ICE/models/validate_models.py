from machine_data_model.builder.data_model_builder import DataModelBuilder
from machine_data_model.nodes.folder_node import FolderNode
from machine_data_model.nodes.variable_node import *
from machine_data_model.nodes.method_node import *
import os
import yaml

def validate_yaml(file_path):
    try:
        with open(file_path, 'r') as file:            
            model = DataModelBuilder().get_data_model(file_path)
            print(f"Successfully validated: {file_path}")
            return model
    except Exception as e:
        print(f"Failed to validate {file_path}: {e}")
        return None

def main():
    directory = os.path.dirname(os.path.abspath(__file__))
    for filename in os.listdir(directory):
        if filename.endswith(".yml"):
            file_path = os.path.join(directory, filename)
            validate_yaml(file_path)

if __name__ == "__main__":
    main()