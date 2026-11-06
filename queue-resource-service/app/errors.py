"""RFC 7807 Problem Details with an extra error code (report section 6.1)."""
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.logging_setup import correlation_id_var

log = logging.getLogger(__name__)


class ProblemError(Exception):
    def __init__(self, status: int, code: str, title: str, detail: str | None = None):
        super().__init__(detail or title)
        self.status, self.code, self.title, self.detail = status, code, title, detail


def problem_response(request: Request, status: int, code: str, title: str, detail: str | None = None) -> JSONResponse:
    cid = getattr(request.state, "correlation_id", None) or correlation_id_var.get()
    body = {
        "type": f"https://clinilink.com/errors/{code.lower().replace('_', '-')}",
        "title": title,
        "status": status,
        "code": code,
        "detail": detail,
        "instance": request.url.path,
        "correlation_id": cid,
    }
    return JSONResponse(body, status_code=status, media_type="application/problem+json",
                        headers={"X-Correlation-ID": cid})


_HTTP_CODES = {401: "UNAUTHORIZED", 403: "FORBIDDEN", 404: "NOT_FOUND", 405: "METHOD_NOT_ALLOWED"}


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ProblemError)
    async def _problem(request: Request, exc: ProblemError):
        return problem_response(request, exc.status, exc.code, exc.title, exc.detail)

    @app.exception_handler(RequestValidationError)
    async def _validation(request: Request, exc: RequestValidationError):
        detail = "; ".join(f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}" for e in exc.errors())
        return problem_response(request, 400, "VALIDATION_FAILED", "Validation Failed", detail)

    @app.exception_handler(StarletteHTTPException)
    async def _http(request: Request, exc: StarletteHTTPException):
        code = _HTTP_CODES.get(exc.status_code, "HTTP_ERROR")
        return problem_response(request, exc.status_code, code, code.replace("_", " ").title(), str(exc.detail))

    @app.exception_handler(Exception)
    async def _unexpected(request: Request, exc: Exception):
        log.exception("Unhandled error")
        return problem_response(request, 500, "INTERNAL_ERROR", "Internal Server Error", "An unexpected error occurred.")
