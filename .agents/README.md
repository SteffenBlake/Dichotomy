# Dichotomy player sessions

A local system for three independent player agents: **Spike**, **Johnny**, and
**Timmy**. Each reads the rules, invents a personality, and plays one session.
The supervising agent delivers speaking turns without making gameplay decisions.
No Docker, external service or model API setup is needed. Character sheets use the cryptography package for authenticated encryption.

There are two skills:

- [run-session](skills/run-session/SKILL.md): system/operator scripts and session management.
- [play-session](skills/play-session/SKILL.md): all player commands, with character tracking as a reference.

```text
.agents/
  skills/
    run-session/
      SKILL.md
      requirements.txt
      scripts/                 # Creation, broker, encryption, rendering and management
    play-session/
      SKILL.md
      scripts/
        client.py
        Spike/                 # Spike's authenticated commands
        Johnny/                # Johnny's authenticated commands
        Timmy/                 # Timmy's authenticated commands
      references/              # Character tracking and transcript example
  sessions/skeleton/           # Tracked session configuration and instructions
```

## Create a session

Create a Python environment outside the repository and install the one runtime dependency:

```sh
python3 -m venv /tmp/dichotomy-framework-env
/tmp/dichotomy-framework-env/bin/python -m pip install -r .agents/skills/run-session/requirements.txt
source /tmp/dichotomy-framework-env/bin/activate
```

From the repository root, run:

```sh
python3 .agents/skills/run-session/scripts/create-session.py session-001
```

Supply a JSON object on stdin containing three distinct passwords, with keys
`Spike`, `Johnny`, and `Timmy`. Generate real passwords with Python's
`secrets.token_urlsafe(24)` and retain them privately in the supervisor's context.
Avoid putting real passwords in examples or saved files. The creation script does
not print or save plaintext passwords. It rejects invalid IDs and refuses to
overwrite any existing session, including concurrent creation attempts.

All live files are under `/tmp/dichotomy-sessions/session-001/`. Each player's
`interop.py` has its own hard-coded salted scrypt verifier. The broker stores
verifiers too and independently checks every request, including reads. The
operator skill describes the private locations; players must not inspect them.
The repository holds only the framework, examples, and `sessions/skeleton/`.
That skeleton is tracked; any real session accidentally placed alongside it is
ignored. No real session data or credentials belong in this repository.

## Start transport and watch

The supervisor starts this command in a background tool session:

```sh
python3 .agents/skills/run-session/scripts/session.py serve session-001
```

It handles requests and updates the transcript immediately. No separate monitor
is necessary. You can watch it with:

```sh
tail -F /tmp/dichotomy-sessions/session-001/transcript.md
```

`status.md` shows the current speaker, completion/pause status and the players'
latest checkpoint reports. `events.jsonl` also includes silent passes and turn
endings. `journal.sqlite3` in the operator area is authoritative; the broker
reconstructs observer files after a restart. All timestamps include their UTC
offset in the detailed event history. `/tmp` is temporary; preserve a transcript
elsewhere yourself if desired.

The story transcript uses `# Prologue`, `# Chapter N: Name`, `## Challenge N: Name`
and `### Player — Action`.
Speaker headings include the character name once created, or `(director)` while
that player is directing. Historical headings use the role/name known then.
Completed dice rolls are a single line, including stat, die/face, signed bonus
(`†` for inversion), total,
and ✅/❌ (or 🎲 for a random selection). All system-generated transcript messages
are italicized with `*…*`. Internal sheet updates, group bookkeeping, checkpoints,
declarations and transport details stay
in `events.jsonl` and the status view, rather than interrupting the story.
Feedback and feature requests also have their own logs. To regenerate a stopped
session's observer files from its journal after a formatting change:

```sh
python3 .agents/skills/run-session/scripts/session.py rebuild-logs session-001
```

Creating a session or starting transport does not start players or consume model
quota. The operator explicitly launches three `gpt-6-luna` agents with fresh,
separate contexts and supplies each its own brief and password. Obtain a brief:

```sh
python3 .agents/skills/run-session/scripts/session.py brief session-001 Spike
```

Activate Spike first, then Johnny, then Timmy. On subsequent turns the supervisor
resumes the same player's conversation with a neutral instruction to read new
events and contribute. The agent chooses what to say or do. Speaking order does
not assign narrative authority in the game.

## Player commands

Each player has its own commands under `.agents/skills/play-session/scripts/<name>/`. Every command
requires exactly **PASSWORD SESSION_ID** as its two arguments. Messages and JSON
payloads go through stdin. A public launcher hands off to the generated endpoint
at `/tmp/dichotomy-sessions/<id>/<player>/interop.py` without revealing its source.
The endpoint checks its baked-in hash, then invokes the authenticated broker.

Example shape only—never use these placeholder credentials in a real game:

```sh
python3 .agents/skills/play-session/scripts/Spike/read.py 'YOUR_PASSWORD' 'session-001'
python3 .agents/skills/play-session/scripts/Spike/d8.py 'YOUR_PASSWORD' 'session-001'
```

- `read.py`: unread public events and current status, using a private cursor.
- `say.py`: arbitrary player prose on stdin, labeled by authenticated author.
- `start_chapter.py`, `start_challenge.py`: agreed numbered/named story boundaries.
- `action.py`: a specific action/narration with `title` and `text` on JSON stdin.
- `declare_attribute.py`: choose an attribute and purpose; the broker derives
  its actual die/bonus from your encrypted sheet and confirms the next die script.
  Optional Aspect selection derives the inverted bonus.
- `declare.py`: `kind` (`selection` or `luck`), `sides`, and `purpose`; no modifier.
- `d4.py`, `d6.py`, `d8.py`, `d10.py`, `d12.py`, `d20.py`: fixed rolls, requiring
  a matching declaration. A wrong die is rejected without rolling. No result,
  seed, count or extra dice arguments accepted.
- `end_turn.py`, `pass.py`: yield or pass; passes add no dialogue to the transcript.
- `wait.py`: optional notification wait, up to 45 seconds; normal play uses turns.
- `open_bid.py`, `bid.py`: public round opening and sealed integer submissions.
- `checkpoint.py`: a player's readable report for the live status view.
- `finish.py`: completion vote with reason on stdin; all three must vote.

Dice use OS randomness through `secrets.randbelow`. The broker records each face
before returning it; only it creates typed roll events. Retries use a request ID
so a lost reply cannot cause a second roll. Players interpret modifiers, account
for resources, resolve rules, and agree fair mappings for all random selections.
Sealed bids reveal together only after all three submit; the service does not
choose a winner or spend game resources.

## Pauses and violations

Three consecutive passes or the configured speaking-turn budget pauses the
session. Ctrl-C also records a pause. Inspect status, stop the old broker if
necessary, and restart with a procedural note:

```sh
python3 .agents/skills/run-session/scripts/session.py serve session-001 --resume 'Transport restored; continue your discussion.'
```

The budget and suggested session scope are copied from `sessions/skeleton/` into
the operator's live configuration. A single host lock prevents duplicate brokers.
The supervisor stops transport after completion and links the transcript/status.

Players are explicitly forbidden from reading or editing implementation scripts,
discovering storage or password hashes, inspecting each other's files, sharing
passwords, or impersonating each other. Violations mean disqualification. The
operator records an observed violation after stopping transport:

```sh
python3 .agents/skills/run-session/scripts/session.py disqualify session-001 Spike 'observed rule violation'
```

That player's future requests are denied and the session stays paused. Detection
is a conduct rule supervised by the operator, not a filesystem sandbox. These are
modest safeguards against accidents: cooperating agents still share a host user.
Authentication verifies who posted; prose cannot prove somebody else agreed.
Every player's text is labeled by its authenticated author. Corrections are
appended as new messages, not edits to history. The story transcript is a readable
projection; the detailed, immutable event history remains available to the agents.


## Character sheets and playtest logs

Each character sheet is encrypted using AES-256-GCM and a separate salted scrypt
key derived from that player's password. Encrypted revisions stay in the session
database; plaintext is returned only through the authenticated read command.
Section-specific update commands require the latest version, so a stale patch
cannot overwrite a newer revision. The idempotency table stores request hashes,
not plaintext character patches. The full rulebook's personal fields and a public
Saga/Volume/Chapter ledger are covered by the tracking skill.

`sheet_create.py` creates the complete starting character in one command and one
encrypted revision; see the tracking skill for its JSON input. It refuses an
already edited character sheet. `sheet_read.py` reads a character sheet.
Later updates are `sheet_identity.py`,
`sheet_attributes.py`, `sheet_resources.py`, `sheet_aspects.py`, `sheet_threads.py`,
`sheet_calamities.py`, and `sheet_notes.py`. `group_read.py` and `group_update.py`
track the shared Saga sheet. All take the same password and session ID arguments.
`token.py` / `director.py` distinguish the speaking token from the current Chapter
Director. `set_director.py` records the group-agreed Director. `bids.py` reads the
open blind bid and latest reveal, complementing `open_bid.py` and `bid.py`.

Players must actively use `feedback.py` for constructive criticism of the game,
and `feature_request.py` for requests for additional scripts. Both take text on
stdin and the usual two credential/session arguments. They can log at any time,
including outside their speaking turn, without moving the token. Feedback is an
explicit goal of this playtest. These are local logs, not external messages.

Separate live files are `creator-feedback.md` and `feature-requests.md` beside the
session transcript. The broker updates them as events arrive and reconstructs
them after restart. To open the transcript and creator feedback together in the
current VS Code window:

```sh
python3 .agents/skills/run-session/scripts/session.py open-logs session-001
```

This uses the `code` (or `code-insiders`) command on PATH. The supervisor opens
the files and links them to the user after creation. No test suite is included;
the player agents will exercise the tools during play.

Encryption reference: [cryptography authenticated encryption documentation](https://cryptography.io/en/latest/hazmat/primitives/aead/).
