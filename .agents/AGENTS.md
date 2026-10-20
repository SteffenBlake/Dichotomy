# Dichotomy simulation framework

For the supervising operator, read `skills/run-session/SKILL.md` before creating
or running a session. For an assigned player, read `skills/play-session/SKILL.md`,
including its character-tracking reference when maintaining player/group records.
System scripts live in `skills/run-session/scripts/`; player scripts live in
`skills/play-session/scripts/`. Do not add top-level scripts or extra skills for
individual player features.

Players must execute only their supplied player commands. Reading/editing Python
implementation scripts, discovering storage or hashes, inspecting another player's
files, sharing passwords, or impersonation results in disqualification. These
restrictions apply to players; the operator may maintain and test the framework.

All live files belong in `/tmp/dichotomy-sessions/<session-id>/`. Keep only the
framework, examples and session skeleton in the repository. Do not start real
players while testing or modifying the framework.
