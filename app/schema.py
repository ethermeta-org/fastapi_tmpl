from http import HTTPStatus

from pydantic import BaseModel, field_validator


class AnyLinkerErrorResponse(BaseModel):
    code: int = HTTPStatus.BAD_REQUEST.value
    message: str = ""
    target: str = ""


class AnyLinkerErrorWebResponse(BaseModel):
    error: AnyLinkerErrorResponse

