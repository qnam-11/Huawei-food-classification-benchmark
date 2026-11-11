class AppError(Exception):
    status_code = 500
    code = "inference_failed"

    def __init__(self, detail: str | None = None):
        super().__init__(detail or self.code)
        self.detail = detail


class InvalidImageError(AppError):
    status_code = 400
    code = "invalid_image"


class FileTooLargeError(AppError):
    status_code = 413
    code = "file_too_large"


class UnsupportedTypeError(AppError):
    status_code = 415
    code = "unsupported_type"


class UnknownModelError(AppError):
    status_code = 422
    code = "unknown_model"


class InferenceFailedError(AppError):
    status_code = 500
    code = "inference_failed"
