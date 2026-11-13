# KOBUS Seat Watcher — Seosan → Daejeon

**Target:** 2026-11-15 20:30 KST, Seosan (393) → Daejeon Complex (300).

## Status

- Discord webhook test: previously confirmed by user.
- KOBUS request parameters: captured from user browser.
- 20:30 HTML structure: captured from user browser (`span.start_time`, `span.remain`).
- **Live access from GitHub Actions: NOT YET VERIFIED.** The server may block access or return changed HTML. A green workflow means the request/parser completed, not that seat availability is independently certified.

## Setup

1. In **Settings → Secrets and variables → Actions**, configure the repository secret `DISCORD_WEBHOOK_URL`. Rotate any URL previously exposed in chat/screenshots.
2. In **Actions → Bus Seat Watcher → Run workflow**, leave `test_discord` **unchecked** to perform a **real read-only KOBUS lookup test**.
3. Open the job log for **Check and notify**. It should print `KOBUS ... N seats`. If not, a lookup error will be logged and the job will fail.
4. If a verified response has more than 0 seats, the workflow sends a Discord notification with a link for manual booking.
5. Schedule uses GitHub cron approx. every 5 minutes, subject to delays and skipped executions.

The first positive result is cached to avoid duplicate alerts. As implemented, there is **at most one alert** for the trip; if tickets disappear and reappear, no second alert will be sent. Do not mistake a successful test webhook message for a confirmed seat.

No booking, purchases, logins, or seat reservations are performed. Requests should remain low volume and honor provider access limitations.

## Shutdown

Scheduled workflow still starts after departure but exits without querying. Disable the workflow after the trip.

## Technical detail

`watcher.py` starts a cookie session by loading the KOBUS route page and then submits the form fields captured from the user’s browser to `/mrs/alcnSrch.do`. It finds the exact 20:30 row and parses the adjacent remaining seat count. Any missing or ambiguous row is treated as **failure**, never as available seats.

A site change, redirect, session validation, network block, or changed endpoint can make this method fail. It is *not* an official API integration.
