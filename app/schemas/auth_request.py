from pydantic import BaseModel, Field

from app.enum.user_role import UserRole


class UserRegisterRequest(BaseModel):
    """Public self service registration.

    The role is deliberately not part of this payload: self registration
    must not be able to hand itself TELLER or ADMIN rights.
    """

    username: str = Field(min_length=3, max_length=50)

    # bcrypt only hashes the first 72 bytes, so longer values are rejected.
    password: str = Field(min_length=8, max_length=72)


class UserCreateRequest(UserRegisterRequest):
    """Administrative user creation, where the role can be chosen."""

    role: UserRole = UserRole.CUSTOMER


class UserLoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)

    password: str = Field(min_length=1, max_length=72)
