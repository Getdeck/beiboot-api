class BeibootException(Exception):
    def __init__(self, message: str, error: str):
        self.message = message
        self.error = error
