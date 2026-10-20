#!/usr/bin/env python3
"""Bootstrap and supervise local Dichotomy player sessions.

This file is part of Dichotomy.
This work is licensed under CC BY-NC-ND 4.0.
License: https://raw.githubusercontent.com/SteffenBlake/Dichotomy/refs/heads/main/LICENSE
"""

import argparse
from contextlib import contextmanager
import fcntl
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

from broker import Broker, PLAYERS, create_credentials

ROOT = Path(__file__).resolve().parents[3]
SYSTEM_SCRIPTS = Path(__file__).resolve().parent
PLAYER_SKILL = ROOT / "skills" / "play-session"
REPO = ROOT.parent
SESSIONS = Path('/tmp/dichotomy-sessions')
MOTIVATIONS = {
    'Spike': 'Seek mastery and effective decisions. Defend plans that make good use of resources and pursue your Threads; question inefficient plans or unsupported difficulty claims. Invent your own distinct personality.',
    'Johnny': 'Seek creative expression and unusual solutions. Advocate for your own inventive approaches and personal Threads; push back when a safe or obvious plan sidelines what interests you. Invent your own distinct personality.',
    'Timmy': 'Seek memorable experiences and emotionally significant stakes. Advocate for bold choices and your personal aims; push back when excessive caution drains the drama or ignores what your character cares about. Invent your own distinct personality.',
}


def session_path(name):
    """Reject traversal, reserved skeleton names and oversized socket paths."""
    if not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,23}', name):
        raise ValueError('session IDs use 1–24 lowercase letters, digits or hyphens')
    return SESSIONS / name


@contextmanager
def exclusive(directory):
    """Prevent a second operator from replacing live session sockets."""
    with (directory / '.operator' / 'operator.lock').open('a', encoding='utf-8') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise ValueError('a broker already owns this session') from error
        yield


def create_session(name, passwords):
    """Create one session atomically without ever overwriting an existing one."""
    directory = session_path(name)
    try:
        import sheets
    except ModuleNotFoundError as error:
        raise ValueError('install .agents/skills/run-session/requirements.txt in your framework Python environment first') from error
    if not isinstance(passwords, dict) or set(passwords) != set(PLAYERS):
        raise ValueError('supply a JSON object with exactly Spike, Johnny and Timmy passwords')
    if any(not isinstance(value, str) or not 1 <= len(value) <= 256 for value in passwords.values()):
        raise ValueError('passwords must contain 1–256 characters')
    if len(set(passwords.values())) != len(PLAYERS):
        raise ValueError('give each player a different password')
    SESSIONS.mkdir(parents=True, exist_ok=True, mode=0o700)
    # This exclusive mkdir is the overwrite guard, including concurrent creators.
    directory.mkdir(mode=0o700)
    private = directory / '.operator'
    private.mkdir(mode=0o700)
    create_credentials(private, passwords)
    config = json.loads((ROOT / 'sessions' / 'skeleton' / 'session.json').read_text(encoding='utf-8'))
    config['motivations'] = dict(MOTIVATIONS)
    (private / 'session.json').write_text(json.dumps(config, indent=2) + '\n', encoding='utf-8')
    shutil.copyfile(ROOT / 'sessions' / 'skeleton' / 'instructions.md', directory / 'instructions.md')
    records = json.loads((private / 'auth.json').read_text(encoding='utf-8'))
    header = '''#!/usr/bin/env python3
"""Generated player endpoint. Players must never read or edit this script.

This file is part of Dichotomy.
This work is licensed under CC BY-NC-ND 4.0.
License: https://raw.githubusercontent.com/SteffenBlake/Dichotomy/refs/heads/main/LICENSE
"""
import sys
'''
    for player in PLAYERS:
        player_directory = directory / player
        player_directory.mkdir(mode=0o700)
        script = header + f'''
SESSION_ID = {name!r}
PLAYER = {player!r}
PASSWORD_RECORD = {records[player]!r}
sys.path.insert(0, {str(SYSTEM_SCRIPTS)!r})
from broker import verify_password
if len(sys.argv) not in (4, 5) or sys.argv[2] != SESSION_ID or not verify_password(sys.argv[1], PASSWORD_RECORD):
    raise SystemExit('Invalid credentials or session ID')
sys.path.insert(0, {str(PLAYER_SKILL / 'scripts')!r})
from client import execute
execute(sys.argv[3], int(sys.argv[4]) if len(sys.argv) == 5 else None,
        sys.argv[1], {str(private / 'ports' / player / 'rpc.sock')!r},
        {str(player_directory / 'cursor.json')!r})
'''
        (player_directory / 'interop.py').write_text(script, encoding='utf-8')
        (player_directory / 'interop.py').chmod(0o500)
    broker = Broker(private, directory)
    broker.seed_sheets(passwords)
    broker.close()
    return directory


def configuration(directory):
    """Load host-only player model and bounded session scope."""
    config = json.loads((directory / '.operator' / 'session.json').read_text(encoding='utf-8'))
    if config['players'] != list(PLAYERS) or type(config['max_turns']) is not int or config['max_turns'] < 1:
        raise ValueError('invalid player list or speaking-turn budget')
    return config


def brief(directory, player):
    """Give a player only rules, skill, public example and its own command location."""
    config = configuration(directory)
    return f'''You are {player}, an independent player of Dichotomy.
{config.get('motivations', MOTIVATIONS)[player]}
Session ID: {directory.name}
Read these instructions and rules yourself:
- {PLAYER_SKILL / 'SKILL.md'}
- {PLAYER_SKILL / 'references' / 'character-tracking.md'}
- {directory / 'instructions.md' if (directory / 'instructions.md').exists() else ROOT / 'sessions' / 'skeleton' / 'instructions.md'}
- {REPO / 'AGENTS.md'} and relevant skills in {ROOT / 'skills'}
- The complete rules: {REPO / 'content.md'}
Formatting example only: {PLAYER_SKILL / 'references' / 'transcript-example.md'}
Your commands: {PLAYER_SKILL / 'scripts' / player}
Every command takes YOUR_PASSWORD SESSION_ID as its only two arguments.
Your password will be supplied privately by the operator. Never disclose it.
Use declare_attribute.py for character attribute rolls; the sheet supplies the
die and bonus. Read its confirmation and invoke the returned next_command.
Use declare.py only with kind selection or luck for other random choices.
Use start_chapter.py/start_challenge.py for agreed numbered/named boundaries,
and action.py for titled story actions. Internal updates are hidden from the
human story transcript, so put narration and dialogue in action.py/say.py.
The purpose is playtesting: actively use feedback.py for constructive criticism
of the game, and feature_request.py for additional script requests. Both accept
text on stdin and can be used whenever you notice an issue, including out of turn.
{config['scope']}
On each activation, invoke read.py, decide your own contribution, then invoke
end_turn.py, pass.py or finish.py and end your response. Do not spawn subagents.
Speak only as yourself. Do not invent another player's agreement or dialogue.
Do not inspect directories, other players' files, session storage, Python source,
implementation scripts, environment/process lists, or password hashes. You may
read the listed rules, skill, instructions and example. Run the provided commands
without reading their implementation. Sharing credentials, impersonation, or
reading/editing implementation scripts results in disqualification from the game.
'''


def serve(directory, resume=None):
    """Run notifications and live exports; the supervising agent dispatches players."""
    config = configuration(directory)
    with exclusive(directory):
        broker = Broker(directory / '.operator', directory)
        try:
            state = broker.state()
            if state['complete']:
                raise ValueError('this session is complete')
            if state['paused'] and not resume:
                raise ValueError('session paused; inspect status and use --resume NOTE')
            if resume:
                broker.notice(resume, resume=True)
            broker.start()
            print(f'Ready. Transcript: {directory / "transcript.md"}', flush=True)
            while not broker.state()['complete'] and not broker.state()['paused']:
                if broker.state()['turn_number'] > config['max_turns']:
                    broker.notice('Speaking-turn budget reached; paused, not completed.')
                    break
                time.sleep(0.2)
        except KeyboardInterrupt:
            if not broker.state()['complete']:
                broker.notice('Operator stopped the broker; session paused.')
        finally:
            broker.close()


def main():
    """Keep all runtime files under /tmp and all passwords out of persistent prose."""
    parser = argparse.ArgumentParser(description='Local three-player session tools')
    commands = parser.add_subparsers(dest='command', required=True)
    create = commands.add_parser('create', help='create a session; read player passwords as JSON on stdin')
    create.add_argument('session_id')
    server = commands.add_parser('serve', help='serve authenticated commands and live exports')
    server.add_argument('session_id')
    server.add_argument('--resume', metavar='NOTE')
    status = commands.add_parser('status', help='read observer status; no player credentials needed')
    status.add_argument('session_id')
    rebuild = commands.add_parser('rebuild-logs', help='regenerate observer files from a stopped session journal without playing')
    rebuild.add_argument('session_id')
    opened = commands.add_parser('open-logs', help='open transcript and creator feedback together in VS Code')
    opened.add_argument('session_id')
    launch = commands.add_parser('brief', help='print one private player launch brief, excluding its password')
    launch.add_argument('session_id')
    launch.add_argument('player', choices=PLAYERS)
    kick = commands.add_parser('disqualify', help='after stopping the broker, record a rule violation')
    kick.add_argument('session_id')
    kick.add_argument('player', choices=PLAYERS)
    kick.add_argument('reason')
    args = parser.parse_args()
    try:
        directory = session_path(args.session_id)
        if args.command == 'create':
            directory = create_session(args.session_id, json.loads(sys.stdin.read(4097)))
            print(f'Created {directory}. No players started.\nTranscript: {directory / "transcript.md"}')
        elif args.command == 'serve':
            serve(directory, args.resume)
        elif args.command == 'status':
            print((directory / 'status.md').read_text(encoding='utf-8'))
        elif args.command == 'rebuild-logs':
            with exclusive(directory):
                broker = Broker(directory / '.operator', directory)
                broker.close()
            print(f'Rebuilt observer files: {directory}')
        elif args.command == 'open-logs':
            editor = shutil.which('code') or shutil.which('code-insiders')
            if not editor:
                raise ValueError('VS Code CLI is not on PATH; open the linked files or install its code command')
            logs = [directory / 'transcript.md', directory / 'creator-feedback.md']
            if not all(path.is_file() for path in logs):
                raise ValueError('create the session before opening its logs')
            subprocess.run([editor, '--reuse-window', *(str(path) for path in logs)], check=True)
        elif args.command == 'brief':
            print(brief(directory, args.player))
        else:
            with exclusive(directory):
                broker = Broker(directory / '.operator', directory)
                try:
                    broker.disqualify(args.player, args.reason)
                finally:
                    broker.close()
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        parser.exit(1, f'Error: {error}\n')


if __name__ == '__main__':
    main()
