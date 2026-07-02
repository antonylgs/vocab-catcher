A Telegram bot that turns new words into Obsidian flashcards.

Frictionless language learning for everyday life. Message the bot a word you just
encountered, in any language you configure, and it uses Google Gemini to look it
up (spelling, meaning, example sentence, category), then writes a Markdown note
into your Obsidian vault, ready for the Spaced Repetition plugin.

The target language is set with the `LANGUAGE` variable, so the same bot works for
Korean, Japanese, Spanish, or anything else, just change one line.

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
