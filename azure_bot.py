from __future__ import annotations

import asyncio
import os
from pathlib import Path

import azure.functions as func
from telegram import Update
from telegram.ext import Application, CommandHandler

from commands import expense, income, month, start, summary
from database import initialize


app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

_application: Application | None = None
_startup_lock = asyncio.Lock()
_startup_complete = False


def load_dotenv_file(path: Path = Path(".env")) -> None:
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def build_application() -> Application:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Set TELEGRAM_BOT_TOKEN in your environment or .env file.")

    telegram_app = Application.builder().token(token).build()
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(CommandHandler("expense", expense))
    telegram_app.add_handler(CommandHandler("income", income))
    telegram_app.add_handler(CommandHandler("summary", summary))
    telegram_app.add_handler(CommandHandler("month", month))
    return telegram_app


async def get_application() -> Application:
    global _application, _startup_complete

    if _application is None:
        load_dotenv_file()
        initialize()
        _application = build_application()

    if not _startup_complete:
        async with _startup_lock:
            if not _startup_complete:
                await _application.initialize()
                await _application.start()
                webhook_url = os.getenv("WEBHOOK_URL")
                if not webhook_url:
                    raise RuntimeError("Set WEBHOOK_URL to your Azure Function public URL.")
                secret_token = os.getenv("TELEGRAM_WEBHOOK_SECRET")
                await _application.bot.set_webhook(
                    url=webhook_url,
                    secret_token=secret_token,
                )
                _startup_complete = True

    return _application


@app.route(route="telegram-webhook", methods=["GET", "POST"], auth_level=func.AuthLevel.ANONYMOUS)
async def telegram_webhook(req: func.HttpRequest) -> func.HttpResponse:
    if req.method == "GET":
        return func.HttpResponse("Expense bot webhook is alive.", status_code=200)

    application = await get_application()

    try:
        payload = req.get_json()
    except ValueError:
        return func.HttpResponse("Invalid JSON", status_code=400)

    secret_token = os.getenv("TELEGRAM_WEBHOOK_SECRET")
    if secret_token and req.headers.get("X-Telegram-Bot-Api-Secret-Token") != secret_token:
        return func.HttpResponse("Forbidden", status_code=403)

    update = Update.de_json(payload, application.bot)
    await application.process_update(update)
    return func.HttpResponse("OK", status_code=200)
