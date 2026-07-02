import json
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters


load_dotenv()
TOKEN = os.environ["TELEGRAM_TOKEN"]
VAULT = Path(os.environ["OBSIDIAN_VAULT_PATH"]).expanduser()
VAULT.mkdir(parents=True, exist_ok=True)

SYSTEM_INSTRUCTION = (
    "You are a Korean tutor. The user sends a Korean word, romanization, "
    "or an English description. Reply with ONLY a JSON object with these "
    "string keys: hangul, romanization, meaning_en, example_ko, example_en, theme. "
    "'theme' must be a single lowercase category word. "
    "'form_ko' must be the exact surface form of the word as it literally appears in example_ko "
    "(e.g. if hangul is 말하다 and the sentence uses 말하는, then form_ko is 말하는)."
)

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def enrich(text: str) -> dict:
    resp = client.models.generate_content(
        model=os.environ["MODEL"],
        contents=text,
        config=genai.types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            response_mime_type="application/json",
        )
    )

    return json.loads(resp.text)

def make_cloze(example_ko: str, form_ko: str) -> str | None:
    if form_ko and form_ko in example_ko:
        return example_ko.replace(form_ko, f'=={form_ko}==', 1)
    return None

def build_note(e: dict) -> str:
    theme = e.get('theme', 'mix').strip().lower().replace(' ', '-')
    cloze = make_cloze(e['example_ko'], e['form_ko'])

    note = (
        f"# {e['romanization']}\n\n"
        f"**{e['meaning_en']}**\n\n"
        f"{e['example_en']}\n\n"
        f"#flashcards/korean/{theme}\n\n"
        f"{e['hangul']}::{e['meaning_en']}\n\n"
    )

    if cloze:
        note += f"{cloze}\n{e['example_en']}\n\n"
    return note

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word = update.message.text.strip()
    e = enrich(word)

    note = build_note(e)

    (VAULT / f"{e['hangul']}.md").write_text(note, encoding="utf-8")

    await update.message.reply_text(f"Saved: {e['hangul']} - {e['meaning_en']}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    print("~~Bot running~~")
    app.run_polling()

if __name__ == '__main__':
    main()
