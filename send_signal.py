import os
import json
import requests
from datetime import datetime, timezone, timedelta

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]
SL_DISTANCE = 60.0
STATE_FILE = "state.json"
PERTH = timezone(timedelta(hours=8))


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    r = requests.post(url, data={"chat_id": CHAT_ID, "text": message}, timeout=15)
    r.raise_for_status()


def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def main():
    state = load_state()
    price_1530 = state.get("price_1530")
    price_2330 = state.get("price_2330")
    today = datetime.now(PERTH).date().isoformat()

    if price_1530 is None or price_2330 is None:
        print("Missing one or both captures, skipping signal.")
        return

    if state.get("signal_sent_date") == today:
        print("Signal already sent today, skipping.")
        return

    if price_2330 > price_1530:
        direction = "\U0001F7E2 BUY"
        entry = price_2330
        stop_loss = entry - SL_DISTANCE
        order_type = "Buy Stop Entry"
    else:
        direction = "\U0001F534 SELL"
        entry = price_2330
        stop_loss = entry + SL_DISTANCE
        order_type = "Sell Stop Entry"

    message = (
        "\U0001F4CA XAUUSD ASIA SIGNAL\n"
        f"Direction: {direction}\n"
        f"15:30 Price: {price_1530}\n"
        f"23:30 Price: {price_2330}\n"
        f"{order_type}: {entry}\n"
        f"Stop Loss: {stop_loss}\n"
        "SL Distance: $60 movement\n"
        "Timezone: Perth"
    )

    send_telegram(message)
    print(message)

    state["signal_sent_date"] = today
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)


if __name__ == "__main__":
    main()
