class AppException(Exception):
    status_code: int = 500
    detail: str = "Internal server error"

    def __init__(self, detail: str | None = None):
        if detail:
            self.detail = detail
        super().__init__(self.detail)


class NotFoundError(AppException):
    status_code = 404
    detail = "Resource not found"


class BadRequestError(AppException):
    status_code = 400
    detail = "Bad request"


class ConflictError(AppException):
    status_code = 409
    detail = "Resource conflict"
