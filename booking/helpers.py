import os
import csv
import json
import re
import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta


def get_csv_data(file_name: str) -> list:
    """Reads input parameters from a CSV file."""
    if not os.path.exists(file_name):
        return []
    with open(file_name, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row for row in reader if any(row.values())]


def find_number_in_string(string: str) -> str:
    """Extracts digits from a string."""
    digits = re.findall(r"\d+", str(string).replace(",", "").replace(".", ""))
    return "".join(digits) if digits else "0"


def clean_price(price_str: str) -> str:
    """Cleans raw price string."""
    if not price_str:
        return "0"
    cleaned = re.sub(r"[^\d.,]", "", str(price_str)).strip()
    return cleaned if cleaned else str(price_str).strip()


def generate_default_dates(days_ahead: int = 7, duration_days: int = 3) -> tuple[str, str]:
    """Generates default checkin and checkout dates."""
    today = datetime.date.today()
    checkin = today + timedelta(days=days_ahead)
    checkout = checkin + timedelta(days=duration_days)
    return checkin.strftime("%Y-%m-%d"), checkout.strftime("%Y-%m-%d")


def construct_date_range(
    start_year: int, start_month: int, duration: int, place: str, adult: int, rooms: int
) -> list:
    """Constructs a list of date query dictionaries."""
    today = datetime.date.today()
    try:
        start_date = datetime.date(start_year, start_month, 1)
    except ValueError:
        start_date = today + timedelta(days=1)

    if start_date <= today:
        start_date = today.replace(day=1) + relativedelta(months=1)

    duration = max(1, min(duration, 12))
    date_ranges = []

    for i in range(duration):
        checkin_date = start_date + relativedelta(months=i)
        checkout_date = checkin_date + timedelta(days=14)
        date_ranges.append({
            "checkin": checkin_date.strftime("%Y-%m-%d"),
            "checkout": checkout_date.strftime("%Y-%m-%d"),
            "month": checkin_date.strftime("%B"),
            "place": place,
            "adult": adult,
            "rooms": rooms,
        })

    return date_ranges


def save_to_csv(data: list, filepath: str, fieldnames: list = None) -> None:
    """Appends data rows to a CSV file."""
    if not data:
        return
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    if not fieldnames:
        fieldnames = list(data[0].keys())

    file_exists = os.path.exists(filepath)
    with open(filepath, "a" if file_exists else "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        if not file_exists:
            writer.writeheader()
        for row in data:
            writer.writerow(row)


def save_to_json(data: list, filepath: str) -> None:
    """Saves data list to a JSON file."""
    if not data:
        return
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
