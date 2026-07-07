from __future__ import annotations

import os
import asyncio
from pathlib import Path

from telegram.ext import Application, CommandHandler

from commands import expense, income, month, start, summary
from database import initialize


def load_dotenv_file(path: Path = Path(".env")) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def main() -> None:
    load_dotenv_file()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Set TELEGRAM_BOT_TOKEN in your environment or .env file.")

    initialize()

    asyncio.set_event_loop(asyncio.new_event_loop())
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("expense", expense))
    app.add_handler(CommandHandler("income", income))
    app.add_handler(CommandHandler("summary", summary))
    app.add_handler(CommandHandler("month", month))

    app.run_polling()


if __name__ == "__main__":
    main()
