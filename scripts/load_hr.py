import csv, sys, time, requests

LIMIT = None if "--all" in sys.argv else 20
HR_URL = "http://localhost:8080/workers"

with open("acme_workers.csv") as f:
    rows = list(csv.DictReader(f))

existing = {w["employeeId"] for w in requests.get(HR_URL).json()}
sent = 0
for row in rows:
    if LIMIT is not None and sent >= LIMIT:
        break
    if row["employeeId"] in existing:
        continue  # already loaded on an earlier run
    r = requests.post(HR_URL, json=row)
    print(row["employeeId"], row["email"], r.status_code)
    sent += 1
    time.sleep(0.3)  # stay well under Okta's rate limits

print(f"sent {sent} workers")