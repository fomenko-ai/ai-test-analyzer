"""Bound local inputs before decoding; do not expose file contents in errors."""

import os
import stat
from pathlib import Path


class InputError(ValueError):
    """An input cannot be safely consumed."""


def read_bounded(path: Path, maximum: int) -> bytes:
    root = path.absolute().parent.resolve(strict=True)
    resolved = path.resolve(strict=True)
    if not resolved.is_relative_to(root):
        raise InputError("Input symlink escapes its supplied directory")
    descriptor = os.open(resolved, os.O_RDONLY | os.O_NONBLOCK | os.O_NOFOLLOW)
    with os.fdopen(descriptor, "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise InputError("Input must be a regular file")
        data = stream.read(maximum + 1)
    if len(data) > maximum:
        raise InputError("Input exceeds its configured size limit")
    return data
