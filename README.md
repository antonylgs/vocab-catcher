A Telegram bot that turns new words into Obsidian flashcards.

Frictionless language learning for everyday life. Message the bot a word you just
encountered, in any language you configure, and it uses Google Gemini to look it
up (spelling, meaning, example sentence, category), then writes a Markdown note
into your Obsidian vault, ready for the Spaced Repetition plugin.

The target language is set with the `LANGUAGE` variable, so the same bot works for
Korean, Japanese, Spanish, or anything else, just change one line.

## Contents

- [What you get per word](#what-you-get-per-word)
- [Setup](#setup)
- [Run](#run)
- [Run as a background service (macOS)](#run-as-a-background-service-macos)
- [Run on an always-on server (VPS)](#run-on-an-always-on-server-vps)

## What you get per word

For each word it saves a note in your vault with:

- The word + its romanization/reading and English meaning
- An example sentence (target language + English)
- An auto tag like `#flashcards/<language>/food`
- A `word::meaning` flashcard
- A cloze (fill-in-the-blank) card using the word in the example sentence

## Setup

1. **Requirements**: Python 3.13+ and [uv](https://docs.astral.sh/uv/).

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Get credentials**:
   - Telegram bot token, create a bot via [@BotFather](https://t.me/BotFather).
   - Gemini API key, from [Google AI Studio](https://aistudio.google.com/apikey).

4. **Create a `.env` file** in the project root:
   ```env
   TELEGRAM_TOKEN=your-telegram-bot-token
   GEMINI_API_KEY=your-gemini-api-key
   MODEL=gemini-2.5-flash
   OBSIDIAN_VAULT_PATH=~/path/to/your/obsidian/vault
   LANGUAGE=Korean
   ```

   Set `LANGUAGE` to whatever you want to learn (e.g. `Japanese`, `Spanish`).

## Run

```bash
uv run bot.py
```

Then message your bot on Telegram with a word (e.g. `사랑`, `annyeong`, or a
plain English description). It replies `Saved: ...` once the note is written to
your vault.

## Run as a background service (macOS)

Use the [`macos-background-service`](https://github.com/antonylgs/vocab-catcher/tree/macos-background-service) branch

To keep the bot running and auto-start it at login, install it as a launchd
user agent. Paths are resolved dynamically, so it works from wherever the
project lives:

```bash
./install-service.sh
```

This generates `~/Library/LaunchAgents/com.ags.vocab-catcher.plist` from the
template and loads it. To stop and remove it:

```bash
./install-service.sh uninstall
```

## Run on an always-on server (VPS)

Use the [`vps-deployment`](https://github.com/antonylgs/vocab-catcher/tree/vps-deployment) branch.

Running on an always-on server avoids the message drops you get when a laptop
sleeps. This branch commits and pushes each new note to a git-backed vault.

**Setup (Debian-style VM):**

1. Make the **vault its own private git repo** and give the VM push access
   (SSH deploy key with write scope). Set `user.name`/`user.email` in the clone
   or commits fail.
2. Clone this branch, `python3 -m venv .venv && .venv/bin/pip install -e .`.
3. Write `.env` (see [Setup](#setup)); point `OBSIDIAN_VAULT_PATH` at the vault clone.
   Git sync is always on here, no flag.
4. Run under `systemd` (`ExecStart=.venv/bin/python3 bot.py`, `Restart=always`),
   then `systemctl enable --now vocab`.
5. **Stop any other poller** (e.g. the macOS launchd agent). Only one bot per
   token is allowed, or Telegram returns `409 Conflict`.

Your devices pull the vault via the Obsidian Git plugin (or Obsidian Sync).

> Updates use `./update.sh` (`reset --hard`), **not** `git pull`: the branch is
> force-pushed, so a plain pull would conflict.
