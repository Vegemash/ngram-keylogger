# Minimal ngram-keylogger config

import ngram_keylogger
from ngram_keylogger.types import EventGen, KEventGen


async def action_generator(event_and_extras_gen: EventGen) -> KEventGen:
    gen = ngram_keylogger.aspect.keys_only(event_and_extras_gen)
    async for event, _ in gen:
        yield ngram_keylogger.util.short_key_name(event.code), None
