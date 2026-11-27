"""Small, explicit local settings; future corporate examples are not accepted."""

import json
from pathlib import Path

import yaml  # type: ignore[import-untyped]

from ai_test_analyzer.adapters.files import InputError, read_bounded
from ai_test_analyzer.domain.models import FileContext, Settings


def unique_mapping(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise InputError("Duplicate configuration key")
        result[key] = value
    return result


class UniqueSafeLoader(yaml.SafeLoader):
    pass


def yaml_mapping(loader: UniqueSafeLoader, node: yaml.MappingNode) -> dict[str, object]:
    if not isinstance(node, yaml.MappingNode):
        raise InputError("Expected configuration mapping")
    pairs = [
        (
            loader.construct_object(key, deep=True),
            loader.construct_object(value, deep=True),
        )
        for key, value in node.value
    ]
    return unique_mapping(pairs)


UniqueSafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, yaml_mapping
)


def load_settings(path: Path | None) -> Settings:
    if path is None:
        return Settings()
    try:
        value = yaml.load(read_bounded(path, 64 * 1024), Loader=UniqueSafeLoader)
        return Settings.model_validate(value)
    except Exception:
        raise InputError("Configuration is unavailable or invalid") from None


def load_context(path: Path | None) -> FileContext:
    if path is None:
        return FileContext()
    try:
        value = json.loads(
            read_bounded(path, 64 * 1024), object_pairs_hook=unique_mapping
        )
        return FileContext.model_validate(value)
    except Exception:
        raise InputError("Context is unavailable or invalid") from None
