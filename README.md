# TTTTTTT — Bus Seat Monitor (deployment diagnostic only)

Target: **Seosan → Daejeon Complex**, **2026-11-15 20:30 Asia/Seoul**.

> ⚠️ This repository currently tests Northflank deployment and Discord webhook delivery **only**.
> It does NOT connect to KOBUS, verify available seats, or send seat alerts.

## Northflank
1. Create a **Combined** service from this repository, branch `main`.
2. Select **Dockerfile**, build context `/`, Dockerfile path `/Dockerfile`.
3. No public ports needed.
4. Set a secret environment variable `DISCORD_WEBHOOK_URL` to your Discord webhook URL.
5. Deploy and read logs: look for "DIAGNOSTIC MODE ONLY". Expect a test notification only.
6. Delete the service after the target date to release resources.

Optional environment variables:
- `CHECK_INTERVAL_SECONDS=300` (diagnostic heartbeat only; minimum 60)
- `SEND_STARTUP_TEST=true` (send one test message at startup; set false to disable)

Never commit the webhook URL into this public repository.

## Next work
Implement and independently verify a legitimate, permitted real-time seat availability data source, including correctness and access restrictions, before enabling any seat alerts. Timetable information alone does **not** indicate available seats.
