from pallet import Pallet 
def PriorityAlgorithm(buffer):
    temp = buffer["BAY"]
    str = "BAY"
    if temp is None:
        temp = buffer["IN_UP"]
        temp2 = buffer["IN_DOWN"]
        if not temp and not temp2:
            return None
        elif not temp:
            return "IN_DOWN"
        elif not temp2:
            return "IN_UP"
        else:
            if temp[0].action == "OUT" and temp2[0].action == "OUT":
                return "BOTH"
            elif temp[0].action == "OUT":
                return "IN_UP"
            elif temp2[0].action == "OUT":
                return "IN_DOWN"
            elif temp[0].action == "BAY":
                return "IN_UP"
            elif temp2[0].action == "CROSS" and temp2[0].bay == False:
                return "IN_DOWN"
            elif temp[0].action == "CROSS" and temp[0].bay == False:
                return "IN_UP"
            else:
                return "IN_DOWN"            
    else:
        return str