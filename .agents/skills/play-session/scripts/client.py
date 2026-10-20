#!/usr/bin/env python3
"""Call a player's authenticated broker endpoint without direct journal access.

This file is part of Dichotomy.
This work is licensed under CC BY-NC-ND 4.0.
License: https://raw.githubusercontent.com/SteffenBlake/Dichotomy/refs/heads/main/LICENSE
"""

import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import uuid
import re


def request(payload):
    """Retry identical requests so a lost reply cannot duplicate a dice roll."""
    password = os.environ.get("INTEROP_PASSWORD")
    if not password:
        raise ValueError("set your private INTEROP_PASSWORD for every command; never share it")
    payload = {**payload, "password": password}
    wire = (json.dumps(payload) + "\n").encode("utf-8")
    for _ in range(3):
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
                connection.settimeout(55)
                connection.connect(os.environ["INTEROP_SOCKET"])
                connection.sendall(wire)
                with connection.makefile("rb") as reader:
                    response = json.loads(reader.readline())
            if not response.get("ok"):
                raise ValueError(response.get("error", "broker rejected request"))
            return response
        except (OSError, json.JSONDecodeError):
            pass
    raise RuntimeError("broker unavailable; ask the operator to restore transport; do not invent a result")


def run(operation, sides=None, player=None):
    """Hand the public command to its generated, password-checking session endpoint."""
    try:
        if len(sys.argv) != 3:
            raise ValueError("usage: command.py PASSWORD SESSION_ID; supply messages or JSON on stdin")
        password, session_id = sys.argv[1:]
        player = player or os.environ.get("INTEROP_PLAYER")
        if player not in ("Spike", "Johnny", "Timmy") or not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,23}", session_id):
            raise ValueError("invalid player or session ID")
        endpoint = Path("/tmp/dichotomy-sessions") / session_id / player / "interop.py"
        if not endpoint.is_file():
            raise ValueError("session endpoint unavailable; ask the operator")
        command = [sys.executable, str(endpoint), password, session_id, operation]
        if sides is not None:
            command.append(str(sides))
        raise SystemExit(subprocess.call(command))
    except (ValueError, OSError) as error:
        print(f"Interop error: {error}", file=sys.stderr)
        raise SystemExit(1) from error


def execute(operation, sides, password, socket_path, cursor_path):
    """Run only after the generated endpoint validates its baked-in password hash."""
    os.environ["INTEROP_PASSWORD"] = password
    os.environ["INTEROP_SOCKET"] = socket_path
    os.environ["INTEROP_CURSOR"] = cursor_path
    try:
        cursor_file = Path(os.environ["INTEROP_CURSOR"])
        if operation in ("sheet_read", "group_read"):
            response = request({"op": operation})
        elif operation in ("token", "director", "bids"):
            status = request({"op": "read", "after": 2147483647})["status"]
            fields = ("bid_round", "submitted", "last_bid_reveal") if operation == "bids" else ("speaker", "director", "turn_number", "paused", "complete")
            response = {"ok": True, **{field: status[field] for field in fields}}
        elif operation in ("read", "wait"):
            after = json.loads(cursor_file.read_text(encoding="utf-8")) if cursor_file.exists() else 0
            response = request({"op": operation, "after": after})
            cursor_file.write_text(json.dumps(response["cursor"]), encoding="utf-8")
        else:
            payload = {"op": operation, "id": str(uuid.uuid4())}
            if operation in ("say", "checkpoint", "finish", "feature_request", "feedback"):
                payload["text"] = sys.stdin.read(24001)
            elif operation in ("declare", "declare_attribute", "open_bid", "bid", "set_director", "group_update", "start_chapter", "start_challenge", "action") or operation.startswith("sheet_"):
                data = json.loads(sys.stdin.read(65537))
                keys = {"declare": {"kind", "sides", "purpose"},
                        "declare_attribute": {"attribute", "magnitude", "purpose", "aspect_index", "aspect_source", "aspect_reason"},
                        "open_bid": {"round", "purpose"}, "bid": {"round", "amount"},
                        "set_director": {"director", "reason"},
                        "start_chapter": {"number", "name"}, "start_challenge": {"number", "name"},
                        "action": {"title", "text"},
                        "sheet_create": {"character"}}.get(operation, {"changes", "expected_version"})
                if not isinstance(data, dict) or set(data) - keys:
                    raise ValueError("unexpected input fields")
                payload.update(data)
                if operation.startswith("sheet_") and operation != "sheet_create":
                    payload["op"] = "sheet_update"
                    payload["section"] = operation.removeprefix("sheet_")
            elif operation == "roll":
                payload["sides"] = sides
            status = request({"op": "read", "after": 2147483647})["status"]
            payload["turn"] = status["turn_number"]
            response = request(payload)
            # The roll is already durable before the player receives its value.
            if operation == "roll":
                response["recorded_event"] = request({"op": "read", "after": response["event_id"] - 1})["events"][0]
        print(json.dumps(response, ensure_ascii=False, indent=2))
    except (ValueError, OSError, RuntimeError) as error:
        print(f"Interop error: {error}", file=sys.stderr)
        raise SystemExit(1) from error
