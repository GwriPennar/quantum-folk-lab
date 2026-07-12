"""Public Learning Console Foundations package.

Parses portable Markdown lessons under ``learn/`` without depending on
ignored ``private/`` trees.
"""

from __future__ import annotations

from quantum_folk_lab.learning.models import LessonDocument, LessonMetadata
from quantum_folk_lab.learning.registry import LessonRegistry, load_registry

__all__ = [
    "LessonDocument",
    "LessonMetadata",
    "LessonRegistry",
    "load_registry",
]
