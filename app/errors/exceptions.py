from functools import partial

from fastapi import HTTPException, status


class TimezoneException(ValueError):
    pass


HTTPInvalidTimezoneException = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid timezone")


HTTPNotFoundException = partial(HTTPException, status_code=status.HTTP_404_NOT_FOUND)
HTTPUserNotFoundException = HTTPNotFoundException(detail="User not found")
HTTPToDoNotFoundException = HTTPNotFoundException(detail="ToDo not found")

HTTPAlreadyExistsException = partial(HTTPException, status_code=status.HTTP_409_CONFLICT)
HTTPUserAlreadyExistsException = HTTPAlreadyExistsException(detail="User already exists")
HTTPToDoAlreadyExistsException = HTTPAlreadyExistsException(detail="ToDo already exists")
