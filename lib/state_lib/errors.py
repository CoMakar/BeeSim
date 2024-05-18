class STLError(Exception):
    ...


class EventAlreadyExists(STLError):
    ...


class EventNotFound(STLError):
    ...
    
    
class IncorrectState(STLError):
    ...
