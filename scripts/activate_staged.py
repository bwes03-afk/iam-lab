import os, time, requests

ORG = os.environ["OKTA_ORG_URL"]
H = {"Authorization": f"SSWS {os.environ['OKTA_API_TOKEN']}", "Accept": "application/json"}

users = requests.get(f"{ORG}/api/v1/users", headers=H, params={
    "search": 'status eq "STAGED" and profile.employmentStatus eq "ACTIVE"',
    "limit": 200}).json()
print(f"activating {len(users)} users")
for u in users:
    r = requests.post(f"{ORG}/api/v1/users/{u['id']}/lifecycle/activate",
                      headers=H, params={"sendEmail": "false"})
    print(u["profile"]["login"], r.status_code)
    time.sleep(0.3)