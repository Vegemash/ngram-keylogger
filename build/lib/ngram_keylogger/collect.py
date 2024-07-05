#!/usr/bin/env python
# Copyright (c) 2021, see AUTHORS. Licensed under GPLv3+, see LICENSE.

import asyncio
import signal

import click
import evdev
from evdev.device import InputDevice

import ngram_keylogger
from ngram_keylogger.types import EventGen, EventPlus


def collect(device_paths: tuple[str, ...], db_path: str, config: str) -> None:
    action_generator = ngram_keylogger.config.read(config)

    statsdb = ngram_keylogger.db.StatsDB(db_path)
    event_and_extras_queue: asyncio.Queue[EventPlus] = asyncio.Queue()

    async def shutdown(sig, loop):
        click.echo(f"Caught {sig.name}")
        click.echo("Stopping keystroke collection...")
        for task in asyncio.all_tasks():
            if task is not asyncio.current_task():
                task.cancel()
        click.echo("Flushing statistics...")
        statsdb.save_all_to_disk()
        click.echo("Stopping...")
        await event_and_extras_queue.join()
        loop.call_soon_threadsafe(loop.stop)

    async def collect_events(device_path):
        while True:
            try:
                click.echo(f"Opening device {device_path}...")
                device: InputDevice = evdev.InputDevice(device_path)
                click.echo(f"Opened device {device_path}.")
            except OSError:
                click.echo(f"Could not open {device_path}.")
                await asyncio.sleep(15)
                continue
            try:
                async for event in device.async_read_loop():
                    # click.echo(evdev.categorize(event), sep=": ")
                    # print(event)
                    await event_and_extras_queue.put((event, {}))
            except OSError:
                click.echo(f"Lost device {device_path}.")
                await asyncio.sleep(5)

    async def unwind_queue(
        l_event_and_extras_queue: asyncio.Queue[EventPlus],
    ) -> EventGen:
        while True:
            event, extras = await l_event_and_extras_queue.get()
            l_event_and_extras_queue.task_done()
            yield event, extras

    for device in device_paths:
        asyncio.ensure_future(collect_events(device))

    loop = asyncio.get_event_loop()
    for sig in signal.SIGINT, signal.SIGTERM, signal.SIGHUP:
        loop.add_signal_handler(
            sig, lambda sig=sig: asyncio.create_task(shutdown(sig, loop))
        )

    async def process_actions():
        gen = action_generator(unwind_queue(event_and_extras_queue))
        async for action, context in gen:
            if action != ngram_keylogger.NOTHING:
                statsdb.account_for_action(action, context)
            else:
                statsdb.flush_pipeline()

    try:
        loop.run_until_complete(process_actions())
    except asyncio.exceptions.CancelledError:
        click.echo("Stopped.")
