from typing import Any
from fastapi import status


class AppException(Exception):
    """
    Lớp cơ sở cho toàn bộ exception tùy chỉnh của ứng dụng.
    """
    def __init__(
        self,
        message: str = "Đã xảy ra lỗi hệ thống",
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str | None = None,
        detail: Any | None = None,
        headers: dict[str, str] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.headers = headers

        # Độ ưu tiên gán detail:
        # 1. detail được truyền trực tiếp
        # 2. Dict cấu trúc {"message": message, "type": error_code} nếu có error_code
        # 3. Chuỗi message thuần túy
        if detail is not None:
            self.detail = detail
        elif error_code is not None:
            self.detail = {
                "message": message,
                "type": error_code
            }
        else:
            self.detail = message


# ==============================================================================
# Các HTTP Exception chuẩn (4xx, 5xx)
# ==============================================================================

class BadRequestException(AppException):
    def __init__(
        self,
        message: str = "Yêu cầu không hợp lệ",
        error_code: str | None = None,
        detail: Any | None = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code=error_code,
            detail=detail
        )


class UnauthorizedException(AppException):
    def __init__(
        self,
        message: str = "Chưa xác thực",
        error_code: str | None = None,
        detail: Any | None = None,
        headers: dict[str, str] | None = None
    ):
        auth_headers = {"WWW-Authenticate": "Bearer"}
        if headers:
            auth_headers.update(headers)
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=error_code,
            detail=detail,
            headers=auth_headers
        )


class ForbiddenException(AppException):
    def __init__(
        self,
        message: str = "Bạn không có quyền thực hiện hành động này",
        error_code: str | None = None,
        detail: Any | None = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code=error_code,
            detail=detail
        )


class NotFoundException(AppException):
    def __init__(
        self,
        message: str = "Không tìm thấy tài nguyên",
        error_code: str | None = None,
        detail: Any | None = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code=error_code,
            detail=detail
        )


class ConflictException(AppException):
    def __init__(
        self,
        message: str = "Dữ liệu đã tồn tại hoặc xảy ra xung đột",
        error_code: str | None = None,
        detail: Any | None = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            error_code=error_code,
            detail=detail
        )


class InternalServerErrorException(AppException):
    def __init__(
        self,
        message: str = "Đã xảy ra lỗi hệ thống. Vui lòng thử lại sau.",
        error_code: str | None = None,
        detail: Any | None = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=error_code,
            detail=detail
        )


# ==============================================================================
# Domain / Business Exceptions cụ thể
# ==============================================================================

class InvalidCredentialsException(UnauthorizedException):
    def __init__(self, message: str = "Sai username hoặc password"):
        super().__init__(message=message, error_code="invalid_credentials")


class InvalidTokenException(UnauthorizedException):
    def __init__(self, message: str = "Access token không hợp lệ"):
        super().__init__(message=message, error_code="invalid_access_token")


class ExpiredTokenException(UnauthorizedException):
    def __init__(self, message: str = "Access token đã hết hạn"):
        super().__init__(message=message, error_code="expired_access_token")


class InvalidRefreshTokenException(UnauthorizedException):
    def __init__(self, message: str = "Refresh token không hợp lệ"):
        super().__init__(message=message, error_code="invalid_refresh_token")


class ExpiredRefreshTokenException(UnauthorizedException):
    def __init__(self, message: str = "Refresh token đã hết hạn"):
        super().__init__(message=message, error_code="expired_refresh_token")


class UserNotFoundException(NotFoundException):
    def __init__(self, message: str = "Không tìm thấy user"):
        super().__init__(message=message, error_code="user_not_found")


class CourseNotFoundException(NotFoundException):
    def __init__(self, message: str = "Không tìm thấy khóa học"):
        super().__init__(message=message)
