class TimezoneException(ValueError):
    pass


class JWTException(ValueError):
    pass


class JWTExpiredTokenException(JWTException):
    pass


class JWTInvalidTokenException(JWTException):
    pass


class TooLargeException(ValueError):
    pass


class FileNotFoundException(ValueError):
    pass


class FileFormatException(ValueError):
    pass
