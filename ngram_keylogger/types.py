from collections.abc import AsyncIterator
from typing import Any

from evdev import KeyEvent


EventPlus = tuple[KeyEvent, dict[Any, Any]]
EventGen = AsyncIterator[EventPlus]
KEventGen = AsyncIterator[tuple[str, str | None]]
