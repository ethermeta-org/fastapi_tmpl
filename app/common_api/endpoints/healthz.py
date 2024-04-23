from http import HTTPStatus
from typing import Union

from fastapi import APIRouter, Header, Response

router = APIRouter()


@router.get("/healthz")
async def healthCheck(
    x_org_name: Union[str, None] = Header(default=None, example="anylinker")
):
    return Response(status_code=HTTPStatus.NO_CONTENT)


@router.get("/readiness")
async def readiness(
    x_org_name: Union[str, None] = Header(default=None, example="anylinker")
):
    return Response(status_code=HTTPStatus.NO_CONTENT)