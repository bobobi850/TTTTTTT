"""GitHub Actions execution diagnostic.

No live KOBUS availability lookup has been verified yet.
"""
import os
import sys
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
DEPARTURE = datetime(2026, 11, 15, 20, 30, tzinfo=ZoneInfo("Asia/Seoul"))


def notify(message):
    url = os.environ.get("DISCORD_WEBHOOK_URL", "").strip()
    if not url:
        raise RuntimeError("GitHub Actions secret DISCORD_WEBHOOK_URL is missing")
    response = requests.post(url, json={"content": message}, timeout=15)
    response.raise_for_status()
    logging.info("Discord notification delivered (HTTP %s).", response.status_code)


def main():
    now = datetime.now(ZoneInfo("Asia/Seoul"))
    logging.info("Target: Seosan -> Daejeon Complex, 2026-11-15 20:30 KST")
    if now >= DEPARTURE:
        logging.info("Departure time passed. Exiting.")
        return
    if "--test-webhook" in sys.argv:
        notify("🧪 GitHub Actions 알림 테스트 성공! ⚠️ 실제 KOBUS 잔여 좌석 조회는 아직 구현되지 않았습니다.")
        return
    # Never claim seats are available based on a mere successful workflow run.
    logging.warning("DIAGNOSTIC ONLY: live seat checker not yet implemented; no seat alert sent.")


if __name__ == "__main__":
    main()
