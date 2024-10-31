from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.log_config import get_logger
from fastapi import HTTPException as FastAPIHTTPException

# 커스텀 예외 클래스들
class CustomHTTPException(Exception):
    def __init__(self, status_code: int, detail: str, error_code: str = None):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code

class InvalidEnumValueError(CustomHTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail, error_code="INVALID_ENUM_VALUE")

class NotFoundError(CustomHTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=404, detail=detail, error_code="NOT_FOUND")

class BadRequestError(CustomHTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=400, detail=detail, error_code="BAD_REQUEST")

class UnauthorizedError(CustomHTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=401, detail=detail, error_code="UNAUTHORIZED")

class ForbiddenError(CustomHTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=403, detail=detail, error_code="FORBIDDEN")

class BranchNotFoundException(Exception):
    def __init__(self, branch_id: int):
        self.branch_id = branch_id
        self.message = f'Branch not found with id: {branch_id}'
        super().__init__(self.message)

def add_exception_handlers(app: FastAPI):
    @app.exception_handler(CustomHTTPException)
    async def custom_exception_handler(request: Request, exc: CustomHTTPException):
        logger = await get_logger()
        await logger.error(f"Custom HTTP error: {exc.status_code} - {exc.detail}", exc_info=True)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.error_code,
                    "message": exc.detail
                }
            }
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
        logger = await get_logger()
        await logger.error(f"Database error occurred: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"message": "An internal server error occurred"},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger = await get_logger()
        await logger.error(f"Validation error: {exc.errors()}", exc_info=True)
        return JSONResponse(
            status_code=422,
            content={"message": exc.errors()},
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger = await get_logger()

        await logger.error(f"HTTP error {exc.status_code}: {exc.detail}", exc_info=True)
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger = await get_logger()
        await logger.error(f"An unexpected error occurred: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"message": "An unexpected error occurred"},
        )