#!/usr/bin/env python3
"""Track the shared game ledger without deciding game outcomes.

This file is part of Dichotomy.
This work is licensed under CC BY-NC-ND 4.0.
License: https://raw.githubusercontent.com/SteffenBlake/Dichotomy/refs/heads/main/LICENSE
"""


def empty_group():
    """Include Saga, pacing, Raised Stakes and shared rewards from the full rules."""
    return {
        "version": 0, "saga_question": "", "saga_number": 1, "saga_points": 0,
        "volume": 1, "chapter": 0, "challenge": 0, "challenge_limit": 4,
        "chapter_name": "", "challenge_name": "",
        "raised_stakes_triggered": False, "raised_stakes_next_chapter": False,
        "raised_stakes_active": False, "climactic_end": False, "interlude_active": False,
        "group_aspects": [], "completed_sagas": [], "notes": "",
    }


def update_group(group, changes, expected_version):
    """Apply an explicit, version-checked patch to the shared ledger."""
    group = {**empty_group(), **group}
    if type(expected_version) is not int or expected_version != group["version"]:
        raise ValueError("stale group version; read the shared ledger again")
    if not isinstance(changes, dict) or not changes or set(changes) - (set(group) - {"version"}):
        raise ValueError("invalid group fields")
    for name, value in changes.items():
        prototype = group[name]
        if type(prototype) is bool and type(value) is not bool:
            raise ValueError(f"{name} must be true or false")
        if type(prototype) is int and (type(value) is not int or not 0 <= value <= 1000000):
            raise ValueError(f"{name} must be a nonnegative integer")
        if type(prototype) is str and (not isinstance(value, str) or len(value) > 12000):
            raise ValueError(f"{name} must be text of at most 12000 characters")
        if name == "challenge_limit" and value not in (4, 8):
            raise ValueError("challenge_limit is 4 or 8")
        if name in ("group_aspects", "completed_sagas"):
            if not isinstance(value, list) or len(value) > 1000:
                raise ValueError("supply a list of shared entries")
            expected = {"text", "spent"} if name == "group_aspects" else {"saga_question", "chooser", "group_aspect"}
            for entry in value:
                if not isinstance(entry, dict) or set(entry) != expected:
                    raise ValueError(f"invalid {name} entry fields")
                for key, content in entry.items():
                    if key == "spent":
                        if type(content) is not bool:
                            raise ValueError("spent must be true or false")
                    elif not isinstance(content, str) or len(content) > 8000:
                        raise ValueError("shared entry values must be text")
    group.update(changes)
    group["version"] += 1
    return group
