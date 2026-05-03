from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class TokenPair(BaseModel):
    accessToken: str
    refreshToken: str
    tokenType: str
    accessExpiresAt: str
    refreshExpiresAt: str

# --------------- Refresh Access Token ---------------

class RefreshRequest(BaseModel):
    refreshToken: str  


class RefreshResponse(BaseModel):
    accessToken: str
    type: str
    exp: int        

# --------------- Register ---------------

class RegisterRequest(BaseModel):
    email: EmailStr = Field(example="intellia2026@gmail.com")

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class RegisterResponse(BaseModel):
    email: str
    isVerified: bool

# --------------- Login ---------------

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class LoginResponse(BaseModel):
    token: TokenPair

# --------------- Login ---------------

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


class RevokeRequest(BaseModel):
    token: str 

# --------------- Set Password ---------------

class SetPasswordRequest(BaseModel):
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


class SetPasswordResponse(BaseModel):
    token: TokenPair

# --------------- Verifiy OTP ---------------

class VerifiyOtpRequest(BaseModel):
    email: EmailStr = Field(example="intellia2026@gmail.com")
    otp: int

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        return v.strip().lower()


class VerifiyOtpResponse(BaseModel):
    email: str
    isVerified: bool

# --------------- Message ---------------

class MessegeResponse(BaseModel):
    message: str = "success"    