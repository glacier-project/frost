def get_coordinates(value):
    matrix = [
        ['M', 'L', 'I', 'H', 'G','F'],
        ['E', 'D', 'C', 'B', 'Z','A']
    ]
    for i, row in enumerate(matrix):
        for j, element in enumerate(row):
            if element == value:
                return (i, j)
    return None

def get_BAY_coordinates(value):
    if value == "Z1":
        return "M"
        
    matrix = [
        ['P1', 'P2', 'P3'],
        ['O1', 'O2', 'O3'],
        ['N1', 'N2', 'N3']
    ]
    
    for i, row in enumerate(matrix):
        for j, element in enumerate(row):
            if element == value:
                if i == 0:
                    return "L"
                if i == 1:
                    return "I"
                if i == 2:
                    return "H"
    return None

def calculate_next_position(current_position, destination):
    
    pos = get_coordinates(current_position)
    dest = get_coordinates(destination)
    
    if pos is None:
        pos = get_coordinates(get_BAY_coordinates(current_position))
        
    if dest is None:
        dest = get_coordinates(get_BAY_coordinates(destination))

    if pos == dest:
        return "BAY"
    
    if pos[0] == 0 and dest[0] == 0:
        if pos[1] < dest[1]:
            return "OUT"        
        else :
            return "CROSS"
            
    elif pos[0] == 1 and dest[0] == 1:
        if pos[1] < dest[1]:
            return "CROSS"
        else :
            return "OUT"
        
    elif pos[0] == 0 and dest[0] == 1:
        if current_position == "M":
            return "OUT"
        elif pos[1] < dest[1]:
            return "OUT"
        else:
            return "CROSS"
                
    elif pos[0] == 1 and dest[0] == 0:
        if current_position == "A" or current_position == "E":
            return "OUT"
        elif pos[1] <= dest[1]:
            return "CROSS"
        else :
            return "OUT"

def Routing(position, destination):
    if position == "L" and destination[0] == "P":
        return "BAY"
    elif position == "I" and destination[0] == "O":
        return "BAY"
    elif position == "H" and destination[0] == "N":
        return "BAY" 
    elif position == "M" and destination[0] == "Z":
        return "BAY"
    else:
        return calculate_next_position(position, destination)