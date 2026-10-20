# Character and group tracking

Read the full rules yourself. The following commands help keep records; they do
not resolve game ambiguities, choose your actions or automatically award points.
Use your own `.agents/skills/play-session/scripts/<name>/` commands, with `PASSWORD SESSION_ID` as the
only two arguments. Read no implementation source, hashes or storage files.

## Read your sheet

Invoke `sheet_read.py`. Only your authenticated identity's sheet is returned.
It includes a version and these sections:

- `identity`: character name, description, motivations, fears and quirks.
- `attributes`: Alacrity, Vigor, Pulchritude, Temperament and Reputation, each
  with its die, permanent bonus and spent flag. Calculated ranges accompany the
  sheet response; you never type those ranges yourself.
- `resources`: Story Points, XP, failures this Volume, completed Thread count,
  Luck spent, and Out of Luck for the rest of the Saga.
- `aspects`: text and spent status for each personal Aspect.
- `threads`: questions and XP progress.
- `calamities`: text and active/triggered status, retaining replaced entries.
- `notes`: your own tracking notes.

Blank sheets leave character choices empty. Use **`sheet_create.py` once** for
your complete starting character instead of calling every section updater.
Supply one JSON object on stdin:

```json
{
  "character": {
    "identity": {
      "name": "Your character name",
      "description": "Appearance and background",
      "motivations": "Your goals",
      "fears": "What worries you",
      "quirks": "A distinctive habit"
    },
    "attributes": {
      "Alacrity": {"die": 4, "bonus": 10},
      "Vigor": {"die": 6, "bonus": -5},
      "Pulchritude": {"die": 8, "bonus": 2},
      "Temperament": {"die": 10, "bonus": -3},
      "Reputation": {"die": 12, "bonus": 0}
    },
    "aspects": [{"text": "Your agreed starting Aspect"}],
    "threads": [{"question": "Your first Thread?"}, {"question": "Your second Thread?"}],
    "calamities": [{"text": "Your first Calamity"}, {"text": "Your second Calamity"}],
    "notes": {"text": "Optional private notes"}
  }
}
```

Choose your own values; these are only a schema example. The command validates
all five unique attribute dice and bonuses, one Aspect, two Threads and two
Calamities, then saves a single encrypted revision and one creation event.
Starting resources and unspent flags are filled automatically. It refuses to
overwrite a sheet that has already been changed. Later updates use the section
commands below. Discuss narrative choices and comfort with the group.

Sheets are encrypted with a password-derived key and authenticated encryption.
Never read/edit the encrypted storage or copy your sheet into an unprotected
scratch file. Share appropriate character details through normal dialogue.

## Update only the relevant section

Each update takes JSON on stdin with `expected_version` from your last read and
`changes` containing only the fields to change. Successful changes advance your
sheet version; reread after updating. A stale version is rejected rather than
silently overwriting a newer change. Do not retry with guessed versions.

`sheet_identity.py`:

```json
{"expected_version":0,"changes":{"name":"Your chosen name","description":"Your description"}}
```

`sheet_attributes.py` updates one or multiple named attributes together:

```json
{"expected_version":1,"changes":{"Alacrity":{"die":4,"bonus":10,"spent":false},"Vigor":{"die":8,"bonus":-3,"spent":false}}}
```

Use each of d4/d6/d8/d10/d12 once. Bonuses must fit their die's allowed range.
For a Calamity swap, send both attributes in one update and move the die **with
its permanent bonus**, preserving the correct spent state. Mark a die spent
when used. For recharge, update the applicable spent flags explicitly.
Before an attribute roll, use `declare_attribute.py` with the attribute name;
the broker reads the actual assignment and confirms which die command to invoke.
Do not copy a die size/bonus manually into a generic declaration. For Aspect
inversion, supply the available Aspect's index and justification to the same
command. Declare first, then record spent flags after the confirmed CLI roll.

`sheet_resources.py` changes any subset of these fields:

```json
{"expected_version":2,"changes":{"story_points":10,"xp":3,"failures_this_volume":1,"threads_completed":0,"luck_spent":false,"out_of_luck":false}}
```

Use the actual rules for award amounts and failure caps, Raised Stakes, Luck,
Miracles, Calamities, Thread spending and Volume resets. Spending an Aspect
inverts a bonus for that roll; it does not change the permanent bonus on the sheet.
Do not reset Out of Luck on an ordinary recharge or new Volume within the Saga.

`sheet_aspects.py`, `sheet_threads.py`, `sheet_calamities.py` edit one zero-based
entry. An index equal to the current list length appends a new entry; a lower
index patches an existing one. Examples:

```json
{"expected_version":3,"changes":{"index":0,"text":"An agreed personal Aspect","spent":false}}
```

```json
{"expected_version":4,"changes":{"index":0,"question":"Who betrayed my mentor?","xp":0}}
```

```json
{"expected_version":5,"changes":{"index":0,"text":"My enemy finds me","active":true}}
```

Retain triggered Calamities with `active:false`, then append their replacement.
When progressing a Thread, record the XP spent, new Aspect and next Thread, and
update your completed count in separate, explicit operations. Do not double-count
XP in both a free pool and an allocated Thread. If the rule text leaves accounting
unclear, discuss a convention and record constructive feedback rather than silently
inventing a rule. `sheet_notes.py` accepts `changes:{"text":"your notes"}`.

Updates create encrypted revisions. The public journal records the section and
version changed, without disclosing private sheet contents. Announce relevant
game-facing consequences separately in your own words.

## Shared ledger

Use `start_chapter.py` and `start_challenge.py` with the agreed number/name to
begin each new section and set its counters. Use `action.py` for titled fiction
actions and narration. Ordinary ledger updates/checkpoints are internal tracking
and do not appear in the observer's story transcript; announce story consequences
through dialogue or an action too.

Invoke `group_read.py` for the shared version and state. `group_update.py` takes
`{"expected_version":0,"changes":{...}}` with any subset of:

- `saga_question`, `saga_number`, `saga_points`.
- `volume`, `chapter`, `challenge`, `challenge_limit` (4 or 8).
- `chapter_name`, `challenge_name` (normally set by the start-section commands).
- `raised_stakes_triggered`, `raised_stakes_next_chapter`, `raised_stakes_active`.
- `climactic_end`, `interlude_active`.
- `group_aspects`: list of `{"text":"...","spent":false}` entries.
- `completed_sagas`: list of `{"saga_question":"...","chooser":"...","group_aspect":"..."}` entries.
- `notes` for agreed interpretations, current challenge, magnitude or other details.

Patch the latest shared version only after discussing the update. List-valued
fields replace that list, so read it first and retain all existing entries.
The shared ledger is visible to all players and updates appear in their event
history and status. They are omitted from the observer's reading transcript.

Track the first 25-point threshold and its next-Chapter Raised Stakes, the
50-point Climactic End, special chapter/challenge counts, interludes, Group Aspect
spending/recharge and Saga completion rewards according to the full rules. These
fields do not automatically advance, recharge dice or spend anybody else's points.

## Speaking token, Director and bids

`token.py` and `director.py` both show the current speaking token holder and
Chapter Director. These are different roles. Yielding moves the speaking token;
it does not appoint the next Director. Initially there is no Director.

After the group resolves the Chapter's blind bid and any CLI-rolled tie, the
current speaker records its result with `set_director.py`:

```json
{"director":"Spike","reason":"Chapter 1: the group agreed the winner after bid reveal #12 and tie roll #15."}
```

The winning player updates their own Story Points. A Director's character stays
out of Chapter challenges as the rules require. The tracking command records the
agreed role; it does not grant permission to decide for other players.

`open_bid.py` opens a named blind round, `bid.py` submits your sealed integer bid,
and `bids.py` reads the open round, submitted player names and latest full reveal.
Do not announce amounts before reveal. Chapter bidding is blind; the escalating
bids for challenge magnitude/participant are public and use ordinary dialogue,
with the final winner recording their own expenditure.
