"""Northflank deployment and Discord notification smoke-test.

IMPORTANT: This is NOT a working KOBUS seat availability checker.
It intentionally does not claim available seats or scrape a booking site.
"""
import os
import time
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
KST = ZoneInfo("Asia/Seoul")
DEPARTURE = datetime(2026, 11, 15, 20, 30, tzinfo=KST)
CHECK_INTERVAL = max(60, int(os.getenv("CHECK_INTERVAL_SECONDS", "300")))
WEBHOOK = os.getenv("DISCORD_WEBHOOK_URL", "").strip()
SEND_STARTUP = os.getenv("SEND_STARTUP_TEST", "true").lower() == "true"


def notify(message: str) -> None:
    if not WEBHOOK:
        logging.warning("DISCORD_WEBHOOK_URL is missing. No Discord notification sent.")
        return
    try:
        response = requests.post(WEBHOOK, json={"content": message}, timeout=15)
        response.raise_for_status()
        logging.info("Discord message sent.")
    except requests.RequestException as exc:
        logging.error("Discord notification failed: %s", exc)


def main() -> None:
    logging.warning("DIAGNOSTIC MODE ONLY: no live seat monitoring is implemented.")
    logging.info("Target: Seosan -> Daejeon Complex, 2026-11-15 20:30 KST")
    if SEND_STARTUP:
        notify("🧪 버스 알림 테스트: Northflank 컨테이너가 시작되었습니다. ⚠️ 아직 KOBUS 좌석 감시 기능은 연결되지 않았습니다.")
    while datetime.now(KST) < DEPARTURE:
        logging.info("Container alive; live seat checking is NOT enabled.")
        time.sleep(CHECK_INTERVAL)
    logging.info("Departure time passed; shutting down.")


if __name__ == "__main__":
    main()
