class AttemptFails(Exception):
    """
    This is an exception which is thrown when there were too many attempts to grab an element.
    """
    def __init__(self, message:str, attempts:int, failed_rows=None):
        super().__init__(message)
        self.attempts = attempts

class NullIndex(Exception):
    """
    This element is for index's in the list which no longer exist.
    """
    def __init__(self, message:str, index:int, failed_rows=None):
        super().__init__(message)
        self.nulledIndex = index