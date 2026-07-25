import os
import json
import requests
from datetime import datetime, timezone, timedelta

GOLDAPI_KEY = os.environ["GOLDAPI_KEY"]
STATE_FILE = "state.json"
PERTH = timezone(timedelta(hours=8))  # Perth has no daylight saving


def get_gold_price():
    url = "https://www.goldapi.io/api/XAU/USD"
    headers = {"x-access-token": GOLDAPI_KEY}
    r = requests.get(url, headers=headers, timeout=15)
    r.raise_for_status()
    data = r.json()
    return round(data["price"], 2)


def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def main():
    price = get_gold_price()
    today = datetime.now(PERTH).date().isoformat()

    state = load_state()
    if state.get("date") != today:
        state = {"date": today}  # new day, wipe yesterday's captures

    state["price_1530"] = price
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

    print(f"15:30 XAUUSD: {price}")


if __name__ == "__main__":
    main()
