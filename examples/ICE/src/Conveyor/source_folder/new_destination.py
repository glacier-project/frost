def New_Destination(pos, dest, lp):
    if dest == "Z":
        return [False, True, dest]
    if lp == 1: 
        if dest == "G":
            return [False, False, dest]
        elif dest == None:
            return [True, False, None]
        else:
            return [False, True, dest]
    elif lp == 2:
        if dest == "G":
            return [False, False, dest]           
        elif dest == None:
            return [True, False, None]
        else:            
            return [False, True, dest]