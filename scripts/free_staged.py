import os, time, requests

ORG = os.environ["OKTA_ORG_URL"]
H = {"Authorization": f"SSWS {os.environ['OKTA_API_TOKEN']}", "Accept": "application/json"}
HR = "http://localhost:8080/workers"

# Staged Acme users (employee numbers start with A), oldest first
users = requests.get(f"{ORG}/api/v1/users", headers=H, params={
    "search": 'status eq "STAGED" and profile.employeeNumber sw "A"', "limit": 20}).json()
print(f"retiring {len(users)} staged users")

for u in users:
    emp = u["profile"].get("employeeNumber")
    hr = requests.post(f"{HR}/{emp}/terminate")          # keep HR consistent first
    ok = requests.post(f"{ORG}/api/v1/users/{u['id']}/lifecycle/deactivate", headers=H)
    print(emp, u["profile"]["login"], "HR:", hr.status_code, "Okta deactivate:", ok.status_code)
    time.sleep(0.5)