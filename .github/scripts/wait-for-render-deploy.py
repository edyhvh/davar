"""Poll Render API until a deploy reaches a terminal state."""

import json
import os
import sys
import time
import urllib.error
import urllib.request

api_key = os.environ["RENDER_API_KEY"]
service_id = os.environ["RENDER_SERVICE_ID"]
deploy_id = os.environ["DEPLOY_ID"]

url = f"https://api.render.com/v1/services/{service_id}/deploys/{deploy_id}"

# Known terminal states from Render deploy lifecycle.
success_states = {"live"}
failure_states = {
    "build_failed",
    "update_failed",
    "canceled",
    "deactivated",
}

max_attempts = 90  # 90 * 20s = 30 minutes
sleep_seconds = 20

for attempt in range(1, max_attempts + 1):
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"Render API HTTP error: {exc.code} {body}")
        sys.exit(1)
    except Exception as exc:
        print(f"Render API request failed: {exc}")
        sys.exit(1)

    status = payload.get("status", "unknown")
    print(f"Attempt {attempt}/{max_attempts}: deploy status = {status}")

    if status in success_states:
        print("Render deploy succeeded.")
        sys.exit(0)

    if status in failure_states:
        print("Render deploy failed.")
        sys.exit(1)

    time.sleep(sleep_seconds)

print("Timed out waiting for Render deploy to reach a terminal state.")
sys.exit(1)
