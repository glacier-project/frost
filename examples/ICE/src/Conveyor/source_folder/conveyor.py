from enum import Enum
class PalletAction(Enum):
    OUT = 1
    CROSS = 2
    BAY = 3
    LOOP = 4

class Action(Enum):
    MOVE = 1
    CREATE = 2
    RELEASE = 3
    GIVE = 4

