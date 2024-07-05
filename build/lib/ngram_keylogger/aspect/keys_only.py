# Copyright (c) 2021, see AUTHORS. Licensed under GPLv3+, see LICENSE.

import evdev

from ngram_keylogger.types import EventGen


async def keys_only(event_and_extras_gen: EventGen) -> EventGen:
    async for event, extras in event_and_extras_gen:
        if event.type == evdev.ecodes.EV_KEY:  # type: ignore[reportAttributeAccessIssue]
            yield event, extras
