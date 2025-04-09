#!/usr/bin/env python3

import inspect
import pkgutil
import sys

def print_classes(package):
    """Prints all classes in the given package."""
    print(f"Inspecting package: {package.__name__}")
    
    for _, module_name, is_pkg in pkgutil.walk_packages(package.__path__, package.__name__ + "."):
        try:
            module = __import__(module_name, fromlist=[""])
        except ImportError as e:
            print(f"Could not import {module_name}: {e}")
            continue
        
        for name, obj in inspect.getmembers(module, inspect.isclass):
            if obj.__module__ == module_name:
                print(f"Found class: {name} in {module_name}")

if __name__ == "__main__":
    # You can replace this with your library's import
    import machine_data_model  # Replace with the name of your library
    
    print_classes(machine_data_model)
