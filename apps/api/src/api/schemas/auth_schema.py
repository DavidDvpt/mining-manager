"""Authentication request and response schemas."""

from pydantic import BaseModel, ConfigDict, Field


class SignInRequest(BaseModel):
    pseudo: str = Field(min_length=8, max_length=50)
    password: str = Field(min_length=8, max_length=50)


class SignUpRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    pseudo: str = Field(min_length=1, max_length=50)
    password: str = Field(min_length=8, max_length=50)


class UserResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    id: str
    role: str
    pseudo: str


class ProfileResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    user_id: str = Field(serialization_alias="userId")
    firstname: str | None = Field(default=None, serialization_alias="firstName")
    lastname: str | None = Field(default=None, serialization_alias="lastName")
    avatar_name: str | None = Field(default=None, serialization_alias="avatarName")
    email: str
