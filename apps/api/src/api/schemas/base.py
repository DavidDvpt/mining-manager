"""Shared Pydantic configuration for API response schemas."""

import re

from pydantic import BaseModel, ConfigDict


def to_camel(value: str) -> str:
    """Convert a snake_case field name to the camelCase API representation."""

    return re.sub(r"_([a-zA-Z0-9])", lambda match: match.group(1).upper(), value)


class ApiResponseModel(BaseModel):
    """Base model that serializes every API response field using camelCase."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        from_attributes=True,
        populate_by_name=True,
    )
