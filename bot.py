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

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

def enrich(text: str) -> dict:
    resp = client.models.generate_content(
        model=os.environ["MODEL"],
        contents=text,
        config=genai.types.GenerateContentConfig(
            system_instruction=("You are a Korean tutor. The user sends a Korean word, romanization, "
                "or an English description. Reply with ONLY a JSON object with these "
                "string keys: hangul, romanization, meaning_en, example_ko, example_en."),
            response_mime_type="application/json",
        )
    )

    return json.loads(resp.text)

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    word = update.message.text.strip()
    e = enrich(word)

    note = (
        f"# {e['hangul']}\n\n"
        f"**{e['meaning_en']}** ({e['romanization']})\n\n"
        f"{e['example_ko']}\n{e['example_en']}\n\n"
        f"#flashcards/korean\n"
        f"{e['hangul']}:::{e['meaning_en']}\n"
    )
    (VAULT / f"{e['hangul']}.md").write_text(note, encoding="utf-8")

    await update.message.reply_text(f"Saved: {e['hangul']} - {e['meaning_en']}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    print("~~Bot running~~")
    app.run_polling()

if __name__ == '__main__':
    main()
