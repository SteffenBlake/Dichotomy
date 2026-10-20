#!/usr/bin/env python3
"""Render the public story separately from the agents' detailed event history.

This file is part of Dichotomy.
This work is licensed under CC BY-NC-ND 4.0.
License: https://raw.githubusercontent.com/SteffenBlake/Dichotomy/refs/heads/main/LICENSE
"""

import re

MAGNITUDES = {"Small": (1, 4), "Medium": (5, 8), "Large": (9, 12), "Huge": (13, 16)}


def roll_line(actor, data):
    """Keep stat, die face, effective bonus, total and outcome on one line."""
    purpose = data.get("purpose", "")
    attribute = data.get("attribute")
    if not attribute:
        match = re.search(r"\b(Alacrity|Vigor|Pulchritude|Temperament|Reputation)\b", purpose, re.IGNORECASE)
        attribute = match.group(1).capitalize() if match else None
    kind = data.get("kind")
    if not kind:
        kind = "attribute" if attribute else "luck" if data["sides"] == 20 and re.search(r"\bluck\b", purpose, re.IGNORECASE) else "selection"
    label = attribute or ("Luck" if kind == "luck" else "Selection")
    inverted = "aspect_index" in data or ("kind" not in data and bool(re.search(r"\binvert(?:s|ed|ing)?\b", purpose, re.IGNORECASE)))
    bonus = f"{data['modifier']:+d}" + ("†" if inverted else "")
    total = data["result"] + data["modifier"]
    success = data.get("success")
    if kind == "attribute" and success is None:
        magnitude = data.get("magnitude")
        if not magnitude:
            agreed = re.search(r"\bagreed\s+(Small|Medium|Large|Huge)\b", purpose, re.IGNORECASE)
            candidates = set(word.capitalize() for word in re.findall(r"\b(Small|Medium|Large|Huge)\b", purpose, re.IGNORECASE))
            magnitude = agreed.group(1).capitalize() if agreed else next(iter(candidates)) if len(candidates) == 1 else None
        if magnitude in MAGNITUDES:
            lower, upper = MAGNITUDES[magnitude]
            success = lower <= abs(total) <= upper
    elif kind == "luck" and success is None:
        success = data["result"] >= 11
    emoji = "✅" if success is True else "❌" if success is False else "🎲" if kind == "selection" else "❔"
    return f"*{actor} · {label}: d{data['sides']}({data['result']}) {bonus} → {total} {emoji}*"


def heading_text(text):
    """Keep a supplied section name on one readable heading line."""
    return " ".join(str(text).split()).replace("#", "").strip()


def story_text(text):
    """Preserve prose Markdown while reserving the transcript's heading hierarchy."""
    lines = []
    for line in text.strip().splitlines():
        match = re.match(r"^\s*#{1,6}\s+(.+)$", line)
        lines.append(f"**{match.group(1)}**" if match else line)
    return "\n".join(lines)


def legacy_name(changes, kind, number):
    """Recover a historical section label only from previously recorded notes."""
    explicit = changes.get(f"{kind}_name", "")
    if explicit:
        return heading_text(explicit)
    notes = changes.get("notes", "")
    match = re.search(rf"\b{kind}\s+{number}\s*(?::|is\b)\s*([^.;\n]+)", notes, re.IGNORECASE)
    if match:
        name = heading_text(match.group(1))
        return name[:1].upper() + name[1:]
    if kind == "challenge":
        beats = re.search(r"Planned beats:\s*([^.\n]+)", notes, re.IGNORECASE)
        if beats:
            parts = [re.sub(r"^and\s+", "", part.strip()) for part in beats.group(1).split(",")]
            if 0 < number <= len(parts):
                name = heading_text(parts[number - 1])
                return name[:1].upper() + name[1:]
    return ""


def sections(events):
    """Use explicit boundaries, with ledger transitions for older session journals."""
    result = {}
    chapter = challenge = 0
    volume = 1
    for index, event in enumerate(events):
        kind, data = event["kind"], event["data"]
        if kind == "chapter_started":
            chapter, challenge = data["number"], 0
            volume = data.get("volume", volume)
            result.setdefault(index, []).append((1, chapter, data["name"]))
        elif kind == "challenge_started":
            challenge = data["number"]
            result.setdefault(index, []).append((2, challenge, data["name"]))
        elif kind == "group_updated":
            changes = data["changes"]
            next_volume = changes.get("volume", volume)
            next_chapter = changes.get("chapter", chapter)
            next_challenge = changes.get("challenge", challenge)
            new_chapter = next_chapter > 0 and (next_chapter != chapter or next_volume != volume)
            new_challenge = next_chapter > 0 and next_challenge > 0 and (new_chapter or next_challenge != challenge)
            anchor = index
            # Old players announced the scene immediately before updating counters.
            for previous in range(index - 1, -1, -1):
                prior = events[previous]
                if prior["kind"] in ("say", "action", "roll", "director", "chapter_started", "challenge_started", "end_turn", "pass"):
                    if prior["kind"] in ("say", "action") and prior["actor"] == event["actor"]:
                        anchor = previous
                    break
            if new_chapter:
                result.setdefault(anchor, []).append((1, next_chapter, legacy_name(changes, "chapter", next_chapter)))
            if new_challenge:
                result.setdefault(anchor, []).append((2, next_challenge, legacy_name(changes, "challenge", next_challenge)))
            chapter, challenge, volume = next_chapter, next_challenge, next_volume
    return result


def render_transcript(events, legacy_character_names=None):
    """Show story actions and completed rolls, omitting internal bookkeeping."""
    output = ["# Prologue\n"]
    boundaries = sections(events)
    character_names = {}
    director = None
    legacy_character_names = legacy_character_names or {}
    for index, event in enumerate(events):
        for level, number, name in boundaries.get(index, []):
            label = "Chapter" if level == 1 else "Challenge"
            suffix = f": {heading_text(name)}" if name else ""
            output.append(f"\n{'#' * level} {label} {number}{suffix}\n")
        kind, actor, data = event["kind"], event["actor"], event["data"]
        if kind in ("sheet_created", "sheet_updated"):
            name = data.get("character_name", legacy_character_names.get(str(event["id"])))
            if name is not None:
                character_names[actor] = name
        if kind in ("chapter_started", "bid_opened"):
            director = None
        elif kind == "director":
            director = data["director"]
        if kind in ("say", "action"):
            title = f" — {heading_text(data['title'])}" if kind == "action" else ""
            role = "director" if actor == director else character_names.get(actor)
            name = f"{actor} ({heading_text(role)})" if role else actor
            output.append(f"\n### {name}{title}\n\n{story_text(data['text'])}\n")
        elif kind == "roll":
            output.append("\n" + roll_line(actor, data) + "\n")
        elif kind == "bid_opened":
            output.append("\n### Chapter Director bidding\n\n*Blind bids opened.*\n")
        elif kind == "bid_revealed":
            bids = " · ".join(f"{player}: {amount}" for player, amount in data["bids"].items())
            output.append(f"\n*Bids: {bids}.*\n")
        elif kind == "director":
            output.append(f"\n*Chapter Director: {data['director']}.*\n")
        elif kind == "complete":
            output.append("\n*All three players agreed to end the session.*\n")
        elif kind in ("attention", "disqualified"):
            output.append(f"\n*{story_text(data['text'])}*\n")
        # Declarations, checkpoints, sheet/group updates, feedback and transport
        # events remain available in events.jsonl and their dedicated views.
    return "\n\n".join(part.strip("\n") for part in output) + "\n"
