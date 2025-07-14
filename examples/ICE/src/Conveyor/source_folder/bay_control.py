def Bay_Control(buff, val):
    for i in range(val, 1, -1):
        if not buff[i-1]:
            return False
    return True

def Update_Truth_Table(buff, val):
    for i in range(val-1, 3, 1):
        buff[i] = False
    return buff