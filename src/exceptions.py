class InvalidIPError(Exception):
    def __init__(self, message=""):
        self.message = message
        super().__init__("Error running server configurations: Invalid IP address")


class ArgumentsMissingError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__("Arguments missing")


class TooManyArgumentsError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__("Too many arguments")


class InvalidValueTTL(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__("Invalid value for TTL")


class InvalidValuePriority(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__("Invalid value for priority")

class InvalidType(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__("Invalid entry type")

class NameNotFoundError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__("Name not found")