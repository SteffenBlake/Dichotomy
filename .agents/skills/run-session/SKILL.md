---
name: run-session
description: Bootstrap and supervise three independent Dichotomy player agents with private passwords, a live /tmp transcript, and mechanical speaking-turn delivery. Use for the operator creating or running a simulation, not for a player.
---

# Operator: create and supervise a session

Keep gameplay decisions with the players. This framework uses local scripts and
modest accident safeguards, not containers or an adversarial security boundary.
Never give player agents source code, hashes, storage locations or other players'
private credentials. Player rules prohibit discovering them, with disqualification
for a violation. Ordinary prose is labeled by authenticated author; it cannot
prove another player agreed to its claims.

## Bootstrap

Use a Python environment with `.agents/skills/run-session/requirements.txt` installed. For example,
create `/tmp/dichotomy-framework-env` with `python3 -m venv`, install the listed
dependency there, and use that environment's Python for creation and serving.
The character sheets use password-derived scrypt keys and AES-GCM encrypted
revisions. Read the complete game rules before maintaining tracking tools.

1. Choose a session ID using 1–24 lowercase letters, digits or hyphens. Generate
   three distinct high-entropy passwords using CLI `secrets.token_urlsafe(24)`.
   Supply a JSON object keyed `Spike`, `Johnny`, `Timmy` through stdin to:

   ```sh
   python3 .agents/skills/run-session/scripts/create-session.py SESSION_ID
   ```

   Keep the passwords in your private operator context and send each only to its
   assigned player. Never put plaintext passwords in repository files, transcript,
   launch examples, or shared agent context. The creator stores salted scrypt
   verifiers only; it refuses an existing session directory without modifying it.
2. Everything live is generated under `/tmp/dichotomy-sessions/SESSION_ID/`.
   Each `<player>/interop.py` has that player's salted verifier baked into it.
   The tracked `.agents/skills/play-session/scripts/<player>/*.py` commands hand off there. The broker
   checks credentials again, fixes author identity and serializes journal writes.
3. Link the user directly to `/tmp/dichotomy-sessions/SESSION_ID/transcript.md`
   once it exists. The observer can use `tail -F` on it. `status.md` is a readable
   current checkpoint; `events.jsonl` includes silent passes and turn endings.
   Do not copy live data back into the repository. `/tmp` persistence is temporary.

Creating the files does not authorize starting gameplay if the user only asked
for setup. When asked to play, continue with the following steps.

## Start transport and independent players

Start the broker yourself in a background execution session:

```sh
python3 .agents/skills/run-session/scripts/session.py serve SESSION_ID
```

It updates transcript/status immediately after every accepted event. There is no
separate monitoring process to maintain. Verify the Ready output before players
invoke tools. Keep its execution handle for shutdown; do not leave a forgotten
broker after completion or failure.

Obtain each launch brief using:

```sh
python3 .agents/skills/run-session/scripts/session.py brief SESSION_ID Spike
```

Spawn three independent player agents, named **Spike**, **Johnny**, **Timmy**, using
`model="gpt-6-luna"` and `fork_turns="none"`. Supply only that player's brief and
password. Do not fork the supervisor's conversation: it contains all passwords.
This is explicitly authorized delegation when the user asks to run the session.
There are three player slots plus the supervising operator.

The brief gives rules/skill/example locations and the correct command folder.
Each agent reads the rules independently and invents a personality motivated by:

- Spike: mastery and effective decisions.
- Johnny: creative expression and clever combinations.
- Timmy: memorable shared experiences and dramatic moments.

New sessions give each player a distinct priority to advocate for. Encourage
reasoned pushback, alternatives, negotiation and bidding when their interests
conflict; do not reward blanket agreement or require artificial disputes.
Creation snapshots the session instructions and motivations so changes intended
for the next session do not rewrite an existing group's brief.

## Deliver speaking turns

Activate Spike first, then Johnny, then Timmy. Agents can be spawned on their
first speaking turn and retained for the rest of the session. After each yields,
read `status` and mechanically activate the named next speaker. Resume that same
agent's conversation with `followup_task`; do not create a replacement player.
A suitable neutral message is: "Your speaking turn. Read new events, decide your
own contribution, then explicitly yield or pass and end your response."

```sh
python3 .agents/skills/run-session/scripts/session.py status SESSION_ID
```

Players see each other's public events through `read.py` and their private
cursors. Do not summarize, reinterpret or insert gameplay suggestions. A player's
final response to you is not public table dialogue; only script-posted events
are shared. If it forgets to yield, remind only that player to use a yield command.

Three consecutive passes or the configured speaking-turn limit pauses the
session, without choosing a game outcome. Inspect the procedural problem and
resume transport with `serve SESSION_ID --resume 'procedural note'` if appropriate.
Do not silently discard actions or reroll when recovering from a technical fault.
Completion requires all three player votes; do not start a second session.

## Violations and shutdown

If a player reads/edits implementation scripts, shares credentials or impersonates
another player, stop transport and record the violation:

```sh
python3 .agents/skills/run-session/scripts/session.py disqualify SESSION_ID Spike 'observed violation'
```

That player's commands are then denied and the session stays paused. Do not claim
automatic detection: the operator enforces the conduct rule when a violation is
observed. No game decisions are made as part of this enforcement.

Stop the broker when done. Tell the user whether the session completed or paused,
and link the transcript and status. Do not expose private passwords or raw hashes.

## Live feedback and feature requests

The purpose is to playtest the game for its creator. Ensure each player's brief
includes the player tracking reference and instructions to use `feedback.py` actively during
play, plus a final retrospective. `feature_request.py` logs desired additional
scripts for later; do not steer their gameplay to manufacture observations.

The broker updates `creator-feedback.md` and `feature-requests.md` beside the
transcript on every accepted report. Reports can be submitted outside speaking
turns without moving the token. Link all logs to the user when they exist.
To open the transcript and creator feedback in VS Code yourself, run:

```sh
python3 .agents/skills/run-session/scripts/session.py open-logs SESSION_ID
```

Use the host VS Code `code` command; no additional monitoring process is needed.
These reports are local session logs, not external messages to anybody.

## Observer transcript

The human transcript uses `# Prologue`, numbered/named `# Chapter` sections,
`## Challenge` sections and `### Player — Action` entries. Players name sections
with start_chapter.py/start_challenge.py and actions with action.py. A completed
roll appears once, on one line. Do not add bookkeeping dumps to the story view;
the agents retain their full declarations, counters, checkpoints and event IDs.

After updating formatting, regenerate a stopped session with
`python3 .agents/skills/run-session/scripts/session.py rebuild-logs SESSION_ID`. This only rebuilds observer
files; it does not advance the game or change recorded rolls. Legacy journals use
their recorded counter transitions and notes to recover section boundaries.
