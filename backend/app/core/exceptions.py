
# from fastapi import HTTPException, status

# class AppException(Exception):
#     """
#     Base application exception.
#     """

#     def __init__(
#         self,
#         message: str,
#         status_code: int = 400,
#     ):
#         self.message = message
#         self.status_code = status_code
#         super().__init__(message)


# class BadRequestException(AppException):
#     def __init__(self, message: str = "Bad request"):
#         super().__init__(
#             message=message,
#             status_code=400,
#         )


# class UnauthorizedException(AppException):
#     def __init__(self, message: str = "Authentication required"):
#         super().__init__(
#             message=message,
#             status_code=401,
#         )


# class ForbiddenException(AppException):
#     def __init__(self, message: str = "You do not have permission to perform this action"):
#         super().__init__(
#             message=message,
#             status_code=403,
#         )


# class NotFoundException(AppException):
#     def __init__(self, message: str = "Resource not found"):
#         super().__init__(
#             message=message,
#             status_code=404,
#         )


# class ConflictException(AppException):
#     def __init__(self, message: str = "Resource conflict"):
#         super().__init__(
#             message=message,
#             status_code=409,
#         )
        
        
from typing import Any, Optional


class AppException(Exception):
    """
    Base application exception.

    Use this for expected business/application errors.
    """

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Optional[Any] = None,
    ):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details

        super().__init__(message)


class BadRequestException(AppException):
    def __init__(
        self,
        code: str = "BAD_REQUEST",
        message: str = "Bad request",
        details: Optional[Any] = None,
    ):
        super().__init__(
            status_code=400,
            code=code,
            message=message,
            details=details,
        )


class UnauthorizedException(AppException):
    def __init__(
        self,
        code: str = "UNAUTHORIZED",
        message: str = "Authentication required",
        details: Optional[Any] = None,
    ):
        super().__init__(
            status_code=401,
            code=code,
            message=message,
            details=details,
        )


class ForbiddenException(AppException):
    def __init__(
        self,
        code: str = "FORBIDDEN",
        message: str = "You do not have permission to perform this action",
        details: Optional[Any] = None,
    ):
        super().__init__(
            status_code=403,
            code=code,
            message=message,
            details=details,
        )


class NotFoundException(AppException):
    def __init__(
        self,
        code: str = "NOT_FOUND",
        message: str = "Resource not found",
        details: Optional[Any] = None,
    ):
        super().__init__(
            status_code=404,
            code=code,
            message=message,
            details=details,
        )


class ConflictException(AppException):
    def __init__(
        self,
        code: str = "CONFLICT",
        message: str = "Resource conflict",
        details: Optional[Any] = None,
    ):
        super().__init__(
            status_code=409,
            code=code,
            message=message,
            details=details,
        )
        
        
    