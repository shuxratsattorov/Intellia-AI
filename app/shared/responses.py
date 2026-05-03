from fastapi import status

from app.core.error.error_code import ErrorCode, ErrorModel



def responses(errors: list[str]) -> dict:
        responses = {}

        if ErrorCode.REGISTER_USER_ALREADY_EXISTS in errors:
            responses[status.HTTP_400_BAD_REQUEST] = {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.REGISTER_USER_ALREADY_EXISTS: {
                                "summary": "User already exists",
                                "value": {
                                    "detail": ErrorCode.REGISTER_USER_ALREADY_EXISTS
                                },
                            }
                        }
                    }
                },
            }

        if ErrorCode.DEFAULT_ROLE_NOT_CONFIGURED in errors:
            responses[status.HTTP_500_INTERNAL_SERVER_ERROR] = {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.DEFAULT_ROLE_NOT_CONFIGURED: {
                                "summary": "Default role not configured",
                                "value": {
                                    "detail": ErrorCode.DEFAULT_ROLE_NOT_CONFIGURED
                                },
                            }
                        }
                    }
                },
            }

        return responses