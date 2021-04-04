from rest_framework.exceptions import ValidationError, NotAuthenticated, MethodNotAllowed
from rest_framework.views import exception_handler

from core.utils.response_formatter import ResponseFormatterUtil


class ApiError(Exception):
    def __init__(self, message, response_status_code=400):
        self.message = message
        self.response_status_code = response_status_code
        super().__init__(message)


def custom_exception_handler(exc, context):
    # response = exception_handler(exc, context)

    if isinstance(exc, ApiError):
        return ResponseFormatterUtil.error(str(exc.message), exc.response_status_code)

    if isinstance(exc, ValidationError):
        return ResponseFormatterUtil.form_validation_error(exc.detail)

    if isinstance(exc, NotAuthenticated):
        return ResponseFormatterUtil.error('', 403)

    if isinstance(exc, MethodNotAllowed):
        return ResponseFormatterUtil.error('', 405)

    return ResponseFormatterUtil.error("unknown failure")


