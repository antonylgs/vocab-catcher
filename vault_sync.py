"""Best-effort git commit+push of vault notes.

Exists only on the VPS deployment branch, so bot.py's core stays free of
deployment concerns (and merges from main almost never conflict).
"""

import asyncio
import logging
import subprocess
from pathlib import Path

log = logging.getLogger("vocab-catcher")

_git_lock = asyncio.Lock()


def _git(vault: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(vault), *args],
        check=check,
        capture_output=True,
        text=True,
        timeout=30,
    )


async def sync_to_git(vault: Path, filename: str) -> None:
    """Commit+push a saved note to the vault repo.

    Never raises: the note is already on disk, and a failed push self-heals on
    the next message (the pending commit rides along with the next push).
    """
    async with _git_lock:
        try:
            await asyncio.to_thread(_git, vault, "add", filename)
            unchanged = await asyncio.to_thread(
                lambda: _git(vault, "diff", "--cached", "--quiet", check=False).returncode == 0
            )
            if unchanged:
                return
            await asyncio.to_thread(_git, vault, "commit", "-m", f"add {filename}")
            await asyncio.to_thread(_git, vault, "push")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            stderr = (getattr(exc, "stderr", "") or "").strip()
            log.error("git sync failed for %s: %s", filename, stderr)
