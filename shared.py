from enum import Enum

class MoveResponse(Enum):
    INVALID = 0
    VALID = 1
    WIN = 2
    DRAW = 3
    LOSE = 4
