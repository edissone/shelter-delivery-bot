from typing import List, Type

from src.models import ErrorResponse


class ServiceException(RuntimeError):
    error_code = 0

    def __init__(self, error: ErrorResponse):
        self.code = error.code
        self.timestamp = error.timestamp
        self.error = error.error
        self.error_message = error.message
        self.path = error.path

    @classmethod
    def raise_exception(cls, error: ErrorResponse):
        subclasses: List[Type[ServiceException]] = cls.__subclasses__()
        for exception in subclasses:
            if exception.error_code == error.code:
                raise exception(error)


class NotFoundException(ServiceException):
    error_code = 4000

    def __init__(self, error: ErrorResponse):
        super().__init__(error)


class InvalidStateException(ServiceException):
    error_code = 4010

    def __init__(self, error: ErrorResponse):
        super().__init__(error)


class ActiveOrdersExistException(ServiceException):
    error_code = 4020

    def __init__(self, error: ErrorResponse):
        super().__init__(error)


class PermissionDeniedException(ServiceException):
    error_code = 4030

    def __init__(self, error: ErrorResponse):
        super().__init__(error)


class UnassignedOrderProcessingException(ServiceException):
    error_code = 4040

    def __init__(self, error: ErrorResponse):
        super().__init__(error)


class AlreadyExists(ServiceException):
    error_code = 4050

    def __init__(self, error: ErrorResponse):
        super().__init__(error)


class InvalidComputationException(ServiceException):
    error_code = 5000

    def __init__(self, error: ErrorResponse):
        super().__init__(error)
