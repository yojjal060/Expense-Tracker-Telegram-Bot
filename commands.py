from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from expenses import build_month_summary, build_today_summary, handle_expense_command, handle_income_command


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hi! Use:\n"
        "/expense <amount> <category>\n"
        "/income <amount> <category>\n"
        "/summary\n"
        "/month"
    )


async def expense(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        message = handle_expense_command(update.message.text or "")
    except ValueError as exc:
        message = str(exc)
    await update.message.reply_text(message)


async def income(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        message = handle_income_command(update.message.text or "")
    except ValueError as exc:
        message = str(exc)
    await update.message.reply_text(message)


async def summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(build_today_summary())


async def month(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(build_month_summary())
