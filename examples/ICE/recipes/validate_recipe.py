from handle_recipe import get_messages, get_conditions
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validate_recipe.py <path_to_yaml>")
        sys.exit(1)

    path_to_recipe = sys.argv[1]
    messages = get_messages(path_to_recipe)
    path_to_condition = sys.argv[2]
    conditions = get_conditions(path_to_condition)