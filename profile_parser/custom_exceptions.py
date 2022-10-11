class InvalidCredentials(Exception):
    def __init__(self, message="Provide a valid not null credentials"):
        self.message = message
        super().__init__(self.message)
