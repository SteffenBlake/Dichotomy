#!/usr/bin/env python3
"""Store password-encrypted character sheet revisions with narrow update operations.

This file is part of Dichotomy.
This work is licensed under CC BY-NC-ND 4.0.
License: https://raw.githubusercontent.com/SteffenBlake/Dichotomy/refs/heads/main/LICENSE
"""

import hashlib
import json
import secrets

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

ATTRIBUTES = ("Alacrity", "Vigor", "Pulchritude", "Temperament", "Reputation")
BONUSES = {4: (-13, 12), 6: (-11, 10), 8: (-9, 8), 10: (-7, 6), 12: (-5, 4)}


def empty_sheet(player):
    """Leave character choices to the player rather than inventing a build."""
    return {
        "player": player, "version": 0,
        "identity": {key: "" for key in ("name", "description", "motivations", "fears", "quirks")},
        "attributes": {key: {"die": None, "bonus": 0, "spent": False} for key in ATTRIBUTES},
        "resources": {"story_points": 12, "xp": 0, "failures_this_volume": 0,
                      "threads_completed": 0, "luck_spent": False, "out_of_luck": False},
        "aspects": [], "threads": [], "calamities": [], "notes": {"text": ""},
    }


def store(db, actor, password, session_id, sheet):
    """Append an AES-GCM revision using a fresh scrypt salt and nonce."""
    salt, nonce = secrets.token_bytes(16), secrets.token_bytes(12)
    key = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=16384, r=8, p=1, dklen=32)
    associated = f"dichotomy-sheet-v1:{session_id}:{actor}:{sheet['version']}".encode()
    ciphertext = AESGCM(key).encrypt(nonce, json.dumps(sheet, ensure_ascii=False).encode(), associated)
    db.execute("INSERT INTO sheet_versions VALUES (?,?,?,?,?)",
               (actor, sheet["version"], salt, nonce, ciphertext))


def read(db, actor, password, session_id, version=None):
    """Decrypt this player's current sheet or a specific operator-requested revision."""
    if not password:
        raise ValueError("password required to decrypt character sheet")
    if version is None:
        row = db.execute("SELECT * FROM sheet_versions WHERE actor=? ORDER BY version DESC LIMIT 1", (actor,)).fetchone()
    else:
        row = db.execute("SELECT * FROM sheet_versions WHERE actor=? AND version=?", (actor, version)).fetchone()
    if row is None:
        raise ValueError("character sheet has not been initialized")
    key = hashlib.scrypt(password.encode("utf-8"), salt=row["salt"], n=16384, r=8, p=1, dklen=32)
    associated = f"dichotomy-sheet-v1:{session_id}:{actor}:{row['version']}".encode()
    try:
        return json.loads(AESGCM(key).decrypt(row["nonce"], row["ciphertext"], associated))
    except InvalidTag as error:
        raise ValueError("character sheet authentication failed; do not overwrite it") from error


def attribute_declaration(sheet, attribute, aspect_index=None, aspect_source="personal", aspect_reason=None, group_aspects=()):
    """Resolve a chosen attribute from the sheet instead of trusting copied dice."""
    if not isinstance(attribute, str) or attribute not in ATTRIBUTES:
        raise ValueError("choose Alacrity, Vigor, Pulchritude, Temperament or Reputation")
    assignment = sheet["attributes"][attribute]
    if assignment["die"] is None:
        raise ValueError("create your character before declaring an attribute roll")
    if assignment["spent"]:
        raise ValueError(f"{attribute} is already spent; choose an available attribute")
    intent = {"kind": "attribute", "attribute": attribute, "sides": assignment["die"],
              "permanent_bonus": assignment["bonus"], "modifier": assignment["bonus"],
              "sheet_version": sheet["version"]}
    if aspect_source not in ("personal", "group"):
        raise ValueError("aspect_source must be personal or group")
    if aspect_index is not None:
        aspects = sheet["aspects"] if aspect_source == "personal" else group_aspects
        if type(aspect_index) is not int or not 0 <= aspect_index < len(aspects):
            raise ValueError("choose an existing zero-based Aspect index")
        if aspects[aspect_index]["spent"]:
            raise ValueError("that Aspect is already spent")
        if not isinstance(aspect_reason, str) or not aspect_reason.strip() or len(aspect_reason) > 8000:
            raise ValueError("explain why the chosen Aspect applies before inverting the bonus")
        intent.update(modifier=-assignment["bonus"], aspect_index=aspect_index,
                      aspect_source=aspect_source, aspect_reason=aspect_reason)
    elif aspect_reason is not None or aspect_source != "personal":
        raise ValueError("provide aspect_index when choosing an Aspect")
    return intent


def validate_fields(changes, allowed):
    """Refuse unknown keys instead of silently replacing unrelated sheet data."""
    if not isinstance(changes, dict) or not changes or set(changes) - set(allowed):
        raise ValueError("invalid or empty section fields")
    for name, value in changes.items():
        kind = allowed[name]
        if kind is str and (not isinstance(value, str) or len(value) > 8000):
            raise ValueError(f"{name} must be text of at most 8000 characters")
        if kind is bool and type(value) is not bool:
            raise ValueError(f"{name} must be true or false")
        if kind is int and (type(value) is not int or not 0 <= value <= 1000000):
            raise ValueError(f"{name} must be a nonnegative integer")


def create(sheet, character):
    """Validate a whole starting character before saving a single revision."""
    if sheet["version"] != 0:
        raise ValueError("character already created; use section updates for later changes")
    required = {"identity", "attributes", "aspects", "threads", "calamities"}
    if not isinstance(character, dict) or not required <= set(character) or set(character) - required - {"notes"}:
        raise ValueError("provide identity, attributes, aspects, threads, calamities, and optional notes")
    result = empty_sheet(sheet["player"])
    identity = character["identity"]
    if not isinstance(identity, dict) or set(identity) != set(result["identity"]) or any(not isinstance(value, str) or not value.strip() for value in identity.values()):
        raise ValueError("provide name, description, motivations, fears and quirks")
    result = update(result, "identity", identity, result["version"])
    if not isinstance(character["attributes"], dict) or set(character["attributes"]) != set(ATTRIBUTES):
        raise ValueError("assign all five attributes in the initial character")
    result = update(result, "attributes", character["attributes"], result["version"])
    if any(value["spent"] for value in result["attributes"].values()):
        raise ValueError("starting attribute dice must be unspent")
    for section, count in (("aspects", 1), ("threads", 2), ("calamities", 2)):
        entries = character[section]
        if not isinstance(entries, list) or len(entries) != count:
            raise ValueError(f"starting characters need exactly {count} {section}")
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict) or "index" in entry:
                raise ValueError("initial list entries are objects without an index")
            result = update(result, section, {**entry, "index": index}, result["version"])
    if result["aspects"][0]["spent"] or any(entry["xp"] for entry in result["threads"]) or any(not entry["active"] for entry in result["calamities"]):
        raise ValueError("starting Aspects are unspent, Threads have zero XP, and Calamities are active")
    if "notes" in character:
        result = update(result, "notes", character["notes"], result["version"])
    result["version"] = 1
    return result


def update(sheet, section, changes, expected_version):
    """Patch one named section and reject an update based on a stale sheet."""
    if type(expected_version) is not int or expected_version != sheet["version"]:
        raise ValueError("stale sheet version; read your sheet again")
    if section == "identity":
        validate_fields(changes, {key: str for key in sheet[section]})
        sheet[section].update(changes)
    elif section == "resources":
        validate_fields(changes, {key: bool if type(value) is bool else int
                                  for key, value in sheet[section].items()})
        sheet[section].update(changes)
    elif section == "notes":
        validate_fields(changes, {"text": str})
        sheet[section].update(changes)
    elif section == "attributes":
        if not isinstance(changes, dict) or not changes or set(changes) - set(ATTRIBUTES):
            raise ValueError("use the five named attributes")
        for attribute, patch in changes.items():
            if not isinstance(patch, dict) or not patch or set(patch) - {"die", "bonus", "spent"}:
                raise ValueError("attribute fields are die, bonus and spent")
            current = {**sheet[section][attribute], **patch}
            die, bonus = current["die"], current["bonus"]
            if type(die) is not int or die not in BONUSES or type(bonus) is not int or not BONUSES[die][0] <= bonus <= BONUSES[die][1]:
                raise ValueError("invalid attribute die or bonus range")
            if type(current["spent"]) is not bool:
                raise ValueError("spent must be true or false")
            sheet[section][attribute] = current
        assigned = [value["die"] for value in sheet[section].values() if value["die"] is not None]
        if len(set(assigned)) != len(assigned):
            raise ValueError("each die size can be assigned only once; swap both attributes in one update")
    elif section in ("aspects", "threads", "calamities"):
        if not isinstance(changes, dict):
            raise ValueError("supply an indexed entry patch")
        changes = dict(changes)
        index = changes.pop("index", None)
        if type(index) is not int or not 0 <= index <= len(sheet[section]):
            raise ValueError("index must identify an existing entry or the next new entry (zero-based)")
        defaults = {"aspects": {"text": "", "spent": False},
                    "threads": {"question": "", "xp": 0},
                    "calamities": {"text": "", "active": True}}[section]
        validate_fields(changes, {key: type(value) for key, value in defaults.items()})
        if index == len(sheet[section]):
            content = "question" if section == "threads" else "text"
            if not changes.get(content, "").strip():
                raise ValueError("a new entry needs its description")
            sheet[section].append(defaults)
        sheet[section][index].update(changes)
    else:
        raise ValueError("unknown sheet section")
    sheet["version"] += 1
    return sheet
