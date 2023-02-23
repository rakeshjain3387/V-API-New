class HandledExceptions(Exception):
    """Base class for other exceptions"""
    pass


class InvalidRequest(HandledExceptions):
    """Raised when No file is uploaded"""
    def __init__(self,error) -> None:
        self.message="Invalid Request"
        self.error=error
        self.response_code=111
        super().__init__(self.message)

class MultipleRto(HandledExceptions):
    """Raised when No file is uploaded"""
    def __init__(self,error) -> None:
        self.message="Multiple RTO Found"
        self.error=error
        self.response_code=103
        super().__init__(self.message)

class InvalidRegistrationNumber(HandledExceptions):
    """Raised when No file is uploaded"""
    def __init__(self,error) -> None:
        self.message="Invalid Registration Number"
        self.error=error
        self.response_code=106
        super().__init__(self.message)

class SourceError(HandledExceptions):
    """Raised when No file is uploaded"""
    def __init__(self,error) -> None:
        self.message="Source Error"
        self.error=error
        self.response_code=110
        super().__init__(self.message)