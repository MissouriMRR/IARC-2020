from enum import Enum

class ObjectType(Enum):
    AVOID = 'avoid'
    PYLON = 'pylon'
    MODULE = 'module'
    BOAT = 'boat'
    UNKNOWN = 'unknown'

MIN_THRESHOLD = 100
MAX_THRESHOLD = 500

MIN_AREA = 100
MAX_AREA = 2000000

MIN_CIRCULARITY = 0.785
MAX_CIRCULARITY = 0.95

