from fastapi import HTTPException, Header, status

from internal.settings import settings


def check_api_key(x_api_key: str | None = Header(default=None, alias='X-API-Key')) -> None:
    if x_api_key is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='X-API-Key header required')
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid X-API-Key header')

    return None
