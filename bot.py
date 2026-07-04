import asyncio
import json
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

from vault_sync import sync_to_git


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger("vocab-catcher")

load_dotenv()
TOKEN = os.environ["TELEGRAM_TOKEN"]
VAULT = Path(os.environ["OBSIDIAN_VAULT_PATH"]).expanduser()
VAULT.mkdir(parents=True, exist_ok=True)
LANGUAGE = os.environ.get("LANGUAGE", "Korean")

SYSTEM_INSTRUCTION = (
    f"You are a {LANGUAGE} tutor. The user sends a {LANGUAGE} word, romanization, "
    "or an English description. Reply with ONLY a JSON object with these "
    "string keys: hangul, romanization, meaning_en, example_ko, example_en, theme, form_ko. "
    "'theme' must be a single lowercase category word. "
    "'form_ko' must be the exact surface form of the word as it literally appears in example_ko "
    "(e.g. if the sentence conjugates or inflects the word, form_ko is that exact surface form)."
)

GENAI_TIMEOUT = 60

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"],
    http_options=genai.types.HttpOptions(timeout=GENAI_TIMEOUT * 1000),
)


async def enrich(text: str) -> dict:
    resp = await asyncio.wait_for(
        client.aio.models.generate_content(
            model=os.environ["MODEL"],
            contents=text,
            config=genai.types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                response_mime_type="application/json",
            ),
        ),
        timeout=GENAI_TIMEOUT + 5,
    )

    return json.loads(resp.text)


def make_cloze(example_ko: str, form_ko: str) -> str | None:
    if form_ko and form_ko in example_ko:
        return example_ko.replace(form_ko, f"=={form_ko}==", 1)
    return None


def build_note(e: dict) -> str:
    theme = e.get("theme", "mix").strip().lower().replace(" ", "-")
    cloze = make_cloze(e.get("example_ko", ""), e.get("form_ko", ""))

    note = (
        f"# {e['romanization']}\n\n"
        f"**{e['meaning_en']}**\n\n"
        f"{e['example_en']}\n\n"
        f"#flashcards/{LANGUAGE.lower()}/{theme}\n\n"
        f"{e['hangul']}::{e['meaning_en']}\n\n"
    )

    if cloze:
        note += f"{cloze}\n{e['example_en']}\n\n"
    return note


async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word = update.message.text.strip()
    log.info("processing: %s", word)
    try:
        e = await enrich(word)
        note = build_note(e)
        (VAULT / f"{e['hangul']}.md").write_text(note, encoding="utf-8")
        await sync_to_git(VAULT, f"{e['hangul']}.md")
    except Exception:
        log.exception("failed to process %r", word)
        await update.message.reply_text(f"Failed to process: {word}")
        return

    log.info("saved: %s", e["hangul"])
    await update.message.reply_text(f"Saved: {e['hangul']} - {e['meaning_en']}")


async def on_error(update: object, context: ContextTypes.DEFAULT_TYPE):
    log.error("unhandled error", exc_info=context.error)


async def on_start(app):
    log.info("~~Bot running~~")

    async def watchdog():
        while True:
            await asyncio.sleep(30)
            if app.updater is None or not app.updater.running:
                log.error("updater not running — exiting for launchd restart")
                os._exit(1)

    app.create_task(watchdog())


def main():
    app = ApplicationBuilder().token(TOKEN).post_init(on_start).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.add_error_handler(on_error)
    app.run_polling(bootstrap_retries=-1)


if __name__ == "__main__":
    main()
