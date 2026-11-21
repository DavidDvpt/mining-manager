"""Authentication request and response schemas."""

from pydantic import BaseModel, ConfigDict, Field

from .base import ApiResponseModel


class SignInRequest(BaseModel):
    pseudo: str = Field(min_length=8, max_length=50)
    password: str = Field(min_length=8, max_length=50)


class SignUpRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    pseudo: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=8, max_length=50)


class UserResponse(ApiResponseModel):
    id: str
    role: str
    pseudo: str


class ProfileResponse(ApiResponseModel):
    user_id: str = Field(serialization_alias="userId")
    firstname: str | None = Field(default=None, serialization_alias="firstName")
    lastname: str | None = Field(default=None, serialization_alias="lastName")
    avatar_name: str | None = Field(default=None, serialization_alias="avatarName")
    email: str
