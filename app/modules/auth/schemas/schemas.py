from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class RegisterRequest(BaseModel):
    email: EmailStr = Field(example="intellia2026@gmail.com")
    password: str = Field(min_length=8, max_length=32, example="intellia2026")
    confirm_password: str = Field(example="intellia2026")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8, max_length=32, example="intellia2026")
    confirm_password: str = Field(example="intellia2026")

    @model_validator(mode="after")
    def passwords_match(self):
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    access_expires_at: str
    refresh_expires_at: str


class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    roles: list[str]


class RegisterResponse(BaseModel):
    user: UserOut
    tokens: TokenPair


class LoginResponse(BaseModel):
    tokens: TokenPair


class MessageResponse(BaseModel):
    message: str
