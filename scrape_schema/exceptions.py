class BaseSchemaException(Exception):
    ...


class ValidationError(BaseSchemaException):
    ...


class ParseFailAttemptsError(BaseSchemaException):
    ...
