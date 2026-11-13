"""Read-only KOBUS departure seat watcher.

The request is based on a captured KOBUS timetable form. A successful
GitHub Actions run is not proof that live querying works: inspect the logs.
No seat selection, reservation, or payment requests are sent.
"""
import argparse
import logging
import os
import re
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup

BASE = "https://www.kobus.co.kr"
DEPARTURE = datetime(2026, 11, 15, 20, 30, tzinfo=ZoneInfo("Asia/Seoul"))
TARGET_TIME = "20:30"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.7",
}
FORM = {
    "deprCd": "393", "deprNm": "서산",
    "arvlCd": "300", "arvlNm": "대전복합",
    "tfrCd": "", "tfrNm": "", "tfrArvlFullNm": "",
    "pathDvs": "sngl", "pathStep": "1",
    "crchDeprArvlYn": "N",
    "deprDtm": "20261115", "deprDtmAll": "2026. 11. 15. 일",
    "arvlDtm": "20261115", "arvlDtmAll": "2026. 11. 15. 일",
    "busClsCd": "0", "abrnData": "", "prmmDcYn": "N",
    "rtrpChc": "1", "timeLinkMin": "00", "timeLinkMax": "23",
}
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


class SeatLookupError(Exception):
    pass


def seat_count_from_html(html: str) -> int:
    soup = BeautifulSoup(html, "html.parser")
    matches = []
    for start in soup.select("span.start_time"):
        normalized = re.sub(r"\s+", "", start.get_text(" ", strip=True))
        if normalized != TARGET_TIME:
            continue
        # On the KOBUS timetable a single <a> encloses the departure row.
        ancestor = start.find_parent("a")
        if ancestor is None:
            ancestor = start.find_parent("p")
        if ancestor is None:
            continue
        remain = ancestor.select_one("span.remain")
        if remain is None:
            continue
        match = re.fullmatch(r"\s*(\d+)\s*석\s*", remain.get_text(" ", strip=True))
        if match:
            matches.append(int(match.group(1)))
    if len(matches) != 1:
        raise SeatLookupError(
            f"Expected exactly one 20:30 seat row; found {len(matches)}. "
            "Website structure or route/session may have changed."
        )
    return matches[0]


def live_seat_count() -> int:
    with requests.Session() as session:
        session.headers.update(HEADERS)
        # Open search page first to establish ordinary website session cookies.
        page = session.get(BASE + "/mrs/rotinf.do", timeout=20)
        page.raise_for_status()
        result = session.post(
            BASE + "/mrs/alcnSrch.do",
            data=FORM,
            headers={"Referer": BASE + "/mrs/rotinf.do", "Origin": BASE},
            timeout=25,
            allow_redirects=True,
        )
        result.raise_for_status()
        if "/login" in result.url.lower():
            raise SeatLookupError("Redirected to login rather than timetable")
        result.encoding = result.apparent_encoding or result.encoding
        logging.info("Timetable HTTP %s, final path %s, body %s bytes",
                     result.status_code, requests.utils.urlparse(result.url).path,
                     len(result.content))
        return seat_count_from_html(result.text)


def send_discord(message: str) -> None:
    url = os.getenv("DISCORD_WEBHOOK_URL", "")
    if not url.startswith("https://discord.com/api/webhooks/"):
        raise RuntimeError("DISCORD_WEBHOOK_URL secret missing or malformed")
    response = requests.post(url, json={"content": message}, timeout=15)
    response.raise_for_status()
    logging.info("Discord sent, HTTP %s", response.status_code)


def set_output(name: str, value: str) -> None:
    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a", encoding="utf-8") as file:
            file.write(f"{name}={value}\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-webhook", action="store_true")
    args = parser.parse_args()
    if args.test_webhook:
        send_discord("🧪 GitHub Actions → Discord 웹훅 테스트 성공 (좌석 조회와 별개)")
        return

    if datetime.now(ZoneInfo("Asia/Seoul")) >= DEPARTURE:
        logging.info("2026-11-15 20:30 KST passed. No further seat checks.")
        set_output("found", "false")
        return

    try:
        seats = live_seat_count()
    except (requests.RequestException, SeatLookupError) as error:
        logging.error("KOBUS lookup NOT verified this run: %s", error)
        raise SystemExit(1)

    logging.info("KOBUS 2026-11-15 20:30 Seosan -> Daejeon: %s seats", seats)
    set_output("found", str(seats > 0).lower())
    if seats > 0 and os.getenv("SEAT_ALERT_ALREADY_SENT") != "true":
        send_discord(
            f"🚨 서산 → 대전복합 2026년 11월 15일 20:30 취소표 감지: "
            f"잔여 {seats}석! 직접 예매: {BASE}/"
        )
        logging.info("Seat alert sent")
    elif seats > 0:
        logging.info("Seat alert already sent; suppressing duplicate")
    else:
        logging.info("Sold out; no Discord seat alert")


if __name__ == "__main__":
    main()
