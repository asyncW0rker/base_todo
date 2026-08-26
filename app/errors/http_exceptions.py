from functools import partial

from fastapi import HTTPException, status


HTTPBadRequest = partial(HTTPException, status_code=status.HTTP_400_BAD_REQUEST)
HTTPInvalidTimezoneException = HTTPBadRequest(detail="Invalid timezone")
HTTPValueError = HTTPBadRequest(detail="Invalid value")
HTTPNoFileProvidedException = HTTPBadRequest(detail="No file provided")


HTTPNotAuthException = partial(HTTPException, status_code=status.HTTP_401_UNAUTHORIZED)
HTTPExpiredTokenException = HTTPNotAuthException(detail="Expired token")
HTTPInvalidTokenException = HTTPNotAuthException(detail="Invalid token")
HTTPWrongCredentialsException = HTTPNotAuthException(detail="Wrong credentials")


HTTPForbiddenException = partial(HTTPException, status_code=status.HTTP_403_FORBIDDEN)
HTTPRolePermissionDeniedException = HTTPForbiddenException(detail="Permission denied")
HTTPPrivatePermissionDeniedException = HTTPForbiddenException(detail="Permission denied")


HTTPNotFoundException = partial(HTTPException, status_code=status.HTTP_404_NOT_FOUND)
HTTPUserNotFoundException = HTTPNotFoundException(detail="User not found")
HTTPToDoNotFoundException = HTTPNotFoundException(detail="ToDo not found")
HTTPTokenNotFoundException = HTTPNotFoundException(detail="Token not found")
HTTPAnalyticsJobNotFoundException = HTTPNotFoundException(detail="Analytics job not found")
HTTPAttachmentNotFoundException = HTTPNotFoundException(detail="Attachment not found")
HTTPImportJobNotFoundException = HTTPNotFoundException(detail="Import job not found")


HTTPConflictException = partial(HTTPException, status_code=status.HTTP_409_CONFLICT)
HTTPUserAlreadyExistsException = HTTPConflictException(detail="User already exists")
HTTPToDoAlreadyExistsException = HTTPConflictException(detail="ToDo already exists")
HTTPToDoVersionMismatchException = HTTPConflictException


HTTPTooLargeException = partial(HTTPException, status_code=status.HTTP_413_CONTENT_TOO_LARGE)
HTTPAttachmentTooLargeException = HTTPTooLargeException(detail="Payload too large")


HTTPUnsupportedMedia = partial(HTTPException, status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
HTTPAttachmentUnsupportedMedia = HTTPUnsupportedMedia(detail="Unsupported file type")
HTTPFileFormatException = HTTPUnsupportedMedia(detail="Unsupported file format")
