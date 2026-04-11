

class VisuLanguageError(Exception):
    pass


class LexError(VisuLanguageError):
    pass


class ParseError(VisuLanguageError):
    pass


class VisuRuntimeError(VisuLanguageError):
    def __init__(self, line: int, message: str):
        super().__init__(f"Line {line}: {message}")
        self.line = line
        self.message = message
