import csv, os, time, datetime, requests

M = os.path.expanduser("~/iam-lab/migration")
ORG = os.environ["OKTA_ORG_URL"]
H = {"Authorization": f"SSWS {os.environ['OKTA_API_TOKEN']}",
     "Accept": "application/json", "Content-Type": "application/json"}

log = []
with open(f"{M}/decisions.csv") as f:
    for d in csv.DictReader(f):
        result = ""
        if d["decision"] == "LINK":
            # Find the existing Acme identity by its HR employee number
            users = requests.get(f"{ORG}/api/v1/users", headers=H, params={
                "search": f'profile.employeeNumber eq "{d["acmeEmployeeId"]}"'}).json()
            if not users:
                result = "SKIPPED: Acme account not in Okta (already offboarded)"
            else:
                u = users[0]
                r = requests.post(f"{ORG}/api/v1/users/{u['id']}", headers=H, json={
                    "profile": {"secondEmail": d["globexEmail"], "globexId": d["globexId"]}})
                result = f"LINKED to {u['profile']['login']}" if r.ok else f"FAILED {r.status_code}"
            time.sleep(0.3)
        elif d["decision"] == "SEPARATE":
            result = "SEPARATE: will be onboarded as a new worker"
        else:
            result = "PENDING: no action until a decision is recorded"
        log.append({**d, "result": result,
                    "appliedAt": datetime.datetime.now().isoformat(timespec="seconds")})
        print(d["globexId"], d["name"], "->", result)

with open(f"{M}/link_log.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=log[0].keys())
    w.writeheader()
    w.writerows(log)
print("audit log written to migration/link_log.csv")