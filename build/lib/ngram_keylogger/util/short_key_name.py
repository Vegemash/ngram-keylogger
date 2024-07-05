# Copyright (c) 2021, see AUTHORS. Licensed under GPLv3+, see LICENSE.

import evdev

KEY_TO_CHARACTER = {  # type: ignore[reportUnknownVariableType]
    evdev.ecodes.KEY_GRAVE: "~",  # type: ignore[reportAttributeAccessIssue]
    evdev.ecodes.KEY_COMMA: ",",  # type: ignore[reportAttributeAccessIssue]
    evdev.ecodes.KEY_DOT: ".",  # type: ignore[reportAttributeAccessIssue]
    evdev.ecodes.KEY_SLASH: "/",  # type: ignore[reportAttributeAccessIssue]
    evdev.ecodes.KEY_SEMICOLON: ";",  # type: ignore[reportAttributeAccessIssue]
    evdev.ecodes.KEY_APOSTROPHE: "'",  # type: ignore[reportAttributeAccessIssue]
    evdev.ecodes.KEY_LEFTBRACE: "[",  # type: ignore[reportAttributeAccessIssue]
    evdev.ecodes.KEY_RIGHTBRACE: "]",  # type: ignore[reportAttributeAccessIssue]
    evdev.ecodes.KEY_BACKSLASH: "\\",  # type: ignore[reportAttributeAccessIssue]
    evdev.ecodes.KEY_MINUS: "-",  # type: ignore[reportAttributeAccessIssue]
    evdev.ecodes.KEY_EQUAL: "=",  # type: ignore[reportAttributeAccessIssue]
}


def short_key_name(key_code) -> str:  # type: ignore[a]
    if key_code in KEY_TO_CHARACTER:
        return KEY_TO_CHARACTER[key_code]

    s: str | list[str] = evdev.ecodes.KEY[key_code]  # type: ignore[reportAttributeAccessIssue]
    s: str = s[0] if isinstance(s, list) else s
    if s.startswith("KEY_"):
        s = s.replace("KEY_", "", 1)
    s = s.lower()
    return s
