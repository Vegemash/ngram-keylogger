# Copyright (c) 2021, see AUTHORS. Licensed under GPLv3+, see LICENSE.

from collections.abc import AsyncIterator
import os
import runpy
import sys
from typing import Callable
import xdg.BaseDirectory

from ngram_keylogger.types import EventGen

FALLBACK = os.path.join(
    xdg.BaseDirectory.xdg_config_home, "ngram-keylogger", "config.py"
)


def default_path():
    find_config = xdg.BaseDirectory.load_first_config
    path = find_config("ngram-keylogger", "config.py")
    return path or FALLBACK


def read(path: str) -> Callable[[EventGen], AsyncIterator[tuple[str, str | None]]]:
    if not os.path.exists(path):
        print(f"Config {path} path does not exist", file=sys.stderr)
        sys.exit(1)
    return runpy.run_path(path)["action_generator"]
