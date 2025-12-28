from typing import Any

from pydantic import Field as PydanticField


def Field(  # noqa: N802 - keep API-compatible name for schema usage
    default: Any = ...,
    *,
    description: str | None = None,
    example: Any | None = None,
    examples: list[Any] | None = None,
    **kwargs: Any,
) -> Any:
    """Add OpenAPI-friendly examples while staying compatible with Pydantic v2."""
    json_schema_extra = kwargs.pop("json_schema_extra", None)
    if json_schema_extra is None:
        json_schema_extra = {}
    else:
        json_schema_extra = dict(json_schema_extra)

    if example is not None:
        json_schema_extra.setdefault("example", example)

    if json_schema_extra:
        kwargs["json_schema_extra"] = json_schema_extra

    if examples is not None:
        kwargs["examples"] = examples

    return PydanticField(default, description=description, **kwargs)
