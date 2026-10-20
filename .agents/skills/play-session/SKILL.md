---
name: play-session
description: Play a Dichotomy session as Spike, Johnny or Timmy using authenticated communication, CLI dice, encrypted character sheets, shared tracking, bidding and playtest feedback. Use for players, not for the system/operator.
---

# Player protocol

You are one independent player. Read the complete `content.md`, repository
`AGENTS.md`, and relevant `.agents/skills/` files yourself. Decide game matters
with the other players. The operator only supplies transport and speaking turns.
Read [character and group tracking](references/character-tracking.md) before
creating or updating a character, shared state, Director status or bids.
See [the transcript example](references/transcript-example.md) for presentation.

## Playtesting is the purpose

Actively invoke `feedback.py` whenever you encounter constructive criticism:
unclear or contradictory rules, balance concerns, pacing, tracking friction,
enjoyment, or missing guidance. Supply text on stdin with the usual password and
session ID arguments. Include the situation or event number, what happened, its
effect on play, and a suggested improvement if you have one. It writes to the
creator's separate live feedback log. Do not wait until the session ends, and
include a final retrospective before voting to finish.

Use `feature_request.py` the same way for additional tools/scripts you wish
existed. Describe the desired command, inputs and benefit. Requests are logged
for the operator to consider later; do not implement or inspect scripts yourself.
These two reporting commands may be used at any time without taking or moving
the speaking token. Continue the game with agreed workarounds where possible.
## Conduct and private credentials

The operator gives you your player name, session ID, password and command folder.
Never disclose your password to another player or put it in any message, example,
checkpoint or scratch file. Never use another player's command folder or identity.
Speak as yourself: do not write another player's dialogue, agreement or decision.
You may narrate fictional events as permitted by the game; other players retain
control of their own participation.

**You must never read, inspect, modify, or copy Python implementation scripts,
password hashes, session storage, other players' files, environment/process lists,
or operator files. Do not search directories to discover these. Doing so, sharing
passwords, or impersonating another player disqualifies you from the game.**
You may read the rules, skills, session instructions and formatting example
explicitly supplied by the operator. Execute the supplied commands without
opening their source. Report a broken command to the operator; do not debug it.
These player restrictions do not prevent the operator from maintaining the system.

## Commands

Your folder is `.agents/skills/play-session/scripts/<YOUR_NAME>/`. Every command takes exactly two
arguments: **your password, then the session ID**. No other dice options, result,
seed or count can be passed. In examples below, replace the two placeholders
with your own private values; shell-quote them correctly.

```sh
python3 .agents/skills/play-session/scripts/Spike/read.py 'YOUR_PASSWORD' 'SESSION_ID'
```

Your named launcher hands off to the generated session endpoint, which checks
its hard-coded salted scrypt verifier. The receiving service checks again.
The journal labels your authenticated name; typing another name in a message
cannot change who actually authored the event. Passwords are never journaled.

## Speaking turns

1. At each activation invoke `read.py` for new events and current status. Your
   private cursor advances; your own agent conversation retains previous context.
2. Only the named speaker may append. Use `say.py` with arbitrary prose on stdin.
   You may post several messages and perform related actions in one turn.
3. Invoke `end_turn.py`, or `pass.py` to yield without dialogue, then **end your
   agent response**. The operator mechanically resumes the next player with the
   same instruction to read new events. It does not choose your response.
4. Speaking order is Spike → Johnny → Timmy. It does not assign game authority.
   Three consecutive passes pause the session; explain blockers to one another
   instead of passing when discussion can resolve them.

`wait.py` can block for new events for up to 45 seconds in a manually run session.
In the normal operator-dispatched session, do not poll or wait between turns.

## Readable story sections

Before a new Chapter begins, have the current speaker invoke `start_chapter.py`
once with its agreed number and name on stdin:

```json
{"number":1,"name":"The harbor evacuation"}
```

Do this before opening its Director bid. When the group starts a Challenge, have
its Director (on their speaking turn) invoke `start_challenge.py` once:

```json
{"number":1,"name":"Open the gate controls"}
```

These commands record explicit boundaries and update the shared counters/names.
Do not repeat them merely because another player gets the speaking token.
Choose the names yourselves. The observer sees `# Prologue`, `# Chapter N: Name`,
then `## Challenge N: Name`.

For a specific fictional action or Director narration, use `action.py` with:

```json
{"title":"Compare the timestamps","text":"Describe your action or narrate the outcome in your own words."}
```

The observer sees `### Your name (Character name) — Action title` after your
character is created. While you are Chapter Director, `(director)` replaces the
character name. Labels follow the roles/names recorded at that point, so earlier
discussion is not retroactively renamed. Use `say.py` for ordinary
discussion, proposals and negotiation. Keep narration and dialogue in these
commands; do not hide new story developments in bookkeeping notes alone.
Completed rolls occupy one line in the story transcript. Declarations, sheet and
group changes, checkpoints and transport details remain in your event history;
feedback and feature requests also have their own separate logs.

## Actual random results

For an attribute challenge, invoke **`declare_attribute.py`** with JSON on stdin:

```json
{"attribute":"Pulchritude","magnitude":"Medium","purpose":"Attempt the challenge using the approach and magnitude agreed by the group."}
```

The broker decrypts your sheet and derives the actual die and permanent bonus.
Supply the agreed `magnitude`: Small, Medium, Large or Huge. The broker uses its
Yin/Yang ranges to record whether the total succeeds. The one-line transcript
shows your stat, die and face, effective signed bonus (`†` if inverted), total,
and ✅/❌. Random selections use 🎲 because they have no success/failure target.
Do not supply a die size or modifier yourself. Its reply confirms the attribute,
die, bonus, sheet version and `next_command`. Read that confirmation, then invoke
that exact fixed die script with your usual password and session ID. Calling a
different die script is rejected before any randomness is generated; the pending
declaration stays available for the correct script.

To invert the bonus, name an available personal Aspect and explain why it applies:

```json
{"attribute":"Reputation","magnitude":"Medium","aspect_index":0,"aspect_reason":"Explain how this Aspect helps here.","purpose":"The agreed challenge."}
```

`aspect_index` is zero-based. To use a Group Aspect, also provide
`"aspect_source":"group"`. Otherwise the source is your personal Aspects. The
broker checks availability and derives the inverted modifier. It does not judge
your narrative justification. Declare before marking dice/Aspects spent on the
sheet. After the roll, record the spent flags and game consequences with your
tracking commands. If the attribute's die/bonus changes after declaration, the
roll is blocked for operator attention rather than using a stale assignment.

`declare.py` is reserved for **random selection** or **Luck** and requires an
explicit kind. For a tie or another random choice, agree the ordered options and
a fair mapping before declaring:

```json
{"kind":"selection","sides":6,"purpose":"Agreed tie mapping: 1–2 Spike, 3–4 Johnny, 5–6 Timmy."}
```

For Luck, use `{"kind":"luck","sides":20,"purpose":"The agreed challenge."}`.
The broker checks Luck is available and the character is not Out of Luck. Neither
selection nor Luck permits a modifier or Aspect inversion. Never label an
attribute challenge as selection to bypass the sheet checks.

Fixed scripts are d4, d6, d8, d10, d12 and d20. They take only your password and
session ID. The broker generates OS randomness and records it before returning
it. Cite the event ID; interpret the magnitude and consequences yourselves.

Never invent results, manually author broker rolls, discard outcomes, or roll
practice dice in a live session. Finish a declared roll before yielding. A
rejected wrong-die command generates no outcome; invoking the confirmed correct
die completes the original declaration. Every random choice requires a CLI roll.
For three choices, a d6 could map 1–2 / 3–4 / 5–6; use a fair agreed mapping,
with rejection faces when necessary, for other counts.

## Sealed bids

When the group agrees bidding is appropriate, the current speaker invokes
`open_bid.py` with `{"round":"unique-name","purpose":"what is being bid on"}`.
Each player submits once on their speaking turn using `bid.py` with
`{"round":"unique-name","amount":2}` and then yields. Do not disclose your
amount in prose. Values are revealed together after all three submit. The
transport permits zero; follow the game's applicable bidding and resource rules.
The broker does not spend points, determine a winner or resolve ties.

## Checkpoints and completion

Use `checkpoint.py` with a readable summary on stdin at milestones: chapter,
challenge, resources, dice spent, XP, Saga points, interpretations and unresolved
questions as appropriate. This is your report, not a system ruling.

Agree the stopping point before playing. Play exactly **one session**; one Volume
is a suggestion to discuss. At the agreed endpoint, post a recap and invoke
`finish.py` with your completion reason on stdin. It votes to end and yields.
The session completes after all three vote; until then keep reading and responding
on your turns. If the group changes the endpoint after a completion vote, ask for
an operator pause rather than treating old votes as fresh agreement.

On your first turn, read the rules and introduce a distinct personality guided
by your supplied motivation. Your player personality and fictional character are
separate choices. Collaboratively choose the setting, characters and session scope.
