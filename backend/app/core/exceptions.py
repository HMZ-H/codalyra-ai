class CodalyraException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class NotFoundException(CodalyraException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail)


class UnauthorizedException(CodalyraException):
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(status_code=401, detail=detail)


class ForbiddenException(CodalyraException):
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(status_code=403, detail=detail)


class ConflictException(CodalyraException):
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=409, detail=detail)


class BadRequestException(CodalyraException):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=400, detail=detail)
