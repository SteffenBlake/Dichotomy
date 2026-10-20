This hand-written example demonstrates formatting only. Its die result is
illustrative, not a recorded roll, and must never be used during actual play.

# Prologue

### Spike

I like plans with consequences. I'd like our story to revolve around restoring
an abandoned observatory, with a clear stopping point we agree together.

### Johnny

I want the machinery to matter to a personal mystery. I'll advocate for an
inventive approach, even if it makes the straightforward repair less attractive.

### Timmy

I want someone we care about to need that telescope working tonight. Let's
choose the stakes and boundaries before we make characters.

# Chapter 1: The silent observatory

*Chapter Director: Timmy.*

## Challenge 1: Reopen the dome

### Johnny (Elias Venn) — Free the mechanism

I wedge the frozen gear and use a careful, steady pull to free the telescope's
housing. I'll use Vigor for the approach we agreed.

*Johnny · Vigor: d8(6) -3 → 3 ✅*

### Timmy (director) — The dome opens

The housing shifts, and moonlight cuts across the floor. Something has been
scratched into the glass from the inside.

---

**Tool sequence, for illustration:**

The current speaker invokes `start_chapter.py` with
`{"number":1,"name":"The silent observatory"}`. The Director invokes
`start_challenge.py` with `{"number":1,"name":"Reopen the dome"}`.

A player invokes `action.py` with a title and their narration on stdin. For this
illustration only, assume Vigor was assigned d8 with a permanent bonus of -3.
The player invokes `declare_attribute.py` with
`{"attribute":"Vigor","magnitude":"Small","purpose":"Free the mechanism for the agreed challenge."}`,
reads its confirmation and invokes the returned die command:

```sh
python3 .agents/skills/play-session/scripts/Johnny/d8.py 'YOUR_PASSWORD' 'SESSION_ID'
```

These are placeholders. Real passwords must never be posted to the table.
The broker generates and logs the face. Its declaration/result pair appears as
one line in the story transcript after the roll. Players narrate consequences;
the broker does not choose them.

Detailed declarations, event IDs, timestamps, sheet/group updates, checkpoints,
turn endings and silent passes remain in `events.jsonl` for the agents.
Feedback and feature requests have separate logs. Blind bid values stay hidden
until all three submissions arrive, then a compact reveal appears in the story.
