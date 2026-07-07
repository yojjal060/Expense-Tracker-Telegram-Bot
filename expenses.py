from __future__ import annotations

from datetime import date

from database import (
    add_expense,
    add_income,
    get_daily_income_summary,
    get_daily_income_total,
    get_daily_summary,
    get_month_income_summary,
    get_month_income_total,
    get_month_summary,
    get_total_for_day,
    get_total_for_month,
)


def format_money(amount: float) -> str:
    if amount.is_integer():
        return f"Rs {int(amount):,}"
    return f"Rs {amount:,.2f}"


def parse_amount_and_category(text: str) -> tuple[float, str]:
    parts = text.split(maxsplit=2)
    if len(parts) < 3:
        raise ValueError("Use /command <amount> <category>")

    try:
        amount = float(parts[1])
    except ValueError as exc:
        raise ValueError("Amount must be a number.") from exc

    category = parts[2].strip()
    if not category:
        raise ValueError("Category cannot be empty.")

    return amount, category


def handle_expense_command(text: str) -> str:
    amount, category = parse_amount_and_category(text)
    add_expense(amount, category)
    return (
        "✅ Expense Added\n\n"
        f"Amount: {format_money(amount)}\n"
        f"Category: {category.title()}\n"
        "Date: Today"
    )


def handle_income_command(text: str) -> str:
    amount, category = parse_amount_and_category(text)
    add_income(amount, category)
    return (
        "✅ Income Added\n\n"
        f"Amount: {format_money(amount)}\n"
        f"Category: {category.title()}\n"
        "Date: Today"
    )


def build_today_summary() -> str:
    expense_rows = get_daily_summary()
    income_rows = get_daily_income_summary()
    expense_total = get_total_for_day()
    income_total = get_daily_income_total()
    net_total = income_total - expense_total

    if not expense_rows and not income_rows:
        return "📊 Today's Summary\n\nNo income or expenses recorded today."

    lines = ["📊 Today's Summary", ""]
    if income_rows:
        lines.append("Income")
        for row in income_rows:
            lines.append(f"{row.category}: {format_money(row.amount)}")
        lines.append(f"Income Total: {format_money(income_total)}")
        lines.append("")
    if expense_rows:
        lines.append("Expenses")
        for row in expense_rows:
            lines.append(f"{row.category}: {format_money(row.amount)}")
        lines.append(f"Expense Total: {format_money(expense_total)}")
        lines.append("")
    lines.append(f"Net: {format_money(net_total)}")
    return "\n".join(lines)


def build_month_summary(year_month: str | None = None) -> str:
    month_key = year_month or date.today().strftime("%Y-%m")
    expense_rows = get_month_summary(month_key)
    income_rows = get_month_income_summary(month_key)
    expense_total = get_total_for_month(month_key)
    income_total = get_month_income_total(month_key)
    net_total = income_total - expense_total

    if not expense_rows and not income_rows:
        return f"📅 Monthly Summary\n\nNo income or expenses recorded for {month_key}."

    lines = [f"📅 Monthly Summary ({month_key})", ""]
    if income_rows:
        lines.append("Income")
        for row in income_rows:
            lines.append(f"{row.category}: {format_money(row.amount)}")
        lines.append(f"Income Total: {format_money(income_total)}")
        lines.append("")
    if expense_rows:
        lines.append("Expenses")
        for row in expense_rows:
            lines.append(f"{row.category}: {format_money(row.amount)}")
        lines.append(f"Expense Total: {format_money(expense_total)}")
        lines.append("")
    lines.append(f"Net: {format_money(net_total)}")
    return "\n".join(lines)
