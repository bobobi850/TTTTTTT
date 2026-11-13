# TTTTTTT — Bus Seat Watcher

Target: **Seosan → Daejeon Complex** on **2026-11-15 20:30 KST**.

## Current status: deployment diagnostic only

The GitHub Actions workflow and Discord webhook test are installed, but **real KOBUS seat availability lookup is not implemented or verified**. Scheduled runs log a diagnostic message only; **they do not monitor seats or notify when a seat becomes available**. Do not rely on this as a booking alert.

## GitHub Actions setup

1. Open **Settings → Secrets and variables → Actions → New repository secret**.
2. Set the name to `DISCORD_WEBHOOK_URL`, value to a newly rotated Discord webhook URL.
3. Open **Actions → Bus Seat Watcher (diagnostic only) → Run workflow**.
4. Turn on `test_discord` for this manual run to send one test notification.
5. A green Actions run verifies only job execution. A delivered Discord test verifies only the webhook.
6. The schedule is currently every 5 minutes (best effort; GitHub can delay it). It does not yet check seats.

The webhook secret should not appear in source code or screenshots. Any previously shared webhook URL should be rotated.

## Files

- `watcher.py`: one-shot diagnostic with a manual `--test-webhook` option
- `.github/workflows/bus-watch.yml`: scheduled no-op diagnostic + manual Discord test
- `requirements.txt`: requests
- `Dockerfile`: container environment for possible future VM deployment

## Next step

Choose and verify an authorized real-time availability data source (for example, a supported provider API where credentials and coverage are available). Confirm that the specific departure and remaining seats are returned, then implement state transition alerts and enable scheduled monitoring. The existence of a route or timetable entry alone does not establish seat availability.

## Cleanup

Disable or remove the scheduled workflow after November 15 to avoid unnecessary runs.
