from functools import partial

from fastapi import HTTPException, status


class TimezoneException(ValueError):
    pass


class JWTException(ValueError):
    pass


class JWTExpiredTokenException(JWTException):
    pass


class JWTInvalidTokenException(JWTException):
    pass


HTTPBadRequest = partial(HTTPException, status_code=status.HTTP_400_BAD_REQUEST)
HTTPInvalidTimezoneException = HTTPBadRequest(detail="Invalid timezone")
HTTPValueError = HTTPBadRequest(detail="Invalid value")


HTTPNotAuthException = partial(HTTPException, status_code=status.HTTP_401_UNAUTHORIZED)
HTTPExpiredTokenException = HTTPNotAuthException(detail="Expired token")
HTTPInvalidTokenException = HTTPNotAuthException(detail="Invalid token")


HTTPNotFoundException = partial(HTTPException, status_code=status.HTTP_404_NOT_FOUND)
HTTPUserNotFoundException = HTTPNotFoundException(detail="User not found")
HTTPToDoNotFoundException = HTTPNotFoundException(detail="ToDo not found")


HTTPAlreadyExistsException = partial(HTTPException, status_code=status.HTTP_409_CONFLICT)
HTTPUserAlreadyExistsException = HTTPAlreadyExistsException(detail="User already exists")
HTTPToDoAlreadyExistsException = HTTPAlreadyExistsException(detail="ToDo already exists")
