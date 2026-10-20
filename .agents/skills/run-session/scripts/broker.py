#!/usr/bin/env python3
"""Own the simulation journal and expose per-player append-only sockets.

This file is part of Dichotomy.
This work is licensed under CC BY-NC-ND 4.0.
License: https://raw.githubusercontent.com/SteffenBlake/Dichotomy/refs/heads/main/LICENSE
"""

import hashlib
import hmac
import json
import os
from pathlib import Path
import secrets
import socketserver
import sqlite3
import threading
import time
from datetime import datetime, timezone
from group import empty_group, update_group
from transcript import MAGNITUDES, render_transcript

PLAYERS = ("Spike", "Johnny", "Timmy")
DICE = (4, 6, 8, 10, 12, 20)
MAX_REQUEST = 65536


def password_record(password):
    """Derive a salted scrypt verifier without persisting the password itself."""
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=16384, r=8, p=1, dklen=32)
    return {"algorithm": "scrypt", "salt": salt.hex(), "n": 16384, "r": 8, "p": 1,
            "digest": digest.hex()}


def create_credentials(directory, passwords=None):
    """Return initial passwords once; store only their salted password verifiers."""
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    passwords = passwords or {actor: secrets.token_urlsafe(24) for actor in PLAYERS}
    records = {actor: password_record(password) for actor, password in passwords.items()}
    with (directory / "auth.json").open("x", encoding="utf-8") as handle:
        json.dump(records, handle)
    (directory / "auth.json").chmod(0o600)
    return passwords


def verify_password(password, record):
    """Use the stored scrypt parameters and constant-time digest comparison."""
    if not isinstance(password, str) or not 1 <= len(password) <= 256:
        return False
    if record["algorithm"] != "scrypt":
        return False
    digest = hashlib.scrypt(password.encode("utf-8"), salt=bytes.fromhex(record["salt"]),
                            n=record["n"], r=record["r"], p=record["p"], dklen=32)
    return hmac.compare_digest(digest, bytes.fromhex(record["digest"]))


def quoted(text):
    """Keep player prose visibly separate from broker event headings."""
    return "\n".join("> " + line if line else ">" for line in text.splitlines())


def display_value(value):
    """Format structured tracking data without HTML entities or dense JSON."""
    if isinstance(value, bool):
        return "yes" if value else "no"
    if value is None:
        return "none"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, indent=2)
    return str(value)


def render_event(event):
    """Render a journal event without giving prose system provenance."""
    if event["kind"] in ("pass", "end_turn", "bid_submitted"):
        return ""
    data = event["data"]
    if event["kind"] == "sheet_updated":
        return f"\n*#{event['id']} · {event['actor']} updated {data['section']} (sheet version {data['version']}).*\n"
    heading = f"\n## #{event['id']} · {event['actor']} · {event['kind']} · {event['time']}\n\n"
    if event["kind"] == "roll":
        body = (f"**Broker roll: d{data['sides']} → {data['result']}** "
                f"(declared in #{data['intent_id']}; modifier {data['modifier']:+d}).\n\n"
                + quoted(data["purpose"]))
        if data.get("attribute"):
            body = f"**{data['attribute']}** · total **{data['result'] + data['modifier']}**\n\n" + body
    elif event["kind"] == "declare":
        body = f"Declared **d{data['sides']}**, modifier **{data['modifier']:+d}**.\n\n" + quoted(data["purpose"])
        if data.get("attribute"):
            body = f"**Confirmed from sheet: {data['attribute']}** (version {data['sheet_version']}).\n\n" + body
        if data.get("aspect_reason"):
            body += "\n\n" + quoted("Aspect inversion: " + data["aspect_reason"])
    elif event["kind"] == "bid_opened":
        body = f"Blind bidding opened: **{data['round']}**.\n\n" + quoted(data["text"])
    elif event["kind"] == "bid_revealed":
        rows = "\n".join(f"| {player} | {amount} |" for player, amount in data["bids"].items())
        body = f"**{data['round']} — bids revealed**\n\n| Player | Bid |\n| --- | ---: |\n{rows}"
    elif event["kind"] == "director":
        body = f"**Chapter Director: {data['director']}**\n\n" + quoted(data["reason"])
    elif event["kind"] == "group_updated":
        changes = "\n".join(f"- {key.replace('_', ' ').capitalize()}: {display_value(value)}" for key, value in data["changes"].items())
        body = f"Shared ledger version {data['version']}:\n\n" + quoted(changes)
    elif event["kind"] == "sheet_created":
        body = "Created the complete starting character sheet in one encrypted revision."
    else:
        body = quoted(data.get("text", json.dumps(data, ensure_ascii=False, indent=2)))
    return heading + body + "\n"


class Broker:
    """Serialize mutations and keep identity outside player-supplied payloads."""

    def __init__(self, directory, observer_directory=None):
        """Open durable storage and recover observer files from committed events."""
        self.directory = Path(directory).resolve()
        self.directory.mkdir(parents=True, exist_ok=True)
        self.observer = Path(observer_directory or directory).resolve()
        self.observer.mkdir(parents=True, exist_ok=True)
        self.credentials = json.loads((self.directory / "auth.json").read_text(encoding="utf-8"))
        self.condition = threading.Condition(threading.RLock())
        self.servers = []
        self.closing = False
        self.db = sqlite3.connect(self.directory / "journal.sqlite3", check_same_thread=False)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
            PRAGMA journal_mode=WAL;
            PRAGMA synchronous=FULL;
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time TEXT NOT NULL, actor TEXT NOT NULL,
                kind TEXT NOT NULL, data TEXT NOT NULL
            );
            CREATE TRIGGER IF NOT EXISTS events_no_update BEFORE UPDATE ON events
                BEGIN SELECT RAISE(ABORT, 'events are append only'); END;
            CREATE TRIGGER IF NOT EXISTS events_no_delete BEFORE DELETE ON events
                BEGIN SELECT RAISE(ABORT, 'events are append only'); END;
            CREATE TABLE IF NOT EXISTS state (id INTEGER PRIMARY KEY CHECK(id=1), data TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS requests (
                actor TEXT NOT NULL, request_id TEXT NOT NULL,
                payload TEXT NOT NULL, response TEXT NOT NULL,
                PRIMARY KEY(actor, request_id)
            );
            CREATE TABLE IF NOT EXISTS sheet_versions (
                actor TEXT NOT NULL, version INTEGER NOT NULL,
                salt BLOB NOT NULL, nonce BLOB NOT NULL, ciphertext BLOB NOT NULL,
                PRIMARY KEY(actor, version)
            );
        """)
        initial = {"turn": 0, "turn_number": 1, "passes": 0, "paused": False,
                   "complete": False, "pending": {}, "bid_round": None,
                   "bids": {}, "used_rounds": [], "finish_votes": [], "checkpoints": {},
                   "disqualified": [], "director": None, "last_bid_reveal": None, "group": empty_group()}
        with self.db:
            self.db.execute("INSERT OR IGNORE INTO state VALUES (1, ?)", (json.dumps(initial),))
            if not self.db.execute("SELECT 1 FROM events LIMIT 1").fetchone():
                self.append("System", "started", {"text": "Session ready. Speaking order: Spike → Johnny → Timmy. Read the rules independently and agree on one session's scope."})
        self.exported = 0
        (self.observer / "events.jsonl").write_text("", encoding="utf-8")
        for name, title in (("feature-requests.md", "Requests for additional scripts"),
                            ("creator-feedback.md", "Constructive playtest feedback for the creator")):
            (self.observer / name).write_text(f"# {title}\n\n", encoding="utf-8")
        self.export()

    def seed_sheets(self, passwords):
        """Initialize blank encrypted sheets without retaining their passwords."""
        from sheets import empty_sheet, store
        with self.condition, self.db:
            for actor in PLAYERS:
                if not self.db.execute("SELECT 1 FROM sheet_versions WHERE actor=?", (actor,)).fetchone():
                    store(self.db, actor, passwords[actor], self.observer.name, empty_sheet(actor))

    def state(self):
        """Load the committed scheduling and sealed-submission state."""
        with self.condition:
            return json.loads(self.db.execute("SELECT data FROM state WHERE id=1").fetchone()[0])

    def save(self, state):
        """Persist scheduling state inside the caller's transaction."""
        self.db.execute("UPDATE state SET data=? WHERE id=1", (json.dumps(state),))

    def append(self, actor, kind, data):
        """Assign provenance and sequence at the trusted storage boundary."""
        now = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
        result = self.db.execute("INSERT INTO events(time,actor,kind,data) VALUES (?,?,?,?)",
                                 (now, actor, kind, json.dumps(data, ensure_ascii=False)))
        return result.lastrowid

    def events(self, after=0):
        """Read only public events; unrevealed bid values live outside this table."""
        with self.condition:
            return [{"id": row["id"], "time": row["time"], "actor": row["actor"],
                     "kind": row["kind"], "data": json.loads(row["data"])}
                    for row in self.db.execute("SELECT * FROM events WHERE id>? ORDER BY id", (after,))]

    def public_state(self, state):
        """Exclude secret bid values from every player's status response."""
        return {"speaker": PLAYERS[state["turn"]], "turn_number": state["turn_number"],
                "paused": state["paused"], "complete": state["complete"],
                "bid_round": state["bid_round"], "submitted": list(state["bids"]),
                "disqualified": state["disqualified"],
                "director": state["director"], "last_bid_reveal": state["last_bid_reveal"],
                "group": state["group"],
                "finish_votes": state["finish_votes"], "checkpoints": state["checkpoints"]}

    def export(self):
        """Append observer events and atomically replace the current status view."""
        events = self.events(self.exported)
        with (self.observer / "events.jsonl").open("a", encoding="utf-8") as raw:
            for event in events:
                raw.write(json.dumps(event, ensure_ascii=False) + "\n")
                log = {"feature_request": "feature-requests.md", "feedback": "creator-feedback.md"}.get(event["kind"])
                if log:
                    with (self.observer / log).open("a", encoding="utf-8") as notes:
                        notes.write(render_event(event))
                self.exported = event["id"]
        names_path = self.directory / "character-names.json"
        legacy_names = json.loads(names_path.read_text(encoding="utf-8")) if names_path.exists() else {}
        transcript = render_transcript(self.events(), legacy_names)
        path = self.observer / "transcript.md"
        previous = path.read_text(encoding="utf-8") if path.exists() else ""
        if transcript.startswith(previous):
            with path.open("a", encoding="utf-8") as readable:
                readable.write(transcript[len(previous):])
        else:
            # Historical regeneration may reorganize sections; new sessions use
            # explicit boundaries so ordinary live updates continue to append.
            path.write_text(transcript, encoding="utf-8")
        state = self.public_state(self.state())
        content = ("# Session status\n\n"
                   f"- Speaker: {state['speaker']}\n- Speaking turn: {state['turn_number']}\n"
                   f"- Paused: {state['paused']}\n- Complete: {state['complete']}\n"
                   f"- Open sealed bid: {state['bid_round']}\n"
                   f"- Bid submissions: {', '.join(state['submitted']) or 'none'}\n"
                   f"- Completion votes: {', '.join(state['finish_votes']) or 'none'}\n")
        content += f"- Disqualified: {', '.join(state['disqualified']) or 'none'}\n"
        content += f"- Chapter Director: {state['director'] or 'not assigned'}\n"
        group = state["group"]
        content += (f"- Saga {group['saga_number']}: {group['saga_points']} points\n"
                    f"- Volume / chapter / challenge: {group['volume']} / {group['chapter']} / {group['challenge']}\n"
                    f"- Raised Stakes active: {group['raised_stakes_active']}\n"
                    f"- Climactic End: {group['climactic_end']}\n"
                    f"- Interlude active: {group['interlude_active']}\n")
        shared = "\n".join(f"- {key.replace('_', ' ').capitalize()}: {display_value(value)}" for key, value in group.items())
        content += f"\n## Shared ledger\n\n{quoted(shared)}\n"
        for actor, checkpoint in state["checkpoints"].items():
            content += f"\n## {actor}'s latest checkpoint\n\n{quoted(checkpoint)}\n"
        temporary = self.observer / "status.md.tmp"
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(self.observer / "status.md")

    def text(self, request, key="text"):
        """Reject empty or oversized content before storing it."""
        value = request.get(key)
        if not isinstance(value, str) or not value.strip() or len(value) > 24000:
            raise ValueError(f"{key} must be nonempty text of at most 24000 characters")
        return value

    def advance(self, state, passed=False):
        """Rotate speaking turns without interpreting gameplay."""
        state["passes"] = state["passes"] + 1 if passed else 0
        state["turn"] = (state["turn"] + 1) % len(PLAYERS)
        state["turn_number"] += 1
        if state["passes"] >= len(PLAYERS):
            state["paused"] = True
            self.append("System", "attention", {"text": "All three players passed. Session paused for operator attention. No gameplay outcome has been chosen."})

    def mutate(self, actor, request, state, password=None):
        """Apply the small allowed player protocol; never accept a claimed actor."""
        operation = request["op"]
        if operation in ("feature_request", "feedback"):
            return {"ok": True, "event_id": self.append(actor, operation, {"text": self.text(request)})}
        if state["complete"] or state["paused"]:
            raise ValueError("session is complete or paused")
        if actor != PLAYERS[state["turn"]]:
            raise ValueError("it is another player's speaking turn")
        if request.get("turn") != state["turn_number"]:
            raise ValueError("stale speaking turn; read status again")
        if operation in ("start_chapter", "start_challenge"):
            if actor in state["pending"]:
                raise ValueError("finish the pending roll before starting a new section")
            number, name = request.get("number"), request.get("name")
            if type(number) is not int or number < 1 or not isinstance(name, str) or not name.strip() or len(name) > 160 or "\n" in name or "\r" in name:
                raise ValueError("supply a positive section number and a single-line name (at most 160 characters)")
            group = state["group"]
            if operation == "start_chapter":
                group.update(chapter=number, chapter_name=name.strip(), challenge=0, challenge_name="")
                state["director"] = None
                kind = "chapter_started"
            else:
                if group["chapter"] < 1 or number > group["challenge_limit"]:
                    raise ValueError("start a chapter first and choose a challenge within its limit")
                group.update(challenge=number, challenge_name=name.strip())
                kind = "challenge_started"
            group["version"] += 1
            event_id = self.append(actor, kind, {"number": number, "name": name.strip(), "volume": group["volume"], "chapter": group["chapter"]})
        elif operation == "action":
            title = self.text(request, "title")
            if len(title) > 160 or "\n" in title or "\r" in title:
                raise ValueError("action title must fit on one line (at most 160 characters)")
            event_id = self.append(actor, "action", {"title": title, "text": self.text(request)})
            state["passes"] = 0
        elif operation == "group_update":
            state["group"] = update_group(state["group"], request.get("changes"), request.get("expected_version"))
            event_id = self.append(actor, "group_updated", {"version": state["group"]["version"], "changes": request["changes"]})
        elif operation == "sheet_create":
            from sheets import create, read, store
            sheet = create(read(self.db, actor, password, self.observer.name), request.get("character"))
            store(self.db, actor, password, self.observer.name, sheet)
            event_id = self.append(actor, "sheet_created", {"version": sheet["version"], "character_name": sheet["identity"]["name"]})
        elif operation == "sheet_update":
            from sheets import read, store, update
            sheet = read(self.db, actor, password, self.observer.name)
            sheet = update(sheet, request.get("section"), request.get("changes"), request.get("expected_version"))
            store(self.db, actor, password, self.observer.name, sheet)
            metadata = {"section": request["section"], "version": sheet["version"]}
            if request["section"] == "identity":
                metadata["character_name"] = sheet["identity"]["name"]
            event_id = self.append(actor, "sheet_updated", metadata)
        elif operation == "set_director":
            director = request.get("director")
            if director not in PLAYERS:
                raise ValueError("director must be Spike, Johnny or Timmy")
            state["director"] = director
            event_id = self.append(actor, "director", {"director": director, "reason": self.text(request, "reason")})
        elif operation in ("say", "checkpoint"):
            value = self.text(request)
            event_id = self.append(actor, operation, {"text": value})
            if operation == "checkpoint":
                state["checkpoints"][actor] = value
            state["passes"] = 0
        elif operation in ("declare", "declare_attribute"):
            if actor in state["pending"]:
                raise ValueError("roll the already declared die first")
            if operation == "declare_attribute":
                from sheets import attribute_declaration, read
                if "sides" in request or "modifier" in request:
                    raise ValueError("the attribute's die and bonus come from your sheet; do not supply them")
                sheet = read(self.db, actor, password, self.observer.name)
                intent = attribute_declaration(sheet, request.get("attribute"), request.get("aspect_index"),
                                               request.get("aspect_source", "personal"), request.get("aspect_reason"),
                                               state["group"]["group_aspects"])
                magnitude = request.get("magnitude")
                if not isinstance(magnitude, str) or magnitude.capitalize() not in MAGNITUDES:
                    raise ValueError("supply the agreed magnitude: Small, Medium, Large or Huge")
                intent["magnitude"] = magnitude.capitalize()
            else:
                kind, sides = request.get("kind"), request.get("sides")
                if kind not in ("selection", "luck"):
                    raise ValueError("use declare_attribute.py for attribute challenges; declare.py requires kind selection or luck")
                if type(sides) is not int or sides not in DICE or "modifier" in request:
                    raise ValueError("select a supported die; selection and Luck rolls have no bonus modifier")
                if kind == "luck":
                    from sheets import read
                    sheet = read(self.db, actor, password, self.observer.name)
                    if sides != 20 or sheet["resources"]["luck_spent"] or sheet["resources"]["out_of_luck"]:
                        raise ValueError("Luck requires an available d20 and a character who is not Out of Luck")
                intent = {"kind": kind, "sides": sides, "modifier": 0}
            intent["purpose"] = self.text(request, "purpose")
            event_id = self.append(actor, "declare", intent)
            state["pending"][actor] = {**intent, "intent_id": event_id}
            return {"ok": True, "event_id": event_id, "declaration": intent,
                    "next_command": f"d{intent['sides']}.py"}
        elif operation == "roll":
            intent = state["pending"].get(actor)
            if intent is None:
                raise ValueError("declare your attribute or random selection before rolling")
            if request.get("sides") != intent["sides"]:
                raise ValueError(f"the pending declaration requires d{intent['sides']}.py; no die was rolled")
            if intent.get("kind") == "attribute":
                from sheets import read
                if intent.get("magnitude") not in MAGNITUDES:
                    raise ValueError("this older declaration lacks a target magnitude; ask the operator before rolling")
                assignment = read(self.db, actor, password, self.observer.name)["attributes"][intent["attribute"]]
                if assignment["die"] != intent["sides"] or assignment["bonus"] != intent["permanent_bonus"]:
                    raise ValueError("attribute assignment changed after declaration; ask the operator to resolve the pending declaration before rolling")
            result = {**intent, "result": secrets.randbelow(intent["sides"]) + 1}
            result["total"] = result["result"] + result["modifier"]
            if intent.get("kind") == "attribute":
                lower, upper = MAGNITUDES[intent["magnitude"]]
                result["success"] = lower <= abs(result["total"]) <= upper
            elif intent.get("kind") == "luck":
                result["success"] = result["result"] >= 11
            event_id = self.append(actor, "roll", result)
            del state["pending"][actor]
        elif operation in ("end_turn", "pass", "finish"):
            if actor in state["pending"]:
                raise ValueError("a declared roll must be resolved before ending the turn")
            if operation == "finish":
                if state["bid_round"]:
                    raise ValueError("finish the open bid before ending the session")
                if actor not in state["finish_votes"]:
                    state["finish_votes"].append(actor)
                event_id = self.append(actor, "finish_vote", {"text": self.text(request)})
                if len(state["finish_votes"]) == len(PLAYERS):
                    state["complete"] = True
                    self.append("System", "complete", {"text": "All players agreed to end this single session."})
            else:
                event_id = self.append(actor, operation, {})
            self.advance(state, operation == "pass")
        elif operation == "open_bid":
            name = self.text(request, "round")
            if len(name) > 100 or state["bid_round"] or name in state["used_rounds"]:
                raise ValueError("bid round must be unique and no other round may be open")
            state["bid_round"] = name
            state["used_rounds"].append(name)
            event_id = self.append(actor, "bid_opened", {"round": name, "text": self.text(request, "purpose")})
        elif operation == "bid":
            amount = request.get("amount")
            if not state["bid_round"] or request.get("round") != state["bid_round"]:
                raise ValueError("no matching open bid round")
            if actor in state["bids"] or type(amount) is not int or amount < 0 or amount > 1000000:
                raise ValueError("one nonnegative integer bid per player per round")
            state["bids"][actor] = amount
            event_id = self.append(actor, "bid_submitted", {"round": state["bid_round"]})
            if len(state["bids"]) == len(PLAYERS):
                reveal = {"round": state["bid_round"], "bids": state["bids"]}
                reveal_id = self.append("System", "bid_revealed", reveal)
                state["last_bid_reveal"] = {**reveal, "event_id": reveal_id}
                state["bid_round"], state["bids"] = None, {}
        else:
            raise ValueError("unsupported operation")
        return {"ok": True, "event_id": event_id}

    def handle(self, actor, request, password=None):
        """Provide idempotent transactions and condition-based event notifications."""
        with self.condition:
            try:
                if not isinstance(request, dict) or actor not in PLAYERS:
                    raise ValueError("invalid request")
                if actor in self.state()["disqualified"]:
                    raise ValueError("player has been disqualified")
                operation = request.get("op")
                allowed = {"op", "id", "turn", "after", "timeout", "text", "purpose", "sides", "modifier", "round", "amount",
                           "section", "changes", "expected_version", "director", "reason", "character",
                           "kind", "attribute", "aspect_index", "aspect_source", "aspect_reason", "number", "name", "title", "magnitude"}
                if set(request) - allowed:
                    raise ValueError("unknown fields (identity and results are server-owned)")
                if operation == "sheet_read":
                    from sheets import read
                    sheet = read(self.db, actor, password, self.observer.name)
                    ranges = {name: ([value["bonus"] + 1, value["bonus"] + value["die"]]
                                     if value["die"] is not None else None)
                              for name, value in sheet["attributes"].items()}
                    return {"ok": True, "sheet": sheet, "calculated_ranges": ranges}
                if operation == "group_read":
                    return {"ok": True, "group": self.state()["group"]}
                if operation in ("read", "wait"):
                    after = request.get("after", 0)
                    timeout = request.get("timeout", 45) if operation == "wait" else 0
                    if type(after) is not int or after < 0 or type(timeout) is not int or not 0 <= timeout <= 45:
                        raise ValueError("invalid cursor or timeout")
                    deadline = time.monotonic() + timeout
                    while not self.events(after) and time.monotonic() < deadline and not self.closing:
                        self.condition.wait(deadline - time.monotonic())
                    events = self.events(after)
                    return {"ok": True, "events": events, "cursor": events[-1]["id"] if events else after,
                            "status": self.public_state(self.state()), "you": actor}
                request_id = request.get("id")
                if not isinstance(request_id, str) or not 1 <= len(request_id) <= 100:
                    raise ValueError("a unique request id is required")
                # Private sheet patches must not leak into the idempotency table.
                payload = hashlib.sha256(json.dumps(request, sort_keys=True).encode("utf-8")).hexdigest()
                cached = self.db.execute("SELECT payload,response FROM requests WHERE actor=? AND request_id=?", (actor, request_id)).fetchone()
                if cached:
                    if cached["payload"] != payload:
                        raise ValueError("request id reused with different content")
                    return json.loads(cached["response"])
                with self.db:
                    state = self.state()
                    response = self.mutate(actor, request, state, password)
                    self.save(state)
                    self.db.execute("INSERT INTO requests VALUES (?,?,?,?)", (actor, request_id, payload, json.dumps(response)))
                self.export()
                self.condition.notify_all()
                return response
            except (ValueError, TypeError, KeyError) as error:
                return {"ok": False, "error": str(error)}

    def notice(self, text, resume=False):
        """Allow only the host operator to record a pause, resume or failure."""
        with self.condition, self.db:
            state = self.state()
            if state["complete"]:
                raise ValueError("completed sessions cannot resume")
            if resume and state["disqualified"]:
                raise ValueError("a session with a disqualified player cannot resume")
            state["paused"] = not resume
            state["passes"] = 0
            self.save(state)
            self.append("System", "operator", {"text": text})
        with self.condition:
            self.export()
            self.condition.notify_all()

    def disqualify(self, actor, reason):
        """Record the operator's observed violation and stop that player's access."""
        if actor not in PLAYERS or not reason.strip():
            raise ValueError("identify a player and a reason")
        with self.condition, self.db:
            state = self.state()
            if actor not in state["disqualified"]:
                state["disqualified"].append(actor)
            state["paused"] = True
            self.save(state)
            self.append("System", "disqualified", {"text": f"{actor} is disqualified: {reason}"})
        self.export()

    def authenticated(self, actor, request):
        """Strip credentials before dispatch so no password reaches journal storage."""
        if not isinstance(request, dict):
            return {"ok": False, "error": "invalid request"}
        request = dict(request)
        password = request.pop("password", None)
        if not verify_password(password, self.credentials[actor]):
            return {"ok": False, "error": "authentication failed"}
        # Prevent accidental disclosure of this player's credential in public text.
        if any(password in value for value in request.values() if isinstance(value, str)):
            return {"ok": False, "error": "never publish your password"}
        if password in json.dumps(request, ensure_ascii=False):
            return {"ok": False, "error": "never publish your password"}
        return self.handle(actor, request, password)

    def start(self):
        """Give each player a password-protected socket with a fixed identity."""
        broker = self
        for actor in PLAYERS:
            directory = self.directory / "ports" / actor
            directory.mkdir(parents=True, exist_ok=True)
            path = directory / "rpc.sock"
            if len(os.fsencode(path)) > 103:
                raise ValueError("session path is too long for Unix sockets; use a shorter session name/path")
            if path.exists():
                path.unlink()

            class Handler(socketserver.StreamRequestHandler):
                """Read exactly one bounded JSON request from a player socket."""

                def handle(self):
                    """Reject oversized frames before decoding them."""
                    self.connection.settimeout(55)
                    try:
                        line = self.rfile.readline(MAX_REQUEST + 1)
                        if len(line) > MAX_REQUEST:
                            raise ValueError("request too large")
                        response = broker.authenticated(self.server.actor, json.loads(line))
                    except (ValueError, UnicodeError, TimeoutError) as error:
                        response = {"ok": False, "error": str(error)}
                    try:
                        self.wfile.write((json.dumps(response) + "\n").encode("utf-8"))
                    except (BrokenPipeError, ConnectionResetError):
                        pass  # A retry with the same request id returns the committed result.

            server = socketserver.ThreadingUnixStreamServer(str(path), Handler)
            server.daemon_threads = True
            server.actor = actor
            path.chmod(0o600)
            self.servers.append(server)
            threading.Thread(target=server.serve_forever, daemon=True).start()

    def close(self):
        """Stop socket workers before closing shared storage."""
        with self.condition:
            self.closing = True
            self.condition.notify_all()
        for server in self.servers:
            server.shutdown()
            server.server_close()
        self.db.close()
