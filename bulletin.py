import requests
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()
URL = os.getenv("FRANKFURTER_URL")
if URL is None:
    raise SystemExit("ERROR: FRANKFURTER_URL not found. Check your .env file.")


def fetch_rates(url, params, max_retries=3):
    """Fetches exchange rates from the API with retry and backoff."""

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Attempt {attempt}: Status code {response.status_code}")
        except requests.exceptions.RequestException as error:
            print(f"Attempt {attempt}: {type(error).__name__}")
        if attempt < max_retries:
            time.sleep(2 * attempt)
    return None


def load_history(path):
    """Loads rate history from JSON file, returns empty list if missing."""
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_history(path, history):
    """Saves rate history list to JSON file."""
    with open(path, "w", encoding="utf-8") as file:
        json.dump(history, file, indent=2, ensure_ascii=False)


def calculate_change(old, new):
    """Returns percentage change from old to new value."""
    return (new - old) / old * 100


def format_change(change):
    """Returns ' (↑ 0.3%)' style suffix, or empty string if change is None."""
    if change is None:
        return ""
    ok = "↑" if change >= 0 else "↓"
    return f" ({ok} {abs(change):.1f}%)"


def format_bulletin(date, usd_rate, eur_rate, usd_change=None, eur_change=None):
    """Builds a human-readable bulletin string with optional change indicators."""
    bulletin = f"""📅 Currency Bulletin — {date}
💵 1 USD = {usd_rate:.2f} TRY{format_change(usd_change)}
💶 1 EUR = {eur_rate:.2f} TRY{format_change(eur_change)}"""
    return bulletin


def main():
    """Orchestrates the bulletin flow: fetch, record, and display."""
    usd_data = fetch_rates(URL, {"from": "USD", "to": "TRY"})
    eur_data = fetch_rates(URL, {"from": "EUR", "to": "TRY"})
    if usd_data is None or eur_data is None:
        print("Could not fetch rates. Try again later.")
        return

    usd_rate = usd_data["rates"]["TRY"]
    eur_rate = eur_data["rates"]["TRY"]
    date = usd_data["date"]

    history = load_history("rates.json")

    previous = None
    if history and history[-1]["date"] != date:
        previous = history[-1]
    elif len(history) >= 2 and history[-1]["date"] == date:
        previous = history[-2]

    usd_change = None
    eur_change = None
    if previous is not None:
        usd_change = calculate_change(previous["usd_try"], usd_rate)
        eur_change = calculate_change(previous["eur_try"], eur_rate)

    today_record = {"date": date, "usd_try": usd_rate, "eur_try": eur_rate}

    if history and history[-1]["date"] == date:
        print(f"Already recorded for {date}.")
    else:
        history.append(today_record)
        save_history("rates.json", history)
        print(f"Saved. Total records: {len(history)}")

    bulletin = format_bulletin(date, usd_rate, eur_rate, usd_change, eur_change)
    print(bulletin)


if __name__ == "__main__":
    main()
