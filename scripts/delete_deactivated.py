import os, time, requests

ORG = os.environ["OKTA_ORG_URL"]
H = {"Authorization": f"SSWS {os.environ['OKTA_API_TOKEN']}", "Accept": "application/json"}

users = requests.get(f"{ORG}/api/v1/users", headers=H, params={
    "search": 'status eq "DEPROVISIONED"', "limit": 200}).json()
print(f"deleting {len(users)} deactivated users")

for u in users:
    # For an already-deactivated user, one DELETE removes them permanently
    r = requests.delete(f"{ORG}/api/v1/users/{u['id']}", headers=H)
    print(u["profile"]["login"], r.status_code)
    time.sleep(0.4)