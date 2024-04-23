from http.client import BAD_REQUEST
from typing import Annotated, Any, Optional, Dict

from fastapi import HTTPException
from typing_extensions import Doc


class AnyLinkerException(HTTPException):
    def __init__(
            self,
            status_code: Annotated[
                int,
                Doc(
                    """
                    HTTP status code to send to the client.
                    """
                ),
            ] = BAD_REQUEST.value,
            detail: Annotated[
                Any,
                Doc(
                    """
                    Any data to be sent to the client in the `detail` key of the JSON
                    response.
                    """
                ),
            ] = None,
            headers: Annotated[
                Optional[Dict[str, str]],
                Doc(
                    """
                    Any headers to send to the client in the response.
                    """
                ),
            ] = None,
    ) -> None:
        if not detail:
            detail = ''
        super(AnyLinkerException, self).__init__(status_code=status_code, detail=detail, headers=headers)

    def __str__(self):
        return self.detail
